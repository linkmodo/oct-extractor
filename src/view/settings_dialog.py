#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings Dialog
-------------
Dialog for configuring application settings and cropping parameters.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QGroupBox, QGridLayout, QSpinBox,
                           QCheckBox, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt
import json
import os

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        
        self.settings = {}
        self.presets = {}
        
        # Load existing settings and presets
        self.load_settings()
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # Cropping parameters
        crop_group = QGroupBox("Cropping Parameters:")
        crop_layout = QVBoxLayout(crop_group)
        
        self.crop_checkbox = QCheckBox("Enable cropping")
        if hasattr(self.parent(), 'crop_checkbox'):
            self.crop_checkbox.setChecked(self.parent().crop_checkbox.isChecked())
        crop_layout.addWidget(self.crop_checkbox)
        
        crop_params_layout = QGridLayout()
        
        crop_params_layout.addWidget(QLabel("Top:"), 0, 0)
        self.crop_top = QSpinBox()
        self.crop_top.setRange(0, 10000)
        if hasattr(self.parent(), 'crop_top'):
            self.crop_top.setValue(self.parent().crop_top.value())
        crop_params_layout.addWidget(self.crop_top, 0, 1)
        
        crop_params_layout.addWidget(QLabel("Left:"), 1, 0)
        self.crop_left = QSpinBox()
        self.crop_left.setRange(0, 10000)
        if hasattr(self.parent(), 'crop_left'):
            self.crop_left.setValue(self.parent().crop_left.value())
        crop_params_layout.addWidget(self.crop_left, 1, 1)
        
        crop_params_layout.addWidget(QLabel("Width:"), 2, 0)
        self.crop_width = QSpinBox()
        self.crop_width.setRange(1, 10000)
        if hasattr(self.parent(), 'crop_width'):
            self.crop_width.setValue(self.parent().crop_width.value())
        crop_params_layout.addWidget(self.crop_width, 2, 1)
        
        crop_params_layout.addWidget(QLabel("Height:"), 3, 0)
        self.crop_height = QSpinBox()
        self.crop_height.setRange(1, 10000)
        if hasattr(self.parent(), 'crop_height'):
            self.crop_height.setValue(self.parent().crop_height.value())
        crop_params_layout.addWidget(self.crop_height, 3, 1)
        
        crop_layout.addLayout(crop_params_layout)
        
        # Preset management
        preset_layout = QHBoxLayout()
        
        self.save_preset_checkbox = QCheckBox("Save as preset")
        preset_layout.addWidget(self.save_preset_checkbox)
        
        preset_layout.addWidget(QLabel("Preset name:"))
        
        self.preset_name = QLineEdit("Macular OCT Crop")
        preset_layout.addWidget(self.preset_name)
        
        crop_layout.addLayout(preset_layout)
        
        # Preset selection
        preset_select_layout = QHBoxLayout()
        preset_select_layout.addWidget(QLabel("Saved Presets:"))
        
        self.preset_combo = QComboBox()
        self.update_preset_combo()
        self.preset_combo.currentIndexChanged.connect(self.load_preset)
        preset_select_layout.addWidget(self.preset_combo)
        
        crop_layout.addLayout(preset_select_layout)
        
        main_layout.addWidget(crop_group)
        
        # Application settings
        app_group = QGroupBox("Application Settings:")
        app_layout = QVBoxLayout(app_group)
        
        # Auto-save settings
        self.auto_save = QCheckBox("Auto-save settings on exit")
        self.auto_save.setChecked(self.settings.get('auto_save', True))
        app_layout.addWidget(self.auto_save)
        
        # Default export format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default export format:"))
        
        self.default_format = QComboBox()
        self.default_format.addItems(["PNG", "JPEG", "TIFF", "DICOM"])
        self.default_format.setCurrentText(self.settings.get('default_format', "PNG"))
        format_layout.addWidget(self.default_format)
        
        app_layout.addLayout(format_layout)
        
        main_layout.addWidget(app_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.crop_checkbox.toggled.connect(self.toggle_crop_controls)
        self.save_preset_checkbox.toggled.connect(self.toggle_preset_name)
    
    def toggle_crop_controls(self, enabled):
        """Enable or disable crop controls based on checkbox state."""
        self.crop_top.setEnabled(enabled)
        self.crop_left.setEnabled(enabled)
        self.crop_width.setEnabled(enabled)
        self.crop_height.setEnabled(enabled)
        self.save_preset_checkbox.setEnabled(enabled)
        self.preset_name.setEnabled(enabled and self.save_preset_checkbox.isChecked())
        self.preset_combo.setEnabled(enabled)
    
    def toggle_preset_name(self, enabled):
        """Enable or disable preset name based on checkbox state."""
        self.preset_name.setEnabled(enabled)
    
    def update_preset_combo(self):
        """Update the preset combo box with available presets."""
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Select Preset --")
        
        for name in self.presets.keys():
            self.preset_combo.addItem(name)
    
    def load_preset(self, index):
        """Load a preset when selected from the combo box."""
        if index <= 0:
            return
        
        preset_name = self.preset_combo.currentText()
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            
            self.crop_top.setValue(preset.get('top', 0))
            self.crop_left.setValue(preset.get('left', 0))
            self.crop_width.setValue(preset.get('width', 100))
            self.crop_height.setValue(preset.get('height', 100))
    
    def load_settings(self):
        """Load settings and presets from file."""
        settings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "settings")
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_file = os.path.join(settings_dir, "settings.json")
        presets_file = os.path.join(settings_dir, "presets.json")
        
        # Load settings
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {}
        
        # Load presets
        if os.path.exists(presets_file):
            try:
                with open(presets_file, 'r') as f:
                    self.presets = json.load(f)
            except:
                self.presets = {}
    
    def save_settings(self):
        """Save settings and presets to file."""
        # Update settings
        self.settings['auto_save'] = self.auto_save.isChecked()
        self.settings['default_format'] = self.default_format.currentText()
        
        # Save preset if requested
        if self.crop_checkbox.isChecked() and self.save_preset_checkbox.isChecked():
            preset_name = self.preset_name.text()
            if preset_name:
                self.presets[preset_name] = {
                    'top': self.crop_top.value(),
                    'left': self.crop_left.value(),
                    'width': self.crop_width.value(),
                    'height': self.crop_height.value()
                }
        
        # Write to files
        settings_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "settings")
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_file = os.path.join(settings_dir, "settings.json")
        presets_file = os.path.join(settings_dir, "presets.json")
        
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            with open(presets_file, 'w') as f:
                json.dump(self.presets, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
        
        # Update parent window if available
        if self.parent():
            if hasattr(self.parent(), 'crop_checkbox'):
                self.parent().crop_checkbox.setChecked(self.crop_checkbox.isChecked())
            
            if hasattr(self.parent(), 'crop_top'):
                self.parent().crop_top.setValue(self.crop_top.value())
            
            if hasattr(self.parent(), 'crop_left'):
                self.parent().crop_left.setValue(self.crop_left.value())
            
            if hasattr(self.parent(), 'crop_width'):
                self.parent().crop_width.setValue(self.crop_width.value())
            
            if hasattr(self.parent(), 'crop_height'):
                self.parent().crop_height.setValue(self.crop_height.value())
            
            if hasattr(self.parent(), 'format_combo'):
                index = self.parent().format_combo.findText(self.default_format.currentText())
                if index >= 0:
                    self.parent().format_combo.setCurrentIndex(index)
        
        self.accept()
