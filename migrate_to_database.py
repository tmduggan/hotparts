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
                file_type='matches',
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
                file_type='matches',
                status='error',
                error_message=str(e)
            )
            return 0
    
    def migrate_excess_inventory_data(self, processed_dir: str = "processed") -> int:
        """Migrate excess inventory data from processed files to database.
        
        Args:
            processed_dir: Directory containing processed excess files
            
        Returns:
            Number of records migrated
        """
        if not os.path.exists(processed_dir):
            logger.warning(f"Processed directory not found: {processed_dir}")
            return 0
        
        try:
            logger.info(f"Migrating excess inventory data from: {processed_dir}")
            
            # Find excess files (files that don't contain 'Weekly Hot Parts')
            excess_files = []
            for file in os.listdir(processed_dir):
                if (file.endswith('.xlsx') and 
                    'Weekly Hot Parts' not in file and
                    not file.endswith('_ERROR.xlsx') and
                    not file.startswith('duplicate_') and
                    not file.startswith('test_')):
                    excess_files.append(os.path.join(processed_dir, file))
            
            if not excess_files:
                logger.info("No excess files found for migration")
                return 0
            
            logger.info(f"Found {len(excess_files)} excess files to migrate")
            
            total_migrated = 0
            
            # Import the excess processor to parse files
            from enhanced_excess_processor import EnhancedExcessProcessor
            
            excess_processor = EnhancedExcessProcessor()
            
            for file_path in excess_files:
                try:
                    logger.info(f"Processing excess file: {os.path.basename(file_path)}")
                    
                    # Find the relevant sheet
                    sheet_name, df = excess_processor.find_relevant_sheet(file_path)
                    if sheet_name is None:
                        logger.warning(f"No relevant sheet found in {file_path}")
                        continue
                    
                    # Find MPN, QTY, and Price columns
                    mpn_cols = [col for col in df.columns if 'mpn' in str(col).lower()]
                    qty_col = excess_processor.find_qty_column(df)
                    price_col = excess_processor.find_price_column(df)
                    
                    if not mpn_cols:
                        logger.warning(f"No MPN column found in {file_path}")
                        continue
                    
                    mpn_col = mpn_cols[0]
                    
                    # Convert DataFrame to list of dictionaries
                    records = []
                    for idx, row in df.iterrows():
                        mpn_value = row[mpn_col]
                        
                        if pd.isna(mpn_value) or str(mpn_value).strip() == '':
                            continue
                        
                        # Clean MPN value
                        mpn_clean = str(mpn_value).strip()
                        
                        # Get quantity value
                        qty_value = 0
                        if qty_col:
                            qty_value = excess_processor.clean_qty_value(row[qty_col])
                        
                        # Get target price value (with 12% markup)
                        target_price = None
                        if price_col:
                            target_price = excess_processor.clean_price_value(row[price_col])
                        
                        record = {
                            'MPN': mpn_clean,
                            'Excess_Filename': os.path.basename(file_path),
                            'Excess_QTY': qty_value,
                            'Target_Price': target_price,
                            'Manufacturer': '',  # Could be extracted if available
                            'sheet_name': sheet_name
                        }
                        records.append(record)
                    
                    # Insert into database
                    inserted = self.db_manager.insert_excess_inventory(records)
                    total_migrated += inserted
                    
                    # Log processing
                    self.db_manager.log_processing(
                        filename=os.path.basename(file_path),
                        file_type='excess',
                        status='success',
                        records_processed=len(records),
                        records_added=inserted,
                        records_skipped=len(records) - inserted
                    )
                    
                    logger.info(f"Migrated {inserted} records from {os.path.basename(file_path)}")
                    
                except Exception as e:
                    logger.error(f"Failed to migrate excess file {file_path}: {e}")
                    
                    # Log error
                    self.db_manager.log_processing(
                        filename=os.path.basename(file_path),
                        file_type='excess',
                        status='error',
                        error_message=str(e)
                    )
            
            logger.info(f"Successfully migrated {total_migrated} total excess inventory records")
            return total_migrated
            
        except Exception as e:
            logger.error(f"Failed to migrate excess inventory data: {e}")
            return 0
    
    def migrate_all_data(self) -> dict:
        """Migrate all available Excel data to database.
        
        Returns:
            Dictionary with migration results
        """
        results = {
            'hot_parts_migrated': 0,
            'excess_migrated': 0,
            'matches_migrated': 0,
            'total_migrated': 0
        }
        
        logger.info("Starting migration of all Excel data to database")
        
        # Migrate hot parts data
        results['hot_parts_migrated'] = self.migrate_hot_parts_data()
        
        # Migrate excess inventory data
        results['excess_migrated'] = self.migrate_excess_inventory_data()
        
        # Migrate matches data
        results['matches_migrated'] = self.migrate_matches_data()
        
        # Calculate total
        results['total_migrated'] = (results['hot_parts_migrated'] + 
                                   results['excess_migrated'] + 
                                   results['matches_migrated'])
        
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
            
            if stats['excess_inventory_count'] > 0:
                print(f"✅ Excess Inventory: {stats['excess_inventory_count']} records")
            else:
                print("❌ Excess Inventory: No records found")
            
            if stats['matches_count'] > 0:
                print(f"✅ Matches: {stats['matches_count']} records")
            else:
                print("❌ Matches: No records found")
            
            if stats['unique_hot_parts_mpns'] > 0:
                print(f"✅ Unique Hot Parts MPNs: {stats['unique_hot_parts_mpns']}")
            else:
                print("❌ Unique Hot Parts MPNs: No data")
            
            if stats['unique_excess_mpns'] > 0:
                print(f"✅ Unique Excess MPNs: {stats['unique_excess_mpns']}")
            else:
                print("❌ Unique Excess MPNs: No data")
            
            if stats['unique_match_mpns'] > 0:
                print(f"✅ Unique Match MPNs: {stats['unique_match_mpns']}")
            else:
                print("❌ Unique Match MPNs: No data")
            
            print(f"✅ Date Range: {stats.get('hot_parts_date_range', 'No data')}")
            print("="*50)
            
            # Check if we have meaningful data
            return (stats['hot_parts_count'] > 0 or stats['excess_inventory_count'] > 0 or stats['matches_count'] > 0)
            
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
    print(f"Excess Inventory Records: {results['excess_migrated']}")
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