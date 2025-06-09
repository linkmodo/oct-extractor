# OCT Image Extraction Application Architecture Design

## Overview
This document outlines the architecture and user interface design for a Windows application that extracts and processes images from Zeiss Cirrus OCT RAW (.img) files and Heidelberg OCT (.e2e) files used in ophthalmology.

## Application Requirements
1. Import Zeiss Cirrus OCT RAW (.img) and Heidelberg OCT (.e2e) files
2. Define export folder for extracted images
3. Select specific frames to export
4. Batch rotate images
5. Crop images using pre-determined parameters

## Architecture

### High-Level Architecture
The application will follow a Model-View-Controller (MVC) pattern:
- **Model**: Handles data processing, file operations, and image manipulation
- **View**: User interface components
- **Controller**: Coordinates between the model and view, handles user input

### Component Diagram
```
+---------------------+     +----------------------+     +---------------------+
|       View          |     |     Controller       |     |       Model         |
|                     |     |                      |     |                     |
| - Main Window       |<--->| - File Controller    |<--->| - OCT File Reader   |
| - Import Dialog     |     | - Export Controller  |     | - Image Processor   |
| - Frame Selector    |     | - Frame Controller   |     | - File Manager      |
| - Export Dialog     |     | - Image Controller   |     |                     |
| - Settings Dialog   |     |                      |     |                     |
+---------------------+     +----------------------+     +---------------------+
```

### Core Components

#### Model Components
1. **OCT File Reader**
   - Utilizes OCT-Converter library to read Zeiss and Heidelberg files
   - Extracts OCT volumes, fundus images, and metadata
   - Provides access to individual frames

2. **Image Processor**
   - Handles image rotation operations
   - Implements cropping functionality with configurable parameters
   - Manages image format conversion

3. **File Manager**
   - Manages file system operations
   - Handles import and export paths
   - Ensures proper file naming and organization

#### Controller Components
1. **File Controller**
   - Manages file import operations
   - Validates file formats
   - Coordinates with OCT File Reader

2. **Export Controller**
   - Manages export folder selection
   - Handles batch export operations
   - Ensures proper file naming

3. **Frame Controller**
   - Manages frame selection
   - Coordinates with Image Processor for frame extraction

4. **Image Controller**
   - Coordinates image processing operations
   - Manages rotation and cropping parameters
   - Handles batch processing

#### View Components
1. **Main Window**
   - Primary application interface
   - Contains menu bar, toolbar, and status bar
   - Hosts other UI components

2. **Import Dialog**
   - File selection interface
   - Displays file information
   - Validates selected files

3. **Frame Selector**
   - Visual interface for selecting frames
   - Thumbnail preview of available frames
   - Selection tools (individual, range, all)

4. **Export Dialog**
   - Export folder selection
   - Export format options
   - Batch processing settings

5. **Settings Dialog**
   - Configuration for rotation parameters
   - Configuration for cropping parameters
   - Application preferences

### Data Flow
1. User imports OCT files through the Import Dialog
2. File Controller validates files and passes them to OCT File Reader
3. OCT File Reader extracts volumes, images, and metadata
4. Frame Selector displays available frames for user selection
5. User selects frames and configures processing options
6. User initiates export operation
7. Export Controller coordinates with Image Processor for rotation and cropping
8. File Manager handles saving processed images to the selected export folder

## User Interface Design

### Main Window
```
+----------------------------------------------------------------------+
| File   Edit   View   Tools   Help                                     |
+----------------------------------------------------------------------+
| [Import] [Export] [Settings] [About]                                  |
+----------------------------------------------------------------------+
|                                                                      |
|  +---------------------------+  +-------------------------------+    |
|  |                           |  |                               |    |
|  |  File Browser             |  |  Preview Panel                |    |
|  |                           |  |                               |    |
|  |  - Imported Files         |  |  - Current Frame Preview      |    |
|  |  - File Information       |  |  - Metadata Display           |    |
|  |                           |  |                               |    |
|  +---------------------------+  +-------------------------------+    |
|                                                                      |
|  +------------------------------------------------------------------+|
|  |                                                                  ||
|  |  Frame Selection Panel                                           ||
|  |                                                                  ||
|  |  [□] [□] [□] [□] [□] [□] [□] [□] [□] [□] [□] [□] [□] [□] [□]    ||
|  |                                                                  ||
|  +------------------------------------------------------------------+|
|                                                                      |
|  +---------------------------+  +-------------------------------+    |
|  |                           |  |                               |    |
|  |  Processing Options       |  |  Export Options               |    |
|  |                           |  |                               |    |
|  |  - Rotation: [_____]      |  |  - Export Path: [_________]   |    |
|  |  - Crop: [X] Enable       |  |  - Format: [PNG▼]             |    |
|  |    - Top: [___]           |  |  - Quality: [High▼]           |    |
|  |    - Left: [___]          |  |                               |    |
|  |    - Width: [___]         |  |  [Export Selected Frames]     |    |
|  |    - Height: [___]        |  |                               |    |
|  +---------------------------+  +-------------------------------+    |
|                                                                      |
| Status: Ready                                                        |
+----------------------------------------------------------------------+
```

### Import Dialog
```
+----------------------------------------------------------------------+
| Import OCT Files                                                      |
+----------------------------------------------------------------------+
|                                                                      |
| Select Files:                                                        |
| [_________________________________________________] [Browse...]      |
|                                                                      |
| Supported Formats:                                                   |
| [X] Zeiss Cirrus OCT (.img)                                          |
| [X] Heidelberg OCT (.e2e)                                            |
|                                                                      |
| [         Cancel         ]            [         Import         ]     |
+----------------------------------------------------------------------+
```

### Frame Selection Dialog
```
+----------------------------------------------------------------------+
| Select Frames to Export                                               |
+----------------------------------------------------------------------+
|                                                                      |
| [Select All] [Deselect All] [Invert Selection]                       |
|                                                                      |
| +------------------------------------------------------------------+ |
| |                                                                  | |
| | [X] Frame 1  [X] Frame 2  [X] Frame 3  [X] Frame 4  [X] Frame 5  | |
| | [_] Frame 6  [_] Frame 7  [_] Frame 8  [_] Frame 9  [_] Frame 10 | |
| | [_] Frame 11 [_] Frame 12 [_] Frame 13 [_] Frame 14 [_] Frame 15 | |
| |                                                                  | |
| +------------------------------------------------------------------+ |
|                                                                      |
| [         Cancel         ]            [          OK           ]      |
+----------------------------------------------------------------------+
```

### Export Settings Dialog
```
+----------------------------------------------------------------------+
| Export Settings                                                       |
+----------------------------------------------------------------------+
|                                                                      |
| Export Location:                                                     |
| [_________________________________________________] [Browse...]      |
|                                                                      |
| File Format:                                                         |
| ( ) PNG                                                              |
| ( ) JPEG                                                             |
| ( ) TIFF                                                             |
| (X) DICOM                                                            |
|                                                                      |
| Batch Processing:                                                    |
| [X] Apply rotation: [90°▼]                                           |
| [X] Apply cropping with current parameters                           |
|                                                                      |
| Naming Convention:                                                   |
| ( ) Original filename + frame number                                 |
| (X) Custom prefix: [OCT_Export_] + frame number                      |
|                                                                      |
| [         Cancel         ]            [         Export         ]     |
+----------------------------------------------------------------------+
```

### Cropping Settings Dialog
```
+----------------------------------------------------------------------+
| Cropping Parameters                                                   |
+----------------------------------------------------------------------+
|                                                                      |
| [X] Enable cropping                                                  |
|                                                                      |
| Crop Parameters:                                                     |
|    Top:    [____] px                                                 |
|    Left:   [____] px                                                 |
|    Width:  [____] px                                                 |
|    Height: [____] px                                                 |
|                                                                      |
| [X] Save as preset                                                   |
| Preset name: [Macular OCT Crop]                                      |
|                                                                      |
| Saved Presets:                                                       |
| [Macular OCT Crop▼]                                                  |
|                                                                      |
| [         Cancel         ]            [          Save          ]     |
+----------------------------------------------------------------------+
```

## Technology Stack
1. **Programming Language**: Python 3.8+
2. **GUI Framework**: PyQt5/PySide2 for cross-platform UI
3. **Core Libraries**:
   - OCT-Converter for file parsing
   - NumPy and OpenCV for image processing
   - Pillow for image manipulation
4. **Packaging**: PyInstaller for creating standalone Windows executables

## Implementation Strategy
1. Develop core functionality using OCT-Converter library
2. Create basic UI components with PyQt5
3. Implement file import and preview functionality
4. Add frame selection capabilities
5. Implement image processing features (rotation, cropping)
6. Develop export functionality
7. Add settings and configuration options
8. Package as standalone Windows application

## Considerations
1. **Performance**: Optimize for handling large OCT datasets
2. **Memory Management**: Efficient handling of large image volumes
3. **Error Handling**: Robust error handling for file parsing issues
4. **Usability**: Intuitive interface for ophthalmology professionals
5. **Extensibility**: Design to allow future format support
