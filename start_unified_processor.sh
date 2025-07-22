#!/bin/bash

# Unified Auto Processor Startup Script
# Handles both hot parts and excess files in unified directories

echo "=========================================="
echo "Unified Auto Processor for Hot Parts"
echo "=========================================="
echo ""
echo "This processor handles both hot parts and excess files:"
echo "  - Hot Parts: Files containing 'Weekly Hot Parts' in filename"
echo "  - Excess: Files NOT containing 'Weekly Hot Parts' in filename"
echo ""
echo "Directories:"
echo "  - Drop files: unprocessed/"
echo "  - Processed files: processed/"
echo "  - Failed files: stay in unprocessed/ with .error files"
echo ""
echo "Starting unified processor..."
echo "Press Ctrl+C to stop"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "unified_auto_processor.py" ]; then
    echo "Error: unified_auto_processor.py not found"
    exit 1
fi

# Create directories if they don't exist
mkdir -p unprocessed
mkdir -p processed

echo "Directories created/verified"
echo ""

# Start the unified processor
python3 unified_auto_processor.py 