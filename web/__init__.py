"""
Web interface package for power meter monitoring system
"""

__version__ = '1.0.0'

# Import static server functions for easier access
from .static_server import (
    serve_static_files, 
    start_static_server,
    start_smart_server,
    get_default_monitor_page
)

# Define package exports
__all__ = [
    'serve_static_files', 
    'start_static_server',
    'start_smart_server',
    'get_default_monitor_page'
]
