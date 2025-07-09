# Hot Parts Excel Processor

An intelligent, automated system for processing "Weekly Hot Parts List" Excel files with duplicate detection and real-time file monitoring.

## 🚀 Features

- **Automatic File Processing**: Drop Excel files into `unprocessed/` directory for instant processing
- **Duplicate Detection**: Intelligently prevents redundant entries while preserving new datapoints
- **Real-time Monitoring**: File watcher automatically detects and processes new files
- **Data Integrity**: Maintains clean master files with no duplicates
- **Error Handling**: Robust error recovery and detailed logging
- **Scalable**: Handles hundreds of files efficiently

## 📁 Repository Structure

```
HotParts/
├── unprocessed/                    # 🎯 Drop Excel files here
├── processed/                      # ✅ Processed files go here
├── enhanced_auto_processor.py      # 🤖 Enhanced processor with duplicate detection
├── hot_parts_parser.py            # 🔧 Core parsing engine
├── start_enhanced_processor.sh     # 🚀 Easy startup script
├── requirements.txt               # 📦 Python dependencies
├── .gitignore                     # 🚫 Excludes Excel files and logs
└── [documentation files...]
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

### 3. Start the Enhanced Processor
```bash
./start_enhanced_processor.sh
```

### 4. Drop Excel Files
Simply drag and drop your "Weekly Hot Parts List" Excel files into the `unprocessed/` directory. The system will:
- ✅ Process files automatically
- ✅ Detect and remove duplicates
- ✅ Move processed files to `processed/` directory
- ✅ Update master data files

## 📊 Output Files

The system creates two master files:

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

## 🔍 Duplicate Detection Logic

### ✅ What Gets Detected as Duplicates
- **Same MPN + Same Date**: Identical tab data across different files
- **Result**: Only the first occurrence is kept

### ✅ What Gets Preserved as New Data
- **Same MPN + Different Date**: Same part number in different time periods
- **Different MPN**: Always new data regardless of date
- **Result**: Both records kept (different datapoints)

## 🛠️ Usage Options

### Enhanced Auto Processor (Recommended)
```bash
./start_enhanced_processor.sh
```

### Direct Python Command
```bash
python enhanced_auto_processor.py
```

### Custom Directories
```bash
python enhanced_auto_processor.py \
  --unprocessed /path/to/unprocessed \
  --processed /path/to/processed \
  --output /path/to/output
```

### Batch Processing
```bash
python batch_processor.py [input_dir] [output_dir]
```

## 📝 Logging

- **enhanced_auto_processor.log**: Detailed processing logs
- **auto_processor.log**: Basic processor logs
- Console output: Real-time status updates

## 🔧 Configuration

Edit `config.py` to customize:
- File patterns to process
- Column mappings
- Output file names
- Data cleaning options

## 🚨 Safety Features

### ✅ Duplicate File Safety
- **No data corruption**: Original files never modified
- **File movement**: Processed files safely moved to `processed/` directory
- **Error handling**: Failed files marked with `_ERROR` suffix
- **Audit trail**: All activities logged

### ✅ Data Integrity
- **Duplicate prevention**: No redundant entries in master files
- **Memory efficient**: Only loads existing data once
- **Fast processing**: Uses optimized algorithms for large datasets

## 📈 Performance

- **Small files** (< 1MB): ~2-5 seconds
- **Medium files** (1-10MB): ~5-15 seconds  
- **Large files** (> 10MB): ~15-60 seconds
- **Scalability**: Handles hundreds of files efficiently

## 🎯 Use Cases

### Daily Workflow
1. Start the enhanced processor: `./start_enhanced_processor.sh`
2. Drop new Excel files into `unprocessed/` directory
3. Monitor processing via log files
4. Use updated master files for analysis

### Batch Processing
1. Copy multiple files to `unprocessed/` directory
2. Start auto processor
3. Monitor progress via log file
4. Check master files for consolidated data

## 🚨 Troubleshooting

### Common Issues

**Files not being processed:**
- Check that filenames contain "Weekly Hot Parts List"
- Verify files have `.xlsx` or `.xls` extension
- Check log files for error messages

**Processing errors:**
- Look for `_ERROR` files in `processed/` directory
- Check log file for specific error details
- Verify Excel file structure matches expected format

**Duplicate detection issues:**
- Check log file for duplicate detection details
- Verify tab names and MPN formatting
- Review the duplicate detection scenarios in documentation

## 📞 Support

For issues or questions:
1. Check the log files for detailed information
2. Review the documentation files
3. Verify file naming and structure
4. Test with a small subset of files first

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