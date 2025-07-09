#!/usr/bin/env python3
"""
Excess Cross-Reference Processor
Cross-references excess lists with master hot parts data to create matches
"""

import pandas as pd
import os
import re
from datetime import datetime

class ExcessCrossReference:
    def __init__(self, master_hot_parts_file="Master_Hot_Parts_Data.xlsx"):
        self.master_hot_parts_file = master_hot_parts_file
        self.master_data = None
        self.matches_data = []
        
    def load_master_data(self):
        """Load the master hot parts data"""
        try:
            self.master_data = pd.read_excel(self.master_hot_parts_file)
            print(f"Loaded master hot parts data: {len(self.master_data)} records")
            print(f"Columns: {list(self.master_data.columns)}")
        except Exception as e:
            print(f"Error loading master data: {e}")
            return False
        return True
    
    def clean_qty_value(self, qty_value):
        """Clean quantity value to ensure it's a number"""
        if pd.isna(qty_value):
            return 0
        
        # Convert to string and remove commas, spaces
        qty_str = str(qty_value).strip()
        qty_str = qty_str.replace(',', '').replace(' ', '')
        
        # Try to convert to number
        try:
            return int(float(qty_str))
        except (ValueError, TypeError):
            return 0
    
    def find_relevant_sheet(self, file_path):
        """Find the relevant sheet in an excess file (ignoring 'match' sheets)"""
        try:
            xl_file = pd.ExcelFile(file_path)
            
            for sheet_name in xl_file.sheet_names:
                # Skip sheets with 'match' or 'matching' in the name
                if any(keyword in sheet_name.lower() for keyword in ['match', 'matching']):
                    continue
                
                # Check if this sheet has MPN column
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                mpn_cols = [col for col in df.columns if 'mpn' in str(col).lower()]
                
                if mpn_cols:
                    return sheet_name, df
            
            return None, None
            
        except Exception as e:
            print(f"Error finding relevant sheet in {file_path}: {e}")
            return None, None
    
    def find_qty_column(self, df):
        """Find the quantity column in the dataframe"""
        qty_columns = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ['qty', 'quantity', 'stock']):
                qty_columns.append(col)
        
        # Prefer 'QTY' over 'Stock QTY' if both exist
        if 'QTY' in qty_columns:
            return 'QTY'
        elif 'Stock QTY' in qty_columns:
            return 'Stock QTY'
        elif qty_columns:
            return qty_columns[0]
        
        return None
    
    def process_excess_file(self, file_path):
        """Process a single excess file"""
        print(f"Processing excess file: {file_path}")
        
        # Find the relevant sheet
        sheet_name, df = self.find_relevant_sheet(file_path)
        if sheet_name is None:
            print(f"  ⚠️  No relevant sheet found in {file_path}")
            return
        
        print(f"  📋 Using sheet: {sheet_name}")
        print(f"  📊 Data shape: {df.shape}")
        
        # Find MPN and QTY columns
        mpn_cols = [col for col in df.columns if 'mpn' in str(col).lower()]
        qty_col = self.find_qty_column(df)
        
        if not mpn_cols:
            print(f"  ❌ No MPN column found in {file_path}")
            return
        
        mpn_col = mpn_cols[0]
        print(f"  🔍 MPN column: {mpn_col}")
        print(f"  📦 QTY column: {qty_col}")
        
        # Process each row
        matches_found = 0
        for idx, row in df.iterrows():
            mpn_value = row[mpn_col]
            
            if pd.isna(mpn_value) or str(mpn_value).strip() == '':
                continue
            
            # Clean MPN value
            mpn_clean = str(mpn_value).strip()
            
            # Find matches in master data
            master_matches = self.master_data[self.master_data['MPN'] == mpn_clean]
            
            if not master_matches.empty:
                # Get quantity value
                qty_value = 0
                if qty_col:
                    qty_value = self.clean_qty_value(row[qty_col])
                
                # Create match records for each master match
                for _, master_row in master_matches.iterrows():
                    match_record = {
                        'MPN': mpn_clean,
                        'Weekly_Hot_Parts_Date': master_row['Date'],
                        'Reqs_Count': master_row['Reqs_Count'],
                        'Manufacturer': master_row['Manufacturer'],
                        'Product_Class': master_row['Product_Class'],
                        'Description': master_row['Description'],
                        'Excess_Filename': os.path.basename(file_path),
                        'Excess_QTY': qty_value
                    }
                    self.matches_data.append(match_record)
                    matches_found += 1
        
        print(f"  ✅ Found {matches_found} matches in {file_path}")
    
    def find_excess_files(self, directory="."):
        """Find excess files in the directory"""
        excess_files = []
        for file in os.listdir(directory):
            if file.endswith('.xlsx') and ('Kelly Chen' in file or 'Vicky Zhang' in file):
                excess_files.append(file)
        
        return excess_files
    
    def process_all_excess_files(self, directory="."):
        """Process all excess files in the directory"""
        excess_files = self.find_excess_files(directory)
        
        if not excess_files:
            print("No excess files found")
            return
        
        print(f"Found {len(excess_files)} excess files:")
        for file in excess_files:
            print(f"  - {file}")
        print()
        
        for file in excess_files:
            file_path = os.path.join(directory, file)
            self.process_excess_file(file_path)
    
    def create_master_matches_file(self, output_file="Master_Matches_Data.xlsx"):
        """Create the master matches data file"""
        if not self.matches_data:
            print("No matches found to create master matches file")
            return
        
        # Create dataframe
        matches_df = pd.DataFrame(self.matches_data)
        
        # Remove duplicates (same MPN, date, and filename combination)
        matches_df = matches_df.drop_duplicates()
        
        # Sort by MPN and date
        matches_df = matches_df.sort_values(['MPN', 'Weekly_Hot_Parts_Date'])
        
        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            matches_df.to_excel(writer, sheet_name='Master_Matches', index=False)
        
        print(f"\n✅ Master Matches Data created: {output_file}")
        print(f"📊 Total matches: {len(matches_df)}")
        print(f"🔍 Unique MPNs matched: {matches_df['MPN'].nunique()}")
        print(f"📅 Date range: {matches_df['Weekly_Hot_Parts_Date'].min()} to {matches_df['Weekly_Hot_Parts_Date'].max()}")
        
        # Show sample of matches
        print(f"\n📋 Sample matches:")
        print(matches_df.head(10))
        
        return matches_df

def main():
    """Main function"""
    print("Excess Cross-Reference Processor")
    print("=" * 50)
    
    # Create processor
    processor = ExcessCrossReference()
    
    # Load master data
    if not processor.load_master_data():
        print("❌ Failed to load master data")
        return
    
    # Process all excess files
    processor.process_all_excess_files()
    
    # Create master matches file
    processor.create_master_matches_file()
    
    print("\n🎉 Cross-reference processing complete!")

if __name__ == "__main__":
    main() 