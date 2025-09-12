"""
SHORGAN-BOT Portfolio Cleanup
Removes non-micro-cap positions and frees up cash
THIS IS ONLY FOR SHORGAN-BOT - DEE-BOT UNCHANGED
"""

import os
import sys
import time
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class ShorganCleanup:
    def __init__(self):
        # SHORGAN-BOT API ONLY
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
    def cleanup_portfolio(self):
        """Clean up SHORGAN-BOT portfolio only"""
        print("="*60)
        print("SHORGAN-BOT PORTFOLIO CLEANUP")
        print("THIS DOES NOT AFFECT DEE-BOT")
        print("="*60)
        
        # Positions to close (non-micro-caps)
        close_list = ['SPY', 'NVDA', 'AMD', 'ORCL']
        
        # Positions to trim (taking profits)
        trim_list = {'RGTI': 0.5}  # Trim 50%
        
        positions = self.api.list_positions()
        
        for pos in positions:
            symbol = pos.symbol
            qty = abs(int(pos.qty))
            side = pos.side
            
            # Close non-micro-caps
            if symbol in close_list:
                try:
                    print(f"\nClosing {symbol} (not micro-cap)...")
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=qty,
                        side='sell' if side == 'long' else 'buy',
                        type='market',
                        time_in_force='day'
                    )
                    print(f"  [SUCCESS] Closing {qty} shares of {symbol}")
                    time.sleep(1)
                except Exception as e:
                    print(f"  [ERROR] Failed to close {symbol}: {e}")
            
            # Trim profitable positions
            elif symbol in trim_list:
                trim_qty = int(qty * trim_list[symbol])
                if trim_qty > 0:
                    try:
                        print(f"\nTrimming {symbol} (taking profits)...")
                        order = self.api.submit_order(
                            symbol=symbol,
                            qty=trim_qty,
                            side='sell' if side == 'long' else 'buy',
                            type='market',
                            time_in_force='day'
                        )
                        print(f"  [SUCCESS] Trimmed {trim_qty} shares of {symbol}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"  [ERROR] Failed to trim {symbol}: {e}")
        
        print("\n" + "="*60)
        print("CLEANUP COMPLETE - SHORGAN-BOT ONLY")
        print("DEE-BOT remains unchanged")
        print("="*60)

def main():
    # Auto-execute without prompt for automation
    cleanup = ShorganCleanup()
    cleanup.cleanup_portfolio()

if __name__ == "__main__":
    main()