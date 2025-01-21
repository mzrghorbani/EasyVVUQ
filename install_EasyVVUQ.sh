#!/bin/bash

# Script to install EasyVVUQ in a virtual environment and test the installation

# Exit the script if any command fails
set -e

# Create a virtual environment named 'venv'
echo "Creating virtual environment 'venv'..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Navigate to the EasyVVUQ directory
echo "Navigating to the EasyVVUQ directory..."
cd EasyVVUQ

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# Test the installation
echo "Testing EasyVVUQ installation..."
python -c "import easyvvuq; print('EasyVVUQ version:', easyvvuq.__version__)"

# Success message
echo "EasyVVUQ has been installed and verified successfully! You can now run the tests using 'pytest tests/' if you wish."

