"""
Power Meter Monitor - Web Server Redirect Test

This module tests the web server redirect functionality to ensure that
accessing the root URL properly redirects to the monitor page.

Functions:
    run_web_redirect_test: Main function to test web server redirect functionality
"""

import sys
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_web_redirect_test():
    """
    Test the web server redirect functionality
    
    This function tests that the web server properly redirects requests from
    the root URL (/) to the appropriate monitor page based on configuration.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    print("Testing Web Server Redirect Functionality")
    print("=" * 50)
    
    try:
        # Import and start the smart web server
        from web import start_smart_server
        
        print("Starting smart web server on port 8001...")  # Use different port to avoid conflicts
        server_thread = start_smart_server(8001)
        
        # Give the server time to start
        time.sleep(2)
        
        print("Testing redirect functionality...")
        
        # Test accessing root path
        try:
            print("\n1. Testing http://localhost:8001/")
            
            # Create a request that doesn't follow redirects automatically
            request = urllib.request.Request('http://localhost:8001/')
            
            try:
                response = urllib.request.urlopen(request)
                print(f"   Status: {response.getcode()}")
                print(f"   Final URL: {response.geturl()}")
                
                if 'monitor' in response.geturl():
                    print("   SUCCESS: Redirected to monitor page!")
                    success = True
                else:
                    print("   ISSUE: No redirect to monitor page detected")
                    success = False
                    
            except urllib.error.HTTPError as e:
                if e.code == 302:
                    location = e.headers.get('Location', 'Unknown')
                    print(f"   SUCCESS: Redirect (302) to {location}")
                    success = True
                else:
                    print(f"   HTTP Error {e.code}: {e.reason}")
                    success = False
            
        except Exception as e:
            print(f"   Connection error: {e}")
            print("   Make sure no other service is running on port 8001")
            success = False
            
        print(f"\n2. Configuration-based redirect test:")
        try:
            from config.settings import CONFIG
            dashboard_style = CONFIG.get('DASHBOARD_STYLE', 'classic')
            expected_page = 'monitor_modern.html' if dashboard_style == 'modern' else 'monitor.html'
            print(f"   Dashboard style: {dashboard_style}")
            print(f"   Expected redirect: {expected_page}")
        except ImportError:
            print("   Could not load configuration for style check")
        
        print(f"\n3. Manual verification:")
        print(f"   Open your browser and go to: http://localhost:8001/")
        print(f"   You should be automatically redirected to monitor.html")
        print(f"   (or monitor_modern.html if DASHBOARD_STYLE is 'modern')")
        
        print(f"\n4. Direct access test:")
        print(f"   http://localhost:8001/monitor.html - Classic interface")
        print(f"   http://localhost:8001/monitor_modern.html - Modern interface")
        
        print(f"\nWeb server is running on port 8001...")
        print(f"Test will run for 10 seconds, then auto-stop...")
        
        # Run for 10 seconds then stop
        time.sleep(10)
        print(f"\nStopping web server...")
        
        return 0 if success else 1
            
    except ImportError as e:
        print(f"Error importing web module: {e}")
        return 1
    except Exception as e:
        print(f"Error starting web server: {e}")
        return 1

# Backward compatibility alias
main = run_web_redirect_test

if __name__ == "__main__":
    try:
        exit_code = run_web_redirect_test()
        print("Test completed successfully!" if exit_code == 0 else "Test failed!")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
