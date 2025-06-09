@echo off
echo ===================================
echo OCT Extractor v2.0F Packaging Tool
echo ===================================

:: Set version number
set VERSION=2.0F
set APP_NAME="OCT Extractor"
set DIST_DIR=dist\%APP_NAME% v%VERSION%
set ZIP_FILE=dist\%APP_NAME%_v%VERSION%.zip

:: Clean previous build
echo.
echo Cleaning previous build...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%ZIP_FILE%" del "%ZIP_FILE%"

:: Build the application
echo.
echo Building the application...
call build.bat
if %ERRORLEVEL% neq 0 (
    echo Build failed. Check the output for errors.
    pause
    exit /b 1
)

:: Create distribution directory
echo.
echo Creating distribution package...
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

:: Copy required files
xcopy /E /Y "dist\%APP_NAME%\*" "%DIST_DIR%\"
copy "README.md" "%DIST_DIR%\"
copy "LICENSE" "%DIST_DIR%\"

:: Create a ZIP archive
echo.
echo Creating ZIP archive...
powershell -command "Compress-Archive -Path '%DIST_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================
    echo Package created successfully!
    echo Location: %ZIP_FILE%
    echo =======================================
) else (
    echo.
    echo =======================================
    echo Failed to create package
    echo =======================================
)

pause
