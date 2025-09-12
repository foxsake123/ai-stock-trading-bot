"""
SHORGAN-BOT Daily Trade Execution Script
Date: September 11, 2025
Portfolio: $104,522.50
Execution: Market is now open
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs('09_logs/trading', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'09_logs/trading/trades_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class ShorganBotTrader:
    """Execute daily trades for SHORGAN-BOT based on pre-market analysis"""
    
    def __init__(self):
        """Initialize trader with SHORGAN-BOT credentials"""
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        self.account = None
        self.positions = {}
        self.orders = []
        
    def get_account_info(self):
        """Get current account information"""
        self.account = self.api.get_account()
        logging.info(f"Account Value: ${float(self.account.portfolio_value):,.2f}")
        logging.info(f"Buying Power: ${float(self.account.buying_power):,.2f}")
        logging.info(f"Cash: ${float(self.account.cash):,.2f}")
        return self.account
        
    def calculate_position_size(self, percentage: float) -> float:
        """Calculate position size based on portfolio percentage"""
        portfolio_value = float(self.account.portfolio_value)
        return portfolio_value * (percentage / 100)
        
    def execute_long_position(self, symbol: str, entry_range: Tuple[float, float], 
                            stop_loss: float, target: float, size_pct: float,
                            profit_taking: Dict = None):
        """Execute a long position with proper risk management"""
        try:
            # Get current price
            quote = self.api.get_latest_quote(symbol)
            current_price = quote.ask_price
            
            logging.info(f"Checking {symbol}: Current price ${current_price:.2f}, Entry range ${entry_range[0]:.2f}-${entry_range[1]:.2f}")
            
            # Check if price is within entry range
            if entry_range[0] <= current_price <= entry_range[1]:
                position_value = self.calculate_position_size(size_pct)
                shares = int(position_value / current_price)
                
                if shares > 0:
                    # Place market order
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    
                    logging.info(f"✅ LONG ORDER PLACED: {symbol}")
                    logging.info(f"  Shares: {shares}")
                    logging.info(f"  Entry: ${current_price:.2f}")
                    logging.info(f"  Stop: ${stop_loss:.2f}")
                    logging.info(f"  Target: ${target:.2f}")
                    
                    # Place stop loss order
                    time.sleep(2)  # Wait for order to fill
                    stop_order = self.api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='sell',
                        type='stop',
                        time_in_force='gtc',
                        stop_price=stop_loss
                    )
                    
                    self.orders.append({
                        'symbol': symbol,
                        'type': 'long',
                        'shares': shares,
                        'entry': current_price,
                        'stop': stop_loss,
                        'target': target,
                        'profit_taking': profit_taking,
                        'order_id': order.id,
                        'stop_order_id': stop_order.id
                    })
                    
                    return True
            else:
                logging.warning(f"❌ {symbol} price ${current_price:.2f} outside entry range")
                return False
                
        except Exception as e:
            logging.error(f"Error executing long position for {symbol}: {e}")
            return False
            
    def execute_short_position(self, symbol: str, entry_range: Tuple[float, float],
                             stop_loss: float, target: float, size_pct: float,
                             profit_taking: Dict = None):
        """Execute a short position with proper risk management"""
        try:
            # Get current price
            quote = self.api.get_latest_quote(symbol)
            current_price = quote.bid_price
            
            logging.info(f"Checking {symbol} for short: Current price ${current_price:.2f}, Entry range ${entry_range[0]:.2f}-${entry_range[1]:.2f}")
            
            # Check if price is within entry range
            if entry_range[0] <= current_price <= entry_range[1]:
                position_value = self.calculate_position_size(size_pct)
                shares = int(position_value / current_price)
                
                if shares > 0:
                    # Place short sell order
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='sell',
                        type='market',
                        time_in_force='day'
                    )
                    
                    logging.info(f"✅ SHORT ORDER PLACED: {symbol}")
                    logging.info(f"  Shares: {shares}")
                    logging.info(f"  Entry: ${current_price:.2f}")
                    logging.info(f"  Stop: ${stop_loss:.2f}")
                    logging.info(f"  Target: ${target:.2f}")
                    
                    # Place stop loss order (buy to cover)
                    time.sleep(2)  # Wait for order to fill
                    stop_order = self.api.submit_order(
                        symbol=symbol,
                        qty=shares,
                        side='buy',
                        type='stop',
                        time_in_force='gtc',
                        stop_price=stop_loss
                    )
                    
                    self.orders.append({
                        'symbol': symbol,
                        'type': 'short',
                        'shares': shares,
                        'entry': current_price,
                        'stop': stop_loss,
                        'target': target,
                        'profit_taking': profit_taking,
                        'order_id': order.id,
                        'stop_order_id': stop_order.id
                    })
                    
                    return True
            else:
                logging.warning(f"❌ {symbol} price ${current_price:.2f} outside short entry range")
                return False
                
        except Exception as e:
            logging.error(f"Error executing short position for {symbol}: {e}")
            return False
            
    def execute_all_trades(self):
        """Execute all trades from today's pre-market report"""
        
        # Trade definitions from pre-market report
        trades = [
            {
                'symbol': 'DAKT',
                'type': 'long',
                'entry_range': (21.50, 22.00),
                'stop_loss': 19.50,
                'target': 25.00,
                'size_pct': 15,
                'profit_taking': {24.00: 0.5, 25.00: 1.0}
            },
            {
                'symbol': 'CHWY',
                'type': 'long',
                'entry_range': (37.50, 38.50),
                'stop_loss': 35.00,
                'target': 45.00,
                'size_pct': 15,
                'profit_taking': {42.00: 0.5, 45.00: 1.0}
            },
            {
                'symbol': 'AXSM',
                'type': 'long',
                'entry_range': (129.00, 131.00),
                'stop_loss': 120.00,
                'target': 145.00,
                'size_pct': 10,
                'profit_taking': {140.00: 0.5, 145.00: 1.0}
            },
            {
                'symbol': 'VNCE',
                'type': 'long',
                'entry_range': (2.40, 2.60),
                'stop_loss': 2.00,
                'target': 3.50,
                'size_pct': 5,
                'profit_taking': {3.00: 0.33, 3.25: 0.66, 3.50: 1.0}
            },
            {
                'symbol': 'NCNO',
                'type': 'short',
                'entry_range': (30.00, 31.00),
                'stop_loss': 33.00,
                'target': 26.00,
                'size_pct': 10,
                'profit_taking': {28.00: 0.5, 26.00: 1.0}
            },
            {
                'symbol': 'SHC',
                'type': 'short',
                'entry_range': (14.80, 15.20),
                'stop_loss': 16.00,
                'target': 13.50,
                'size_pct': 10,
                'profit_taking': {14.00: 0.5, 13.50: 1.0}
            }
        ]
        
        logging.info("="*60)
        logging.info("EXECUTING DAILY TRADES FOR SHORGAN-BOT")
        logging.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("="*60)
        
        # Execute each trade
        successful_trades = 0
        failed_trades = []
        
        for trade in trades:
            logging.info(f"\n--- Processing {trade['symbol']} ---")
            
            if trade['type'] == 'long':
                success = self.execute_long_position(
                    symbol=trade['symbol'],
                    entry_range=trade['entry_range'],
                    stop_loss=trade['stop_loss'],
                    target=trade['target'],
                    size_pct=trade['size_pct'],
                    profit_taking=trade.get('profit_taking')
                )
            else:  # short
                success = self.execute_short_position(
                    symbol=trade['symbol'],
                    entry_range=trade['entry_range'],
                    stop_loss=trade['stop_loss'],
                    target=trade['target'],
                    size_pct=trade['size_pct'],
                    profit_taking=trade.get('profit_taking')
                )
                
            if success:
                successful_trades += 1
            else:
                failed_trades.append(trade['symbol'])
                
            # Small delay between orders
            time.sleep(2)
            
        logging.info("\n" + "="*60)
        logging.info(f"EXECUTION COMPLETE: {successful_trades}/{len(trades)} trades placed")
        if failed_trades:
            logging.info(f"Failed trades: {', '.join(failed_trades)}")
        logging.info("="*60)
        
        # Save execution report
        self.save_execution_report(successful_trades, failed_trades)
        
        return successful_trades, failed_trades
        
    def save_execution_report(self, successful_trades, failed_trades):
        """Save execution report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'account_value': float(self.account.portfolio_value),
            'successful_trades': successful_trades,
            'failed_trades': failed_trades,
            'orders': self.orders
        }
        
        os.makedirs('09_logs/trading', exist_ok=True)
        report_path = f"09_logs/trading/execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logging.info(f"Execution report saved to {report_path}")
        
def main():
    """Main execution function"""
    try:
        logging.info("Starting SHORGAN-BOT trade execution...")
        
        trader = ShorganBotTrader()
        
        # Get account info
        account = trader.get_account_info()
        
        # Check if market is open
        clock = trader.api.get_clock()
        if not clock.is_open:
            logging.error("Market is closed! Cannot execute trades.")
            return
            
        logging.info("Market is OPEN - proceeding with trades")
        
        # Execute trades
        successful, failed = trader.execute_all_trades()
        
        # Final summary
        logging.info("\n" + "="*60)
        logging.info("FINAL SUMMARY")
        logging.info(f"Successful trades: {successful}")
        logging.info(f"Failed trades: {len(failed)}")
        if failed:
            logging.info(f"Failed symbols: {failed}")
        logging.info("Trade execution script completed")
        logging.info("="*60)
        
    except Exception as e:
        logging.error(f"Critical error in main execution: {e}")
        raise
    
if __name__ == "__main__":
    main()