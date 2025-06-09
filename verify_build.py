import os
import sys

def check_file_exists(path, description):
    if not os.path.exists(path):
        print(f"❌ {description} not found at: {path}")
        return False
    print(f"✓ {description} found")
    return True

def verify_build_environment():
    print("🔍 Verifying build environment...\n")
    
    # Check for required files
    required_files = [
        ("src/main.py", "Main application file"),
        ("requirements.txt", "Dependencies file"),
        ("assets/icon.ico", "Application icon"),
        ("README.md", "Documentation"),
        ("LICENSE", "License file")
    ]
    
    all_ok = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_ok = False
    
    # Check Python version
    print("\n🐍 Python version:", sys.version.split(' ')[0])
    
    # Check for required directories
    required_dirs = [
        ("src", "Source directory"),
        ("src/view", "View components"),
        ("src/controller", "Controller components"),
        ("src/model", "Model components")
    ]
    
    for dir_path, description in required_dirs:
        if not os.path.isdir(dir_path):
            print(f"❌ {description} directory not found: {dir_path}")
            all_ok = False
        else:
            print(f"✓ {description} directory found")
    
    return all_ok

if __name__ == "__main__":
    if verify_build_environment():
        print("\n✅ Build environment is ready!")
        print("You can now run 'build.bat' to build the application.")
    else:
        print("\n❌ Some required files or directories are missing.")
        print("Please check the output above and fix the issues before building.")
        sys.exit(1)
