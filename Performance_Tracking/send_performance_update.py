"""
Send Daily Performance Update to Telegram
This is PERFORMANCE TRACKING, not research
"""

import json
import os
import telegram
from telegram import Bot
import asyncio
from datetime import datetime
from pathlib import Path

class PerformanceReporter:
    """Send performance updates via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '7870288896')
        self.date = datetime.now().strftime('%Y-%m-%d')
        
    async def send_performance_update(self):
        """Send performance update to Telegram"""
        # Load today's performance data
        perf_dir = Path(f"daily_performance/{self.date}")
        if not perf_dir.exists():
            print("[ERROR] No performance data for today")
            return
        
        # Get most recent performance file
        perf_files = list(perf_dir.glob("performance_*.json"))
        if not perf_files:
            print("[ERROR] No performance files found")
            return
            
        latest_file = max(perf_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Create performance message
        message = self.format_performance_message(data)
        
        # Send to Telegram
        try:
            bot = Bot(token=self.bot_token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            print("[SUCCESS] Performance update sent to Telegram!")
            
        except Exception as e:
            print(f"[ERROR] Failed to send: {str(e)}")
    
    def format_performance_message(self, data):
        """Format performance data as Telegram message"""
        dee_bot = data.get('dee_bot', {}).get('metrics', {})
        shorgan_bot = data.get('shorgan_bot', {}).get('metrics', {})
        combined = data.get('combined', {})
        
        # Determine overall status emoji
        total_pnl = combined.get('total_return', 0)
        if total_pnl > 1000:
            status_emoji = "🚀"
        elif total_pnl > 0:
            status_emoji = "📈"
        elif total_pnl < 0:
            status_emoji = "📉"
        else:
            status_emoji = "➡️"
        
        message = f"""
{status_emoji} *DAILY PERFORMANCE UPDATE*
📅 {self.date}
⏰ {datetime.now().strftime('%I:%M %p ET')}

━━━━━━━━━━━━━━━━━━
📊 *DEE-BOT PERFORMANCE*
Strategy: S&P 100 Multi-Agent

💰 Portfolio: ${dee_bot.get('current_value', 100000):,.2f}
📈 Daily P&L: ${dee_bot.get('daily_pnl', 0):,.2f} ({dee_bot.get('daily_pnl_pct', 0):.2f}%)
🎯 Total Return: ${dee_bot.get('total_pnl', 0):,.2f} ({dee_bot.get('total_return_pct', 0):.2f}%)
📍 Positions: {dee_bot.get('position_count', 0)}
🏆 Win Rate: {dee_bot.get('win_rate', 0):.1f}%
"""
        
        # Add largest winner/loser for DEE-BOT
        if dee_bot.get('largest_winner'):
            winner = dee_bot['largest_winner']
            message += f"✅ Best: {winner['symbol']} +${winner['pnl']:.2f}\n"
        if dee_bot.get('largest_loser'):
            loser = dee_bot['largest_loser']
            message += f"❌ Worst: {loser['symbol']} ${loser['pnl']:.2f}\n"
            
        message += f"""
━━━━━━━━━━━━━━━━━━
⚡ *SHORGAN-BOT PERFORMANCE*
Strategy: Catalyst Event Trading

💰 Portfolio: ${shorgan_bot.get('current_value', 100000):,.2f}
📈 Daily P&L: ${shorgan_bot.get('daily_pnl', 0):,.2f} ({shorgan_bot.get('daily_pnl_pct', 0):.2f}%)
🎯 Total Return: ${shorgan_bot.get('total_pnl', 0):,.2f} ({shorgan_bot.get('total_return_pct', 0):.2f}%)
📍 Positions: {shorgan_bot.get('position_count', 0)}
🏆 Win Rate: {shorgan_bot.get('win_rate', 0):.1f}%
"""
        
        # Add largest winner/loser for SHORGAN-BOT
        if shorgan_bot.get('largest_winner'):
            winner = shorgan_bot['largest_winner']
            message += f"✅ Best: {winner['symbol']} +${winner['pnl']:.2f}\n"
        if shorgan_bot.get('largest_loser'):
            loser = shorgan_bot['largest_loser']
            message += f"❌ Worst: {loser['symbol']} ${loser['pnl']:.2f}\n"
            
        # Combined summary
        message += f"""
━━━━━━━━━━━━━━━━━━
💼 *COMBINED PORTFOLIO*

💵 Total Value: ${combined.get('total_value', 200000):,.2f}
📊 Daily P&L: ${combined.get('total_daily_pnl', 0):,.2f}
🎯 Total Return: ${combined.get('total_return', 0):,.2f}
📍 Total Positions: {combined.get('total_positions', 0)}

#TradingPerformance #AlpacaPaperTrading
"""
        
        return message

if __name__ == "__main__":
    reporter = PerformanceReporter()
    asyncio.run(reporter.send_performance_update())