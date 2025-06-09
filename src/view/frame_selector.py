#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frame Selector Widget
--------------------
Widget for selecting frames from OCT files.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QGridLayout, QCheckBox, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import os
import numpy as np
from PIL import Image
import io

class FrameSelector(QWidget):
    """Widget for selecting frames from OCT files."""
    
    # Signal emitted when frame selection changes
    selectionChanged = pyqtSignal()
    # Signal emitted when a frame is clicked for preview
    framePreviewRequested = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize the frame selector widget."""
        super().__init__(parent)
        
        self.frames = []  # List of frame information dictionaries
        self.selected_frames = []  # List of selected frame IDs
        self.frame_widgets = {}  # Dictionary mapping frame IDs to widgets
        
        # Setup UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout for the entire widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all)
        button_layout.addWidget(self.deselect_all_button)
        
        self.invert_selection_button = QPushButton("Invert Selection")
        self.invert_selection_button.clicked.connect(self.invert_selection)
        button_layout.addWidget(self.invert_selection_button)
        
        main_layout.addLayout(button_layout)
        
        # Create scroll area that will contain all frames
        self.scroll_area = QScrollArea()
        self.scroll_area.setFrameShape(QScrollArea.StyledPanel)
        self.scroll_area.setWidgetResizable(True)  # IMPORTANT: Allow widget to resize
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Always show vertical scrollbar
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Frame container widget
        self.frame_container = QWidget()
        
        # Create a flow layout for the frames
        self.frame_layout = QVBoxLayout(self.frame_container)
        self.frame_layout.setContentsMargins(2, 2, 2, 2)
        self.frame_layout.setSpacing(2)
        self.frame_layout.setAlignment(Qt.AlignTop)  # Important: Align frames to top
        
        # Set the container widget as the scroll area's widget
        self.scroll_area.setWidget(self.frame_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(self.scroll_area, 1)  # Give stretch factor to ensure it expands
        
    def set_frames(self, frames):
        """
        Set the frames to display.
        
        Args:
            frames: List of frame information dictionaries
        """
        self.frames = frames
        self.selected_frames = []
        self.frame_widgets = {}
        
        # Clear existing frames from layout
        while self.frame_layout.count():
            item = self.frame_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Create a multi-column flow layout using a grid
        flow_widget = QWidget()
        flow_layout = QGridLayout(flow_widget)
        flow_layout.setContentsMargins(2, 2, 2, 2)
        flow_layout.setSpacing(2)
        
        # Add frames to the flow layout
        row, col = 0, 0
        max_cols = 10  # Increased number of columns to fit more frames horizontally
        
        for i, frame in enumerate(frames):
            frame_widget = self._create_frame_widget(frame)
            flow_layout.addWidget(frame_widget, row, col)
            
            # Update row and column
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Add the flow widget to the main frame layout
        self.frame_layout.addWidget(flow_widget)
        
        # Emit signal
        self.selectionChanged.emit()
    
    def _create_frame_widget(self, frame):
        """
        Create a widget for a frame.
        
        Args:
            frame: Frame information dictionary
            
        Returns:
            QWidget: Frame widget
        """
        frame_id = frame['id']
        
        # Create widget
        frame_widget = QWidget()
        frame_widget.setStyleSheet("QWidget:hover { background-color: #e0e0e0; }")
        frame_widget.setMaximumWidth(120)  # Limit maximum width
        frame_layout = QHBoxLayout(frame_widget)
        frame_layout.setContentsMargins(2, 1, 2, 1)  # Minimal margins
        frame_layout.setSpacing(1)  # Minimal spacing
        
        # Checkbox for selection
        checkbox = QCheckBox()
        checkbox.setChecked(False)
        checkbox.setStyleSheet("QCheckBox { margin: 0; padding: 0; }")
        checkbox.stateChanged.connect(lambda state, fid=frame_id: self._on_frame_selected(fid, state))
        
        # Create a widget for frame info
        frame_info_widget = QWidget()
        frame_info_layout = QVBoxLayout(frame_info_widget)
        frame_info_layout.setContentsMargins(0, 0, 0, 0)
        frame_info_layout.setSpacing(0)
        
        # Label for frame ID
        id_label = QLabel(frame_id)
        id_label.setStyleSheet("font-weight: bold; font-size: 8pt;")
        frame_info_layout.addWidget(id_label)
        
        # Label for showing frame type
        if 'type' in frame:
            type_text = f"{frame['type']}"
            type_label = QLabel(type_text)
            type_label.setStyleSheet("font-size: 7pt; color: #666;")
            frame_info_layout.addWidget(type_label)
        
        # Add to main layout
        frame_layout.addWidget(checkbox)
        frame_layout.addWidget(frame_info_widget, 1)  # Give the info widget stretch
        
        # Store widget reference
        self.frame_widgets[frame_id] = {
            'widget': frame_widget,
            'checkbox': checkbox,
            'label': id_label,
            'frame_data': frame  # Store the frame data for easy access
        }
        
        return frame_widget
    
    def _on_frame_clicked(self, event, frame):
        """
        Handle frame click for preview.
        
        Args:
            event: Mouse event
            frame: Frame data dictionary
        """
        # Emit signal with the frame data to request a preview
        self.framePreviewRequested.emit(frame)
    
    def _on_frame_selected(self, frame_id, state):
        """
        Handle frame selection change.
        
        Args:
            frame_id: ID of the frame
            state: Checkbox state
        """
        if state == Qt.Checked:
            if frame_id not in self.selected_frames:
                self.selected_frames.append(frame_id)
        else:
            if frame_id in self.selected_frames:
                self.selected_frames.remove(frame_id)
        
        # Emit signal
        self.selectionChanged.emit()
    
    def select_all(self):
        """Select all frames."""
        self.selected_frames = [frame['id'] for frame in self.frames]
        
        # Update checkboxes
        for frame_id, widgets in self.frame_widgets.items():
            widgets['checkbox'].setChecked(True)
        
        # Emit signal
        self.selectionChanged.emit()
    
    def deselect_all(self):
        """Deselect all frames."""
        self.selected_frames = []
        
        # Update checkboxes
        for frame_id, widgets in self.frame_widgets.items():
            widgets['checkbox'].setChecked(False)
        
        # Emit signal
        self.selectionChanged.emit()
    
    def invert_selection(self):
        """Invert the current selection."""
        all_frame_ids = [frame['id'] for frame in self.frames]
        self.selected_frames = [fid for fid in all_frame_ids if fid not in self.selected_frames]
        
        # Update checkboxes
        for frame_id, widgets in self.frame_widgets.items():
            widgets['checkbox'].setChecked(frame_id in self.selected_frames)
        
        # Emit signal
        self.selectionChanged.emit()
    
    def get_selected_frames(self):
        """
        Get the selected frames.
        
        Returns:
            List[Dict[str, Any]]: List of selected frame information dictionaries
        """
        selected = []
        
        for frame in self.frames:
            if frame['id'] in self.selected_frames:
                selected.append(frame)
        
        return selected
    
    def set_frame_preview(self, frame_id, image_data):
        """
        Set a preview image for a frame.
        
        Args:
            frame_id: ID of the frame
            image_data: Image data as numpy array
        """
        if frame_id not in self.frame_widgets:
            return
        
        widgets = self.frame_widgets[frame_id]
        
        # Convert image data to QPixmap
        if isinstance(image_data, np.ndarray):
            # Convert numpy array to PIL Image
            image = Image.fromarray(image_data)
            
            # Convert PIL Image to QPixmap
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_buffer.getvalue())
            
            # Create or update image label
            if 'image' not in widgets:
                image_label = QLabel()
                image_label.setFixedSize(100, 100)
                image_label.setScaledContents(True)
                widgets['layout'].insertWidget(1, image_label)
                widgets['image'] = image_label
            
            widgets['image'].setPixmap(pixmap)
