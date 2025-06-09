#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import Dialog
------------
Dialog for importing OCT files.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QListWidget, QCheckBox,
                           QGroupBox)
from PyQt5.QtCore import Qt

class ImportDialog(QDialog):
    """Dialog for importing OCT files."""
    
    def __init__(self, parent=None):
        """Initialize the import dialog."""
        super().__init__(parent)
        
        self.selected_files = []
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Import OCT Files")
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # File selection
        main_layout.addWidget(QLabel("Select Files:"))
        
        file_layout = QHBoxLayout()
        self.file_path = QLabel("No files selected")
        file_layout.addWidget(self.file_path)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_files)
        file_layout.addWidget(self.browse_button)
        
        main_layout.addLayout(file_layout)
        
        # File list
        self.file_list = QListWidget()
        main_layout.addWidget(self.file_list)
        
        # Show supported formats
        format_group = QGroupBox("Supported Formats")
        format_layout = QVBoxLayout(format_group)
        
        # Display all supported formats
        format_label = QLabel(
            "• Zeiss Cirrus OCT (.img, .IMG)\n"
            "• Heidelberg OCT (.e2e, .E2E)\n"
            "• Topcon OCT (.fds, .FDS, .fda, .FDA)\n"
            "• Bioptigen OCT (.oct, .OCT)\n"
            "• POCT Files (.poct, .POCT)\n"
            "• DICOM Files (.dcm, .DCM)"
        )
        format_layout.addWidget(format_label)
        
        # Add note about automatic format detection
        note_label = QLabel("<i>All supported formats will be included automatically.</i>")
        note_label.setStyleSheet("color: #666; font-size: 10px;")
        format_layout.addWidget(note_label)
        
        main_layout.addWidget(format_group)
        
        # Warning about file overwriting
        warning_label = QLabel("<b>Warning:</b> When saving frames with the same filename, old files will be overwritten. "
                            "Please ensure original files are named differently to avoid data loss.")
        warning_label.setStyleSheet("color: #d32f2f; font-size: 11px;")
        warning_label.setWordWrap(True)
        main_layout.addWidget(warning_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.accept)
        self.import_button.setEnabled(False)
        button_layout.addWidget(self.import_button)
        
        main_layout.addLayout(button_layout)
    
    def browse_files(self):
        """Browse for files to import."""
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
            
            # Enable import button
            self.import_button.setEnabled(True)
    
    def get_selected_files(self):
        """
        Get the selected files.
        
        Returns:
            List[str]: List of selected file paths
        """
        return self.selected_files
