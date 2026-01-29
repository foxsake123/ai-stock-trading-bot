#!/bin/bash
# Railway start script - routes to correct service based on RAILWAY_SERVICE_NAME

echo "Service name: $RAILWAY_SERVICE_NAME"
echo "Current directory: $(pwd)"

if [ "$RAILWAY_SERVICE_NAME" = "stock-bot" ]; then
    echo "Starting Stock-Bot web server..."
    cd scripts/mcp
    echo "Changed to: $(pwd)"
    echo "Files here: $(ls -la)"
    python3 stock_bot_server.py || python stock_bot_server.py
else
    echo "Starting Trading Bot scheduler..."
    python3 railway_scheduler.py || python railway_scheduler.py
fi
