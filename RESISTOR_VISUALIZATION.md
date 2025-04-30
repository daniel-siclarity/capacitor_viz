# Resistor Visualization Guide

This guide explains how to use the newly added resistor visualization feature in the Capacitor Visualization Tool.

## Overview

The tool now allows you to visualize both capacitors and resistors in the same 3D space. Resistors are displayed as dashed lines with square markers, while capacitors are displayed as solid lines with circular markers. Different color schemes are used for each component type to help distinguish between them.

## Data Format

Resistor data should be provided in a CSV file with the following columns:
- `Resistor_Name`: Name/identifier of the resistor
- `Start_X`, `Start_Y`, `Start_Z`: Starting coordinates of the resistor (node 1)
- `End_X`, `End_Y`, `End_Z`: Ending coordinates of the resistor (node 2)
- `Value`: Resistance value
- `Unit`: Unit of resistance (e.g., Ohm)

The expected file name convention is `*_resistor_coordinates.csv`, which matches the `*_capacitor_coordinates.csv` convention for capacitor data.

## Using the GUI Application

1. Launch the application:
   ```
   python capacitor_visualizer_app.py
   ```

2. In the Data Selection section:
   - Use the "Capacitor Data File" browse button to select your capacitor data
   - Use the "Resistor Data File" browse button to select your resistor data
   - If you load a capacitor file, the tool will automatically look for a matching resistor file in the same directory (and vice versa)

3. Select which components to show using the checkboxes:
   - Capacitors
   - Resistors
   - Both

4. Adjust filters for both component types:
   - Use the Capacitance Filter sliders to filter capacitors by value
   - Use the Resistance Filter sliders to filter resistors by value

5. Choose visualization options:
   - Basic or Advanced visualization
   - Show/hide nodes
   - Show/hide component values
   - Show Z-level planes

6. Click "Visualize" to generate the 3D visualization

## Advanced Visualization Features

In the Advanced visualization mode, you'll get additional controls:
- Toggle button to cycle between showing both components, only capacitors, or only resistors
- Buttons to toggle node display and value display
- Ability to highlight specific value ranges

## Command Line Usage

You can also run the visualization from the command line:

```bash
# Basic visualization with both component types
python visualize_capacitors.py path/to/capacitor_coordinates.csv path/to/resistor_coordinates.csv

# Advanced visualization with both component types
python visualize_capacitors_advanced.py path/to/capacitor_coordinates.csv path/to/resistor_coordinates.csv
```

Or use the provided shell script for interactive selection:

```bash
./run_visualize.sh
```

## Example Data

You can generate example data for both capacitors and resistors using the "Create Example Data" button in the GUI. This will create sample CSV files in your home directory under `~/capacitor_visualizer_samples/`.

## Quick Test

To quickly test the resistor visualization feature:

```bash
python test_resistor_visualization.py
```

This script will look for sample data files and display both capacitors and resistors in a simple 3D plot.

## Visual Differentiation

To help distinguish between capacitors and resistors:

- Capacitors are shown as solid lines with circular markers
- Resistors are shown as dashed lines with square markers
- Different color scales are used (viridis for capacitors, plasma for resistors)
- The legend includes separate entries for each component type 