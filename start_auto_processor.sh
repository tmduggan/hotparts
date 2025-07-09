#!/bin/bash

# Hot Parts Auto Processor Startup Script

echo "Starting Hot Parts Auto Processor..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import pandas, openpyxl, watchdog" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
fi

# Create directories if they don't exist
mkdir -p unprocessed processed

echo ""
echo "Directories created:"
echo "  - unprocessed/ (drop Excel files here)"
echo "  - processed/ (processed files go here)"
echo "  - Master files will be created in current directory"
echo ""

# Start the auto processor
echo "Starting file watcher..."
echo "Drop 'Weekly Hot Parts List' Excel files into the 'unprocessed' directory"
echo "Press Ctrl+C to stop"
echo ""

python3 auto_processor.py 