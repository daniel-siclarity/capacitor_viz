"""
Script to generate a simple app icon for the Capacitor Visualizer application.
This creates icons for Windows (.ico), macOS (.icns), and Linux (.png).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
import os
import io

def create_3d_box():
    """Create a simple 3D box icon."""
    # Define figure with transparent background
    fig = plt.figure(figsize=(5, 5), dpi=100)
    fig.patch.set_alpha(0.0)
    ax = fig.add_subplot(111, projection='3d')
    
    # Turn off axis
    ax.set_axis_off()
    
    # Define cube vertices
    vertices = [
        [0, 0, 0],  # 0
        [1, 0, 0],  # 1
        [1, 1, 0],  # 2
        [0, 1, 0],  # 3
        [0, 0, 1],  # 4
        [1, 0, 1],  # 5
        [1, 1, 1],  # 6
        [0, 1, 1]   # 7
    ]
    
    # Define faces using indices
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # top
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # front
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # back
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # right
        [vertices[0], vertices[3], vertices[7], vertices[4]]   # left
    ]
    
    # Define face colors (with different alpha for each face for 3D effect)
    face_colors = [
        (0.1, 0.5, 0.9, 0.7),  # bottom - blue
        (0.9, 0.1, 0.1, 0.7),  # top - red
        (0.1, 0.9, 0.1, 0.5),  # front - green
        (0.9, 0.5, 0.1, 0.6),  # back - orange
        (0.5, 0.1, 0.9, 0.5),  # right - purple
        (0.9, 0.9, 0.1, 0.6)   # left - yellow
    ]
    
    # Create collections for each face
    for i, (face, color) in enumerate(zip(faces, face_colors)):
        # Create 3D collection for the face
        poly3d = Poly3DCollection([face], facecolor=color[:3], edgecolor='black', alpha=color[3])
        ax.add_collection3d(poly3d)
    
    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])
    
    # Set view angle
    ax.view_init(elev=30, azim=45)
    
    # Tight layout
    plt.tight_layout(pad=0)
    
    # Convert to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, transparent=True)
    buf.seek(0)
    img = Image.open(buf)
    
    plt.close(fig)
    return img

def create_icons(sizes=None):
    """Create icons in various sizes."""
    if sizes is None:
        # Standard icon sizes for various platforms
        sizes = [16, 32, 48, 64, 128, 256, 512]
    
    print("Generating app icons...")
    base_img = create_3d_box()
    
    # Create directory for icons if it doesn't exist
    os.makedirs('icons', exist_ok=True)
    
    # Save as PNG in various sizes
    images = []
    for size in sizes:
        img_resized = base_img.resize((size, size), Image.LANCZOS)
        img_resized.save(f'icons/icon_{size}x{size}.png')
        images.append(img_resized)
        print(f"Created {size}x{size} PNG icon")
    
    # Create Windows ICO
    try:
        # Windows icon
        base_img.save('app_icon.ico', sizes=[(s, s) for s in sizes])
        print("Created Windows ICO icon")
    except Exception as e:
        print(f"Warning: Could not create ICO file: {e}")
    
    # Create macOS ICNS if on macOS
    try:
        if os.name == 'posix' and os.path.exists('/usr/bin/iconutil'):
            # Create iconset directory
            iconset_dir = 'icons.iconset'
            os.makedirs(iconset_dir, exist_ok=True)
            
            # Save each size with the required naming convention
            for size in [16, 32, 128, 256, 512]:
                img_resized = base_img.resize((size, size), Image.LANCZOS)
                img_resized.save(f"{iconset_dir}/icon_{size}x{size}.png")
                
                # For Retina displays, also save 2x sizes
                if size * 2 <= 512:  # Don't exceed 512
                    img_2x = base_img.resize((size * 2, size * 2), Image.LANCZOS)
                    img_2x.save(f"{iconset_dir}/icon_{size}x{size}@2x.png")
            
            # Convert iconset to icns using iconutil
            os.system('iconutil -c icns icons.iconset')
            print("Created macOS ICNS icon")
            
            # Clean up
            import shutil
            shutil.rmtree(iconset_dir, ignore_errors=True)
        else:
            # Save as PNG for Linux/other systems
            base_img.resize((256, 256), Image.LANCZOS).save('app_icon.png')
            print("Created PNG icon for Linux/other systems")
    except Exception as e:
        print(f"Warning: Could not create ICNS file: {e}")
        # Fallback to PNG
        base_img.resize((256, 256), Image.LANCZOS).save('app_icon.png')
        print("Created PNG icon for Linux/other systems as fallback")
    
    print("Icon generation complete.")

if __name__ == "__main__":
    create_icons() 