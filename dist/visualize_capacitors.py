import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import random
import sys
import os

def read_capacitor_data(file_path):
    """Read capacitor data from CSV file."""
    return pd.read_csv(file_path)

def create_box_vertices(start_x, start_y, start_z, end_x, end_y, end_z):
    """Create vertices for a 3D box."""
    return [
        [start_x, start_y, start_z],
        [end_x, start_y, start_z],
        [end_x, end_y, start_z],
        [start_x, end_y, start_z],
        [start_x, start_y, end_z],
        [end_x, start_y, end_z],
        [end_x, end_y, end_z],
        [start_x, end_y, end_z]
    ]

def create_box_faces(vertices):
    """Create faces for a 3D box."""
    return [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # bottom
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # top
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # front
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # back
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # right
        [vertices[0], vertices[3], vertices[7], vertices[4]]   # left
    ]

def generate_random_color():
    """Generate a random color."""
    h = random.random()
    s = 0.7 + random.random() * 0.3  # High saturation
    v = 0.7 + random.random() * 0.3  # High value
    r, g, b = mcolors.hsv_to_rgb([h, s, v])
    return (r, g, b, 0.5)  # RGBA with alpha=0.5 for blending

def visualize_capacitors(data_file):
    """Visualize capacitors as 3D boxes."""
    # Read data
    try:
        df = read_capacitor_data(data_file)
        print(f"Successfully loaded data file: {data_file}")
        print(f"Found {len(df)} capacitor entries")
    except Exception as e:
        print(f"Error loading data file: {e}")
        return
    
    # Validate the CSV has the required columns
    required_columns = ['Capacitor_Name', 'Start_X', 'Start_Y', 'Start_Z', 'End_X', 'End_Y', 'End_Z', 'Value']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Error: Missing required columns in the CSV file: {', '.join(missing_columns)}")
        print("The CSV file must contain the following columns:")
        print(', '.join(required_columns))
        return
    
    # Create figure with larger size to accommodate legend and info
    fig = plt.figure(figsize=(14, 10))
    
    # Use GridSpec for better layout control
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(1, 1, figure=fig)
    ax = fig.add_subplot(gs[0, 0], projection='3d')
    
    # Set plot limits based on data range
    x_min, x_max = df[['Start_X', 'End_X']].values.min(), df[['Start_X', 'End_X']].values.max()
    y_min, y_max = df[['Start_Y', 'End_Y']].values.min(), df[['Start_Y', 'End_Y']].values.max()
    z_min, z_max = df[['Start_Z', 'End_Z']].values.min(), df[['Start_Z', 'End_Z']].values.max()
    
    # Add some padding to the limits
    padding = 0.05
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min
    
    ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
    ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
    ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
    
    # Store colors for legend
    colors = {}
    legend_elements = []
    
    # Seed random for reproducible colors
    random.seed(42)
    
    # Plot each capacitor
    for _, row in df.iterrows():
        # Get box coordinates
        capacitor_name = row['Capacitor_Name']
        start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
        end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
        
        # Create box
        vertices = create_box_vertices(start_x, start_y, start_z, end_x, end_y, end_z)
        faces = create_box_faces(vertices)
        
        # Create 3D collection of faces with a random color
        color = generate_random_color()
        colors[capacitor_name] = color
        
        poly = Poly3DCollection(faces, alpha=0.5, linewidth=1, edgecolor='black')
        poly.set_facecolor(color)
        
        # Add to plot
        ax.add_collection3d(poly)
        
        # Create legend entry
        rgb_color = color[:3]  # Remove alpha for legend
        legend_elements.append(mpatches.Patch(color=rgb_color, label=capacitor_name))
    
    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Get the filename without path for the title
    filename = os.path.basename(data_file)
    ax.set_title(f'Capacitor Visualization: {filename}')
    
    # Add unit information
    unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
    
    # Add colorbar with capacitor values
    norm = plt.Normalize(df['Value'].min(), df['Value'].max())
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, label=f'Capacitance ({unit})')
    
    # Create legend for capacitor names - place it outside the main plot
    leg = ax.legend(handles=legend_elements, loc='center left', 
              bbox_to_anchor=(1.05, 0.5), title="Capacitor Names", fontsize='small')
    
    # Add some information text using fig.text instead of figtext
    fig.text(0.02, 0.02, 
                f"Total Capacitors: {len(df)}\n"
                f"Value Range: {df['Value'].min():.6f} - {df['Value'].max():.6f} {unit}", 
                ha='left', fontsize=10)
    
    # Manually adjust layout instead of using tight_layout
    # This avoids the warning about tight_layout not being compatible with some elements
    plt.subplots_adjust(left=0.05, right=0.78, top=0.95, bottom=0.1)
    
    plt.show()

if __name__ == "__main__":
    # Default data file path
    default_data_file = "coor_data/AND2X1/AND2X1_1_RT_6_1/AND2X1_1_RT_6_1_capacitor_coordinates.csv"
    
    # Use command line argument if provided, otherwise use default
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    
    visualize_capacitors(data_file) 