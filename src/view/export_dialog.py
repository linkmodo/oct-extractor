#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export Dialog
------------
Dialog for exporting OCT frames.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QComboBox, QCheckBox,
                           QGroupBox, QGridLayout, QSpinBox, QLineEdit,
                           QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt

class ExportDialog(QDialog):
    """Dialog for exporting OCT frames."""
    
    def __init__(self, parent=None):
        """Initialize the export dialog."""
        super().__init__(parent)
        
        self.export_settings = {}
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Export Settings")
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # Export location
        main_layout.addWidget(QLabel("Export Location:"))
        
        location_layout = QHBoxLayout()
        self.export_path = QLineEdit()
        if hasattr(self.parent(), 'export_path'):
            self.export_path.setText(self.parent().export_path.text())
        location_layout.addWidget(self.export_path)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_export_folder)
        location_layout.addWidget(self.browse_button)
        
        main_layout.addLayout(location_layout)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout()
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "TIFF", "DICOM"])
        options_layout.addRow("Format:", self.format_combo)
        
        # Rotation selection
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["0°", "90°", "180°", "270°"])
        options_layout.addRow("Rotation:", self.rotation_combo)
        
        # Duplicate file handling
        self.duplicate_combo = QComboBox()
        self.duplicate_combo.addItem("Overwrite", "overwrite")
        self.duplicate_combo.addItem("Skip", "skip")
        self.duplicate_combo.addItem("Create unique name", "unique")
        self.duplicate_combo.setToolTip(
            "What to do if a file with the same name already exists:\n"
            "- Overwrite: Replace existing files\n"
            "- Skip: Keep existing files, skip exporting\n"
            "- Create unique name: Append a number to create a new file"
        )
        options_layout.addRow("If file exists:", self.duplicate_combo)
        
        # Crop options
        self.crop_checkbox = QCheckBox("Crop images")
        self.crop_checkbox.toggled.connect(self.toggle_crop_controls)
        options_layout.addRow(self.crop_checkbox)
        
        # Crop parameters (initially hidden)
        self.crop_params_group = QGroupBox("Crop Parameters")
        crop_layout = QGridLayout()
        
        self.crop_top = QSpinBox()
        self.crop_top.setRange(0, 10000)
        self.crop_left = QSpinBox()
        self.crop_left.setRange(0, 10000)
        self.crop_width = QSpinBox()
        self.crop_width.setRange(1, 10000)
        self.crop_height = QSpinBox()
        self.crop_height.setRange(1, 10000)
        
        crop_layout.addWidget(QLabel("Top:"), 0, 0)
        crop_layout.addWidget(self.crop_top, 0, 1)
        crop_layout.addWidget(QLabel("Left:"), 0, 2)
        crop_layout.addWidget(self.crop_left, 0, 3)
        crop_layout.addWidget(QLabel("Width:"), 1, 0)
        crop_layout.addWidget(self.crop_width, 1, 1)
        crop_layout.addWidget(QLabel("Height:"), 1, 2)
        crop_layout.addWidget(self.crop_height, 1, 3)
        
        self.crop_params_group.setLayout(crop_layout)
        self.crop_params_group.setVisible(False)
        options_layout.addRow(self.crop_params_group)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # File naming
        naming_group = QGroupBox("Naming Convention:")
        naming_layout = QVBoxLayout(naming_group)
        
        # Naming convention
        naming_group = QGroupBox("Naming Convention:")
        naming_layout = QVBoxLayout(naming_group)
        
        self.original_radio = QRadioButton("Original filename + frame number")
        naming_layout.addWidget(self.original_radio)
        
        custom_layout = QHBoxLayout()
        self.custom_radio = QRadioButton("Custom prefix:")
        custom_layout.addWidget(self.custom_radio)
        
        self.prefix_edit = QLineEdit("OCT_Export_")
        custom_layout.addWidget(self.prefix_edit)
        custom_layout.addWidget(QLabel("+ frame number"))
        
        naming_layout.addLayout(custom_layout)
        
        # Set default naming convention
        self.custom_radio.setChecked(True)
        
        main_layout.addWidget(naming_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.accept)
        button_layout.addWidget(self.export_button)
        
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.rotation_checkbox.toggled.connect(self.toggle_rotation_combo)
        self.custom_radio.toggled.connect(self.toggle_prefix_edit)
    
    def browse_export_folder(self):
        """Browse for export folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder:
            self.export_path.setText(folder)
    
    def toggle_crop_controls(self, checked):
        """Enable or disable crop controls based on checkbox state."""
        self.crop_params_group.setVisible(checked)
    
    def toggle_prefix_edit(self, checked):
        """Enable or disable prefix edit based on radio button state."""
        self.prefix_edit.setEnabled(checked)
    
    def get_export_settings(self):
        """Get the export settings from the dialog."""
        # Get format
        format_str = self.format_combo.currentText()
        
        # Get rotation
        rotation = self.rotation_combo.currentText()
        
        # Get crop parameters
        crop_params = {
            'top': self.crop_top.value(),
            'left': self.crop_left.value(),
            'width': self.crop_width.value(),
            'height': self.crop_height.value()
        }
        
        # Get crop parameters from parent if available
        if hasattr(self.parent(), 'crop_top') and self.crop_checkbox.isChecked():
            crop_params = {
                'top': self.parent().crop_top.value(),
                'left': self.parent().crop_left.value(),
                'width': self.parent().crop_width.value(),
                'height': self.parent().crop_height.value()
            }
        
        # Get naming convention
        if self.custom_radio.isChecked():
            naming = {
                'type': 'custom',
                'prefix': self.prefix_edit.text()
            }
        else:
            naming = {
                'type': 'original'
            }
        
        # Build settings dictionary
        self.export_settings = {
            'export_dir': self.export_path.text(),
            'format': format_str,
            'rotation': rotation,
            'crop': self.crop_checkbox.isChecked(),
            'crop_params': crop_params,
            'naming': naming,
            'on_duplicate': self.duplicate_combo.currentData()
        }
        
        return self.export_settings
