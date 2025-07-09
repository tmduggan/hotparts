#!/usr/bin/env python3
"""
Excess Auto Processor
Automatically processes excess files dropped into unprocessed_XS directory
Cross-references with master hot parts data and updates Master_Matches_Data.xlsx
"""

import os
import time
import shutil
import logging
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from enhanced_excess_processor import EnhancedExcessProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('excess_auto_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExcessFileHandler(FileSystemEventHandler):
    def __init__(self, unprocessed_dir, processed_dir, output_dir):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.processor = EnhancedExcessProcessor(
            master_hot_parts_file=os.path.join(output_dir, "Master_Hot_Parts_Data.xlsx"),
            output_file=os.path.join(output_dir, "Master_Matches_Data.xlsx")
        )
        
        # Load master data once at startup
        if not self.processor.load_master_data():
            logger.error("Failed to load master hot parts data")
            raise RuntimeError("Master hot parts data not available")
        
        logger.info("Excess file handler initialized")
    
    def is_excess_file(self, filename):
        """Check if file is an excess file (contains Kelly Chen, Vicky Zhang, Micron stock, or BCM Excess)"""
        return (filename.endswith('.xlsx') and 
                ('Kelly Chen' in filename or 
                 'Vicky Zhang' in filename or
                 'Micron stock' in filename or
                 'BCM Excess' in filename))
    
    def process_excess_file(self, file_path, filename):
        """Process a single excess file"""
        try:
            logger.info(f"Processing excess file: {filename}")
            
            # Process the file
            self.processor.process_excess_file(file_path)
            
            # Update master matches file
            matches_df = self.processor.update_master_matches()
            
            if matches_df is not None:
                logger.info(f"Successfully processed {filename}")
                logger.info(f"Updated Master_Matches_Data.xlsx with {len(matches_df)} total matches")
                
                # Move file to processed directory
                processed_path = os.path.join(self.processed_dir, filename)
                shutil.move(file_path, processed_path)
                logger.info(f"Moved {filename} to processed directory")
            else:
                logger.error(f"Failed to update master matches for {filename}")
                # Move to processed with error suffix
                error_filename = filename.replace('.xlsx', '_ERROR.xlsx')
                error_path = os.path.join(self.processed_dir, error_filename)
                shutil.move(file_path, error_path)
                logger.info(f"Moved {filename} to processed directory as {error_filename}")
                
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            # Move to processed with error suffix
            error_filename = filename.replace('.xlsx', '_ERROR.xlsx')
            error_path = os.path.join(self.processed_dir, error_filename)
            try:
                shutil.move(file_path, error_path)
                logger.info(f"Moved {filename} to processed directory as {error_filename}")
            except Exception as move_error:
                logger.error(f"Failed to move {filename} to error directory: {move_error}")
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        # Check if it's an excess file
        if not self.is_excess_file(filename):
            logger.info(f"Ignoring non-excess file: {filename}")
            return
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Check if file still exists
        if not os.path.exists(file_path):
            logger.warning(f"File {filename} was removed before processing")
            return
        
        # Process the file
        self.process_excess_file(file_path, filename)
    
    def on_moved(self, event):
        """Handle file move events (when files are moved into the directory)"""
        if event.is_directory:
            return
        
        dest_path = event.dest_path
        filename = os.path.basename(dest_path)
        
        # Check if it's an excess file
        if not self.is_excess_file(filename):
            logger.info(f"Ignoring non-excess file: {filename}")
            return
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Check if file still exists
        if not os.path.exists(dest_path):
            logger.warning(f"File {filename} was removed before processing")
            return
        
        # Process the file
        self.process_excess_file(dest_path, filename)

def check_existing_files(unprocessed_dir, handler):
    """Check for existing files in unprocessed directory"""
    logger.info("Checking for existing files in unprocessed directory...")
    
    if not os.path.exists(unprocessed_dir):
        logger.warning(f"Unprocessed directory does not exist: {unprocessed_dir}")
        return
    
    files = os.listdir(unprocessed_dir)
    excess_files = [f for f in files if handler.is_excess_file(f)]
    
    if excess_files:
        logger.info(f"Found {len(excess_files)} existing excess files to process:")
        for file in excess_files:
            logger.info(f"  - {file}")
        
        for file in excess_files:
            file_path = os.path.join(unprocessed_dir, file)
            handler.process_excess_file(file_path, file)
    else:
        logger.info("No existing excess files found")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Excess Auto Processor')
    parser.add_argument('--unprocessed', default='unprocessed_XS', 
                       help='Directory to monitor for new excess files')
    parser.add_argument('--processed', default='processed_XS', 
                       help='Directory to move processed files')
    parser.add_argument('--output', default='.', 
                       help='Output directory for master files')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    os.makedirs(args.unprocessed, exist_ok=True)
    os.makedirs(args.processed, exist_ok=True)
    
    print("Excess Auto Processor")
    print("=" * 50)
    print(f"Monitoring directory: {args.unprocessed}")
    print(f"Processed files directory: {args.processed}")
    print(f"Output directory: {args.output}")
    print("Features: Automatic excess file processing, cross-referencing")
    print("=" * 50)
    
    # Create file handler
    try:
        handler = ExcessFileHandler(args.unprocessed, args.processed, args.output)
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        return
    
    # Check for existing files
    check_existing_files(args.unprocessed, handler)
    
    # Set up file watcher
    observer = Observer()
    observer.schedule(handler, args.unprocessed, recursive=False)
    observer.start()
    
    logger.info("Excess file watcher started. Drop excess files into the 'unprocessed_XS' directory.")
    logger.info("Excess files should contain 'Kelly Chen' or 'Vicky Zhang' in the filename.")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping excess auto processor...")
        observer.stop()
    
    observer.join()
    logger.info("Excess auto processor stopped")

if __name__ == "__main__":
    main() 