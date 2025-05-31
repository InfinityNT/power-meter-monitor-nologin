"""
Power Meter Monitor - Core Module Package

This package contains the core functionality for the power meter monitoring system.
The main application entry point has been moved from main.py to application.py
to better organize the codebase structure.

Core Components:
    application: Production application module (previously main.py)
    data_manager: Power meter data collection and management
    database_handler: Database operations and connectivity
    reader: Hardware communication with power meters
    simulator: Power meter data simulation for testing

Functions and Classes:
    PowerMeterReader: Hardware communication interface
    PowerMeterDataManager: Data collection and management
    PowerMeterSimulator: Simulated power meter for testing
    run_production_application: Main production application function
"""

__version__ = '1.0.0'

# Import key components for easier access
from .data_manager import PowerMeterDataManager
from .reader import PowerMeterReader
from .simulator import PowerMeterSimulator

# Import the main application function
try:
    from .application import run_production_application
except ImportError:
    # Fallback for backward compatibility
    run_production_application = None

# Define package exports
__all__ = [
    'PowerMeterDataManager', 
    'PowerMeterReader', 
    'PowerMeterSimulator',
    'run_production_application'
]
