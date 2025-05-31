"""
Static file server for web interface with automatic redirection
"""
import http.server
import socketserver
import os
import threading
import logging
from urllib.parse import urlparse

logger = logging.getLogger('powermeter.web.static_server')

class PowerMeterHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with automatic redirection to monitor.html"""
    
    def do_GET(self):
        """Handle GET requests with automatic redirection"""
        parsed_path = urlparse(self.path)
        
        # If accessing root path, redirect to monitor.html
        if parsed_path.path == '/' or parsed_path.path == '':
            self.send_response(302)  # Found (redirect)
            self.send_header('Location', '/monitor.html')
            self.end_headers()
            return
        
        # If accessing /monitor without .html, redirect to monitor.html
        if parsed_path.path == '/monitor':
            self.send_response(302)
            self.send_header('Location', '/monitor.html')
            self.end_headers()
            return
        
        # For all other requests, use the default handler
        super().do_GET()
    
    def log_message(self, format, *args):
        """Custom logging to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def serve_static_files(port=8000):
    """
    Serve static files from the web/templates directory with auto-redirect
    
    Parameters:
    - port: TCP port to listen on
    """
    # Get the web templates directory
    web_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'web', 'templates'
    )
    
    # Ensure the directory exists
    if not os.path.exists(web_dir):
        logger.error(f"Web templates directory does not exist: {web_dir}")
        return
    
    # Check if monitor.html exists
    monitor_file = os.path.join(web_dir, 'monitor.html')
    if not os.path.exists(monitor_file):
        logger.warning(f"monitor.html not found in {web_dir}")
        logger.info("Available files:")
        for file in os.listdir(web_dir):
            if file.endswith('.html'):
                logger.info(f"  - {file}")
    
    # Change to web directory
    original_cwd = os.getcwd()
    os.chdir(web_dir)
    
    try:
        # Create and start HTTP server with custom handler
        handler = PowerMeterHTTPHandler
        httpd = socketserver.TCPServer(("", port), handler)
        httpd.allow_reuse_address = True
        
        logger.info(f"Web interface available at http://localhost:{port}/")
        logger.info(f"Automatic redirect to monitor.html enabled")
        logger.info(f"Serving files from: {web_dir}")
        
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting web server: {e}")
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

def start_static_server(port=8000):
    """
    Start a static file server in a separate thread with auto-redirect
    
    Parameters:
    - port: TCP port to listen on
    
    Returns:
    - Thread object for the server
    """
    server_thread = threading.Thread(target=serve_static_files, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server a moment to start
    import time
    time.sleep(0.5)
    
    return server_thread

def get_default_monitor_page():
    """
    Determine which monitor page to use based on configuration
    
    Returns:
    - str: Filename of the monitor page to use
    """
    try:
        from config.settings import CONFIG
        dashboard_style = CONFIG.get('DASHBOARD_STYLE', 'classic')
        
        if dashboard_style == 'modern':
            return 'monitor_modern.html'
        else:
            return 'monitor.html'
    except ImportError:
        # Fallback if config is not available
        return 'monitor.html'

class SmartPowerMeterHTTPHandler(PowerMeterHTTPHandler):
    """Enhanced handler that selects monitor page based on config"""
    
    def do_GET(self):
        """Handle GET requests with smart monitor page selection"""
        parsed_path = urlparse(self.path)
        
        # If accessing root path, redirect to appropriate monitor page
        if parsed_path.path == '/' or parsed_path.path == '':
            monitor_page = get_default_monitor_page()
            self.send_response(302)
            self.send_header('Location', f'/{monitor_page}')
            self.end_headers()
            return
        
        # If accessing /monitor without .html, redirect to appropriate monitor page
        if parsed_path.path == '/monitor':
            monitor_page = get_default_monitor_page()
            self.send_response(302)
            self.send_header('Location', f'/{monitor_page}')
            self.end_headers()
            return
        
        # For all other requests, use the parent handler
        super().do_GET()

def start_smart_server(port=8000):
    """
    Start a smart static file server that automatically selects the correct monitor page
    
    Parameters:
    - port: TCP port to listen on
    
    Returns:
    - Thread object for the server
    """
    def serve_smart_files(port):
        """Serve files with smart monitor page selection"""
        web_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'web', 'templates'
        )
        
        if not os.path.exists(web_dir):
            logger.error(f"Web templates directory does not exist: {web_dir}")
            return
        
        original_cwd = os.getcwd()
        os.chdir(web_dir)
        
        try:
            handler = SmartPowerMeterHTTPHandler
            httpd = socketserver.TCPServer(("", port), handler)
            httpd.allow_reuse_address = True
            
            monitor_page = get_default_monitor_page()
            logger.info(f"Smart web interface available at http://localhost:{port}/")
            logger.info(f"Auto-redirecting to: {monitor_page}")
            logger.info(f"Serving files from: {web_dir}")
            
            httpd.serve_forever()
        except Exception as e:
            logger.error(f"Error starting smart web server: {e}")
        finally:
            os.chdir(original_cwd)
    
    server_thread = threading.Thread(target=serve_smart_files, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    import time
    time.sleep(0.5)
    
    return server_thread
