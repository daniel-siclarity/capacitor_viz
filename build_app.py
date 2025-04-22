"""
Script to build the Capacitor Visualizer App into a standalone executable
using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import platform

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

def create_example_data():
    """Create example data file to be bundled with the application."""
    sample_dir = os.path.join("dist", "example_data")
    os.makedirs(sample_dir, exist_ok=True)
    
    file_path = os.path.join(sample_dir, "sample_capacitor_data.csv")
    
    # Create a sample CSV file with basic capacitor data
    sample_data = """Capacitor_Name,Start_X,Start_Y,Start_Z,End_X,End_Y,End_Z,Value,Unit
Cap1,0.0,0.0,0.0,0.1,0.1,0.01,0.005,fF
Cap2,0.05,0.05,0.0,0.15,0.15,0.01,0.008,fF
Cap3,0.1,0.1,0.0,0.2,0.2,0.01,0.012,fF
Cap4,0.0,0.15,0.0,0.1,0.25,0.01,0.007,fF
Cap5,0.15,0.0,0.0,0.25,0.1,0.01,0.009,fF
Cap6,0.08,0.08,0.0,0.18,0.18,0.01,0.011,fF
"""
    
    with open(file_path, "w") as f:
        f.write(sample_data)
    
    print(f"Created example data at {file_path}")

def generate_app_icon():
    """Generate the application icon."""
    # Check for the main icon generator
    if not os.path.exists('app_icon.py'):
        # Check for the simple icon generator
        if os.path.exists('simple_icon.py'):
            print("Using simple icon generator...")
            try:
                subprocess.check_call([sys.executable, 'simple_icon.py'])
                print("Simple icon generation complete.")
                return True
            except Exception as e:
                print(f"Error generating simple icon: {e}")
                print("Continuing build without custom icon...")
                return False
        else:
            print("Icon generator scripts not found. Skipping icon generation.")
            return False
    
    # Try the main (matplotlib) icon generator
    try:
        print("Generating application icon...")
        subprocess.check_call([sys.executable, 'app_icon.py'])
        print("Icon generation complete.")
        return True
    except Exception as e:
        print(f"Error with main icon generator: {e}")
        # Try the simple icon generator as fallback
        if os.path.exists('simple_icon.py'):
            print("Trying simple icon generator as fallback...")
            try:
                subprocess.check_call([sys.executable, 'simple_icon.py'])
                print("Simple icon generation complete.")
                return True
            except Exception as e2:
                print(f"Error generating simple icon: {e2}")
                print("Continuing build without custom icon...")
                return False
        else:
            print("No fallback icon generator found. Continuing without custom icon...")
            return False

def build_app():
    """Build the application into an executable."""
    print("Building Capacitor Visualizer App...")
    
    # Generate app icon
    try:
        icon_generated = generate_app_icon()
    except Exception as e:
        print(f"Icon generation error: {e}")
        print("Continuing build without custom icon...")
        icon_generated = False
    
    # Determine the platform-specific options
    system = platform.system().lower()
    
    # Check if icons exist, regardless of whether we just generated them
    ico_exists = os.path.exists('app_icon.ico')
    icns_exists = os.path.exists('app_icon.icns')
    png_exists = os.path.exists('app_icon.png')
    
    if system == 'windows':
        icon_option = ['--icon=app_icon.ico'] if ico_exists else []
        separator = ';'
        ext = '.exe'
    elif system == 'darwin':
        icon_option = ['--icon=app_icon.icns'] if icns_exists else []
        separator = ':'
        ext = '.app'
    else:  # Linux and others
        icon_option = ['--icon=app_icon.png'] if png_exists else []
        separator = ':'
        ext = ''
    
    # Adjust add-data format based on platform
    add_data_format = f'README.md{separator}.'
    
    # Clean build and dist directories first
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name} directory")
    
    # Build the executable
    pyinstaller_args = [
        'pyinstaller',
        '--name=CapacitorVisualizer',
        '--onefile',
        '--windowed',
        '--clean',
        *icon_option,
        f'--add-data={add_data_format}',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=matplotlib',
        '--hidden-import=scipy',
        '--hidden-import=matplotlib.backends.backend_tkagg',
        '--hidden-import=tkinter',
        'capacitor_visualizer_app.py'
    ]
    
    try:
        subprocess.check_call(pyinstaller_args)
        print(f"Successfully built the application at dist/CapacitorVisualizer{ext}")
    except subprocess.CalledProcessError as e:
        print(f"Error building application: {e}")
        print("Trying alternate build method...")
        
        # Fallback to a more reliable but less optimized build
        alt_args = [
            'pyinstaller',
            '--name=CapacitorVisualizer',
            '--windowed',
            '--clean',
            *icon_option,
            f'--add-data={add_data_format}',
            'capacitor_visualizer_app.py'
        ]
        
        try:
            subprocess.check_call(alt_args)
            print(f"Successfully built the application with alternate method at dist/CapacitorVisualizer{ext}")
        except subprocess.CalledProcessError as e:
            print(f"Error building application with alternate method: {e}")
            print("Build failed. Please check the requirements and try again.")
            return
    
    # Create example data
    create_example_data()
    
    # Copy additional files if needed
    files_to_copy = [
        'README.md',
        'visualize_capacitors.py',
        'visualize_capacitors_advanced.py'
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            dest = os.path.join('dist', file)
            shutil.copy2(file, dest)
            print(f"Copied {file} to {dest}")
    
    print("\nBuild complete!")
    print("The executable can be found in the 'dist' directory.")
    
    print("\nUsage:")
    print("1. Run the CapacitorVisualizer executable")
    print("2. Use the GUI to load your capacitor data CSV file")
    print("3. Customize visualization options")
    print("4. Click 'Visualize' to generate the visualization")
    print("5. Use the 'Save Visualization' button to export the result as an image")

def check_dependencies():
    """Check and install required dependencies."""
    if os.path.exists("packaging_requirements.txt"):
        print("Checking for required dependencies...")
        try:
            # Check if required packages are installed
            process = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "packaging_requirements.txt", "--dry-run"],
                capture_output=True, 
                text=True
            )
            
            # If dry run indicates packages would be installed
            if "would be installed" in process.stdout or "would be installed" in process.stderr:
                print("Some required packages are missing. Installing...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "packaging_requirements.txt"])
                print("Dependencies installed successfully.")
            else:
                print("All required dependencies are already installed.")
                
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to check or install dependencies: {e}")
            print("Continuing anyway, but build might fail.")
    else:
        print("Warning: packaging_requirements.txt not found. Dependency check skipped.")

if __name__ == "__main__":
    check_dependencies()
    check_pyinstaller()
    build_app() 