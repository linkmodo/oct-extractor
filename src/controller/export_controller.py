#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export Controller Module
-----------------------
Controls file export operations for the OCT Image Extraction application.
"""

import os
import logging
import json
import numpy as np
from typing import Tuple, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ExportController:
    """Controller class for export operations."""
    
    def __init__(self, file_manager, oct_reader, image_controller=None):
        """
        Initialize the export controller.
        
        Args:
            file_manager: FileManager instance
            oct_reader: OCTFileReader instance
            image_controller: ImageController instance (optional)
        """
        self.file_manager = file_manager
        self.oct_reader = oct_reader
        self.image_controller = image_controller
    
    def set_export_directory(self, directory: str) -> Tuple[bool, str]:
        """
        Set the export directory.
        
        Args:
            directory: Path to the export directory
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        return self.file_manager.set_export_directory(directory)
    
    def get_export_directory(self) -> str:
        """
        Get the current export directory.
        
        Returns:
            str: Path to the export directory
        """
        return self.file_manager.get_export_directory()
    
    def export_frames(self, frames: List[Dict[str, Any]], export_dir: str, 
                     export_settings: Dict[str, Any], progress_callback=None) -> Tuple[bool, str]:
        """
        Export frames with specified settings.
        
        Args:
            frames: List of frame information dictionaries
            export_dir: Directory to export frames to
            export_settings: Dictionary with export settings
                - format: Export format (PNG, JPEG, TIFF, DICOM)
                - rotation: Rotation angle (0°, 90°, 180°, 270°)
                - crop: Boolean indicating whether to crop
                - crop_params: Dictionary with crop parameters (top, left, width, height)
                - on_duplicate: Action for duplicate files ('overwrite', 'skip', 'unique')
            progress_callback: Optional callback function to report progress (float 0-1)
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        """
        Export frames with specified settings.
        
        Args:
            frames: List of frame information dictionaries
            export_dir: Directory to export frames to
            export_settings: Dictionary with export settings
                - format: Export format (PNG, JPEG, TIFF, DICOM)
                - rotation: Rotation angle (0°, 90°, 180°, 270°)
                - crop: Boolean indicating whether to crop
                - crop_params: Dictionary with crop parameters (top, left, width, height)
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        # Validate export directory
        valid, message = self.file_manager.validate_directory(export_dir)
        if not valid:
            logger.error(f"Invalid export directory: {message}")
            return False, message
        
        # Set export directory
        self.file_manager.set_export_directory(export_dir)
        
        # Get duplicate handling option
        on_duplicate = export_settings.get('on_duplicate', 'overwrite')
        logger.info(f"Using duplicate file handling: {on_duplicate}")
        logger.info(f"Full export settings: {export_settings}")
        
        # Process and export each frame
        success_count = 0
        error_count = 0
        error_messages = []
        total_frames = len(frames)
        
        for i, frame in enumerate(frames):
            # Update progress if callback provided
            if progress_callback and callable(progress_callback):
                # If progress_callback returns False, cancel the export
                if not progress_callback(i / total_frames):
                    logger.info("Export canceled by user")
                    return False, "Export canceled by user"
            try:
                # Get file name and frame ID
                file_name = frame.get('file_name', '')
                frame_id = frame.get('id', '')
                
                if not file_name or not frame_id:
                    error_count += 1
                    error_message = f"Invalid frame information: {frame}"
                    error_messages.append(error_message)
                    logger.error(error_message)
                    continue
                
                # Get frame image data using the shared OCTFileReader instance
                logger.info(f"Exporting frame: {frame_id} from {file_name} (type: {frame.get('type', 'unknown')})")                
                image_data = self.oct_reader.get_frame_image(file_name, frame_id)
                
                if image_data is None:
                    error_count += 1
                    error_message = f"Could not get image data for frame: {frame_id} in file {file_name}"
                    error_messages.append(error_message)
                    logger.error(error_message)
                    continue
                    
                # Log image data shape and type to help with debugging
                logger.debug(f"Image data for {frame_id}: shape={image_data.shape}, dtype={image_data.dtype}")
                
                # Ensure the image data is in the correct format for saving
                if image_data.dtype != np.uint8 and export_format != 'DICOM':
                    logger.info(f"Converting {frame_id} from {image_data.dtype} to uint8")
                    # Normalize to 0-255 range for proper display
                    image_data = ((image_data - image_data.min()) / 
                                (image_data.max() - image_data.min() + 1e-10) * 255).astype(np.uint8)
                
                # Process image if image controller is available
                if self.image_controller:
                    image_data = self.image_controller.process_image(image_data, export_settings)
                
                # Determine export format
                export_format = export_settings.get('format', 'PNG')
                if export_format == 'DICOM':
                    # For DICOM export, use OCT-Converter's DICOM export
                    success, msg = self.oct_reader.export_to_dicom(file_name, export_dir)
                    if success:
                        success_count += 1
                        logger.info(f"Successfully exported {file_name} to DICOM")
                    else:
                        error_count += 1
                        error_messages.append(msg)
                        logger.error(f"Failed to export {file_name} to DICOM: {msg}")
                else:
                    # For image formats, save using file manager
                    output_file = os.path.join(
                        export_dir, 
                        f"{os.path.splitext(file_name)[0]}_{frame_id}.{export_format.lower()}"
                    )
                    
                    # Save with duplicate handling
                    logger.info(f"Attempting to save frame {frame_id} to {output_file} with on_duplicate={on_duplicate}")
                    success, msg, saved_path = self.file_manager.save_image(
                        image_data, 
                        output_file, 
                        export_format,
                        on_duplicate=on_duplicate
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(f"Successfully saved frame {frame_id} to {saved_path}")
                    elif "already exists, skipping" in msg:
                        logger.info(msg)  # Log as info for skipped files
                        continue  # Skip to next frame
                    else:
                        error_count += 1
                        error_messages.append(f"Failed to save frame {frame_id}: {msg}")
                        logger.error(f"Failed to save frame {frame_id}: {msg}")
                        continue
                    
                    # Export DICOM metadata if requested (only for successful saves)
                    if success and export_settings.get('export_metadata', False):
                            try:
                                # Get detailed metadata for the file
                                file_path = frame.get('file_path')
                                if file_path and file_path in self.oct_reader.loaded_files:
                                    file_obj = self.oct_reader.loaded_files[file_path]
                                    
                                    # Check if the object has DICOM metadata
                                    metadata_to_export = None
                                    if hasattr(file_obj, 'dicom_metadata') and file_obj.dicom_metadata:
                                        metadata_to_export = file_obj.dicom_metadata
                                    elif hasattr(file_obj, 'metadata') and file_obj.metadata:
                                        metadata_to_export = file_obj.metadata
                                    
                                    if metadata_to_export:
                                        # Create metadata file path
                                        metadata_file = os.path.join(
                                            export_dir,
                                            f"{os.path.splitext(file_name)[0]}_{frame_id}_metadata.json"
                                        )
                                        
                                        # Save metadata as JSON
                                        with open(metadata_file, 'w') as f:
                                            json.dump(metadata_to_export, f, indent=2, default=str)
                                        
                                        logger.info(f"Saved metadata to {metadata_file}")
                            except Exception as e:
                                logger.warning(f"Failed to export metadata for {frame_id}: {e}")
            
            except Exception as e:
                error_count += 1
                error_message = f"Error processing frame: {str(e)}"
                error_messages.append(error_message)
                logger.exception(f"Exception while processing frame: {e}")
        
        # Final progress update
        if progress_callback and callable(progress_callback):
            # Don't continue if the export was canceled at the last moment
            if not progress_callback(1.0):
                logger.info("Export canceled by user at final step")
                return False, "Export canceled by user"
        
        # Return results
        if error_count == 0:
            result_message = f"Successfully exported {success_count} frames to {export_dir}"
            logger.info(result_message)
            return True, result_message
        else:
            result_message = f"Exported {success_count} frames with {error_count} errors: {'; '.join(error_messages[:3])}"
            if len(error_messages) > 3:
                result_message += f" and {len(error_messages) - 3} more errors"
            logger.warning(result_message)
            return False, result_message
    
    def export_to_dicom(self, file_name: str, export_dir: str) -> Tuple[bool, str]:
        """
        Export an OCT file to DICOM format.
        
        Args:
            file_name: Name of the OCT file
            export_dir: Directory to export DICOM files to
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        # Validate export directory
        valid, message = self.file_manager.validate_directory(export_dir)
        if not valid:
            logger.error(f"Invalid export directory for DICOM export: {message}")
            return False, message
        
        # Export to DICOM using the shared OCTFileReader instance
        return self.oct_reader.export_to_dicom(file_name, export_dir)
