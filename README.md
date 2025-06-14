# OCT Image Extraction Tool v2.1

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful desktop application for extracting and processing images from various Optical Coherence Tomography (OCT) file formats used in ophthalmology. Built with Python and PyQt5, it provides a user-friendly interface for medical professionals and researchers.

## 🛠️ Built With

This application was developed with the assistance of:
- [Manus.im](https://manus.im) - A generative AI agent that helped design and implement features
- [Windsurf](https://windsurf.dev) - An agentic AI IDE that accelerated development

![OCT Extractor Screenshot](screenshots/app-screenshot.png)

## 🌟 Features

- **Multi-format Support**: Import from various OCT file formats including:
  - Heidelberg Engineering (.e2e)
  - Zeiss (.img)
  - Topcon (.fds, .fda)
  - Bioptigen (.oct)
  - POCT (.poct)
  - DICOM (.dcm)

- **Image Extraction**:
  - Extract both B-scan and fundus images
  - Batch process multiple files
  - Export to common formats (PNG, JPEG, TIFF, DICOM)

- **User Interface**:
  - Intuitive file browser
  - Image preview and navigation
  - Progress tracking for long operations
  - Customizable export settings

- **Duplicate File Handling**:
  - Overwrite existing files
  - Skip duplicates
  - Create unique filenames automatically

## 🚀 Installation

### Prerequisites
- Windows 10/11
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space

### Option 1: Download Pre-built Executable
1. Download the latest release from the [Releases](https://github.com/linkmodo/oct-extractor/releases) page
2. Extract the ZIP file
3. Run `OCT Extractor.exe`

### Option 2: Build from Source
```bash
# Clone the repository
git clone https://github.com/linkmodo/oct-extractor.git
cd oct-extractor

# Install dependencies
pip install -r requirements.txt

# Build the executable
python build_oct_extractor.bat
```

## 🖥️ Usage

1. **Import Files**:
   - Click "File" > "Import" or drag and drop OCT files into the application
   - Select one or more files for processing

2. **View and Navigate**:
   - Use the file browser to select different scans
   - Navigate through image stacks using the slider or arrow keys

3. **Export Images**:
   - Select the frames you want to export
   - Choose your preferred export format and settings
   - Select the output directory
   - Click "Export" to save the images

## 🛠️ Development

### Project Structure
```
oct-extractor/
├── src/                  # Source code
│   ├── controller/       # Application controllers
│   ├── model/            # Data models and processing
│   └── view/             # UI components
├── resources/            # Application resources
├── tests/                # Test files
└── requirements.txt      # Python dependencies
```

### Building the Application
```bash
# Install build dependencies
pip install pyinstaller

# Build the executable
python build_oct_extractor.bat
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project was made possible thanks to:

- [Manus.im](https://manus.im) for AI-assisted development and feature implementation
- [Windsurf](https://windsurf.dev) for providing an agentic AI development environment
- The [OCT-Converter](https://github.com/marksgraham/OCT-Converter) library for OCT file format support
- [Font Awesome](https://fontawesome.com/) for icons
- The Python community for amazing open-source tools and libraries

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
   
 