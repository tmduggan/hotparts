#!/usr/bin/env python3
"""
Enhanced Automatic Hot Parts Excel File Processor
Handles duplicate detection and prevents redundant entries while allowing new datapoints
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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_auto_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedExcelFileHandler(FileSystemEventHandler):
    def __init__(self, unprocessed_dir, processed_dir, output_dir):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.parser = HotPartsParser()
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
    
    def create_data_hash(self, df):
        """Create a hash of the data to detect exact duplicates"""
        if df.empty:
            return None
        
        # Create a hash based on the data content (excluding any index)
        data_str = df.to_string(index=False)
        return hashlib.md5(data_str.encode()).hexdigest()
    
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
    
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        if (filename.endswith(('.xlsx', '.xls')) and 
            'Weekly Hot Parts List' in filename and
            filename not in self.processing_files):
            
            logger.info(f"New file detected: {filename}")
            self.process_file(file_path, filename)
    
    def on_moved(self, event):
        """Handle file moves (like drag and drop)"""
        if event.is_directory:
            return
            
        file_path = event.dest_path
        filename = os.path.basename(file_path)
        
        if (filename.endswith(('.xlsx', '.xls')) and 
            'Weekly Hot Parts List' in filename and
            filename not in self.processing_files):
            
            logger.info(f"File moved to unprocessed: {filename}")
            self.process_file(file_path, filename)
    
    def process_file(self, file_path, filename):
        """Process a single file with duplicate detection"""
        self.processing_files.add(filename)
        
        try:
            logger.info(f"Starting to process: {filename}")
            
            # Wait a moment to ensure file is fully written
            time.sleep(2)
            
            # Load existing master files
            self.load_existing_master_files()
            
            # Process the file
            self.parser.process_file(file_path)
            
            # Handle master data with duplicate detection
            if self.parser.master_data:
                logger.info(f"Processing {len(self.parser.master_data)} master data chunks")
                new_master_data = []
                
                for chunk in self.parser.master_data:
                    # Remove duplicates from this chunk
                    unique_chunk = self.detect_duplicates(chunk, self.master_data_cache, "master")
                    if not unique_chunk.empty:
                        new_master_data.append(unique_chunk)
                        # Update cache with new data
                        self.master_data_cache = pd.concat([self.master_data_cache, unique_chunk], ignore_index=True)
                
                # Replace parser data with deduplicated data
                self.parser.master_data = new_master_data
            
            # Handle pivot data with duplicate detection
            if self.parser.pivot_data:
                logger.info(f"Processing {len(self.parser.pivot_data)} pivot data chunks")
                new_pivot_data = []
                
                for chunk in self.parser.pivot_data:
                    # Remove duplicates from this chunk
                    unique_chunk = self.detect_duplicates(chunk, self.pivot_data_cache, "pivot")
                    if not unique_chunk.empty:
                        new_pivot_data.append(unique_chunk)
                        # Update cache with new data
                        self.pivot_data_cache = pd.concat([self.pivot_data_cache, unique_chunk], ignore_index=True)
                
                # Replace parser data with deduplicated data
                self.parser.pivot_data = new_pivot_data
            
            # Move file to processed directory
            processed_path = os.path.join(self.processed_dir, filename)
            shutil.move(file_path, processed_path)
            
            logger.info(f"Successfully processed and moved: {filename}")
            
            # Update master files
            self.update_master_files()
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            # Move file to processed directory with error suffix
            error_filename = f"{os.path.splitext(filename)[0]}_ERROR{os.path.splitext(filename)[1]}"
            error_path = os.path.join(self.processed_dir, error_filename)
            shutil.move(file_path, error_path)
            logger.error(f"Moved {filename} to {error_filename}")
        
        finally:
            self.processing_files.discard(filename)
    
    def update_master_files(self):
        """Update the master files with new data"""
        try:
            # Compile master files using the updated parser data
            self.parser.compile_master_files(self.output_dir)
            logger.info("Master files updated successfully")
            
            # Update our cache
            self.load_existing_master_files()
            
        except Exception as e:
            logger.error(f"Error updating master files: {str(e)}")
    
    def process_existing_files(self):
        """Process any existing files in the unprocessed directory"""
        logger.info("Checking for existing files in unprocessed directory...")
        
        for filename in os.listdir(self.unprocessed_dir):
            file_path = os.path.join(self.unprocessed_dir, filename)
            
            if (os.path.isfile(file_path) and 
                filename.endswith(('.xlsx', '.xls')) and 
                'Weekly Hot Parts List' in filename):
                
                logger.info(f"Processing existing file: {filename}")
                self.process_file(file_path, filename)

class EnhancedAutoProcessor:
    def __init__(self, unprocessed_dir="unprocessed", processed_dir="processed", output_dir="."):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.observer = Observer()
        
    def start(self):
        """Start the enhanced automatic file processor"""
        logger.info("Starting Enhanced Automatic Hot Parts File Processor")
        logger.info(f"Monitoring directory: {self.unprocessed_dir}")
        logger.info(f"Processed files directory: {self.processed_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("Features: Duplicate detection, intelligent data merging")
        logger.info("=" * 60)
        
        # Create directories if they don't exist
        os.makedirs(self.unprocessed_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up file handler
        event_handler = EnhancedExcelFileHandler(self.unprocessed_dir, self.processed_dir, self.output_dir)
        
        # Process any existing files first
        event_handler.process_existing_files()
        
        # Start watching for new files
        self.observer.schedule(event_handler, self.unprocessed_dir, recursive=False)
        self.observer.start()
        
        logger.info("Enhanced file watcher started. Drop Excel files into the 'unprocessed' directory.")
        logger.info("Duplicate detection enabled - only new data will be added to master files.")
        logger.info("Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the enhanced automatic file processor"""
        logger.info("Stopping enhanced file watcher...")
        self.observer.stop()
        self.observer.join()
        logger.info("Enhanced file watcher stopped.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Automatic Hot Parts Excel File Processor')
    parser.add_argument('--unprocessed', default='unprocessed', 
                       help='Directory to monitor for new files (default: unprocessed)')
    parser.add_argument('--processed', default='processed', 
                       help='Directory for processed files (default: processed)')
    parser.add_argument('--output', default='.', 
                       help='Directory for output files (default: current directory)')
    
    args = parser.parse_args()
    
    # Create and start the enhanced auto processor
    auto_processor = EnhancedAutoProcessor(args.unprocessed, args.processed, args.output)
    
    try:
        auto_processor.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        auto_processor.stop()

if __name__ == "__main__":
    main() 