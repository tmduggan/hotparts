#!/usr/bin/env python3
"""
Unified Automatic File Processor
Handles both hot parts and excess files in unified directories with simplified detection
"""

import os
import time
import shutil
import logging
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hot_parts_parser import HotPartsParser
from enhanced_excess_processor import EnhancedExcessProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_auto_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedFileHandler(FileSystemEventHandler):
    def __init__(self, unprocessed_dir, processed_dir, output_dir):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.hot_parts_parser = HotPartsParser()
        self.excess_processor = EnhancedExcessProcessor()
        self.processing_files = set()
        self.master_data_cache = None
        self.pivot_data_cache = None
        
    def load_existing_master_files(self):
        """Load existing master files to check for duplicates"""
        try:
            master_file = os.path.join(self.output_dir, "Master_Hot_Parts_Data.xlsx")
            pivot_file = os.path.join(self.output_dir, "Master_Pivot_Data.xlsx")
            
            if os.path.exists(master_file):
                self.master_data_cache = pd.read_excel(master_file)
                logger.info(f"Loaded existing master data: {len(self.master_data_cache)} records")
            else:
                self.master_data_cache = pd.DataFrame()
                logger.info("No existing master data found")
                
            if os.path.exists(pivot_file):
                self.pivot_data_cache = pd.read_excel(pivot_file)
                logger.info(f"Loaded existing pivot data: {len(self.pivot_data_cache)} records")
            else:
                self.pivot_data_cache = pd.DataFrame()
                logger.info("No existing pivot data found")
                
        except Exception as e:
            logger.error(f"Error loading existing master files: {e}")
            self.master_data_cache = pd.DataFrame()
            self.pivot_data_cache = pd.DataFrame()
    
    def detect_duplicates(self, new_data, existing_data, data_type="master"):
        """Detect and remove duplicates from new data"""
        if existing_data.empty or new_data.empty:
            return new_data
        
        # For master data, check MPN + Date combinations
        if data_type == "master":
            # Create composite key for duplicate detection
            new_data['composite_key'] = new_data['MPN'] + '|' + new_data['Date']
            existing_data['composite_key'] = existing_data['MPN'] + '|' + existing_data['Date']
            
            # Find duplicates
            existing_keys = set(existing_data['composite_key'].values)
            new_data['is_duplicate'] = new_data['composite_key'].isin(existing_keys)
            
            # Remove duplicates
            unique_data = new_data[~new_data['is_duplicate']].copy()
            duplicates = new_data[new_data['is_duplicate']].copy()
            
            # Clean up temporary columns
            unique_data = unique_data.drop(['composite_key', 'is_duplicate'], axis=1)
            duplicates = duplicates.drop(['composite_key', 'is_duplicate'], axis=1)
            
            if not duplicates.empty:
                logger.info(f"Removed {len(duplicates)} duplicate {data_type} records")
                logger.info(f"Sample duplicates: {duplicates[['MPN', 'Date']].head(3).to_dict('records')}")
            
            return unique_data
        
        # For pivot data, check MPN + Date combinations
        elif data_type == "pivot":
            new_data['composite_key'] = new_data['MPN'] + '|' + new_data['Date']
            existing_data['composite_key'] = existing_data['MPN'] + '|' + existing_data['Date']
            
            existing_keys = set(existing_data['composite_key'].values)
            new_data['is_duplicate'] = new_data['composite_key'].isin(existing_keys)
            
            unique_data = new_data[~new_data['is_duplicate']].copy()
            duplicates = new_data[new_data['is_duplicate']].copy()
            
            unique_data = unique_data.drop(['composite_key', 'is_duplicate'], axis=1)
            duplicates = duplicates.drop(['composite_key', 'is_duplicate'], axis=1)
            
            if not duplicates.empty:
                logger.info(f"Removed {len(duplicates)} duplicate {data_type} records")
            
            return unique_data
        
        return new_data
    
    def is_hot_parts_file(self, filename):
        """Check if file is a hot parts file based on filename"""
        return 'Weekly Hot Parts' in filename
    
    def is_excess_file(self, filename):
        """Check if file is an excess file based on filename"""
        return not self.is_hot_parts_file(filename)
    
    def create_error_file(self, file_path, error_message):
        """Create an error file with failure details"""
        error_file_path = f"{file_path}.error"
        try:
            with open(error_file_path, 'w') as f:
                f.write(f"Processing failed for: {os.path.basename(file_path)}\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {error_message}\n")
            logger.info(f"Created error file: {error_file_path}")
        except Exception as e:
            logger.error(f"Failed to create error file: {e}")
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        if filename in self.processing_files:
            return
        
        if filename.endswith(('.xlsx', '.xls')):
            logger.info(f"File moved to unprocessed: {filename}")
            time.sleep(1)  # Wait for file to be fully written
            self.process_file(event.src_path, filename)
    
    def on_moved(self, event):
        """Handle file move events (drag & drop)"""
        if event.is_directory:
            return
        
        filename = os.path.basename(event.dest_path)
        if filename in self.processing_files:
            return
        
        if filename.endswith(('.xlsx', '.xls')):
            logger.info(f"File moved to unprocessed: {filename}")
            time.sleep(1)  # Wait for file to be fully written
            self.process_file(event.dest_path, filename)
    
    def process_file(self, file_path, filename):
        """Process a single file with unified handling"""
        self.processing_files.add(filename)
        
        try:
            logger.info(f"Starting to process: {filename}")
            
            # Wait a moment to ensure file is fully written
            time.sleep(2)
            
            # Determine file type and process accordingly
            if self.is_hot_parts_file(filename):
                logger.info(f"Processing as hot parts file: {filename}")
                self.process_hot_parts_file(file_path, filename)
            elif self.is_excess_file(filename):
                logger.info(f"Processing as excess file: {filename}")
                self.process_excess_file(file_path, filename)
            else:
                raise ValueError(f"Unknown file type: {filename}")
            
        except Exception as e:
            error_msg = f"Error processing {filename}: {str(e)}"
            logger.error(error_msg)
            
            # Create error file in unprocessed directory
            self.create_error_file(file_path, error_msg)
            
            # Keep file in unprocessed directory (don't move to processed)
            logger.info(f"File {filename} kept in unprocessed directory with error file")
        
        finally:
            self.processing_files.discard(filename)
    
    def process_hot_parts_file(self, file_path, filename):
        """Process hot parts file with duplicate detection and database storage"""
        # Load existing master files
        self.load_existing_master_files()
        
        # Process the file
        self.hot_parts_parser.process_file(file_path)
        
        # Handle master data with duplicate detection
        if self.hot_parts_parser.master_data:
            logger.info(f"Processing {len(self.hot_parts_parser.master_data)} master data chunks")
            new_master_data = []
            
            for chunk in self.hot_parts_parser.master_data:
                # Remove duplicates from this chunk
                unique_chunk = self.detect_duplicates(chunk, self.master_data_cache, "master")
                if not unique_chunk.empty:
                    new_master_data.append(unique_chunk)
                    # Update cache with new data
                    self.master_data_cache = pd.concat([self.master_data_cache, unique_chunk], ignore_index=True)
            
            # Replace parser data with deduplicated data
            self.hot_parts_parser.master_data = new_master_data
        
        # Handle pivot data with duplicate detection
        if self.hot_parts_parser.pivot_data:
            logger.info(f"Processing {len(self.hot_parts_parser.pivot_data)} pivot data chunks")
            new_pivot_data = []
            
            for chunk in self.hot_parts_parser.pivot_data:
                # Remove duplicates from this chunk
                unique_chunk = self.detect_duplicates(chunk, self.pivot_data_cache, "pivot")
                if not unique_chunk.empty:
                    new_pivot_data.append(unique_chunk)
                    # Update cache with new data
                    self.pivot_data_cache = pd.concat([self.pivot_data_cache, unique_chunk], ignore_index=True)
            
            # Replace parser data with deduplicated data
            self.hot_parts_parser.pivot_data = new_pivot_data
        
        # Save hot parts data to database
        self.save_hot_parts_to_database(filename)
        
        # Move file to processed directory
        processed_path = os.path.join(self.processed_dir, filename)
        shutil.move(file_path, processed_path)
        
        logger.info(f"Successfully processed and moved hot parts file: {filename}")
        
        # Update master files
        self.update_hot_parts_master_files()
    
    def save_hot_parts_to_database(self, filename):
        """Save hot parts data to database"""
        try:
            from database_manager import DatabaseManager
            
            # Initialize database manager
            db_manager = DatabaseManager()
            
            # Convert parser data to database format
            records = []
            
            # Process master data
            if self.hot_parts_parser.master_data:
                for chunk in self.hot_parts_parser.master_data:
                    for _, row in chunk.iterrows():
                        record = {
                            'MPN': str(row.get('MPN', '')),
                            'Date': str(row.get('Date', '')),
                            'Reqs_Count': int(row.get('Reqs_Count', 0)) if pd.notna(row.get('Reqs_Count')) else 0,
                            'Manufacturer': str(row.get('Manufacturer', '')),
                            'Product_Class': str(row.get('Product_Class', '')),
                            'Description': str(row.get('Description', '')),
                            'source_file': filename
                        }
                        records.append(record)
            
            # Insert into database
            if records:
                inserted = db_manager.insert_hot_parts(records)
                
                # Log processing
                db_manager.log_processing(
                    filename=filename,
                    file_type='hot_parts',
                    status='success',
                    records_processed=len(records),
                    records_added=inserted,
                    records_skipped=len(records) - inserted
                )
                
                logger.info(f"Saved {inserted} hot parts records to database from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save hot parts data to database: {e}")
            # Don't raise - this is not critical for file processing
    
    def process_excess_file(self, file_path, filename):
        """Process excess file with simplified validation and database storage"""
        try:
            # Process the excess file
            self.excess_processor.process_excess_file(file_path)
            
            # Save excess data to database
            self.save_excess_to_database(file_path, filename)
            
            # Move file to processed directory
            processed_path = os.path.join(self.processed_dir, filename)
            shutil.move(file_path, processed_path)
            
            logger.info(f"Successfully processed and moved excess file: {filename}")
            
        except Exception as e:
            # Re-raise to be handled by the main error handler
            raise e
    
    def save_excess_to_database(self, file_path, filename):
        """Save excess inventory data to database"""
        try:
            from database_manager import DatabaseManager
            
            # Initialize database manager
            db_manager = DatabaseManager()
            
            # Find the relevant sheet
            sheet_name, df = self.excess_processor.find_relevant_sheet(file_path)
            if sheet_name is None:
                logger.warning(f"No relevant sheet found in {file_path}")
                return
            
            # Find MPN, QTY, and Price columns
            mpn_cols = [col for col in df.columns if 'mpn' in str(col).lower()]
            qty_col = self.excess_processor.find_qty_column(df)
            price_col = self.excess_processor.find_price_column(df)
            
            if not mpn_cols:
                logger.warning(f"No MPN column found in {file_path}")
                return
            
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
                    qty_value = self.excess_processor.clean_qty_value(row[qty_col])
                
                # Get target price value (with 12% markup)
                target_price = None
                if price_col:
                    target_price = self.excess_processor.clean_price_value(row[price_col])
                
                record = {
                    'MPN': mpn_clean,
                    'Excess_Filename': filename,
                    'Excess_QTY': qty_value,
                    'Target_Price': target_price,
                    'Manufacturer': '',  # Could be extracted if available
                    'sheet_name': sheet_name
                }
                records.append(record)
            
            # Insert into database
            inserted = db_manager.insert_excess_inventory(records)
            
            # Log processing
            db_manager.log_processing(
                filename=filename,
                file_type='excess',
                status='success',
                records_processed=len(records),
                records_added=inserted,
                records_skipped=len(records) - inserted
            )
            
            logger.info(f"Saved {inserted} excess records to database from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save excess data to database: {e}")
            # Don't raise - this is not critical for file processing
    
    def update_hot_parts_master_files(self):
        """Update the hot parts master files with new data"""
        try:
            # Compile master files using the updated parser data
            self.hot_parts_parser.compile_master_files(self.output_dir)
            logger.info("Hot parts master files updated successfully")
            
            # Update our cache
            self.load_existing_master_files()
            
        except Exception as e:
            logger.error(f"Error updating hot parts master files: {str(e)}")
    
    def process_existing_files(self):
        """Process any existing files in the unprocessed directory"""
        logger.info("Checking for existing files in unprocessed directory...")
        
        for filename in os.listdir(self.unprocessed_dir):
            file_path = os.path.join(self.unprocessed_dir, filename)
            
            if (os.path.isfile(file_path) and 
                filename.endswith(('.xlsx', '.xls')) and
                not filename.endswith('.error')):
                
                logger.info(f"Processing existing file: {filename}")
                self.process_file(file_path, filename)

class UnifiedAutoProcessor:
    def __init__(self, unprocessed_dir="unprocessed", processed_dir="processed", output_dir="."):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.observer = None
    
    def start(self):
        """Start the unified file watcher"""
        logger.info(f"Starting unified file watcher...")
        logger.info(f"Monitoring directory: {self.unprocessed_dir}")
        logger.info(f"Processed files directory: {self.processed_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Create directories if they don't exist
        os.makedirs(self.unprocessed_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Create event handler
        event_handler = UnifiedFileHandler(self.unprocessed_dir, self.processed_dir, self.output_dir)
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(event_handler, self.unprocessed_dir, recursive=False)
        
        # Start observer
        self.observer.start()
        
        # Process any existing files
        event_handler.process_existing_files()
        
        logger.info("Unified file watcher started. Drop Excel files into the 'unprocessed' directory.")
        logger.info("File type detection:")
        logger.info("  - Contains 'Weekly Hot Parts' → Process as hot parts file")
        logger.info("  - Does NOT contain 'Weekly Hot Parts' → Process as excess file")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping unified file watcher...")
            self.stop()
    
    def stop(self):
        """Stop the unified file watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Unified file watcher stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Auto Processor for Hot Parts and Excess Files")
    parser.add_argument('--unprocessed', default='unprocessed',
                       help='Directory to monitor for new files (default: unprocessed)')
    parser.add_argument('--processed', default='processed',
                       help='Directory for processed files (default: processed)')
    parser.add_argument('--output', default='.',
                       help='Directory for output files (default: current directory)')
    
    args = parser.parse_args()
    
    auto_processor = UnifiedAutoProcessor(args.unprocessed, args.processed, args.output)
    auto_processor.start()

if __name__ == "__main__":
    main() 