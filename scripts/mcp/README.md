# Stock-Bot MCP Server

A hosted MCP (Model Context Protocol) server for AI-powered stock trading via Claude Desktop.

## Features

- **Multi-user support**: Each user gets their own API key
- **Encrypted credentials**: Alpaca API keys stored encrypted
- **Two strategies**: DEE-BOT (conservative) and SHORGAN (aggressive)
- **Rate limiting**: 60 requests/minute per user
- **Paper & Live trading**: Support for both modes

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Generate a master key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variable
export MASTER_KEY="your-generated-key-here"

# Start server
docker-compose up -d

# Server running at http://localhost:8000
```

### Option 2: Local Python

```bash
# Install dependencies
pip install aiohttp aiohttp-cors alpaca-py cryptography

# Generate a master key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variable
export MASTER_KEY="your-generated-key-here"

# Run server
python stock_bot_server.py
```

### Option 3: Cloud Deployment

Deploy to Railway, Render, Fly.io, or any cloud platform:

1. Set `MASTER_KEY` environment variable
2. Deploy the Dockerfile or Python script
3. Note your server URL

## User Setup

### Step 1: Register for API Key

```bash
curl -X POST https://your-server.com/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com"}'
```

Response:
```json
{
  "ok": true,
  "user_id": "a1b2c3d4",
  "api_key": "sb_XXXXXXXXXXXX",
  "message": "Save your API key - it won't be shown again!"
}
```

### Step 2: Configure Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "stock-bot": {
      "url": "https://your-server.com/mcp",
      "headers": {
        "Authorization": "Bearer sb_YOUR_API_KEY_HERE"
      }
    }
  }
}
```

### Step 3: Connect Alpaca Account

In Claude Desktop, say:
> "Connect my Alpaca paper trading account"

Claude will ask for your Alpaca API credentials.

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/register` | POST | No | Create user, get API key |
| `/accounts` | POST | Yes | Add Alpaca account |
| `/accounts` | GET | Yes | List accounts |
| `/accounts/{id}` | DELETE | Yes | Remove account |
| `/accounts/{id}/portfolio` | GET | Yes | Get portfolio |
| `/accounts/{id}/run/{strategy}` | POST | Yes | Run strategy |
| `/mcp` | GET | Yes | MCP SSE endpoint |

## Strategies

### DEE-BOT (Conservative)
- Dividend-focused portfolio
- 11% stop loss
- Target allocations: CVX 14%, GILD 14%, JNJ 10%, etc.
- Automatic rebalancing

### SHORGAN (Aggressive)
- Catalyst-driven trading
- 18% stop loss, 25% take profit
- Supports long and short positions
- Automatic profit taking

## Example Usage in Claude

Once connected, you can say things like:

> "Show me my portfolio"

> "Run DEE-BOT in dry run mode"

> "What would SHORGAN recommend for my account?"

> "Execute the SHORGAN strategy (confirm live)"

## Security

- API keys are hashed (SHA-256)
- Alpaca credentials are encrypted (Fernet/AES)
- PBKDF2 key derivation (480,000 iterations)
- Rate limiting prevents abuse
- Per-user data isolation

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MASTER_KEY` | Yes | - | 32+ char encryption key |
| `PORT` | No | 8000 | Server port |
| `HOST` | No | 0.0.0.0 | Server host |
| `DATA_DIR` | No | ./data/stock_bot_hosted | Data directory |

## License

MIT License - Use at your own risk. Not financial advice.
