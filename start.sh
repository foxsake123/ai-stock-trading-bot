#!/bin/bash
# Railway start script - routes to correct service based on RAILWAY_SERVICE_NAME

if [ "$RAILWAY_SERVICE_NAME" = "stock-bot" ]; then
    echo "Starting Stock-Bot web server..."
    cd scripts/mcp && python stock_bot_server.py
else
    echo "Starting Trading Bot scheduler..."
    python railway_scheduler.py
fi
