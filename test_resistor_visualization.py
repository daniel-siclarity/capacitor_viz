#!/usr/bin/env python3
"""
Test script to demonstrate capacitor and resistor visualization.
"""

import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import BoundaryNorm
from mpl_toolkits.mplot3d import Axes3D

def visualize_components(capacitor_file=None, resistor_file=None):
    """
    Visualize capacitors and resistors from CSV files.
    
    Args:
        capacitor_file: Path to capacitor coordinates CSV file
        resistor_file: Path to resistor coordinates CSV file
    """
    # Create figure
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Track overall plot limits
    x_min, x_max = float('inf'), float('-inf')
    y_min, y_max = float('inf'), float('-inf')
    z_min, z_max = float('inf'), float('-inf')
    
    # Process capacitors if file is provided
    if capacitor_file and os.path.exists(capacitor_file):
        try:
            cap_df = pd.read_csv(capacitor_file)
            print(f"Loaded {len(cap_df)} capacitors from {capacitor_file}")
            
            # Get capacitance range
            cap_min = cap_df['Value'].min()
            cap_max = cap_df['Value'].max()
            
            # Create color bins for capacitance
            num_bins = 5
            if cap_max / (cap_min + 1e-10) > 100:
                # Use logarithmic bins for wide ranges
                bins = np.logspace(np.log10(max(cap_min, 1e-15)), np.log10(cap_max), num_bins+1)
            else:
                # Use equal width bins
                bins = np.linspace(cap_min, cap_max, num_bins+1)
            
            # Create colormap
            cap_cmap = plt.cm.viridis
            cap_norm = BoundaryNorm(bins, cap_cmap.N)
            
            # Plot each capacitor
            for _, row in cap_df.iterrows():
                start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
                end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
                
                # Get color based on value
                color = cap_cmap(cap_norm(row['Value']))
                
                # Plot the edge
                ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                     color=color, linewidth=2, marker='o', markersize=5)
                
                # Update plot limits
                x_min = min(x_min, start_x, end_x)
                x_max = max(x_max, start_x, end_x)
                y_min = min(y_min, start_y, end_y)
                y_max = max(y_max, start_y, end_y)
                z_min = min(z_min, start_z, end_z)
                z_max = max(z_max, start_z, end_z)
            
            # Add capacitor legend entry
            unit = cap_df['Unit'].iloc[0] if 'Unit' in cap_df.columns else ''
            plt.plot([], [], '-', color='gray', label=f'Capacitors ({unit})')
            
        except Exception as e:
            print(f"Error loading capacitor data: {e}")
    
    # Process resistors if file is provided
    if resistor_file and os.path.exists(resistor_file):
        try:
            res_df = pd.read_csv(resistor_file)
            print(f"Loaded {len(res_df)} resistors from {resistor_file}")
            
            # Get resistance range
            res_min = res_df['Value'].min()
            res_max = res_df['Value'].max()
            
            # Create color bins for resistance
            num_bins = 5
            if res_max / (res_min + 1e-10) > 100:
                # Use logarithmic bins for wide ranges
                bins = np.logspace(np.log10(max(res_min, 1e-15)), np.log10(res_max), num_bins+1)
            else:
                # Use equal width bins
                bins = np.linspace(res_min, res_max, num_bins+1)
            
            # Create colormap - different from capacitors
            res_cmap = plt.cm.plasma
            res_norm = BoundaryNorm(bins, res_cmap.N)
            
            # Plot each resistor
            for _, row in res_df.iterrows():
                start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
                end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
                
                # Get color based on value
                color = res_cmap(res_norm(row['Value']))
                
                # Plot the edge - dashed line with square markers for resistors
                ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                     color=color, linewidth=2, marker='s', markersize=5, linestyle='--')
                
                # Update plot limits
                x_min = min(x_min, start_x, end_x)
                x_max = max(x_max, start_x, end_x)
                y_min = min(y_min, start_y, end_y)
                y_max = max(y_max, start_y, end_y)
                z_min = min(z_min, start_z, end_z)
                z_max = max(z_max, start_z, end_z)
            
            # Add resistor legend entry
            unit = res_df['Unit'].iloc[0] if 'Unit' in res_df.columns else ''
            plt.plot([], [], '--', color='gray', label=f'Resistors ({unit})')
            
        except Exception as e:
            print(f"Error loading resistor data: {e}")
    
    # If no data was loaded
    if x_min == float('inf') or x_max == float('-inf'):
        print("No data was loaded. Please check your input files.")
        return
    
    # Add some padding to the plot limits
    padding = 0.05
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min
    
    ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
    ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
    ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    cap_name = os.path.basename(capacitor_file) if capacitor_file else "None"
    res_name = os.path.basename(resistor_file) if resistor_file else "None"
    title = f"Component Visualization\nCapacitors: {cap_name}, Resistors: {res_name}"
    ax.set_title(title, fontsize=10)
    
    # Add a legend
    ax.legend()
    
    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) > 2:
        cap_file = sys.argv[1]
        res_file = sys.argv[2]
        visualize_components(cap_file, res_file)
    elif len(sys.argv) > 1:
        # If only one file is provided, try to guess if it's a capacitor or resistor file
        file_path = sys.argv[1]
        if "capacitor" in file_path.lower():
            # It's likely a capacitor file, try to find a matching resistor file
            res_path = file_path.replace("capacitor", "resistor")
            if os.path.exists(res_path):
                visualize_components(file_path, res_path)
            else:
                visualize_components(capacitor_file=file_path)
        elif "resistor" in file_path.lower():
            # It's likely a resistor file, try to find a matching capacitor file
            cap_path = file_path.replace("resistor", "capacitor")
            if os.path.exists(cap_path):
                visualize_components(cap_path, file_path)
            else:
                visualize_components(resistor_file=file_path)
        else:
            # Can't determine, just use as capacitor file
            visualize_components(capacitor_file=file_path)
    else:
        # No arguments, use default files from sample location
        example_dir = os.path.join(os.path.expanduser("~"), "capacitor_visualizer_samples")
        cap_file = os.path.join(example_dir, "sample_capacitor_data.csv")
        res_file = os.path.join(example_dir, "sample_resistor_data.csv")
        
        if os.path.exists(cap_file) and os.path.exists(res_file):
            visualize_components(cap_file, res_file)
        else:
            print("Usage: python test_resistor_visualization.py [capacitor_file] [resistor_file]")
            print("No sample files found. Please create them first using the capacitor_visualizer_app.py application.") 