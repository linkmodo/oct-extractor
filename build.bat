@echo off
setlocal enabledelayedexpansion

echo ===================================
echo OCT Extractor v2.0F Build Tool
echo ===================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Verify build environment
echo.
echo Verifying build environment...
python verify_build.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Build environment verification failed.
    pause
    exit /b 1
)

:: Install required packages if needed
echo.
echo Installing/updating required packages...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: Create necessary directories if they don't exist
if not exist "assets" mkdir assets
if not exist "dist" mkdir dist

:: Build the executable
echo.
echo Starting build process...
python build.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================
    echo Build successful! (%TIME%)
    echo The executable is in the 'dist\OCT Extractor' folder.
    echo.
    echo You can now run 'package.bat' to create a distributable ZIP.
    echo =======================================
) else (
    echo.
    echo =======================================
    echo Build failed with error code %ERRORLEVEL% (%TIME%)
    echo =======================================
    pause
    exit /b 1
)

pause
