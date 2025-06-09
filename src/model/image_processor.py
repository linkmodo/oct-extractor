#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Processor Module
---------------------
Handles image processing operations for the OCT Image Extraction application.
"""

import os
import numpy as np
from typing import Tuple, Dict, Any, Optional
from PIL import Image

class ImageProcessor:
    """Class for processing OCT images."""
    
    def __init__(self):
        """Initialize the image processor."""
        pass
    
    def rotate_image(self, image_data: np.ndarray, angle: int) -> np.ndarray:
        """
        Rotate an image by a specified angle.
        
        Args:
            image_data: Image data as numpy array
            angle: Rotation angle in degrees (0, 90, 180, 270)
            
        Returns:
            np.ndarray: Rotated image data
        """
        if angle not in [0, 90, 180, 270]:
            raise ValueError("Rotation angle must be 0, 90, 180, or 270 degrees")
        
        if angle == 0:
            return image_data
        
        # Convert to PIL Image for rotation
        image = Image.fromarray(image_data)
        
        # Rotate image
        rotated_image = image.rotate(-angle, expand=True)
        
        # Convert back to numpy array
        return np.array(rotated_image)
    
    def crop_image(self, image_data: np.ndarray, crop_params: Dict[str, int]) -> np.ndarray:
        """
        Crop an image using specified parameters.
        
        Args:
            image_data: Image data as numpy array
            crop_params: Dictionary with crop parameters (top, left, width, height)
            
        Returns:
            np.ndarray: Cropped image data
        """
        # Extract crop parameters
        top = crop_params.get('top', 0)
        left = crop_params.get('left', 0)
        width = crop_params.get('width', image_data.shape[1] - left)
        height = crop_params.get('height', image_data.shape[0] - top)
        
        # Validate crop parameters
        if top < 0 or left < 0:
            raise ValueError("Crop top and left must be non-negative")
        
        if top + height > image_data.shape[0] or left + width > image_data.shape[1]:
            raise ValueError("Crop region exceeds image dimensions")
        
        # Crop image
        return image_data[top:top+height, left:left+width]
    
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
        processed_image = image_data.copy()
        
        # Apply rotation if specified
        if 'rotation' in processing_params:
            angle = self._parse_rotation_angle(processing_params['rotation'])
            processed_image = self.rotate_image(processed_image, angle)
        
        # Apply cropping if specified
        if processing_params.get('crop', False) and 'crop_params' in processing_params:
            processed_image = self.crop_image(processed_image, processing_params['crop_params'])
        
        return processed_image
    
    def _parse_rotation_angle(self, rotation: str) -> int:
        """
        Parse rotation angle from string.
        
        Args:
            rotation: Rotation angle as string (e.g., "90°")
            
        Returns:
            int: Rotation angle in degrees
        """
        if isinstance(rotation, int):
            return rotation
        
        try:
            # Remove non-numeric characters and convert to int
            angle = int(''.join(filter(str.isdigit, rotation)))
            return angle
        except:
            return 0
    
    def enhance_contrast(self, image_data: np.ndarray) -> np.ndarray:
        """
        Enhance the contrast of an image.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            np.ndarray: Enhanced image data
        """
        # Convert to PIL Image for contrast enhancement
        image = Image.fromarray(image_data)
        
        # Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(1.5)  # Enhance by factor of 1.5
        
        # Convert back to numpy array
        return np.array(enhanced_image)
    
    def adjust_brightness(self, image_data: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust the brightness of an image.
        
        Args:
            image_data: Image data as numpy array
            factor: Brightness adjustment factor (0.0 to 2.0)
            
        Returns:
            np.ndarray: Brightness-adjusted image data
        """
        if factor < 0.0 or factor > 2.0:
            raise ValueError("Brightness factor must be between 0.0 and 2.0")
        
        # Convert to PIL Image for brightness adjustment
        image = Image.fromarray(image_data)
        
        # Adjust brightness
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(image)
        adjusted_image = enhancer.enhance(factor)
        
        # Convert back to numpy array
        return np.array(adjusted_image)
