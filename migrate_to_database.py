"""
Migration Script: Excel to Database
Converts existing Excel master files to SQLite database format.
"""

import pandas as pd
import logging
import os
from database_manager import DatabaseManager
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelToDatabaseMigrator:
    """Migrates Excel data to SQLite database."""
    
    def __init__(self, db_path: str = "hotparts.db"):
        """Initialize migrator.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_manager = DatabaseManager(db_path)
    
    def migrate_hot_parts_data(self, excel_file: str = "Master_Hot_Parts_Data.xlsx") -> int:
        """Migrate hot parts data from Excel to database.
        
        Args:
            excel_file: Path to Excel file containing hot parts data
            
        Returns:
            Number of records migrated
        """
        if not os.path.exists(excel_file):
            logger.warning(f"Hot parts Excel file not found: {excel_file}")
            return 0
        
        try:
            logger.info(f"Migrating hot parts data from: {excel_file}")
            
            # Read Excel file
            df = pd.read_excel(excel_file)
            logger.info(f"Read {len(df)} records from Excel file")
            
            # Convert DataFrame to list of dictionaries
            records = []
            for _, row in df.iterrows():
                record = {
                    'MPN': str(row.get('MPN', '')),
                    'Date': str(row.get('Date', '')),
                    'Reqs_Count': int(row.get('Reqs_Count', 0)) if pd.notna(row.get('Reqs_Count')) else 0,
                    'Manufacturer': str(row.get('Manufacturer', '')),
                    'Product_Class': str(row.get('Product_Class', '')),
                    'Description': str(row.get('Description', '')),
                    'source_file': excel_file
                }
                records.append(record)
            
            # Insert into database
            inserted = self.db_manager.insert_hot_parts(records)
            
            # Log processing
            self.db_manager.log_processing(
                filename=excel_file,
                file_type='hot_parts',
                status='success',
                records_processed=len(records),
                records_added=inserted,
                records_skipped=len(records) - inserted
            )
            
            logger.info(f"Successfully migrated {inserted} hot parts records")
            return inserted
            
        except Exception as e:
            logger.error(f"Failed to migrate hot parts data: {e}")
            
            # Log error
            self.db_manager.log_processing(
                filename=excel_file,
                file_type='hot_parts',
                status='error',
                error_message=str(e)
            )
            return 0
    
    def migrate_matches_data(self, excel_file: str = "Master_Matches_Data.xlsx") -> int:
        """Migrate matches data from Excel to database.
        
        Args:
            excel_file: Path to Excel file containing matches data
            
        Returns:
            Number of records migrated
        """
        if not os.path.exists(excel_file):
            logger.warning(f"Matches Excel file not found: {excel_file}")
            return 0
        
        try:
            logger.info(f"Migrating matches data from: {excel_file}")
            
            # Read Excel file
            df = pd.read_excel(excel_file)
            logger.info(f"Read {len(df)} records from Excel file")
            
            # Convert DataFrame to list of dictionaries
            records = []
            for _, row in df.iterrows():
                record = {
                    'MPN': str(row.get('MPN', '')),
                    'Weekly_Hot_Parts_Date': str(row.get('Weekly_Hot_Parts_Date', '')),
                    'Reqs_Count': int(row.get('Reqs_Count', 0)) if pd.notna(row.get('Reqs_Count')) else 0,
                    'Manufacturer': str(row.get('Manufacturer', '')),
                    'Product_Class': str(row.get('Product_Class', '')),
                    'Description': str(row.get('Description', '')),
                    'Excess_Filename': str(row.get('Excess_Filename', '')),
                    'Excess_QTY': int(row.get('Excess_QTY', 0)) if pd.notna(row.get('Excess_QTY')) else 0,
                    'Target_Price': float(row.get('Target_Price', 0)) if pd.notna(row.get('Target_Price')) else None
                }
                records.append(record)
            
            # Insert into database
            inserted = self.db_manager.insert_matches(records)
            
            # Log processing
            self.db_manager.log_processing(
                filename=excel_file,
                file_type='excess',
                status='success',
                records_processed=len(records),
                records_added=inserted,
                records_skipped=len(records) - inserted
            )
            
            logger.info(f"Successfully migrated {inserted} matches records")
            return inserted
            
        except Exception as e:
            logger.error(f"Failed to migrate matches data: {e}")
            
            # Log error
            self.db_manager.log_processing(
                filename=excel_file,
                file_type='excess',
                status='error',
                error_message=str(e)
            )
            return 0
    
    def migrate_all_data(self) -> dict:
        """Migrate all available Excel data to database.
        
        Returns:
            Dictionary with migration results
        """
        results = {
            'hot_parts_migrated': 0,
            'matches_migrated': 0,
            'total_migrated': 0
        }
        
        logger.info("Starting migration of all Excel data to database")
        
        # Migrate hot parts data
        results['hot_parts_migrated'] = self.migrate_hot_parts_data()
        
        # Migrate matches data
        results['matches_migrated'] = self.migrate_matches_data()
        
        # Calculate total
        results['total_migrated'] = results['hot_parts_migrated'] + results['matches_migrated']
        
        logger.info(f"Migration completed: {results['total_migrated']} total records migrated")
        
        return results
    
    def verify_migration(self) -> bool:
        """Verify that migration was successful.
        
        Returns:
            True if verification passes, False otherwise
        """
        try:
            stats = self.db_manager.get_database_stats()
            
            print("\n" + "="*50)
            print("MIGRATION VERIFICATION")
            print("="*50)
            
            if stats['hot_parts_count'] > 0:
                print(f"✅ Hot Parts: {stats['hot_parts_count']} records")
            else:
                print("❌ Hot Parts: No records found")
            
            if stats['matches_count'] > 0:
                print(f"✅ Matches: {stats['matches_count']} records")
            else:
                print("❌ Matches: No records found")
            
            if stats['unique_hot_parts_mpns'] > 0:
                print(f"✅ Unique Hot Parts MPNs: {stats['unique_hot_parts_mpns']}")
            else:
                print("❌ Unique Hot Parts MPNs: No data")
            
            if stats['unique_match_mpns'] > 0:
                print(f"✅ Unique Match MPNs: {stats['unique_match_mpns']}")
            else:
                print("❌ Unique Match MPNs: No data")
            
            print(f"✅ Date Range: {stats.get('hot_parts_date_range', 'No data')}")
            print("="*50)
            
            # Check if we have meaningful data
            return (stats['hot_parts_count'] > 0 or stats['matches_count'] > 0)
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

def main():
    """Main function for migration script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Excel data to SQLite database")
    parser.add_argument('--db', default='hotparts.db', help='Database file path')
    parser.add_argument('--hot-parts-file', default='Master_Hot_Parts_Data.xlsx', help='Hot parts Excel file')
    parser.add_argument('--matches-file', default='Master_Matches_Data.xlsx', help='Matches Excel file')
    parser.add_argument('--verify', action='store_true', help='Verify migration after completion')
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = ExcelToDatabaseMigrator(args.db)
    
    # Perform migration
    results = migrator.migrate_all_data()
    
    # Print results
    print("\n" + "="*50)
    print("MIGRATION RESULTS")
    print("="*50)
    print(f"Hot Parts Records: {results['hot_parts_migrated']}")
    print(f"Matches Records: {results['matches_migrated']}")
    print(f"Total Records: {results['total_migrated']}")
    print("="*50)
    
    # Verify if requested
    if args.verify:
        success = migrator.verify_migration()
        if success:
            print("\n✅ Migration verification passed!")
        else:
            print("\n❌ Migration verification failed!")
    
    # Show database stats
    print("\n" + "="*50)
    print("DATABASE STATISTICS")
    print("="*50)
    stats = migrator.db_manager.get_database_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 