# Capacitor Visualization Tool

This tool allows you to visualize capacitor coordinates in 3D, representing them as edges connecting start and end nodes with colors based on capacitance values. It includes features for filtering capacitors by capacitance range and interactive visualization.

## Features

### Basic Visualization
- 3D representation of capacitors as edges between start and end nodes
- Color coding based on capacitance values
- Capacitance range filtering using sliders or direct input
- Statistics display showing capacitor counts and capacitance distribution
- Legend showing capacitance ranges and their corresponding colors

### Advanced Visualization
- All features from the basic visualization
- Interactive toggling of node and value display
- Highlighting specific capacitance ranges
- Proximity analysis to identify closest edges
- Button to save visualization as PNG

## Prerequisites

- Python 3.x
- Required libraries: numpy, pandas, matplotlib, scipy, tkinter

## Usage Options

### Option 1: Run the GUI from source (Recommended)

```bash
python capacitor_visualizer_app.py
```

### Option 2: Standalone GUI Application 

1. Download the packaged application from the releases section.
2. Run the `CapacitorVisualizer` executable.
3. Use the GUI to:
   - Browse for your capacitor data file
   - Create example data if needed
   - Select visualization type (Basic or Advanced)
   - Adjust line width, marker size, and color scheme
   - Filter capacitors by capacitance range
   - Save the visualization as an image file

### Option 3: Run the shell script (for command-line)

1. Make the shell script executable:
   ```bash
   chmod +x run_visualize.sh
   ```

2. Run the script:
   ```bash
   ./run_visualize.sh
   ```

3. Follow the interactive prompts:
   - First, select a cell folder from the `coor_data` directory
   - Next, select a layout folder within the chosen cell
   - Then, select a CSV data file to visualize
   - Finally, choose either basic or advanced visualization

The script automatically detects available cells, layouts, and data files, making it easy to navigate through your data.

### Option 4: Run Python scripts directly

For basic visualization with a specific data file:
```bash
python3 visualize_capacitors.py /path/to/your/data_file.csv
```

For advanced visualization with a specific data file:
```bash
python3 visualize_capacitors_advanced.py /path/to/your/data_file.csv
```

## Building the Standalone Application

To package the application into a standalone executable:

1. Ensure you have PyInstaller installed:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_app.py
   ```

3. The packaged application will be created in the `dist` directory.

## Data Format

The tool expects a CSV file with the following columns:
- `Capacitor_Name`: Name/identifier of the capacitor
- `Start_X`, `Start_Y`, `Start_Z`: Starting coordinates of the capacitor (node 1)
- `End_X`, `End_Y`, `End_Z`: Ending coordinates of the capacitor (node 2)
- `Value`: Capacitance value
- `Unit`: Unit of capacitance (e.g., fF)

## Directory Structure (for Command-line Usage)

For the command-line interface, the tool expects data to be organized in the following structure:
```
coor_data/
├── CellName1/
│   ├── Layout1/
│   │   ├── Layout1_capacitor_coordinates.csv
│   │   └── ...
│   ├── Layout2/
│   │   └── ...
│   └── ...
├── CellName2/
│   └── ...
└── ...
```

## Controls in the GUI

- Use the "Browse" button to select your data file
- Use the "Create Example Data" button to generate a sample data file
- Select "Basic" or "Advanced" visualization type
- Choose color scheme and number of color ranges
- Adjust line width and marker size using the sliders
- Filter capacitors by capacitance using sliders or input boxes
- Toggle node markers and value display
- Use logarithmic scale for large capacitance ranges
- Click "Visualize" to create the visualization
- Use mouse to rotate the 3D view
- Use scroll wheel to zoom in/out
- Click "Save Visualization" to export the image

## Capacitance Filtering

The tool provides two ways to filter capacitors by their capacitance values:

1. **Sliders**: Drag the min and max capacitance sliders to quickly adjust the visible range
2. **Input Boxes**: Enter exact values for precise filtering, supporting scientific notation

The filtering is applied in real-time, updating the visualization to show only capacitors within the selected range.
