# OCT Image Extraction Tool v2.1

## Overview
The OCT Image Extraction Tool is a Windows application designed to extract and process images from various OCT file formats used in ophthalmology. Built with Python and PyQt5, it provides a user-friendly interface for viewing and exporting OCT images and metadata.

## Supported File Formats
- **Heidelberg Engineering** (.e2e)
- **Zeiss** (.img)
- **Topcon** (.fds, .fda)
- **Bioptigen** (.oct)
- **POCT** (.poct)
- **DICOM** (.dcm)

## Features
- Import multiple OCT file formats
- Preview OCT scans and fundus images
- Export to multiple image formats (PNG, JPEG, TIFF, DICOM)
- Batch process multiple files
- View and export detailed metadata
- User-friendly interface with image preview
- Built on top of the powerful OCT-Converter library

## System Requirements
- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Screen resolution of 1280x720 or higher

## Installation
### Pre-built Executable
1. Download the latest release from the [Releases](https://github.com/yourusername/oct-extractor/releases) page
2. Extract the ZIP file to a directory of your choice
3. Run `OCT Extractor.exe` to start the application

### Building from Source
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/oct-extractor.git
   cd oct-extractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. Build the executable:
   ```
   python build.py
   ```
   or on Windows:
   ```
   build.bat
   ```

4. The executable will be in the `dist` directory

## Usage
### Basic Workflow
1. Click "Import..." to load one or more OCT files
2. Select a file from the list to view its contents
3. Use the preview panel to examine the OCT scans
4. Select frames to export
5. Choose export options and click "Export"

### Keyboard Shortcuts
- `Ctrl+O`: Import files
- `Ctrl+E`: Export selected frames
- `Ctrl+A`: Select all frames
- `Ctrl+D`: Deselect all frames

## Dependencies
This application uses the following open-source components:
- [OCT-Converter](https://github.com/marksgraham/OCT-Converter) by Mark Graham
- PyQt5
- NumPy
- Pillow
- h5py
- Matplotlib

## License
[MIT License](LICENSE)

## System Requirements
- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Screen resolution of 1280x720 or higher

## Installation
1. Extract the ZIP file to a directory of your choice
2. Run "OCT Image Extraction Tool.exe" to start the application
3. No additional installation steps required

## Usage Guide

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

## License
This application is provided for use in ophthalmology practices and research.

## Support
For support, please contact your system administrator or the application provider.
