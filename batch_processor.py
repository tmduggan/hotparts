#!/usr/bin/env python3
"""
Batch processor for multiple Hot Parts Excel files
Handles multiple files, provides progress tracking, and error reporting
"""

import os
import sys
import pandas as pd
from datetime import datetime
from hot_parts_parser import HotPartsParser

class BatchProcessor:
    def __init__(self, input_dir=".", output_dir=".", file_pattern="Weekly Hot Parts List"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.file_pattern = file_pattern
        self.processed_files = []
        self.failed_files = []
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_records': 0,
            'total_pivot_records': 0
        }
    
    def find_excel_files(self):
        """Find all Excel files matching the pattern"""
        excel_files = []
        for file in os.listdir(self.input_dir):
            if (file.endswith(('.xlsx', '.xls')) and 
                self.file_pattern in file):
                excel_files.append(file)
        return sorted(excel_files)
    
    def process_batch(self):
        """Process all Excel files in batch"""
        print(f"Batch Processing Hot Parts Excel Files")
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print("=" * 60)
        
        # Find all files
        excel_files = self.find_excel_files()
        self.stats['total_files'] = len(excel_files)
        
        if not excel_files:
            print("No Excel files found matching the pattern!")
            return
        
        print(f"Found {len(excel_files)} files to process:")
        for file in excel_files:
            print(f"  - {file}")
        print()
        
        # Process each file
        for i, file in enumerate(excel_files, 1):
            print(f"Processing file {i}/{len(excel_files)}: {file}")
            
            try:
                # Create parser for this file
                parser = HotPartsParser(self.input_dir)
                file_path = os.path.join(self.input_dir, file)
                
                # Process the file
                parser.process_file(file_path)
                
                # Add to master data
                if parser.master_data:
                    self.stats['total_records'] += sum(len(df) for df in parser.master_data)
                if parser.pivot_data:
                    self.stats['total_pivot_records'] += sum(len(df) for df in parser.pivot_data)
                
                self.processed_files.append(file)
                self.stats['processed_files'] += 1
                
                print(f"  ✓ Successfully processed")
                
            except Exception as e:
                print(f"  ✗ Failed to process: {str(e)}")
                self.failed_files.append((file, str(e)))
                self.stats['failed_files'] += 1
        
        # Compile final master files
        print("\nCompiling master files...")
        self.compile_final_master_files()
        
        # Print summary
        self.print_summary()
    
    def compile_final_master_files(self):
        """Compile all processed data into final master files"""
        all_master_data = []
        all_pivot_data = []
        
        # Collect data from all processed files
        for file in self.processed_files:
            try:
                parser = HotPartsParser(self.input_dir)
                file_path = os.path.join(self.input_dir, file)
                parser.process_file(file_path)
                
                if parser.master_data:
                    all_master_data.extend(parser.master_data)
                if parser.pivot_data:
                    all_pivot_data.extend(parser.pivot_data)
                    
            except Exception as e:
                print(f"Error re-processing {file}: {e}")
        
        # Create final master files
        if all_master_data:
            master_df = pd.concat(all_master_data, ignore_index=True)
            master_df = master_df.drop_duplicates()
            master_df = master_df.sort_values(['MPN', 'Date'])
            
            master_file = os.path.join(self.output_dir, "Master_Hot_Parts_Data.xlsx")
            with pd.ExcelWriter(master_file, engine='openpyxl') as writer:
                master_df.to_excel(writer, sheet_name='Master_Data', index=False)
            
            print(f"✓ Master data compiled: {master_file}")
            print(f"  Records: {len(master_df)}")
        
        if all_pivot_data:
            pivot_df = pd.concat(all_pivot_data, ignore_index=True)
            pivot_df = pivot_df.drop_duplicates()
            pivot_df = pivot_df.sort_values(['MPN', 'Date'])
            
            pivot_file = os.path.join(self.output_dir, "Master_Pivot_Data.xlsx")
            with pd.ExcelWriter(pivot_file, engine='openpyxl') as writer:
                pivot_df.to_excel(writer, sheet_name='Pivot_Data', index=False)
            
            print(f"✓ Pivot data compiled: {pivot_file}")
            print(f"  Records: {len(pivot_df)}")
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "=" * 60)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total files found: {self.stats['total_files']}")
        print(f"Successfully processed: {self.stats['processed_files']}")
        print(f"Failed to process: {self.stats['failed_files']}")
        print(f"Total master records: {self.stats['total_records']}")
        print(f"Total pivot records: {self.stats['total_pivot_records']}")
        
        if self.failed_files:
            print("\nFailed files:")
            for file, error in self.failed_files:
                print(f"  - {file}: {error}")
        
        print(f"\nProcessing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    # Parse command line arguments
    input_dir = "."
    output_dir = "."
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Run batch processor
    processor = BatchProcessor(input_dir, output_dir)
    processor.process_batch()

if __name__ == "__main__":
    main() 