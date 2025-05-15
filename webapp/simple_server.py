#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Report Helper - Simple Web Server for Shared Hosting
Created by Murad Tadesse
"""

import os
import sys
import logging
from pathlib import Path
import http.server
import socketserver

# Configuration
PORT = int(os.environ.get('PORT', 8080))
WEBAPP_DIR = Path(__file__).parent.absolute()
LOG_FILE = WEBAPP_DIR / "webapp.log"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TikTok-Report-Webapp")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS support and logging."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEBAPP_DIR), **kwargs)
    
    def end_headers(self):
        """Add CORS headers and other necessary headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Override log_message to use our logger."""
        logger.info("%s - %s", self.client_address[0], format % args)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()

def start_server():
    """Start the HTTP server."""
    handler = CustomHandler
    
    try:
        # Bind to all interfaces on the specified port
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            logger.info(f"Starting server at http://0.0.0.0:{PORT}")
            logger.info(f"Serving files from: {WEBAPP_DIR}")
            
            # Start the server
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Port {PORT} is already in use.")
            sys.exit(1)
        else:
            logger.error(f"Error starting server: {e}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
