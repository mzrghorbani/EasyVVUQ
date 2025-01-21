#!/bin/bash

# Script to install EasyVVUQ in a virtual environment and test the installation

# Exit on any error
set -e

# Get the directory of the script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Define variables
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="requirements.txt"
PACKAGE_NAME="easyvvuq"

echo "Starting EasyVVUQ installation and testing..."

# Step 1: Navigate to the script's directory (ensures relative paths work)
cd "$SCRIPT_DIR"

# Step 2: Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv $VENV_DIR

# Step 3: Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Step 4: Ensure we're in the EasyVVUQ directory
if [ -f "$SCRIPT_DIR/$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "Error: $REQUIREMENTS_FILE not found in $SCRIPT_DIR!"
    exit 1
fi

# Step 5: Test the installation
echo "Testing EasyVVUQ installation..."
python -c "import $PACKAGE_NAME; print('$PACKAGE_NAME version:', $PACKAGE_NAME.__version__)"

echo You can now run the tests using 'pytest tests/' if you wish."
