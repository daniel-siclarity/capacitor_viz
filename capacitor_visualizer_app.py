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

# Import visualization functionality
try:
    import visualize_capacitors as basic_vis
    import visualize_capacitors_advanced as advanced_vis
    IMPORTED_MODULES = True
except ImportError:
    IMPORTED_MODULES = False

class CapacitorVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Capacitor Visualizer")
        self.root.geometry("1400x900")  # Larger default size
        self.root.minsize(1000, 700)  # Larger minimum size
        
        # Set up styles
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TFrame", padding=10)
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a splitter for control panel and visualization
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for controls (on the left)
        self.control_frame = ttk.Frame(self.paned_window, width=350)
        
        # Create the visualization frame (on the right)
        self.viz_container = ttk.Frame(self.paned_window)
        self.viz_frame = ttk.LabelFrame(self.viz_container, text="Visualization")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add frames to the paned window
        self.paned_window.add(self.control_frame, weight=1)
        self.paned_window.add(self.viz_container, weight=4)
        
        # Create the title
        title_label = ttk.Label(self.control_frame, text="Capacitor Visualization Tool", 
                               font=("Arial", 14, "bold"))  # Smaller title font
        title_label.pack(pady=(0, 10))
        
        # Create the data selection frame
        self.data_frame = ttk.LabelFrame(self.control_frame, text="Data Selection")
        self.data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Data file selection
        file_frame = ttk.Frame(self.data_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_label = ttk.Label(file_frame, text="Capacitor Data File:")
        file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=25)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_button.pack(side=tk.LEFT)
        
        # Create example data button
        create_example_button = ttk.Button(file_frame, text="Create Example Data", 
                                         command=self.create_example_data)
        create_example_button.pack(side=tk.LEFT, padx=(10, 0))
        
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
        self.ax = None
        self.line_objects = []
        self.colors = {}
        self.legend_elements = []
        self.color_ranges = []
        self.bin_edges = []
        self.legend_ax = None
        
        # Store capacitance range
        self.capacitance_min = 0.0
        self.capacitance_max = 1.0
        
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
                            'capacitor1': row1['Capacitor_Name'],
                            'capacitor2': row2['Capacitor_Name'],
                            'min_distance': min_distance
                        })
            
            return proximity
        
        # Assign functions to the global scope
        self.calculate_distance = calculate_distance
        self.find_closest_edges = find_closest_edges

    def browse_file(self):
        """Open a file dialog to select the capacitor data file."""
        file_path = filedialog.askopenfilename(
            title="Select Capacitor Data File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_data(file_path)

    def create_example_data(self):
        """Create an example data file for testing."""
        # Create a sample data directory
        sample_dir = os.path.join(os.path.expanduser("~"), "capacitor_visualizer_samples")
        os.makedirs(sample_dir, exist_ok=True)
        
        file_path = os.path.join(sample_dir, "sample_capacitor_data.csv")
        
        # Create a sample CSV file with node coordinates and a range of values
        sample_data = """Capacitor_Name,Start_X,Start_Y,Start_Z,End_X,End_Y,End_Z,Value,Unit
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
        
        with open(file_path, "w") as f:
            f.write(sample_data)
        
        self.file_path_var.set(file_path)
        messagebox.showinfo(
            "Example Data Created", 
            f"Sample data file created at:\n{file_path}"
        )
        
        self.load_data(file_path)

    def load_data(self, file_path):
        """Load and validate the data file."""
        try:
            self.data_df = pd.read_csv(file_path)
            self.status_var.set(f"Loaded data from {os.path.basename(file_path)}: {len(self.data_df)} records")
            
            # Validate required columns
            required_columns = ['Capacitor_Name', 'Start_X', 'Start_Y', 'Start_Z', 
                              'End_X', 'End_Y', 'End_Z', 'Value']
            
            missing_columns = [col for col in required_columns if col not in self.data_df.columns]
            
            if missing_columns:
                error_msg = f"Missing columns in the data file: {', '.join(missing_columns)}"
                self.status_var.set(error_msg)
                messagebox.showerror("Data Error", error_msg)
                self.data_df = None
            else:
                # Update capacitance range sliders
                self.capacitance_min = self.data_df['Value'].min()
                self.capacitance_max = self.data_df['Value'].max()
                
                # Configure sliders
                self.min_cap_var.set(self.capacitance_min)
                self.max_cap_var.set(self.capacitance_max)
                
                self.min_cap_scale.configure(from_=self.capacitance_min, to=self.capacitance_max)
                self.max_cap_scale.configure(from_=self.capacitance_min, to=self.capacitance_max)
                
                # Update entry fields
                self.min_cap_entry_var.set(f"{self.capacitance_min:.2e}")
                self.max_cap_entry_var.set(f"{self.capacitance_max:.2e}")
            
        except Exception as e:
            self.status_var.set(f"Error loading data: {str(e)}")
            messagebox.showerror("Data Loading Error", str(e))
            self.data_df = None

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
        """Basic visualization of capacitors as edges between nodes with color based on capacitance."""
        if self.data_df is None:
            messagebox.showwarning("No Data", "Please load a data file first.")
            return
            
        # Clear previous plot
        self.fig.clear()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Reset collections and colors
        self.line_objects = []
        self.legend_elements = []
        
        df = self.data_df
        
        # Apply capacitance filters
        min_cap = self.min_cap_var.get()
        max_cap = self.max_cap_var.get()
        filtered_df = df[(df['Value'] >= min_cap) & (df['Value'] <= max_cap)]
        
        if len(filtered_df) == 0:
            messagebox.showwarning("No Data", "No capacitors match the current filter range.")
            return
            
        # Analyze capacitance distribution and create color ranges
        self.color_ranges, self.bin_edges = self.analyze_capacitance_distribution(df)
        
        # Set plot limits based on data range
        x_min, x_max = df[['Start_X', 'End_X']].values.min(), df[['Start_X', 'End_X']].values.max()
        y_min, y_max = df[['Start_Y', 'End_Y']].values.min(), df[['Start_Y', 'End_Y']].values.max()
        z_min, z_max = df[['Start_Z', 'End_Z']].values.min(), df[['Start_Z', 'End_Z']].values.max()
        
        # Add some padding to the limits
        padding = 0.05
        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = z_max - z_min
        
        self.ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
        self.ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
        self.ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
        
        # Create a colormap for the capacitance values
        cmap = plt.get_cmap(self.color_scheme_var.get())
        norm = BoundaryNorm(self.bin_edges, cmap.N)
        
        # Plot each capacitor as an edge between start and end nodes
        for _, row in filtered_df.iterrows():
            capacitor_name = row['Capacitor_Name']
            start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
            end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
            
            # Get color based on capacitance value
            value = row['Value']
            color = self.get_color_for_value(value, norm, cmap)
            
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
        
        # Create a color legend for the ranges - more compact
        unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
        legend_title = f"Capacitance Ranges ({unit})"
        
        for i, range_info in enumerate(self.color_ranges):
            # Get the color for the middle of this range
            mid_val = (range_info['min'] + range_info['max']) / 2
            color = self.get_color_for_value(mid_val, norm, cmap)
            
            # Create a compact label
            label = f"{range_info['label']} ({range_info['count']})"
            
            # Create a patch for the legend
            self.legend_elements.append(mpatches.Patch(color=color, label=label))
        
        # Set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Get filename for title
        filename = os.path.basename(self.file_path_var.get())
        self.ax.set_title(f'Capacitor Edge Visualization: {filename}', fontsize=10)  # Smaller title
        
        # Create dedicated legend axes on the bottom right corner
        self.legend_ax = self.fig.add_axes([0.70, 0.05, 0.25, 0.20])  # Smaller height
        self.legend_ax.axis('off')  # Hide axes
        legend = self.legend_ax.legend(handles=self.legend_elements, 
                                    title=legend_title, 
                                    fontsize='x-small',  # Smaller font for legend items
                                    title_fontsize='small',  # Smaller font for legend title
                                    loc='center')
        
        # Add some information text with smaller font
        filtered_count = len(filtered_df)
        total_count = len(df)
        stats_text = (
            f"Showing: {filtered_count}/{total_count} capacitors\n"
            f"Filter: {min_cap:.2e} - {max_cap:.2e} {unit}\n"
            f"Range: {df['Value'].min():.2e} - {df['Value'].max():.2e} {unit}\n"
            f"Mean: {df['Value'].mean():.2e} {unit}"
        )
        self.fig.text(0.02, 0.02, stats_text, ha='left', fontsize='x-small')
        
        # Maximize the visualization area
        plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.15)
        self.canvas.draw()
        
        self.status_var.set(f"Basic visualization created with {filtered_count} of {total_count} capacitors")

    def visualize_advanced(self):
        """Advanced visualization with interactive features and color based on capacitance values."""
        if self.data_df is None:
            messagebox.showwarning("No Data", "Please load a data file first.")
            return
            
        # Clear previous plot
        self.fig.clear()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Reset collections and colors
        self.line_objects = []
        self.legend_elements = []
        
        df = self.data_df
        
        # Apply capacitance filters
        min_cap = self.min_cap_var.get()
        max_cap = self.max_cap_var.get()
        filtered_df = df[(df['Value'] >= min_cap) & (df['Value'] <= max_cap)]
        
        if len(filtered_df) == 0:
            messagebox.showwarning("No Data", "No capacitors match the current filter range.")
            return
        
        # Analyze capacitance distribution and create color ranges
        self.color_ranges, self.bin_edges = self.analyze_capacitance_distribution(df)
        
        # Set plot limits based on data range
        x_min, x_max = df[['Start_X', 'End_X']].values.min(), df[['Start_X', 'End_X']].values.max()
        y_min, y_max = df[['Start_Y', 'End_Y']].values.min(), df[['Start_Y', 'End_Y']].values.max()
        z_min, z_max = df[['Start_Z', 'End_Z']].values.min(), df[['Start_Z', 'End_Z']].values.max()
        
        # Add some padding to the limits
        padding = 0.05
        x_range = max(x_max - x_min, 1e-6)  # Avoid division by zero
        y_range = max(y_max - y_min, 1e-6)
        z_range = max(z_max - z_min, 1e-6)
        
        self.ax.set_xlim(x_min - padding * x_range, x_max + padding * x_range)
        self.ax.set_ylim(y_min - padding * y_range, y_max + padding * y_range)
        self.ax.set_zlim(z_min - padding * z_range, z_max + padding * z_range)
        
        # Set labels
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Get the filename without path for the title
        filename = os.path.basename(self.file_path_var.get())
        self.ax.set_title(f'Capacitor Edge Visualization: {filename}', fontsize=10)  # Smaller title
        
        # Create a colormap for the capacitance values
        cmap = plt.get_cmap(self.color_scheme_var.get())
        norm = BoundaryNorm(self.bin_edges, cmap.N)
        
        # Find closest edges for analysis
        proximity_data = self.find_closest_edges(filtered_df)
        
        # Create legend axes on the bottom right corner
        self.legend_ax = self.fig.add_axes([0.70, 0.05, 0.25, 0.20])  # Smaller height
        self.legend_ax.axis('off')  # Hide axes
        
        # Add unit information
        unit = df['Unit'].iloc[0] if 'Unit' in df.columns else 'unknown unit'
        legend_title = f"Capacitance Ranges ({unit})"
        
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
        
        # Plot each capacitor as an edge between nodes
        for _, row in filtered_df.iterrows():
            capacitor_name = row['Capacitor_Name']
            start_x, start_y, start_z = row['Start_X'], row['Start_Y'], row['Start_Z']
            end_x, end_y, end_z = row['End_X'], row['End_Y'], row['End_Z']
            
            # Get color based on capacitance value
            value = row['Value']
            color = self.get_color_for_value(value, norm, cmap)
            
            # Plot the edge as a line
            if self.show_nodes_var.get():
                line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                 color=color, linewidth=self.line_width_var.get(), 
                                 marker='o', markersize=self.marker_size_var.get())
            else:
                line, = self.ax.plot([start_x, end_x], [start_y, end_y], [start_z, end_z], 
                                 color=color, linewidth=self.line_width_var.get())
            
            self.line_objects.append(line)
            
            # Add capacitance values as text if enabled
            if self.show_values_var.get():
                # Calculate midpoint of the edge
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                mid_z = (start_z + end_z) / 2
                
                # Add text with capacitance value
                self.ax.text(mid_x, mid_y, mid_z, f"{row['Value']:.3e}", 
                         color='black', fontsize=7, ha='center', va='center')
        
        # Create a color legend for the ranges - more compact
        for i, range_info in enumerate(self.color_ranges):
            # Get the color for the middle of this range
            mid_val = (range_info['min'] + range_info['max']) / 2
            color = self.get_color_for_value(mid_val, norm, cmap)
            
            # Create a compact label
            label = f"{range_info['label']} ({range_info['count']})"
            
            # Create a patch for the legend
            self.legend_elements.append(mpatches.Patch(color=color, label=label))
        
        # Add legend with capacitance ranges
        legend = self.legend_ax.legend(handles=self.legend_elements, 
                                    title=legend_title, 
                                    fontsize='x-small',  # Smaller font size
                                    title_fontsize='small',  # Smaller title font size
                                    loc='center')
        
        # Add some information text - more compact with smaller font
        filtered_count = len(filtered_df)
        total_count = len(df)
        stats_text = (
            f"Showing: {filtered_count}/{total_count} capacitors\n"
            f"Filter: {min_cap:.2e} - {max_cap:.2e} {unit}\n"
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
        self.fig.text(0.02, 0.02, stats_text, ha='left', fontsize='x-small')
        
        # Maximize the visualization area
        plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.15)
        self.canvas.draw()
        
        self.status_var.set(f"Advanced visualization created with {filtered_count} of {total_count} capacitors")

    def visualize(self):
        """Visualize the data based on selected visualization type."""
        if not self.file_path_var.get():
            messagebox.showwarning("No File Selected", "Please select a data file first.")
            return
        
        # Check if data is loaded
        if self.data_df is None:
            self.load_data(self.file_path_var.get())
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

def main():
    """Main function to start the application."""
    root = tk.Tk()
    app = CapacitorVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 