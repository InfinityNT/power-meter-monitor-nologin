"""
Power Meter Monitor - Database Connection Test

This module provides comprehensive testing for MS Access database connectivity.
It verifies database configuration, driver availability, and connection establishment.

Functions:
    run_database_connection_test: Main function to test database connectivity
"""

import os
import sys
import pyodbc

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import CONFIG

def run_database_connection_test():
    """
    Test the MS Access database connection and configuration
    
    This function performs comprehensive testing of the database setup including:
    - Database path verification
    - ODBC driver availability check
    - Connection establishment test
    - Table existence verification
    - Record count reporting
    
    Returns:
        bool: True if all tests pass, False if any test fails
    """
    print("Testing MS Access Database Connection")
    print("=" * 50)
    
    # Get database path from config
    db_path = CONFIG.get('DATABASE_PATH')
    print(f"Database path: {db_path}")
    
    # Check if directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        print(f"Creating directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    # List available ODBC drivers
    print("\nAvailable ODBC Drivers:")
    drivers = pyodbc.drivers()
    for driver in drivers:
        print(f"  - {driver}")
    
    # Find MS Access driver
    access_drivers = [d for d in drivers if 'Microsoft Access Driver' in d]
    if not access_drivers:
        print("\nERROR: No Microsoft Access Driver found!")
        print("Please install Microsoft Access Database Engine from:")
        print("https://www.microsoft.com/en-us/download/details.aspx?id=54920")
        return False
    
    print(f"\nUsing driver: {access_drivers[0]}")
    
    # Try to connect
    try:
        conn_str = (
            f'DRIVER={{{access_drivers[0]}}};'
            f'DBQ={db_path};'
        )
        print(f"\nConnection string: {conn_str}")
        
        print("\nConnecting to database...")
        connection = pyodbc.connect(conn_str)
        print("SUCCESS: Connected to database!")
        
        # Try to create a test table
        cursor = connection.cursor()
        
        # Check if our table exists
        tables = cursor.tables(table=CONFIG.get('DATABASE_TABLE', 'meter_readings'), tableType='TABLE').fetchall()
        if tables:
            print(f"\nTable '{CONFIG.get('DATABASE_TABLE')}' exists")
            
            # Count records
            cursor.execute(f"SELECT COUNT(*) FROM {CONFIG.get('DATABASE_TABLE')}")
            count = cursor.fetchone()[0]
            print(f"Number of records: {count}")
        else:
            print(f"\nTable '{CONFIG.get('DATABASE_TABLE')}' does not exist yet")
            print("It will be created when you run the main application")
        
        cursor.close()
        connection.close()
        print("\nDatabase connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to connect to database")
        print(f"Error details: {str(e)}")
        print("\nPossible solutions:")
        print("1. Ensure Microsoft Access Database Engine is installed")
        print("2. Check if you have 32-bit Python with 64-bit Office or vice versa")
        print("3. Try installing the opposite bit version of Access Database Engine")
        return False

# Backward compatibility alias
test_database_connection = run_database_connection_test

if __name__ == "__main__":
    success = run_database_connection_test()
    sys.exit(0 if success else 1)
