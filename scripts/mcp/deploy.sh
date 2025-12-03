#!/bin/bash
# Stock-Bot MCP Server Deployment Script
# Usage: ./deploy.sh [platform]
# Platforms: railway, render, fly, local

set -e

PLATFORM=${1:-local}

echo "========================================"
echo "Stock-Bot MCP Server Deployment"
echo "========================================"

# Generate master key if not set
if [ -z "$MASTER_KEY" ]; then
    echo "Generating new MASTER_KEY..."
    MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "MASTER_KEY=$MASTER_KEY"
    echo ""
    echo "IMPORTANT: Save this key! You'll need it to decrypt user data."
    echo ""
fi

case $PLATFORM in
    local)
        echo "Starting local server..."
        export MASTER_KEY
        python3 stock_bot_server.py
        ;;

    docker)
        echo "Building and starting Docker container..."
        docker-compose up -d --build
        echo ""
        echo "Server running at http://localhost:8000"
        ;;

    railway)
        echo "Deploying to Railway..."
        echo ""
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Create project: railway init"
        echo "4. Set secrets: railway variables set MASTER_KEY=$MASTER_KEY"
        echo "5. Deploy: railway up"
        echo ""
        echo "Or use the dashboard: https://railway.app"
        ;;

    render)
        echo "Deploying to Render..."
        echo ""
        echo "1. Go to https://render.com"
        echo "2. Create new Web Service"
        echo "3. Connect your GitHub repo"
        echo "4. Set Build Command: pip install aiohttp aiohttp-cors alpaca-py cryptography"
        echo "5. Set Start Command: python scripts/mcp/stock_bot_server.py"
        echo "6. Add Environment Variable: MASTER_KEY=$MASTER_KEY"
        echo "7. Deploy"
        ;;

    fly)
        echo "Deploying to Fly.io..."
        echo ""
        echo "1. Install Fly CLI: curl -L https://fly.io/install.sh | sh"
        echo "2. Login: fly auth login"
        echo "3. Launch: fly launch --dockerfile scripts/mcp/Dockerfile"
        echo "4. Set secret: fly secrets set MASTER_KEY=$MASTER_KEY"
        echo "5. Deploy: fly deploy"
        ;;

    *)
        echo "Unknown platform: $PLATFORM"
        echo ""
        echo "Usage: ./deploy.sh [platform]"
        echo "Platforms:"
        echo "  local   - Run locally"
        echo "  docker  - Run with Docker"
        echo "  railway - Deploy to Railway"
        echo "  render  - Deploy to Render"
        echo "  fly     - Deploy to Fly.io"
        exit 1
        ;;
esac

echo ""
echo "Done!"
