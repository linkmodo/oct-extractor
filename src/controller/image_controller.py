#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Controller Module
----------------------
Controls image processing operations for the OCT Image Extraction application.
"""

import os
from typing import Tuple, Dict, Any, Optional
import numpy as np

class ImageController:
    """Controller class for image processing operations."""
    
    def __init__(self, image_processor):
        """
        Initialize the image controller.
        
        Args:
            image_processor: ImageProcessor instance
        """
        self.image_processor = image_processor
    
    def process_image(self, image_data: np.ndarray, processing_params: Dict[str, Any]) -> np.ndarray:
        """
        Process an image with specified parameters.
        
        Args:
            image_data: Image data as numpy array
            processing_params: Dictionary with processing parameters
                - rotation: Rotation angle in degrees (0, 90, 180, 270)
                - crop: Boolean indicating whether to crop
                - crop_params: Dictionary with crop parameters (top, left, width, height)
            
        Returns:
            np.ndarray: Processed image data
        """
        return self.image_processor.process_image(image_data, processing_params)
    
    def rotate_image(self, image_data: np.ndarray, angle: int) -> np.ndarray:
        """
        Rotate an image by a specified angle.
        
        Args:
            image_data: Image data as numpy array
            angle: Rotation angle in degrees (0, 90, 180, 270)
            
        Returns:
            np.ndarray: Rotated image data
        """
        return self.image_processor.rotate_image(image_data, angle)
    
    def crop_image(self, image_data: np.ndarray, crop_params: Dict[str, int]) -> np.ndarray:
        """
        Crop an image using specified parameters.
        
        Args:
            image_data: Image data as numpy array
            crop_params: Dictionary with crop parameters (top, left, width, height)
            
        Returns:
            np.ndarray: Cropped image data
        """
        return self.image_processor.crop_image(image_data, crop_params)
    
    def enhance_contrast(self, image_data: np.ndarray) -> np.ndarray:
        """
        Enhance the contrast of an image.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            np.ndarray: Enhanced image data
        """
        return self.image_processor.enhance_contrast(image_data)
    
    def adjust_brightness(self, image_data: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust the brightness of an image.
        
        Args:
            image_data: Image data as numpy array
            factor: Brightness adjustment factor (0.0 to 2.0)
            
        Returns:
            np.ndarray: Brightness-adjusted image data
        """
        return self.image_processor.adjust_brightness(image_data, factor)
    
    def batch_process_images(self, images: Dict[str, np.ndarray], processing_params: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Process multiple images with the same parameters.
        
        Args:
            images: Dictionary mapping image IDs to image data
            processing_params: Dictionary with processing parameters
            
        Returns:
            Dict[str, np.ndarray]: Dictionary mapping image IDs to processed image data
        """
        processed_images = {}
        
        for image_id, image_data in images.items():
            processed_images[image_id] = self.process_image(image_data, processing_params)
        
        return processed_images
    
    def save_processing_preset(self, preset_name: str, processing_params: Dict[str, Any]) -> bool:
        """
        Save processing parameters as a preset.
        
        Args:
            preset_name: Name of the preset
            processing_params: Dictionary with processing parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        # This would typically save to a configuration file or database
        # For now, we'll just return True
        return True
    
    def load_processing_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Load processing parameters from a preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Optional[Dict[str, Any]]: Processing parameters or None if not found
        """
        # This would typically load from a configuration file or database
        # For now, we'll just return None
        return None
