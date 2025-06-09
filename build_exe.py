import PyInstaller.__main__
import os

# Get the absolute path to the icon file
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, 'resources', 'icon.ico')

# Run PyInstaller
PyInstaller.__main__.run([
    'src/main.py',                      # Your main script
    '--name=OCT-Extractor',             # Name of the executable
    '--onedir',                         # Create a directory with all dependencies
    '--windowed',                       # Windows application (not console)
    '--clean',                          # Clean PyInstaller cache
    f'--icon={icon_path}',              # Application icon
    '--add-data=resources:resources',   # Include resources directory
    '--hidden-import=numpy',            # Required dependencies
    '--hidden-import=PIL',
    '--hidden-import=h5py',
    '--hidden-import=matplotlib',
    '--hidden-import=PyQt5',
    '--hidden-import=json',
    '--noconsole',                      # No console window
])

print("Build completed. Executable should be in the 'dist/OCT-Extractor' directory.")
