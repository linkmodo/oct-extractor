#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from src.model.oct_file_reader import OCTFileReader

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_extraction.log')
    ]
)
logger = logging.getLogger('test_extraction')

def test_oct_extraction(file_path):
    """Test the OCT file extraction functionality"""
    # Convert to absolute path if not already
    file_path = os.path.abspath(file_path)
    logger.info(f"Testing OCT extraction with absolute file path: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return
        
    # Create OCTFileReader instance
    oct_reader = OCTFileReader()
    
    # Get file name from path
    file_name = os.path.basename(file_path)
    
    # Load the file
    try:
        logger.info("Loading OCT file...")
        success, message = oct_reader.load_file(file_path)
        if not success:
            logger.error(f"Failed to load file: {message}")
            return
        logger.info(f"OCT file loaded successfully: {message}")
        
        # The OCTFileReader extracts the filename from the path internally
        # Let's get the file name from the reader's mappings
        file_name = os.path.basename(file_path)  # This should match what the reader uses
    except Exception as e:
        logger.error(f"Error loading file: {str(e)}", exc_info=True)
        return
    
    # Get available frames
    try:
        logger.info("Getting available frames...")
        frames = oct_reader.get_frames(file_name)
        logger.info(f"Found {len(frames)} frames")
        
        # Print frame information
        for i, frame in enumerate(frames[:5]):  # Print info for first 5 frames
            logger.info(f"Frame {i} info: {frame}")
        
        if len(frames) > 5:
            logger.info(f"... and {len(frames) - 5} more frames")
    except Exception as e:
        logger.error(f"Error getting frames: {str(e)}", exc_info=True)
        return
    
    # Extract some frame images
    if frames:
        try:
            # Try to extract the first frame, and a middle frame if there are enough
            frames_to_extract = [0]
            if len(frames) > 10:
                frames_to_extract.append(len(frames) // 2)
                
            for idx in frames_to_extract:
                frame = frames[idx]
                frame_id = frame['id']
                logger.info(f"Extracting image for frame {frame_id}...")
                
                image_data = oct_reader.get_frame_image(file_name, frame_id)
                
                if image_data is not None:
                    logger.info(f"Successfully extracted image with shape: {image_data.shape}, dtype: {image_data.dtype}")
                    
                    # Save the image
                    output_path = f"extracted_{file_name}_{frame_id}.png"
                    img = Image.fromarray(image_data)
                    img.save(output_path)
                    logger.info(f"Saved image to {output_path}")
                    
                    # Display basic image information
                    logger.info(f"Image min value: {image_data.min()}, max value: {image_data.max()}")
                else:
                    logger.error(f"Failed to extract image for frame {frame_id}")
        except Exception as e:
            logger.error(f"Error extracting frame images: {str(e)}", exc_info=True)

def main():
    # Check if command line argument was provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        logger.info(f"Using file path from command line: {file_path}")
        if os.path.exists(file_path):
            test_oct_extraction(file_path)
            return
        else:
            logger.error(f"File not found: {file_path}")
    
    # Look for OCT files in the current directory
    oct_files = []
    for extension in ['.oct', '.OCT', '.e2e', '.E2E', '.img', '.IMG']:
        oct_files.extend(list(Path('.').glob(f"*{extension}")))
    
    if not oct_files:
        logger.warning("No OCT files found in the current directory")
        # Ask for a file path
        file_path = input("Enter the path to an OCT file: ")
        file_path = file_path.strip('"\'')
        
        # Verify the file exists
        if os.path.exists(file_path):
            oct_files = [Path(file_path)]
            logger.info(f"File found: {file_path}")
        else:
            logger.error(f"File not found: {file_path}")
            return
    
    # Test with the first OCT file found
    if oct_files:
        logger.info(f"Found OCT files: {[str(f) for f in oct_files]}")
        test_oct_extraction(str(oct_files[0]))
    else:
        logger.error("No OCT files available for testing")

if __name__ == "__main__":
    main()
