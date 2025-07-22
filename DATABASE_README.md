# Hot Parts Database System

A SQLite-based database system for managing hot parts and excess inventory data with advanced querying capabilities.

## 🎯 Overview

The database system provides:
- **Structured Data Storage**: SQLite database with proper schema and relationships
- **Advanced Querying**: Complex queries for random parts selection and analysis
- **Data Integrity**: Proper constraints and duplicate prevention
- **Performance**: Indexed tables for fast queries
- **Compatibility**: Excel export for existing workflows

## 📊 Database Schema

### Tables

#### `hot_parts`
Stores data from weekly hot parts lists:
- `id`: Primary key
- `mpn`: Part number
- `date`: Tab date
- `reqs_count`: Requirements count
- `manufacturer`: Part manufacturer
- `product_class`: Product classification
- `description`: Part description
- `source_file`: Source Excel file
- `created_at`, `updated_at`: Timestamps

#### `excess_inventory`
Stores data from excess inventory lists:
- `id`: Primary key
- `mpn`: Part number
- `excess_filename`: Source file name
- `excess_qty`: Available quantity
- `target_price`: Price with markup
- `manufacturer`: Part manufacturer
- `sheet_name`: Source sheet name
- `created_at`, `updated_at`: Timestamps

#### `matches`
Stores cross-referenced data:
- `id`: Primary key
- `mpn`: Part number
- `hot_parts_date`: Date from hot parts
- `reqs_count`: Requirements count
- `manufacturer`: Part manufacturer
- `product_class`: Product classification
- `description`: Part description
- `excess_filename`: Source excess file
- `excess_qty`: Available quantity
- `target_price`: Target price
- `created_at`, `updated_at`: Timestamps

#### `processing_log`
Tracks file processing history:
- `id`: Primary key
- `filename`: Processed file name
- `file_type`: Type of file ('hot_parts' or 'excess')
- `status`: Processing status
- `records_processed`: Number of records processed
- `records_added`: Number of records added
- `records_skipped`: Number of records skipped
- `error_message`: Error message if any
- `processed_at`: Processing timestamp

### Views

#### `v_hot_parts_summary`
Summary statistics for hot parts data:
- `mpn`, `manufacturer`
- `total_occurrences`: Number of times part appears
- `first_seen`, `last_seen`: Date range
- `total_reqs_count`, `avg_reqs_count`: Requirements statistics

#### `v_excess_summary`
Summary statistics for excess inventory:
- `mpn`, `manufacturer`
- `total_listings`: Number of listings
- `total_available_qty`: Total available quantity
- `avg_target_price`, `min_target_price`, `max_target_price`: Price statistics

#### `v_matches_summary`
Summary statistics for matches:
- `mpn`, `manufacturer`
- `total_matches`: Number of matches
- `total_available_qty`: Total available quantity
- `avg_target_price`, `min_target_price`, `max_target_price`: Price statistics

## 🚀 Quick Start

### 1. Initialize Database
```bash
# The database is automatically initialized when you first use it
python -c "from database_manager import DatabaseManager; DatabaseManager()"
```

### 2. Migrate Existing Excel Data
```bash
# Migrate existing Excel files to database
python migrate_to_database.py --verify
```

### 3. Test Database Functionality
```bash
# Run tests to verify everything works
python test_database.py
```

### 4. Generate Random Parts List
```bash
# Get 10 random parts with price >$10 from up to 5 manufacturers
python query_interface.py random --count 10 --min-price 10.0 --max-manufacturers 5
```

## 📋 Usage Examples

### Command Line Interface

#### Generate Random Parts List
```bash
# Basic random parts list
python query_interface.py random

# Custom parameters
python query_interface.py random --count 15 --min-price 25.0 --max-manufacturers 3 --output my_parts_list

# Save to file
python query_interface.py random --count 20 --min-price 15.0 --output daily_parts
```

#### View Database Statistics
```bash
# Show database statistics
python query_interface.py stats

# Show data summaries
python query_interface.py summaries
```

#### Export Data
```bash
# Export to Excel files
python query_interface.py export

# Export to specific directory
python query_interface.py export --output-dir /path/to/exports
```

#### Custom Queries
```bash
# Execute custom SQL query
python query_interface.py query "SELECT * FROM matches WHERE target_price > 50.0 LIMIT 10"

# Find parts by manufacturer
python query_interface.py query "SELECT * FROM matches WHERE manufacturer LIKE '%Broadcom%'"
```

### Programmatic Usage

#### Basic Database Operations
```python
from database_manager import DatabaseManager

# Initialize database
db = DatabaseManager("hotparts.db")

# Insert hot parts data
hot_parts_data = [
    {
        'MPN': 'ABC123',
        'Date': '2025.07.07',
        'Reqs_Count': 5,
        'Manufacturer': 'Test Manufacturer',
        'Product_Class': 'Test Class',
        'Description': 'Test Description',
        'source_file': 'test_file.xlsx'
    }
]
db.insert_hot_parts(hot_parts_data)

# Get random parts
random_parts = db.get_random_parts(count=10, min_price=10.0, max_manufacturers=5)

# Get database statistics
stats = db.get_database_stats()
```

#### Query Interface
```python
from query_interface import QueryInterface

# Initialize interface
interface = QueryInterface("hotparts.db")

# Generate random parts list
df = interface.get_random_parts_list(
    count=10, 
    min_price=15.0, 
    max_manufacturers=3,
    output_file="daily_parts"
)

# Show database statistics
interface.show_database_stats()

# Export data
interface.export_data("./exports")
```

## 🎯 Random Parts Selection

The system provides intelligent random parts selection with the following features:

### Selection Criteria
- **Count**: Number of parts to return
- **Minimum Price**: Filter by minimum target price
- **Maximum Manufacturers**: Limit diversity across manufacturers
- **Pseudorandom**: True randomization, not alphabetical

### Algorithm
1. **Filter by Price**: Select only parts above minimum price
2. **Select Manufacturers**: Randomly select up to N manufacturers
3. **Rank by Manufacturer**: Within each manufacturer, rank parts randomly
4. **Limit per Manufacturer**: Maximum 2 parts per manufacturer
5. **Final Random Selection**: Randomly select from ranked results

### Example Query
```sql
WITH ranked_parts AS (
    SELECT 
        mpn, manufacturer, target_price, excess_qty,
        ROW_NUMBER() OVER (
            PARTITION BY manufacturer 
            ORDER BY RANDOM()
        ) as rn
    FROM matches 
    WHERE target_price > 10.0
    AND manufacturer IN (
        SELECT DISTINCT manufacturer 
        FROM matches 
        WHERE target_price > 10.0
        ORDER BY RANDOM() 
        LIMIT 5
    )
)
SELECT * FROM ranked_parts 
WHERE rn <= 2
ORDER BY RANDOM()
LIMIT 10;
```

## 📊 Data Analysis

### Summary Views
The database provides pre-built views for common analysis:

#### Hot Parts Analysis
```sql
SELECT * FROM v_hot_parts_summary 
WHERE total_occurrences > 5 
ORDER BY total_reqs_count DESC;
```

#### Excess Inventory Analysis
```sql
SELECT * FROM v_excess_summary 
WHERE total_available_qty > 1000 
ORDER BY avg_target_price DESC;
```

#### Match Analysis
```sql
SELECT * FROM v_matches_summary 
WHERE total_matches > 1 
ORDER BY total_available_qty DESC;
```

### Custom Analysis
```python
# Find high-value opportunities
high_value_query = """
SELECT mpn, manufacturer, target_price, excess_qty,
       (target_price * excess_qty) as total_value
FROM matches 
WHERE target_price > 50.0 AND excess_qty > 100
ORDER BY total_value DESC
LIMIT 20
"""

# Find parts with high demand
high_demand_query = """
SELECT mpn, manufacturer, reqs_count, target_price
FROM matches 
WHERE reqs_count > 10
ORDER BY reqs_count DESC
LIMIT 20
"""
```

## 🔧 Migration from Excel

### Automatic Migration
```bash
# Migrate all existing Excel files
python migrate_to_database.py

# Migrate with verification
python migrate_to_database.py --verify

# Migrate specific files
python migrate_to_database.py --hot-parts-file my_hot_parts.xlsx --matches-file my_matches.xlsx
```

### Migration Process
1. **Read Excel Files**: Parse existing master files
2. **Data Validation**: Check data integrity
3. **Database Insertion**: Insert with duplicate prevention
4. **Logging**: Track migration progress
5. **Verification**: Confirm successful migration

### Migration Results
```
==================================================
MIGRATION RESULTS
==================================================
Hot Parts Records: 1,234
Matches Records: 567
Total Records: 1,801
==================================================
```

## 📈 Performance

### Query Performance
- **Small Queries** (< 1000 records): ~1-5ms
- **Medium Queries** (1000-10000 records): ~5-50ms
- **Large Queries** (> 10000 records): ~50-500ms

### Database Size
- **Small Dataset** (< 10,000 records): ~1-5MB
- **Medium Dataset** (10,000-100,000 records): ~5-50MB
- **Large Dataset** (> 100,000 records): ~50-500MB

### Optimization Features
- **Indexed Columns**: All frequently queried columns are indexed
- **Composite Keys**: Efficient duplicate prevention
- **Views**: Pre-computed summaries for fast access
- **Connection Pooling**: Efficient database connections

## 🔒 Data Integrity

### Constraints
- **Primary Keys**: Unique identifiers for all records
- **Foreign Keys**: Referential integrity (if needed)
- **Unique Constraints**: Prevent duplicate entries
- **Check Constraints**: Data validation rules

### Duplicate Prevention
- **Hot Parts**: Unique on (MPN, Date, source_file)
- **Excess**: Unique on (MPN, excess_filename, sheet_name)
- **Matches**: Unique on all relevant fields

### Error Handling
- **Graceful Failures**: Continue processing after individual errors
- **Error Logging**: Detailed error tracking
- **Data Validation**: Input validation before insertion
- **Transaction Safety**: ACID compliance

## 🚨 Troubleshooting

### Common Issues

**Database not found:**
```bash
# Check if database file exists
ls -la hotparts.db

# Reinitialize database
python -c "from database_manager import DatabaseManager; DatabaseManager()"
```

**Migration fails:**
```bash
# Check Excel file format
python -c "import pandas as pd; print(pd.read_excel('Master_Hot_Parts_Data.xlsx').columns.tolist())"

# Check file permissions
ls -la Master_Hot_Parts_Data.xlsx
```

**No random parts found:**
```bash
# Check if data exists
python query_interface.py stats

# Lower minimum price
python query_interface.py random --min-price 1.0
```

**Slow queries:**
```bash
# Check database size
python query_interface.py stats

# Optimize with indexes (automatic)
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.init_database()"
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug logging
python query_interface.py random --count 5
```

## 📞 Support

### Getting Help
1. **Check Logs**: Review database operation logs
2. **Verify Data**: Use `python query_interface.py stats`
3. **Test Functionality**: Run `python test_database.py`
4. **Check Documentation**: Review this README

### File Requirements
- **Database**: SQLite 3.x compatible
- **Excel Files**: .xlsx format for migration
- **Permissions**: Read/write access to database directory

### Best Practices
- **Regular Backups**: Copy database file periodically
- **Data Validation**: Verify data before migration
- **Performance Monitoring**: Check query performance
- **Error Handling**: Monitor processing logs

---

**Note**: The database system is designed to work alongside the existing Excel-based workflow. You can continue using Excel files while gradually migrating to the database for advanced querying capabilities. 