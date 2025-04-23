"""
Simpler icon generator script for the Capacitor Visualizer application.
This creates a basic icon without requiring matplotlib 3D.
"""

from PIL import Image, ImageDraw
import os
import shutil

def create_simple_icon(size=512):
    """Create a simple icon using PIL."""
    # Create a transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate positions
    margin = int(size * 0.1)
    box_size = size - 2 * margin
    
    # Define colors
    colors = {
        'front': (25, 230, 25, 180),    # Green
        'top': (230, 25, 25, 200),      # Red
        'right': (128, 25, 230, 180),   # Purple
        'outline': (0, 0, 0, 255)       # Black
    }
    
    # Draw a simple 3D cube
    # Front face (square)
    front_coords = [
        (margin, margin + box_size//3),                  # Top left
        (margin + box_size//3*2, margin + box_size//3),  # Top right
        (margin + box_size//3*2, margin + box_size),     # Bottom right
        (margin, margin + box_size)                      # Bottom left
    ]
    draw.polygon(front_coords, fill=colors['front'])
    draw.line(front_coords + [front_coords[0]], fill=colors['outline'], width=3)
    
    # Top face (parallelogram)
    top_coords = [
        (margin, margin + box_size//3),                  # Bottom left
        (margin + box_size//3*2, margin + box_size//3),  # Bottom right
        (margin + box_size, margin),                     # Top right
        (margin + box_size//3, margin)                   # Top left
    ]
    draw.polygon(top_coords, fill=colors['top'])
    draw.line(top_coords + [top_coords[0]], fill=colors['outline'], width=3)
    
    # Right face (parallelogram)
    right_coords = [
        (margin + box_size//3*2, margin + box_size//3),  # Top left
        (margin + box_size, margin),                     # Top right
        (margin + box_size, margin + box_size//3*2),     # Bottom right
        (margin + box_size//3*2, margin + box_size)      # Bottom left
    ]
    draw.polygon(right_coords, fill=colors['right'])
    draw.line(right_coords + [right_coords[0]], fill=colors['outline'], width=3)
    
    return img

def create_icons():
    """Create icons in various sizes."""
    print("Generating simple app icons...")
    
    # Create directory for icons if it doesn't exist
    os.makedirs('icons', exist_ok=True)
    
    # Standard icon sizes for various platforms
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    # Create base icon
    base_img = create_simple_icon(512)
    
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
        # Fallback - copy the largest PNG
        shutil.copy('icons/icon_256x256.png', 'app_icon.png')
        print("Created fallback PNG icon instead")
    
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