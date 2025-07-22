"""
Demo: Random Parts Selection
Demonstrates the random parts selection functionality with sample data.
"""

import logging
from database_manager import DatabaseManager
from query_interface import QueryInterface

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample data for demonstration."""
    db_manager = DatabaseManager("demo_hotparts.db")
    
    # Sample hot parts data
    hot_parts_data = [
        {'MPN': 'ABC123', 'Date': '2025.07.07', 'Reqs_Count': 5, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': '3.2T Switch', 'source_file': 'demo.xlsx'},
        {'MPN': 'DEF456', 'Date': '2025.07.08', 'Reqs_Count': 8, 'Manufacturer': 'Intel', 'Product_Class': 'Processor', 'Description': 'Xeon CPU', 'source_file': 'demo.xlsx'},
        {'MPN': 'GHI789', 'Date': '2025.07.09', 'Reqs_Count': 3, 'Manufacturer': 'AMD', 'Product_Class': 'Processor', 'Description': 'EPYC CPU', 'source_file': 'demo.xlsx'},
        {'MPN': 'JKL012', 'Date': '2025.07.10', 'Reqs_Count': 12, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': 'Network Card', 'source_file': 'demo.xlsx'},
        {'MPN': 'MNO345', 'Date': '2025.07.11', 'Reqs_Count': 6, 'Manufacturer': 'Intel', 'Product_Class': 'Memory', 'Description': 'DDR4 Module', 'source_file': 'demo.xlsx'},
        {'MPN': 'PQR678', 'Date': '2025.07.12', 'Reqs_Count': 9, 'Manufacturer': 'AMD', 'Product_Class': 'Memory', 'Description': 'DDR5 Module', 'source_file': 'demo.xlsx'},
        {'MPN': 'STU901', 'Date': '2025.07.13', 'Reqs_Count': 4, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': 'Fibre Channel', 'source_file': 'demo.xlsx'},
        {'MPN': 'VWX234', 'Date': '2025.07.14', 'Reqs_Count': 7, 'Manufacturer': 'Intel', 'Product_Class': 'Storage', 'Description': 'NVMe SSD', 'source_file': 'demo.xlsx'},
        {'MPN': 'YZA567', 'Date': '2025.07.15', 'Reqs_Count': 11, 'Manufacturer': 'AMD', 'Product_Class': 'Storage', 'Description': 'SATA SSD', 'source_file': 'demo.xlsx'},
        {'MPN': 'BCD890', 'Date': '2025.07.16', 'Reqs_Count': 2, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': 'Ethernet Card', 'source_file': 'demo.xlsx'},
    ]
    
    # Sample excess inventory data
    excess_data = [
        {'MPN': 'ABC123', 'Excess_Filename': 'excess1.xlsx', 'Excess_QTY': 150, 'Target_Price': 25.50, 'Manufacturer': 'Broadcom', 'sheet_name': 'Raw Data'},
        {'MPN': 'DEF456', 'Excess_Filename': 'excess1.xlsx', 'Excess_QTY': 75, 'Target_Price': 45.75, 'Manufacturer': 'Intel', 'sheet_name': 'Raw Data'},
        {'MPN': 'GHI789', 'Excess_Filename': 'excess2.xlsx', 'Excess_QTY': 200, 'Target_Price': 35.25, 'Manufacturer': 'AMD', 'sheet_name': 'Raw Data'},
        {'MPN': 'JKL012', 'Excess_Filename': 'excess2.xlsx', 'Excess_QTY': 100, 'Target_Price': 15.80, 'Manufacturer': 'Broadcom', 'sheet_name': 'Raw Data'},
        {'MPN': 'MNO345', 'Excess_Filename': 'excess3.xlsx', 'Excess_QTY': 300, 'Target_Price': 8.95, 'Manufacturer': 'Intel', 'sheet_name': 'Raw Data'},
        {'MPN': 'PQR678', 'Excess_Filename': 'excess3.xlsx', 'Excess_QTY': 125, 'Target_Price': 12.30, 'Manufacturer': 'AMD', 'sheet_name': 'Raw Data'},
        {'MPN': 'STU901', 'Excess_Filename': 'excess4.xlsx', 'Excess_QTY': 80, 'Target_Price': 55.20, 'Manufacturer': 'Broadcom', 'sheet_name': 'Raw Data'},
        {'MPN': 'VWX234', 'Excess_Filename': 'excess4.xlsx', 'Excess_QTY': 250, 'Target_Price': 22.40, 'Manufacturer': 'Intel', 'sheet_name': 'Raw Data'},
        {'MPN': 'YZA567', 'Excess_Filename': 'excess5.xlsx', 'Excess_QTY': 180, 'Target_Price': 18.75, 'Manufacturer': 'AMD', 'sheet_name': 'Raw Data'},
        {'MPN': 'BCD890', 'Excess_Filename': 'excess5.xlsx', 'Excess_QTY': 90, 'Target_Price': 32.60, 'Manufacturer': 'Broadcom', 'sheet_name': 'Raw Data'},
    ]
    
    # Sample matches data (cross-referenced)
    matches_data = [
        {'MPN': 'ABC123', 'Weekly_Hot_Parts_Date': '2025.07.07', 'Reqs_Count': 5, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': '3.2T Switch', 'Excess_Filename': 'excess1.xlsx', 'Excess_QTY': 150, 'Target_Price': 25.50},
        {'MPN': 'DEF456', 'Weekly_Hot_Parts_Date': '2025.07.08', 'Reqs_Count': 8, 'Manufacturer': 'Intel', 'Product_Class': 'Processor', 'Description': 'Xeon CPU', 'Excess_Filename': 'excess1.xlsx', 'Excess_QTY': 75, 'Target_Price': 45.75},
        {'MPN': 'GHI789', 'Weekly_Hot_Parts_Date': '2025.07.09', 'Reqs_Count': 3, 'Manufacturer': 'AMD', 'Product_Class': 'Processor', 'Description': 'EPYC CPU', 'Excess_Filename': 'excess2.xlsx', 'Excess_QTY': 200, 'Target_Price': 35.25},
        {'MPN': 'JKL012', 'Weekly_Hot_Parts_Date': '2025.07.10', 'Reqs_Count': 12, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': 'Network Card', 'Excess_Filename': 'excess2.xlsx', 'Excess_QTY': 100, 'Target_Price': 15.80},
        {'MPN': 'MNO345', 'Weekly_Hot_Parts_Date': '2025.07.11', 'Reqs_Count': 6, 'Manufacturer': 'Intel', 'Product_Class': 'Memory', 'Description': 'DDR4 Module', 'Excess_Filename': 'excess3.xlsx', 'Excess_QTY': 300, 'Target_Price': 8.95},
        {'MPN': 'PQR678', 'Weekly_Hot_Parts_Date': '2025.07.12', 'Reqs_Count': 9, 'Manufacturer': 'AMD', 'Product_Class': 'Memory', 'Description': 'DDR5 Module', 'Excess_Filename': 'excess3.xlsx', 'Excess_QTY': 125, 'Target_Price': 12.30},
        {'MPN': 'STU901', 'Weekly_Hot_Parts_Date': '2025.07.13', 'Reqs_Count': 4, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': 'Fibre Channel', 'Excess_Filename': 'excess4.xlsx', 'Excess_QTY': 80, 'Target_Price': 55.20},
        {'MPN': 'VWX234', 'Weekly_Hot_Parts_Date': '2025.07.14', 'Reqs_Count': 7, 'Manufacturer': 'Intel', 'Product_Class': 'Storage', 'Description': 'NVMe SSD', 'Excess_Filename': 'excess4.xlsx', 'Excess_QTY': 250, 'Target_Price': 22.40},
        {'MPN': 'YZA567', 'Weekly_Hot_Parts_Date': '2025.07.15', 'Reqs_Count': 11, 'Manufacturer': 'AMD', 'Product_Class': 'Storage', 'Description': 'SATA SSD', 'Excess_Filename': 'excess5.xlsx', 'Excess_QTY': 180, 'Target_Price': 18.75},
        {'MPN': 'BCD890', 'Weekly_Hot_Parts_Date': '2025.07.16', 'Reqs_Count': 2, 'Manufacturer': 'Broadcom', 'Product_Class': 'Interface', 'Description': 'Ethernet Card', 'Excess_Filename': 'excess5.xlsx', 'Excess_QTY': 90, 'Target_Price': 32.60},
    ]
    
    # Insert data
    print("Creating sample data...")
    db_manager.insert_hot_parts(hot_parts_data)
    db_manager.insert_excess_inventory(excess_data)
    db_manager.insert_matches(matches_data)
    
    print("Sample data created successfully!")
    return db_manager

def demonstrate_random_selection():
    """Demonstrate random parts selection with different criteria."""
    print("\n" + "="*60)
    print("RANDOM PARTS SELECTION DEMONSTRATION")
    print("="*60)
    
    # Create sample data
    db_manager = create_sample_data()
    query_interface = QueryInterface("demo_hotparts.db")
    
    # Show database stats
    print("\n📊 Database Statistics:")
    query_interface.show_database_stats()
    
    # Demo 1: Basic random selection
    print("\n🎯 Demo 1: Basic Random Selection (5 parts, any price)")
    df1 = query_interface.get_random_parts_list(count=5, min_price=0.0, max_manufacturers=3)
    if not df1.empty:
        print(df1.to_string(index=False))
    
    # Demo 2: High-value parts
    print("\n💰 Demo 2: High-Value Parts (>$30, 3 parts)")
    df2 = query_interface.get_random_parts_list(count=3, min_price=30.0, max_manufacturers=3)
    if not df2.empty:
        print(df2.to_string(index=False))
    
    # Demo 3: Diverse manufacturers
    print("\n🏭 Demo 3: Diverse Manufacturers (6 parts, 3 manufacturers)")
    df3 = query_interface.get_random_parts_list(count=6, min_price=10.0, max_manufacturers=3)
    if not df3.empty:
        print(df3.to_string(index=False))
    
    # Demo 4: Budget-friendly parts
    print("\n💸 Demo 4: Budget-Friendly Parts (<$20, 4 parts)")
    df4 = query_interface.get_random_parts_list(count=4, min_price=5.0, max_manufacturers=2)
    if not df4.empty:
        # Filter to show only parts under $20
        df4_filtered = df4[df4['target_price'].str.replace('$', '').astype(float) < 20.0]
        if not df4_filtered.empty:
            print(df4_filtered.to_string(index=False))
        else:
            print("No parts found under $20")
    
    # Demo 5: Save to file
    print("\n💾 Demo 5: Save Random Selection to File")
    df5 = query_interface.get_random_parts_list(
        count=8, 
        min_price=15.0, 
        max_manufacturers=3,
        output_file="demo_random_parts"
    )
    if not df5.empty:
        print("Random parts list saved to: demo_random_parts_[timestamp].xlsx")
        print(df5.to_string(index=False))
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED")
    print("="*60)
    
    # Clean up
    import os
    if os.path.exists("demo_hotparts.db"):
        os.remove("demo_hotparts.db")
        print("Demo database cleaned up")

if __name__ == "__main__":
    demonstrate_random_selection() 