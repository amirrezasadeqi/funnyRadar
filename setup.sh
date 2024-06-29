#!/bin/bash

# Function to print a message and exit
function error_exit {
    echo "$1" 1>&2
    exit 1
}

# Check for Python 3.8.x (ignore minor version differences)
PYTHON_VERSION=$(python3 --version 2>&1)
if [[ ! $PYTHON_VERSION =~ "Python 3.8" ]]; then
    error_exit "Python 3.8.x is required. Please install Python 3.8.x."
fi

# Check if the virtual environment directory exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating a new one..."
    python3 -m venv venv || error_exit "Failed to create virtual environment."
fi

# Activate the virtual environment
source venv/bin/activate || error_exit "Failed to activate virtual environment."

# Check if dependencies need to be installed
if ! cmp -s <(pip freeze) requirements.txt; then
    echo "Installing dependencies..."
    pip install -r requirements.txt || error_exit "Failed to install dependencies."
fi

# Run the main script
#echo "Running project..."
#python main_script.py || error_exit "Failed to run the main script."

# Deactivate the virtual environment
deactivate

echo "Activate the virtual environment before running the scripts! Use below command for activation:"
echo "source venv/bin/activate"
echo ""

# Pause to allow user to see the output (for convenience)
read -p "Press [Enter] key to exit..."
