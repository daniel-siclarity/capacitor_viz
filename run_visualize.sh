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

# Function to display a numbered menu and get selection
function display_menu() {
    local options=("$@")
    local selection

    if [ ${#options[@]} -eq 0 ]; then
        echo "No options available."
        return 1
    fi

    echo "Available options:"
    for i in "${!options[@]}"; do
        echo "$((i+1)). ${options[$i]}"
    done
    echo

    while true; do
        read -p "Enter selection (1-${#options[@]}): " selection
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#options[@]}" ]; then
            return $selection
        else
            echo "Invalid selection. Please try again."
        fi
    done
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

# Step 1: Get list of cell folders
echo "Step 1: Select a cell folder"
cell_folders=($(ls -d "$BASE_DIR"/*/ 2>/dev/null | xargs -n 1 basename 2>/dev/null))

# Add option to create a new cell folder or use a sample
cell_folders+=("Create a new cell folder")
cell_folders+=("Use sample data")

# Display cell folders menu
display_menu "${cell_folders[@]}"
cell_index=$?
selected_cell="${cell_folders[$((cell_index-1))]}"

# Handle special options
if [ "$selected_cell" == "Create a new cell folder" ]; then
    read -p "Enter name for new cell folder: " new_cell_name
    mkdir -p "$BASE_DIR/$new_cell_name"
    selected_cell="$new_cell_name"
    echo "Created new cell folder: $selected_cell"
elif [ "$selected_cell" == "Use sample data" ]; then
    selected_cell="SampleCell"
    mkdir -p "$BASE_DIR/$selected_cell/SampleLayout"
    create_sample_data "$BASE_DIR/$selected_cell/SampleLayout" "sample_capacitor_coordinates.csv"
fi

echo "Selected cell: $selected_cell"
echo

# Step 2: Get list of layout folders for the selected cell
echo "Step 2: Select a layout folder"
CELL_DIR="$BASE_DIR/$selected_cell"
layout_folders=($(ls -d "$CELL_DIR"/*/ 2>/dev/null | xargs -n 1 basename 2>/dev/null))

# Add option to create a new layout folder
layout_folders+=("Create a new layout folder")

# Display layout folders menu or create one if none exists
if [ ${#layout_folders[@]} -eq 1 ] && [ "${layout_folders[0]}" == "Create a new layout folder" ]; then
    echo "No layout folders found in $CELL_DIR."
    read -p "Enter name for new layout folder: " new_layout_name
    mkdir -p "$CELL_DIR/$new_layout_name"
    selected_layout="$new_layout_name"
    echo "Created new layout folder: $selected_layout"
else
    display_menu "${layout_folders[@]}"
    layout_index=$?
    selected_layout="${layout_folders[$((layout_index-1))]}"
    
    # Handle create new layout option
    if [ "$selected_layout" == "Create a new layout folder" ]; then
        read -p "Enter name for new layout folder: " new_layout_name
        mkdir -p "$CELL_DIR/$new_layout_name"
        selected_layout="$new_layout_name"
        echo "Created new layout folder: $selected_layout"
    fi
fi

echo "Selected layout: $selected_layout"
echo

# Step 3: Look for capacitor coordinate files in the selected layout folder
echo "Step 3: Select a data file"
LAYOUT_DIR="$CELL_DIR/$selected_layout"

# Try various patterns to find capacitor data files
data_files=($(find "$LAYOUT_DIR" -name "*capacitor*coordinates*.csv" -o -name "*_capacitor_*.csv" -o -name "*capacitance*.csv" 2>/dev/null | xargs -n 1 basename 2>/dev/null))

if [ ${#data_files[@]} -eq 0 ]; then
    echo "No capacitor coordinate files found in $LAYOUT_DIR."
    
    # If no specific capacitor files found, look for any CSV files
    data_files=($(find "$LAYOUT_DIR" -name "*.csv" 2>/dev/null | xargs -n 1 basename 2>/dev/null))
    
    if [ ${#data_files[@]} -eq 0 ]; then
        echo "No CSV files found in $LAYOUT_DIR."
        
        # Add option to create a sample data file
        read -p "Would you like to create a sample data file for testing? (y/n): " create_sample
        if [[ "$create_sample" =~ ^[Yy] ]]; then
            create_sample_data "$LAYOUT_DIR" "sample_capacitor_coordinates.csv"
            data_files=("sample_capacitor_coordinates.csv")
        else
            echo "Please add data files and try again."
            exit 1
        fi
    else
        echo "Found general CSV files instead:"
    fi
fi

# Add option to use a different file
data_files+=("Specify a different file")

# Display data files menu
display_menu "${data_files[@]}"
file_index=$?
selected_file="${data_files[$((file_index-1))]}"

# Handle specify different file option
if [ "$selected_file" == "Specify a different file" ]; then
    read -p "Enter full path to CSV file: " custom_file_path
    if [ -f "$custom_file_path" ]; then
        DATA_FILE="$custom_file_path"
    else
        echo "File not found: $custom_file_path"
        exit 1
    fi
else
    # Full path to the selected data file
    DATA_FILE="$LAYOUT_DIR/$selected_file"
fi

echo "Selected file: $DATA_FILE"
echo

# Step 4: Select visualization type
echo "Step 4: Select visualization type"
echo "1. Basic Edge Visualization (edges colored by capacitance value)"
echo "2. Advanced Edge Visualization (with interactive features and capacitance coloring)"
echo "3. Exit"
echo

# Get user choice for visualization type
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Running basic edge visualization for $DATA_FILE..."
        echo "Colors represent capacitance values - see legend for ranges"
        python3 visualize_capacitors.py "$DATA_FILE"
        ;;
    2)
        echo "Running advanced edge visualization for $DATA_FILE..."
        echo "Colors represent capacitance values - see legend for ranges"
        python3 visualize_capacitors_advanced.py "$DATA_FILE"
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again and select 1-3."
        exit 1
        ;;
esac

exit 0 