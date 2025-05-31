"""
Power Meter Monitor - Network Ports Test

This module provides comprehensive testing for network connectivity and port accessibility.
It creates test servers on multiple ports to verify network configuration and remote access.

Functions:
    run_network_ports_test: Main function to test network connectivity
    get_local_ip: Get the local IP address of the machine
    start_server: Start a test server on a specified port
"""

import http.server
import socketserver
import threading
import socket

def get_local_ip():
    """
    Get the local IP address of this machine.
    
    Uses a UDP socket connection to determine which local interface
    would be used for external connectivity.
    
    Returns:
        str: Local IP address or '127.0.0.1' as fallback
    """
    try:
        # Create a socket that connects to an external server
        # This doesn't actually establish a connection but helps determine
        # which local interface would be used
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

class NetworkTestHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for network testing"""
    
    def do_GET(self):
        """Handle GET requests with network test information"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        # Get server port
        port = self.server.server_address[1]
        
        # Create a simple HTML response showing IP and port
        html = f"""
        <html>
        <head>
            <title>Port {port} is open!</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                .container {{ padding: 20px; background-color: #f0f0f0; border-radius: 10px; display: inline-block; }}
                .success {{ color: green; font-size: 24px; }}
                .info {{ margin: 20px; padding: 15px; background-color: #e7f3ff; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">Network Test Successful!</h1>
                <p>You've successfully connected to <strong>{get_local_ip()}</strong> on port <strong>{port}</strong></p>
                <p>This confirms that port {port} is open and accessible from your network.</p>
                <div class="info">
                    <h3>Network Information</h3>
                    <p>Server IP: {get_local_ip()}</p>
                    <p>Server Port: {port}</p>
                    <p>Connection Status: Active</p>
                    <p>Test Time: {self.date_time_string()}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())

def start_server(port):
    """
    Start a test server on the specified port.
    
    Args:
        port (int): Port number to start the server on
    """
    handler = NetworkTestHTTPHandler
    
    # Allow the socket to be reused
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server running on http://{get_local_ip()}:{port}")
        httpd.serve_forever()

def run_network_ports_test():
    """
    Run network port connectivity tests
    
    This function starts test servers on multiple ports to verify:
    - Local network interface availability
    - Port accessibility
    - Remote connectivity (if tested from other devices)
    - Basic HTTP server functionality
    
    The test runs indefinitely until interrupted with Ctrl+C.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Get and display the local IP
        local_ip = get_local_ip()
        print(f"Local IP address: {local_ip}")
        print("Starting network connectivity test servers...")
        print("Testing ports 8000 and 8080...")
        
        # Create and start threads for each server
        thread1 = threading.Thread(target=start_server, args=(8000,))
        thread2 = threading.Thread(target=start_server, args=(8080,))
        
        # Set as daemon threads so they exit when the main program exits
        thread1.daemon = True
        thread2.daemon = True
        
        thread1.start()
        thread2.start()
        
        print("\nNetwork test servers are running!")
        print(f"To test from this device, visit:")
        print(f"  http://localhost:8000")
        print(f"  http://localhost:8080")
        print(f"\nTo test from another device on your LAN, visit:")
        print(f"  http://{local_ip}:8000")
        print(f"  http://{local_ip}:8080")
        print("\nPress Ctrl+C to stop the servers...")
        
        try:
            # Keep the main thread alive
            thread1.join()
        except KeyboardInterrupt:
            print("\nNetwork test servers stopped.")
            return 0
            
    except Exception as e:
        print(f"Error running network test: {e}")
        return 1
    
    return 0

# Backward compatibility alias
main = run_network_ports_test

if __name__ == "__main__":
    import sys
    sys.exit(run_network_ports_test())
