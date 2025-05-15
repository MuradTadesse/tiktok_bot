#!/bin/bash
# TikTok Report Helper - Production Deployment Script
# Created by Murad Tadesse
#
# This script sets up the webapp for production deployment on a Linux server

# Configuration
WEBAPP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN_NAME="${1:-example.com}"
PORT=8080
LOG_FILE="$WEBAPP_DIR/webapp.log"

# Check if running as root (needed for some operations)
if [ "$EUID" -ne 0 ]; then
  echo "NOTE: Some operations may require root privileges."
fi

echo "====================================================="
echo "  TikTok Report Helper - Production Deployment"
echo "====================================================="
echo "Deploying webapp to: $WEBAPP_DIR"
echo "Domain: $DOMAIN_NAME"
echo "Port: $PORT"
echo

# Create required directories
mkdir -p "$WEBAPP_DIR/logs"

# Install dependencies if needed
echo "Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Create or update the .env file for the webapp
echo "Configuring environment..."
cat > "$WEBAPP_DIR/../.env" << EOF
# Existing variables
$(grep -v "WEBAPP_URL" "$WEBAPP_DIR/../.env" 2>/dev/null || echo "# Bot environment variables")

# Webapp configuration
WEBAPP_URL=https://$DOMAIN_NAME
WEBAPP_PORT=$PORT
EOF

echo "Environment file updated."

# Create a service file for systemd
echo "Creating systemd service file..."
cat > "$WEBAPP_DIR/deployment/tiktok-report-webapp.service" << EOF
[Unit]
Description=TikTok Report Helper Web Application
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WEBAPP_DIR
ExecStart=/usr/bin/python3 $WEBAPP_DIR/server.py
Restart=on-failure
Environment="PORT=$PORT"
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at: $WEBAPP_DIR/deployment/tiktok-report-webapp.service"
echo "To install the service:"
echo "  sudo cp $WEBAPP_DIR/deployment/tiktok-report-webapp.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable tiktok-report-webapp.service"
echo "  sudo systemctl start tiktok-report-webapp.service"

# Create an nginx configuration file
echo "Creating Nginx configuration..."
cat > "$WEBAPP_DIR/deployment/tiktok-report-webapp.nginx.conf" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    access_log /var/log/nginx/tiktok-report-webapp-access.log;
    error_log /var/log/nginx/tiktok-report-webapp-error.log;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

echo "Nginx configuration created at: $WEBAPP_DIR/deployment/tiktok-report-webapp.nginx.conf"
echo "To install the Nginx configuration:"
echo "  sudo cp $WEBAPP_DIR/deployment/tiktok-report-webapp.nginx.conf /etc/nginx/sites-available/"
echo "  sudo ln -s /etc/nginx/sites-available/tiktok-report-webapp.nginx.conf /etc/nginx/sites-enabled/"
echo "  sudo nginx -t"
echo "  sudo systemctl reload nginx"

# Create a production-ready server file
echo "Creating production server script..."
cat > "$WEBAPP_DIR/production_server.py" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Report Helper - Production Web Server
Created by Murad Tadesse
"""

import os
import sys
import logging
from pathlib import Path
import http.server
import socketserver
from threading import Thread
import time

# Configuration
PORT = int(os.environ.get('PORT', 8080))
WEBAPP_DIR = Path(__file__).parent.absolute()
LOG_FILE = WEBAPP_DIR / "logs" / "webapp.log"

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
    
    # Try to start the server
    retries = 5
    while retries > 0:
        try:
            with socketserver.TCPServer(("", PORT), handler) as httpd:
                logger.info(f"Starting server at http://0.0.0.0:{PORT}")
                logger.info(f"Serving files from: {WEBAPP_DIR}")
                
                # Start the server
                httpd.serve_forever()
                
        except OSError as e:
            if e.errno == 98:  # Address already in use
                logger.warning(f"Port {PORT} is already in use. Retrying in 5 seconds...")
                retries -= 1
                time.sleep(5)
            else:
                logger.error(f"Error starting server: {e}")
                sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)
    
    logger.error(f"Failed to start server after multiple attempts")
    sys.exit(1)

def healthcheck_thread():
    """Run a background thread for health checks and maintenance."""
    while True:
        try:
            # Log a health check message every hour
            logger.info("Server health check - Running")
            time.sleep(3600)  # 1 hour
        except Exception as e:
            logger.error(f"Health check error: {e}")
            time.sleep(60)  # Wait a minute and try again

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Start health check thread
    Thread(target=healthcheck_thread, daemon=True).start()
    
    # Start the server
    start_server()
EOF

echo "Production server script created at: $WEBAPP_DIR/production_server.py"
echo "To make it executable:"
echo "  chmod +x $WEBAPP_DIR/production_server.py"

# Modify the bot launcher script to include the webapp URL
echo "Updating bot launcher script..."
if [ -f "$WEBAPP_DIR/../bot_launcher.sh" ]; then
    if ! grep -q "WEBAPP_URL" "$WEBAPP_DIR/../bot_launcher.sh"; then
        sed -i "/export TELEGRAM_BOT_TOKEN/a export WEBAPP_URL=https://$DOMAIN_NAME" "$WEBAPP_DIR/../bot_launcher.sh"
        echo "Bot launcher script updated with WEBAPP_URL."
    else
        echo "Bot launcher script already contains WEBAPP_URL."
    fi
else
    echo "Bot launcher script not found. You may need to update it manually."
fi

# Deployment summary
echo "====================================================="
echo "         Deployment Preparation Complete"
echo "====================================================="
echo
echo "Next steps:"
echo
echo "1. Copy the webapp files to your server:"
echo "   scp -r $WEBAPP_DIR user@your-server:~/tiktok_bot/"
echo
echo "2. Install the systemd service:"
echo "   Follow the instructions above to install the service"
echo
echo "3. Configure Nginx:"
echo "   Follow the instructions above to set up Nginx"
echo
echo "4. Set up SSL (recommended):"
echo "   sudo certbot --nginx -d $DOMAIN_NAME"
echo
echo "5. Restart your bot to use the webapp:"
echo "   sudo systemctl restart your-bot-service-name"
echo
echo "====================================================="
