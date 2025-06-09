#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Batch Processing Dialog
---------------------
Dialog for batch processing OCT files.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QListWidget, QComboBox,
                           QGroupBox, QCheckBox, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import os
import logging

logger = logging.getLogger(__name__)

class BatchProcessWorker(QThread):
    """Worker thread for batch processing."""
    
    # Signals
    progress_updated = pyqtSignal(int, int)  # (current, total)
    file_progress_updated = pyqtSignal(float)  # file progress (0-1)
    processing_file = pyqtSignal(str)  # file being processed
    processing_complete = pyqtSignal(bool, str)  # (success, message)
    
    # Cancel flag
    _cancel_requested = False
    
    def __init__(self, file_controller, export_controller, files, export_dir, export_settings):
        """
        Initialize the worker.
        
        Args:
            file_controller: FileController instance
            export_controller: ExportController instance
            files: List of file paths to process
            export_dir: Directory to export to
            export_settings: Export settings dictionary
        """
        super().__init__()
        self.file_controller = file_controller
        self.export_controller = export_controller
        self.files = files
        self.export_dir = export_dir
        self.export_settings = export_settings
        self._cancel_requested = False
    
    def cancel(self):
        """Request cancellation of the batch process."""
        logger.info("Batch processing cancellation requested")
        self._cancel_requested = True
        
    def run(self):
        """Run the batch processing."""
        total_files = len(self.files)
        processed_files = 0
        success_count = 0
        error_count = 0
        error_messages = []
        
        try:
            for file_path in self.files:
                # Check if cancellation was requested
                if self._cancel_requested:
                    logger.info("Batch processing canceled by user")
                    self.processing_complete.emit(False, "Batch processing canceled by user")
                    return
                    
                # Update progress
                processed_files += 1
                self.progress_updated.emit(processed_files, total_files)
                
                file_name = os.path.basename(file_path)
                self.processing_file.emit(file_name)
                
                try:
                    # Import file
                    success, message = self.file_controller.import_file(file_path)
                    
                    if success:
                        # Get frames
                        frames = self.file_controller.frame_controller.get_available_frames(file_name)
                        
                        if frames:
                            # Create file-specific export directory
                            file_export_dir = os.path.join(self.export_dir, os.path.splitext(file_name)[0])
                            os.makedirs(file_export_dir, exist_ok=True)
                            
                            # Export frames with progress tracking
                            def file_progress_callback(progress):
                                # Update the file-specific progress
                                self.file_progress_updated.emit(progress)
                                # Check if cancellation was requested
                                return not self._cancel_requested
                                
                            # Export frames
                            export_success, export_message = self.export_controller.export_frames(
                                frames,
                                file_export_dir,
                                self.export_settings,
                                file_progress_callback
                            )
                            
                            if export_success:
                                success_count += 1
                                logger.info(f"Successfully processed {file_name}")
                            else:
                                error_count += 1
                                error_messages.append(f"Error exporting {file_name}: {export_message}")
                                logger.error(f"Error exporting {file_name}: {export_message}")
                        else:
                            error_count += 1
                            error_messages.append(f"No frames found in {file_name}")
                            logger.warning(f"No frames found in {file_name}")
                    else:
                        error_count += 1
                        error_messages.append(f"Error importing {file_name}: {message}")
                        logger.error(f"Error importing {file_name}: {message}")
                        
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"Error processing {file_name}: {str(e)}")
                    logger.exception(f"Exception processing {file_name}: {e}")
            
            # Emit completion signal
            if error_count == 0:
                self.processing_complete.emit(True, f"Successfully processed {success_count} files")
            else:
                self.processing_complete.emit(False, f"Processed {success_count} files with {error_count} errors")
                
        except Exception as e:
            self.processing_complete.emit(False, f"Batch processing failed: {str(e)}")
            logger.exception(f"Batch processing failed: {e}")

class BatchDialog(QDialog):
    """Dialog for batch processing OCT files."""
    
    def __init__(self, parent=None, file_controller=None, export_controller=None):
        """
        Initialize the batch processing dialog.
        
        Args:
            parent: Parent widget
            file_controller: FileController instance
            export_controller: ExportController instance
        """
        super().__init__(parent)
        
        self.file_controller = file_controller
        self.export_controller = export_controller
        self.selected_files = []
        self.worker = None
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Batch Process OCT Files")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        main_layout = QVBoxLayout(self)
        
        # Source files section
        source_group = QGroupBox("Source Files")
        source_layout = QVBoxLayout(source_group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_path = QLabel("No files selected")
        file_layout.addWidget(self.file_path, 1)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_files)
        file_layout.addWidget(self.browse_button)
        
        source_layout.addLayout(file_layout)
        
        # File list
        self.file_list = QListWidget()
        source_layout.addWidget(self.file_list)
        
        main_layout.addWidget(source_group)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout(export_group)
        
        # Export directory
        export_dir_layout = QHBoxLayout()
        export_dir_layout.addWidget(QLabel("Export Directory:"))
        self.export_path = QLabel("Not selected")
        export_dir_layout.addWidget(self.export_path, 1)
        
        self.browse_export_button = QPushButton("Browse...")
        self.browse_export_button.clicked.connect(self.browse_export_dir)
        export_dir_layout.addWidget(self.browse_export_button)
        
        export_layout.addLayout(export_dir_layout)
        
        # Export settings
        export_settings_group = QGroupBox("Export Settings")
        export_settings_layout = QVBoxLayout()
        
        # Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "TIFF"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        export_settings_layout.addLayout(format_layout)
        
        # Duplicate file handling
        duplicate_layout = QHBoxLayout()
        duplicate_label = QLabel("When file exists:")
        self.duplicate_combo = QComboBox()
        self.duplicate_combo.addItem("Overwrite", "overwrite")
        self.duplicate_combo.addItem("Skip", "skip")
        self.duplicate_combo.addItem("Create unique name", "unique")
        self.duplicate_combo.setToolTip("Choose how to handle duplicate filenames during export")
        duplicate_layout.addWidget(duplicate_label)
        duplicate_layout.addWidget(self.duplicate_combo)
        export_settings_layout.addLayout(duplicate_layout)
        
        # Export metadata
        self.export_metadata_checkbox = QCheckBox("Export metadata (JSON)")
        self.export_metadata_checkbox.setChecked(True)
        export_settings_layout.addWidget(self.export_metadata_checkbox)
        
        # Create subfolder for each file
        self.create_subfolder_checkbox = QCheckBox("Create subfolder for each file")
        self.create_subfolder_checkbox.setChecked(True)
        export_settings_layout.addWidget(self.create_subfolder_checkbox)
        
        export_settings_group.setLayout(export_settings_layout)
        export_layout.addWidget(export_settings_group)
        
        main_layout.addWidget(export_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        # Overall progress bar
        overall_label = QLabel("Overall Progress:")
        progress_layout.addWidget(overall_label)
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        # Current file label
        self.current_file_label = QLabel("Ready")
        progress_layout.addWidget(self.current_file_label)
        
        # File progress bar
        file_label = QLabel("Current File Progress:")
        progress_layout.addWidget(file_label)
        self.file_progress_bar = QProgressBar()
        self.file_progress_bar.setRange(0, 100)  # Set range from 0-100
        self.file_progress_bar.setValue(0)  # Initialize at 0
        progress_layout.addWidget(self.file_progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Start Processing")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setEnabled(False)
        button_layout.addWidget(self.process_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.file_progress_bar.setValue(0)
    
    def browse_files(self):
        """Browse for files to process."""
        # Include all supported formats by default
        filters = [
            "All Supported OCT Files (*.e2e *.E2E *.img *.IMG *.fds *.FDS *.fda *.FDA *.oct *.OCT *.poct *.POCT *.dcm *.DCM)",
            "Heidelberg OCT (*.e2e *.E2E)",
            "Zeiss Cirrus OCT (*.img *.IMG)",
            "Topcon OCT (*.fds *.FDS *.fda *.FDA)",
            "Bioptigen OCT (*.oct *.OCT)",
            "POCT Files (*.poct *.POCT)",
            "DICOM Files (*.dcm *.DCM)",
            "All Files (*)"
        ]
        
        filter_str = ";;".join(filters)
        
        # Open file dialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select OCT Files",
            "",
            filter_str
        )
        
        if files:
            self.selected_files = files
            
            # Update file list
            self.file_list.clear()
            for file_path in files:
                self.file_list.addItem(file_path)
            
            # Update label
            if len(files) == 1:
                self.file_path.setText(files[0])
            else:
                self.file_path.setText(f"{len(files)} files selected")
            
            # Enable process button if export path is also selected
            self.update_process_button()
    
    def browse_export_dir(self):
        """Browse for export directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        
        if directory:
            self.export_path.setText(directory)
            
            # Enable process button if files are also selected
            self.update_process_button()
    
    def update_process_button(self):
        """Update the state of the process button."""
        self.process_button.setEnabled(
            len(self.selected_files) > 0 and 
            self.export_path.text() != "Not selected"
        )
    
    def start_processing(self):
        """Start the batch processing."""
        if not self.selected_files:
            QMessageBox.warning(self, "Error", "No files selected for processing")
            return
        
        if self.export_path.text() == "Not selected":
            QMessageBox.warning(self, "Error", "No export directory selected")
            return
        
        # Create export settings
        export_settings = {
            'format': self.format_combo.currentText(),
            'rotation': '0°',  # Default rotation
            'crop': False,     # No cropping in batch mode
            'crop_params': {},
            'export_metadata': self.export_metadata_checkbox.isChecked(),
            'on_duplicate': self.duplicate_combo.currentData()  # Add duplicate handling option
        }
        
        # Disable UI during processing
        self.setUIEnabled(False)
        
        # Create and start worker thread
        self.worker = BatchProcessWorker(
            self.file_controller,
            self.export_controller,
            self.selected_files,
            self.export_path.text(),
            export_settings
        )
        
        # Connect worker signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.file_progress_updated.connect(self.update_file_progress)
        self.worker.processing_file.connect(self.update_current_file)
        self.worker.processing_complete.connect(self.processing_complete)
        
        # Start worker
        self.worker.start()
    
    def update_progress(self, current, total):
        """Update the overall progress bar."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def update_file_progress(self, progress):
        """Update the file progress bar.
        
        Args:
            progress: Progress value between 0 and 1
        """
        # Convert 0-1 to 0-100 for progress bar
        progress_percent = int(progress * 100)
        self.file_progress_bar.setValue(progress_percent)
    
    def update_current_file(self, file_name):
        """Update the current file label."""
        self.current_file_label.setText(f"Processing: {file_name}")
        # Reset file progress bar when starting a new file
        self.file_progress_bar.setValue(0)
    
    def processing_complete(self, success, message):
        """Handle processing completion."""
        # Re-enable UI
        self.setUIEnabled(True)
        
        # Update status
        self.current_file_label.setText("Processing complete")
        
        # Show result
        if success:
            QMessageBox.information(self, "Batch Processing Complete", message)
        else:
            QMessageBox.warning(self, "Batch Processing Complete", message)
    
    def setUIEnabled(self, enabled):
        """Enable or disable UI elements."""
        self.browse_button.setEnabled(enabled)
        self.browse_export_button.setEnabled(enabled)
        self.format_combo.setEnabled(enabled)
        self.export_metadata_checkbox.setEnabled(enabled)
        self.create_subfolder_checkbox.setEnabled(enabled)
        self.process_button.setEnabled(enabled)
        self.cancel_button.setEnabled(not enabled)
        
    def cancel_processing(self):
        """Cancel the batch processing operation."""
        if self.worker and self.worker.isRunning():
            self.current_file_label.setText("Canceling...")
            self.worker.cancel()
            # The worker will emit processing_complete signal when it stops
