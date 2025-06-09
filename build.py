import os
import PyInstaller.__main__
import shutil

def clean_build():
    """Remove previous build and dist directories."""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name} directory")

def build_executable():
    """Build the executable with PyInstaller."""
    # Main script
    script = 'src/main.py'
    
    # Application name
    app_name = 'OCT Extractor'
    
    # Additional data files (icons, images, etc.)
    datas = [
        ('src/view/icons/*', 'view/icons/'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ]
    
    # Hidden imports (libraries that PyInstaller might miss)
    hidden_imports = [
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'numpy',
        'PIL',
        'h5py',
        'matplotlib',
        'oct_converter',
        'oct_converter.readers',
        'oct_converter.readers.e2e',
        'oct_converter.readers.fda',
        'oct_converter.readers.fds',
        'oct_converter.readers.oct',
        'oct_converter.readers.img',
        'oct_converter.readers.poct',
    ]
    
    # Build command
    cmd = [
        script,
        '--name=' + app_name,
        '--windowed',
        '--onefile',
        '--clean',
        '--noconfirm',
    ]
    
    # Add data files
    for src, dst in datas:
        cmd.append(f'--add-data={src}{os.pathsep}{dst}')
    
    # Add hidden imports
    for imp in hidden_imports:
        cmd.append(f'--hidden-import={imp}')
    
    # Additional PyInstaller options
    cmd.extend([
        '--icon=assets/icon.ico',  # Make sure you have this file
        '--noconsole',
        '--add-binary=src/view/icons/*.ico;view/icons/',
    ])
    
    # Run PyInstaller
    PyInstaller.__main__.run(cmd)

if __name__ == '__main__':
    print("Starting build process...")
    clean_build()
    build_executable()
    print("\nBuild complete! The executable is in the 'dist' folder.")
