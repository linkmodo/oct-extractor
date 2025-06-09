#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation Test Script
---------------------
Script to validate extraction and processing accuracy for OCT files.
"""

import os
import sys
import numpy as np
from PIL import Image
import json
import argparse
from datetime import datetime

# Add parent directory to path to import application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application modules
from src.model import OCTFileReader, FileManager, ImageProcessor
from src.controller import ImageController

def validate_file_loading(file_path):
    """
    Validate file loading functionality.
    
    Args:
        file_path: Path to the OCT file
        
    Returns:
        dict: Validation results
    """
    print(f"Validating file loading for: {file_path}")
    
    results = {
        "file": os.path.basename(file_path),
        "tests": [],
        "success": False,
        "errors": []
    }
    
    try:
        # Initialize OCT reader
        oct_reader = OCTFileReader()
        
        # Test file format detection
        test_result = {
            "name": "File format detection",
            "success": False,
            "details": ""
        }
        
        is_supported = oct_reader.is_supported_file(file_path)
        if is_supported:
            file_type = oct_reader.get_file_type(file_path)
            test_result["success"] = True
            test_result["details"] = f"Detected file type: {file_type}"
        else:
            test_result["details"] = "File format not supported"
        
        results["tests"].append(test_result)
        
        if not is_supported:
            results["errors"].append("Unsupported file format")
            return results
        
        # Test file loading
        test_result = {
            "name": "File loading",
            "success": False,
            "details": ""
        }
        
        success, message = oct_reader.load_file(file_path)
        test_result["success"] = success
        test_result["details"] = message
        
        results["tests"].append(test_result)
        
        if not success:
            results["errors"].append(message)
            return results
        
        # Test metadata extraction
        test_result = {
            "name": "Metadata extraction",
            "success": False,
            "details": ""
        }
        
        file_name = os.path.basename(file_path)
        if file_name in oct_reader.file_metadata:
            metadata = oct_reader.file_metadata[file_name]
            test_result["success"] = True
            test_result["details"] = f"Extracted {len(metadata)} metadata fields"
        else:
            test_result["details"] = "Failed to extract metadata"
        
        results["tests"].append(test_result)
        
        # Test preview generation
        test_result = {
            "name": "Preview generation",
            "success": False,
            "details": ""
        }
        
        preview_path, metadata_str = oct_reader.get_preview(file_name)
        if preview_path and os.path.exists(preview_path):
            test_result["success"] = True
            test_result["details"] = f"Preview generated: {preview_path}"
        else:
            test_result["details"] = "Failed to generate preview"
        
        results["tests"].append(test_result)
        
        # Test frame extraction
        test_result = {
            "name": "Frame extraction",
            "success": False,
            "details": ""
        }
        
        frames = oct_reader.get_frames(file_name)
        if frames and len(frames) > 0:
            test_result["success"] = True
            test_result["details"] = f"Extracted {len(frames)} frames"
        else:
            test_result["details"] = "Failed to extract frames"
        
        results["tests"].append(test_result)
        
        # Overall success
        results["success"] = all(test["success"] for test in results["tests"])
        
    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
    
    return results

def validate_image_processing(file_path):
    """
    Validate image processing functionality.
    
    Args:
        file_path: Path to the OCT file
        
    Returns:
        dict: Validation results
    """
    print(f"Validating image processing for: {file_path}")
    
    results = {
        "file": os.path.basename(file_path),
        "tests": [],
        "success": False,
        "errors": []
    }
    
    try:
        # Initialize components
        oct_reader = OCTFileReader()
        image_processor = ImageProcessor()
        image_controller = ImageController(image_processor)
        
        # Load file
        success, message = oct_reader.load_file(file_path)
        if not success:
            results["errors"].append(message)
            return results
        
        file_name = os.path.basename(file_path)
        
        # Get frames
        frames = oct_reader.get_frames(file_name)
        if not frames or len(frames) == 0:
            results["errors"].append("No frames found in file")
            return results
        
        # Test frame image extraction
        test_result = {
            "name": "Frame image extraction",
            "success": False,
            "details": ""
        }
        
        frame = frames[0]  # Use first frame for testing
        frame_id = frame['id']
        
        image_data = oct_reader.get_frame_image(file_name, frame_id)
        if image_data is not None:
            test_result["success"] = True
            test_result["details"] = f"Extracted image data for frame {frame_id}"
        else:
            test_result["details"] = f"Failed to extract image data for frame {frame_id}"
        
        results["tests"].append(test_result)
        
        if image_data is None:
            results["errors"].append("Failed to extract image data")
            return results
        
        # Test image rotation
        test_result = {
            "name": "Image rotation",
            "success": False,
            "details": ""
        }
        
        try:
            rotated_image = image_controller.rotate_image(image_data, 90)
            if rotated_image is not None:
                test_result["success"] = True
                test_result["details"] = "Successfully rotated image by 90 degrees"
            else:
                test_result["details"] = "Failed to rotate image"
        except Exception as e:
            test_result["details"] = f"Error rotating image: {str(e)}"
        
        results["tests"].append(test_result)
        
        # Test image cropping
        test_result = {
            "name": "Image cropping",
            "success": False,
            "details": ""
        }
        
        try:
            # Define crop parameters (use a small region in the center)
            height, width = image_data.shape[:2]
            crop_params = {
                'top': height // 4,
                'left': width // 4,
                'width': width // 2,
                'height': height // 2
            }
            
            cropped_image = image_controller.crop_image(image_data, crop_params)
            if cropped_image is not None:
                test_result["success"] = True
                test_result["details"] = f"Successfully cropped image to {cropped_image.shape}"
            else:
                test_result["details"] = "Failed to crop image"
        except Exception as e:
            test_result["details"] = f"Error cropping image: {str(e)}"
        
        results["tests"].append(test_result)
        
        # Test combined processing
        test_result = {
            "name": "Combined processing",
            "success": False,
            "details": ""
        }
        
        try:
            processing_params = {
                'rotation': 180,
                'crop': True,
                'crop_params': crop_params
            }
            
            processed_image = image_controller.process_image(image_data, processing_params)
            if processed_image is not None:
                test_result["success"] = True
                test_result["details"] = f"Successfully processed image with rotation and cropping"
            else:
                test_result["details"] = "Failed to process image"
        except Exception as e:
            test_result["details"] = f"Error processing image: {str(e)}"
        
        results["tests"].append(test_result)
        
        # Overall success
        results["success"] = all(test["success"] for test in results["tests"])
        
    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
    
    return results

def validate_export(file_path, export_dir):
    """
    Validate export functionality.
    
    Args:
        file_path: Path to the OCT file
        export_dir: Directory to export files to
        
    Returns:
        dict: Validation results
    """
    print(f"Validating export for: {file_path}")
    
    results = {
        "file": os.path.basename(file_path),
        "tests": [],
        "success": False,
        "errors": []
    }
    
    try:
        # Initialize components
        oct_reader = OCTFileReader()
        file_manager = FileManager()
        image_processor = ImageProcessor()
        image_controller = ImageController(image_processor)
        
        # Create export directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)
        
        # Load file
        success, message = oct_reader.load_file(file_path)
        if not success:
            results["errors"].append(message)
            return results
        
        file_name = os.path.basename(file_path)
        
        # Get frames
        frames = oct_reader.get_frames(file_name)
        if not frames or len(frames) == 0:
            results["errors"].append("No frames found in file")
            return results
        
        # Test PNG export
        test_result = {
            "name": "PNG export",
            "success": False,
            "details": ""
        }
        
        try:
            frame = frames[0]  # Use first frame for testing
            frame_id = frame['id']
            
            image_data = oct_reader.get_frame_image(file_name, frame_id)
            if image_data is None:
                test_result["details"] = "Failed to extract image data"
                results["tests"].append(test_result)
                results["errors"].append("Failed to extract image data")
                return results
            
            output_file = os.path.join(export_dir, f"{file_name}_{frame_id}.png")
            success, message = file_manager.save_image(image_data, output_file, "PNG")
            
            if success and os.path.exists(output_file):
                test_result["success"] = True
                test_result["details"] = f"Successfully exported to PNG: {output_file}"
            else:
                test_result["details"] = f"Failed to export to PNG: {message}"
        except Exception as e:
            test_result["details"] = f"Error exporting to PNG: {str(e)}"
        
        results["tests"].append(test_result)
        
        # Test JPEG export
        test_result = {
            "name": "JPEG export",
            "success": False,
            "details": ""
        }
        
        try:
            output_file = os.path.join(export_dir, f"{file_name}_{frame_id}.jpg")
            success, message = file_manager.save_image(image_data, output_file, "JPEG")
            
            if success and os.path.exists(output_file):
                test_result["success"] = True
                test_result["details"] = f"Successfully exported to JPEG: {output_file}"
            else:
                test_result["details"] = f"Failed to export to JPEG: {message}"
        except Exception as e:
            test_result["details"] = f"Error exporting to JPEG: {str(e)}"
        
        results["tests"].append(test_result)
        
        # Test processed image export
        test_result = {
            "name": "Processed image export",
            "success": False,
            "details": ""
        }
        
        try:
            # Process image (rotate and crop)
            height, width = image_data.shape[:2]
            processing_params = {
                'rotation': 90,
                'crop': True,
                'crop_params': {
                    'top': height // 4,
                    'left': width // 4,
                    'width': width // 2,
                    'height': height // 2
                }
            }
            
            processed_image = image_controller.process_image(image_data, processing_params)
            
            output_file = os.path.join(export_dir, f"{file_name}_{frame_id}_processed.png")
            success, message = file_manager.save_image(processed_image, output_file, "PNG")
            
            if success and os.path.exists(output_file):
                test_result["success"] = True
                test_result["details"] = f"Successfully exported processed image: {output_file}"
            else:
                test_result["details"] = f"Failed to export processed image: {message}"
        except Exception as e:
            test_result["details"] = f"Error exporting processed image: {str(e)}"
        
        results["tests"].append(test_result)
        
        # Overall success
        results["success"] = all(test["success"] for test in results["tests"])
        
    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
    
    return results

def run_validation(test_files, export_dir):
    """
    Run validation tests on test files.
    
    Args:
        test_files: List of test file paths
        export_dir: Directory to export files to
        
    Returns:
        dict: Validation results
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "files_tested": len(test_files),
        "file_results": [],
        "overall_success": False
    }
    
    for file_path in test_files:
        file_results = {
            "file": os.path.basename(file_path),
            "loading": validate_file_loading(file_path),
            "processing": validate_image_processing(file_path),
            "export": validate_export(file_path, export_dir)
        }
        
        file_results["success"] = (
            file_results["loading"]["success"] and
            file_results["processing"]["success"] and
            file_results["export"]["success"]
        )
        
        results["file_results"].append(file_results)
    
    # Overall success
    results["overall_success"] = all(file_result["success"] for file_result in results["file_results"])
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate OCT Image Extraction Application")
    parser.add_argument("--test-dir", help="Directory containing test files")
    parser.add_argument("--export-dir", help="Directory to export files to")
    parser.add_argument("--output", help="Output file for validation results")
    
    args = parser.parse_args()
    
    # Set default directories if not provided
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    test_dir = args.test_dir if args.test_dir else os.path.join(base_dir, "test_files")
    export_dir = args.export_dir if args.export_dir else os.path.join(base_dir, "test_exports")
    output_file = args.output if args.output else os.path.join(base_dir, "validation_results.json")
    
    # Create directories if they don't exist
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(export_dir, exist_ok=True)
    
    # Find test files
    test_files = []
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.lower().endswith(('.e2e', '.img')):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print(f"No test files found in {test_dir}")
        print("Please add .e2e or .img files to the test directory")
        return
    
    print(f"Found {len(test_files)} test files")
    for file in test_files:
        print(f"  - {os.path.basename(file)}")
    
    # Run validation
    print("\nRunning validation tests...")
    results = run_validation(test_files, export_dir)
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nValidation results saved to {output_file}")
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Files tested: {results['files_tested']}")
    print(f"Overall success: {results['overall_success']}")
    
    for file_result in results["file_results"]:
        print(f"\n{file_result['file']}:")
        print(f"  Loading: {'✓' if file_result['loading']['success'] else '✗'}")
        print(f"  Processing: {'✓' if file_result['processing']['success'] else '✗'}")
        print(f"  Export: {'✓' if file_result['export']['success'] else '✗'}")
        print(f"  Overall: {'✓' if file_result['success'] else '✗'}")
    
    print("\nExported files can be found in:", export_dir)

if __name__ == "__main__":
    main()
