"""
Power Meter Monitor - Test Package

This package contains all test modules for the power meter monitoring system.
All test files have been renamed with descriptive names to clearly indicate
their specific purpose and functionality.

Test Modules:
    simulator_application_test: Complete application test with power meter simulator
    database_connection_test: MS Access database connectivity testing
    network_ports_test: Network port and connectivity testing
    unicode_detection_test: Unicode character detection and validation

Functions:
    run_simulator_test: Run the simulator application test
    run_database_test: Run database connection test
    run_network_test: Run network connectivity test
    run_unicode_test: Run unicode character detection test
"""

__version__ = '1.0.0'
__author__ = 'Power Meter Monitor Team'

import os
import sys

# Add parent directory to path to allow imports from main project
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Test module functions for easy access
def run_simulator_test():
    """Run the simulator application test"""
    from .simulator_application_test import run_simulator_test
    return run_simulator_test()

def run_database_test():
    """Run database connection test"""
    from .database_connection_test import run_database_connection_test
    return run_database_connection_test()

def run_network_test():
    """Run network connectivity test"""
    from .network_ports_test import run_network_ports_test
    return run_network_ports_test()

def run_unicode_test():
    """Run unicode character detection test"""
    from .unicode_detection_test import run_unicode_detection_test
    return run_unicode_detection_test()

# Define package exports
__all__ = [
    'run_simulator_test',
    'run_database_test', 
    'run_network_test',
    'run_unicode_test'
]

# Test utilities
def setup_test_environment():
    """Setup common test environment"""
    import logging
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ensure project directories exist
    project_root = _parent_dir
    dirs_to_check = ['logs', 'data']
    
    for directory in dirs_to_check:
        dir_path = os.path.join(project_root, directory)
        os.makedirs(dir_path, exist_ok=True)

def get_test_info():
    """Get information about available tests"""
    tests = {
        'simulator_test': {
            'description': 'Complete application test with power meter simulator',
            'file': 'simulator_application_test.py',
            'function': 'run_simulator_test()',
            'purpose': 'Testing full application without hardware'
        },
        'database_test': {
            'description': 'MS Access database connection and configuration test',
            'file': 'database_connection_test.py', 
            'function': 'run_database_test()',
            'purpose': 'Verifying database connectivity and setup'
        },
        'network_test': {
            'description': 'Network port and connectivity test',
            'file': 'network_ports_test.py',
            'function': 'run_network_test()', 
            'purpose': 'Testing network configuration and accessibility'
        },
        'unicode_test': {
            'description': 'Unicode character detection and validation test',
            'file': 'unicode_detection_test.py',
            'function': 'run_unicode_test()',
            'purpose': 'Ensuring ASCII-only content compliance'
        }
    }
    return tests

# Initialize test environment when package is imported
setup_test_environment()
