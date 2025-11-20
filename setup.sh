#!/bin/bash

echo "========================================"
echo "Dependency Scanner - Setup Script"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "Python found!"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "Virtual environment created successfully!"
echo ""

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To use the scanner:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run: python scanner.py <url>"
echo ""

