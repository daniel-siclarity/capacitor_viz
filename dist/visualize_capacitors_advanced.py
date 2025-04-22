import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import random
from matplotlib.widgets import Button
import sys
import os

def read_capacitor_data(file_path):
    """Read capacitor data from CSV file."""
    return pd.read_csv(file_path)

def generate_random_color():
    """Generate a random color."""
    h = random.random()
    s = 0.7 + random.random() * 0.3  # High saturation
    v = 0.7 + random.random() * 0.3  # High value
    r, g, b = mcolors.hsv_to_rgb([h, s, v])
    return (r, g, b, 0.8)  # RGBA with alpha=0.8

def map_value_to_width(value, min_val, max_val, min_width=1, max_width=8):
    """Map capacitor value to line width."""
    if min_val == max_val:
        return (min_width + max_width) / 2
    normalized = (value - min_val) / (max_val - min_val)
    width = min_width + normalized * (max_width - min_width)
    return width

def visualize_capacitors_as_lines(data_file):
    """Visualize capacitors as 3D lines connecting start and end points."""
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
    ax = fig.add_subplot(111, projection='3d')
    
    # Seed random for reproducible colors
    random.seed(42)
    
    # Get value range for mapping to line widths
    min_val = df['Value'].min()
    max_val = df['Value'].max()
    
    # Generate colors for each capacitor
    colors = {row['Capacitor_Name']: generate_random_color() for _, row in df.iterrows()}
    
    # Store line objects and legend elements
    lines = []
    legend_elements = []
    
    # Plot nodes and connections for each capacitor
    for _, row in df.iterrows():
        capacitor_name = row['Capacitor_Name']
        start = (row['Start_X'], row['Start_Y'], row['Start_Z'])
        end = (row['End_X'], row['End_Y'], row['End_Z'])
        value = row['Value']
        
        # Get the color for this capacitor
        color = colors[capacitor_name]
        
        # Map value to line width
        line_width = map_value_to_width(value, min_val, max_val)
        
        # Plot the start and end points as small spheres
        ax.scatter(*start, color=color, s=30, alpha=0.8)
        ax.scatter(*end, color=color, s=30, alpha=0.8)
        
        # Plot a line connecting the points
        line = ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]],
                 color=color, linewidth=line_width, label=f"{capacitor_name} ({value:.2e})")
        lines.append(line)
        
        # Create legend entry
        rgb_color = color[:3]  # Remove alpha for legend
        legend_elements.append(mpatches.Patch(color=rgb_color, label=f"{capacitor_name} ({value:.2e})"))
    
    # Set axes limits
    all_points = np.vstack([
        df[['Start_X', 'Start_Y', 'Start_Z']].values,
        df[['End_X', 'End_Y', 'End_Z']].values
    ])
    
    min_vals = all_points.min(axis=0)
    max_vals = all_points.max(axis=0)
    
    # Add padding (10%)
    padding = 0.1 * (max_vals - min_vals)
    min_vals -= padding
    max_vals += padding
    
    ax.set_xlim(min_vals[0], max_vals[0])
    ax.set_ylim(min_vals[1], max_vals[1])
    ax.set_zlim(min_vals[2], max_vals[2])
    
    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Get the filename without path for the title
    filename = os.path.basename(data_file)
    ax.set_title(f'Capacitor Visualization: {filename}')
    
    # Add unit information
    unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
    
    # Create a custom colorbar for capacitance values
    # Create a scalar mappable for the colorbar
    norm = plt.Normalize(min_val, max_val)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, label=f'Capacitance ({unit})')
    
    # Create legend for capacitor names - place it outside the main plot
    leg = ax.legend(handles=legend_elements, loc='center left', 
               bbox_to_anchor=(1.05, 0.5), title="Capacitors", fontsize='small')
    
    # Add some information text
    info_text = (
        f"Total Capacitors: {len(df)}\n"
        f"Value Range: {min_val:.6e} - {max_val:.6e} {unit}\n"
        f"Line thickness indicates capacitance value"
    )
    
    # Add text with information
    fig.text(0.02, 0.02, info_text, ha='left', fontsize=10)
    
    # Add save button
    def save_figure(event):
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(data_file), "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on input file
        base_filename = os.path.splitext(os.path.basename(data_file))[0]
        file_name = os.path.join(output_dir, f"{base_filename}_line_view.png")
        
        plt.savefig(file_name, dpi=300, bbox_inches='tight')
        print(f"Figure saved as {file_name}")
    
    ax_save = plt.axes([0.8, 0.01, 0.15, 0.04])
    save_button = Button(ax_save, 'Save Figure', color='lightgoldenrodyellow')
    save_button.on_clicked(save_figure)
    
    # Adjust layout
    plt.subplots_adjust(left=0.05, right=0.78, top=0.95, bottom=0.1)
    
    plt.show()

if __name__ == "__main__":
    # Default data file path
    default_data_file = "coor_data/AND2X1/AND2X1_1_RT_6_1/AND2X1_1_RT_6_1_capacitor_coordinates.csv"
    
    # Use command line argument if provided, otherwise use default
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    
    visualize_capacitors_as_lines(data_file) 