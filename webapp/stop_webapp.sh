#!/bin/bash
# TikTok Report Helper - WebApp Stop Script
# Created by Murad Tadesse

# Configuration
WEBAPP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$WEBAPP_DIR/webapp.pid"

# Check if the PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "WebApp is not running (no PID file found)."
    exit 0
fi

# Get the PID
PID=$(cat "$PID_FILE")

# Check if the process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "WebApp is not running (process not found). Removing stale PID file."
    rm "$PID_FILE"
    exit 0
fi

# Kill the process
echo "Stopping WebApp (PID: $PID)..."
kill "$PID"

# Wait for the process to terminate
for i in {1..5}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        break
    fi
    echo "Waiting for WebApp to terminate... ($i/5)"
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "WebApp did not terminate gracefully. Force killing..."
    kill -9 "$PID"
fi

# Remove PID file
rm "$PID_FILE"
echo "WebApp stopped."
