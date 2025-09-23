"""
Post-Market Portfolio Updater
Runs daily at 4:30 PM ET after market close
Updates portfolio values, calculates P&L, and generates daily summary
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging
import requests

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
log_dir = '09_logs/portfolio'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/post_market_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class PostMarketUpdater:
    """Updates portfolio after market close and generates daily summary"""
    
    def __init__(self):
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Telegram settings
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
        
        # File paths
        self.portfolio_csv = '02_data/portfolio/positions/shorgan_bot_positions.csv'
        self.daily_report_dir = '07_docs/daily_reports'
        self.pnl_history = '02_data/portfolio/history/pnl_history.csv'
        
        os.makedirs(self.daily_report_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.pnl_history), exist_ok=True)
    
    def get_current_positions(self):
        """Fetch current positions from Alpaca"""
        try:
            positions = self.api.list_positions()
            
            position_data = []
            for pos in positions:
                position_data.append({
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'avg_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price or 0),
                    'market_value': float(pos.market_value or 0),
                    'cost_basis': float(pos.cost_basis or 0),
                    'unrealized_pnl': float(pos.unrealized_pl or 0),
                    'unrealized_pnl_pct': float(pos.unrealized_plpc or 0) * 100,
                    'change_today': float(pos.change_today or 0),
                    'change_today_pct': float(getattr(pos, 'change_today_pct', 0) or 0) * 100
                })
            
            return position_data
            
        except Exception as e:
            logging.error(f"Error fetching positions: {e}")
            return []
    
    def get_todays_trades(self):
        """Get all trades executed today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            orders = self.api.list_orders(
                status='all',
                after=f"{today}T00:00:00Z",
                direction='desc',
                limit=100
            )
            
            filled_orders = [o for o in orders if o.status == 'filled']
            
            trades = []
            for order in filled_orders:
                trades.append({
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': int(order.filled_qty or 0),
                    'price': float(order.filled_avg_price or 0),
                    'time': order.filled_at,
                    'order_type': order.order_type
                })
            
            return trades
            
        except Exception as e:
            logging.error(f"Error fetching today's trades: {e}")
            return []
    
    def calculate_daily_pnl(self, positions):
        """Calculate today's P&L"""
        realized_pnl = 0.0  # Would need trade pairs to calculate
        unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions)
        daily_change = sum(pos['change_today'] for pos in positions)
        
        return {
            'unrealized_pnl': unrealized_pnl,
            'daily_change': daily_change,
            'realized_pnl': realized_pnl,  # Placeholder
            'total_pnl': unrealized_pnl + realized_pnl
        }
    
    def update_portfolio_csv(self, positions):
        """Update the portfolio CSV file"""
        try:
            df = pd.DataFrame(positions)
            
            # Add timestamp
            df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to CSV
            df.to_csv(self.portfolio_csv, index=False)
            logging.info(f"Updated portfolio CSV with {len(positions)} positions")
            
        except Exception as e:
            logging.error(f"Error updating portfolio CSV: {e}")
    
    def update_pnl_history(self, pnl_data, account_value):
        """Track P&L history over time"""
        try:
            # Load existing history or create new
            if os.path.exists(self.pnl_history):
                df = pd.read_csv(self.pnl_history)
            else:
                df = pd.DataFrame()
            
            # Add today's data
            new_row = pd.DataFrame([{
                'date': datetime.now().strftime('%Y-%m-%d'),
                'portfolio_value': account_value,
                'unrealized_pnl': pnl_data['unrealized_pnl'],
                'realized_pnl': pnl_data['realized_pnl'],
                'daily_change': pnl_data['daily_change'],
                'total_pnl': pnl_data['total_pnl']
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Keep last 90 days
            df = df.tail(90)
            
            # Save
            df.to_csv(self.pnl_history, index=False)
            logging.info("Updated P&L history")
            
        except Exception as e:
            logging.error(f"Error updating P&L history: {e}")
    
    def generate_daily_report(self, data):
        """Generate daily summary report"""
        
        report = f"""# SHORGAN-BOT Daily Report
## {datetime.now().strftime('%B %d, %Y')}

---

## Portfolio Summary
- **Total Value**: ${data['account']['portfolio_value']:,.2f}
- **Cash Balance**: ${data['account']['cash']:,.2f}
- **Buying Power**: ${data['account']['buying_power']:,.2f}
- **Day's Change**: ${data['pnl']['daily_change']:,.2f}
- **Unrealized P&L**: ${data['pnl']['unrealized_pnl']:,.2f}

---

## Today's Trading Activity
**Trades Executed**: {len(data['trades'])}

"""
        
        if data['trades']:
            report += "| Time | Symbol | Side | Qty | Price | Value |\n"
            report += "|------|--------|------|-----|-------|-------|\n"
            
            for trade in data['trades'][:10]:  # Show last 10 trades
                time_str = trade['time'].strftime('%H:%M') if trade['time'] else 'N/A'
                value = trade['quantity'] * trade['price']
                report += f"| {time_str} | {trade['symbol']} | {trade['side'].upper()} | {trade['quantity']} | ${trade['price']:.2f} | ${value:,.2f} |\n"
        
        report += f"""
---

## Current Positions ({len(data['positions'])})

### Top Gainers Today
"""
        
        # Sort by daily change
        sorted_positions = sorted(data['positions'], key=lambda x: x['change_today_pct'], reverse=True)
        
        for pos in sorted_positions[:3]:
            if pos['change_today_pct'] > 0:
                report += f"- **{pos['symbol']}**: +{pos['change_today_pct']:.2f}% (${pos['change_today']:,.2f})\n"
        
        report += """
### Top Losers Today
"""
        
        for pos in sorted_positions[-3:]:
            if pos['change_today_pct'] < 0:
                report += f"- **{pos['symbol']}**: {pos['change_today_pct']:.2f}% (${pos['change_today']:,.2f})\n"
        
        report += f"""
---

## Position Details

| Symbol | Qty | Avg Cost | Current | Today % | Total P&L | P&L % |
|--------|-----|----------|---------|---------|-----------|-------|
"""
        
        for pos in data['positions']:
            report += f"| {pos['symbol']} | {pos['quantity']} | ${pos['avg_price']:.2f} | ${pos['current_price']:.2f} | {pos['change_today_pct']:+.2f}% | ${pos['unrealized_pnl']:,.2f} | {pos['unrealized_pnl_pct']:+.2f}% |\n"
        
        report += f"""
---

## Risk Metrics
- **Number of Positions**: {len(data['positions'])}
- **Largest Position**: {data['largest_position']['symbol'] if data['largest_position'] else 'N/A'} ({data['largest_position']['pct']:.1f}% of portfolio)
- **Portfolio Beta**: ~1.0 (target)
- **Cash Available**: ${data['account']['cash']:,.2f}

---

*Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}*
"""
        
        return report
    
    def send_telegram_summary(self, data):
        """Send daily summary via Telegram"""
        try:
            emoji = "📈" if data['pnl']['daily_change'] >= 0 else "📉"
            
            message = f"""{emoji} <b>SHORGAN-BOT Daily Summary</b>
            
📅 {datetime.now().strftime('%B %d, %Y')}
💰 Portfolio: ${data['account']['portfolio_value']:,.2f}
📊 Day's Change: ${data['pnl']['daily_change']:+,.2f}
📈 Unrealized P&L: ${data['pnl']['unrealized_pnl']:+,.2f}

<b>Today's Activity:</b>
• Trades: {len(data['trades'])}
• Positions: {len(data['positions'])}
• Cash: ${data['account']['cash']:,.2f}

<b>Top Movers:</b>"""
            
            # Add top gainers
            sorted_pos = sorted(data['positions'], key=lambda x: x['change_today_pct'], reverse=True)
            
            if sorted_pos and sorted_pos[0]['change_today_pct'] > 0:
                top = sorted_pos[0]
                message += f"\n🟢 {top['symbol']}: {top['change_today_pct']:+.2f}%"
            
            if sorted_pos and sorted_pos[-1]['change_today_pct'] < 0:
                bottom = sorted_pos[-1]
                message += f"\n🔴 {bottom['symbol']}: {bottom['change_today_pct']:.2f}%"
            
            # Send message
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logging.info("Telegram summary sent successfully")
            else:
                logging.error(f"Failed to send Telegram: {response.text}")
                
        except Exception as e:
            logging.error(f"Error sending Telegram summary: {e}")
    
    def run(self):
        """Run post-market update"""
        logging.info("="*60)
        logging.info("POST-MARKET PORTFOLIO UPDATE")
        logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        logging.info("="*60)
        
        try:
            # Get account info
            account = self.api.get_account()
            account_data = {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity)
            }
            
            # Get positions
            positions = self.get_current_positions()
            
            # Get today's trades
            trades = self.get_todays_trades()
            
            # Calculate P&L
            pnl_data = self.calculate_daily_pnl(positions)
            
            # Find largest position
            largest_position = None
            if positions:
                largest = max(positions, key=lambda x: x['market_value'])
                largest_position = {
                    'symbol': largest['symbol'],
                    'pct': (largest['market_value'] / account_data['portfolio_value']) * 100
                }
            
            # Compile all data
            data = {
                'account': account_data,
                'positions': positions,
                'trades': trades,
                'pnl': pnl_data,
                'largest_position': largest_position
            }
            
            # Update portfolio CSV
            self.update_portfolio_csv(positions)
            
            # Update P&L history
            self.update_pnl_history(pnl_data, account_data['portfolio_value'])
            
            # Generate report
            report = self.generate_daily_report(data)
            
            # Save report
            report_file = f"{self.daily_report_dir}/daily_report_{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            logging.info(f"Daily report saved to {report_file}")
            
            # Send Telegram summary
            self.send_telegram_summary(data)
            
            logging.info("="*60)
            logging.info("POST-MARKET UPDATE COMPLETE")
            logging.info(f"Positions: {len(positions)}, Trades Today: {len(trades)}")
            logging.info(f"Day's P&L: ${pnl_data['daily_change']:+,.2f}")
            logging.info("="*60)
            
        except Exception as e:
            logging.error(f"Post-market update failed: {e}")


if __name__ == "__main__":
    updater = PostMarketUpdater()
    updater.run()