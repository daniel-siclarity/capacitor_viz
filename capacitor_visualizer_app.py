import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import random
from matplotlib.widgets import Button
import threading
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, LinearSegmentedColormap, BoundaryNorm
import re
import json
import platform

# Import visualization functionality
try:
    import visualize_capacitors as basic_vis
    import visualize_capacitors_advanced as advanced_vis
    IMPORTED_MODULES = True
except ImportError:
    IMPORTED_MODULES = False

class CapacitorVisualizerApp:
    def __init__(self, root, capacitor_file=None, resistor_file=None, highlight_outliers=False):
        """Initialize the application."""
        self.root = root
        self.root.title("RLC Network Visualizer")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Configure styles for buttons, labels, and frames
        self.configure_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window to separate control panel from visualization area
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create control frame with scrollbar (on the left)
        self.control_frame_outer = ttk.Frame(self.paned_window, width=350)
        
        # Add a canvas for scrolling
        self.control_canvas = tk.Canvas(self.control_frame_outer)
        self.control_scrollbar = ttk.Scrollbar(self.control_frame_outer, orient="vertical", command=self.control_canvas.yview)
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)
        
        # Pack scrollbar and canvas
        self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create the actual control frame that will be scrolled
        self.control_frame = ttk.Frame(self.control_canvas)
        
        # Add the control frame to the canvas
        self.control_canvas_frame = self.control_canvas.create_window((0, 0), window=self.control_frame, anchor="nw")
        
        # Configure canvas to scroll with mousewheel and resize with window
        self.control_canvas.bind('<Configure>', self._configure_control_canvas)
        self.control_frame.bind('<Configure>', self._configure_control_frame)
        
        # Bind mousewheel to scroll with platform-specific options
        # For Windows and generic mousewheel
        self.control_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # For Linux
        self.control_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.control_canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        # Create the visualization frame (on the right)
        self.viz_container = ttk.Frame(self.paned_window)
        self.viz_frame = ttk.LabelFrame(self.viz_container, text="Visualization")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add frames to the paned window
        self.paned_window.add(self.control_frame_outer, weight=1)
        self.paned_window.add(self.viz_container, weight=4)
        
        # Create the title
        title_label = ttk.Label(self.control_frame, text="Circuit Component Visualization Tool", 
                               font=("Arial", 14, "bold"))  # Smaller title font
        title_label.pack(pady=(0, 10))
        
        # Create the data selection frame
        self.data_frame = ttk.LabelFrame(self.control_frame, text="Data Selection")
        self.data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Data file selection - Capacitors
        cap_frame = ttk.Frame(self.data_frame)
        cap_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        cap_label = ttk.Label(cap_frame, text="Capacitor Data File:")
        cap_label.pack(side=tk.LEFT, padx=(0, 10))
        
        cap_entry = ttk.Entry(cap_frame, textvariable=self.file_path_var, width=25)
        cap_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_cap_button = ttk.Button(cap_frame, text="Browse", command=self.browse_capacitor_file)
        browse_cap_button.pack(side=tk.LEFT)
        
        # Resistor data file selection
        res_frame = ttk.Frame(self.data_frame)
        res_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.resistor_file_path_var = tk.StringVar()
        res_label = ttk.Label(res_frame, text="Resistor Data File:")
        res_label.pack(side=tk.LEFT, padx=(0, 10))
        
        res_entry = ttk.Entry(res_frame, textvariable=self.resistor_file_path_var, width=25)
        res_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_res_button = ttk.Button(res_frame, text="Browse", command=self.browse_resistor_file)
        browse_res_button.pack(side=tk.LEFT)
        
        # Create example data button
        create_example_button = ttk.Button(self.data_frame, text="Create Example Data", 
                                         command=self.create_example_data)
        create_example_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Component selection
        component_frame = ttk.Frame(self.data_frame)
        component_frame.pack(fill=tk.X, padx=5, pady=5)
        
        component_label = ttk.Label(component_frame, text="Components to Show:")
        component_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.show_capacitors_var = tk.BooleanVar(value=True)
        cap_check = ttk.Checkbutton(component_frame, text="Capacitors", 
                                  variable=self.show_capacitors_var)
        cap_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.show_resistors_var = tk.BooleanVar(value=True)
        res_check = ttk.Checkbutton(component_frame, text="Resistors", 
                                  variable=self.show_resistors_var)
        res_check.pack(side=tk.LEFT)
        
        # Visualization type selection
        viz_frame = ttk.Frame(self.data_frame)
        viz_frame.pack(fill=tk.X, padx=5, pady=5)
        
        viz_label = ttk.Label(viz_frame, text="Visualization Type:")
        viz_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.viz_type_var = tk.StringVar(value="Basic")
        viz_basic_radio = ttk.Radiobutton(viz_frame, text="Basic", 
                                        variable=self.viz_type_var, value="Basic")
        viz_basic_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        viz_advanced_radio = ttk.Radiobutton(viz_frame, text="Advanced", 
                                           variable=self.viz_type_var, value="Advanced")
        viz_advanced_radio.pack(side=tk.LEFT)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.control_frame, text="Visualization Options")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Color scheme selection
        color_frame = ttk.Frame(options_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        color_label = ttk.Label(color_frame, text="Color Scheme:")
        color_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_scheme_var = tk.StringVar(value="viridis")
        color_schemes = ["viridis", "plasma", "inferno", "magma", "cividis", "rainbow"]
        color_combobox = ttk.Combobox(color_frame, textvariable=self.color_scheme_var, 
                                    values=color_schemes, width=15)
        color_combobox.pack(side=tk.LEFT, padx=(0, 20))
        
        # Number of bins for color ranges
        bins_label = ttk.Label(color_frame, text="Color Ranges:")
        bins_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.num_bins_var = tk.IntVar(value=5)
        bins_spinbox = ttk.Spinbox(color_frame, from_=2, to=10, width=5, 
                                 textvariable=self.num_bins_var)
        bins_spinbox.pack(side=tk.LEFT)
        
        # Line width option
        line_width_frame = ttk.Frame(options_frame)
        line_width_frame.pack(fill=tk.X, padx=5, pady=5)
        
        line_width_label = ttk.Label(line_width_frame, text="Line Width:")
        line_width_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.line_width_var = tk.DoubleVar(value=2.0)
        line_width_scale = ttk.Scale(line_width_frame, from_=0.5, to=5.0, orient=tk.HORIZONTAL,
                                   variable=self.line_width_var, length=150)
        line_width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Marker size option
        marker_size_frame = ttk.Frame(options_frame)
        marker_size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        marker_size_label = ttk.Label(marker_size_frame, text="Marker Size:")
        marker_size_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.marker_size_var = tk.DoubleVar(value=5.0)
        marker_size_scale = ttk.Scale(marker_size_frame, from_=1.0, to=10.0, orient=tk.HORIZONTAL,
                                    variable=self.marker_size_var, length=150)
        marker_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Capacitance filtering options
        cap_filter_frame = ttk.LabelFrame(self.control_frame, text="Capacitance Filter")
        cap_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Min capacitance slider
        min_cap_frame = ttk.Frame(cap_filter_frame)
        min_cap_frame.pack(fill=tk.X, padx=5, pady=5)
        
        min_cap_label = ttk.Label(min_cap_frame, text="Min Capacitance:")
        min_cap_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.min_cap_var = tk.DoubleVar(value=0.0)  # Will be updated when data is loaded
        self.min_cap_scale = ttk.Scale(min_cap_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                    variable=self.min_cap_var, length=150, 
                                    command=self.update_min_capacitance)
        self.min_cap_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Replace label with entry widget
        self.min_cap_entry_var = tk.StringVar(value="0.00e+00")
        self.min_cap_entry = ttk.Entry(min_cap_frame, textvariable=self.min_cap_entry_var, width=10)
        self.min_cap_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.min_cap_entry.bind("<Return>", self.update_min_from_entry)
        self.min_cap_entry.bind("<FocusOut>", self.update_min_from_entry)
        
        # Max capacitance slider
        max_cap_frame = ttk.Frame(cap_filter_frame)
        max_cap_frame.pack(fill=tk.X, padx=5, pady=5)
        
        max_cap_label = ttk.Label(max_cap_frame, text="Max Capacitance:")
        max_cap_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.max_cap_var = tk.DoubleVar(value=1.0)  # Will be updated when data is loaded
        self.max_cap_scale = ttk.Scale(max_cap_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                    variable=self.max_cap_var, length=150, 
                                    command=self.update_max_capacitance)
        self.max_cap_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Replace label with entry widget
        self.max_cap_entry_var = tk.StringVar(value="1.00e+00")
        self.max_cap_entry = ttk.Entry(max_cap_frame, textvariable=self.max_cap_entry_var, width=10)
        self.max_cap_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.max_cap_entry.bind("<Return>", self.update_max_from_entry)
        self.max_cap_entry.bind("<FocusOut>", self.update_max_from_entry)
        
        # Reset filters button
        reset_filters_button = ttk.Button(cap_filter_frame, text="Reset Filters", 
                                        command=self.reset_capacitance_filters)
        reset_filters_button.pack(pady=5)
        
        # Resistance filtering options
        res_filter_frame = ttk.LabelFrame(self.control_frame, text="Resistance Filter")
        res_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Min resistance slider
        min_res_frame = ttk.Frame(res_filter_frame)
        min_res_frame.pack(fill=tk.X, padx=5, pady=5)
        
        min_res_label = ttk.Label(min_res_frame, text="Min Resistance:")
        min_res_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.min_res_var = tk.DoubleVar(value=0.0)  # Will be updated when data is loaded
        self.min_res_scale = ttk.Scale(min_res_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                     variable=self.min_res_var, length=150, 
                                     command=self.update_min_resistance)
        self.min_res_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Entry for min resistance
        self.min_res_entry_var = tk.StringVar(value="0.00e+00")
        self.min_res_entry = ttk.Entry(min_res_frame, textvariable=self.min_res_entry_var, width=10)
        self.min_res_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.min_res_entry.bind("<Return>", self.update_min_res_from_entry)
        self.min_res_entry.bind("<FocusOut>", self.update_min_res_from_entry)
        
        # Max resistance slider
        max_res_frame = ttk.Frame(res_filter_frame)
        max_res_frame.pack(fill=tk.X, padx=5, pady=5)
        
        max_res_label = ttk.Label(max_res_frame, text="Max Resistance:")
        max_res_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.max_res_var = tk.DoubleVar(value=1.0)  # Will be updated when data is loaded
        self.max_res_scale = ttk.Scale(max_res_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                     variable=self.max_res_var, length=150, 
                                     command=self.update_max_resistance)
        self.max_res_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Entry for max resistance
        self.max_res_entry_var = tk.StringVar(value="1.00e+00")
        self.max_res_entry = ttk.Entry(max_res_frame, textvariable=self.max_res_entry_var, width=10)
        self.max_res_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.max_res_entry.bind("<Return>", self.update_max_res_from_entry)
        self.max_res_entry.bind("<FocusOut>", self.update_max_res_from_entry)
        
        # Reset resistor filters button
        reset_res_filters_button = ttk.Button(res_filter_frame, text="Reset Filters", 
                                           command=self.reset_resistance_filters)
        reset_res_filters_button.pack(pady=5)
        
        # Display options
        display_frame = ttk.Frame(options_frame)
        display_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Show nodes option
        self.show_nodes_var = tk.BooleanVar(value=True)
        show_nodes_check = ttk.Checkbutton(display_frame, text="Show Nodes", 
                                         variable=self.show_nodes_var)
        show_nodes_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Show values option
        self.show_values_var = tk.BooleanVar(value=False)
        show_values_check = ttk.Checkbutton(display_frame, text="Show Values", 
                                          variable=self.show_values_var)
        show_values_check.pack(side=tk.LEFT)
        
        # Show Z-level planes option
        self.show_z_planes_var = tk.BooleanVar(value=False)
        show_z_planes_check = ttk.Checkbutton(display_frame, text="Show Z-Level Planes", 
                                            variable=self.show_z_planes_var)
        show_z_planes_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # Logarithmic scale option
        scale_frame = ttk.Frame(options_frame)
        scale_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.use_log_scale_var = tk.BooleanVar(value=False)
        log_scale_check = ttk.Checkbutton(scale_frame, text="Use Logarithmic Scale", 
                                        variable=self.use_log_scale_var)
        log_scale_check.pack(side=tk.LEFT)
        
        # Button frame
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Visualize button
        visualize_button = ttk.Button(button_frame, text="Visualize", 
                                    command=self.visualize)
        visualize_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save Visualization", 
                               command=self.save_visualization)
        save_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Matplotlib figure and canvas
        self.fig = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.viz_frame)
        self.toolbar.update()
        
        # Initialize variables
        self.data_df = None
        self.resistor_df = None
        self.ax = None
        self.line_objects = []
        self.resistor_line_objects = []
        self.colors = {}
        self.legend_elements = []
        self.color_ranges = []
        self.resistance_color_ranges = []
        self.bin_edges = []
        self.resistance_bin_edges = []
        self.legend_ax = None
        self.plane_objects = []
        
        # Store capacitance and resistance range
        self.capacitance_min = 0.0
        self.capacitance_max = 1.0
        self.resistance_min = 0.0
        self.resistance_max = 1.0
        
        # Check if we have standalone mode
        if not IMPORTED_MODULES:
            self.include_visualization_functions()

    def include_visualization_functions(self):
        """Include the necessary functions when running as standalone app."""
        # Import needed functions
        global calculate_distance, find_closest_edges
        
        def calculate_distance(p1, p2):
            """Calculate Euclidean distance between two points."""
            return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)
        
        def find_closest_edges(df, threshold=0.05, component_type="capacitor"):
            """Find edges that are close to each other.
            
            Args:
                df: DataFrame containing component coordinates
                threshold: Distance threshold for considering edges "close"
                component_type: 'capacitor' or 'resistor'
            """
            proximity = []
            
            # Determine name column based on component type
            name_col = 'Capacitor_Name' if component_type == "capacitor" else 'Resistor_Name'
            
            for i, row1 in df.iterrows():
                p1_start = np.array([row1['Start_X'], row1['Start_Y'], row1['Start_Z']])
                p1_end = np.array([row1['End_X'], row1['End_Y'], row1['End_Z']])
                
                for j, row2 in df.iloc[i+1:].iterrows():
                    p2_start = np.array([row2['Start_X'], row2['Start_Y'], row2['Start_Z']])
                    p2_end = np.array([row2['End_X'], row2['End_Y'], row2['End_Z']])
                    
                    # Calculate minimum distance between the two edges
                    # This is a simplified approach
                    distances = [
                        calculate_distance(p1_start, p2_start),
                        calculate_distance(p1_start, p2_end),
                        calculate_distance(p1_end, p2_start),
                        calculate_distance(p1_end, p2_end)
                    ]
                    
                    min_distance = min(distances)
                    
                    if min_distance < threshold:
                        proximity.append({
                            'capacitor1': row1[name_col],
                            'capacitor2': row2[name_col],
                            'min_distance': min_distance
                        })
            
            return proximity
        
        # Assign functions to the global scope
        self.calculate_distance = calculate_distance
        self.find_closest_edges = find_closest_edges

    def browse_capacitor_file(self):
        """Open a file dialog to select the capacitor data file."""
        file_path = filedialog.askopenfilename(
            title="Select Capacitor Data File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_data(file_path, "capacitor")
            
            # Try to find matching resistor file if not already loaded
            if not self.resistor_file_path_var.get():
                # Parse path to look for resistor file in same directory
                dirname = os.path.dirname(file_path)
                basename = os.path.basename(file_path)
                # Replace capacitor with resistor in filename
                resistor_filename = basename.replace("capacitor", "resistor")
                resistor_filepath = os.path.join(dirname, resistor_filename)
                
                if os.path.exists(resistor_filepath):
                    self.resistor_file_path_var.set(resistor_filepath)
                    self.load_data(resistor_filepath, "resistor")
    
    def browse_resistor_file(self):
        """Open a file dialog to select the resistor data file."""
        file_path = filedialog.askopenfilename(
            title="Select Resistor Data File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.resistor_file_path_var.set(file_path)
            self.load_data(file_path, "resistor")
            
            # Try to find matching capacitor file if not already loaded
            if not self.file_path_var.get():
                # Parse path to look for capacitor file in same directory
                dirname = os.path.dirname(file_path)
                basename = os.path.basename(file_path)
                # Replace resistor with capacitor in filename
                capacitor_filename = basename.replace("resistor", "capacitor")
                capacitor_filepath = os.path.join(dirname, capacitor_filename)
                
                if os.path.exists(capacitor_filepath):
                    self.file_path_var.set(capacitor_filepath)
                    self.load_data(capacitor_filepath, "capacitor")

    def create_example_data(self):
        """Create example data files for testing."""
        # Create a sample data directory
        sample_dir = os.path.join(os.path.expanduser("~"), "capacitor_visualizer_samples")
        os.makedirs(sample_dir, exist_ok=True)
        
        # Create capacitor file
        cap_file_path = os.path.join(sample_dir, "sample_capacitor_data.csv")
        
        cap_sample_data = """Capacitor_Name,Start_X,Start_Y,Start_Z,End_X,End_Y,End_Z,Value,Unit
Cap1,0.0,0.0,0.0,0.1,0.1,0.01,0.005,fF
Cap2,0.05,0.05,0.0,0.15,0.15,0.01,0.008,fF
Cap3,0.1,0.1,0.0,0.2,0.2,0.01,0.012,fF
Cap4,0.0,0.15,0.0,0.1,0.25,0.01,0.007,fF
Cap5,0.15,0.0,0.0,0.25,0.1,0.01,0.009,fF
Cap6,0.08,0.08,0.0,0.18,0.18,0.01,0.015,fF
Cap7,0.12,0.12,0.0,0.22,0.22,0.01,0.020,fF
Cap8,0.05,0.15,0.0,0.15,0.25,0.01,0.004,fF
Cap9,0.18,0.05,0.0,0.28,0.15,0.01,0.003,fF
Cap10,0.15,0.15,0.0,0.25,0.25,0.01,0.025,fF
"""
        
        with open(cap_file_path, "w") as f:
            f.write(cap_sample_data)
        
        # Create resistor file
        res_file_path = os.path.join(sample_dir, "sample_resistor_data.csv")
        
        res_sample_data = """Resistor_Name,Start_X,Start_Y,Start_Z,End_X,End_Y,End_Z,Value,Unit
Res1,0.0,0.0,0.0,0.1,0.1,0.02,100.5,Ohm
Res2,0.05,0.05,0.0,0.15,0.15,0.02,250.8,Ohm
Res3,0.1,0.1,0.0,0.2,0.2,0.02,75.2,Ohm
Res4,0.0,0.15,0.0,0.1,0.25,0.02,183.7,Ohm
Res5,0.15,0.0,0.0,0.25,0.1,0.02,321.9,Ohm
Res6,0.08,0.08,0.0,0.18,0.18,0.02,95.6,Ohm
Res7,0.12,0.12,0.0,0.22,0.22,0.02,542.3,Ohm
Res8,0.05,0.15,0.0,0.15,0.25,0.02,128.4,Ohm
Res9,0.18,0.05,0.0,0.28,0.15,0.02,420.7,Ohm
Res10,0.15,0.15,0.0,0.25,0.25,0.02,63.2,Ohm
"""
        
        with open(res_file_path, "w") as f:
            f.write(res_sample_data)
        
        # Set file paths in the UI
        self.file_path_var.set(cap_file_path)
        self.resistor_file_path_var.set(res_file_path)
        
        messagebox.showinfo(
            "Example Data Created", 
            f"Sample data files created at:\n{cap_file_path}\n{res_file_path}"
        )
        
        # Load the data
        self.load_data(cap_file_path, "capacitor")
        self.load_data(res_file_path, "resistor")

    def load_data(self, file_path, data_type="capacitor"):
        """Load and validate the data file for capacitors or resistors."""
        try:
            df = pd.read_csv(file_path)
            
            if data_type == "capacitor":
                self.data_df = df
                self.status_var.set(f"Loaded capacitor data from {os.path.basename(file_path)}: {len(df)} records")
                
                # Validate required columns
                required_columns = ['Capacitor_Name', 'Start_X', 'Start_Y', 'Start_Z', 
                                  'End_X', 'End_Y', 'End_Z', 'Value']
            else:  # resistor
                self.resistor_df = df
                self.status_var.set(f"Loaded resistor data from {os.path.basename(file_path)}: {len(df)} records")
                
                # Validate required columns
                required_columns = ['Resistor_Name', 'Start_X', 'Start_Y', 'Start_Z', 
                                  'End_X', 'End_Y', 'End_Z', 'Value']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                error_msg = f"Missing columns in the {data_type} data file: {', '.join(missing_columns)}"
                self.status_var.set(error_msg)
                messagebox.showerror("Data Error", error_msg)
                if data_type == "capacitor":
                    self.data_df = None
                else:
                    self.resistor_df = None
            else:
                # Update capacitance/resistance range sliders
                if data_type == "capacitor":
                    self.capacitance_min = df['Value'].min()
                    self.capacitance_max = df['Value'].max()
                    
                    # Configure sliders
                    self.min_cap_var.set(self.capacitance_min)
                    self.max_cap_var.set(self.capacitance_max)
                    
                    self.min_cap_scale.configure(from_=self.capacitance_min, to=self.capacitance_max)
                    self.max_cap_scale.configure(from_=self.capacitance_min, to=self.capacitance_max)
                    
                    # Update entry fields
                    self.min_cap_entry_var.set(f"{self.capacitance_min:.2e}")
                    self.max_cap_entry_var.set(f"{self.capacitance_max:.2e}")
                else:  # resistor
                    self.resistance_min = df['Value'].min()
                    self.resistance_max = df['Value'].max()
                    
                    # Configure sliders
                    self.min_res_var.set(self.resistance_min)
                    self.max_res_var.set(self.resistance_max)
                    
                    self.min_res_scale.configure(from_=self.resistance_min, to=self.resistance_max)
                    self.max_res_scale.configure(from_=self.resistance_min, to=self.resistance_max)
                    
                    # Update entry fields
                    self.min_res_entry_var.set(f"{self.resistance_min:.2e}")
                    self.max_res_entry_var.set(f"{self.resistance_max:.2e}")
            
        except Exception as e:
            self.status_var.set(f"Error loading {data_type} data: {str(e)}")
            messagebox.showerror(f"{data_type.title()} Data Loading Error", str(e))
            if data_type == "capacitor":
                self.data_df = None
            else:
                self.resistor_df = None

    def update_min_capacitance(self, _=None):
        """Update the min capacitance filter value label and constrain max slider."""
        value = self.min_cap_var.get()
        self.min_cap_entry_var.set(f"{value:.2e}")
        
        # Ensure max is at least equal to min
        if value > self.max_cap_var.get():
            self.max_cap_var.set(value)
            self.max_cap_entry_var.set(f"{value:.2e}")

    def update_max_capacitance(self, _=None):
        """Update the max capacitance filter value label and constrain min slider."""
        value = self.max_cap_var.get()
        self.max_cap_entry_var.set(f"{value:.2e}")
        
        # Ensure min is at most equal to max
        if value < self.min_cap_var.get():
            self.min_cap_var.set(value)
            self.min_cap_entry_var.set(f"{value:.2e}")

    def update_min_from_entry(self, event=None):
        """Update min capacitance slider from entry input."""
        try:
            # Parse scientific notation or regular float
            value_str = self.min_cap_entry_var.get().strip()
            value = float(value_str)
            
            # Check bounds
            if value < self.capacitance_min:
                value = self.capacitance_min
                self.min_cap_entry_var.set(f"{value:.2e}")
            elif value > self.capacitance_max:
                value = self.capacitance_max
                self.min_cap_entry_var.set(f"{value:.2e}")
                
            # Update slider
            self.min_cap_var.set(value)
            
            # Ensure max is not less than min
            if value > self.max_cap_var.get():
                self.max_cap_var.set(value)
                self.max_cap_entry_var.set(f"{value:.2e}")
                
        except ValueError:
            # Restore previous valid value on parse error
            self.min_cap_entry_var.set(f"{self.min_cap_var.get():.2e}")
    
    def update_max_from_entry(self, event=None):
        """Update max capacitance slider from entry input."""
        try:
            # Parse scientific notation or regular float
            value_str = self.max_cap_entry_var.get().strip()
            value = float(value_str)
        
            # Check bounds
            if value > self.capacitance_max:
                value = self.capacitance_max
                self.max_cap_entry_var.set(f"{value:.2e}")
            elif value < self.capacitance_min:
                value = self.capacitance_min
                self.max_cap_entry_var.set(f"{value:.2e}")
                
            # Update slider
            self.max_cap_var.set(value)
            
            # Ensure min is not greater than max
            if value < self.min_cap_var.get():
                self.min_cap_var.set(value)
                self.min_cap_entry_var.set(f"{value:.2e}")
                
        except ValueError:
            # Restore previous valid value on parse error
            self.max_cap_entry_var.set(f"{self.max_cap_var.get():.2e}")

    def reset_capacitance_filters(self):
        """Reset capacitance filters to the full data range."""
        if self.data_df is not None:
            self.min_cap_var.set(self.capacitance_min)
            self.max_cap_var.set(self.capacitance_max)
            self.min_cap_entry_var.set(f"{self.capacitance_min:.2e}")
            self.max_cap_entry_var.set(f"{self.capacitance_max:.2e}")

    def analyze_capacitance_distribution(self, df):
        """Analyze the distribution of capacitance values and create suitable ranges."""
        values = df['Value'].values
        
        # Get basic statistics
        min_val = np.min(values)
        max_val = np.max(values)
        mean_val = np.mean(values)
        median_val = np.median(values)
        
        self.status_var.set(f"Capacitance range: {min_val:.6e} to {max_val:.6e}")
        
        # Get number of bins from UI
        num_bins = self.num_bins_var.get()
        
        # If the range is very large (several orders of magnitude) or log scale is selected, use logarithmic bins
        if self.use_log_scale_var.get() or max_val / (min_val + 1e-10) > 100:
            # Ensure min_val is positive for log scale
            log_min = np.log10(max(min_val, 1e-15))
            log_max = np.log10(max_val)
            bins = np.logspace(log_min, log_max, num_bins+1)
        else:
            # Otherwise use equal width bins
            bins = np.linspace(min_val, max_val, num_bins+1)
        
        # Count the number of values in each bin
        hist, bin_edges = np.histogram(values, bins=bins)
        
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

    def get_color_for_value(self, value, norm, cmap):
        """Get a color for a specific capacitance value using the colormap."""
        return cmap(norm(value))

    def visualize_basic(self):
        """Basic visualization of capacitors and resistors as edges between nodes with color based on values."""
        if self.data_df is None and self.resistor_df is None:
            messagebox.showwarning("No Data", "Please load at least one data file (capacitor or resistor).")
            return
            
        # Clear previous plot
        self.fig.clear()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Reset collections and colors
        self.line_objects = []
        self.resistor_line_objects = []
        self.legend_elements = []
        self.plane_objects = []
        
        # Set global plot limits
        x_min, x_max = float('inf'), float('-inf')
        y_min, y_max = float('inf'), float('-inf')
        z_min, z_max = float('inf'), float('-inf')
        
        # Add a legend item to show the difference between capacitors and resistors
        if self.data_df is not None and self.show_capacitors_var.get() and self.resistor_df is not None and self.show_resistors_var.get():
            # Add visual style identifiers
            capacitor_style = plt.Line2D([0], [0], color='gray', lw=2, linestyle='-', 
                                       label='Capacitor Style')
            resistor_style = plt.Line2D([0], [0], color='gray', lw=2, linestyle='--', 
                                      label='Resistor Style')
            self.legend_elements.append(capacitor_style)
            self.legend_elements.append(resistor_style)
        
        # Capacitor visualization
        if self.data_df is not None and self.show_capacitors_var.get():
            df = self.data_df
            
            # Apply capacitance filters
            min_cap = self.min_cap_var.get()
            max_cap = self.max_cap_var.get()
            filtered_df = df[(df['Value'] >= min_cap) & (df['Value'] <= max_cap)]
            
            if len(filtered_df) == 0:
                messagebox.showwarning("No Data", "No capacitors match the current filter range.")
            else:
                # Analyze capacitance distribution and create color ranges
                self.color_ranges, self.bin_edges = self.analyze_capacitance_distribution(df)
                
                # Update plot limits based on capacitor data
                cap_x_min = filtered_df[['Start_X', 'End_X']].values.min()
                cap_x_max = filtered_df[['Start_X', 'End_X']].values.max()
                cap_y_min = filtered_df[['Start_Y', 'End_Y']].values.min()
                cap_y_max = filtered_df[['Start_Y', 'End_Y']].values.max()
                cap_z_min = filtered_df[['Start_Z', 'End_Z']].values.min()
                cap_z_max = filtered_df[['Start_Z', 'End_Z']].values.max()
        
                x_min, x_max = min(x_min, cap_x_min), max(x_max, cap_x_max)
                y_min, y_max = min(y_min, cap_y_min), max(y_max, cap_y_max)
                z_min, z_max = min(z_min, cap_z_min), max(z_max, cap_z_max)
        
                # Create a colormap for the capacitance values
                cap_cmap = plt.get_cmap(self.color_scheme_var.get())
                cap_norm = BoundaryNorm(self.bin_edges, cap_cmap.N)
        
                # Plot each capacitor as an edge between start and end nodes
                for _, row in filtered_df.iterrows():
                    # Get node coordinates
                    capacitor_name = row['Capacitor_Name']
                    start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
                    end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
            
                    # Get color based on capacitance value
                    value = row['Value']
                    color = self.get_color_for_value(value, cap_norm, cap_cmap)
                    
                    # Plot the edge as a line with optional markers
                    if self.show_nodes_var.get():
                        line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                         color=color, linewidth=self.line_width_var.get(), 
                                         marker='o', markersize=self.marker_size_var.get())
                    else:
                        line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                         color=color, linewidth=self.line_width_var.get())
                    
                    self.line_objects.append(line)
                    
                    # Show capacitance values if enabled
                    if self.show_values_var.get():
                        # Calculate midpoint of the edge
                        mid_x = (start_x + end_x) / 2
                        mid_y = (start_y + end_y) / 2
                        mid_z = (start_z + end_z) / 2
                        
                        # Add text with capacitance value
                        self.ax.text(mid_x, mid_y, mid_z, f"{row['Value']:.3e}", 
                                 color='black', fontsize=7, ha='center', va='center')
            
                # Create capacitor legend items
                cap_unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
                cap_legend_title = f"Capacitance Ranges ({cap_unit})"
                
                for i, range_info in enumerate(self.color_ranges):
                    # Get the color for the middle of this range
                    mid_val = (range_info['min'] + range_info['max']) / 2
                    color = self.get_color_for_value(mid_val, cap_norm, cap_cmap)
            
                    # Create a compact label
                    label = f"Cap: {range_info['label']} ({range_info['count']})"
                    
                    # Create a patch for the legend
                    self.legend_elements.append(mpatches.Patch(color=color, label=label))
        
        # Resistor visualization
        if self.resistor_df is not None and self.show_resistors_var.get():
            res_df = self.resistor_df
            
            # Apply resistance filters
            min_res = self.min_res_var.get()
            max_res = self.max_res_var.get()
            filtered_res_df = res_df[(res_df['Value'] >= min_res) & (res_df['Value'] <= max_res)]
            
            if len(filtered_res_df) == 0:
                messagebox.showwarning("No Data", "No resistors match the current filter range.")
            else:
                # Analyze resistance distribution and create color ranges
                self.resistance_color_ranges, self.resistance_bin_edges = self.analyze_resistance_distribution(res_df)
                
                # Update plot limits based on resistor data
                res_x_min = filtered_res_df[['Start_X', 'End_X']].values.min()
                res_x_max = filtered_res_df[['Start_X', 'End_X']].values.max()
                res_y_min = filtered_res_df[['Start_Y', 'End_Y']].values.min()
                res_y_max = filtered_res_df[['Start_Y', 'End_Y']].values.max()
                res_z_min = filtered_res_df[['Start_Z', 'End_Z']].values.min()
                res_z_max = filtered_res_df[['Start_Z', 'End_Z']].values.max()
                
                x_min, x_max = min(x_min, res_x_min), max(x_max, res_x_max)
                y_min, y_max = min(y_min, res_y_min), max(y_max, res_y_max)
                z_min, z_max = min(z_min, res_z_min), max(z_max, res_z_max)
                
                # Create a colormap for resistance values - different from capacitors
                res_cmap = plt.get_cmap('plasma')  # Different colormap for resistors
                res_norm = BoundaryNorm(self.resistance_bin_edges, res_cmap.N)
                
                # Plot each resistor as an edge between start and end nodes
                for _, row in filtered_res_df.iterrows():
                    # Get node coordinates
                    resistor_name = row['Resistor_Name']
                    start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
                    end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
                    
                    # Get color based on resistance value
                    value = row['Value']
                    color = self.get_color_for_value(value, res_norm, res_cmap)
                    
                    # Plot the edge as a line with optional markers
                    if self.show_nodes_var.get():
                        line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                         color=color, linewidth=self.line_width_var.get(), 
                                         marker='s', markersize=self.marker_size_var.get(),
                                         linestyle='--')  # Dashed line for resistors
                    else:
                        line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                         color=color, linewidth=self.line_width_var.get(),
                                         linestyle='--')  # Dashed line for resistors
                    
                    self.resistor_line_objects.append(line)
        
                    # Show resistance values if enabled
                    if self.show_values_var.get():
                        # Calculate midpoint of the edge
                        mid_x = (start_x + end_x) / 2
                        mid_y = (start_y + end_y) / 2
                        mid_z = (start_z + end_z) / 2
                        
                        # Add text with resistance value
                        self.ax.text(mid_x, mid_y, mid_z, f"{row['Value']:.1f}", 
                                 color='black', fontsize=7, ha='center', va='center')
        
                # Create resistor legend items
                res_unit = res_df['Unit'].iloc[0] if 'Unit' in res_df.columns else 'unknown unit'
                res_legend_title = f"Resistance Ranges ({res_unit})"
                
                for i, range_info in enumerate(self.resistance_color_ranges):
                    # Get the color for the middle of this range
                    mid_val = (range_info['min'] + range_info['max']) / 2
                    color = self.get_color_for_value(mid_val, res_norm, res_cmap)
                    
                    # Create a compact label
                    label = f"Res: {range_info['label']} ({range_info['count']})"
                    
                    # Create a patch for the legend
                    self.legend_elements.append(mpatches.Patch(color=color, label=label))
        
        # If no data was loaded or none passed the filters
        if x_min == float('inf') or x_max == float('-inf'):
            messagebox.showwarning("No Data", "No components match the current filter ranges.")
            return
            
        # Add some padding to the limits
        padding = 0.05
        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = z_max - z_min
        
        self.ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
        self.ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
        self.ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
        
        # Add Z-level planes if enabled
        if self.show_z_planes_var.get():
            # Collect all Z coordinates
            all_z_values = []
            
            if self.data_df is not None and self.show_capacitors_var.get():
                all_z_values.extend(self.data_df['Start_Z'].values)
                all_z_values.extend(self.data_df['End_Z'].values)
                
            if self.resistor_df is not None and self.show_resistors_var.get():
                all_z_values.extend(self.resistor_df['Start_Z'].values)
                all_z_values.extend(self.resistor_df['End_Z'].values)
        
            # Find unique Z coordinates
            z_coordinates = np.unique(np.array(all_z_values))
            self.status_var.set(f"Found {len(z_coordinates)} unique Z levels, drawing planes")
            
            # Store z coordinates for stats display
            self.z_levels_count = len(z_coordinates)
            self.z_levels = z_coordinates
            
            # Create planes for each Z level
            for z in z_coordinates:
                # Create a rectangle at this Z level with light blue color and transparency
                plane_color = 'lightblue'
                alpha = 0.3  # Increased alpha for less transparency
                
                # Create the plane as a rectangular surface
                xs = np.array([x_min - padding * x_range, x_max + padding * x_range])
                ys = np.array([y_min - padding * y_range, y_max + padding * y_range])
                X, Y = np.meshgrid(xs, ys)
                Z = np.full_like(X, z)
        
                # Plot the plane and store it
                plane = self.ax.plot_surface(X, Y, Z, color=plane_color, alpha=alpha, shade=False)
                self.plane_objects.append(plane)
        
        # Set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Get filenames for title
        cap_filename = os.path.basename(self.file_path_var.get()) if self.file_path_var.get() else ""
        res_filename = os.path.basename(self.resistor_file_path_var.get()) if self.resistor_file_path_var.get() else ""
        
        if cap_filename and res_filename:
            self.ax.set_title(f'Component Visualization: {cap_filename} & {res_filename}', fontsize=10)
        elif cap_filename:
            self.ax.set_title(f'Component Visualization: {cap_filename}', fontsize=10)
        elif res_filename:
            self.ax.set_title(f'Component Visualization: {res_filename}', fontsize=10)
        
        # Create dedicated legend axes on the bottom right corner
        self.legend_ax = self.fig.add_axes([0.70, 0.05, 0.25, 0.20])  # Smaller height
        self.legend_ax.axis('off')  # Hide axes
        legend = self.legend_ax.legend(handles=self.legend_elements, 
                                      fontsize='x-small',  # Smaller font for legend items
                                      title_fontsize='small',  # Smaller font for legend title
                                      loc='center')
        
        # Add some information text with smaller font
        stats_text = "Component Statistics:\n"
        
        if self.data_df is not None and self.show_capacitors_var.get():
            filtered_count = len(self.data_df[(self.data_df['Value'] >= self.min_cap_var.get()) & 
                                           (self.data_df['Value'] <= self.max_cap_var.get())])
            total_count = len(self.data_df)
            cap_unit = self.data_df['Unit'].iloc[0] if 'Unit' in self.data_df.columns else 'unknown unit'
            
            stats_text += (
                f"Capacitors: {filtered_count}/{total_count}\n"
                f"Filter: {self.min_cap_var.get():.2e} - {self.max_cap_var.get():.2e} {cap_unit}\n"
                f"Range: {self.data_df['Value'].min():.2e} - {self.data_df['Value'].max():.2e} {cap_unit}\n"
            )
        
        if self.resistor_df is not None and self.show_resistors_var.get():
            filtered_res_count = len(self.resistor_df[(self.resistor_df['Value'] >= self.min_res_var.get()) & 
                                                   (self.resistor_df['Value'] <= self.max_res_var.get())])
            total_res_count = len(self.resistor_df)
            res_unit = self.resistor_df['Unit'].iloc[0] if 'Unit' in self.resistor_df.columns else 'unknown unit'
            
            stats_text += (
                f"Resistors: {filtered_res_count}/{total_res_count}\n"
                f"Filter: {self.min_res_var.get():.2e} - {self.max_res_var.get():.2e} {res_unit}\n"
                f"Range: {self.resistor_df['Value'].min():.2e} - {self.resistor_df['Value'].max():.2e} {res_unit}\n"
            )
        
        # Add Z levels information if planes are shown
        if self.show_z_planes_var.get() and hasattr(self, 'z_levels_count') and self.z_levels_count > 0:
            stats_text += f"\nZ Levels: {self.z_levels_count}\n"
            if len(self.z_levels) <= 10:  # Only show all values if there aren't too many
                stats_text += f"Values: {', '.join([f'{z:.4f}' for z in sorted(self.z_levels)])}"
            else:
                stats_text += f"Range: {self.z_levels.min():.4f} to {self.z_levels.max():.4f}"
        
        self.fig.text(0.02, 0.02, stats_text, ha='left', fontsize='x-small')
        
        # Maximize the visualization area
        plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.15)
        self.canvas.draw()
        
        comp_count_text = []
        if self.data_df is not None and self.show_capacitors_var.get():
            filtered_count = len(self.data_df[(self.data_df['Value'] >= self.min_cap_var.get()) & 
                                           (self.data_df['Value'] <= self.max_cap_var.get())])
            comp_count_text.append(f"{filtered_count} capacitors")
        if self.resistor_df is not None and self.show_resistors_var.get():
            filtered_res_count = len(self.resistor_df[(self.resistor_df['Value'] >= self.min_res_var.get()) & 
                                                   (self.resistor_df['Value'] <= self.max_res_var.get())])
            comp_count_text.append(f"{filtered_res_count} resistors")
            
        self.status_var.set(f"Visualization created with {' and '.join(comp_count_text)}")

    def analyze_resistance_distribution(self, df):
        """Analyze the distribution of resistance values and create suitable ranges."""
        values = df['Value'].values
        
        # Get basic statistics
        min_val = np.min(values)
        max_val = np.max(values)
        mean_val = np.mean(values)
        median_val = np.median(values)
        
        self.status_var.set(f"Resistance range: {min_val:.6e} to {max_val:.6e}")
        
        # Get number of bins from UI
        num_bins = self.num_bins_var.get()
        
        # If the range is very large (several orders of magnitude) or log scale is selected, use logarithmic bins
        if self.use_log_scale_var.get() or max_val / (min_val + 1e-10) > 100:
            # Ensure min_val is positive for log scale
            log_min = np.log10(max(min_val, 1e-15))
            log_max = np.log10(max_val)
            bins = np.logspace(log_min, log_max, num_bins+1)
        else:
            # Otherwise use equal width bins
            bins = np.linspace(min_val, max_val, num_bins+1)
        
        # Count the number of values in each bin
        hist, bin_edges = np.histogram(values, bins=bins)
        
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

    def visualize(self):
        """Visualize the data based on selected visualization type."""
        if not self.file_path_var.get():
            messagebox.showwarning("No File Selected", "Please select a data file first.")
            return
        
        # Check if data is loaded
        if self.data_df is None:
            self.load_data(self.file_path_var.get(), "capacitor")
            if self.data_df is None:  # Still None after attempted load
                return
        
        # Run visualization in a separate thread to avoid GUI freezing
        viz_type = self.viz_type_var.get()
        
        if viz_type == "Basic":
            threading.Thread(target=self.visualize_basic_thread).start()
        else:
            threading.Thread(target=self.visualize_advanced_thread).start()

    def visualize_basic_thread(self):
        """Run basic visualization in a thread."""
        self.status_var.set("Creating basic visualization...")
        self.root.update_idletasks()
        
        # Call the visualization function directly
        self.root.after(0, self.visualize_basic)

    def visualize_advanced_thread(self):
        """Run advanced visualization in a thread."""
        self.status_var.set("Creating advanced visualization...")
        self.root.update_idletasks()
        
        # Call the visualization function directly
        self.root.after(0, self.visualize_advanced)

    def save_visualization(self):
        """Save the current visualization as an image file."""
        if self.fig is None:
            messagebox.showwarning("No Visualization", "Please create a visualization first.")
            return
        
        # Create a file dialog to select save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg"),
                ("PDF Files", "*.pdf"),
                ("SVG Files", "*.svg"),
                ("All Files", "*.*")
            ],
            title="Save Visualization As"
        )
        
        if file_path:
            try:
                # Save the figure
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Visualization saved to {file_path}")
                messagebox.showinfo("Save Successful", f"Visualization saved to:\n{file_path}")
            except Exception as e:
                self.status_var.set(f"Error saving figure: {str(e)}")
                messagebox.showerror("Save Error", str(e))

    def update_min_resistance(self, _=None):
        """Update the min resistance filter value label and constrain max slider."""
        value = self.min_res_var.get()
        self.min_res_entry_var.set(f"{value:.2e}")
        
        # Ensure max is at least equal to min
        if value > self.max_res_var.get():
            self.max_res_var.set(value)
            self.max_res_entry_var.set(f"{value:.2e}")
    
    def update_max_resistance(self, _=None):
        """Update the max resistance filter value label and constrain min slider."""
        value = self.max_res_var.get()
        self.max_res_entry_var.set(f"{value:.2e}")
        
        # Ensure min is at most equal to max
        if value < self.min_res_var.get():
            self.min_res_var.set(value)
            self.min_res_entry_var.set(f"{value:.2e}")
    
    def update_min_res_from_entry(self, event=None):
        """Update min resistance slider from entry input."""
        try:
            # Parse scientific notation or regular float
            value_str = self.min_res_entry_var.get().strip()
            value = float(value_str)
            
            # Check bounds
            if value < self.resistance_min:
                value = self.resistance_min
                self.min_res_entry_var.set(f"{value:.2e}")
            elif value > self.resistance_max:
                value = self.resistance_max
                self.min_res_entry_var.set(f"{value:.2e}")
                
            # Update slider
            self.min_res_var.set(value)
            
            # Ensure max is not less than min
            if value > self.max_res_var.get():
                self.max_res_var.set(value)
                self.max_res_entry_var.set(f"{value:.2e}")
                
        except ValueError:
            # Restore previous valid value on parse error
            self.min_res_entry_var.set(f"{self.min_res_var.get():.2e}")
    
    def update_max_res_from_entry(self, event=None):
        """Update max resistance slider from entry input."""
        try:
            # Parse scientific notation or regular float
            value_str = self.max_res_entry_var.get().strip()
            value = float(value_str)
            
            # Check bounds
            if value > self.resistance_max:
                value = self.resistance_max
                self.max_res_entry_var.set(f"{value:.2e}")
            elif value < self.resistance_min:
                value = self.resistance_min
                self.max_res_entry_var.set(f"{value:.2e}")
                
            # Update slider
            self.max_res_var.set(value)
            
            # Ensure min is not greater than max
            if value < self.min_res_var.get():
                self.min_res_var.set(value)
                self.min_res_entry_var.set(f"{value:.2e}")
                
        except ValueError:
            # Restore previous valid value on parse error
            self.max_res_entry_var.set(f"{self.max_res_var.get():.2e}")
    
    def reset_resistance_filters(self):
        """Reset resistance filters to the full data range."""
        if self.resistor_df is not None:
            self.min_res_var.set(self.resistance_min)
            self.max_res_var.set(self.resistance_max)
            self.min_res_entry_var.set(f"{self.resistance_min:.2e}")
            self.max_res_entry_var.set(f"{self.resistance_max:.2e}")

    def visualize_advanced(self):
        """Advanced visualization with interactive features for both capacitors and resistors."""
        if self.data_df is None and self.resistor_df is None:
            messagebox.showwarning("No Data", "Please load at least one data file (capacitor or resistor).")
            return
            
        # Clear previous plot
        self.fig.clear()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Reset collections and colors
        self.line_objects = []
        self.resistor_line_objects = []
        self.legend_elements = []
        self.plane_objects = []
        
        # Set global plot limits
        x_min, x_max = float('inf'), float('-inf')
        y_min, y_max = float('inf'), float('-inf')
        z_min, z_max = float('inf'), float('-inf')
        
        # Add a legend item to show the difference between capacitors and resistors
        if self.data_df is not None and self.show_capacitors_var.get() and self.resistor_df is not None and self.show_resistors_var.get():
            # Add visual style identifiers
            capacitor_style = plt.Line2D([0], [0], color='gray', lw=2, linestyle='-', 
                                       label='Capacitor Style')
            resistor_style = plt.Line2D([0], [0], color='gray', lw=2, linestyle='--', 
                                      label='Resistor Style')
            self.legend_elements.append(capacitor_style)
            self.legend_elements.append(resistor_style)
        
        # Capacitor visualization
        cap_filtered_df = None
        if self.data_df is not None and self.show_capacitors_var.get():
            df = self.data_df
            
            # Apply capacitance filters
            min_cap = self.min_cap_var.get()
            max_cap = self.max_cap_var.get()
            cap_filtered_df = df[(df['Value'] >= min_cap) & (df['Value'] <= max_cap)]
            
            if len(cap_filtered_df) == 0:
                messagebox.showwarning("No Data", "No capacitors match the current filter range.")
            else:
                # Analyze capacitance distribution and create color ranges
                self.color_ranges, self.bin_edges = self.analyze_capacitance_distribution(df)
                
                # Update plot limits based on capacitor data
                cap_x_min = cap_filtered_df[['Start_X', 'End_X']].values.min()
                cap_x_max = cap_filtered_df[['Start_X', 'End_X']].values.max()
                cap_y_min = cap_filtered_df[['Start_Y', 'End_Y']].values.min()
                cap_y_max = cap_filtered_df[['Start_Y', 'End_Y']].values.max()
                cap_z_min = cap_filtered_df[['Start_Z', 'End_Z']].values.min()
                cap_z_max = cap_filtered_df[['Start_Z', 'End_Z']].values.max()
                
                x_min, x_max = min(x_min, cap_x_min), max(x_max, cap_x_max)
                y_min, y_max = min(y_min, cap_y_min), max(y_max, cap_y_max)
                z_min, z_max = min(z_min, cap_z_min), max(z_max, cap_z_max)
                
                # Proximity analysis for capacitors
                cap_proximity_data = None
                if hasattr(self, 'find_closest_edges'):
                    cap_proximity_data = self.find_closest_edges(cap_filtered_df)
        
        # Resistor visualization
        res_filtered_df = None
        if self.resistor_df is not None and self.show_resistors_var.get():
            res_df = self.resistor_df
            
            # Apply resistance filters
            min_res = self.min_res_var.get()
            max_res = self.max_res_var.get()
            res_filtered_df = res_df[(res_df['Value'] >= min_res) & (res_df['Value'] <= max_res)]
            
            if len(res_filtered_df) == 0:
                messagebox.showwarning("No Data", "No resistors match the current filter range.")
            else:
                # Analyze resistance distribution and create color ranges
                self.resistance_color_ranges, self.resistance_bin_edges = self.analyze_resistance_distribution(res_df)
                
                # Update plot limits based on resistor data
                res_x_min = res_filtered_df[['Start_X', 'End_X']].values.min()
                res_x_max = res_filtered_df[['Start_X', 'End_X']].values.max()
                res_y_min = res_filtered_df[['Start_Y', 'End_Y']].values.min()
                res_y_max = res_filtered_df[['Start_Y', 'End_Y']].values.max()
                res_z_min = res_filtered_df[['Start_Z', 'End_Z']].values.min()
                res_z_max = res_filtered_df[['Start_Z', 'End_Z']].values.max()
                
                x_min, x_max = min(x_min, res_x_min), max(x_max, res_x_max)
                y_min, y_max = min(y_min, res_y_min), max(y_max, res_y_max)
                z_min, z_max = min(z_min, res_z_min), max(z_max, res_z_max)
                
                # Proximity analysis for resistors
                res_proximity_data = None
                if hasattr(self, 'find_closest_edges'):
                    res_proximity_data = self.find_closest_edges(res_filtered_df)
                    
        # If no data was loaded or none passed the filters
        if x_min == float('inf') or x_max == float('-inf'):
            messagebox.showwarning("No Data", "No components match the current filter ranges.")
            return
            
        # Add some padding to the limits
        padding = 0.05
        x_range = max(x_max - x_min, 1e-6)  # Avoid division by zero
        y_range = max(y_max - y_min, 1e-6)
        z_range = max(z_max - z_min, 1e-6)
        
        # Set up the plot axes
        self.ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
        self.ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
        self.ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
        
        # Set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Get filenames for title
        cap_filename = os.path.basename(self.file_path_var.get()) if self.file_path_var.get() else ""
        res_filename = os.path.basename(self.resistor_file_path_var.get()) if self.resistor_file_path_var.get() else ""
        
        if cap_filename and res_filename:
            self.ax.set_title(f'Component Visualization: {cap_filename} & {res_filename}', fontsize=10)
        elif cap_filename:
            self.ax.set_title(f'Component Visualization: {cap_filename}', fontsize=10)
        elif res_filename:
            self.ax.set_title(f'Component Visualization: {res_filename}', fontsize=10)
        
        # Add Z-level planes if enabled
        if self.show_z_planes_var.get():
            # Collect all Z coordinates
            all_z_values = []
            
            if self.data_df is not None and self.show_capacitors_var.get():
                all_z_values.extend(self.data_df['Start_Z'].values)
                all_z_values.extend(self.data_df['End_Z'].values)
                
            if self.resistor_df is not None and self.show_resistors_var.get():
                all_z_values.extend(self.resistor_df['Start_Z'].values)
                all_z_values.extend(self.resistor_df['End_Z'].values)
            
            # Find unique Z coordinates
            z_coordinates = np.unique(np.array(all_z_values))
            self.status_var.set(f"Found {len(z_coordinates)} unique Z levels, drawing planes")
            
            # Store z coordinates for stats display
            self.z_levels_count = len(z_coordinates)
            self.z_levels = z_coordinates
            
            # Create planes for each Z level
            for z in z_coordinates:
                # Create a rectangle at this Z level with light blue color and transparency
                plane_color = 'lightblue'
                alpha = 0.3  # Increased alpha for less transparency
                
                # Create the plane as a rectangular surface
                xs = np.array([x_min - padding * x_range, x_max + padding * x_range])
                ys = np.array([y_min - padding * y_range, y_max + padding * y_range])
                X, Y = np.meshgrid(xs, ys)
                Z = np.full_like(X, z)
                
                # Plot the plane and store it
                plane = self.ax.plot_surface(X, Y, Z, color=plane_color, alpha=alpha, shade=False)
                self.plane_objects.append(plane)
        
        # Create legend axes on the bottom right corner
        self.legend_ax = self.fig.add_axes([0.70, 0.05, 0.25, 0.20])  # Smaller height
        self.legend_ax.axis('off')  # Hide axes
        
        # Current visualization modes for capacitors and resistors
        cap_viz_mode = {'show_nodes': self.show_nodes_var.get(), 'show_values': self.show_values_var.get(), 'highlight_range': None}
        res_viz_mode = {'show_nodes': self.show_nodes_var.get(), 'show_values': self.show_values_var.get(), 'highlight_range': None}
        
        # Draw capacitors if available
        if cap_filtered_df is not None and len(cap_filtered_df) > 0:
            # Create a colormap for the capacitance values
            cap_cmap = plt.get_cmap(self.color_scheme_var.get())
            cap_norm = BoundaryNorm(self.bin_edges, cap_cmap.N)
            
            # Plot each capacitor as an edge
            for _, row in cap_filtered_df.iterrows():
                capacitor_name = row['Capacitor_Name']
                start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
                end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
                
                # Get color based on capacitance value
                value = row['Value']
                color = self.get_color_for_value(value, cap_norm, cap_cmap)
                
                # Plot the edge as a line
                if cap_viz_mode['show_nodes']:
                    line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                     color=color, linewidth=self.line_width_var.get(), 
                                     marker='o', markersize=self.marker_size_var.get())
                else:
                    line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                     color=color, linewidth=self.line_width_var.get())
                
                self.line_objects.append((line, value))
                
                # Add capacitance values as text if enabled
                if cap_viz_mode['show_values']:
                    # Calculate midpoint of the edge
                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    mid_z = (start_z + end_z) / 2
                    
                    # Add text with capacitance value
                    self.ax.text(mid_x, mid_y, mid_z, f"{row['Value']:.3e}", 
                             color='black', fontsize=7, ha='center', va='center')
            
            # Create a color legend for capacitors
            cap_unit = self.data_df['Unit'].iloc[0] if 'Unit' in self.data_df.columns else 'unknown unit'
            cap_legend_title = f"Capacitance Ranges ({cap_unit})"
            
            for i, range_info in enumerate(self.color_ranges):
                # Get the color for the middle of this range
                mid_val = (range_info['min'] + range_info['max']) / 2
                color = self.get_color_for_value(mid_val, cap_norm, cap_cmap)
                
                # Create a compact label
                label = f"Cap: {range_info['label']} ({range_info['count']})"
                
                # Create a patch for the legend
                self.legend_elements.append(mpatches.Patch(color=color, label=label))
        
        # Draw resistors if available
        if res_filtered_df is not None and len(res_filtered_df) > 0:
            # Create a colormap for resistance values - different from capacitors
            res_cmap = plt.get_cmap('plasma')  # Different colormap for resistors
            res_norm = BoundaryNorm(self.resistance_bin_edges, res_cmap.N)
            
            # Plot each resistor as an edge
            for _, row in res_filtered_df.iterrows():
                resistor_name = row['Resistor_Name']
                start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
                end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
                
                # Get color based on resistance value
                value = row['Value']
                color = self.get_color_for_value(value, res_norm, res_cmap)
                
                # Plot the edge as a line
                if res_viz_mode['show_nodes']:
                    line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                     color=color, linewidth=self.line_width_var.get(), 
                                     marker='s', markersize=self.marker_size_var.get(),
                                     linestyle='--')  # Dashed line for resistors
                else:
                    line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                     color=color, linewidth=self.line_width_var.get(),
                                     linestyle='--')  # Dashed line for resistors
                
                self.resistor_line_objects.append((line, value))
                
                # Add resistance values as text if enabled
                if res_viz_mode['show_values']:
                    # Calculate midpoint of the edge
                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    mid_z = (start_z + end_z) / 2
                    
                    # Add text with resistance value
                    self.ax.text(mid_x, mid_y, mid_z, f"{row['Value']:.1f}", 
                             color='black', fontsize=7, ha='center', va='center')
            
            # Create a color legend for resistors
            res_unit = self.resistor_df['Unit'].iloc[0] if 'Unit' in self.resistor_df.columns else 'unknown unit'
            res_legend_title = f"Resistance Ranges ({res_unit})"
            
            for i, range_info in enumerate(self.resistance_color_ranges):
                # Get the color for the middle of this range
                mid_val = (range_info['min'] + range_info['max']) / 2
                color = self.get_color_for_value(mid_val, res_norm, res_cmap)
                
                # Create a compact label
                label = f"Res: {range_info['label']} ({range_info['count']})"
                
                # Create a patch for the legend
                self.legend_elements.append(mpatches.Patch(color=color, label=label))
        
        # Add legend with all elements
        legend = self.legend_ax.legend(handles=self.legend_elements, 
                                     fontsize='x-small',  # Smaller font size
                                     title_fontsize='small',  # Smaller title font size
                                     loc='center')
        
        # Add some information text - more compact with smaller font
        stats_text = "Component Statistics:\n"
        
        if self.data_df is not None and self.show_capacitors_var.get():
            filtered_count = len(self.data_df[(self.data_df['Value'] >= self.min_cap_var.get()) & 
                                           (self.data_df['Value'] <= self.max_cap_var.get())])
            total_count = len(self.data_df)
            cap_unit = self.data_df['Unit'].iloc[0] if 'Unit' in self.data_df.columns else 'unknown unit'
            
            stats_text += (
                f"Capacitors: {filtered_count}/{total_count}\n"
                f"Filter: {self.min_cap_var.get():.2e} - {self.max_cap_var.get():.2e} {cap_unit}\n"
                f"Range: {self.data_df['Value'].min():.2e} - {self.data_df['Value'].max():.2e} {cap_unit}\n"
            )
        
        if self.resistor_df is not None and self.show_resistors_var.get():
            filtered_res_count = len(self.resistor_df[(self.resistor_df['Value'] >= self.min_res_var.get()) & 
                                                   (self.resistor_df['Value'] <= self.max_res_var.get())])
            total_res_count = len(self.resistor_df)
            res_unit = self.resistor_df['Unit'].iloc[0] if 'Unit' in self.resistor_df.columns else 'unknown unit'
            
            stats_text += (
                f"Resistors: {filtered_res_count}/{total_res_count}\n"
                f"Filter: {self.min_res_var.get():.2e} - {self.max_res_var.get():.2e} {res_unit}\n"
                f"Range: {self.resistor_df['Value'].min():.2e} - {self.resistor_df['Value'].max():.2e} {res_unit}\n"
            )

        # Add Z levels information if planes are shown
        if self.show_z_planes_var.get() and hasattr(self, 'z_levels_count') and self.z_levels_count > 0:
            stats_text += f"\nZ Levels: {self.z_levels_count}\n"
            if len(self.z_levels) <= 10:  # Only show all values if there aren't too many
                stats_text += f"Values: {', '.join([f'{z:.4f}' for z in sorted(self.z_levels)])}"
            else:
                stats_text += f"Range: {self.z_levels.min():.4f} to {self.z_levels.max():.4f}"
        
        # Add proximity data information if available
        if cap_proximity_data:
            # Sort proximity data by distance
            cap_proximity_data.sort(key=lambda x: x['min_distance'])
            # Add top 3 close capacitor edges to info text
            stats_text += "\n\nClosest Capacitor Edges:"
            for i, prox in enumerate(cap_proximity_data[:3]):
                stats_text += f"\n{prox['capacitor1']} & {prox['capacitor2']}: {prox['min_distance']:.2e}"
        
        if res_proximity_data:
            # Sort proximity data by distance
            res_proximity_data.sort(key=lambda x: x['min_distance'])
            # Add top 3 close resistor edges to info text
            stats_text += "\n\nClosest Resistor Edges:"
            for i, prox in enumerate(res_proximity_data[:3]):
                stats_text += f"\n{prox['capacitor1']} & {prox['capacitor2']}: {prox['min_distance']:.2e}"
        
        # Place stats text in the bottom left
        self.fig.text(0.02, 0.02, stats_text, ha='left', fontsize='x-small')
        
        # Add buttons for advanced interactions
        button_width = 0.12
        button_height = 0.03
        button_left = 0.82
        button_spacing = 0.01
        button_bottom = 0.32  # Above the legend
        
        # Position buttons
        btn_toggle_nodes = plt.axes([button_left, button_bottom, button_width, button_height])
        toggle_nodes_button = Button(btn_toggle_nodes, 
                                   'Hide Nodes' if self.show_nodes_var.get() else 'Show Nodes',
                                   color='lightgoldenrodyellow')
        
        btn_toggle_values = plt.axes([button_left, button_bottom - (button_height + button_spacing), button_width, button_height])
        toggle_values_button = Button(btn_toggle_values, 
                                    'Hide Values' if self.show_values_var.get() else 'Show Values', 
                                    color='lightgoldenrodyellow')
        
        btn_toggle_components = plt.axes([button_left, button_bottom - 2 * (button_height + button_spacing), button_width, button_height])
        toggle_components_button = Button(btn_toggle_components, 
                                        'Toggle Components', 
                                        color='lightgoldenrodyellow')
        
        btn_save = plt.axes([button_left, button_bottom - 3 * (button_height + button_spacing), button_width, button_height])
        save_button = Button(btn_save, 'Save Figure', color='lightgoldenrodyellow')
        
        # Function to toggle nodes
        def toggle_nodes(event):
            self.show_nodes_var.set(not self.show_nodes_var.get())
            self.visualize_advanced()
        toggle_nodes_button.on_clicked(toggle_nodes)
        
        # Function to toggle values
        def toggle_values(event):
            self.show_values_var.set(not self.show_values_var.get())
            self.visualize_advanced()
        toggle_values_button.on_clicked(toggle_values)
        
        # Function to toggle between showing capacitors, resistors, or both
        def toggle_components(event):
            # Cycle through options:
            # 1. Show both
            # 2. Show only capacitors
            # 3. Show only resistors
            if self.show_capacitors_var.get() and self.show_resistors_var.get():
                # Currently showing both, switch to only capacitors
                self.show_capacitors_var.set(True)
                self.show_resistors_var.set(False)
            elif self.show_capacitors_var.get():
                # Currently showing only capacitors, switch to only resistors
                self.show_capacitors_var.set(False)
                self.show_resistors_var.set(True)
            else:
                # Currently showing only resistors or none, switch to both
                self.show_capacitors_var.set(True)
                self.show_resistors_var.set(True)
            
            self.visualize_advanced()
        toggle_components_button.on_clicked(toggle_components)
        
        # Function to save the figure
        def save_figure(event):
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), "visualizations")
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename based on input files
            base_filename = ""
            if cap_filename:
                base_filename += os.path.splitext(cap_filename)[0]
            if res_filename:
                if base_filename:
                    base_filename += "_with_"
                base_filename += os.path.splitext(res_filename)[0]
                
            if not base_filename:
                base_filename = "component_visualization"
                
            file_path = os.path.join(output_dir, f"{base_filename}.png")
            
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            self.status_var.set(f"Figure saved as {file_path}")
            messagebox.showinfo("Save Successful", f"Visualization saved to:\n{file_path}")
            
        save_button.on_clicked(save_figure)
        
        # Maximize the visualization area
        plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.15)
        self.canvas.draw()
        
        # Update status bar
        comp_count_text = []
        if self.data_df is not None and self.show_capacitors_var.get():
            filtered_count = len(self.data_df[(self.data_df['Value'] >= self.min_cap_var.get()) & 
                                           (self.data_df['Value'] <= self.max_cap_var.get())])
            comp_count_text.append(f"{filtered_count} capacitors")
        if self.resistor_df is not None and self.show_resistors_var.get():
            filtered_res_count = len(self.resistor_df[(self.resistor_df['Value'] >= self.min_res_var.get()) & 
                                                   (self.resistor_df['Value'] <= self.max_res_var.get())])
            comp_count_text.append(f"{filtered_res_count} resistors")
            
        self.status_var.set(f"Advanced visualization created with {' and '.join(comp_count_text)}")

    def _configure_canvas(self, event=None):
        """Configure the canvas scrolling region when the window is resized."""
        # Update the scrollregion to include all of the control frame
        self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))
        
        # Get the width of the canvas (minus the scrollbar width)
        canvas_width = self.control_canvas.winfo_width()
        if canvas_width > 0:  # Only update if we have a valid width
            # Configure the control frame to expand to the width of the canvas
            self.control_canvas.itemconfig(self.control_canvas_frame, width=canvas_width)
            
        # Make sure all children of the control frame are visible
        control_frame_height = self.control_frame.winfo_reqheight()
        canvas_height = self.control_canvas.winfo_height()
        
        # If the control frame content is taller than the canvas view
        if control_frame_height > canvas_height:
            # Enable the scrollbar if not already visible
            if not self.control_scrollbar.winfo_viewable():
                self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)
        else:
            # Disable the scrollbar if not needed
            if self.control_scrollbar.winfo_viewable():
                self.control_scrollbar.pack_forget()
                self.control_canvas.configure(yscrollcommand=None)
    
    def _configure_control_frame(self, event):
        """Update the scrollregion when the control frame changes size."""
        self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))
        
    def _configure_control_canvas(self, event):
        """Resize the control frame when the canvas is resized."""
        # Update the width of the control frame to fill the canvas
        canvas_width = event.width
        self.control_canvas.itemconfig(self.control_canvas_frame, width=canvas_width)
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        # Determine the scroll direction and amount based on platform
        if event.num == 4 or event.delta > 0:  # Scroll up
            self.control_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.control_canvas.yview_scroll(1, "units")
    
    def configure_styles(self):
        """Configure the ttk styles for the application"""
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TFrame", padding=10)

def main():
    """Main function to start the application."""
    root = tk.Tk()
    app = CapacitorVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 