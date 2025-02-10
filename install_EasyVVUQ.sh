#!/bin/bash

# Exit on any error
set -e

echo "Starting EasyVVUQ installation..."

# Step 1: Define the directory for the virtual environment
VENV_DIR="./venv"
REQUIREMENTS_FILE="requirements.txt"

# Step 2: Create a virtual environment in the EasyVVUQ directory
echo "Creating a virtual environment in the EasyVVUQ directory..."
python3 -m venv $VENV_DIR

# Step 3: Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Step 4: Install dependencies from requirements.txt
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "Error: $REQUIREMENTS_FILE not found in the EasyVVUQ directory!"
    exit 1
fi

# Step 5: Test the EasyVVUQ installation
echo "Testing EasyVVUQ installation..."
python -c "import easyvvuq; print('EasyVVUQ version:', easyvvuq.__version__)"

echo "EasyVVUQ installation and testing completed successfully!"
