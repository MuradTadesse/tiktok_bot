#!/bin/bash
# TikTok Report Helper - WebApp Startup Script
# Created by Murad Tadesse

# Configuration 
WEBAPP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8080
LOG_FILE="$WEBAPP_DIR/webapp.log"
PID_FILE="$WEBAPP_DIR/webapp.pid"

# Check if the server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "WebApp is already running with PID: $PID"
        exit 1
    else
        echo "Removing stale PID file."
        rm "$PID_FILE"
    fi
fi

# Launch the server
echo "Starting TikTok Report Helper WebApp on port $PORT..."
cd "$WEBAPP_DIR"

# Start the server in the background
nohup python3 simple_server.py > "$LOG_FILE" 2>&1 &

# Save the PID
PID=$!
echo $PID > "$PID_FILE"
echo "WebApp started with PID: $PID"
echo "Log file: $LOG_FILE"
