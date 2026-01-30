#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DICOM Export Dialog
------------------
Dialog for exporting OCT files to DICOM format with proper headers.
"""

import os
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QComboBox, QCheckBox,
                           QGroupBox, QGridLayout, QSpinBox, QLineEdit,
                           QListWidget, QListWidgetItem, QProgressBar,
                           QMessageBox, QDoubleSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

logger = logging.getLogger(__name__)


class DicomExportWorker(QThread):
    """Worker thread for DICOM export."""
    
    progress_updated = pyqtSignal(int, int)  # (current, total)
    file_exported = pyqtSignal(str, bool, str, list)  # (file_name, success, message, created_files)
    export_complete = pyqtSignal(int, int, list)  # (success_count, error_count, all_files)
    
    def __init__(self, oct_reader, files_to_export, output_dir, dicom_options):
        super().__init__()
        self.oct_reader = oct_reader
        self.files_to_export = files_to_export
        self.output_dir = output_dir
        self.dicom_options = dicom_options
        self._cancel_requested = False
    
    def cancel(self):
        """Request cancellation of the export."""
        self._cancel_requested = True
    
    def run(self):
        """Run the DICOM export."""
        success_count = 0
        error_count = 0
        all_created_files = []
        total_files = len(self.files_to_export)
        
        for i, file_name in enumerate(self.files_to_export):
            if self._cancel_requested:
                break
            
            self.progress_updated.emit(i, total_files)
            
            try:
                # Create subdirectory for each file
                file_output_dir = os.path.join(
                    self.output_dir, 
                    os.path.splitext(file_name)[0]
                )
                os.makedirs(file_output_dir, exist_ok=True)
                
                success, message, created_files = self.oct_reader.export_to_dicom(
                    file_name, file_output_dir, self.dicom_options
                )
                
                self.file_exported.emit(file_name, success, message, created_files)
                
                if success:
                    success_count += 1
                    all_created_files.extend(created_files)
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                self.file_exported.emit(file_name, False, str(e), [])
                logger.exception(f"Error exporting {file_name} to DICOM: {e}")
        
        self.progress_updated.emit(total_files, total_files)
        self.export_complete.emit(success_count, error_count, all_created_files)


class DicomExportDialog(QDialog):
    """Dialog for exporting OCT files to DICOM format."""
    
    def __init__(self, oct_reader, parent=None):
        """Initialize the DICOM export dialog.
        
        Args:
            oct_reader: OCTFileReader instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.oct_reader = oct_reader
        self.worker = None
        self.created_files = []
        
        self.init_ui()
        self.populate_file_list()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Export to DICOM")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        main_layout = QVBoxLayout(self)
        
        # File selection
        files_group = QGroupBox("Files to Export")
        files_layout = QVBoxLayout()
        
        files_layout.addWidget(QLabel("Select files to export to DICOM format:"))
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        files_layout.addWidget(self.file_list)
        
        # Selection buttons
        sel_btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_files)
        sel_btn_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_files)
        sel_btn_layout.addWidget(self.deselect_all_btn)
        
        files_layout.addLayout(sel_btn_layout)
        files_group.setLayout(files_layout)
        main_layout.addWidget(files_group)
        
        # Output directory
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout()
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output directory...")
        output_layout.addWidget(self.output_path)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_btn)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # DICOM Options
        options_group = QGroupBox("DICOM Export Options")
        options_layout = QFormLayout()
        
        # E2E specific options
        e2e_label = QLabel("<b>Heidelberg E2E Options:</b>")
        options_layout.addRow(e2e_label)
        
        self.extract_repeats_checkbox = QCheckBox("Extract all scan repeats")
        self.extract_repeats_checkbox.setToolTip("Extract all repeated scans from E2E files")
        options_layout.addRow(self.extract_repeats_checkbox)
        
        # IMG specific options
        img_label = QLabel("<b>Zeiss IMG Options:</b>")
        options_layout.addRow(img_label)
        
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(128, 4096)
        self.rows_spin.setValue(1024)
        self.rows_spin.setToolTip("Number of rows for IMG files")
        options_layout.addRow("Rows:", self.rows_spin)
        
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(128, 4096)
        self.cols_spin.setValue(512)
        self.cols_spin.setToolTip("Number of columns for IMG files")
        options_layout.addRow("Columns:", self.cols_spin)
        
        self.interlaced_checkbox = QCheckBox("Interlaced")
        self.interlaced_checkbox.setToolTip("Set interlaced mode for IMG files")
        options_layout.addRow(self.interlaced_checkbox)
        
        # OCT specific options
        oct_label = QLabel("<b>Bioptigen OCT Options:</b>")
        options_layout.addRow(oct_label)
        
        self.diskbuffered_checkbox = QCheckBox("Disk buffered (reduce memory)")
        self.diskbuffered_checkbox.setToolTip("Use disk buffering to reduce memory usage for large OCT files")
        options_layout.addRow(self.diskbuffered_checkbox)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_export)
        button_layout.addWidget(self.cancel_btn)
        
        self.export_btn = QPushButton("Export to DICOM")
        self.export_btn.clicked.connect(self.start_export)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.file_list.itemSelectionChanged.connect(self.update_export_button)
        self.output_path.textChanged.connect(self.update_export_button)
    
    def populate_file_list(self):
        """Populate the file list with DICOM-exportable files."""
        self.file_list.clear()
        
        dicom_files = self.oct_reader.get_dicom_supported_files()
        
        for file_name in dicom_files:
            item = QListWidgetItem(file_name)
            item.setData(Qt.UserRole, file_name)
            
            # Get file type for display
            try:
                file_path = self.oct_reader.file_paths.get(file_name, "")
                file_type = self.oct_reader.get_file_type(file_path).upper()
                item.setText(f"{file_name} [{file_type}]")
            except Exception:
                pass
            
            self.file_list.addItem(item)
        
        if self.file_list.count() == 0:
            self.status_label.setText("No files available for DICOM export. Import OCT files first.")
    
    def select_all_files(self):
        """Select all files in the list."""
        for i in range(self.file_list.count()):
            self.file_list.item(i).setSelected(True)
    
    def deselect_all_files(self):
        """Deselect all files in the list."""
        for i in range(self.file_list.count()):
            self.file_list.item(i).setSelected(False)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_path.setText(directory)
    
    def update_export_button(self):
        """Update the export button state."""
        has_files = len(self.file_list.selectedItems()) > 0
        has_output = bool(self.output_path.text().strip())
        self.export_btn.setEnabled(has_files and has_output)
    
    def get_dicom_options(self):
        """Get DICOM export options from UI."""
        return {
            # E2E options
            'extract_scan_repeats': self.extract_repeats_checkbox.isChecked(),
            # IMG options
            'rows': self.rows_spin.value(),
            'cols': self.cols_spin.value(),
            'interlaced': self.interlaced_checkbox.isChecked(),
            # OCT options
            'diskbuffered': self.diskbuffered_checkbox.isChecked()
        }
    
    def start_export(self):
        """Start the DICOM export."""
        # Get selected files
        selected_files = []
        for item in self.file_list.selectedItems():
            file_name = item.data(Qt.UserRole)
            selected_files.append(file_name)
        
        if not selected_files:
            QMessageBox.warning(self, "Error", "No files selected for export")
            return
        
        output_dir = self.output_path.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "Error", "No output directory selected")
            return
        
        # Validate output directory
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            QMessageBox.warning(self, "Error", f"Cannot create output directory: {e}")
            return
        
        # Disable UI
        self.set_ui_enabled(False)
        self.created_files = []
        
        # Get options
        dicom_options = self.get_dicom_options()
        
        # Create and start worker
        self.worker = DicomExportWorker(
            self.oct_reader,
            selected_files,
            output_dir,
            dicom_options
        )
        
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.file_exported.connect(self.on_file_exported)
        self.worker.export_complete.connect(self.on_export_complete)
        
        self.worker.start()
    
    def cancel_export(self):
        """Cancel the export or close the dialog."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            self.status_label.setText("Export cancelled")
            self.set_ui_enabled(True)
        else:
            self.reject()
    
    def set_ui_enabled(self, enabled):
        """Enable or disable UI elements."""
        self.file_list.setEnabled(enabled)
        self.output_path.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)
        self.export_btn.setEnabled(enabled)
        self.extract_repeats_checkbox.setEnabled(enabled)
        self.rows_spin.setEnabled(enabled)
        self.cols_spin.setEnabled(enabled)
        self.interlaced_checkbox.setEnabled(enabled)
        self.diskbuffered_checkbox.setEnabled(enabled)
    
    def on_progress_updated(self, current, total):
        """Handle progress update."""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
    
    def on_file_exported(self, file_name, success, message, created_files):
        """Handle file export completion."""
        if success:
            self.status_label.setText(f"Exported: {file_name} ({len(created_files)} files)")
            self.created_files.extend(created_files)
        else:
            self.status_label.setText(f"Failed: {file_name} - {message}")
    
    def on_export_complete(self, success_count, error_count, all_files):
        """Handle export completion."""
        self.set_ui_enabled(True)
        self.progress_bar.setValue(self.progress_bar.maximum())
        
        if error_count == 0:
            self.status_label.setText(f"Export complete: {success_count} files exported successfully")
            QMessageBox.information(
                self, 
                "Export Complete",
                f"Successfully exported {success_count} files to DICOM format.\n"
                f"Total DICOM files created: {len(all_files)}"
            )
        else:
            self.status_label.setText(f"Export complete with errors: {success_count} succeeded, {error_count} failed")
            QMessageBox.warning(
                self,
                "Export Complete with Errors",
                f"Exported {success_count} files successfully.\n"
                f"{error_count} files failed to export.\n"
                f"Check the log for details."
            )
