#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Manager Module
------------------
Handles file system operations for the OCT Image Extraction application.
"""

import os
import shutil
from typing import Tuple, List, Dict, Any, Optional
import uuid
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

class FileManager:
    """Class for managing file system operations."""
    
    def __init__(self):
        """Initialize the file manager."""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.temp_dir = os.path.join(self.base_dir, "temp")
        self.export_dir = ""
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if a file path exists and is accessible.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple[bool, str]: (Valid, Message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Not a file: {file_path}"
        
        try:
            with open(file_path, 'rb') as f:
                # Try to read a small chunk to verify access
                f.read(1)
            return True, "File is valid and accessible"
        except Exception as e:
            return False, f"File access error: {str(e)}"
    
    def validate_directory(self, directory: str) -> Tuple[bool, str]:
        """
        Validate if a directory exists and is writable.
        
        Args:
            directory: Path to the directory
            
        Returns:
            Tuple[bool, str]: (Valid, Message)
        """
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                return True, "Directory created successfully"
            except Exception as e:
                return False, f"Could not create directory: {str(e)}"
        
        if not os.path.isdir(directory):
            return False, f"Not a directory: {directory}"
        
        # Check if directory is writable
        test_file = os.path.join(directory, f"test_{uuid.uuid4().hex}.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True, "Directory is valid and writable"
        except Exception as e:
            return False, f"Directory is not writable: {str(e)}"
    
    def set_export_directory(self, directory: str) -> Tuple[bool, str]:
        """
        Set the export directory.
        
        Args:
            directory: Path to the export directory
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        valid, message = self.validate_directory(directory)
        if valid:
            self.export_dir = directory
            return True, f"Export directory set to: {directory}"
        else:
            return False, message
    
    def get_export_directory(self) -> str:
        """
        Get the current export directory.
        
        Returns:
            str: Path to the export directory
        """
        return self.export_dir
    
    def create_temp_file(self, prefix: str = "temp", suffix: str = ".tmp") -> str:
        """
        Create a temporary file.
        
        Args:
            prefix: Prefix for the temporary file name
            suffix: Suffix for the temporary file name
            
        Returns:
            str: Path to the temporary file
        """
        temp_file = os.path.join(self.temp_dir, f"{prefix}_{uuid.uuid4().hex}{suffix}")
        return temp_file
    
    def save_image(self, image_data: Any, file_path: str, file_format: str = "PNG", 
                 on_duplicate: str = 'overwrite') -> Tuple[bool, str, str]:
        """
        Save image data to a file with duplicate handling.
        
        Args:
            image_data: Image data to save (numpy array or PIL Image)
            file_path: Path to save the image
            file_format: Format to save the image (PNG, JPEG, TIFF)
            on_duplicate: Action to take if file exists:
                        'overwrite' - Overwrite existing file
                        'skip' - Skip saving this file
                        'unique' - Create a unique filename by appending a number
            
        Returns:
            Tuple[bool, str, str]: 
                - Success (bool): True if file was saved
                - Message (str): Status message
                - Final path (str): Final path where file was saved (may differ from input)
        """
        logger.info(f"Saving image to {file_path} with format {file_format} and on_duplicate={on_duplicate}")
        try:
            from PIL import Image
            import numpy as np
            
            # Convert to PIL Image if numpy array
            if isinstance(image_data, np.ndarray):
                image = Image.fromarray(image_data)
            elif isinstance(image_data, Image.Image):
                image = image_data
            else:
                return False, "Unsupported image data type"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            final_path = file_path
            
            # Handle duplicate files
            if os.path.exists(file_path):
                logger.info(f"Duplicate file detected at {file_path}")
                if on_duplicate == 'skip':
                    logger.info(f"Skipping file due to on_duplicate='skip' setting")
                    return False, f"File already exists, skipping: {file_path}", file_path
                    
                elif on_duplicate == 'unique':
                    logger.info(f"Creating unique filename due to on_duplicate='unique' setting")
                    base, ext = os.path.splitext(file_path)
                    counter = 1
                    while os.path.exists(final_path):
                        final_path = f"{base}_{counter}{ext}"
                        counter += 1
                    logger.info(f"Created unique filename: {final_path}")
                    
                    # Update message to indicate a new filename was created
                    msg = f"File already exists, saved as: {os.path.basename(final_path)}"
                else:  # default to 'overwrite'
                    logger.info(f"Will overwrite existing file due to on_duplicate='overwrite' setting")
                    msg = f"Overwriting existing file: {file_path}"
            else:
                logger.info(f"No duplicate detected, saving normally")
                msg = f"Image saved to: {file_path}"
            
            # Save image
            image.save(final_path, format=file_format)
            return True, msg, final_path
        
        except Exception as e:
            return False, f"Error saving image: {str(e)}", file_path
    
    def clean_temp_directory(self) -> Tuple[bool, str]:
        """
        Clean the temporary directory.
        
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            return True, "Temporary directory cleaned successfully"
        
        except Exception as e:
            return False, f"Error cleaning temporary directory: {str(e)}"
