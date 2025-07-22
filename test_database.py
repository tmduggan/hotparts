"""
Test Database Functionality
Tests the database operations and query interface.
"""

import logging
from database_manager import DatabaseManager
from query_interface import QueryInterface
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_operations():
    """Test basic database operations."""
    print("Testing Database Operations...")
    
    # Initialize database manager
    db_manager = DatabaseManager("test_hotparts.db")
    
    # Test data insertion
    test_hot_parts = [
        {
            'MPN': 'TEST001',
            'Date': '2025.07.07',
            'Reqs_Count': 5,
            'Manufacturer': 'Test Manufacturer 1',
            'Product_Class': 'Test Class',
            'Description': 'Test Description 1',
            'source_file': 'test_file.xlsx'
        },
        {
            'MPN': 'TEST002',
            'Date': '2025.07.08',
            'Reqs_Count': 3,
            'Manufacturer': 'Test Manufacturer 2',
            'Product_Class': 'Test Class',
            'Description': 'Test Description 2',
            'source_file': 'test_file.xlsx'
        }
    ]
    
    test_excess = [
        {
            'MPN': 'TEST001',
            'Excess_Filename': 'test_excess.xlsx',
            'Excess_QTY': 100,
            'Target_Price': 15.50,
            'Manufacturer': 'Test Manufacturer 1',
            'sheet_name': 'Raw Data'
        },
        {
            'MPN': 'TEST002',
            'Excess_Filename': 'test_excess.xlsx',
            'Excess_QTY': 50,
            'Target_Price': 25.75,
            'Manufacturer': 'Test Manufacturer 2',
            'sheet_name': 'Raw Data'
        }
    ]
    
    test_matches = [
        {
            'MPN': 'TEST001',
            'Weekly_Hot_Parts_Date': '2025.07.07',
            'Reqs_Count': 5,
            'Manufacturer': 'Test Manufacturer 1',
            'Product_Class': 'Test Class',
            'Description': 'Test Description 1',
            'Excess_Filename': 'test_excess.xlsx',
            'Excess_QTY': 100,
            'Target_Price': 15.50
        }
    ]
    
    # Insert test data
    print("Inserting test data...")
    hot_parts_inserted = db_manager.insert_hot_parts(test_hot_parts)
    excess_inserted = db_manager.insert_excess_inventory(test_excess)
    matches_inserted = db_manager.insert_matches(test_matches)
    
    print(f"Hot parts inserted: {hot_parts_inserted}")
    print(f"Excess inserted: {excess_inserted}")
    print(f"Matches inserted: {matches_inserted}")
    
    # Test random parts query
    print("\nTesting random parts query...")
    random_parts = db_manager.get_random_parts(count=5, min_price=10.0, max_manufacturers=2)
    print(f"Random parts found: {len(random_parts)}")
    
    # Test database stats
    print("\nTesting database stats...")
    stats = db_manager.get_database_stats()
    print("Database stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test query interface
    print("\nTesting query interface...")
    query_interface = QueryInterface("test_hotparts.db")
    query_interface.show_database_stats()
    
    # Clean up test database
    if os.path.exists("test_hotparts.db"):
        os.remove("test_hotparts.db")
        print("\nTest database cleaned up")
    
    print("\n✅ Database operations test completed successfully!")

def test_query_interface():
    """Test the query interface functionality."""
    print("\nTesting Query Interface...")
    
    # Initialize database with test data
    db_manager = DatabaseManager("test_query.db")
    
    # Insert some test data for querying
    test_matches = [
        {
            'MPN': 'QUERY001',
            'Weekly_Hot_Parts_Date': '2025.07.07',
            'Reqs_Count': 10,
            'Manufacturer': 'Manufacturer A',
            'Product_Class': 'Class A',
            'Description': 'Description A',
            'Excess_Filename': 'excess_a.xlsx',
            'Excess_QTY': 200,
            'Target_Price': 15.50
        },
        {
            'MPN': 'QUERY002',
            'Weekly_Hot_Parts_Date': '2025.07.08',
            'Reqs_Count': 8,
            'Manufacturer': 'Manufacturer B',
            'Product_Class': 'Class B',
            'Description': 'Description B',
            'Excess_Filename': 'excess_b.xlsx',
            'Excess_QTY': 150,
            'Target_Price': 25.75
        },
        {
            'MPN': 'QUERY003',
            'Weekly_Hot_Parts_Date': '2025.07.09',
            'Reqs_Count': 12,
            'Manufacturer': 'Manufacturer A',
            'Product_Class': 'Class A',
            'Description': 'Description C',
            'Excess_Filename': 'excess_c.xlsx',
            'Excess_QTY': 300,
            'Target_Price': 35.25
        }
    ]
    
    db_manager.insert_matches(test_matches)
    
    # Test query interface
    query_interface = QueryInterface("test_query.db")
    
    # Test random parts list
    print("Testing random parts list generation...")
    df = query_interface.get_random_parts_list(count=3, min_price=10.0, max_manufacturers=2)
    if not df.empty:
        print("Random parts list generated successfully:")
        print(df.to_string(index=False))
    else:
        print("No random parts found")
    
    # Test summaries
    print("\nTesting summaries...")
    query_interface.show_summaries()
    
    # Clean up
    if os.path.exists("test_query.db"):
        os.remove("test_query.db")
        print("\nTest query database cleaned up")
    
    print("\n✅ Query interface test completed successfully!")

if __name__ == "__main__":
    print("="*60)
    print("DATABASE FUNCTIONALITY TESTS")
    print("="*60)
    
    try:
        test_database_operations()
        test_query_interface()
        print("\n🎉 All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")
    
    print("="*60) 