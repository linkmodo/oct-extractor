#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCT File Reader Module
---------------------
Handles reading and parsing of OCT files using the OCT-Converter library.
Supports both Zeiss Cirrus OCT RAW (.img) files and Heidelberg OCT (.e2e) files.
"""

import os
import json
import tempfile
import shutil
import logging
from typing import Tuple, List, Dict, Any, Optional, Union
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Import OCT-Converter library
try:
    import pkg_resources
    from oct_converter.readers import E2E, IMG, FDS, FDA, BOCT, POCT
    from oct_converter.readers import BOCT as OCT  # Alias BOCT as OCT for backward compatibility
    from oct_converter.readers import POCT as OCTRAW  # Alias POCT as OCTRAW for backward compatibility
    from oct_converter.dicom import create_dicom_from_oct
    
    # Check OCT-Converter version
    required_version = "0.4.0"
    current_version = pkg_resources.get_distribution("oct-converter").version
    if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(required_version):
        logger.warning(f"OCT-Converter version {current_version} may be outdated. Version {required_version} or higher is recommended.")
    
    logger.info(f"OCT-Converter version {current_version} loaded successfully")
    
except ImportError as e:
    error_msg = "OCT-Converter library not found. Please install it using: pip install oct-converter"
    logger.error(error_msg)
    raise ImportError(error_msg) from e

class OCTFileReader:
    """Class for reading and parsing OCT files."""
    
    def __init__(self):
        """Initialize the OCT file reader."""
        self.loaded_files = {}  # Dictionary to store loaded file objects by full path
        self.file_paths = {}    # Dictionary to map file names to full paths
        self.file_metadata = {}  # Dictionary to store file metadata by file name
        self.supported_extensions = [
            '.e2e', '.E2E',  # Heidelberg
            '.img', '.IMG',  # Zeiss
            '.fds', '.FDS',  # Topcon
            '.fda', '.FDA',  # Topcon
            '.oct', '.OCT',  # Bioptigen / Optovue
            '.dcm', '.DCM'   # DICOM
        ]
        self.temp_files = []  # Track temporary files for cleanup
        
        # Create a dedicated temp directory for this instance
        self.temp_dir = tempfile.mkdtemp(prefix="oct_extractor_")
        logger.debug(f"Created temporary directory: {self.temp_dir}")
        
    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        self.cleanup_temp_files()
    
    def cleanup_temp_files(self):
        """Clean up all temporary files and directories."""
        # Clean up individual temp files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_file}: {e}")
        
        # Clear the list
        self.temp_files = []
        
        # Clean up temp directory
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Removed temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory {self.temp_dir}: {e}")
            
    def _create_temp_file(self, prefix="", suffix=""):
        """Create a temporary file and track it for later cleanup.
        
        Args:
            prefix: Optional prefix for the temporary filename
            suffix: Optional suffix for the temporary filename (e.g., '.png')
            
        Returns:
            str: Path to the temporary file
        """
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=self.temp_dir)
        os.close(fd)  # Close the file descriptor
        self.temp_files.append(temp_path)
        return temp_path
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if the file is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if the file is supported, False otherwise
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower() in [x.lower() for x in self.supported_extensions]
    
    def get_file_type(self, file_path: str) -> str:
        """
        Get the type of OCT file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: File type identifier based on extension
                - 'e2e': Heidelberg files (.e2e)
                - 'img': Zeiss files (.img) 
                - 'fds': Topcon files (.fds)
                - 'fda': Topcon files (.fda)
                - 'oct': Bioptigen files (.oct)
                - 'octraw': Optovue files (.OCT)
                - 'dcm': DICOM files (.dcm)
        """
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()
        
        if ext_lower == '.e2e':
            return 'e2e'
        elif ext_lower == '.img':
            return 'img'
        elif ext_lower == '.fds':
            return 'fds'
        elif ext_lower == '.fda':
            return 'fda'
        elif ext_lower == '.oct':
            return 'oct'
        elif ext_lower == '.dcm':
            return 'dcm'
        # Special case for .OCT files (Optovue)
        elif ext == '.OCT':
            return 'octraw'
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
    
    def load_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Load an OCT file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        try:
            # Normalize path for consistent lookup - using pathlib.Path like oct_converter does
            from pathlib import Path
            file_path_obj = Path(file_path)
            file_path = str(file_path_obj.absolute())
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return False, f"File not found: {file_path}"
            
            if not self.is_supported_file(file_path):
                logger.error(f"Unsupported file type: {file_path}")
                return False, f"Unsupported file type: {file_path}"
            
            file_type = self.get_file_type(file_path)
            file_name = file_path_obj.name
            
            logger.info(f"Loading OCT file: {file_name} ({file_type}) from {file_path}")
            
            # Store the mapping from file name to file path
            self.file_paths[file_name] = file_path
            
            # Load the file based on its type - Direct instantiation like in the oct_converter example
            try:
                if file_type == 'e2e':
                    # Using filepath directly as E2E class expects
                    self.loaded_files[file_path] = E2E(file_path)
                    logger.info(f"Successfully loaded E2E file {file_name}")
                elif file_type == 'img':
                    self.loaded_files[file_path] = IMG(file_path)
                    logger.info(f"Successfully loaded IMG file {file_name}")
                elif file_type == 'fds':
                    self.loaded_files[file_path] = FDS(file_path)
                    logger.info(f"Successfully loaded FDS file {file_name}")
                elif file_type == 'fda':
                    self.loaded_files[file_path] = FDA(file_path)
                    logger.info(f"Successfully loaded FDA file {file_name}")
                elif file_type == 'oct':
                    self.loaded_files[file_path] = OCT(file_path)
                    logger.info(f"Successfully loaded OCT file {file_name}")
                elif file_type == 'octraw':
                    self.loaded_files[file_path] = OCTRAW(file_path)
                    logger.info(f"Successfully loaded OCTRAW file {file_name}")
                elif file_type == 'dcm':
                    # DICOM files might require special handling
                    # For now, we'll just load it as a basic object
                    self.loaded_files[file_path] = {'file_path': file_path, 'file_type': 'dcm'}
                    logger.info(f"Successfully loaded DICOM file {file_name}")
            except Exception as e:
                logger.error(f"Error loading OCT file {file_path}: {e}", exc_info=True)
                return False, f"Error loading OCT file: {str(e)}"
            
            # Extract and store metadata
            try:
                # Most OCT-Converter readers have read_all_metadata method
                if file_type in ['e2e', 'fds', 'fda', 'oct', 'octraw']:
                    # Use read_all_metadata when available
                    if hasattr(self.loaded_files[file_path], 'read_all_metadata'):
                        metadata = self.loaded_files[file_path].read_all_metadata()
                        self.file_metadata[file_name] = metadata
                        logger.debug(f"Extracted metadata for {file_name} using read_all_metadata()")
                    else:
                        # Fallback to basic metadata if method not available
                        self.file_metadata[file_name] = {
                            "file_type": file_type.upper(),
                            "file_name": file_name,
                            "file_path": file_path
                        }
                        logger.debug(f"Created basic metadata for {file_type.upper()} file {file_name}")
                else:
                    # For other files, create basic metadata
                    self.file_metadata[file_name] = {
                        "file_type": file_type.upper(),
                        "file_name": file_name,
                        "file_path": file_path
                    }
                    logger.debug(f"Created basic metadata for {file_type.upper()} file {file_name}")
            except Exception as e:
                logger.warning(f"Error extracting metadata for {file_name}: {e}", exc_info=True)
                self.file_metadata[file_name] = {
                    "file_type": file_type.upper(),
                    "file_name": file_name,
                    "file_path": file_path,
                    "error": f"Error extracting metadata: {str(e)}"
                }
            
            return True, f"Successfully loaded {file_name}"
        
        except Exception as e:
            logger.error(f"Unhandled error loading file {file_path}: {e}", exc_info=True)
            return False, f"Error loading file: {str(e)}"
    
    def _extract_metadata(self, file_name: str) -> Dict[str, Any]:
        """
        Extract metadata from a loaded file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            Dict[str, Any]: Metadata dictionary
        """
        if file_name not in self.file_paths:
            logger.error(f"File path not found for: {file_name}")
            raise ValueError(f"File not loaded: {file_name}")
        
        file_path = self.file_paths[file_name]
        if file_path not in self.loaded_files:
            logger.error(f"File object not found for path: {file_path}")
            raise ValueError(f"File not loaded correctly: {file_path}")
        
        file_obj = self.loaded_files[file_path]
        
        try:
            # Extract metadata based on file type
            if isinstance(file_obj, E2E):
                logger.debug(f"Extracting metadata for E2E file: {file_name}")
                metadata = file_obj.read_all_metadata()
                # Add basic file information
                metadata.update({
                    "file_type": "Heidelberg OCT E2E",
                    "file_name": file_name,
                    "file_path": file_path
                })
            elif isinstance(file_obj, IMG):
                logger.debug(f"Extracting metadata for IMG file: {file_name}")
                # For IMG files, we have limited metadata
                metadata = {
                    "file_type": "Zeiss Cirrus OCT RAW",
                    "file_name": file_name,
                    "file_path": file_path
                }
                
                # Try to extract more metadata if available
                try:
                    oct_volume = file_obj.read_oct_volume()
                    if hasattr(oct_volume, 'metadata'):
                        metadata.update(oct_volume.metadata)
                except Exception as e:
                    logger.warning(f"Could not extract volume metadata from IMG file: {e}")
            else:
                logger.warning(f"Unknown file type for metadata extraction: {type(file_obj)}")
                metadata = {
                    "file_type": "Unknown",
                    "file_name": file_name,
                    "file_path": file_path
                }
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error extracting metadata for {file_name}: {str(e)}", exc_info=True)
            return {
                "file_type": "Unknown",
                "file_name": file_name,
                "file_path": file_path,
                "error": str(e)
            }
    
    def get_preview(self, file_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get a preview image and metadata for a loaded file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (Preview image path, Metadata string)
        """
        if file_name not in self.file_paths:
            logger.warning(f"Requested preview for non-loaded file: {file_name}")
            return None, None
            
        file_path = self.file_paths[file_name]
        if file_path not in self.loaded_files:
            logger.error(f"File object not found for path: {file_path}")
            return None, None
        
        file_obj = self.loaded_files[file_path]
        preview_path = None
        metadata_str = None
        
        try:
            # Generate preview based on file type
            if isinstance(file_obj, E2E):
                # For E2E files, try to get a fundus image first
                try:
                    logger.debug(f"Attempting to read fundus image from {file_name}")
                    fundus_images = file_obj.read_fundus_image()
                    if fundus_images and len(fundus_images) > 0:
                        # Create a temporary file for the preview
                        preview_path = self._create_temp_file(prefix=f"{file_name}_fundus_", suffix=".png")
                        fundus_images[0].save(preview_path)
                        logger.debug(f"Created fundus preview image for {file_name}")
                except Exception as e:
                    logger.debug(f"Could not create fundus preview for {file_name}: {e}")
                
                # If no fundus image, use first OCT volume
                if not preview_path:
                    try:
                        logger.debug(f"Attempting to read OCT volume from {file_name}")
                        oct_volumes = file_obj.read_oct_volume()
                        if oct_volumes and len(oct_volumes) > 0:
                            # Create a temporary file for the preview
                            preview_path = self._create_temp_file(prefix=f"{file_name}_oct_", suffix=".png")
                            oct_volumes[0].save_projection(preview_path)
                            logger.debug(f"Created OCT volume projection preview for {file_name}")
                    except Exception as e:
                        logger.debug(f"Could not create OCT volume preview for {file_name}: {e}")
            
            elif isinstance(file_obj, IMG):
                # For IMG files, use OCT volume
                try:
                    logger.debug(f"Attempting to read OCT volume from IMG file {file_name}")
                    oct_volume = file_obj.read_oct_volume()
                    # Create a temporary file for the preview
                    preview_path = self._create_temp_file(prefix=f"{file_name}_img_", suffix=".png")
                    oct_volume.save_projection(preview_path)
                    logger.debug(f"Created IMG file preview for {file_name}")
                except Exception as e:
                    logger.warning(f"Could not create IMG file preview for {file_name}: {e}")
            
            # Format metadata as string
            if file_name in self.file_metadata:
                metadata = self.file_metadata[file_name]
                try:
                    metadata_str = json.dumps(metadata, indent=2)
                except Exception as e:
                    logger.warning(f"Failed to convert metadata to JSON for {file_name}: {e}")
                    metadata_str = f"{{\"error\": \"Failed to format metadata: {str(e)}\"}}"
            
            if not preview_path:
                logger.warning(f"Failed to generate any preview for {file_name}")
            
            return preview_path, metadata_str
        
        except Exception as e:
            logger.error(f"Error generating preview for {file_name}: {str(e)}", exc_info=True)
            return None, f"Error: {str(e)}"
    
    def get_frames(self, file_name: str) -> List[Dict[str, Any]]:
        """
        Get a list of available frames in the file.
        
        Args:
            file_name: Name of the loaded file
            
        Returns:
            List[Dict[str, Any]]: List of frame information dictionaries
        """
        if file_name not in self.file_paths:
            logger.warning(f"Attempted to get frames for non-loaded file: {file_name}")
            return []
            
        file_path = self.file_paths[file_name]
        if file_path not in self.loaded_files:
            logger.error(f"File object not found for path: {file_path}")
            return []
        
        file_obj = self.loaded_files[file_path]
        frames = []
        
        try:
            # Extract frames based on file type
            if isinstance(file_obj, E2E):
                try:
                    # For E2E files, get OCT volumes directly
                    logger.debug(f"Reading OCT volumes from {file_name}")
                    oct_volumes = file_obj.read_oct_volume()
                    logger.info(f"Successfully read {len(oct_volumes)} OCT volumes from {file_name}")
                    
                    # Process each volume
                    for i, volume in enumerate(oct_volumes):
                        if not hasattr(volume, 'volume') or volume.volume is None:
                            logger.warning(f"Volume {i} has no volume data")
                            continue
                            
                        # Check if volume.volume is a list or numpy array
                        if isinstance(volume.volume, list):
                            # Handle case where volume.volume is a list
                            slices_count = len(volume.volume)
                            logger.debug(f"Processing volume {i} with {slices_count} slices (list type)")
                        else:
                            # Assume it's a numpy array
                            slices_count = volume.volume.shape[0]
                            logger.debug(f"Processing volume {i} with {slices_count} slices, shape: {volume.volume.shape}")
                        
                        # Get volume_id and laterality from the volume if available
                        volume_id = getattr(volume, 'volume_id', f"vol{i}")
                        laterality = getattr(volume, 'laterality', 'Unknown')
                        logger.debug(f"Volume {i} ID: {volume_id}, laterality: {laterality}")
                    
                        for j in range(slices_count):
                            frames.append({
                                'id': f"vol{i}_slice{j}",
                                'file_name': file_name,
                                'file_path': file_path,
                                'type': 'oct',
                                'volume_id': i,
                                'slice_id': j,
                                'volume_obj_id': volume_id,
                                'laterality': laterality
                            })
                    logger.debug(f"Extracted OCT slices from E2E file {file_name}")
                except Exception as e:
                    logger.error(f"Failed to extract OCT volumes from E2E file {file_name}: {e}", exc_info=True)
                
                try:
                    # Also get fundus images from E2E files
                    logger.debug(f"Reading fundus images from E2E file {file_name}")
                    fundus_images = file_obj.read_fundus_image()
                    logger.info(f"Successfully read {len(fundus_images)} fundus images from E2E file {file_name}")
                    
                    for i, image in enumerate(fundus_images):
                        # Get image_id and laterality from the image if available
                        image_id = getattr(image, 'image_id', f"fundus{i}")
                        laterality = getattr(image, 'laterality', 'Unknown')
                        logger.debug(f"Fundus image {i} ID: {image_id}, laterality: {laterality}")
                        
                        frames.append({
                            'id': f"fundus{i}",
                            'file_name': file_name,
                            'file_path': file_path,
                            'type': 'fundus',
                            'image_id': i,
                            'image_obj_id': image_id,
                            'laterality': laterality
                        })
                    logger.debug(f"Extracted {len(fundus_images)} fundus images from E2E file {file_name}")
                except Exception as e:
                    logger.error(f"Failed to extract fundus images from E2E file {file_name}: {e}")
            
            elif isinstance(file_obj, IMG):
                try:
                    # For IMG files, get OCT volume directly
                    logger.debug(f"Reading OCT volume from IMG file {file_name}")
                    oct_volume = file_obj.read_oct_volume()
                    
                    if not hasattr(oct_volume, 'volume') or oct_volume.volume is None:
                        logger.warning(f"IMG file {file_name} has no volume data")
                        return frames
                
                    # Add each slice as a separate frame
                    slices_count = oct_volume.volume.shape[0]
                    laterality = getattr(oct_volume, 'laterality', 'Unknown')
                    logger.debug(f"Processing IMG volume with {slices_count} slices, shape: {oct_volume.volume.shape}, laterality: {laterality}")
                    
                    for j in range(slices_count):
                        frames.append({
                            'id': f"slice{j}",
                            'file_name': file_name,
                            'file_path': file_path,
                            'type': 'oct',
                            'slice_id': j,
                            'laterality': laterality
                        })
                    logger.info(f"Extracted {slices_count} slices from IMG file {file_name}")
                except Exception as e:
                    logger.error(f"Failed to extract OCT volume from IMG file {file_name}: {e}", exc_info=True)
            
            elif isinstance(file_obj, FDS) or isinstance(file_obj, FDA):
                try:
                    # For Topcon files, get OCT volume
                    logger.debug(f"Reading OCT volume from Topcon file {file_name}")
                    oct_volume = file_obj.read_oct_volume()
                    
                    if not hasattr(oct_volume, 'volume') or oct_volume.volume is None:
                        logger.warning(f"Topcon file {file_name} has no volume data")
                    else:
                        # Add each slice as a separate frame
                        slices_count = oct_volume.volume.shape[0]
                        laterality = getattr(oct_volume, 'laterality', 'Unknown')
                        logger.debug(f"Processing Topcon volume with {slices_count} slices, shape: {oct_volume.volume.shape}, laterality: {laterality}")
                        
                        for j in range(slices_count):
                            frames.append({
                                'id': f"slice{j}",
                                'file_name': file_name,
                                'file_path': file_path,
                                'type': 'oct',
                                'slice_id': j,
                                'laterality': laterality
                            })
                        logger.info(f"Extracted {slices_count} OCT slices from Topcon file {file_name}")
                    
                    # Try to get fundus image
                    try:
                        logger.debug(f"Reading fundus image from Topcon file {file_name}")
                        fundus_image = file_obj.read_fundus_image()
                        if fundus_image is not None:
                            frames.append({
                                'id': "fundus0",
                                'file_name': file_name,
                                'file_path': file_path,
                                'type': 'fundus',
                                'image_id': 0,
                                'laterality': getattr(fundus_image, 'laterality', 'Unknown')
                            })
                            logger.debug(f"Extracted fundus image from Topcon file {file_name}")
                    except Exception as e:
                        logger.warning(f"Failed to extract fundus image from Topcon file {file_name}: {e}")
                except Exception as e:
                    logger.error(f"Failed to extract OCT volume from Topcon file {file_name}: {e}", exc_info=True)
        
            elif isinstance(file_obj, OCT) or isinstance(file_obj, OCTRAW):
                try:
                    # For Bioptigen/Optovue files, get OCT volume
                    file_type_name = type(file_obj).__name__
                    logger.debug(f"Reading OCT volume from {file_type_name} file {file_name}")
                    oct_volume = file_obj.read_oct_volume()
                    
                    if not hasattr(oct_volume, 'volume') or oct_volume.volume is None:
                        logger.warning(f"{file_type_name} file {file_name} has no volume data")
                    else:
                        # Add each slice as a separate frame
                        slices_count = oct_volume.volume.shape[0]
                        laterality = getattr(oct_volume, 'laterality', 'Unknown')
                        logger.debug(f"Processing {file_type_name} volume with {slices_count} slices, shape: {oct_volume.volume.shape}, laterality: {laterality}")
                        
                        for j in range(slices_count):
                            frames.append({
                                'id': f"slice{j}",
                                'file_name': file_name,
                                'file_path': file_path,
                                'type': 'oct',
                                'slice_id': j,
                                'laterality': laterality
                            })
                        logger.info(f"Extracted {slices_count} OCT slices from {file_type_name} file {file_name}")
                except Exception as e:
                    logger.error(f"Failed to extract OCT volume from {type(file_obj).__name__} file {file_name}: {e}", exc_info=True)
            
            elif isinstance(file_obj, dict) and file_obj.get('file_type') == 'dcm':
                # Handle DICOM files - for now just create a placeholder
                try:
                    frames.append({
                        'id': "dicom0",
                        'file_name': file_name,
                        'file_path': file_path,
                        'type': 'dicom',
                        'image_id': 0,
                        'laterality': 'Unknown'
                    })
                    logger.debug(f"Added placeholder frame for DICOM file {file_name}")
                except Exception as e:
                    logger.error(f"Failed to process DICOM file {file_name}: {e}", exc_info=True)
            
            if not frames:
                logger.warning(f"No frames were extracted from {file_name}")
            else:
                logger.info(f"Successfully extracted {len(frames)} total frames from {file_name}")
            
            return frames
        
        except Exception as e:
            logger.error(f"Error getting frames from {file_name}: {e}", exc_info=True)
            return []
    def get_frame_image(self, file_name: str, frame_id: str) -> Optional[np.ndarray]:
        """
        Get the image data for a specific frame.
        
        Args:
            file_name: Name of the loaded file
            frame_id: ID of the frame
            
        Returns:
            Optional[np.ndarray]: Image data as numpy array, or None if error
        """
        if file_name not in self.file_paths:
            logger.warning(f"Cannot get frame image: file '{file_name}' not loaded")
            return None
            
        file_path = self.file_paths[file_name]
        if file_path not in self.loaded_files:
            logger.error(f"File object not found for path: {file_path}")
            return None
        
        file_obj = self.loaded_files[file_path]
        logger.debug(f"Getting frame {frame_id} from file {file_name} (path: {file_path})")
        
        try:
            # Extract frame based on file type and frame ID
            if isinstance(file_obj, E2E):
                if frame_id.startswith('vol'):
                    try:
                        # Parse the volume and slice IDs from the frame_id
                        parts = frame_id.split('_')
                        volume_id = int(parts[0][3:])
                        slice_id = int(parts[1][5:])
                        
                        # Read all OCT volumes (following the example code)
                        logger.debug(f"Reading OCT volumes for {file_name} to access volume {volume_id}, slice {slice_id}")
                        oct_volumes = file_obj.read_oct_volume()
                        
                        if volume_id >= len(oct_volumes):
                            logger.warning(f"Volume index {volume_id} out of bounds in {file_name}. Available volumes: {len(oct_volumes)}")
                            return None
                            
                        volume = oct_volumes[volume_id]
                        if not hasattr(volume, 'volume') or volume.volume is None:
                            logger.warning(f"Volume {volume_id} in {file_name} has no 'volume' attribute or is None")
                            return None
                            
                        # Check if volume.volume is a list or numpy array
                        if isinstance(volume.volume, list):
                            # Handle case where volume.volume is a list
                            if slice_id >= len(volume.volume):
                                logger.warning(f"Slice index {slice_id} out of bounds for volume {volume_id} in {file_name}. "
                                               f"Volume length: {len(volume.volume)}")
                                return None
                                
                            # Get the slice data from the list
                            slice_data = volume.volume[slice_id]
                            logger.debug(f"Successfully retrieved OCT slice {slice_id} from volume {volume_id} of {file_name} (list type).")
                            
                            # If the slice_data isn't already a numpy array, convert it to one
                            if not isinstance(slice_data, np.ndarray):
                                try:
                                    # Try to convert to numpy array
                                    slice_data = np.array(slice_data)
                                    logger.debug(f"Converted list slice to numpy array with shape: {slice_data.shape}, dtype: {slice_data.dtype}")
                                except Exception as e:
                                    logger.error(f"Failed to convert list slice to numpy array: {e}")
                                    return None
                        else:
                            # Original case where volume.volume is a numpy array
                            if slice_id >= volume.volume.shape[0]:
                                logger.warning(f"Slice index {slice_id} out of bounds for volume {volume_id} in {file_name}. "
                                               f"Volume shape: {volume.volume.shape}")
                                return None
                                
                            # Get the slice data from the numpy array
                            slice_data = volume.volume[slice_id]
                            logger.debug(f"Successfully retrieved OCT slice {slice_id} from volume {volume_id} of {file_name}. "
                                         f"Slice shape: {slice_data.shape}, dtype: {slice_data.dtype}")
                        
                        # Convert to uint8 for better display if needed
                        if slice_data.dtype != np.uint8:
                            # Normalize to 0-255 range
                            normalized_data = ((slice_data - slice_data.min()) / 
                                              (slice_data.max() - slice_data.min() + 1e-10) * 255).astype(np.uint8)
                            logger.debug(f"Converted slice data from {slice_data.dtype} to uint8")
                            return normalized_data
                        return slice_data
                        
                    except ValueError as e:
                        logger.error(f"Invalid frame ID format '{frame_id}': {e}")
                    except Exception as e:
                        logger.error(f"Error accessing OCT volume: {e}", exc_info=True)
                
                elif frame_id.startswith('fundus'):
                    try:
                        # Parse the image ID from the frame_id
                        image_id = int(frame_id[6:])
                        
                        # Read all fundus images (following the example code)
                        logger.debug(f"Reading fundus images for {file_name} to access image {image_id}")
                        fundus_images = file_obj.read_fundus_image()
                        
                        if image_id >= len(fundus_images):
                            logger.warning(f"Fundus image index {image_id} out of bounds in {file_name}. "
                                           f"Available fundus images: {len(fundus_images)}")
                            return None
                            
                        # Access the fundus image and convert to numpy array
                        fundus_image = fundus_images[image_id]
                        
                        # Need to convert PIL image to numpy array
                        if not hasattr(fundus_image, 'image') or fundus_image.image is None:
                            # Try direct conversion
                            img_buffer = io.BytesIO()
                            fundus_image.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            fundus_array = np.array(Image.open(img_buffer))
                        else:
                            # Use image attribute if available
                            fundus_array = np.array(fundus_image.image)
                            
                        logger.debug(f"Successfully retrieved fundus image {image_id} from {file_name}. "
                                     f"Image shape: {fundus_array.shape}, dtype: {fundus_array.dtype}")
                        return fundus_array
                        
                    except ValueError as e:
                        logger.error(f"Invalid fundus ID format '{frame_id}': {e}")
                    except Exception as e:
                        logger.error(f"Error accessing fundus image: {e}", exc_info=True)
                else:
                    logger.warning(f"Unknown frame ID format '{frame_id}' for E2E file")
            
            elif isinstance(file_obj, IMG):
                if frame_id.startswith('slice'):
                    try:
                        # Parse the slice ID from the frame_id
                        slice_id = int(frame_id[5:])
                        
                        # Read the OCT volume (following the example code)
                        logger.debug(f"Reading OCT volume for IMG file {file_name} to access slice {slice_id}")
                        oct_volume = file_obj.read_oct_volume()
                        
                        if not hasattr(oct_volume, 'volume') or oct_volume.volume is None:
                            logger.warning(f"OCT volume in IMG file {file_name} has no 'volume' attribute or is None")
                            return None
                            
                        if slice_id >= oct_volume.volume.shape[0]:
                            logger.warning(f"Slice index {slice_id} out of bounds in IMG file {file_name}. "
                                           f"Volume shape: {oct_volume.volume.shape}")
                            return None
                            
                        # Get the slice data
                        slice_data = oct_volume.volume[slice_id]
                        logger.debug(f"Successfully retrieved slice {slice_id} from IMG file {file_name}. "
                                     f"Slice shape: {slice_data.shape}, dtype: {slice_data.dtype}")
                        
                        # Convert to uint8 for better display if needed
                        if slice_data.dtype != np.uint8:
                            # Normalize to 0-255 range
                            normalized_data = ((slice_data - slice_data.min()) / 
                                              (slice_data.max() - slice_data.min() + 1e-10) * 255).astype(np.uint8)
                            logger.debug(f"Converted slice data from {slice_data.dtype} to uint8")
                            return normalized_data
                        return slice_data
                        
                    except ValueError as e:
                        logger.error(f"Invalid slice ID format '{frame_id}': {e}")
                    except Exception as e:
                        logger.error(f"Error accessing OCT volume in IMG file: {e}", exc_info=True)
                else:
                    logger.warning(f"Unknown frame ID format '{frame_id}' for IMG file")
            else:
                logger.warning(f"Unsupported file object type {type(file_obj)} for {file_name}")
            
            # Log detailed error message if we get here
            logger.error(f"Could not get frame image data for frame {frame_id} in file {file_name}")
            return None
        
        except Exception as e:
            logger.error(f"Error getting frame image from {file_name}, frame {frame_id}: {str(e)}", exc_info=True)
            return None
    
    def export_to_dicom(self, file_name: str, output_dir: str) -> Tuple[bool, str]:
        """
        Export the OCT file to DICOM format.
        
        Args:
            file_name: Name of the loaded file
            output_dir: Directory to save the DICOM files
            
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        if file_name not in self.loaded_files:
            error_msg = f"File not loaded: {file_name}"
            logger.error(error_msg)
            return False, error_msg
        
        # Verify output directory exists
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            elif not os.path.isdir(output_dir):
                error_msg = f"Output path is not a directory: {output_dir}"
                logger.error(error_msg)
                return False, error_msg
            elif not os.access(output_dir, os.W_OK):
                error_msg = f"Output directory is not writable: {output_dir}"
                logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"Error validating output directory: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
        
        try:
            file_obj = self.loaded_files[file_name]
            file_path = file_obj.filepath
            
            if not os.path.exists(file_path):
                error_msg = f"OCT file no longer exists at path: {file_path}"
                logger.error(error_msg)
                return False, error_msg
                
            # Create DICOM from OCT file
            logger.info(f"Starting DICOM export for {file_name} to {output_dir}")
            create_dicom_from_oct(file_path, output_dir=output_dir)
            
            # Verify that files were created
            created_files = [f for f in os.listdir(output_dir) if f.lower().endswith('.dcm')]
            if not created_files:
                logger.warning(f"DICOM export completed but no .dcm files found in {output_dir}")
            else:
                logger.info(f"Successfully exported {len(created_files)} DICOM files to {output_dir}")
                
            return True, f"Successfully exported {file_name} to DICOM format ({len(created_files)} files)"
        
        except Exception as e:
            error_msg = f"Error exporting to DICOM: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
