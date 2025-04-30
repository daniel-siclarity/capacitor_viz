# Capacitor and Resistor Visualization Tool

This tool allows you to visualize capacitor and resistor coordinates in 3D, representing them as edges connecting start and end nodes with colors based on their values. It includes features for filtering components by value range and interactive visualization.

## Features

### Basic Visualization
- 3D representation of capacitors and resistors as edges between start and end nodes
- Color coding based on capacitance/resistance values
- Value range filtering using sliders or direct input
- Statistics display showing component counts and value distributions
- Legend showing value ranges and their corresponding colors
- Visual differentiation between capacitors (solid lines) and resistors (dashed lines)

### Advanced Visualization
- All features from the basic visualization
- Interactive toggling of node and value display
- Option to show only capacitors, only resistors, or both together
- Highlighting specific value ranges
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
2. Run the `ComponentVisualizer` executable.
3. Use the GUI to:
   - Browse for your capacitor and resistor data files
   - Create example data if needed
   - Select visualization type (Basic or Advanced)
   - Choose which components to show (capacitors, resistors, or both)
   - Adjust line width, marker size, and color scheme
   - Filter components by value range
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
   - Then, select CSV data files to visualize (capacitors and/or resistors)
   - Finally, choose either basic or advanced visualization

The script automatically detects available cells, layouts, and data files, making it easy to navigate through your data.

### Option 4: Run Python scripts directly

For basic visualization with specific data files:
```bash
python3 visualize_capacitors.py /path/to/your/capacitor_data.csv [/path/to/your/resistor_data.csv]
```

For advanced visualization with specific data files:
```bash
python3 visualize_capacitors_advanced.py /path/to/your/capacitor_data.csv [/path/to/your/resistor_data.csv]
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

The tool expects CSV files with the following columns:

### For Capacitors:
- `Capacitor_Name`: Name/identifier of the capacitor
- `Start_X`, `Start_Y`, `Start_Z`: Starting coordinates of the capacitor (node 1)
- `End_X`, `End_Y`, `End_Z`: Ending coordinates of the capacitor (node 2)
- `Value`: Capacitance value
- `Unit`: Unit of capacitance (e.g., fF)

### For Resistors:
- `Resistor_Name`: Name/identifier of the resistor
- `Start_X`, `Start_Y`, `Start_Z`: Starting coordinates of the resistor (node 1)
- `End_X`, `End_Y`, `End_Z`: Ending coordinates of the resistor (node 2)
- `Value`: Resistance value
- `Unit`: Unit of resistance (e.g., Ohm)

## Directory Structure (for Command-line Usage)

For the command-line interface, the tool expects data to be organized in the following structure:
```
coor_data/
├── CellName1/
│   ├── Layout1/
│   │   ├── Layout1_capacitor_coordinates.csv
│   │   ├── Layout1_resistor_coordinates.csv
│   │   └── ...
│   ├── Layout2/
│   │   └── ...
│   └── ...
├── CellName2/
│   └── ...
└── ...
```

## Controls in the GUI

- Use the "Browse" buttons to select your data files (capacitors and resistors)
- Use the "Create Example Data" button to generate sample data files
- Select which components to show (capacitors, resistors, or both)
- Select "Basic" or "Advanced" visualization type
- Choose color scheme and number of color ranges
- Adjust line width and marker size using the sliders
- Filter components by value using sliders or input boxes
- Toggle node markers and value display
- Use logarithmic scale for large value ranges
- Click "Visualize" to create the visualization
- Use mouse to rotate the 3D view
- Use scroll wheel to zoom in/out
- Click "Save Visualization" to export the image

## Value Filtering

The tool provides two ways to filter components by their values:

1. **Sliders**: Drag the min and max value sliders to quickly adjust the visible range
2. **Input Boxes**: Enter exact values for precise filtering, supporting scientific notation

The filtering is applied in real-time, updating the visualization to show only components within the selected range.

## Visual Differentiation

To help distinguish between capacitors and resistors:

- Capacitors are shown as solid lines with circular markers
- Resistors are shown as dashed lines with square markers
- Different color scales are used for capacitors and resistors
- The legend includes identifying labels for each component type
