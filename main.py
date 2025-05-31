#!/usr/bin/env python3
"""
Power Meter Monitor - Main Entry Point with Auto-Discovery

A comprehensive command-line interface for managing and testing the power meter monitoring system.
This is the main executable entry point with automatic test discovery functionality.

Usage:
    python main.py [command] [options]

Commands:
    start       Start the main power meter monitoring application (production mode)
    test        Start test application with power meter simulator
    status      Show system status and configuration
    install     Install required dependencies
    
Auto-discovered test commands are dynamically loaded from the test/ directory.

Features:
    - Automatic test discovery from test/ directory
    - Separate production and test database tables
    - Clean CLI interface with help text
    - Extensible architecture for easy test addition
"""

import argparse
import sys
import os
import subprocess
import logging
import importlib.util
import glob
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def discover_test_modules():
    """
    Automatically discover test modules from the test/ directory.
    
    Scans for *_test.py files and looks for functions matching run_*_test() pattern.
    Creates CLI commands automatically based on discovered tests.
    
    Returns:
        dict: Dictionary mapping command names to test module info
    """
    test_commands = {}
    test_dir = project_root / 'test'
    
    if not test_dir.exists():
        return test_commands
    
    # Find all test files
    test_files = list(test_dir.glob('*_test.py'))
    
    for test_file in test_files:
        try:
            # Load the module
            module_name = test_file.stem
            spec = importlib.util.spec_from_file_location(module_name, test_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for run_*_test functions
            for attr_name in dir(module):
                if attr_name.startswith('run_') and attr_name.endswith('_test'):
                    func = getattr(module, attr_name)
                    if callable(func):
                        # Generate command name from function name
                        # run_database_connection_test -> test-database-connection
                        # run_network_ports_test -> test-network-ports  
                        cmd_name = attr_name.replace('run_', 'test-').replace('_test', '').replace('_', '-')
                        
                        # Get help text from docstring
                        help_text = func.__doc__.strip().split('\n')[0] if func.__doc__ else f"Run {attr_name}"
                        
                        test_commands[cmd_name] = {
                            'function': func,
                            'module': module_name,
                            'file': str(test_file),
                            'help': help_text
                        }
        except Exception as e:
            print(f"Warning: Could not load test module {test_file}: {e}")
    
    return test_commands

def run_production_app(args):
    """Start the main power meter monitoring application (production mode)"""
    print("Production Mode - Power Meter Monitor")
    print("Connecting to real hardware and monitoring actual power meter data")
    print("=" * 70)
    
    try:
        # Import and run production application from core
        from core.application import run_production_application
        return run_production_application()
    except ImportError as e:
        print(f"Error importing production application: {e}")
        print("Make sure the core/application.py file exists")
        return 1
    except Exception as e:
        print(f"Error running production application: {e}")
        return 1

def run_simulator_test(args):
    """Start the test application with power meter simulator"""
    print("Simulator Mode - Power Meter Test Application")
    print("Using simulated data for testing without real hardware")
    print("=" * 65)
    
    try:
        # Import and run test application
        from test.simulator_application_test import run_simulator_test
        return run_simulator_test()
    except ImportError as e:
        print(f"Error importing simulator test: {e}")
        print("Make sure the test/simulator_application_test.py file exists")
        return 1
    except Exception as e:
        print(f"Error running simulator test: {e}")
        return 1

def show_system_status(args):
    """Show comprehensive system status and configuration"""
    print("Power Meter Monitor System Status")
    print("=" * 70)
    
    try:
        from config.settings import CONFIG
        
        print("\nCurrent Configuration:")
        print(f"  Serial Port: {CONFIG['SERIAL_PORT']}")
        print(f"  Baud Rate: {CONFIG['BAUD_RATE']}")
        print(f"  HTTP Port: {CONFIG['HTTP_PORT']}")
        print(f"  Web Port: {CONFIG.get('WEB_PORT', 8000)}")
        print(f"  Poll Interval: {CONFIG['POLL_INTERVAL']}s")
        print(f"  Dashboard Style: {CONFIG['DASHBOARD_STYLE']}")
        print(f"  Database Enabled: {CONFIG['USE_DATABASE']}")
        print(f"  Test Database Enabled: {CONFIG.get('USE_TEST_DATABASE', False)}")
        
        if CONFIG['USE_DATABASE'] or CONFIG.get('USE_TEST_DATABASE', False):
            print(f"  Production Database: {CONFIG['DATABASE_PATH']}")
            print(f"  Production Table: {CONFIG['DATABASE_TABLE']}")
            print(f"  Test Database: {CONFIG.get('TEST_DATABASE_PATH', 'Auto-generated')}")
            print(f"  Test Table: {CONFIG.get('TEST_DATABASE_TABLE', 'test_meter_readings')}")
        print(f"\nProject Structure:")
        print(f"  Root Directory: {project_root}")
        print(f"  Test Directory: {project_root / 'test'}")
        print(f"  Config Directory: {project_root / 'config'}")
        print(f"  Core Modules: {project_root / 'core'}")
        print(f"  API Modules: {project_root / 'api'}")
        print(f"  Logs Directory: {project_root / 'logs'}")
        print(f"  Data Directory: {project_root / 'data'}")
        
        # Check critical files
        print(f"\nComponent Status:")
        critical_files = [
            ('core/application.py', 'Production Application'),
            ('test/simulator_application_test.py', 'Simulator Test'),
            ('config/settings.py', 'Configuration'),
            ('core/database_handler.py', 'Database Handler'),
            ('core/__init__.py', 'Core Modules'),
            ('api/__init__.py', 'API Modules'),
        ]
        
        for file_path, description in critical_files:
            full_path = project_root / file_path
            status = "OK" if full_path.exists() else "MISSING"
            print(f"  {status}: {description}: {file_path}")
        
        # Show discovered tests
        test_commands = discover_test_modules()
        print(f"\nAuto-Discovered Tests ({len(test_commands)} found):")
        if test_commands:
            for cmd_name, cmd_info in sorted(test_commands.items()):
                print(f"  {cmd_name}: {cmd_info['help']}")
        else:
            print("  No test modules discovered")
        
        # Check directories
        print(f"\nDirectory Status:")
        required_dirs = ['logs', 'data', 'test', 'config', 'core', 'api']
        for directory in required_dirs:
            dir_path = project_root / directory
            status = "OK" if dir_path.exists() else "MISSING"
            print(f"  {status}: {directory}/ directory")
        
        return 0
        
    except ImportError as e:
        print(f"Error importing configuration: {e}")
        print("Make sure the config/settings.py file exists")
        return 1
    except Exception as e:
        print(f"Error getting system status: {e}")
        return 1

def install_dependencies(args):
    """Install required Python dependencies"""
    print("Installing Required Dependencies")
    print("=" * 50)
    
    requirements_file = project_root / 'requirements.txt'
    
    if not requirements_file.exists():
        print("requirements.txt not found in project root")
        print("Make sure you're running this from the project directory")
        return 1
    
    try:
        print("Installing packages from requirements.txt...")
        print("This may take a few minutes...")
        
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], check=True, capture_output=True, text=True)
        
        print("Dependencies installed successfully!")
        if result.stdout:
            print("\nInstallation Output:")
            print(result.stdout)
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        print("\nTry running: pip install -r requirements.txt manually")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

def create_dynamic_test_command(test_info):
    """Create a dynamic command function for a discovered test"""
    def test_command(args):
        try:
            return test_info['function']()
        except Exception as e:
            print(f"Error running {test_info['module']}: {e}")
            return 1
    return test_command

def main():
    """Main CLI entry point with auto-discovery"""
    parser = argparse.ArgumentParser(
        description="Power Meter Monitor - Control and test your power monitoring system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Core application commands
    start_parser = subparsers.add_parser('start', help='Start the production power meter monitoring application')
    start_parser.set_defaults(func=run_production_app)
    
    test_parser = subparsers.add_parser('test', help='Start test application with simulator')
    test_parser.set_defaults(func=run_simulator_test)
    
    status_parser = subparsers.add_parser('status', help='Show system status and configuration')
    status_parser.set_defaults(func=show_system_status)
    
    install_parser = subparsers.add_parser('install', help='Install required dependencies')
    install_parser.set_defaults(func=install_dependencies)
    
    # Auto-discover and add test commands
    test_commands = discover_test_modules()
    
    for cmd_name, test_info in test_commands.items():
        test_parser = subparsers.add_parser(cmd_name, help=test_info['help'])
        test_parser.set_defaults(func=create_dynamic_test_command(test_info))
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        
        # Show discovered tests
        if test_commands:
            print("\nAuto-discovered Test Commands:")
            for cmd_name, test_info in sorted(test_commands.items()):
                print(f"  {cmd_name:<20} {test_info['help']}")
        
        return 1
    
    # Run the selected command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
