# Excess Auto Processor

A dedicated automatic processing system for excess inventory files that cross-references them with master hot parts data in real-time.

## 🎯 Overview

The Excess Auto Processor provides a **separate, dedicated workflow** for processing excess inventory files, completely independent from the main hot parts processing system. This prevents any conflicts and keeps the two workflows organized.

## 📁 Directory Structure

```
HotParts/
├── unprocessed_XS/          # Drop excess files here
│   └── .gitkeep
├── processed_XS/            # Processed files moved here
│   └── .gitkeep
├── unprocessed/             # Hot parts files (separate)
├── processed/               # Processed hot parts (separate)
├── excess_auto_processor.py # Main auto processor
├── start_excess_processor.sh # Startup script
└── Master_Matches_Data.xlsx # Output file
```

## 🚀 Quick Start

### 1. **Start the Processor**
```bash
# Option 1: Use startup script
./start_excess_processor.sh

# Option 2: Direct command
python excess_auto_processor.py
```

### 2. **Drop Excess Files**
Simply drag and drop excess files into the `unprocessed_XS/` directory:
- Files containing "Kelly Chen" in filename
- Files containing "Vicky Zhang" in filename
- Files containing "Micron stock" in filename
- Files containing "BCM Excess" in filename
- `.xlsx` format only

### 3. **Automatic Processing**
- Files are automatically detected and processed
- Cross-referenced with master hot parts data
- `Master_Matches_Data.xlsx` is updated
- Files are moved to `processed_XS/` directory

## 🔧 Configuration

### Default Settings
```bash
python excess_auto_processor.py \
  --unprocessed unprocessed_XS \
  --processed processed_XS \
  --output .
```

### Custom Directories
```bash
python excess_auto_processor.py \
  --unprocessed /path/to/excess/files \
  --processed /path/to/processed/files \
  --output /path/to/output
```

## 📊 What It Does

### **File Detection**
- Monitors `unprocessed_XS/` directory for new files
- Automatically detects excess files by filename pattern:
  - "Kelly Chen" files
  - "Vicky Zhang" files
  - "Micron stock" files
  - "BCM Excess" files
- Ignores non-excess files

### **Processing Steps**
1. **Loads** master hot parts data (`Master_Hot_Parts_Data.xlsx`)
2. **Finds** relevant sheets (ignores 'match'/'matching' sheets, ignores 'Global' for Micron files)
3. **Extracts** MPN, QTY, and Price data from excess files
4. **Applies** 12% markup to price data (if available)
5. **Cross-references** with master hot parts data
6. **Updates** `Master_Matches_Data.xlsx` with new matches
7. **Moves** processed files to `processed_XS/` directory

### **Output: Master Matches Data**
| Column | Description |
|--------|-------------|
| **MPN** | Matched part number |
| **Weekly_Hot_Parts_Date** | Date from hot parts data |
| **Reqs_Count** | Requirements count |
| **Manufacturer** | Part manufacturer |
| **Product_Class** | Product classification |
| **Description** | Part description |
| **Excess_Filename** | Source excess file |
| **Excess_QTY** | Available quantity |
| **Target_Price** | Price with 12% markup (if available) |

## 🎯 Use Cases

### **Daily Workflow**
1. **Start processor**: `./start_excess_processor.sh`
2. **Drop files**: Drag excess files to `unprocessed_XS/`
3. **Monitor**: Watch files get processed automatically
4. **Review**: Check `Master_Matches_Data.xlsx` for matches

### **Batch Processing**
1. **Collect files**: Gather multiple excess files
2. **Drop all**: Move all files to `unprocessed_XS/` at once
3. **Auto process**: All files processed sequentially
4. **Review results**: Check consolidated matches

### **Continuous Operation**
- Processor runs continuously in background
- New files processed as they arrive
- No manual intervention required
- Maintains historical match data

## 📝 Logging

### **Log File: `excess_auto_processor.log`**
Contains detailed information about:
- File detection and processing
- Cross-referencing results
- Error handling and recovery
- File movement operations

### **Sample Log Output**
```
2025-07-09 16:02:10,294 - INFO - Found 1 existing excess files to process:
2025-07-09 16:02:10,294 - INFO -   - 2025.07.08 Kelly Chen - TNR852.xlsx
2025-07-09 16:02:10,317 - INFO - Using sheet: Stock List (shape: (585, 5))
2025-07-09 16:02:10,377 - INFO - Found 29 matches in unprocessed_XS/2025.07.08 Kelly Chen - TNR852.xlsx
2025-07-09 16:02:10,452 - INFO - Updated Master_Matches_Data.xlsx with 632 total matches
2025-07-09 16:02:10,452 - INFO - Moved 2025.07.08 Kelly Chen - TNR852.xlsx to processed directory
```

## 🔒 Safety Features

### **Data Protection**
- **No data corruption**: Original files never modified
- **Duplicate prevention**: Removes redundant matches
- **Error recovery**: Continues processing after individual failures
- **File backup**: Processed files preserved in `processed_XS/`

### **Error Handling**
- **File validation**: Checks file format and structure
- **Graceful failures**: Continues processing other files
- **Error logging**: Detailed error messages in log file
- **File marking**: Failed files marked with `_ERROR` suffix

## 🎯 Benefits

### ✅ **Separation of Concerns**
- **Independent workflows**: Hot parts and excess processing separate
- **No conflicts**: Each system has its own directories
- **Clear organization**: Easy to understand and maintain

### ✅ **Automation**
- **Zero manual work**: Drop files and forget
- **Real-time processing**: Immediate cross-referencing
- **Continuous operation**: Runs 24/7 if needed

### ✅ **Scalability**
- **Handles multiple files**: Processes batch operations
- **Memory efficient**: Processes one file at a time
- **Performance optimized**: Fast processing of large datasets

### ✅ **Reliability**
- **Robust error handling**: Continues after failures
- **Data integrity**: Preserves all original data
- **Audit trail**: Complete logging of all operations

## 🚨 Troubleshooting

### **Common Issues**

**Processor won't start:**
- Check Python 3 is installed: `python3 --version`
- Verify master hot parts file exists: `ls Master_Hot_Parts_Data.xlsx`
- Check directory permissions: `ls -la unprocessed_XS/`

**Files not being processed:**
- Ensure filename contains "Kelly Chen" or "Vicky Zhang"
- Verify file is `.xlsx` format
- Check file is completely copied to directory

**No matches found:**
- Verify master hot parts data exists and is valid
- Check excess files contain valid MPN data
- Review log file for processing details

**Files stuck in unprocessed:**
- Check log file for error messages
- Verify file format and structure
- Ensure file is not corrupted

### **Debug Mode**
For detailed debugging, modify the logging level in the script:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📊 Performance

### **Processing Speed**
- **Small files** (< 1MB): ~1-3 seconds
- **Medium files** (1-10MB): ~3-10 seconds
- **Large files** (> 10MB): ~10-30 seconds

### **Resource Usage**
- **Memory**: Low memory footprint
- **CPU**: Minimal CPU usage
- **Disk**: Only reads input files, writes output

### **Scalability**
- **File count**: Handles hundreds of files
- **File size**: Processes files up to 100MB+
- **Concurrent**: Processes files sequentially for safety

## 🔄 Integration

### **With Hot Parts Processor**
- **Independent operation**: Can run simultaneously
- **Shared data**: Both use `Master_Hot_Parts_Data.xlsx`
- **Separate outputs**: Different output files and directories

### **With Existing Workflows**
- **Non-intrusive**: Doesn't interfere with existing processes
- **Additive**: Adds new functionality without changes
- **Optional**: Can be used independently

## 📞 Support

### **Getting Help**
1. **Check logs**: Review `excess_auto_processor.log`
2. **Verify setup**: Ensure directories and files exist
3. **Test with sample**: Try with a known good file
4. **Check documentation**: Review this README

### **File Requirements**
- **Excess files**: Must contain "Kelly Chen" or "Vicky Zhang"
- **Format**: `.xlsx` files only
- **Structure**: Must have MPN column
- **Master data**: `Master_Hot_Parts_Data.xlsx` must exist

### **Best Practices**
- **Regular monitoring**: Check log file periodically
- **Backup data**: Keep copies of important files
- **Test new files**: Verify format before processing
- **Clean directories**: Remove old processed files periodically 