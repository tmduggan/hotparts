#!/usr/bin/env python3
"""
Enhanced Excess Cross-Reference Processor
Can be integrated with the auto processor system for automatic cross-referencing
"""

import pandas as pd
import os
import re
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('excess_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedExcessProcessor:
    def __init__(self, master_hot_parts_file="Master_Hot_Parts_Data.xlsx", 
                 output_file="Master_Matches_Data.xlsx"):
        self.master_hot_parts_file = master_hot_parts_file
        self.output_file = output_file
        self.master_data = None
        self.matches_data = []
        self.processed_files = set()
        
    def load_master_data(self):
        """Load the master hot parts data"""
        try:
            if os.path.exists(self.master_hot_parts_file):
                self.master_data = pd.read_excel(self.master_hot_parts_file)
                logger.info(f"Loaded master hot parts data: {len(self.master_data)} records")
                return True
            else:
                logger.warning(f"Master hot parts file not found: {self.master_hot_parts_file}")
                return False
        except Exception as e:
            logger.error(f"Error loading master data: {e}")
            return False
    
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
            filename = os.path.basename(file_path)
            
            for sheet_name in xl_file.sheet_names:
                # Skip sheets with 'match' or 'matching' in the name
                if any(keyword in sheet_name.lower() for keyword in ['match', 'matching']):
                    logger.info(f"Skipping sheet '{sheet_name}' - contains 'match' or 'matching'")
                    continue
                
                # Skip 'Global' tab for Micron files
                if 'Micron stock' in filename and sheet_name.lower() == 'global':
                    logger.info(f"Skipping sheet '{sheet_name}' - Global tab for Micron file")
                    continue
                
                # Check if this sheet has MPN column
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                mpn_cols = [col for col in df.columns if 'mpn' in str(col).lower()]
                
                if mpn_cols:
                    return sheet_name, df
            
            return None, None
            
        except Exception as e:
            logger.error(f"Error finding relevant sheet in {file_path}: {e}")
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
    
    def find_price_column(self, df):
        """Find the price column in the dataframe"""
        price_columns = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ['price', 'target', 'cost']):
                price_columns.append(col)
        
        # Prefer 'Price' over other variations
        if 'Price' in price_columns:
            return 'Price'
        elif price_columns:
            return price_columns[0]
        
        return None
    
    def clean_price_value(self, price_value):
        """Clean price value and apply 12% markup"""
        if pd.isna(price_value):
            return None
        
        # Convert to string and remove any formatting
        price_str = str(price_value).strip()
        price_str = price_str.replace('$', '').replace(',', '').replace(' ', '')
        
        # Try to convert to number
        try:
            base_price = float(price_str)
            # Apply 12% markup
            target_price = base_price * 1.12
            return round(target_price, 4)  # Round to 4 decimal places
        except (ValueError, TypeError):
            return None
    
    def process_excess_file(self, file_path):
        """Process a single excess file"""
        if file_path in self.processed_files:
            logger.info(f"File already processed: {file_path}")
            return
        
        logger.info(f"Processing excess file: {file_path}")
        
        # Find the relevant sheet
        sheet_name, df = self.find_relevant_sheet(file_path)
        if sheet_name is None:
            logger.warning(f"No relevant sheet found in {file_path}")
            return
        
        logger.info(f"Using sheet: {sheet_name} (shape: {df.shape})")
        
        # Find MPN, QTY, and Price columns
        mpn_cols = [col for col in df.columns if 'mpn' in str(col).lower()]
        qty_col = self.find_qty_column(df)
        price_col = self.find_price_column(df)
        
        if not mpn_cols:
            logger.error(f"No MPN column found in {file_path}")
            return
        
        mpn_col = mpn_cols[0]
        logger.info(f"MPN column: {mpn_col}, QTY column: {qty_col}, Price column: {price_col}")
        
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
                
                # Get target price value (with 12% markup)
                target_price = None
                if price_col:
                    target_price = self.clean_price_value(row[price_col])
                
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
                        'Excess_QTY': qty_value,
                        'Target_Price': target_price
                    }
                    self.matches_data.append(match_record)
                    matches_found += 1
        
        logger.info(f"Found {matches_found} matches in {file_path}")
        self.processed_files.add(file_path)
    
    def find_excess_files(self, directory="."):
        """Find excess files in the directory"""
        excess_files = []
        for file in os.listdir(directory):
            if file.endswith('.xlsx') and (
                'Kelly Chen' in file or 
                'Vicky Zhang' in file or
                'Micron stock' in file or
                'BCM Excess' in file
            ):
                excess_files.append(file)
        
        return excess_files
    
    def process_all_excess_files(self, directory="."):
        """Process all excess files in the directory"""
        excess_files = self.find_excess_files(directory)
        
        if not excess_files:
            logger.info("No excess files found")
            return
        
        logger.info(f"Found {len(excess_files)} excess files")
        
        for file in excess_files:
            file_path = os.path.join(directory, file)
            self.process_excess_file(file_path)
    
    def create_master_matches_file(self):
        """Create the master matches data file"""
        if not self.matches_data:
            logger.info("No matches found to create master matches file")
            return None
        
        # Create dataframe
        matches_df = pd.DataFrame(self.matches_data)
        
        # Remove duplicates (same MPN, date, and filename combination)
        matches_df = matches_df.drop_duplicates()
        
        # Sort by MPN and date
        matches_df = matches_df.sort_values(['MPN', 'Weekly_Hot_Parts_Date'])
        
        # Save to Excel
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            matches_df.to_excel(writer, sheet_name='Master_Matches', index=False)
        
        logger.info(f"Master Matches Data created: {self.output_file}")
        logger.info(f"Total matches: {len(matches_df)}")
        logger.info(f"Unique MPNs matched: {matches_df['MPN'].nunique()}")
        
        return matches_df
    
    def update_master_matches(self):
        """Update the master matches file with new data"""
        try:
            # Load existing matches if file exists
            existing_matches = []
            if os.path.exists(self.output_file):
                existing_df = pd.read_excel(self.output_file)
                existing_matches = existing_df.to_dict('records')
                logger.info(f"Loaded existing matches: {len(existing_matches)} records")
            
            # Combine existing and new matches
            all_matches = existing_matches + self.matches_data
            
            if not all_matches:
                logger.info("No matches to save")
                return None
            
            # Create dataframe and remove duplicates
            matches_df = pd.DataFrame(all_matches)
            
            # Ensure Target_Price column exists (for backward compatibility)
            if 'Target_Price' not in matches_df.columns:
                matches_df['Target_Price'] = None
            
            matches_df = matches_df.drop_duplicates()
            matches_df = matches_df.sort_values(['MPN', 'Weekly_Hot_Parts_Date'])
            
            # Save to Excel
            with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
                matches_df.to_excel(writer, sheet_name='Master_Matches', index=False)
            
            logger.info(f"Updated Master Matches Data: {self.output_file}")
            logger.info(f"Total matches: {len(matches_df)}")
            logger.info(f"Unique MPNs matched: {matches_df['MPN'].nunique()}")
            
            return matches_df
            
        except Exception as e:
            logger.error(f"Error updating master matches: {e}")
            return None

def main():
    """Main function"""
    print("Enhanced Excess Cross-Reference Processor")
    print("=" * 50)
    
    # Create processor
    processor = EnhancedExcessProcessor()
    
    # Load master data
    if not processor.load_master_data():
        print("❌ Failed to load master data")
        return
    
    # Process all excess files
    processor.process_all_excess_files()
    
    # Create master matches file
    processor.create_master_matches_file()
    
    print("\n🎉 Enhanced cross-reference processing complete!")

if __name__ == "__main__":
    main() 