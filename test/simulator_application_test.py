"""
Power Meter Monitor - Simulator Application Test

This module provides a complete test environment using a power meter simulator
instead of real hardware. It allows testing all functionality without requiring
physical power meter equipment.

Functions:
    run_simulator_test: Main function to run the simulator test application
"""

import sys
import time
import logging
import os

# Add project root to path to allow imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import CONFIG
from core import PowerMeterDataManager, PowerMeterSimulator
from core.database_handler import DatabaseHandler
from web import start_smart_server as start_test_server
from api import PowerMeterHTTPServer

logger = logging.getLogger('powermeter.simulator_test')

def run_simulator_test():
    """
    Run the power meter test application with simulator
    
    This function provides a complete test environment that simulates power meter
    data without requiring real hardware. It includes all the same functionality
    as the production application but uses simulated data.
    
    Features tested:
    - Simulated power meter data generation
    - Data collection and management
    - HTTP API functionality
    - Web interface
    - Database storage (if enabled)
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    logger.info("Starting power meter test application with simulator")
    logger.info(f"Dashboard style: {CONFIG.get('DASHBOARD_STYLE', 'classic')}")
    
    # Create simulated reader instead of real hardware
    reader = PowerMeterSimulator()
    
    # Create custom data manager that maintains the simulator's interface
    class CustomPowerMeterDataManager(PowerMeterDataManager):
        def __init__(self, reader, poll_interval=5):
            """Initialize with database support"""
            self.reader = reader
            self.poll_interval = poll_interval
            self.meter_data = {}
            self.running = False
            self._thread = None
            self.db_handler = DatabaseHandler()
            
        def _read_meter_loop(self):
            """Continuously read from the meter"""
            while self.running:
                try:
                    # Use detailed data if configured
                    if CONFIG.get('DETAILED_DATA', False):
                        data = self.reader.read_detailed_data()
                    else:
                        data = self.reader.read_basic_data()
                        
                    if data is not None:
                        self.meter_data = data
                        
                        power = data.get('system', {}).get('power_kw', data.get('power_kw', 'N/A'))
                        
                        # Store in database if enabled
                        if self.db_handler.enabled:
                            self.db_handler.store_reading(data)
                        
                        logger.info(f"Updated readings: Power={power}kW")
                except Exception as e:
                    logger.error(f"Error in meter reading loop: {str(e)}")
                time.sleep(self.poll_interval)
    
    # Create data manager with simulator
    data_manager = CustomPowerMeterDataManager(reader, 2)  # Poll every 2 seconds
    
    # Create HTTP API server
    http_server = PowerMeterHTTPServer(CONFIG['HTTP_PORT'], data_manager)
    
    try:
        # Start test HTML page server
        start_test_server(8000)
        dashboard_type = "modern" if CONFIG.get('DASHBOARD_STYLE') == 'modern' else "classic"
        logger.info(f"Test page ({dashboard_type} style) available at http://localhost:8000/")
        logger.info(f"Automatically redirects to appropriate monitor page")
        
        # Start components
        data_manager.start()
        http_server.start()
        
        logger.info(f"Test system running. HTTP API available at http://localhost:{CONFIG['HTTP_PORT']}/")
        
        if CONFIG.get('USE_DATABASE', False):
            logger.info("Database storage is ENABLED")
        else:
            logger.info("Database storage is DISABLED")
            
        logger.info("Press Ctrl+C to exit.")
        
        # Keep main thread alive until keyboard interrupt
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupt received. Shutting down.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        # Clean shutdown
        http_server.stop()
        data_manager.stop()
        reader.disconnect()
        logger.info("Test application shut down")
    
    return 0

# Backward compatibility alias
main = run_simulator_test

if __name__ == "__main__":
    sys.exit(run_simulator_test())
