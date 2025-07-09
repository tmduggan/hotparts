#!/bin/bash

# Excess Auto Processor Startup Script
# This script starts the excess auto processor in the background

echo "Starting Excess Auto Processor..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required directories exist
if [ ! -d "unprocessed_XS" ]; then
    echo "Creating unprocessed_XS directory..."
    mkdir -p unprocessed_XS
fi

if [ ! -d "processed_XS" ]; then
    echo "Creating processed_XS directory..."
    mkdir -p processed_XS
fi

# Check if master hot parts data exists
if [ ! -f "Master_Hot_Parts_Data.xlsx" ]; then
    echo "Warning: Master_Hot_Parts_Data.xlsx not found"
    echo "The excess processor requires master hot parts data to function"
    echo "Please ensure Master_Hot_Parts_Data.xlsx exists in the current directory"
fi

# Start the excess auto processor
echo "Starting excess auto processor in background..."
echo "Monitoring: unprocessed_XS/"
echo "Processed files: processed_XS/"
echo "Output: Master_Matches_Data.xlsx"
echo ""
echo "Drop excess files (Kelly Chen, Vicky Zhang) into unprocessed_XS/ directory"
echo "Press Ctrl+C to stop the processor"
echo ""

# Run the processor
python3 excess_auto_processor.py --unprocessed unprocessed_XS --processed processed_XS --output . 