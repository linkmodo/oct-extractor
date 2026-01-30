#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Controller Module
---------------------
Controls file import operations for the OCT Image Extraction application.
"""

import os
import logging
from typing import Tuple, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class FileController:
    """Controller class for file operations."""
    
    def __init__(self, oct_reader, file_manager):
        """
        Initialize the file controller.
        
        Args:
            oct_reader: OCTFileReader instance
            file_manager: FileManager instance
        """
        self.oct_reader = oct_reader
        self.file_manager = file_manager
    
    def import_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Import an OCT file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        if not file_path:
            logger.error("Empty file path provided")
            return False, "No file path provided"
        
        try:
            # Validate file path
            valid, message = self.file_manager.validate_file_path(file_path)
            if not valid:
                logger.warning(f"File validation failed for {file_path}: {message}")
                return False, message
            
            # Check if file is supported
            if not self.oct_reader.is_supported_file(file_path):
                logger.warning(f"Unsupported file format: {file_path}")
                return False, f"Unsupported file format: {os.path.basename(file_path)}"
            
            # Load file
            success, message = self.oct_reader.load_file(file_path)
            if success:
                logger.info(f"Successfully imported file: {file_path}")
            else:
                logger.error(f"Failed to import file {file_path}: {message}")
            return success, message
            
        except Exception as e:
            error_msg = f"Unexpected error importing file: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg
    
    def import_files(self, file_paths: List[str]) -> List[Tuple[str, bool, str]]:
        """
        Import multiple OCT files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List[Tuple[str, bool, str]]: List of (file_name, success, message) tuples
        """
        results = []
        
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            success, message = self.import_file(file_path)
            results.append((file_name, success, message))
        
        return results
    
    def get_imported_files(self) -> List[str]:
        """
        Get a list of imported file names.
        
        Returns:
            List[str]: List of imported file names
        """
        try:
            return list(self.oct_reader.file_paths.keys())
        except Exception as e:
            logger.error(f"Error getting imported files: {e}")
            return []
    
    def get_file_metadata(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an imported file.
        
        Args:
            file_name: Name of the imported file
            
        Returns:
            Optional[Dict[str, Any]]: File metadata or None if not found
        """
        if not file_name:
            logger.warning("Empty file name provided to get_file_metadata")
            return None
            
        try:
            if file_name in self.oct_reader.file_metadata:
                return self.oct_reader.file_metadata[file_name]
            logger.debug(f"No metadata found for file: {file_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting metadata for {file_name}: {e}")
            return None
    
    def get_file_preview(self, file_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get a preview image and metadata for an imported file.
        
        Args:
            file_name: Name of the imported file
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (Preview image path, Metadata string)
        """
        if not file_name:
            logger.warning("Empty file name provided to get_file_preview")
            return None, None
            
        try:
            return self.oct_reader.get_preview(file_name)
        except Exception as e:
            logger.error(f"Error getting preview for {file_name}: {e}")
            return None, None
