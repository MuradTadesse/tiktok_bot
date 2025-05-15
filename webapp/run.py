#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TikTok Report Helper - Web App Runner
Created by Murad Tadesse

This script provides an easy way to start the local development server for testing
the TikTok Report Helper web app.
"""

import os
import sys
import webbrowser
import subprocess
import time
import signal
from pathlib import Path

# Get the webapp directory
WEBAPP_DIR = Path(__file__).parent.absolute()
SERVER_SCRIPT = WEBAPP_DIR / "server.py"
PORT = 8000

def check_requirements():
    """Check if all required files exist."""
    required_files = [
        WEBAPP_DIR / "index.html",
        WEBAPP_DIR / "assets" / "css" / "main.css",
        WEBAPP_DIR / "assets" / "css" / "animations.css",
        WEBAPP_DIR / "assets" / "css" / "responsive.css",
        WEBAPP_DIR / "assets" / "js" / "app.js",
        WEBAPP_DIR / "assets" / "js" / "animations.js",
        WEBAPP_DIR / "assets" / "js" / "carousel.js",
        SERVER_SCRIPT
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    
    if missing_files:
        print("❌ Some required files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPlease make sure all files are in the correct location.")
        return False
    
    return True

def start_server():
    """Start the local development server."""
    print(f"\n🚀 Starting TikTok Report Helper web app server...")
    print(f"📂 Server directory: {WEBAPP_DIR}")
    
    # Check if Python is in PATH
    python_cmd = "python"
    
    try:
        server_process = subprocess.Popen(
            [python_cmd, str(SERVER_SCRIPT)], 
            cwd=WEBAPP_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )
        
        # Wait a moment for the server to start
        time.sleep(1)
        
        if server_process.poll() is not None:
            # Process has exited
            out, err = server_process.communicate()
            print(f"❌ Server failed to start:\n{err}")
            return None
        
        print(f"✅ Server started successfully!")
        return server_process
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def open_browser():
    """Open the web app in the default browser."""
    url = f"http://localhost:{PORT}"
    print(f"🌐 Opening web app in browser: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Browser opened successfully!")
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"   Please open {url} manually in your browser.")

def set_env_vars():
    """Set environment variables for the web app."""
    os.environ['WEBAPP_URL'] = f"http://localhost:{PORT}"
    
    # Check if telegram token is set
    if not os.environ.get('TELEGRAM_TOKEN'):
        # Try to read from .env file
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'TELEGRAM_BOT_TOKEN':
                            os.environ['TELEGRAM_TOKEN'] = value
                            break

def main():
    """Main function to run the web app."""
    print("\n=================================================")
    print("  TikTok Report Helper - Web App Local Server")
    print("=================================================\n")
    
    # Check if all required files exist
    if not check_requirements():
        return
    
    # Set environment variables
    set_env_vars()
    
    # Start the server
    server_process = start_server()
    if not server_process:
        return
    
    # Open the browser
    open_browser()
    
    # Instructions
    print("\n📝 Instructions:")
    print("  1. Test the web app in your browser")
    print("  2. For mobile testing, use your network IP or a tunneling service like ngrok")
    print("  3. To use with Telegram, set the WEBAPP_URL in your .env file")
    print("\n⚠️ Press Ctrl+C to stop the server and exit\n")
    
    try:
        # Display server output
        while True:
            if server_process.poll() is not None:
                # Process has exited
                print("\n❌ Server stopped unexpectedly")
                break
                
            # Read and print server output
            output = server_process.stdout.readline()
            if output:
                print(output.strip())
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        if server_process:
            # Send SIGTERM on Unix, or terminate on Windows
            if hasattr(signal, 'SIGTERM'):
                server_process.send_signal(signal.SIGTERM)
            else:
                server_process.terminate()
            
            # Wait for the process to terminate
            server_process.wait(timeout=5)
            print("✅ Server stopped successfully!")
    
    print("\n🙏 Thank you for using TikTok Report Helper!")
    print("=================================================\n")

if __name__ == "__main__":
    main()
