#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frame Controller Module
----------------------
Controls frame selection operations for the OCT Image Extraction application.
"""

import os
from typing import Tuple, List, Dict, Any, Optional

class FrameController:
    """Controller class for frame operations."""
    
    def __init__(self, oct_reader):
        """
        Initialize the frame controller.
        
        Args:
            oct_reader: OCTFileReader instance
        """
        self.oct_reader = oct_reader
        self.selected_frames = {}  # Dictionary to store selected frames by file
    
    def get_available_frames(self, file_name: str) -> List[Dict[str, Any]]:
        """
        Get a list of available frames in a file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            List[Dict[str, Any]]: List of frame information dictionaries
        """
        frames = self.oct_reader.get_frames(file_name)
        
        # Add file name to each frame for reference
        for frame in frames:
            frame['file_name'] = file_name
        
        return frames
    
    def select_frame(self, file_name: str, frame_id: str) -> bool:
        """
        Select a frame for export.
        
        Args:
            file_name: Name of the loaded file
            frame_id: ID of the frame
            
        Returns:
            bool: True if successful, False otherwise
        """
        if file_name not in self.selected_frames:
            self.selected_frames[file_name] = []
        
        if frame_id not in self.selected_frames[file_name]:
            self.selected_frames[file_name].append(frame_id)
            return True
        
        return False
    
    def deselect_frame(self, file_name: str, frame_id: str) -> bool:
        """
        Deselect a frame.
        
        Args:
            file_name: Name of the loaded file
            frame_id: ID of the frame
            
        Returns:
            bool: True if successful, False otherwise
        """
        if file_name in self.selected_frames and frame_id in self.selected_frames[file_name]:
            self.selected_frames[file_name].remove(frame_id)
            return True
        
        return False
    
    def select_all_frames(self, file_name: str) -> int:
        """
        Select all frames in a file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            int: Number of frames selected
        """
        frames = self.get_available_frames(file_name)
        self.selected_frames[file_name] = [frame['id'] for frame in frames]
        return len(frames)
    
    def deselect_all_frames(self, file_name: str) -> int:
        """
        Deselect all frames in a file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            int: Number of frames deselected
        """
        count = 0
        if file_name in self.selected_frames:
            count = len(self.selected_frames[file_name])
            self.selected_frames[file_name] = []
        
        return count
    
    def get_selected_frames(self, file_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of selected frames.
        
        Args:
            file_name: Name of the loaded file (optional, if None returns all selected frames)
            
        Returns:
            List[Dict[str, Any]]: List of selected frame information dictionaries
        """
        selected = []
        
        if file_name:
            # Get selected frames for a specific file
            if file_name in self.selected_frames:
                for frame_id in self.selected_frames[file_name]:
                    selected.append({
                        'file_name': file_name,
                        'id': frame_id
                    })
        else:
            # Get all selected frames
            for file_name, frame_ids in self.selected_frames.items():
                for frame_id in frame_ids:
                    selected.append({
                        'file_name': file_name,
                        'id': frame_id
                    })
        
        return selected
    
    def is_frame_selected(self, file_name: str, frame_id: str) -> bool:
        """
        Check if a frame is selected.
        
        Args:
            file_name: Name of the loaded file
            frame_id: ID of the frame
            
        Returns:
            bool: True if selected, False otherwise
        """
        return file_name in self.selected_frames and frame_id in self.selected_frames[file_name]
    
    def get_preview(self, file_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get a preview image and metadata for a loaded file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (Preview image path, Metadata string)
        """
        return self.oct_reader.get_preview(file_name)
        
    def get_detailed_metadata(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a loaded file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            Optional[Dict[str, Any]]: Detailed metadata dictionary or None if not available
        """
        if file_name not in self.oct_reader.file_metadata:
            return None
            
        # Get the basic metadata
        metadata = self.oct_reader.file_metadata.get(file_name, {})
        
        # Create a more comprehensive metadata dictionary with additional information
        detailed_metadata = {}
        
        # Add basic metadata
        if 'file_type' in metadata:
            detailed_metadata['File Type'] = metadata['file_type']
        if 'dimensions' in metadata:
            detailed_metadata['Dimensions'] = metadata['dimensions']
        if 'patient' in metadata:
            detailed_metadata['Patient Information'] = metadata['patient']
        
        # Add OCT-specific metadata
        file_path = self.oct_reader.file_paths.get(file_name)
        if file_path and file_path in self.oct_reader.loaded_files:
            file_obj = self.oct_reader.loaded_files[file_path]
            
            # Try to extract additional metadata from the OCT file object
            try:
                if hasattr(file_obj, 'metadata') and file_obj.metadata:
                    detailed_metadata['OCT Metadata'] = file_obj.metadata
                    
                # Check for DICOM-related metadata
                if hasattr(file_obj, 'dicom_metadata') and file_obj.dicom_metadata:
                    detailed_metadata['DICOM Metadata'] = file_obj.dicom_metadata
            except Exception as e:
                pass  # Silently continue if we can't extract additional metadata
        
        return detailed_metadata
    
    def get_frame_image(self, file_name: str, frame_id: str) -> Optional[Any]:
        """
        Get the image data for a specific frame.
        
        Args:
            file_name: Name of the loaded file
            frame_id: ID of the frame
            
        Returns:
            Optional[Any]: Image data, or None if error
        """
        return self.oct_reader.get_frame_image(file_name, frame_id)
