@echo off
echo Building OCT Extractor v2.0F executable...

:: Make sure dependencies are installed
echo Installing/updating dependencies...
pip install -r requirements.txt
pip install pyinstaller

:: Clean previous build files
echo Cleaning previous builds...
rmdir /s /q "build" 2>nul
rmdir /s /q "dist\OCT Extractor" 2>nul

:: Create the executable with hidden imports for OCT file formats
echo Building executable with all dependencies...
python -m PyInstaller ^
 --clean ^
 --name="OCT Extractor" ^
 --windowed ^
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
 --collect-all=oct_converter ^
 --icon="assets\icon.ico" ^
 --add-data="README.md;." ^
 --add-data="LICENSE;." ^
 src\main.py

if %ERRORLEVEL% equ 0 (
    echo Build successful! Executable is available in dist\OCT Extractor folder
) else (
    echo Build failed with error code %ERRORLEVEL%
)

pause
