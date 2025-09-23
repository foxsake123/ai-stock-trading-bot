# Telegram Bot Setup Guide

## Setting Up Telegram Bot for Report Delivery

### Step 1: Create a Telegram Bot
1. Open Telegram and search for **@BotFather**
2. Start a conversation and send `/newbot`
3. Choose a name for your bot (e.g., "AI Trading Reports")
4. Choose a username ending in 'bot' (e.g., "ai_trading_reports_bot")
5. Save the **Bot Token** you receive (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID
1. Start a conversation with your new bot
2. Send any message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":` in the response - that's your Chat ID

### Step 3: Configure the Bot in Code

Add your credentials to the report generator:

```python
# In enhanced_post_market_report.py
report = EnhancedPostMarketReport()
report.setup_telegram(
    bot_token="YOUR_BOT_TOKEN_HERE",
    chat_ids=["YOUR_CHAT_ID_HERE"]  # Can add multiple IDs for group delivery
)
```

### Step 4: Test the Setup
Run the report generator - you should receive:
- Text summary message
- PDF reports for both DEE-BOT and SHORGAN-BOT

### Security Note
**NEVER commit your bot token to version control!**

Use environment variables instead:
```python
import os
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
```

### Features
- Separate PDF reports for each bot
- Emoji indicators for performance
- Real-time delivery after market close
- Multi-recipient support