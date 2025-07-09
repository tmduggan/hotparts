# Automatic Hot Parts File Processor

A fully automated system that watches for new Excel files and processes them automatically, creating master data files in real-time.

## 🚀 Quick Start

### Option 1: Simple Startup Script
```bash
./start_auto_processor.sh
```

### Option 2: Direct Python Command
```bash
python auto_processor.py
```

### Option 3: Custom Directories
```bash
python auto_processor.py --unprocessed /path/to/unprocessed --processed /path/to/processed --output /path/to/output
```

## 📁 Directory Structure

The system creates and manages these directories:

```
HotParts/
├── unprocessed/          # Drop Excel files here
├── processed/            # Processed files are moved here
├── auto_processor.log    # Processing log file
├── Master_Hot_Parts_Data.xlsx    # Master data file
├── Master_Pivot_Data.xlsx        # Master pivot file
└── [other files...]
```

## 🔄 How It Works

1. **Drop Files**: Simply drag and drop your "Weekly Hot Parts List" Excel files into the `unprocessed/` directory
2. **Automatic Processing**: The system detects new files and processes them automatically
3. **File Movement**: Processed files are moved to the `processed/` directory
4. **Master Files**: Master data files are updated with the new data
5. **Logging**: All activities are logged to `auto_processor.log`

## 📋 Features

### ✅ Automatic File Detection
- Watches the `unprocessed/` directory for new files
- Detects both file creation and file moves (drag & drop)
- Only processes files matching "Weekly Hot Parts List" pattern

### ✅ Real-time Processing
- Files are processed immediately when detected
- Master files are updated after each successful processing
- No manual intervention required

### ✅ Error Handling
- Failed files are moved to `processed/` with `_ERROR` suffix
- Detailed error logging
- System continues running even if individual files fail

### ✅ Logging
- Comprehensive logging to both console and file
- Timestamps for all activities
- Error tracking and reporting

### ✅ File Management
- Automatic cleanup of processed files
- Prevents duplicate processing
- Handles file locks and partial writes

## 🛠️ Usage Examples

### Basic Usage
```bash
# Start the auto processor
./start_auto_processor.sh

# Drop files into unprocessed/ directory
# Watch the magic happen!
```

### Advanced Usage
```bash
# Custom directories
python auto_processor.py \
  --unprocessed /path/to/drop/zone \
  --processed /path/to/archive \
  --output /path/to/master/files

# Monitor specific directories
python auto_processor.py --unprocessed /Users/username/Desktop/hot_parts
```

### Programmatic Usage
```python
from auto_processor import AutoProcessor

# Create processor with custom settings
processor = AutoProcessor(
    unprocessed_dir="drop_zone",
    processed_dir="archive", 
    output_dir="master_files"
)

# Start monitoring
processor.start()
```

## 📊 Output Files

### Master_Hot_Parts_Data.xlsx
Contains consolidated data from all date-based tabs:
- **MPN**: Part number
- **Date**: Tab date (e.g., 2025.07.07)
- **Reqs_Count**: Requirements count
- **Manufacturer**: Part manufacturer
- **Product_Class**: Product classification
- **Description**: Part description

### Master_Pivot_Data.xlsx
Contains consolidated data from pivot tabs:
- **MPN**: Part number
- **Reqs_Count**: Requirements count
- **Date**: File date

## 🔧 Configuration

### File Patterns
The system automatically detects files containing:
- "Weekly Hot Parts List" in the filename
- `.xlsx` or `.xls` extension

### Processing Behavior
- **Wait Time**: 2 seconds after file detection (ensures complete file write)
- **Duplicate Prevention**: Tracks files being processed to avoid conflicts
- **Error Recovery**: Failed files are marked with `_ERROR` suffix

## 📝 Logging

### Log File: `auto_processor.log`
Contains detailed information about:
- File detection events
- Processing status
- Error messages
- Master file updates
- System start/stop events

### Log Levels
- **INFO**: Normal operations (file processing, updates)
- **ERROR**: Processing failures and system errors
- **WARNING**: Potential issues (file conflicts, etc.)

## 🚨 Troubleshooting

### Common Issues

**Files not being processed:**
- Check that filenames contain "Weekly Hot Parts List"
- Verify files have `.xlsx` or `.xls` extension
- Check `auto_processor.log` for error messages

**Processing errors:**
- Look for `_ERROR` files in `processed/` directory
- Check log file for specific error details
- Verify Excel file structure matches expected format

**System not starting:**
- Ensure Python 3 is installed
- Install dependencies: `pip install -r requirements.txt`
- Check file permissions on directories

### Debug Mode
For detailed debugging, modify the logging level in `auto_processor.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 🔄 Workflow Integration

### Daily Workflow
1. Start the auto processor: `./start_auto_processor.sh`
2. Drop new Excel files into `unprocessed/` directory
3. Check `processed/` directory for completed files
4. Use master files for analysis and reporting

### Batch Processing
For large batches of files:
1. Copy all files to `unprocessed/` directory
2. Start auto processor
3. Monitor progress via log file
4. Check master files for consolidated data

## 📈 Performance

### Processing Speed
- **Small files** (< 1MB): ~2-5 seconds
- **Medium files** (1-10MB): ~5-15 seconds  
- **Large files** (> 10MB): ~15-60 seconds

### Memory Usage
- Minimal memory footprint
- Processes one file at a time
- Automatic cleanup after processing

### Scalability
- Handles hundreds of files efficiently
- Processes files sequentially to avoid conflicts
- Can run continuously for days/weeks

## 🔒 Security & Reliability

### File Safety
- Original files are never modified
- Processed files are moved, not copied
- Error files preserve original content

### System Reliability
- Continues running after individual file failures
- Handles network interruptions gracefully
- Automatic recovery from temporary errors

## 🎯 Best Practices

1. **File Naming**: Use consistent naming with "Weekly Hot Parts List"
2. **Directory Structure**: Keep unprocessed and processed directories organized
3. **Monitoring**: Check log files regularly for issues
4. **Backup**: Keep backups of master files
5. **Updates**: Process files regularly to maintain current data

## 📞 Support

For issues or questions:
1. Check the log file: `auto_processor.log`
2. Review this README
3. Check file permissions and directory structure
4. Verify Excel file format matches expected structure 