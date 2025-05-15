#!/bin/bash
# TikTok Report Helper - WebApp Monitoring Script
# Created by Murad Tadesse

# Configuration
WEBAPP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$WEBAPP_DIR/webapp.pid"
LOG_FILE="$WEBAPP_DIR/monitor.log"

# Check if the webapp is running
if [ ! -f "$PID_FILE" ]; then
    echo "[$(date)] WebApp is not running (no PID file). Starting..." >> "$LOG_FILE"
    "$WEBAPP_DIR/start_webapp.sh"
    exit 0
fi

# Get the PID
PID=$(cat "$PID_FILE")

# Check if the process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "[$(date)] WebApp crashed or not running (PID: $PID). Restarting..." >> "$LOG_FILE"
    rm "$PID_FILE"
    "$WEBAPP_DIR/start_webapp.sh"
else
    echo "[$(date)] WebApp is running correctly (PID: $PID)" >> "$LOG_FILE"
fi
