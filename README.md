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
├── unprocessed/                    # 🎯 Drop hot parts Excel files here
├── processed/                      # ✅ Processed hot parts files
├── unprocessed_XS/                 # 🎯 Drop excess inventory files here
├── processed_XS/                   # ✅ Processed excess files
├── enhanced_auto_processor.py      # 🤖 Hot parts processor with duplicate detection
├── excess_auto_processor.py        # 🤖 Excess inventory processor
├── hot_parts_parser.py            # 🔧 Core hot parts parsing engine
├── enhanced_excess_processor.py    # 🔧 Core excess processing engine
├── start_enhanced_processor.sh     # 🚀 Hot parts startup script
├── start_excess_processor.sh       # 🚀 Excess startup script
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
├── demo_random_parts.py           # 🎯 Random parts selection demo
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

### 3. Start the Processors

#### Hot Parts Processing
```bash
./start_enhanced_processor.sh
```

#### Excess Inventory Processing
```bash
./start_excess_processor.sh
```

### 4. Drop Files for Processing

#### Hot Parts Files
Drag and drop "Weekly Hot Parts List" Excel files into the `unprocessed/` directory.

#### Excess Inventory Files
Drag and drop excess inventory files (containing "Kelly Chen", "Vicky Zhang", "Micron stock", or "BCM Excess") into the `unprocessed_XS/` directory.

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

## 🔄 How the Processors Work

### Hot Parts Processor
1. **Monitors** `unprocessed/` directory for new files
2. **Detects** files containing "Weekly Hot Parts List"
3. **Parses** date-based tabs and pivot tabs
4. **Removes** duplicates based on MPN + Date combination
5. **Updates** `Master_Hot_Parts_Data.xlsx` and `Master_Pivot_Data.xlsx`
6. **Moves** processed files to `processed/` directory

### Excess Inventory Processor
1. **Monitors** `unprocessed_XS/` directory for new files
2. **Detects** files containing "Kelly Chen", "Vicky Zhang", "Micron stock", or "BCM Excess"
3. **Finds** relevant sheets (ignores 'match'/'matching' sheets, ignores 'Global' for Micron)
4. **Extracts** MPN, QTY, and Price data
5. **Applies** 12% markup to price data (if available)
6. **Cross-references** with master hot parts data
7. **Updates** `Master_Matches_Data.xlsx` with new matches
8. **Moves** processed files to `processed_XS/` directory

## 🛠️ Usage Options

### Enhanced Auto Processor (Hot Parts)
```bash
./start_enhanced_processor.sh
```

### Excess Auto Processor
```bash
./start_excess_processor.sh
```

### Direct Python Commands
```bash
# Hot parts processing
python enhanced_auto_processor.py

# Excess processing
python excess_auto_processor.py
```

### Custom Directories
```bash
# Hot parts with custom directories
python enhanced_auto_processor.py \
  --unprocessed /path/to/unprocessed \
  --processed /path/to/processed \
  --output /path/to/output

# Excess with custom directories
python excess_auto_processor.py \
  --unprocessed unprocessed_XS \
  --processed processed_XS \
  --output .
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

### File Patterns
The system automatically detects files containing:
- **Hot Parts**: "Weekly Hot Parts List" in filename
- **Excess**: "Kelly Chen", "Vicky Zhang", "Micron stock", or "BCM Excess" in filename
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
1. Start both processors: `./start_enhanced_processor.sh` & `./start_excess_processor.sh`
2. Drop new Excel files into respective `unprocessed/` directories
3. Monitor processing via log files
4. Use updated master files for analysis

### Batch Processing
1. Copy multiple files to respective `unprocessed/` directories
2. Start auto processors
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
- Check that filenames contain expected patterns
- Verify files have `.xlsx` or `.xls` extension
- Check log files for error messages

**Processing errors:**
- Look for `_ERROR` files in processed directories
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

**Note**: Excel files (`.xlsx`, `.xls`) are excluded from version control via `.gitignore` to keep the repository clean and avoid storing large binary files. The `unprocessed/`, `processed/`, `unprocessed_XS/`, and `processed_XS/` directories are preserved for workflow structure. 