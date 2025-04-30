import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import random
import sys
import os
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, LinearSegmentedColormap, BoundaryNorm
from matplotlib.widgets import Slider, TextBox, CheckButtons

def read_capacitor_data(file_path):
    """Read capacitor data from CSV file."""
    return pd.read_csv(file_path)

def analyze_capacitance_distribution(df):
    """Analyze the distribution of capacitance values and create suitable ranges."""
    values = df['Value'].values
    
    # Get basic statistics
    min_val = np.min(values)
    max_val = np.max(values)
    mean_val = np.mean(values)
    median_val = np.median(values)
    
    print(f"Capacitance Value Distribution:")
    print(f"Min: {min_val:.6e}, Max: {max_val:.6e}")
    print(f"Mean: {mean_val:.6e}, Median: {median_val:.6e}")
    
    # Method 1: Equal size bins
    num_bins = 5  # Default number of bins
    
    # If the range is very large (several orders of magnitude), use logarithmic bins
    if max_val / (min_val + 1e-10) > 100:
        print("Using logarithmic bins due to wide value range")
        bins = np.logspace(np.log10(max(min_val, 1e-15)), np.log10(max_val), num_bins+1)
    else:
        # Otherwise use equal width bins
        bins = np.linspace(min_val, max_val, num_bins+1)
    
    # Count the number of values in each bin
    hist, bin_edges = np.histogram(values, bins=bins)
    
    # Print histogram
    print("\nValue Distribution by Range:")
    for i in range(len(hist)):
        print(f"{bin_edges[i]:.6e} to {bin_edges[i+1]:.6e}: {hist[i]} capacitors ({hist[i]/len(values)*100:.1f}%)")
    
    # Create color ranges
    color_ranges = []
    for i in range(len(hist)):
        color_ranges.append({
            'min': bin_edges[i],
            'max': bin_edges[i+1],
            'label': f"{bin_edges[i]:.3e} - {bin_edges[i+1]:.3e}",
            'count': hist[i],
            'percentage': hist[i]/len(values)*100
        })
    
    return color_ranges, bin_edges

def get_color_for_value(value, norm, cmap):
    """Get a color for a specific capacitance value using the colormap."""
    return cmap(norm(value))

def visualize_capacitors(data_file):
    """Visualize capacitors as edges between start and end nodes."""
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
    
    # Analyze capacitance distribution and create color ranges
    color_ranges, bin_edges = analyze_capacitance_distribution(df)
    
    # Create figure with larger size to maximize visualization space
    fig = plt.figure(figsize=(16, 12))
    
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
    
    # Create a colormap for the capacitance values
    cmap = plt.cm.viridis
    norm = BoundaryNorm(bin_edges, cmap.N)
    
    # Store legend elements
    legend_elements = []
    
    # Store line objects for visibility control
    line_objects = []
    
    # Get capacitance value range for sliders
    capacitance_min = df['Value'].min()
    capacitance_max = df['Value'].max()
    
    # Plot each capacitor as an edge between start and end nodes
    for _, row in df.iterrows():
        # Get node coordinates
        capacitor_name = row['Capacitor_Name']
        start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
        end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
        
        # Get color based on capacitance value
        value = row['Value']
        color = get_color_for_value(value, norm, cmap)
        
        # Plot the edge as a line
        line, = ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                color=color, linewidth=2, marker='o', markersize=5)
        
        # Store the line object and its capacitance value for later filtering
        line_objects.append((line, value))
    
    # Find unique Z coordinates for the z-level planes
    z_coordinates = np.unique(np.concatenate([df['Start_Z'].values, df['End_Z'].values]))
    print(f"Found {len(z_coordinates)} unique Z levels: {z_coordinates}")
        
    # Create planes for each Z level (initially invisible)
    plane_objects = []
    for z in z_coordinates:
        # Create a rectangle at this Z level
        # Using a very light color with some transparency
        plane_color = 'lightblue'
        alpha = 0.15  # Low alpha for transparency
        
        # Create the plane as a rectangular surface
        xs = np.array([x_min - padding * x_range, x_max + padding * x_range])
        ys = np.array([y_min - padding * y_range, y_max + padding * y_range])
        X, Y = np.meshgrid(xs, ys)
        Z = np.full_like(X, z)
        
        # Plot the plane
        plane = ax.plot_surface(X, Y, Z, color=plane_color, alpha=alpha, shade=False)
        plane.set_visible(False)  # Initially invisible
        
        # Store the plane object
        plane_objects.append(plane)
    
    # Create a color legend with smaller font and compact format
    # Add unit information
    unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
    legend_title = f"Capacitance Ranges ({unit})"
    
    for i, range_info in enumerate(color_ranges):
        # Get the color for the middle of this range
        mid_val = (range_info['min'] + range_info['max']) / 2
        color = get_color_for_value(mid_val, norm, cmap)
        
        # Create a more compact label
        label = f"{range_info['label']} ({range_info['count']})"
        
        # Create a patch for the legend
        legend_elements.append(mpatches.Patch(color=color, label=label))
    
    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Get the filename without path for the title
    filename = os.path.basename(data_file)
    ax.set_title(f'Capacitor Edge Visualization: {filename}', fontsize=10)  # Smaller title
    
    # Create dedicated legend axes on the bottom right corner
    legend_ax = fig.add_axes([0.70, 0.05, 0.25, 0.20])  # Slightly smaller height
    legend_ax.axis('off')  # Hide axes
    legend = legend_ax.legend(handles=legend_elements, 
                             title=legend_title, 
                             fontsize='x-small',  # Smaller font for legend items
                             title_fontsize='small',  # Smaller font for legend title
                             loc='center')
    
    # Add some information text with smaller font
    stats_text = (
        f"Total: {len(df)} capacitors\n"
        f"Range: {df['Value'].min():.2e} - {df['Value'].max():.2e} {unit}\n"
        f"Mean: {df['Value'].mean():.2e} {unit}"
    )
    fig.text(0.02, 0.02, stats_text, ha='left', fontsize='x-small')
    
    # Add sliders for capacitance filtering
    # Make room for sliders and checkbox
    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.20)
    
    # Create slider axes
    slider_height = 0.02
    slider_left = 0.25
    slider_width = 0.45  # Slightly shorter to make room for text input
    
    # Min slider
    ax_min = plt.axes([slider_left, 0.12, slider_width, slider_height])
    min_slider = Slider(
        ax=ax_min,
        label='Min Capacitance',
        valmin=capacitance_min,
        valmax=capacitance_max,
        valinit=capacitance_min,
        valfmt='%1.2e ' + unit
    )
    
    # Min value text input
    ax_min_text = plt.axes([slider_left + slider_width + 0.01, 0.12, 0.08, slider_height])
    min_textbox = TextBox(
        ax=ax_min_text, 
        label='',
        initial=f"{capacitance_min:.2e}"
    )
    
    # Max slider
    ax_max = plt.axes([slider_left, 0.07, slider_width, slider_height])
    max_slider = Slider(
        ax=ax_max,
        label='Max Capacitance',
        valmin=capacitance_min,
        valmax=capacitance_max,
        valinit=capacitance_max,
        valfmt='%1.2e ' + unit
    )
    
    # Max value text input
    ax_max_text = plt.axes([slider_left + slider_width + 0.01, 0.07, 0.08, slider_height])
    max_textbox = TextBox(
        ax=ax_max_text, 
        label='',
        initial=f"{capacitance_max:.2e}"
    )
    
    # Create checkbox for Z-level planes
    ax_z_check = plt.axes([0.02, 0.07, 0.15, 0.05])
    z_check = CheckButtons(
        ax=ax_z_check,
        labels=['Show Z-Level Planes'],
        actives=[False]
    )
    
    # Function to toggle the z-level planes
    def toggle_z_planes(label):
        # Get the current state (now toggled by the checkbox)
        show_planes = z_check.get_status()[0]
        
        # Update visibility of all planes
        for plane in plane_objects:
            plane.set_visible(show_planes)
            
        # Redraw
        fig.canvas.draw_idle()
    
    # Connect the checkbox to the toggle function
    z_check.on_clicked(toggle_z_planes)
    
    # Function to update visibility based on slider values
    def update_from_slider(_):
        min_value = min_slider.val
        max_value = max_slider.val
        
        # Make sure min doesn't exceed max
        if min_value > max_value:
            if min_slider.val > max_slider.val:
                min_slider.set_val(max_slider.val)
                min_textbox.set_val(f"{max_slider.val:.2e}")
            else:
                max_slider.set_val(min_slider.val)
                max_textbox.set_val(f"{min_slider.val:.2e}")
            return
        
        # Update textboxes to match sliders
        min_textbox.set_val(f"{min_value:.2e}")
        max_textbox.set_val(f"{max_value:.2e}")
        
        # Update visibility of each line based on its capacitance value
        for line, value in line_objects:
            line.set_visible(min_value <= value <= max_value)
        
        # Update the figure
        fig.canvas.draw_idle()
    
    # Function to handle min textbox input
    def update_min_from_text(text):
        try:
            value = float(text)
            
            # Enforce min/max bounds
            if value < capacitance_min:
                value = capacitance_min
                min_textbox.set_val(f"{value:.2e}")
            elif value > capacitance_max:
                value = capacitance_max
                min_textbox.set_val(f"{value:.2e}")
                
            # Update slider
            min_slider.set_val(value)
            
            # Check if min exceeds max
            if value > max_slider.val:
                max_slider.set_val(value)
                max_textbox.set_val(f"{value:.2e}")
                
            # Update visibility
            for line, cap_value in line_objects:
                line.set_visible(value <= cap_value <= max_slider.val)
                
            fig.canvas.draw_idle()
            
        except ValueError:
            # Restore valid value if input is invalid
            min_textbox.set_val(f"{min_slider.val:.2e}")
    
    # Function to handle max textbox input
    def update_max_from_text(text):
        try:
            value = float(text)
            
            # Enforce min/max bounds
            if value > capacitance_max:
                value = capacitance_max
                max_textbox.set_val(f"{value:.2e}")
            elif value < capacitance_min:
                value = capacitance_min
                max_textbox.set_val(f"{value:.2e}")
                
            # Update slider
            max_slider.set_val(value)
            
            # Check if max is less than min
            if value < min_slider.val:
                min_slider.set_val(value)
                min_textbox.set_val(f"{value:.2e}")
                
            # Update visibility
            for line, cap_value in line_objects:
                line.set_visible(min_slider.val <= cap_value <= value)
                
            fig.canvas.draw_idle()
            
        except ValueError:
            # Restore valid value if input is invalid
            max_textbox.set_val(f"{max_slider.val:.2e}")
    
    # Connect the update functions to the inputs
    min_slider.on_changed(update_from_slider)
    max_slider.on_changed(update_from_slider)
    min_textbox.on_submit(update_min_from_text)
    max_textbox.on_submit(update_max_from_text)
    
    plt.show()

if __name__ == "__main__":
    # Default data file path
    default_data_file = "coor_data/AND2X1/AND2X1_1_RT_6_1/AND2X1_1_RT_6_1_capacitor_coordinates.csv"
    
    # Use command line argument if provided, otherwise use default
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    
    visualize_capacitors(data_file) 