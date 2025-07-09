import pandas as pd
import os
import re
from datetime import datetime
from pathlib import Path

class HotPartsParser:
    def __init__(self, input_directory="."):
        self.input_directory = input_directory
        self.master_data = []
        self.pivot_data = []
        
    def extract_date_from_filename(self, filename):
        """Extract date from filename like 'Weekly Hot Parts List 2025.07.07.xlsx'"""
        match = re.search(r'(\d{4}\.\d{2}\.\d{2})', filename)
        if match:
            return match.group(1)
        return None
    
    def extract_date_from_sheetname(self, sheet_name):
        """Extract date from sheet name like '2025.07.07'"""
        if re.match(r'\d{4}\.\d{2}\.\d{2}', sheet_name):
            return sheet_name
        return None
    
    def clean_dataframe(self, df, sheet_date):
        """Clean and extract relevant data from a date-based sheet"""
        # Find the header row (row with 'MPN' in it)
        header_row = None
        for idx, row in df.iterrows():
            if 'MPN' in str(row.values):
                header_row = idx
                break
        
        if header_row is None:
            return pd.DataFrame()
        
        # Get the actual headers and data
        headers = df.iloc[header_row]
        data = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Find the relevant columns
        mpn_col = None
        reqs_count_col = None
        mfg_col = None
        product_class_col = None
        description_col = None
        
        for idx, header in enumerate(headers):
            header_str = str(header).strip()
            if 'MPN' in header_str:
                mpn_col = idx
            elif 'Reqs' in header_str and 'Count' in header_str:
                reqs_count_col = idx
            elif 'MFG' in header_str or 'Manufacturer' in header_str:
                mfg_col = idx
            elif 'Product' in header_str and 'Class' in header_str:
                product_class_col = idx
            elif 'Description' in header_str:
                description_col = idx
        
        # Create cleaned dataframe
        cleaned_data = []
        for _, row in data.iterrows():
            if pd.isna(row.iloc[mpn_col]) or str(row.iloc[mpn_col]).strip() == '':
                continue
                
            cleaned_row = {
                'MPN': str(row.iloc[mpn_col]).strip(),
                'Date': sheet_date,
                'Reqs_Count': str(row.iloc[reqs_count_col]).strip() if reqs_count_col is not None else '',
                'Manufacturer': str(row.iloc[mfg_col]).strip() if mfg_col is not None else '',
                'Product_Class': str(row.iloc[product_class_col]).strip() if product_class_col is not None else '',
                'Description': str(row.iloc[description_col]).strip() if description_col is not None else ''
            }
            cleaned_data.append(cleaned_row)
        
        return pd.DataFrame(cleaned_data)
    
    def clean_pivot_data(self, df, file_date):
        """Clean and extract data from pivot sheet"""
        # Find the header row
        header_row = None
        for idx, row in df.iterrows():
            if 'MPN' in str(row.values) and 'Reqs Count' in str(row.values):
                header_row = idx
                break
        
        if header_row is None:
            return pd.DataFrame()
        
        # Get headers and data
        headers = df.iloc[header_row]
        data = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Find MPN and Reqs Count columns
        mpn_col = None
        reqs_count_col = None
        
        for idx, header in enumerate(headers):
            header_str = str(header).strip()
            if 'MPN' in header_str:
                mpn_col = idx
            elif 'Reqs Count' in header_str:
                reqs_count_col = idx
        
        if mpn_col is None or reqs_count_col is None:
            return pd.DataFrame()
        
        # Create cleaned dataframe
        cleaned_data = []
        for _, row in data.iterrows():
            if pd.isna(row.iloc[mpn_col]) or str(row.iloc[mpn_col]).strip() == '':
                continue
                
            cleaned_row = {
                'MPN': str(row.iloc[mpn_col]).strip(),
                'Reqs_Count': str(row.iloc[reqs_count_col]).strip(),
                'Date': file_date
            }
            cleaned_data.append(cleaned_row)
        
        return pd.DataFrame(cleaned_data)
    
    def process_file(self, file_path):
        """Process a single Excel file"""
        print(f"Processing: {file_path}")
        
        # Extract date from filename
        file_date = self.extract_date_from_filename(os.path.basename(file_path))
        if not file_date:
            print(f"Could not extract date from filename: {file_path}")
            return
        
        try:
            # Read all sheets
            xl_file = pd.ExcelFile(file_path)
            
            # Process date-based sheets
            for sheet_name in xl_file.sheet_names:
                sheet_date = self.extract_date_from_sheetname(sheet_name)
                if sheet_date:
                    print(f"  Processing sheet: {sheet_name}")
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    cleaned_df = self.clean_dataframe(df, sheet_date)
                    if not cleaned_df.empty:
                        self.master_data.append(cleaned_df)
            
            # Process pivot sheet
            if 'Pivot' in xl_file.sheet_names:
                print(f"  Processing Pivot sheet")
                pivot_df = pd.read_excel(file_path, sheet_name='Pivot')
                cleaned_pivot = self.clean_pivot_data(pivot_df, file_date)
                if not cleaned_pivot.empty:
                    self.pivot_data.append(cleaned_pivot)
                    
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    def process_all_files(self):
        """Process all Excel files in the input directory"""
        excel_files = [f for f in os.listdir(self.input_directory) 
                      if f.endswith(('.xlsx', '.xls')) and 'Weekly Hot Parts List' in f]
        
        if not excel_files:
            print("No 'Weekly Hot Parts List' Excel files found")
            return
        
        for file in excel_files:
            file_path = os.path.join(self.input_directory, file)
            self.process_file(file_path)
    
    def compile_master_files(self, output_dir="."):
        """Compile the processed data into master files"""
        if not self.master_data and not self.pivot_data:
            print("No data to compile")
            return
        
        # Compile master data
        if self.master_data:
            master_df = pd.concat(self.master_data, ignore_index=True)
            master_df = master_df.drop_duplicates()
            master_df = master_df.sort_values(['MPN', 'Date'])
            
            master_file = os.path.join(output_dir, "Master_Hot_Parts_Data.xlsx")
            with pd.ExcelWriter(master_file, engine='openpyxl') as writer:
                master_df.to_excel(writer, sheet_name='Master_Data', index=False)
            
            print(f"Master data compiled: {master_file}")
            print(f"Records: {len(master_df)}")
            print(f"Columns: {list(master_df.columns)}")
        
        # Compile pivot data
        if self.pivot_data:
            pivot_df = pd.concat(self.pivot_data, ignore_index=True)
            pivot_df = pivot_df.drop_duplicates()
            pivot_df = pivot_df.sort_values(['MPN', 'Date'])
            
            pivot_file = os.path.join(output_dir, "Master_Pivot_Data.xlsx")
            with pd.ExcelWriter(pivot_file, engine='openpyxl') as writer:
                pivot_df.to_excel(writer, sheet_name='Pivot_Data', index=False)
            
            print(f"Pivot data compiled: {pivot_file}")
            print(f"Records: {len(pivot_df)}")
            print(f"Columns: {list(pivot_df.columns)}")

def main():
    """Main function to run the parser"""
    parser = HotPartsParser()
    
    print("Starting Hot Parts Excel Parser")
    print("=" * 50)
    
    # Process all files
    parser.process_all_files()
    
    # Compile master files
    parser.compile_master_files()
    
    print("\nParsing complete!")

if __name__ == "__main__":
    main() 