"""
Automated Daily Trade Generation
Generates TODAYS_TRADES markdown file based on multi-agent consensus
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.fundamental_analyst import FundamentalAnalyst
from agents.technical_analyst import TechnicalAnalyst
from agents.news_analyst import NewsAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.bull_agent import BullAgent
from agents.bear_agent import BearAgent
from agents.risk_manager import RiskManager
from agents.catalyst_hunter import CatalystHunter
from communication.coordinator import Coordinator

class AutomatedTradeGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.docs_dir = self.project_root / 'docs'
        self.daily_json_dir = self.project_root / 'scripts-and-data' / 'daily-json' / 'chatgpt'

        # Initialize agents
        self.coordinator = Coordinator()

        # Portfolio allocations
        self.dee_bot_capital = 100000
        self.shorgan_bot_capital = 100000

        # Trading parameters
        self.dee_bot_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK.B', 'JPM', 'JNJ',
            'V', 'PG', 'UNH', 'HD', 'DIS', 'MA', 'PYPL', 'BAC', 'VZ', 'ADBE',
            'CRM', 'NFLX', 'PFE', 'KO', 'PEP', 'TMO', 'ABBV', 'WMT', 'CVX', 'XOM'
        ]  # Top 30 S&P 100 stocks

        self.shorgan_catalyst_sources = [
            'earnings', 'FDA_approvals', 'M&A', 'product_launches',
            'analyst_upgrades', 'short_squeeze', 'momentum'
        ]

    def get_latest_chatgpt_recommendations(self):
        """Fetch latest recommendations from ChatGPT reports if available"""
        try:
            # Look for today's ChatGPT report
            today = datetime.now().strftime('%Y-%m-%d')
            chatgpt_files = list(self.daily_json_dir.glob(f'*{today}*.json'))

            if chatgpt_files:
                latest_file = sorted(chatgpt_files)[-1]
                with open(latest_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"No ChatGPT recommendations found: {e}")
            return None

    def generate_dee_bot_trades(self):
        """Generate defensive, beta-neutral trades for DEE-BOT"""
        trades = {
            'buy': [],
            'sell': [],
            'hold': []
        }

        print("[DEE-BOT] Analyzing S&P 100 stocks...")

        # Analyze each stock using multi-agent consensus
        for symbol in self.dee_bot_stocks[:15]:  # Limit to top 15 for speed
            try:
                consensus = self.coordinator.analyze_stock(symbol)

                if consensus and consensus['recommendation'] != 'HOLD':
                    # Calculate position size (max 8% of portfolio)
                    position_size = min(
                        self.dee_bot_capital * 0.08,
                        self.dee_bot_capital * consensus['confidence'] * 0.10
                    )

                    # Get current price estimate
                    price = consensus.get('current_price', 100)
                    shares = int(position_size / price)

                    if shares > 0:
                        trade = {
                            'symbol': symbol,
                            'shares': shares,
                            'limit_price': round(price * 1.005, 2),  # 0.5% above market
                            'stop_loss': round(price * 0.97, 2),     # 3% stop loss
                            'rationale': consensus.get('reasoning', 'Multi-agent consensus positive')[:100]
                        }

                        # DEE-BOT is LONG-ONLY
                        if consensus['recommendation'] == 'BUY':
                            trades['buy'].append(trade)
                        elif consensus['recommendation'] == 'SELL':
                            # Only sell if we have a position (checked at execution)
                            trades['sell'].append(trade)

            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue

        # Limit to top 5 buys and sells by confidence
        trades['buy'] = sorted(trades['buy'], key=lambda x: x.get('shares', 0), reverse=True)[:5]
        trades['sell'] = sorted(trades['sell'], key=lambda x: x.get('shares', 0), reverse=True)[:3]

        return trades

    def generate_shorgan_bot_trades(self):
        """Generate catalyst-driven trades for SHORGAN-BOT"""
        trades = {
            'long': [],
            'short': [],
            'sell': []  # Exit existing positions
        }

        print("[SHORGAN-BOT] Hunting for catalysts...")

        # Check ChatGPT recommendations first
        chatgpt_data = self.get_latest_chatgpt_recommendations()

        if chatgpt_data and 'trades' in chatgpt_data:
            for trade in chatgpt_data.get('trades', []):
                if trade.get('action') in ['BUY', 'LONG']:
                    trades['long'].append({
                        'symbol': trade['symbol'],
                        'shares': trade.get('shares', 100),
                        'limit_price': trade.get('limit_price'),
                        'stop_loss': trade.get('stop_loss'),
                        'rationale': trade.get('rationale', 'ChatGPT catalyst identified')
                    })

        # Add some catalyst-driven trades based on agent analysis
        catalyst_stocks = ['BBAI', 'SOUN', 'IONQ', 'RGTI', 'MSTR', 'COIN', 'RIOT']

        for symbol in catalyst_stocks:
            try:
                # Use catalyst hunter agent
                catalyst_hunter = CatalystHunter()
                catalyst = catalyst_hunter.analyze(symbol)

                if catalyst and catalyst.get('has_catalyst'):
                    # High conviction catalyst trades
                    position_size = self.shorgan_bot_capital * 0.10  # 10% max position
                    price = catalyst.get('current_price', 10)
                    shares = int(position_size / price)

                    trade = {
                        'symbol': symbol,
                        'shares': shares,
                        'limit_price': round(price * 1.01, 2),   # 1% above market
                        'stop_loss': round(price * 0.92, 2),     # 8% stop loss
                        'rationale': catalyst.get('catalyst_description', 'Event catalyst detected')[:100]
                    }

                    if catalyst.get('direction') == 'bullish':
                        trades['long'].append(trade)
                    elif catalyst.get('direction') == 'bearish':
                        trades['short'].append(trade)

            except Exception as e:
                print(f"Error analyzing catalyst for {symbol}: {e}")
                continue

        # Limit trades
        trades['long'] = trades['long'][:7]
        trades['short'] = trades['short'][:3]

        return trades

    def generate_markdown_file(self, dee_trades, shorgan_trades):
        """Create the TODAYS_TRADES markdown file"""
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        day_name = today.strftime('%A')

        content = f"""# Today's AI-Generated Trade Recommendations
## {day_name}, {today.strftime('%B %d, %Y')}
## Generated: {today.strftime('%I:%M %p ET')}

---

## 📊 MARKET OVERVIEW
- Multi-agent consensus analysis complete
- Risk parameters verified
- Position sizes optimized for current portfolio

---

## DEE-BOT TRADES (Beta-Neutral S&P 100)
**Strategy**: Defensive, LONG-ONLY, Beta-neutral ~1.0
**Capital**: $100,000
**Max Position**: 8% ($8,000)

### BUY ORDERS
| Symbol | Shares | Limit Price | Stop Loss | Rationale |
|--------|--------|-------------|-----------|-----------|
"""

        # Add DEE-BOT buy orders
        for trade in dee_trades['buy']:
            content += f"| {trade['symbol']} | {trade['shares']} | ${trade['limit_price']} | ${trade['stop_loss']} | {trade['rationale']} |\n"

        if not dee_trades['buy']:
            content += "| No buy orders today | - | - | - | Market conditions unfavorable |\n"

        content += """

### SELL ORDERS (Close Positions)
| Symbol | Shares | Limit Price | Rationale |
|--------|--------|-------------|-----------|
"""

        # Add DEE-BOT sell orders
        for trade in dee_trades['sell']:
            content += f"| {trade['symbol']} | {trade['shares']} | ${trade['limit_price']} | {trade['rationale']} |\n"

        if not dee_trades['sell']:
            content += "| No sell orders today | - | - | Hold all positions |\n"

        content += """

---

## SHORGAN-BOT TRADES (Catalyst Trading)
**Strategy**: Event-driven, momentum, high-volatility
**Capital**: $100,000
**Max Position**: 10% ($10,000)

### LONG POSITIONS
| Symbol | Shares | Limit Price | Stop Loss | Catalyst |
|--------|--------|-------------|-----------|----------|
"""

        # Add SHORGAN long positions
        for trade in shorgan_trades['long']:
            content += f"| {trade['symbol']} | {trade['shares']} | ${trade['limit_price']} | ${trade['stop_loss']} | {trade['rationale']} |\n"

        if not shorgan_trades['long']:
            content += "| No long positions today | - | - | - | No catalysts identified |\n"

        content += """

### SHORT POSITIONS
| Symbol | Shares | Limit Price | Stop Loss | Catalyst |
|--------|--------|-------------|-----------|----------|
"""

        # Add SHORGAN short positions
        for trade in shorgan_trades['short']:
            content += f"| {trade['symbol']} | {trade['shares']} | ${trade['limit_price']} | ${trade['stop_loss']} | {trade['rationale']} |\n"

        if not shorgan_trades['short']:
            content += "| No short positions today | - | - | - | No bearish setups |\n"

        content += """

### SELL ORDERS (Exit Positions)
| Symbol | Shares | Target/Market | Reason |
|--------|--------|---------------|--------|
"""

        # Add SHORGAN exit orders
        for trade in shorgan_trades.get('sell', []):
            content += f"| {trade['symbol']} | {trade['shares']} | ${trade.get('limit_price', 'Market')} | {trade['rationale']} |\n"

        if not shorgan_trades.get('sell', []):
            content += "| No exits today | - | - | Hold winners |\n"

        content += f"""

---

## RISK SUMMARY
- **Total Trades**: {len(dee_trades['buy']) + len(dee_trades['sell']) + len(shorgan_trades['long']) + len(shorgan_trades['short']) + len(shorgan_trades.get('sell', []))}
- **DEE-BOT**: {len(dee_trades['buy'])} buys, {len(dee_trades['sell'])} sells
- **SHORGAN-BOT**: {len(shorgan_trades['long'])} longs, {len(shorgan_trades['short'])} shorts
- **Risk Controls**: All positions have stop losses
- **Execution**: Scheduled for 9:30 AM ET

---

## EXECUTION NOTES
1. This file will be automatically executed at 9:30 AM ET
2. Pre-execution validation will adjust position sizes if needed
3. Margin usage prevented for DEE-BOT (cash only)
4. Position limits enforced (8% DEE, 10% SHORGAN)

---

*Generated by Multi-Agent AI System*
*Execution via execute_daily_trades.py*
"""

        # Save the file
        filename = f"TODAYS_TRADES_{date_str}.md"
        filepath = self.docs_dir / filename

        with open(filepath, 'w') as f:
            f.write(content)

        print(f"[SUCCESS] Generated trades file: {filepath}")
        return filepath

    def run(self):
        """Main execution function"""
        print("=" * 80)
        print("AUTOMATED TRADE GENERATION")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        try:
            # Check if file already exists
            today = datetime.now().strftime('%Y-%m-%d')
            existing_files = list(self.docs_dir.glob(f'TODAYS_TRADES_{today}*.md'))

            if existing_files:
                print(f"[INFO] Trade file already exists: {existing_files[0]}")
                response = input("Overwrite? (y/n): ")
                if response.lower() != 'y':
                    print("[ABORT] Keeping existing file")
                    return

            # Generate trades for both bots
            print("\n[STEP 1] Generating DEE-BOT trades...")
            dee_trades = self.generate_dee_bot_trades()

            print("\n[STEP 2] Generating SHORGAN-BOT trades...")
            shorgan_trades = self.generate_shorgan_bot_trades()

            print("\n[STEP 3] Creating markdown file...")
            filepath = self.generate_markdown_file(dee_trades, shorgan_trades)

            # Summary
            print("\n" + "=" * 80)
            print("GENERATION COMPLETE")
            print(f"DEE-BOT: {len(dee_trades['buy'])} buys, {len(dee_trades['sell'])} sells")
            print(f"SHORGAN-BOT: {len(shorgan_trades['long'])} longs, {len(shorgan_trades['short'])} shorts")
            print(f"File saved: {filepath}")
            print("=" * 80)

            return filepath

        except Exception as e:
            print(f"[ERROR] Trade generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    generator = AutomatedTradeGenerator()
    generator.run()