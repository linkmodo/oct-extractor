#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCT Image Extraction Application
--------------------------------
A Windows application to extract and process images from Zeiss Cirrus OCT RAW files
and Heidelberg OCT e2e files used in ophthalmology.

Features:
- Import Zeiss and Heidelberg OCT files
- Define export folder
- Select frames to export
- Batch rotate images
- Crop images using pre-determined parameters
"""

import sys
import os
import time
import logging
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFileDialog, QMessageBox, QListWidget, 
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit, 
                             QStatusBar, QAction, QToolBar, QSplitter, QFrame, 
                             QGridLayout, QTextBrowser, QMenu, QProgressDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QCursor

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "oct_extractor.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Application starting")

# Import custom modules
from model.oct_file_reader import OCTFileReader
from model.image_processor import ImageProcessor
from model.file_manager import FileManager
from controller.file_controller import FileController
from controller.export_controller import ExportController
from controller.frame_controller import FrameController
from controller.image_controller import ImageController
from view.import_dialog import ImportDialog
from view.frame_selector import FrameSelector
from view.export_dialog import ExportDialog
from view.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize models
        self.file_manager = FileManager()
        self.oct_reader = OCTFileReader()
        self.image_processor = ImageProcessor()
        
        # Initialize controllers - make sure to initialize image_controller first
        self.file_controller = FileController(self.oct_reader, self.file_manager)
        self.image_controller = ImageController(self.image_processor)
        self.frame_controller = FrameController(self.oct_reader)
        # Now we can safely initialize export_controller with image_controller
        self.export_controller = ExportController(self.file_manager, self.oct_reader, self.image_controller)
        
        logger.info("Controllers initialized successfully")
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("OCT Image Extraction Tool")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Toolbar removed as per requirements
        
        # Create main content area
        content_layout = QHBoxLayout()
        
        # Left panel - File browser
        file_browser_group = QGroupBox("File Browser")
        file_browser_layout = QVBoxLayout(file_browser_group)
        
        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        # Add mouse press event to handle clicking on empty file list
        self.file_list.mousePressEvent = self.file_list_mouse_press_event
        file_browser_layout.addWidget(self.file_list)
        
        file_info_label = QLabel("File Information:")
        file_browser_layout.addWidget(file_info_label)
        
        self.file_info = QLabel("No file selected")
        file_browser_layout.addWidget(self.file_info)
        
        # Create a horizontal layout for the preview and metadata panels
        preview_metadata_layout = QHBoxLayout()
        
        # Center panel - Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("No preview available")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        preview_layout.addWidget(self.preview_label)
        
        # No longer displaying basic metadata in the preview window
        
        # Right panel - General Metadata
        metadata_group = QGroupBox("General Metadata")
        metadata_layout = QVBoxLayout(metadata_group)
        
        # Use a text browser for scrollable, formatted metadata display
        self.detailed_metadata = QTextBrowser()
        self.detailed_metadata.setMinimumWidth(300)
        self.detailed_metadata.setReadOnly(True)
        self.detailed_metadata.setOpenExternalLinks(True)  # Allow clicking links if any
        self.detailed_metadata.setText("No metadata available")
        
        # Set vertical scrollbar to always be visible
        self.detailed_metadata.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Use a stylesheet to improve the appearance of the metadata display
        self.detailed_metadata.setStyleSheet("""
            QTextBrowser {
                background-color: #fafafa;
                border: 1px solid #ddd;
                font-family: Arial, sans-serif;
                font-size: 10pt;
            }
        """)
        
        metadata_layout.addWidget(self.detailed_metadata)
        
        # Add preview and metadata panels to the horizontal layout
        preview_metadata_layout.addWidget(preview_group, 2)  # Preview takes 2/3 of space
        preview_metadata_layout.addWidget(metadata_group, 1)  # Metadata takes 1/3 of space
        
        # Add panels to content layout
        content_layout.addWidget(file_browser_group, 1)
        content_layout.addLayout(preview_metadata_layout, 3)  # Give the preview/metadata more space
        
        # Frame selection panel
        frame_selection_group = QGroupBox("Frame Selection")
        frame_selection_layout = QVBoxLayout(frame_selection_group)
        
        self.frame_selector = FrameSelector()
        # Set minimum height for frame selector (reduced to improve visibility of files)
        self.frame_selector.setMinimumHeight(250)
        # Connect to the existing selectionChanged signal
        self.frame_selector.selectionChanged.connect(self.update_selection_info)
        frame_selection_layout.addWidget(self.frame_selector)
        
        # Add the frame selection panel to the content layout with a stretch factor
        content_layout.addWidget(frame_selection_group, 2)  # Give it more vertical space
        
        # Processing and export options
        options_layout = QHBoxLayout()
        
        # Processing options
        processing_group = QGroupBox("Processing Options")
        processing_layout = QVBoxLayout(processing_group)
        
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation:"))
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["0°", "90°", "180°", "270°"])
        rotation_layout.addWidget(self.rotation_combo)
        processing_layout.addLayout(rotation_layout)
        
        self.crop_checkbox = QCheckBox("Enable Cropping")
        processing_layout.addWidget(self.crop_checkbox)
        
        crop_params_layout = QGridLayout()
        crop_params_layout.addWidget(QLabel("Top:"), 0, 0)
        self.crop_top = QSpinBox()
        self.crop_top.setRange(0, 10000)
        crop_params_layout.addWidget(self.crop_top, 0, 1)
        
        crop_params_layout.addWidget(QLabel("Left:"), 1, 0)
        self.crop_left = QSpinBox()
        self.crop_left.setRange(0, 10000)
        crop_params_layout.addWidget(self.crop_left, 1, 1)
        
        crop_params_layout.addWidget(QLabel("Width:"), 2, 0)
        self.crop_width = QSpinBox()
        self.crop_width.setRange(1, 10000)
        crop_params_layout.addWidget(self.crop_width, 2, 1)
        
        crop_params_layout.addWidget(QLabel("Height:"), 3, 0)
        self.crop_height = QSpinBox()
        self.crop_height.setRange(1, 10000)
        crop_params_layout.addWidget(self.crop_height, 3, 1)
        
        processing_layout.addLayout(crop_params_layout)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout(export_group)
        
        export_dir_layout = QHBoxLayout()
        export_dir_layout.addWidget(QLabel("Export Directory:"))
        self.export_path = QLineEdit()
        export_dir_layout.addWidget(self.export_path, 1)
        self.browse_button = QPushButton("Browse...")
        export_dir_layout.addWidget(self.browse_button)
        export_layout.addLayout(export_dir_layout)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "TIFF", "DICOM"])
        format_layout.addWidget(self.format_combo)
        export_layout.addLayout(format_layout)
        
        # Create button for exporting DICOM metadata
        dicom_button_layout = QHBoxLayout()
        dicom_button_layout.addStretch(1)
        
        self.export_dicom_button = QPushButton("Export DICOM Metadata")
        self.export_dicom_button.clicked.connect(self.export_dicom_only)
        dicom_button_layout.addWidget(self.export_dicom_button)
        
        export_layout.addLayout(dicom_button_layout)
        
        self.export_button = QPushButton("Export Selected Frames")
        export_layout.addWidget(self.export_button)
        
        # Add processing and export options to layout
        options_layout.addWidget(processing_group)
        options_layout.addWidget(export_group)
        
        # Add all components to main layout
        main_layout.addLayout(content_layout)
        main_layout.addWidget(frame_selection_group)
        main_layout.addLayout(options_layout)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Connect signals and slots
        self.connect_signals()
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # Import action (directly in menu bar)
        import_action = QAction("Import...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(self.show_import_dialog)
        menubar.addAction(import_action)
        
        # Batch Process action (directly in menu bar)
        batch_process_action = QAction("Batch Process...", self)
        batch_process_action.triggered.connect(self.batch_process)
        menubar.addAction(batch_process_action)
        
        # Settings action (directly in menu bar)
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        menubar.addAction(settings_action)
        
        # Help menu (kept as a submenu for about and future items)
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.show_import_dialog)
        toolbar.addAction(import_action)
        
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.show_export_dialog)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        toolbar.addAction(settings_action)
    
    def connect_signals(self):
        """Connect signals and slots."""
        self.browse_button.clicked.connect(self.browse_export_folder)
        self.export_button.clicked.connect(self.export_selected_frames)
        self.file_list.itemSelectionChanged.connect(self.update_preview)
        self.crop_checkbox.toggled.connect(self.toggle_crop_controls)
        
        # No longer connecting frame preview signal
    
    def show_import_dialog(self):
        """Show the import dialog."""
        dialog = ImportDialog(self)
        if dialog.exec_():
            file_paths = dialog.get_selected_files()
            self.import_files(file_paths)
    
    def import_files(self, file_paths):
        """Import OCT files."""
        try:
            for file_path in file_paths:
                # Use file controller to import file
                success, message = self.file_controller.import_file(file_path)
                
                if success:
                    # Add to file list
                    self.file_list.addItem(os.path.basename(file_path))
                    self.statusBar().showMessage(f"Imported {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Import Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during import: {str(e)}")
    
    # The preview_frame method has been removed and we're using the original static preview functionality
    
    def update_preview(self):
        """Update the preview when a file is selected."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        
        file_name = selected_items[0].text()
        try:
            # Use frame controller to get preview
            preview_image, metadata = self.frame_controller.get_preview(file_name)
            
            if preview_image:
                # Display preview image
                pixmap = QPixmap(preview_image)
                self.preview_label.setPixmap(pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
            
            # Get file metadata for the right panel
            file_obj = self.file_controller.oct_reader.loaded_files.get(
                self.file_controller.oct_reader.file_paths.get(file_name)
            )
            
            if file_obj:
                # Gather general metadata (excluding DICOM-specific details)
                general_metadata = {}
                
                # Add basic file information
                file_path = self.file_controller.oct_reader.file_paths.get(file_name)
                general_metadata['Filename'] = file_name
                general_metadata['File Type'] = os.path.splitext(file_name)[1]
                
                if os.path.exists(file_path):
                    general_metadata['File Size'] = f"{os.path.getsize(file_path) / 1024:.1f} KB"
                    general_metadata['Date Modified'] = time.ctime(os.path.getmtime(file_path))
                
                # Add scan information if available
                if hasattr(file_obj, 'scan_parameters'):
                    general_metadata['Scan Type'] = file_obj.scan_parameters.get('scan_type', 'Unknown')
                    general_metadata['Scan Pattern'] = file_obj.scan_parameters.get('scan_pattern', 'Unknown')
                
                # Add volume information if available
                if hasattr(file_obj, 'volume_data') and file_obj.volume_data is not None:
                    if isinstance(file_obj.volume_data, np.ndarray):
                        general_metadata['Volume Dimensions'] = ' × '.join(map(str, file_obj.volume_data.shape))
                
                # Add basic patient info if available (without PHI)
                if hasattr(file_obj, 'metadata') and file_obj.metadata:
                    meta = file_obj.metadata
                    if 'eye' in meta:
                        general_metadata['Eye'] = meta['eye']
                    if 'study_date' in meta:
                        general_metadata['Study Date'] = meta['study_date']
                    if 'manufacturer' in meta:
                        general_metadata['Manufacturer'] = meta['manufacturer']
                    if 'device_model' in meta:
                        general_metadata['Device Model'] = meta['device_model']
                
                # Format metadata as HTML for better display
                formatted_metadata = "<h3>General File Information</h3>"
                formatted_metadata += "<table style='width:100%'>"
                
                for key, value in general_metadata.items():
                    # Handle regular key-value pairs
                    formatted_metadata += f"<tr><td style='padding:4px 10px 4px 4px;'><b>{key}</b></td><td>{value}</td></tr>"
                
                formatted_metadata += "</table>"
                
                # Get frame information from the frame controller
                frames = self.frame_controller.get_available_frames(file_name)
                
                # Add frame counts
                formatted_metadata += "<h3>Frame Information</h3>"
                formatted_metadata += "<table style='width:100%'>"
                
                # Count OCT vs fundus frames
                oct_frames = 0
                fundus_frames = 0
                
                for frame in frames:
                    if frame.get('type') == 'fundus':
                        fundus_frames += 1
                    else:
                        oct_frames += 1
                
                formatted_metadata += f"<tr><td style='padding:4px 10px 4px 4px;'><b>Total Frames</b></td><td>{len(frames)}</td></tr>"
                formatted_metadata += f"<tr><td style='padding:4px 10px 4px 4px;'><b>OCT Frames</b></td><td>{oct_frames}</td></tr>"
                formatted_metadata += f"<tr><td style='padding:4px 10px 4px 4px;'><b>Fundus Frames</b></td><td>{fundus_frames}</td></tr>"
                formatted_metadata += "</table>"
                
                # Set the formatted metadata in the text browser
                self.detailed_metadata.setHtml(formatted_metadata)
            else:
                self.detailed_metadata.setText("No metadata available")
            
            # Update frame selector
            frames = self.frame_controller.get_available_frames(file_name)
            self.frame_selector.set_frames(frames)
            
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Could not generate preview: {str(e)}")
    
    def browse_export_folder(self):
        """Browse for export folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self.export_path.setText(folder)
    
    def show_export_dialog(self):
        """Show the export dialog."""
        if not self.export_path.text():
            QMessageBox.warning(self, "Export Error", "Please select an export folder first.")
            return
        
        dialog = ExportDialog(self)
        if dialog.exec_():
            export_settings = dialog.get_export_settings()
            self.export_selected_frames(export_settings)
    
    def export_selected_frames(self, export_settings=None):
        """Export selected frames."""
        if not self.export_path.text():
            QMessageBox.warning(self, "Export Error", "Please select an export folder first.")
            return
        
        selected_frames = self.frame_selector.get_selected_frames()
        if not selected_frames:
            QMessageBox.warning(self, "Export Error", "No frames selected for export.")
            return
        
        try:
            # Get export settings
            if not export_settings:
                export_settings = {
                    'format': self.format_combo.currentText(),
                    'rotation': self.rotation_combo.currentText(),
                    'crop': self.crop_checkbox.isChecked(),
                    'crop_params': {
                        'top': self.crop_top.value(),
                        'left': self.crop_left.value(),
                        'width': self.crop_width.value(),
                        'height': self.crop_height.value()
                    },
                    'export_metadata': True,  # Always export metadata
                    'on_duplicate': 'overwrite'  # Default to overwrite behavior
                }
            
            # Create progress dialog
            progress_dialog = QProgressDialog("Exporting frames...", "Cancel", 0, 100, self)
            progress_dialog.setWindowTitle("Export Progress")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setMinimumDuration(0)  # Show immediately
            progress_dialog.setAutoClose(True)
            progress_dialog.setAutoReset(False)
            # Remove the question mark help button
            progress_dialog.setWindowFlags(progress_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            progress_dialog.setAutoReset(True)
            progress_dialog.canceled.connect(lambda: self.statusBar().showMessage("Export canceled"))
            
            # Flag to track if operation was canceled
            export_canceled = [False]
            
            # Progress callback function
            def update_progress(value):
                if export_canceled[0]:
                    return False  # Signal to stop processing
                    
                progress_dialog.setValue(int(value * 100))  # Convert 0-1 to 0-100
                QApplication.processEvents()  # Ensure UI updates
                
                # Check if dialog was canceled
                if progress_dialog.wasCanceled():
                    export_canceled[0] = True
                    self.statusBar().showMessage("Canceling export...")
                    return False  # Signal to stop processing
                    
                return True
            
            # Use export controller to export frames with progress tracking
            success, message = self.export_controller.export_frames(
                selected_frames,
                self.export_path.text(),
                export_settings,
                update_progress
            )
            
            # Close progress dialog when finished
            if progress_dialog.isVisible():
                progress_dialog.setValue(100)
                progress_dialog.close()
            
            if success:
                QMessageBox.information(self, "Export Complete", message)
                self.statusBar().showMessage(message)
            else:
                QMessageBox.warning(self, "Export Error", message)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during export: {str(e)}")
    
    def export_general_metadata(self):
        """Export general metadata for selected file."""
        if not self.export_path.text():
            QMessageBox.warning(self, "Export Error", "Please select an export folder first.")
            return
        
        # Get selected file from file list
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Export Error", "No file selected.")
            return
            
        file_name = selected_items[0].text()
        file_path = self.file_controller.oct_reader.file_paths.get(file_name)
        
        if not file_path:
            QMessageBox.warning(self, "Export Error", f"File {file_name} not found.")
            return
            
        file_obj = self.file_controller.oct_reader.loaded_files.get(file_path)
        if not file_obj:
            QMessageBox.warning(self, "Export Error", f"File object for {file_name} not found.")
            return
        
        # Gather general metadata (non-DICOM)
        general_metadata = {}
        
        # Add basic file information
        general_metadata['filename'] = file_name
        general_metadata['filepath'] = file_path
        general_metadata['file_size'] = os.path.getsize(file_path) if os.path.exists(file_path) else 'Unknown'
        general_metadata['file_type'] = os.path.splitext(file_path)[1]
        general_metadata['date_modified'] = time.ctime(os.path.getmtime(file_path)) if os.path.exists(file_path) else 'Unknown'
        
        # Add OCT specific information
        if hasattr(file_obj, 'metadata') and file_obj.metadata:
            # Filter out DICOM-specific metadata to keep it general
            for key, value in file_obj.metadata.items():
                if key not in ['dicom_metadata'] and not key.startswith('DICOM'):
                    general_metadata[key] = value
        
        # Add scan parameters if available
        if hasattr(file_obj, 'scan_parameters'):
            general_metadata['scan_parameters'] = file_obj.scan_parameters
        
        # Add volume information if available
        if hasattr(file_obj, 'volume_data') and file_obj.volume_data is not None:
            if isinstance(file_obj.volume_data, np.ndarray):
                general_metadata['volume_shape'] = file_obj.volume_data.shape
                general_metadata['volume_data_type'] = str(file_obj.volume_data.dtype)
        
        # Add fundus information if available
        if hasattr(file_obj, 'fundus_data') and file_obj.fundus_data is not None:
            if isinstance(file_obj.fundus_data, np.ndarray):
                general_metadata['fundus_shape'] = file_obj.fundus_data.shape
                general_metadata['fundus_data_type'] = str(file_obj.fundus_data.dtype)
        
        if not general_metadata:
            QMessageBox.warning(self, "Export Error", f"No general metadata found for {file_name}.")
            return
            
        # Export metadata to file
        try:
            import json
            # Create output file path
            output_file = os.path.join(self.export_path.text(), f"{os.path.splitext(file_name)[0]}_general_info.json")
            
            # Write metadata to file
            with open(output_file, 'w') as f:
                json.dump(general_metadata, f, indent=2, default=str)
                
            QMessageBox.information(self, "Export Complete", f"General metadata exported to {output_file}")
            self.statusBar().showMessage(f"General metadata exported to {output_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting general metadata: {str(e)}")
            
    def export_dicom_only(self):
        """Export only DICOM metadata for selected frames."""
        if not self.export_path.text():
            QMessageBox.warning(self, "Export Error", "Please select an export folder first.")
            return
        
        # Get selected file from file list
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Export Error", "No file selected.")
            return
            
        file_name = selected_items[0].text()
        file_path = self.file_controller.oct_reader.file_paths.get(file_name)
        
        if not file_path:
            QMessageBox.warning(self, "Export Error", f"File {file_name} not found.")
            return
            
        file_obj = self.file_controller.oct_reader.loaded_files.get(file_path)
        if not file_obj:
            QMessageBox.warning(self, "Export Error", f"File object for {file_name} not found.")
            return
        
        # Check if file has DICOM metadata - try multiple possible locations/formats
        metadata = {}
        
        # Approach 1: Direct dicom_metadata attribute
        if hasattr(file_obj, 'dicom_metadata') and file_obj.dicom_metadata:
            metadata.update(file_obj.dicom_metadata)
        
        # Approach 2: DICOM data in the metadata dictionary
        if hasattr(file_obj, 'metadata') and file_obj.metadata:
            # Get all metadata
            all_metadata = file_obj.metadata
            
            # Add DICOM-specific fields
            for key, value in all_metadata.items():
                # Include any field that has DICOM in the name or appears to be DICOM-related
                if 'dicom' in key.lower() or key.startswith('0x'):
                    metadata[key] = value
            
            # Check for a nested DICOM dictionary
            if 'dicom' in all_metadata and isinstance(all_metadata['dicom'], dict):
                metadata.update(all_metadata['dicom'])
        
        # Approach 3: Look for a raw_dicom or header attribute that might contain DICOM data
        for attr_name in ['raw_dicom', 'dicom_header', 'header', 'dicom_tags']:
            if hasattr(file_obj, attr_name):
                attr_value = getattr(file_obj, attr_name)
                if attr_value:
                    if isinstance(attr_value, dict):
                        metadata.update(attr_value)
                    else:
                        metadata[attr_name] = str(attr_value)
        
        # If we didn't find anything, use all metadata as a fallback
        if not metadata and hasattr(file_obj, 'metadata') and file_obj.metadata:
            metadata = file_obj.metadata
            
        if not metadata:
            QMessageBox.warning(self, "Export Error", f"No DICOM metadata found for {file_name}.")
            return
            
        # Export metadata to file
        try:
            import json
            # Create output file path
            output_file = os.path.join(self.export_path.text(), f"{os.path.splitext(file_name)[0]}_dicom_metadata.json")
            
            # Write metadata to file
            with open(output_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
                
            QMessageBox.information(self, "Export Complete", f"DICOM metadata exported to {output_file}")
            self.statusBar().showMessage(f"DICOM metadata exported to {output_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting DICOM metadata: {str(e)}")
    
    def select_all_frames(self):
        """Select all frames."""
        self.frame_selector.select_all()
    
    def deselect_all_frames(self):
        """Deselect all frames."""
        self.frame_selector.deselect_all()
        
    def update_selection_info(self):
        """Update information about selected frames."""
        # Get selected frames
        selected_frames = self.frame_selector.selected_frames
        num_selected = len(selected_frames)
        
        # Update status bar with selection info
        if num_selected == 0:
            self.statusBar().showMessage("No frames selected")
        elif num_selected == 1:
            self.statusBar().showMessage(f"1 frame selected")
        else:
            self.statusBar().showMessage(f"{num_selected} frames selected")
            
        # Enable/disable export button based on selection
        self.export_button.setEnabled(num_selected > 0)
    
    def toggle_crop_controls(self, enabled):
        """Enable or disable crop controls based on checkbox state."""
        self.crop_top.setEnabled(enabled)
        self.crop_left.setEnabled(enabled)
        self.crop_width.setEnabled(enabled)
        self.crop_height.setEnabled(enabled)
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def batch_process(self):
        """Batch process multiple files."""
        # Use relative import instead of absolute
        from view.batch_dialog import BatchDialog
        
        # Create and show batch processing dialog
        dialog = BatchDialog(
            self,
            file_controller=self.file_controller,
            export_controller=self.export_controller
        )
        dialog.exec_()
    
    def show_file_context_menu(self, position):
        """Show context menu for file list."""
        # Get selected item
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        # Create context menu
        context_menu = QMenu(self)
        remove_action = QAction("Remove File", self)
        remove_action.triggered.connect(self.remove_selected_file)
        context_menu.addAction(remove_action)
        
        # Show context menu at cursor position
        cursor = QCursor.pos()
        context_menu.exec_(cursor)
    
    def file_list_mouse_press_event(self, event):
        """Custom mouse press event handler for file list.
        Opens the import dialog when the list is empty.
        """
        # Call the original mousePressEvent first
        super(QListWidget, self.file_list).mousePressEvent(event)
        
        # If the file list is empty, open the import dialog
        if self.file_list.count() == 0:
            logger.debug("File list clicked while empty, showing import dialog")
            self.show_import_dialog()
    
    def remove_selected_file(self):
        """Remove the selected file from the list."""
        # Get selected item
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        file_name = selected_item.text()
        
        # Confirm removal
        reply = QMessageBox.question(
            self, 
            'Remove File', 
            f"Are you sure you want to remove {file_name}?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove file from list
            row = self.file_list.row(selected_item)
            self.file_list.takeItem(row)
            
            # Clean up resources if needed
            file_path = self.file_controller.oct_reader.file_paths.get(file_name)
            if file_path:
                # Remove from loaded files dict
                if file_path in self.file_controller.oct_reader.loaded_files:
                    del self.file_controller.oct_reader.loaded_files[file_path]
                
                # Remove from file paths dict
                del self.file_controller.oct_reader.file_paths[file_name]
                
                # Remove from metadata dict
                if file_name in self.file_controller.oct_reader.file_metadata:
                    del self.file_controller.oct_reader.file_metadata[file_name]
            
            # Clear frame selector if no files remain
            if self.file_list.count() == 0:
                self.frame_selector.set_frames([])
                self.preview_label.setText("No preview available")
                self.detailed_metadata.setText("No metadata available")
            
            self.statusBar().showMessage(f"Removed file: {file_name}")
    
    def show_about_dialog(self):
        """Show the about dialog."""
        about_text = """
        <h2>OCT Image Extraction Tool</h2>
        <p>Version 2.1</p>
        
        <p>An application to extract and process images from various OCT file formats used in ophthalmology.</p>
        
        <h3>Supported File Formats:</h3>
        <ul>
            <li>Heidelberg Engineering (.e2e)</li>
            <li>Zeiss (.img)</li>
            <li>Topcon (.fds, .fda)</li>
            <li>Bioptigen (.oct)</li>
            <li>POCT (.poct)</li>
            <li>DICOM (.dcm)</li>
        </ul>
        
        <h3>Open Source Components:</h3>
        <p>This application uses the OCT-Converter library developed by Mark Graham.</p>
        <p>OCT-Converter is available at: <a href="https://github.com/marksgraham/OCT-Converter">github.com/marksgraham/OCT-Converter</a></p>
        
        <p>Created by: Li Fan</p>
        """
        
        # Create a message box with rich text formatting
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About OCT Image Extraction Tool")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(QPixmap("icon.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        msg_box.exec_()


def main():
    """Main application entry point."""
    try:
        logger.info("Initializing application")
        app = QApplication(sys.argv)
        
        logger.info("Creating main window")
        window = MainWindow()
        
        logger.info("Showing main window")
        window.show()
        
        logger.info("Starting application event loop")
        return_code = app.exec_()
        logger.info(f"Application exited with code {return_code}")
        sys.exit(return_code)
        
    except ImportError as e:
        logger.critical(f"Import error: {e}", exc_info=True)
        print(f"ERROR: Missing dependency - {e}")
        print("Please make sure all requirements are installed with: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        print(f"ERROR: {e}")
        print("Please check the log file for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
