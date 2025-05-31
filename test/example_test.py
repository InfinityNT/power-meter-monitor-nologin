"""
Power Meter Monitor - Example Test

This is an example test that demonstrates the auto-discovery system.
It shows how easy it is to add new tests to the system.

Functions:
    run_example_test: Example test function that gets auto-discovered
"""

import time
import random

def run_example_test():
    """
    Run an example test to demonstrate auto-discovery
    
    This test demonstrates:
    - How auto-discovery finds test functions
    - How test results can be stored in test database
    - How to create simple, effective tests
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    print("Example Test - Auto-Discovery Demonstration")
    print("=" * 50)
    
    try:
        # Import test database if available
        try:
            from core.database_handler import get_test_db
            test_db = get_test_db()
            print("✓ Test database handler available")
        except ImportError:
            test_db = None
            print("⚠️  Test database handler not available")
        
        print("\nRunning example test steps...")
        
        # Step 1: Initialize
        print("  1. Initializing test environment...")
        time.sleep(0.5)
        print("     ✓ Test environment ready")
        
        # Step 2: Generate test data
        print("  2. Generating test data...")
        test_data = {
            'power_kw': round(random.uniform(10, 100), 2),
            'voltage_ln_avg': round(random.uniform(220, 240), 1),
            'current_avg': round(random.uniform(1, 10), 2),
            'frequency': round(random.uniform(59.8, 60.2), 1)
        }
        time.sleep(0.3)
        print(f"     ✓ Generated test data: {test_data}")
        
        # Step 3: Validate test data
        print("  3. Validating test data...")
        time.sleep(0.2)
        
        validation_passed = True
        if test_data['power_kw'] < 0 or test_data['power_kw'] > 1000:
            print("     ❌ Power value out of range")
            validation_passed = False
        
        if test_data['voltage_ln_avg'] < 200 or test_data['voltage_ln_avg'] > 250:
            print("     ❌ Voltage value out of range")
            validation_passed = False
        
        if validation_passed:
            print("     ✓ All data validation checks passed")
        
        # Step 4: Store test result
        if test_db and test_db.enabled:
            print("  4. Storing test result in database...")
            success = test_db.store_test_result(
                test_name='Example Auto-Discovery Test',
                test_type='demonstration',
                status='pass' if validation_passed else 'fail',
                duration=1.0,
                notes='Example test to demonstrate auto-discovery system',
                meter_data=test_data
            )
            if success:
                print("     ✓ Test result stored in test database")
            else:
                print("     ⚠️  Test result storage failed (database error)")
        elif test_db and not test_db.enabled:
            print("  4. Test database is disabled in settings.py - skipping storage")
            print("     ⚠️  Set USE_TEST_DATABASE=True in config/settings.py to enable")
        else:
            print("  4. Test database handler not available - skipping storage")
        
        # Final result
        print("\nTest Results:")
        if validation_passed:
            print("  Status: ✅ PASSED")
            print("  All test steps completed successfully")
            print("  Test data generated and validated correctly")
        else:
            print("  Status: ❌ FAILED")
            print("  One or more validation checks failed")
        
        print("\nThis test demonstrates:")
        print("  • Auto-discovery found this function: run_example_test()")
        print("  • CLI command created automatically: test-example")
        print("  • Test results can be stored in test database")
        print("  • Simple test structure with clear reporting")
        
        return 0 if validation_passed else 1
        
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error during test: {e}")
        
        # Try to store error result if possible
        if test_db and test_db.enabled:
            test_db.store_test_result(
                test_name='Example Auto-Discovery Test',
                test_type='demonstration',
                status='error',
                duration=0,
                notes=f'Test failed with error: {str(e)}'
            )
        
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(run_example_test())
