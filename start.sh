#!/bin/bash
# Railway start script - routes to correct service based on RAILWAY_SERVICE_NAME

echo "=========================================="
echo "START.SH - Railway Service Router"
echo "=========================================="
echo "RAILWAY_SERVICE_NAME = '$RAILWAY_SERVICE_NAME'"
echo "Current directory: $(pwd)"
echo "All RAILWAY_ vars:"
env | grep RAILWAY_ || echo "(none found)"
echo "=========================================="

if [ "$RAILWAY_SERVICE_NAME" = "stock-bot" ]; then
    echo "[ROUTING] -> Stock-Bot web server"
    cd scripts/mcp
    echo "Changed to: $(pwd)"
    python3 stock_bot_server.py || python stock_bot_server.py
elif [ "$RAILWAY_SERVICE_NAME" = "trading-bot" ]; then
    echo "[ROUTING] -> Trading Bot scheduler"
    python3 railway_scheduler.py || python railway_scheduler.py
else
    echo "[ROUTING] Unknown service '$RAILWAY_SERVICE_NAME', defaulting to trading-bot"
    python3 railway_scheduler.py || python railway_scheduler.py
fi
