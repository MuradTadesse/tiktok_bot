#!/bin/bash
# TikTok Report Helper - WebApp Configuration
# Created by Murad Tadesse

# Set your domain or hosting URL here
WEBAPP_URL="https://your-domain.com"

# Add the WEBAPP_URL to the environment file
if [ -f "../.env" ]; then
    # Check if WEBAPP_URL already exists in .env
    if grep -q "WEBAPP_URL" "../.env"; then
        # Update existing WEBAPP_URL
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=$WEBAPP_URL|g" "../.env"
    else
        # Add WEBAPP_URL to .env
        echo "WEBAPP_URL=$WEBAPP_URL" >> "../.env"
    fi
    echo "Updated .env file with WEBAPP_URL=$WEBAPP_URL"
else
    # Create new .env file
    echo "WEBAPP_URL=$WEBAPP_URL" > "../.env"
    echo "Created new .env file with WEBAPP_URL=$WEBAPP_URL"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Make scripts executable
chmod +x start_webapp.sh stop_webapp.sh monitor_webapp.sh

echo "Configuration complete!"
echo "Edit this file to change your WEBAPP_URL before running."
