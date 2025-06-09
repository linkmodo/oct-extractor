#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCT Image Extraction Application - Windows Packaging Script
---------------------------------------------------------
Script to package the OCT Image Extraction application for Windows.
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime

def create_spec_file(app_dir, output_dir):
    """
    Create a PyInstaller spec file for the application.
    
    Args:
        app_dir: Application directory
        output_dir: Output directory for the packaged application
    
    Returns:
        str: Path to the spec file
    """
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{os.path.join(app_dir, 'src', 'main.py')}'],
    pathex=['{app_dir}'],
    binaries=[],
    datas=[
        ('{os.path.join(app_dir, "settings")}', 'settings'),
    ],
    hiddenimports=['PIL', 'numpy', 'oct_converter', 'PyQt5'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OCT Image Extraction Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{os.path.join(app_dir, "resources", "icon.ico")}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OCT Image Extraction Tool',
)
"""
    
    spec_file = os.path.join(app_dir, "oct_extraction_tool.spec")
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    return spec_file

def create_resources(app_dir):
    """
    Create necessary resources for packaging.
    
    Args:
        app_dir: Application directory
    """
    # Create resources directory
    resources_dir = os.path.join(app_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create settings directory
    settings_dir = os.path.join(app_dir, "settings")
    os.makedirs(settings_dir, exist_ok=True)
    
    # Create empty settings files if they don't exist
    settings_file = os.path.join(settings_dir, "settings.json")
    if not os.path.exists(settings_file):
        with open(settings_file, 'w') as f:
            f.write("{}")
    
    presets_file = os.path.join(settings_dir, "presets.json")
    if not os.path.exists(presets_file):
        with open(presets_file, 'w') as f:
            f.write("{}")
    
    # Create a simple icon file if it doesn't exist
    # In a real application, you would use a proper icon file
    icon_file = os.path.join(resources_dir, "icon.ico")
    if not os.path.exists(icon_file):
        # Create a simple text file as a placeholder
        with open(icon_file, 'w') as f:
            f.write("This is a placeholder for the icon file.")

def install_dependencies():
    """Install required dependencies for packaging."""
    print("Installing required dependencies...")
    
    try:
        # Install PyInstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Install application dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "PyQt5", "numpy", "Pillow", "oct-converter"], check=True)
        
        print("Dependencies installed successfully.")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def package_application(app_dir, output_dir, spec_file):
    """
    Package the application using PyInstaller.
    
    Args:
        app_dir: Application directory
        output_dir: Output directory for the packaged application
        spec_file: Path to the PyInstaller spec file
    
    Returns:
        bool: True if packaging was successful, False otherwise
    """
    print("Packaging application...")
    
    try:
        # Run PyInstaller
        subprocess.run(["pyinstaller", "--clean", spec_file], check=True, cwd=app_dir)
        
        # Copy the dist directory to the output directory
        dist_dir = os.path.join(app_dir, "dist", "OCT Image Extraction Tool")
        if os.path.exists(dist_dir):
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Create a timestamped directory for this build
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            build_dir = os.path.join(output_dir, f"OCT_Image_Extraction_Tool_{timestamp}")
            os.makedirs(build_dir, exist_ok=True)
            
            # Copy files
            for item in os.listdir(dist_dir):
                src = os.path.join(dist_dir, item)
                dst = os.path.join(build_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            print(f"Application packaged successfully to: {build_dir}")
            return True
        
        else:
            print("Error: PyInstaller did not create the expected output directory.")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"Error packaging application: {e}")
        return False

def create_documentation(app_dir, output_dir):
    """
    Create documentation for the packaged application.
    
    Args:
        app_dir: Application directory
        output_dir: Output directory for the packaged application
    """
    print("Creating documentation...")
    
    # Find the most recent build directory
    build_dirs = [d for d in os.listdir(output_dir) if d.startswith("OCT_Image_Extraction_Tool_")]
    if not build_dirs:
        print("Error: No build directories found.")
        return
    
    build_dirs.sort(reverse=True)
    build_dir = os.path.join(output_dir, build_dirs[0])
    
    # Create docs directory
    docs_dir = os.path.join(build_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    # Create user manual
    user_manual = os.path.join(docs_dir, "User_Manual.md")
    with open(user_manual, 'w') as f:
        f.write("""# OCT Image Extraction Tool - User Manual

## Introduction
The OCT Image Extraction Tool is a Windows application designed to extract and process images from Zeiss Cirrus OCT RAW files and Heidelberg OCT e2e files used in ophthalmology.

## Installation
1. Extract the application files to a directory of your choice
2. Run "OCT Image Extraction Tool.exe" to start the application

## Features
- Import Zeiss Cirrus OCT RAW (.img) and Heidelberg OCT (.e2e) files
- Select specific frames to export
- Batch rotate images
- Crop images using pre-determined parameters
- Export to various formats (PNG, JPEG, TIFF, DICOM)

## Usage

### Importing Files
1. Click "File" > "Import..." or use the Import button in the toolbar
2. Select one or more OCT files to import
3. The files will be loaded and displayed in the file browser

### Selecting Frames
1. Select a file in the file browser to view available frames
2. Use the checkboxes to select frames for export
3. Use the "Select All", "Deselect All", or "Invert Selection" buttons as needed

### Processing Options
1. Set rotation angle (0°, 90°, 180°, 270°)
2. Enable or disable cropping
3. Set crop parameters (top, left, width, height)
4. Save crop parameters as presets for future use

### Exporting Frames
1. Set the export directory
2. Select the export format (PNG, JPEG, TIFF, DICOM)
3. Click "Export Selected Frames" to export the selected frames

## Troubleshooting
- If the application fails to start, ensure that you have the latest Windows updates installed
- If file import fails, check that the file format is supported (.img or .e2e)
- If export fails, ensure that the export directory is writable

## Support
For support, please contact your system administrator or the application provider.
""")
    
    # Create technical documentation
    technical_doc = os.path.join(docs_dir, "Technical_Documentation.md")
    with open(technical_doc, 'w') as f:
        f.write("""# OCT Image Extraction Tool - Technical Documentation

## Architecture
The application follows a Model-View-Controller (MVC) architecture:
- **Model**: Handles data processing, file operations, and image manipulation
- **View**: User interface components
- **Controller**: Coordinates between the model and view, handles user input

## Components

### Model Components
1. **OCTFileReader**: Reads and parses OCT files using the OCT-Converter library
2. **FileManager**: Manages file system operations
3. **ImageProcessor**: Handles image processing operations

### Controller Components
1. **FileController**: Manages file import operations
2. **ExportController**: Manages export operations
3. **FrameController**: Manages frame selection
4. **ImageController**: Coordinates image processing operations

### View Components
1. **MainWindow**: Primary application interface
2. **ImportDialog**: File selection interface
3. **FrameSelector**: Visual interface for selecting frames
4. **ExportDialog**: Export configuration interface
5. **SettingsDialog**: Application settings interface

## Dependencies
- Python 3.8+
- PyQt5 for the user interface
- OCT-Converter for OCT file parsing
- NumPy and Pillow for image processing

## File Formats
- Zeiss Cirrus OCT RAW (.img)
- Heidelberg OCT (.e2e)

## Export Formats
- PNG
- JPEG
- TIFF
- DICOM

## Settings
Settings and presets are stored in JSON files in the "settings" directory.
""")
    
    print(f"Documentation created in: {docs_dir}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Package OCT Image Extraction Application for Windows")
    parser.add_argument("--app-dir", help="Application directory")
    parser.add_argument("--output-dir", help="Output directory for the packaged application")
    
    args = parser.parse_args()
    
    # Set default directories if not provided
    app_dir = args.app_dir if args.app_dir else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = args.output_dir if args.output_dir else os.path.join(app_dir, "dist")
    
    print(f"Application directory: {app_dir}")
    print(f"Output directory: {output_dir}")
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Exiting.")
        return
    
    # Create resources
    create_resources(app_dir)
    
    # Create spec file
    spec_file = create_spec_file(app_dir, output_dir)
    
    # Package application
    if package_application(app_dir, output_dir, spec_file):
        # Create documentation
        create_documentation(app_dir, output_dir)
        print("Packaging completed successfully.")
    else:
        print("Packaging failed.")

if __name__ == "__main__":
    main()
