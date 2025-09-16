"""
Monday September 16, 2025 - Trading Execution
Based on ChatGPT TradingAgents Premarket Report
"""

import os
import sys
import json
import time
from datetime import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MondayTradingExecutor:
    def __init__(self):
        # Initialize Alpaca API for SHORGAN-BOT
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Load premarket report
        report_file = '02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report.json'
        with open(report_file, 'r') as f:
            self.report = json.load(f)
        
        self.executed_trades = []
        
    def check_market_status(self):
        """Check if market is open"""
        clock = self.api.get_clock()
        return clock.is_open
    
    def get_account_info(self):
        """Get account information"""
        account = self.api.get_account()
        return {
            'portfolio_value': float(account.portfolio_value),
            'cash': float(account.cash),
            'buying_power': float(account.buying_power)
        }
    
    def calculate_position_size(self, symbol, size_pct):
        """Calculate position size based on percentage"""
        account = self.get_account_info()
        position_value = account['portfolio_value'] * (size_pct / 100)
        
        # Get current price
        try:
            quote = self.api.get_latest_quote(symbol)
            price = quote.ask_price if quote.ask_price > 0 else quote.bid_price
            
            if price <= 0:
                # Try last trade
                trade = self.api.get_latest_trade(symbol)
                price = trade.price
            
            shares = int(position_value / price)
            return shares, price
            
        except Exception as e:
            logging.error(f"Error getting price for {symbol}: {e}")
            return 0, 0
    
    def execute_mfic_trade(self):
        """Execute MFIC long position"""
        symbol = 'MFIC'
        trade_info = self.report['trades'][0]
        
        logging.info(f"Executing {symbol} trade...")
        
        # Calculate position size (9% of portfolio)
        shares, current_price = self.calculate_position_size(symbol, trade_info['size_pct'])
        
        if shares <= 0:
            logging.error(f"Invalid position size for {symbol}")
            return False
        
        try:
            # Submit market order
            order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            logging.info(f"Order submitted: BUY {shares} shares of {symbol}")
            
            # Wait for fill
            time.sleep(3)
            
            # Get fill price
            order_update = self.api.get_order(order.id)
            fill_price = float(order_update.filled_avg_price) if order_update.filled_avg_price else current_price
            
            # Calculate stop loss (9% below entry)
            stop_price = fill_price * (1 - trade_info['stop_pct'] / 100)
            
            # Submit stop loss order
            stop_order = self.api.submit_order(
                symbol=symbol,
                qty=shares,
                side='sell',
                type='stop',
                stop_price=round(stop_price, 2),
                time_in_force='gtc'
            )
            
            logging.info(f"Stop loss set at ${stop_price:.2f}")
            
            self.executed_trades.append({
                'symbol': symbol,
                'action': 'BUY',
                'shares': shares,
                'price': fill_price,
                'stop': stop_price,
                'target1': fill_price * 1.25,
                'target2': fill_price * 1.30,
                'order_id': order.id,
                'stop_order_id': stop_order.id
            })
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to execute {symbol} trade: {e}")
            return False
    
    def setup_portfolio_hedge(self):
        """Setup SPY puts as portfolio hedge"""
        try:
            # Get SPY price
            spy_quote = self.api.get_latest_quote('SPY')
            spy_price = spy_quote.ask_price if spy_quote.ask_price > 0 else spy_quote.bid_price
            
            # Calculate hedge size (1% of portfolio in put premium)
            account = self.get_account_info()
            hedge_amount = account['portfolio_value'] * 0.01
            
            logging.info(f"Portfolio hedge recommendation: SPY puts with ${hedge_amount:.0f} premium")
            logging.info(f"Current SPY price: ${spy_price:.2f}")
            logging.info("Note: Options not available in paper trading - track manually")
            
            return True
            
        except Exception as e:
            logging.error(f"Error setting up hedge: {e}")
            return False
    
    def screen_insider_purchases(self):
        """Screen for insider purchase opportunities"""
        logging.info("\nScreening for insider purchase opportunities...")
        
        # List of potential candidates to screen
        # In production, this would connect to a screening service
        candidates = [
            'MFIC',  # Already identified
            # Add more based on AAII screen results
        ]
        
        logging.info("Recommendation: Check AAII Insider Net Purchases Screen")
        logging.info("Link: https://www.aaii.com/stocks/screens/39")
        logging.info("Look for small/mid caps with recent insider buying")
        
        return candidates
    
    def check_fda_calendar(self):
        """Check FDA calendar for upcoming catalysts"""
        logging.info("\nChecking FDA calendar for biotech catalysts...")
        
        # In production, this would scrape/API call to FDA calendar
        logging.info("Recommendation: Monitor these sources:")
        logging.info("1. Benzinga FDA Calendar: https://www.benzinga.com/fda-calendar")
        logging.info("2. FDA PDUFA Calendar")
        logging.info("3. Look for events in next 2-4 weeks")
        logging.info("Focus on micro-caps (<$500M) with binary events")
        
        return []
    
    def generate_execution_report(self):
        """Generate execution report"""
        report = f"""
========================================
MONDAY TRADING EXECUTION REPORT
September 16, 2025
========================================

MARKET STATUS: {"OPEN" if self.check_market_status() else "CLOSED"}

ACCOUNT SUMMARY:
"""
        
        account = self.get_account_info()
        report += f"  Portfolio Value: ${account['portfolio_value']:,.2f}\n"
        report += f"  Cash Available: ${account['cash']:,.2f}\n"
        report += f"  Buying Power: ${account['buying_power']:,.2f}\n"
        
        report += f"\nEXECUTED TRADES ({len(self.executed_trades)}):\n"
        
        for trade in self.executed_trades:
            report += f"""
  {trade['symbol']}:
    Action: {trade['action']} {trade['shares']} shares
    Price: ${trade['price']:.2f}
    Stop Loss: ${trade['stop']:.2f}
    Target 1: ${trade['target1']:.2f} (+25%)
    Target 2: ${trade['target2']:.2f} (+30%)
    Order ID: {trade['order_id']}
"""
        
        report += """
RECOMMENDATIONS:
1. Monitor MFIC for breakout confirmation
2. Screen AAII for insider purchase candidates
3. Check FDA calendar for biotech catalysts
4. Maintain SPY put hedge (manual tracking)

RISK REMINDERS:
- Max position size: 10% of portfolio
- Binary events: 2-5% max
- Stop losses are mandatory
- Take 50% profit at +20-25%
- Use trailing stops after target 1

========================================
"""
        
        return report
    
    def run(self):
        """Execute Monday trading plan"""
        logging.info("="*50)
        logging.info("MONDAY TRADING EXECUTION")
        logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        logging.info("="*50)
        
        # Check market status
        if not self.check_market_status():
            logging.warning("Market is closed. Will execute when market opens.")
            # In production, would schedule for market open
        
        # Execute primary trade
        logging.info("\n1. Executing MFIC trade...")
        mfic_success = self.execute_mfic_trade()
        
        # Setup portfolio hedge
        logging.info("\n2. Setting up portfolio hedge...")
        hedge_success = self.setup_portfolio_hedge()
        
        # Screen for additional opportunities
        logging.info("\n3. Screening for additional opportunities...")
        insider_candidates = self.screen_insider_purchases()
        fda_candidates = self.check_fda_calendar()
        
        # Generate report
        report = self.generate_execution_report()
        
        # Save report
        report_file = f"08_trading_logs/execution/monday_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(report)
        
        logging.info(f"\nExecution report saved to: {report_file}")
        
        return self.executed_trades

if __name__ == "__main__":
    executor = MondayTradingExecutor()
    executor.run()