"""
Power Meter Monitor - Production Application Module

This module contains the core production application logic for monitoring
real power meter hardware. Previously this was main.py, but it's now a
feature module rather than the entry point.
"""

import signal
import sys
import time
import logging
import os

# Add project root to path to allow imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import CONFIG
from core import PowerMeterReader, PowerMeterDataManager
from api import PowerMeterHTTPServer
from web import start_smart_server as start_web_server

logger = logging.getLogger('powermeter.application')

# Flag to control application running state
running = True

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Shutdown signal received")
    global running
    running = False

def run_production_application():
    """
    Run the production power meter monitoring application
    
    This function initializes and runs the complete production system including:
    - Hardware connection to power meter
    - Data collection and management
    - HTTP API server
    - Web interface with automatic redirect to monitor page
    - Database logging (if enabled)
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    logger.info("Starting power meter monitoring application")
    
    # Create reader with configuration from settings
    reader = PowerMeterReader(
        CONFIG['SERIAL_PORT'],
        CONFIG['BAUD_RATE'],
        CONFIG['TIMEOUT']
    )
    
    # Set additional reader properties from config
    reader.device_address = CONFIG.get('MODBUS_ADDRESS', 1)
    
    # Test connection
    logger.info("Testing connection to power meter...")
    if not reader.test_connection():
        logger.error("Failed to communicate with power meter. Please check:")
        logger.error(f"1. Is the power meter connected via USB to {CONFIG['SERIAL_PORT']}?")
        logger.error(f"2. Is the baud rate set correctly ({CONFIG['BAUD_RATE']})?")
        logger.error("3. Are other communication parameters correct (data bits, parity, etc.)?")
        logger.error("Exiting.")
        return 1
    
    logger.info("Power meter connection test successful!")
    
    # Create data manager
    data_manager = PowerMeterDataManager(reader, CONFIG['POLL_INTERVAL'])
    
    # Create HTTP server
    http_server = PowerMeterHTTPServer(CONFIG['HTTP_PORT'], data_manager)
    
    try:
        # Start the smart web interface with auto-redirect
        web_port = CONFIG.get('WEB_PORT', 8000)
        start_web_server(web_port)
        
        # The smart server automatically redirects / to the appropriate monitor page
        dashboard_style = CONFIG.get('DASHBOARD_STYLE', 'classic')
        monitor_page = 'monitor_modern.html' if dashboard_style == 'modern' else 'monitor.html'
        
        logger.info(f"Web interface available at http://localhost:{web_port}/")
        logger.info(f"Automatically redirects to {monitor_page}")
        
        # Start components
        data_manager.start()
        http_server.start()
        
        logger.info(f"System running. HTTP API available at http://localhost:{CONFIG['HTTP_PORT']}/")
        logger.info("Press Ctrl+C to exit.")
        
        # Keep main thread alive
        global running
        while running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    finally:
        # Clean shutdown
        http_server.stop()
        data_manager.stop()
        reader.disconnect()
        logger.info("Application shut down")
    
    return 0

def main():
    """
    Main function for when this module is run directly
    
    This is provided for backward compatibility, but the preferred
    entry point is now through the main.py CLI interface.
    """
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    return run_production_application()

if __name__ == "__main__":
    # This allows the module to be run directly for backward compatibility
    sys.exit(main())
