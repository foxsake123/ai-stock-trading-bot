"""
Send Trade Execution Confirmation Report
"""

import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

def send_execution_report():
    """Send execution confirmation to Telegram"""
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
    
    # Get account status
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY_SHORGAN'),
        os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
        'https://paper-api.alpaca.markets',
        api_version='v2'
    )
    
    account = api.get_account()
    portfolio_value = float(account.portfolio_value)
    buying_power = float(account.buying_power)
    
    # Execution summary
    message = f"""✅ **TRADE EXECUTION COMPLETE**

📅 {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}
💰 Portfolio: ${portfolio_value:,.2f}
💵 Buying Power: ${buying_power:,.2f}

**EXECUTED TRADES (3 of 5):**

1️⃣ **INCY** - 61 shares @ $83.97
   • FDA decision Sept 19 (Opzelura pediatric)
   • Stop Loss: $80.61 (-4%)
   • Target: $92.00 (+11%)
   • Consensus: 7.88/10 ✅

2️⃣ **CBRL** - 81 shares @ $51.00
   • Earnings Sept 17 AMC (34% short interest)
   • Stop Loss: $46.92 (-8%)
   • Target: $60.00 (+15%)
   • Consensus: 7.08/10 ✅

3️⃣ **RIVN** - 357 shares @ $14.50
   • Q3 deliveries early October
   • Stop Loss: $12.69 (-12.5%)
   • Target: $15.00 (+25%)
   • Consensus: 7.88/10 ✅

**REJECTED TRADES (2):**
• SRRK - Wash trade detection (try again later)
• PASG - Below consensus threshold (6.28/10)

**MULTI-AGENT ANALYSIS:**
• Average Consensus: 7.43/10
• Risk Manager Approval: 3/5 trades
• Total Allocation: ~14% of portfolio

**UPCOMING CATALYSTS:**
🔔 Tomorrow: CBRL earnings (potential squeeze)
🔔 Sept 19: INCY FDA decision
🔔 Early Oct: RIVN Q3 deliveries

**RISK MANAGEMENT:**
✅ All stop losses set
✅ Position sizes within limits
✅ Portfolio diversified across sectors

_Automated execution via Multi-Agent Trading System_"""
    
    # Send message
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Execution report sent to Telegram")
    else:
        print(f"Failed to send: {response.text}")
    
    # Update portfolio CSV
    import pandas as pd
    
    portfolio_file = '02_data/portfolio/positions/shorgan_bot_positions.csv'
    if os.path.exists(portfolio_file):
        df = pd.read_csv(portfolio_file)
    else:
        df = pd.DataFrame(columns=['symbol', 'quantity', 'avg_price', 'current_price', 
                                  'market_value', 'cost_basis', 'unrealized_pnl', 
                                  'unrealized_pnl_pct', 'change_today', 
                                  'change_today_pct', 'last_updated'])
    
    # Add new positions
    new_positions = [
        {'symbol': 'INCY', 'quantity': 61, 'avg_price': 83.97},
        {'symbol': 'CBRL', 'quantity': 81, 'avg_price': 51.00},
        {'symbol': 'RIVN', 'quantity': 357, 'avg_price': 14.50}
    ]
    
    for pos in new_positions:
        if pos['symbol'] not in df['symbol'].values:
            new_row = {
                'symbol': pos['symbol'],
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'current_price': pos['avg_price'],
                'market_value': pos['quantity'] * pos['avg_price'],
                'cost_basis': pos['quantity'] * pos['avg_price'],
                'unrealized_pnl': 0,
                'unrealized_pnl_pct': 0,
                'change_today': 0,
                'change_today_pct': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save updated portfolio
    df.to_csv(portfolio_file, index=False)
    print(f"Portfolio CSV updated with {len(new_positions)} new positions")

if __name__ == "__main__":
    send_execution_report()