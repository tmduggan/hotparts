# Hot Parts Excel Processor

An intelligent, automated system for processing "Weekly Hot Parts List" Excel files and cross-referencing them with excess inventory data. Features duplicate detection, real-time file monitoring, and comprehensive data analysis.

## 🚀 Features

- **Automatic File Processing**: Drop Excel files into directories for instant processing
- **Duplicate Detection**: Intelligently prevents redundant entries while preserving new datapoints
- **Real-time Monitoring**: File watchers automatically detect and process new files
- **Cross-Reference System**: Matches hot parts with excess inventory for optimization
- **Database System**: SQLite database with advanced querying and random parts selection
- **Data Integrity**: Maintains clean master files with no duplicates
- **Error Handling**: Robust error recovery and detailed logging
- **Scalable**: Handles hundreds of files efficiently

## 📁 Repository Structure

```
HotParts/
├── unprocessed/                    # 🎯 Drop ALL Excel files here (hot parts + excess)
├── processed/                      # ✅ All processed files go here
├── unified_auto_processor.py       # 🤖 Unified processor for both file types
├── enhanced_auto_processor.py      # 🤖 Legacy hot parts processor
├── excess_auto_processor.py        # 🤖 Legacy excess processor
├── hot_parts_parser.py            # 🔧 Core hot parts parsing engine
├── enhanced_excess_processor.py    # 🔧 Core excess processing engine
├── start_unified_processor.sh      # 🚀 Unified startup script (recommended)
├── start_enhanced_processor.sh     # 🚀 Legacy hot parts startup script
├── start_excess_processor.sh       # 🚀 Legacy excess startup script
├── requirements.txt               # 📦 Python dependencies
├── .gitignore                     # 🚫 Excludes Excel files and logs
├── Master_Hot_Parts_Data.xlsx     # 📊 Consolidated hot parts data
├── Master_Pivot_Data.xlsx         # 📊 Consolidated pivot data
├── Master_Matches_Data.xlsx       # 📊 Cross-reference matches
├── database_schema.sql            # 🗄️ Database schema definition
├── database_manager.py            # 🗄️ Database operations manager
├── query_interface.py             # 🔍 Database query interface
├── migrate_to_database.py         # 🔄 Excel to database migration
├── test_database.py               # 🧪 Database functionality tests
└── DATABASE_README.md             # 📖 Database system documentation
```

## 🎯 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/tmduggan/hotparts.git
cd hotparts
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Unified Processor (Recommended)

```bash
./start_unified_processor.sh
```

### 4. Drop Files for Processing

#### All Excel Files
Drag and drop **all** Excel files into the `unprocessed/` directory:

- **Hot Parts Files**: Files containing "Weekly Hot Parts" in the filename
- **Excess Files**: Files that do NOT contain "Weekly Hot Parts" in the filename

The system automatically detects file type and processes accordingly.

### 5. Database Operations (Optional)

#### Migrate to Database
```bash
# Migrate existing Excel data to database
python migrate_to_database.py --verify
```

#### Generate Random Parts Lists
```bash
# Get 10 random parts with price >$10 from up to 5 manufacturers
python query_interface.py random --count 10 --min-price 10.0 --max-manufacturers 5

# Save to file
python query_interface.py random --count 15 --min-price 25.0 --output daily_parts
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

### Master_Matches_Data.xlsx
Contains cross-referenced data between hot parts and excess inventory:
- **MPN**: Matched part number
- **Weekly_Hot_Parts_Date**: Date from hot parts data
- **Reqs_Count**: Requirements count
- **Manufacturer**: Part manufacturer
- **Product_Class**: Product classification
- **Description**: Part description
- **Excess_Filename**: Source excess file
- **Excess_QTY**: Available quantity (cleaned to number)
- **Target_Price**: Price with 12% markup (if available)

## 🔍 Duplicate Detection Logic

### ✅ What Gets Detected as Duplicates
- **Same MPN + Same Date**: Identical tab data across different files
- **Result**: Only the first occurrence is kept

### ✅ What Gets Preserved as New Data
- **Same MPN + Different Date**: Same part number in different time periods
- **Different MPN**: Always new data regardless of date
- **Result**: Both records kept (different datapoints)

### Example Scenarios

#### Scenario 1: Exact Duplicate (Removed)
```
File A (2025.07.07): Tab "2025.06.30" → MPN "ABC123", Reqs_Count=5
File B (2025.06.30): Tab "2025.06.30" → MPN "ABC123", Reqs_Count=5
Result: Only File A record kept (duplicate detected)
```

#### Scenario 2: New Datapoint (Preserved)
```
File A (2025.07.07): Tab "2025.06.30" → MPN "ABC123", Reqs_Count=5
File B (2025.06.30): Tab "2025.07.07" → MPN "ABC123", Reqs_Count=8
Result: Both records kept (different dates = new datapoints)
```

## 🔄 How the Unified Processor Works

### File Type Detection
- **Hot Parts Files**: Filename contains "Weekly Hot Parts"
- **Excess Files**: Filename does NOT contain "Weekly Hot Parts"

### Processing Flow
1. **Monitors** `unprocessed/` directory for new files
2. **Detects** file type based on filename
3. **Routes** to appropriate processor:
   - Hot parts → `hot_parts_parser.py`
   - Excess → `enhanced_excess_processor.py`
4. **Handles** duplicates and validation
5. **Updates** master files accordingly
6. **Moves** successful files to `processed/` directory
7. **Keeps** failed files in `unprocessed/` with `.error` files

### Error Handling
- **Failed files** stay in `unprocessed/` directory
- **Error details** written to `.error` files (e.g., `file.xlsx.error`)
- **Processing continues** for other files

## 🛠️ Usage Options

### Unified Auto Processor (Recommended)
```bash
./start_unified_processor.sh
```

### Legacy Processors (Separate)
```bash
# Hot parts only
./start_enhanced_processor.sh

# Excess only  
./start_excess_processor.sh
```

### Direct Python Commands
```bash
# Unified processing (recommended)
python unified_auto_processor.py

# Legacy separate processing
python enhanced_auto_processor.py  # Hot parts only
python excess_auto_processor.py    # Excess only
```

### Custom Directories
```bash
# Unified with custom directories
python unified_auto_processor.py \
  --unprocessed /path/to/unprocessed \
  --processed /path/to/processed \
  --output /path/to/output

# Legacy with custom directories
python enhanced_auto_processor.py \
  --unprocessed /path/to/unprocessed \
  --processed /path/to/processed \
  --output /path/to/output
```

### Batch Processing
```bash
python batch_processor.py [input_dir] [output_dir]
```

### Database Operations
```bash
# Migrate Excel data to database
python migrate_to_database.py --verify

# Generate random parts list
python query_interface.py random --count 10 --min-price 15.0

# View database statistics
python query_interface.py stats

# Export database to Excel
python query_interface.py export

# Custom SQL query
python query_interface.py query "SELECT * FROM matches WHERE target_price > 50.0"
```

## 📝 Logging

### Log Files
- **enhanced_auto_processor.log**: Hot parts processing logs
- **excess_auto_processor.log**: Excess processing logs
- **auto_processor.log**: Basic processor logs

### Log Content
- File detection and processing status
- Duplicate detection results
- Cross-referencing statistics
- Error handling and recovery
- File movement operations

### Sample Log Output
```
2025-07-09 16:02:10,294 - INFO - Found 1 existing excess files to process:
2025-07-09 16:02:10,294 - INFO -   - 2025.07.08 Kelly Chen - TNR852.xlsx
2025-07-09 16:02:10,317 - INFO - Using sheet: Stock List (shape: (585, 5))
2025-07-09 16:02:10,377 - INFO - Found 29 matches in unprocessed_XS/2025.07.08 Kelly Chen - TNR852.xlsx
2025-07-09 16:02:10,452 - INFO - Updated Master_Matches_Data.xlsx with 632 total matches
2025-07-09 16:02:10,452 - INFO - Moved 2025.07.08 Kelly Chen - TNR852.xlsx to processed directory
```

## 🔧 Configuration

Edit `config.py` to customize:
- File patterns to process
- Column mappings
- Output file names
- Data cleaning options

### File Type Detection
The system automatically detects file types based on filename:
- **Hot Parts**: Contains "Weekly Hot Parts" in filename
- **Excess**: Does NOT contain "Weekly Hot Parts" in filename
- **Format**: `.xlsx` or `.xls` files

### Sheet Filtering
- **Hot Parts**: Processes date-based tabs and "Pivot" tabs
- **Excess**: Ignores sheets with "match" or "matching" in name, ignores "Global" for Micron files

### Column Detection
**MPN Columns**: Any column containing "MPN"
**QTY Columns**: Priority order:
1. "QTY"
2. "Stock QTY" 
3. Any column containing "qty", "quantity", or "stock"
**Price Columns**: Priority order:
1. "Price"
2. Any column containing "price", "target", or "cost"

## 🚨 Safety Features

### ✅ Duplicate File Safety
- **No data corruption**: Original files never modified
- **File movement**: Processed files safely moved to respective directories
- **Error handling**: Failed files marked with `_ERROR` suffix
- **Audit trail**: All activities logged

### ✅ Data Integrity
- **Duplicate prevention**: No redundant entries in master files
- **Memory efficient**: Only loads existing data once
- **Fast processing**: Uses optimized algorithms for large datasets

### ✅ Error Recovery
- **File validation**: Checks file format and structure
- **Graceful failures**: Continues processing other files
- **Error logging**: Detailed error messages in log files
- **File marking**: Failed files marked with `_ERROR` suffix

## 📈 Performance

### Processing Speed
- **Small files** (< 1MB): ~1-5 seconds
- **Medium files** (1-10MB): ~5-15 seconds  
- **Large files** (> 10MB): ~15-60 seconds
- **Scalability**: Handles hundreds of files efficiently

### Resource Usage
- **Memory**: Low memory footprint
- **CPU**: Minimal CPU usage
- **Disk**: Only reads input files, writes output

## 🎯 Use Cases

### Daily Workflow
1. Start unified processor: `./start_unified_processor.sh`
2. Drop all Excel files into `unprocessed/` directory
3. Monitor processing via log files
4. Use updated master files for analysis

### Batch Processing
1. Copy multiple files to `unprocessed/` directory
2. Start unified processor
3. Monitor progress via log files
4. Check master files for consolidated data

### Continuous Operation
- Processors run continuously in background
- New files processed as they arrive
- No manual intervention required
- Maintains historical data

## 🚨 Troubleshooting

### Common Issues

**Files not being processed:**
- Check that filenames contain "Weekly Hot Parts" for hot parts files
- Verify files have `.xlsx` or `.xls` extension
- Check for `.error` files in `unprocessed/` directory
- Check log files for error messages

**Processing errors:**
- Look for `.error` files in `unprocessed/` directory
- Check log files for specific error details
- Verify Excel file structure matches expected format

**Duplicate detection issues:**
- Check log files for duplicate detection details
- Verify tab names and MPN formatting
- Review the duplicate detection scenarios above

**No matches found (excess processing):**
- Verify master hot parts data exists and is valid
- Check excess files contain valid MPN data
- Review log files for processing details

### Debug Mode
For detailed debugging, modify the logging level in the scripts:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📞 Support

For issues or questions:
1. Check the log files for detailed information
2. Review this README and `DATABASE_README.md` for database operations
3. Verify file naming and structure
4. Test with a small subset of files first
5. Run `python test_database.py` to verify database functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: Excel files (`.xlsx`, `.xls`) are excluded from version control via `.gitignore` to keep the repository clean and avoid storing large binary files. The `unprocessed/` and `processed/` directories are preserved for workflow structure. 