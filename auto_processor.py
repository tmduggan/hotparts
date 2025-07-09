#!/usr/bin/env python3
"""
Automatic Hot Parts Excel File Processor
Monitors the 'unprocessed' directory and automatically processes files when dropped in
"""

import os
import time
import shutil
import logging
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
        logging.FileHandler('auto_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExcelFileHandler(FileSystemEventHandler):
    def __init__(self, unprocessed_dir, processed_dir, output_dir):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.parser = HotPartsParser()
        self.processing_files = set()  # Track files being processed
        
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        # Check if it's an Excel file with the right pattern
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
        
        # Check if it's an Excel file with the right pattern
        if (filename.endswith(('.xlsx', '.xls')) and 
            'Weekly Hot Parts List' in filename and
            filename not in self.processing_files):
            
            logger.info(f"File moved to unprocessed: {filename}")
            self.process_file(file_path, filename)
    
    def process_file(self, file_path, filename):
        """Process a single file"""
        self.processing_files.add(filename)
        
        try:
            logger.info(f"Starting to process: {filename}")
            
            # Wait a moment to ensure file is fully written
            time.sleep(2)
            
            # Process the file
            self.parser.process_file(file_path)
            
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
            # Compile master files
            self.parser.compile_master_files(self.output_dir)
            logger.info("Master files updated successfully")
            
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

class AutoProcessor:
    def __init__(self, unprocessed_dir="unprocessed", processed_dir="processed", output_dir="."):
        self.unprocessed_dir = unprocessed_dir
        self.processed_dir = processed_dir
        self.output_dir = output_dir
        self.observer = Observer()
        
    def start(self):
        """Start the automatic file processor"""
        logger.info("Starting Automatic Hot Parts File Processor")
        logger.info(f"Monitoring directory: {self.unprocessed_dir}")
        logger.info(f"Processed files directory: {self.processed_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 60)
        
        # Create directories if they don't exist
        os.makedirs(self.unprocessed_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up file handler
        event_handler = ExcelFileHandler(self.unprocessed_dir, self.processed_dir, self.output_dir)
        
        # Process any existing files first
        event_handler.process_existing_files()
        
        # Start watching for new files
        self.observer.schedule(event_handler, self.unprocessed_dir, recursive=False)
        self.observer.start()
        
        logger.info("File watcher started. Drop Excel files into the 'unprocessed' directory.")
        logger.info("Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the automatic file processor"""
        logger.info("Stopping file watcher...")
        self.observer.stop()
        self.observer.join()
        logger.info("File watcher stopped.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatic Hot Parts Excel File Processor')
    parser.add_argument('--unprocessed', default='unprocessed', 
                       help='Directory to monitor for new files (default: unprocessed)')
    parser.add_argument('--processed', default='processed', 
                       help='Directory for processed files (default: processed)')
    parser.add_argument('--output', default='.', 
                       help='Directory for output files (default: current directory)')
    
    args = parser.parse_args()
    
    # Create and start the auto processor
    auto_processor = AutoProcessor(args.unprocessed, args.processed, args.output)
    
    try:
        auto_processor.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        auto_processor.stop()

if __name__ == "__main__":
    main() 