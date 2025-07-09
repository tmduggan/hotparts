# Configuration for Hot Parts Parser

# Input/Output settings
INPUT_DIRECTORY = "."  # Directory containing Excel files
OUTPUT_DIRECTORY = "."  # Directory for output files

# File patterns to process
FILE_PATTERN = "Weekly Hot Parts List"  # Files containing this pattern will be processed

# Column mappings for different sheet types
DATE_SHEET_COLUMNS = {
    'MPN': ['MPN'],
    'Reqs_Count': ['Reqs Count', 'ReqsCount', 'Requirements Count'],
    'Manufacturer': ['MFG', 'Manufacturer', 'Mfg'],
    'Product_Class': ['Product Class', 'ProductClass', 'Class'],
    'Description': ['Description', 'Desc', 'Part Description']
}

PIVOT_SHEET_COLUMNS = {
    'MPN': ['MPN'],
    'Reqs_Count': ['Reqs Count', 'ReqsCount', 'Requirements Count']
}

# Output file names
MASTER_DATA_FILE = "Master_Hot_Parts_Data.xlsx"
PIVOT_DATA_FILE = "Master_Pivot_Data.xlsx"

# Data cleaning options
REMOVE_DUPLICATES = True
SORT_BY = ['MPN', 'Date']
SORT_ASCENDING = [True, True]

# Date format for extraction
DATE_PATTERN = r'(\d{4}\.\d{2}\.\d{2})'  # Matches YYYY.MM.DD format 