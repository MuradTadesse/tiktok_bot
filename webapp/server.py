#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TikTok Report Helper - Local Development Server
Created by Murad Tadesse

A simple HTTP server for local development and testing of the TikTok Report Helper web app.
This allows you to preview and test the web app locally before deployment.
"""

import os
import http.server
import socketserver
from pathlib import Path

# Configuration
PORT = 8000
DIRECTORY = Path(__file__).parent.absolute()

class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS support for local testing."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        """Add CORS headers to enable testing with Telegram."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    handler = Handler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n🚀 Server started at http://localhost:{PORT}")
        print(f"📂 Serving files from: {DIRECTORY}")
        print(f"📱 Access on your network at: http://YOUR_IP_ADDRESS:{PORT}")
        print("\n📝 Note: For Telegram WebApp testing, use your network IP or a tunneling service like ngrok.")
        print("   Example with ngrok: ngrok http 8000")
        print("\n⚠️ Press Ctrl+C to stop the server.\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")
