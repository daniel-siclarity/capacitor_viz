import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import random
from matplotlib.widgets import Button, CheckButtons, Slider, TextBox
import sys
import os
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, LinearSegmentedColormap, BoundaryNorm

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

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)

def find_closest_edges(df, threshold=0.05):
    """Find edges that are close to each other."""
    proximity = []
    
    for i, row1 in df.iterrows():
        p1_start = np.array([row1['Start_X'], row1['Start_Y'], row1['Start_Z']])
        p1_end = np.array([row1['End_X'], row1['End_Y'], row1['End_Z']])
        
        for j, row2 in df.iloc[i+1:].iterrows():
            p2_start = np.array([row2['Start_X'], row2['Start_Y'], row2['Start_Z']])
            p2_end = np.array([row2['End_X'], row2['End_Y'], row2['End_Z']])
            
            # Calculate minimum distance between the two edges
            # This is a simplified approach - you could use a more accurate algorithm
            distances = [
                calculate_distance(p1_start, p2_start),
                calculate_distance(p1_start, p2_end),
                calculate_distance(p1_end, p2_start),
                calculate_distance(p1_end, p2_end)
            ]
            
            min_distance = min(distances)
            
            if min_distance < threshold:
                proximity.append({
                    'capacitor1': row1['Capacitor_Name'],
                    'capacitor2': row2['Capacitor_Name'],
                    'min_distance': min_distance
                })
    
    return proximity

def visualize_capacitors_advanced(data_file):
    """Visualize capacitors as edges with advanced features."""
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
    fig = plt.figure(figsize=(18, 12))
    
    # Use GridSpec for better layout control
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(1, 1, figure=fig)
    ax = fig.add_subplot(gs[0, 0], projection='3d')
    
    # Create a colormap for the capacitance values
    cmap = plt.cm.viridis
    norm = BoundaryNorm(bin_edges, cmap.N)
    
    # Get capacitance value range for sliders
    capacitance_min = df['Value'].min()
    capacitance_max = df['Value'].max()
    
    # Store line objects for interactivity
    line_objects = []
    
    # Store legend elements
    legend_elements = []
    
    # Current visualization mode
    viz_mode = {'show_nodes': True, 'show_values': False, 'highlight_range': None}
    
    # Analysis of proximity
    proximity_data = find_closest_edges(df)
    
    # Add unit information
    unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
    legend_title = f"Capacitance Ranges ({unit})"
    
    # For storing capacitance min/max values
    capacitance_filter = {'min': capacitance_min, 'max': capacitance_max}
    
    def draw_edges():
        # Clear previous lines
        for line in line_objects:
            line.remove()
        line_objects.clear()
        
        # Clear the legend
        legend_elements.clear()
        
        # Plot each capacitor as an edge between nodes
        for _, row in df.iterrows():
            capacitor_name = row['Capacitor_Name']
            start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
            end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
            
            # Get color based on capacitance value
            value = row['Value']
            
            # Skip edges outside the capacitance filter range
            if value < capacitance_filter['min'] or value > capacitance_filter['max']:
                continue
                
            color = get_color_for_value(value, norm, cmap)
            
            # If highlighting a specific range, make other edges semi-transparent
            if viz_mode['highlight_range'] is not None:
                range_min, range_max = viz_mode['highlight_range']
                if value < range_min or value > range_max:
                    # Make the color more transparent for edges outside the highlighted range
                    color = list(color)
                    color[3] = 0.2  # Set low alpha for non-highlighted edges
            
            # Plot the edge as a line
            if viz_mode['show_nodes']:
                # With markers at the nodes
                line, = ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                              color=color, linewidth=2, marker='o', markersize=5)
            else:
                # Without markers
                line, = ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                              color=color, linewidth=2)
            
            line_objects.append(line)
            
            # Add capacitance values as text if enabled
            if viz_mode['show_values']:
                # Calculate midpoint of the edge
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                mid_z = (start_z + end_z) / 2
                
                # Add text with capacitance value
                ax.text(mid_x, mid_y, mid_z, f"{row['Value']:.3e}", 
                       color='black', fontsize=7, ha='center', va='center')
        
        # Create legend based on capacitance ranges - more compact
        for i, range_info in enumerate(color_ranges):
            # Get the color for the middle of this range
            mid_val = (range_info['min'] + range_info['max']) / 2
            color = get_color_for_value(mid_val, norm, cmap)
        
            # Create a more compact label
            label = f"{range_info['label']} ({range_info['count']})"
            
            # If this is the highlighted range, make it more prominent
            is_highlighted = False
            if viz_mode['highlight_range'] is not None:
                range_min, range_max = viz_mode['highlight_range']
                if range_info['min'] == range_min and range_info['max'] == range_max:
                    is_highlighted = True
            
            # Create a patch for the legend with a border for highlighted range
            patch = mpatches.Patch(
                color=color, 
                label=label,
                linewidth=2 if is_highlighted else 0,
                edgecolor='red' if is_highlighted else None
            )
            legend_elements.append(patch)
        
        # Create dedicated legend axes at the bottom right
        try:
            legend_ax.clear()
        except:
            pass
        
        legend = legend_ax.legend(handles=legend_elements, 
                                 title=legend_title, 
                                 fontsize='x-small',  # Smaller font
                                 title_fontsize='small',  # Smaller title font
                                 loc='center')
    
    def toggle_nodes(event):
        viz_mode['show_nodes'] = not viz_mode['show_nodes']
        ax.clear()
        setup_axes()
        draw_edges()
        toggle_nodes_button.label.set_text('Hide Nodes' if viz_mode['show_nodes'] else 'Show Nodes')
        fig.canvas.draw_idle()
    
    def toggle_values(event):
        viz_mode['show_values'] = not viz_mode['show_values']
        ax.clear()
        setup_axes()
        draw_edges()
        toggle_values_button.label.set_text('Hide Values' if viz_mode['show_values'] else 'Show Values')
        fig.canvas.draw_idle()
    
    def highlight_range(event):
        # Cycle through highlighting each range or none
        if viz_mode['highlight_range'] is None:
            # Start with first range
            viz_mode['highlight_range'] = (color_ranges[0]['min'], color_ranges[0]['max'])
            highlight_button.label.set_text(f"Highlight: {color_ranges[0]['label']}")
        else:
            # Find current range and go to next
            current_range = viz_mode['highlight_range']
            found = False
            for i, range_info in enumerate(color_ranges):
                if range_info['min'] == current_range[0] and range_info['max'] == current_range[1]:
                    found = True
                    if i < len(color_ranges) - 1:
                        # Go to next range
                        viz_mode['highlight_range'] = (color_ranges[i+1]['min'], color_ranges[i+1]['max'])
                        highlight_button.label.set_text(f"Highlight: {color_ranges[i+1]['label']}")
                    else:
                        # Turn off highlighting
                        viz_mode['highlight_range'] = None
                        highlight_button.label.set_text("Highlight Ranges")
                    break
            
            # If somehow we didn't find the current range, reset
            if not found:
                viz_mode['highlight_range'] = None
                highlight_button.label.set_text("Highlight Ranges")
        
        # Redraw with new highlighting
        ax.clear()
        setup_axes()
        draw_edges()
        fig.canvas.draw_idle()
    
    def save_figure(event):
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(data_file), "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on input file
        base_filename = os.path.splitext(os.path.basename(data_file))[0]
        file_name = os.path.join(output_dir, f"{base_filename}_edges.png")
        
        plt.savefig(file_name, dpi=300, bbox_inches='tight')
        print(f"Figure saved as {file_name}")
    
    def update_min_slider(val):
        capacitance_filter['min'] = min_slider.val
        
        # Make sure min doesn't exceed max
        if capacitance_filter['min'] > capacitance_filter['max']:
            min_slider.set_val(capacitance_filter['max'])
            return
            
        # Update textbox
        min_textbox.set_val(f"{capacitance_filter['min']:.2e}")
            
        # Redraw with new filtering
        ax.clear()
        setup_axes()
        draw_edges()
        fig.canvas.draw_idle()
    
    def update_max_slider(val):
        capacitance_filter['max'] = max_slider.val
        
        # Make sure max isn't less than min
        if capacitance_filter['max'] < capacitance_filter['min']:
            max_slider.set_val(capacitance_filter['min'])
            return
            
        # Update textbox
        max_textbox.set_val(f"{capacitance_filter['max']:.2e}")
            
        # Redraw with new filtering
        ax.clear()
        setup_axes()
        draw_edges()
        fig.canvas.draw_idle()
        
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
                
            # Update slider and filter
            min_slider.set_val(value)
            capacitance_filter['min'] = value
            
            # Check if min exceeds max
            if value > capacitance_filter['max']:
                max_slider.set_val(value)
                max_textbox.set_val(f"{value:.2e}")
                capacitance_filter['max'] = value
                
            # Redraw with new filtering
            ax.clear()
            setup_axes()
            draw_edges()
            fig.canvas.draw_idle()
            
        except ValueError:
            # Restore valid value if input is invalid
            min_textbox.set_val(f"{capacitance_filter['min']:.2e}")
    
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
                
            # Update slider and filter
            max_slider.set_val(value)
            capacitance_filter['max'] = value
            
            # Check if max is less than min
            if value < capacitance_filter['min']:
                min_slider.set_val(value)
                min_textbox.set_val(f"{value:.2e}")
                capacitance_filter['min'] = value
                
            # Redraw with new filtering
            ax.clear()
            setup_axes()
            draw_edges()
            fig.canvas.draw_idle()
            
        except ValueError:
            # Restore valid value if input is invalid
            max_textbox.set_val(f"{capacitance_filter['max']:.2e}")
    
    def setup_axes():
        # Set plot limits based on data range
        x_min, x_max = df[['Start_X', 'End_X']].values.min(), df[['Start_X', 'End_X']].values.max()
        y_min, y_max = df[['Start_Y', 'End_Y']].values.min(), df[['Start_Y', 'End_Y']].values.max()
        z_min, z_max = df[['Start_Z', 'End_Z']].values.min(), df[['Start_Z', 'End_Z']].values.max()
        
        # Add some padding to the limits
        padding = 0.05
        x_range = max(x_max - x_min, 1e-6)  # Avoid division by zero
        y_range = max(y_max - y_min, 1e-6)
        z_range = max(z_max - z_min, 1e-6)
        
        ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
        ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
        ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
        
        # Set labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Get the filename without path for the title
        filename = os.path.basename(data_file)
        ax.set_title(f'Capacitor Edge Visualization: {filename}', fontsize=10)  # Smaller title
    
    # Create legend axes on the bottom right corner
    legend_ax = fig.add_axes([0.70, 0.05, 0.25, 0.20])  # Smaller height
    legend_ax.axis('off')  # Hide axes
    
    # Set up axes
    setup_axes()
    
    # Initial drawing
    draw_edges()
    
    # Make room for sliders
    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.20)
    
    # Create buttons for interactivity - position them in a column on the bottom right above the legend
    button_width = 0.12
    button_height = 0.03
    button_left = 0.82
    button_spacing = 0.01
    button_bottom = 0.32  # Above the legend
    
    # Position buttons
    ax_toggle_nodes = plt.axes([button_left, button_bottom, button_width, button_height])
    toggle_nodes_button = Button(ax_toggle_nodes, 'Hide Nodes', color='lightgoldenrodyellow')
    toggle_nodes_button.on_clicked(toggle_nodes)
    
    ax_toggle_values = plt.axes([button_left, button_bottom - (button_height + button_spacing), button_width, button_height])
    toggle_values_button = Button(ax_toggle_values, 'Show Values', color='lightgoldenrodyellow')
    toggle_values_button.on_clicked(toggle_values)
    
    ax_highlight = plt.axes([button_left, button_bottom - 2 * (button_height + button_spacing), button_width, button_height])
    highlight_button = Button(ax_highlight, 'Highlight Ranges', color='lightgoldenrodyellow')
    highlight_button.on_clicked(highlight_range)
    
    ax_save = plt.axes([button_left, button_bottom - 3 * (button_height + button_spacing), button_width, button_height])
    save_button = Button(ax_save, 'Save Figure', color='lightgoldenrodyellow')
    save_button.on_clicked(save_figure)
    
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
    min_slider.on_changed(update_min_slider)
    
    # Min value text input
    ax_min_text = plt.axes([slider_left + slider_width + 0.01, 0.12, 0.08, slider_height])
    min_textbox = TextBox(
        ax=ax_min_text, 
        label='',
        initial=f"{capacitance_min:.2e}"
    )
    min_textbox.on_submit(update_min_from_text)
    
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
    max_slider.on_changed(update_max_slider)
    
    # Max value text input
    ax_max_text = plt.axes([slider_left + slider_width + 0.01, 0.07, 0.08, slider_height])
    max_textbox = TextBox(
        ax=ax_max_text, 
        label='',
        initial=f"{capacitance_max:.2e}"
    )
    max_textbox.on_submit(update_max_from_text)
    
    # Add some information text - more compact with smaller font
    stats_text = (
        f"Total: {len(df)} capacitors\n"
        f"Range: {df['Value'].min():.2e} - {df['Value'].max():.2e} {unit}\n"
        f"Mean: {df['Value'].mean():.2e} {unit}"
    )
    
    if proximity_data:
        # Sort proximity data by distance
        proximity_data.sort(key=lambda x: x['min_distance'])
        # Add top 3 close edges to info text
        stats_text += "\n\nClosest Edges:"
        for i, prox in enumerate(proximity_data[:3]):
            stats_text += f"\n{prox['capacitor1']} & {prox['capacitor2']}: {prox['min_distance']:.2e}"
    
    # Place stats text in the bottom left
    fig.text(0.02, 0.02, stats_text, ha='left', fontsize='x-small')
    
    plt.show()

if __name__ == "__main__":
    # Default data file path
    default_data_file = "coor_data/AND2X1/AND2X1_1_RT_6_1/AND2X1_1_RT_6_1_capacitor_coordinates.csv"
    
    # Use command line argument if provided, otherwise use default
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    
    visualize_capacitors_advanced(data_file) 