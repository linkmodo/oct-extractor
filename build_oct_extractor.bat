@echo off
echo Building OCT Extractor v2.1 executable...

:: Make sure we're in the correct directory
cd /d "%~dp0"

:: Create required directories if they don't exist
if not exist "dist" mkdir dist
if not exist "build" mkdir build

:: Install required packages
echo Installing required packages...
pip install pyinstaller pyqt5 pillow numpy oct-converter h5py matplotlib

:: Clean up previous builds
echo Cleaning up previous builds...
rmdir /s /q "build" 2>nul
rmdir /s /q "dist\OCT Extractor" 2>nul

:: Build the executable
echo Building OCT Extractor...

python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "OCT Extractor" ^
    --icon "src/icon.ico" ^
    --add-data "src/icon.ico;." ^
    --add-data "README.md;." ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --hidden-import=h5py ^
    --hidden-import=matplotlib ^
    --hidden-import=oct_converter ^
    --hidden-import=oct_converter.readers ^
    --hidden-import=oct_converter.readers.e2e ^
    --hidden-import=oct_converter.readers.img ^
    --hidden-import=oct_converter.readers.fds ^
    --hidden-import=oct_converter.readers.fda ^
    --hidden-import=oct_converter.readers.oct ^
    --hidden-import=oct_converter.readers.poct ^
    --hidden-import=oct_converter.image ^
    --hidden-import=pkg_resources ^
    --hidden-import=imageio ^
    --hidden-import=natsort ^
    --hidden-import=opencv-python ^
    --hidden-import=pydicom ^
    --hidden-import=construct ^
    "src/main.py"

if %ERRORLEVEL% equ 0 (
    echo.
    echo Build successful! Executable is available in: dist\OCT Extractor
    echo.
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    echo.
)

pause
