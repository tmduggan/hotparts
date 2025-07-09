# Excess Cross-Reference Processor

An intelligent system that cross-references excess inventory lists with master hot parts data to identify potential matches and create a consolidated Master Matches Data file.

## 🎯 Purpose

Automatically identify parts that appear in both:
- **Excess inventory lists** (from Kelly Chen, Vicky Zhang, etc.)
- **Master hot parts data** (from weekly hot parts lists)

This helps identify potential opportunities to use excess inventory for hot parts requirements.

## 📊 Output: Master Matches Data

The system creates `Master_Matches_Data.xlsx` with the following columns:

| Column | Description | Source |
|--------|-------------|---------|
| **MPN** | Part number that matched | Excess file |
| **Weekly_Hot_Parts_Date** | Date from hot parts data | Master hot parts |
| **Reqs_Count** | Requirements count | Master hot parts |
| **Manufacturer** | Part manufacturer | Master hot parts |
| **Product_Class** | Product classification | Master hot parts |
| **Description** | Part description | Master hot parts |
| **Excess_Filename** | Name of excess file | Excess file |
| **Excess_QTY** | Available quantity | Excess file |
| **Target_Price** | Price with 12% markup | Excess file (if available) |

## 🔍 How It Works

### 1. **File Detection**
- Automatically finds excess files containing:
  - "Kelly Chen" in filename
  - "Vicky Zhang" in filename  
  - "Micron stock" in filename
  - "BCM Excess" in filename
- Supports `.xlsx` format files

### 2. **Sheet Selection**
- **Ignores** sheets with "match" or "matching" in the name
- **Ignores** "Global" tab for Micron stock files
- **Finds** relevant data sheets (often named "Raw Data", "Stock List", "BCM Excess", etc.)
- **Validates** sheets contain MPN column

### 3. **Column Detection**
- **MPN Column**: Automatically finds columns containing "MPN"
- **QTY Column**: Finds quantity columns ("QTY", "Stock QTY", "Quantity")
- **Price Column**: Finds price columns ("Price", "Target", "Cost")

### 4. **Data Cleaning**
- **MPN Values**: Strips whitespace and normalizes
- **QTY Values**: Removes commas, spaces, converts to integers
  - `" 2,643"` → `2643`
  - `"1,000"` → `1000`
- **Price Values**: Removes formatting, applies 12% markup
  - `"1.00"` → `1.12`
  - `"$2.50"` → `2.80`

### 5. **Cross-Reference Matching**
- Compares each MPN from excess files against master hot parts data
- Creates match records for each successful match
- Handles multiple matches per MPN (different dates)

## 🚀 Usage

### Basic Usage
```bash
python excess_cross_reference.py
```

### Enhanced Usage (with logging)
```bash
python enhanced_excess_processor.py
```

### Programmatic Usage
```python
from enhanced_excess_processor import EnhancedExcessProcessor

# Create processor
processor = EnhancedExcessProcessor()

# Load master data
processor.load_master_data()

# Process excess files
processor.process_all_excess_files()

# Create matches file
processor.create_master_matches_file()
```

## 📁 File Structure Requirements

### Excess Files
- **Filename pattern**: Contains "Kelly Chen" or "Vicky Zhang"
- **Format**: `.xlsx` files
- **Required columns**: MPN column (case-insensitive)
- **Optional columns**: QTY/Quantity column

### Example Excess File Structure
```
2025.07.08 Kelly Chen - TNR852.xlsx
├── Stock List (relevant sheet)
│   ├── Manufacturer
│   ├── MPN ✅
│   ├── Stock QTY ✅
│   ├── OPO QTY
│   └── Location
└── matching list (ignored)

2025.07.08 Vicky Zhang - CELIPC-S.xlsx
├── Raw Data (relevant sheet)
│   ├── IPN
│   ├── MPN ✅
│   ├── Manufacturer
│   ├── QTY ✅
│   └── Item Description
└── Matching (ignored)

Micron stock.xlsx
├── Raw Data (relevant sheet)
│   ├── MFG
│   ├── MPN ✅
│   ├── Quantity ✅
│   ├── Market Price ✅
│   └── Description
└── Global (ignored)

BCM Excess - 2025.06.23 to 2025.07.07.xlsx
└── BCM Excess (single sheet)
    ├── Offer Date
    ├── MPN ✅
    ├── Quantity ✅
    ├── Unit Cost ✅
    └── Excess Contact
```

## 📈 Example Results

### Sample Match Record
```
MPN: BCM56870A0KFSBG
Weekly_Hot_Parts_Date: 2025.06.30
Reqs_Count: 5
Manufacturer: Broadcom
Product_Class: Interface
Description: 3.2T 32X100G MULTI LAYER SWITCH
Excess_Filename: 2025.07.08 Vicky Zhang - CELIPC-S.xlsx
Excess_QTY: 1898
Target_Price: 1.12 (if price data available)
```

### Processing Summary
```
Found 4 excess files:
  - 2025.07.08 Kelly Chen - TNR852.xlsx
  - 2025.07.08 Vicky Zhang - CELIPC-S.xlsx
  - Micron stock.xlsx
  - BCM Excess - 2025.06.23 to 2025.07.07.xlsx

Processing results:
  ✅ Kelly Chen: 29 matches found
  ✅ Vicky Zhang: 603 matches found
  ✅ Micron stock: 12 matches found
  ✅ BCM Excess: 6 matches found
  📊 Total matches: 650
  🔍 Unique MPNs: 119
```

## 🔧 Configuration

### File Patterns
The system automatically detects files containing:
- "Kelly Chen" in filename
- "Vicky Zhang" in filename
- `.xlsx` extension

### Sheet Filtering
Automatically skips sheets containing:
- "match" (case-insensitive)
- "matching" (case-insensitive)

### Column Detection
**MPN Columns**: Any column containing "MPN"
**QTY Columns**: Priority order:
1. "QTY"
2. "Stock QTY" 
3. Any column containing "qty", "quantity", or "stock"
**Price Columns**: Priority order:
1. "Price"
2. Any column containing "price", "target", or "cost"

## 📝 Logging

### Log File: `excess_processor.log`
Contains detailed information about:
- File processing status
- Sheet selection decisions
- Column detection results
- Match statistics
- Error messages

### Log Levels
- **INFO**: Normal operations (file processing, matches found)
- **WARNING**: Non-critical issues (sheets skipped, files not found)
- **ERROR**: Processing failures and system errors

## 🎯 Use Cases

### Daily Workflow
1. **Drop excess files** into working directory
2. **Run cross-reference**: `python enhanced_excess_processor.py`
3. **Review matches**: Check `Master_Matches_Data.xlsx`
4. **Take action**: Use excess inventory for hot parts requirements

### Batch Processing
1. **Collect excess files** from multiple sources
2. **Run processor** on all files at once
3. **Analyze results** for inventory optimization opportunities

### Integration with Hot Parts Processor
- Can be run after hot parts processing
- Updates matches when new hot parts data is available
- Maintains historical match data

## 🚨 Troubleshooting

### Common Issues

**No matches found:**
- Check that master hot parts file exists
- Verify excess files contain valid MPN data
- Check log file for processing details

**Files not being processed:**
- Ensure filenames contain "Kelly Chen" or "Vicky Zhang"
- Verify files have `.xlsx` extension
- Check that relevant sheets contain MPN columns

**QTY values showing as 0:**
- Check that QTY columns exist in excess files
- Verify QTY data is in numeric format
- Review log file for QTY column detection

### Debug Mode
For detailed debugging, modify the logging level:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📊 Performance

### Processing Speed
- **Small files** (< 1MB): ~1-3 seconds
- **Medium files** (1-10MB): ~3-10 seconds  
- **Large files** (> 10MB): ~10-30 seconds

### Memory Usage
- Efficient processing of large datasets
- Processes one file at a time
- Automatic cleanup after processing

### Scalability
- Handles hundreds of excess files efficiently
- Processes files sequentially to avoid conflicts
- Can run continuously for batch processing

## 🔒 Data Integrity

### Safety Features
- **No data corruption**: Original files never modified
- **Duplicate prevention**: Removes duplicate matches
- **Data validation**: Validates MPN and QTY formats
- **Error recovery**: Continues processing after individual file failures

### Quality Assurance
- **MPN normalization**: Consistent formatting
- **QTY cleaning**: Removes formatting artifacts
- **Duplicate removal**: Prevents redundant match records
- **Data validation**: Ensures numeric QTY values

## 🎉 Benefits

### ✅ **Inventory Optimization**
- Identifies potential excess inventory usage
- Reduces waste and costs
- Improves inventory turnover

### ✅ **Automation**
- No manual cross-referencing required
- Handles multiple file formats automatically
- Processes large datasets efficiently

### ✅ **Data Quality**
- Consistent data formatting
- Automatic duplicate removal
- Comprehensive logging and audit trail

### ✅ **Scalability**
- Handles growing datasets
- Processes multiple file types
- Maintains performance with large inventories

## 📞 Support

For issues or questions:
1. Check the log file: `excess_processor.log`
2. Review this README
3. Verify file naming and structure
4. Test with a small subset of files first
5. Check that master hot parts data is available 