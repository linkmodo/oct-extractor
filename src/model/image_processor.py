#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Processor Module
---------------------
Handles image processing operations for the OCT Image Extraction application.
"""

import os
import logging
import numpy as np
from typing import Tuple, Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)

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
        if image_data is None:
            raise ValueError("Image data cannot be None")
            
        if not isinstance(image_data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(image_data)}")
            
        if angle not in [0, 90, 180, 270]:
            raise ValueError("Rotation angle must be 0, 90, 180, or 270 degrees")
        
        if angle == 0:
            return image_data
        
        try:
            # Convert to PIL Image for rotation
            image = Image.fromarray(image_data)
            
            # Rotate image
            rotated_image = image.rotate(-angle, expand=True)
            
            # Convert back to numpy array
            return np.array(rotated_image)
        except Exception as e:
            logger.error(f"Error rotating image by {angle} degrees: {e}")
            raise
    
    def crop_image(self, image_data: np.ndarray, crop_params: Dict[str, int]) -> np.ndarray:
        """
        Crop an image using specified parameters.
        
        Args:
            image_data: Image data as numpy array
            crop_params: Dictionary with crop parameters (top, left, width, height)
            
        Returns:
            np.ndarray: Cropped image data
        """
        if image_data is None:
            raise ValueError("Image data cannot be None")
            
        if not isinstance(image_data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(image_data)}")
            
        if not crop_params:
            logger.warning("Empty crop parameters provided, returning original image")
            return image_data
            
        # Extract crop parameters
        top = crop_params.get('top', 0)
        left = crop_params.get('left', 0)
        width = crop_params.get('width', image_data.shape[1] - left)
        height = crop_params.get('height', image_data.shape[0] - top)
        
        # Validate crop parameters
        if top < 0 or left < 0:
            raise ValueError("Crop top and left must be non-negative")
        
        if width <= 0 or height <= 0:
            raise ValueError("Crop width and height must be positive")
        
        if top + height > image_data.shape[0] or left + width > image_data.shape[1]:
            raise ValueError(f"Crop region ({left},{top},{width},{height}) exceeds image dimensions ({image_data.shape[1]},{image_data.shape[0]})")
        
        try:
            # Crop image
            return image_data[top:top+height, left:left+width]
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            raise
    
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
        if image_data is None:
            raise ValueError("Image data cannot be None")
            
        if not isinstance(image_data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(image_data)}")
        
        if not processing_params:
            return image_data.copy()
            
        try:
            processed_image = image_data.copy()
            
            # Apply rotation if specified
            if 'rotation' in processing_params:
                angle = self._parse_rotation_angle(processing_params['rotation'])
                processed_image = self.rotate_image(processed_image, angle)
            
            # Apply cropping if specified
            if processing_params.get('crop', False) and 'crop_params' in processing_params:
                processed_image = self.crop_image(processed_image, processing_params['crop_params'])
            
            return processed_image
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
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
        except (ValueError, TypeError):
            return 0
    
    def enhance_contrast(self, image_data: np.ndarray) -> np.ndarray:
        """
        Enhance the contrast of an image.
        
        Args:
            image_data: Image data as numpy array
            
        Returns:
            np.ndarray: Enhanced image data
        """
        if image_data is None:
            raise ValueError("Image data cannot be None")
            
        if not isinstance(image_data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(image_data)}")
            
        try:
            # Convert to PIL Image for contrast enhancement
            image = Image.fromarray(image_data)
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            enhanced_image = enhancer.enhance(1.5)  # Enhance by factor of 1.5
            
            # Convert back to numpy array
            return np.array(enhanced_image)
        except Exception as e:
            logger.error(f"Error enhancing contrast: {e}")
            raise
    
    def adjust_brightness(self, image_data: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust the brightness of an image.
        
        Args:
            image_data: Image data as numpy array
            factor: Brightness adjustment factor (0.0 to 2.0)
            
        Returns:
            np.ndarray: Brightness-adjusted image data
        """
        if image_data is None:
            raise ValueError("Image data cannot be None")
            
        if not isinstance(image_data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(image_data)}")
            
        if factor < 0.0 or factor > 2.0:
            raise ValueError("Brightness factor must be between 0.0 and 2.0")
        
        try:
            # Convert to PIL Image for brightness adjustment
            image = Image.fromarray(image_data)
            
            # Adjust brightness
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Brightness(image)
            adjusted_image = enhancer.enhance(factor)
            
            # Convert back to numpy array
            return np.array(adjusted_image)
        except Exception as e:
            logger.error(f"Error adjusting brightness: {e}")
            raise
