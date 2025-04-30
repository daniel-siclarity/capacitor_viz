#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required libraries are installed
echo "Checking required libraries..."
REQUIRED_PACKAGES="numpy pandas matplotlib scipy"
MISSING_PACKAGES=""

for package in $REQUIRED_PACKAGES; do
    if ! python3 -c "import $package" &> /dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES $package"
    fi
done

# Install missing packages if needed
if [ ! -z "$MISSING_PACKAGES" ]; then
    echo "Installing missing packages:$MISSING_PACKAGES"
    pip install $MISSING_PACKAGES
fi

# Base data directory
BASE_DIR="coor_data"

# Check if the base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Creating base directory: $BASE_DIR"
    mkdir -p "$BASE_DIR"
fi

# Function to display a selection menu
function show_menu() {
    local options=("$@")
    local count=${#options[@]}
    
    for ((i=0; i<count; i++)); do
        echo "$((i+1)). ${options[i]}"
    done
    
    echo "Enter your choice (1-$count):"
    read choice
    
    # Validate choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "$count" ]; then
        return $((choice-1))
    else
        echo "Invalid choice. Please try again."
        show_menu "${options[@]}"
    fi
}

# Function to create a sample data file for testing
function create_sample_data() {
    local dir="$1"
    local filename="$2"
    local full_path="$dir/$filename"
    
    echo "Creating sample capacitor data file: $full_path"
    
    # Create directory if it doesn't exist
    mkdir -p "$dir"
    
    # Create a sample CSV file with capacitor nodes data with a range of values
    cat > "$full_path" << EOL
Capacitor_Name,Start_X,Start_Y,Start_Z,End_X,End_Y,End_Z,Value,Unit
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
EOL
    
    echo "Sample data file created successfully."
    return 0
}

echo "Capacitor Edge Visualization Tool"
echo "---------------------------"
echo "Colors represent capacitance values"
echo "---------------------------"

# Get list of cell directories
CELLS=($(ls -d "$BASE_DIR"/*/ 2>/dev/null | sort))

if [ ${#CELLS[@]} -eq 0 ]; then
    echo "No cell directories found in $BASE_DIR."
    exit 1
fi

# Extract just the cell names for the menu
CELL_NAMES=()
for cell in "${CELLS[@]}"; do
    CELL_NAMES+=($(basename "$cell"))
done

echo "Select a cell:"
show_menu "${CELL_NAMES[@]}"
CELL_INDEX=$?
SELECTED_CELL="${CELLS[$CELL_INDEX]}"

echo "Selected cell: $(basename "$SELECTED_CELL")"

# Get list of layout directories within the selected cell
LAYOUTS=($(ls -d "$SELECTED_CELL"/*/ 2>/dev/null | sort))

if [ ${#LAYOUTS[@]} -eq 0 ]; then
    echo "No layout directories found in $(basename "$SELECTED_CELL")."
    exit 1
fi

# Extract just the layout names for the menu
LAYOUT_NAMES=()
for layout in "${LAYOUTS[@]}"; do
    LAYOUT_NAMES+=($(basename "$layout"))
done

echo "Select a layout:"
show_menu "${LAYOUT_NAMES[@]}"
LAYOUT_INDEX=$?
SELECTED_LAYOUT="${LAYOUTS[$LAYOUT_INDEX]}"

echo "Selected layout: $(basename "$SELECTED_LAYOUT")"

# Check for capacitor coordinates file
CAPACITOR_FILE=$(find "$SELECTED_LAYOUT" -name "*capacitor_coordinates.csv" 2>/dev/null)
RESISTOR_FILE=$(find "$SELECTED_LAYOUT" -name "*resistor_coordinates.csv" 2>/dev/null)

if [ -z "$CAPACITOR_FILE" ] && [ -z "$RESISTOR_FILE" ]; then
    echo "No component coordinate files found in $(basename "$SELECTED_LAYOUT")."
    exit 1
fi

# Set up visualization options
OPTIONS=("Basic visualization")
OPTIONS+=("Advanced visualization")

echo "Select visualization type:"
show_menu "${OPTIONS[@]}"
VIZ_INDEX=$?

# Determine which files to visualize
if [ -n "$CAPACITOR_FILE" ] && [ -n "$RESISTOR_FILE" ]; then
    echo "Found both capacitor and resistor files."
    FILES=("Capacitors only" "Resistors only" "Both components")
    
    echo "What would you like to visualize?"
    show_menu "${FILES[@]}"
    FILES_INDEX=$?
    
    if [ $FILES_INDEX -eq 0 ]; then
        RESISTOR_FILE=""
    elif [ $FILES_INDEX -eq 1 ]; then
        CAPACITOR_FILE=""
    fi
fi

# Run the appropriate visualization
echo "Starting visualization..."

if [ $VIZ_INDEX -eq 0 ]; then
    # Basic visualization
    if [ -n "$CAPACITOR_FILE" ] && [ -n "$RESISTOR_FILE" ]; then
        echo "Visualizing both capacitors and resistors (basic)..."
        python capacitor_visualizer_app.py "$CAPACITOR_FILE" "$RESISTOR_FILE"
    elif [ -n "$CAPACITOR_FILE" ]; then
        echo "Visualizing capacitors only (basic)..."
        python capacitor_visualizer_app.py "$CAPACITOR_FILE"
    else
        echo "Visualizing resistors only (basic)..."
        python capacitor_visualizer_app.py "" "$RESISTOR_FILE"
    fi
else
    # Advanced visualization
    if [ -n "$CAPACITOR_FILE" ] && [ -n "$RESISTOR_FILE" ]; then
        echo "Visualizing both capacitors and resistors (advanced)..."
        python visualize_capacitors_advanced.py "$CAPACITOR_FILE" "$RESISTOR_FILE"
    elif [ -n "$CAPACITOR_FILE" ]; then
        echo "Visualizing capacitors only (advanced)..."
        python visualize_capacitors_advanced.py "$CAPACITOR_FILE"
    else
        echo "Visualizing resistors only (advanced)..."
        python visualize_capacitors_advanced.py "" "$RESISTOR_FILE"
    fi
fi

echo "Visualization complete!"

exit 0 