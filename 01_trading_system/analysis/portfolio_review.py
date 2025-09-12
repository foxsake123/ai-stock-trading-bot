"""
Portfolio Review and Adjustment Analysis
Reviews current positions and recommends changes
"""

import os
import sys
import json
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime
import yfinance as yf

load_dotenv()

class PortfolioReviewer:
    def __init__(self):
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
    def review_current_positions(self):
        """Review all current positions"""
        print("="*60)
        print("SHORGAN-BOT PORTFOLIO REVIEW")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Get account info
        account = self.api.get_account()
        portfolio_value = float(account.portfolio_value)
        cash = float(account.cash)
        buying_power = float(account.buying_power)
        
        print(f"\nAccount Summary:")
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
        print(f"Cash Available: ${cash:,.2f}")
        print(f"Buying Power: ${buying_power:,.2f}")
        
        # Get positions
        positions = self.api.list_positions()
        
        if not positions:
            print("\nNo current positions")
            return []
        
        print(f"\nCurrent Positions ({len(positions)}):")
        print("-"*60)
        
        position_data = []
        total_pl = 0
        
        for pos in positions:
            symbol = pos.symbol
            qty = int(pos.qty)
            side = pos.side
            avg_price = float(pos.avg_entry_price)
            current_price = float(pos.current_price) if pos.current_price else 0
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl) if pos.unrealized_pl else 0
            unrealized_pl_pct = float(pos.unrealized_plpc) * 100 if pos.unrealized_plpc else 0
            
            # Get market cap from Yahoo Finance
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                market_cap = info.get('marketCap', 0)
                market_cap_cat = self.categorize_market_cap(market_cap)
                
                # Get recent performance
                hist = ticker.history(period="5d")
                if not hist.empty:
                    five_day_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                else:
                    five_day_change = 0
            except:
                market_cap = 0
                market_cap_cat = "Unknown"
                five_day_change = 0
            
            position_info = {
                'symbol': symbol,
                'side': side,
                'quantity': qty,
                'avg_price': avg_price,
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pl': unrealized_pl,
                'unrealized_pl_pct': unrealized_pl_pct,
                'market_cap': market_cap,
                'market_cap_cat': market_cap_cat,
                '5d_change': five_day_change
            }
            
            position_data.append(position_info)
            total_pl += unrealized_pl
            
            print(f"\n{symbol} ({side.upper()}):")
            print(f"  Shares: {qty:,}")
            print(f"  Avg Price: ${avg_price:.2f}")
            print(f"  Current: ${current_price:.2f}")
            print(f"  Market Value: ${market_value:,.2f}")
            print(f"  Unrealized P&L: ${unrealized_pl:,.2f} ({unrealized_pl_pct:+.2f}%)")
            print(f"  Market Cap: {market_cap_cat}")
            print(f"  5-Day Change: {five_day_change:+.2f}%")
        
        print("\n" + "-"*60)
        print(f"Total Unrealized P&L: ${total_pl:,.2f}")
        
        return position_data
    
    def categorize_market_cap(self, market_cap):
        """Categorize market cap"""
        if market_cap < 300_000_000:
            return "Micro-cap (<$300M)"
        elif market_cap < 2_000_000_000:
            return "Small-cap ($300M-$2B)"
        elif market_cap < 10_000_000_000:
            return "Mid-cap ($2B-$10B)"
        elif market_cap < 200_000_000_000:
            return "Large-cap ($10B-$200B)"
        else:
            return "Mega-cap (>$200B)"
    
    def analyze_adjustments(self, positions):
        """Analyze and recommend adjustments"""
        print("\n" + "="*60)
        print("PORTFOLIO ANALYSIS & RECOMMENDATIONS")
        print("="*60)
        
        recommendations = {
            'hold': [],
            'trim': [],
            'close': [],
            'add': []
        }
        
        # Analyze each position
        for pos in positions:
            symbol = pos['symbol']
            pl_pct = pos['unrealized_pl_pct']
            market_cap_cat = pos['market_cap_cat']
            five_day = pos['5d_change']
            
            # Check if position meets micro-cap requirement
            if "Large-cap" in market_cap_cat or "Mega-cap" in market_cap_cat:
                recommendations['close'].append({
                    'symbol': symbol,
                    'reason': f"Not micro/small/mid-cap ({market_cap_cat})",
                    'action': 'CLOSE - Violates micro-cap mandate'
                })
                continue
            
            # Performance-based recommendations
            if pl_pct > 20:
                recommendations['trim'].append({
                    'symbol': symbol,
                    'reason': f"Up {pl_pct:.1f}% - Consider taking profits",
                    'action': 'TRIM 50% to lock gains'
                })
            elif pl_pct < -15:
                recommendations['close'].append({
                    'symbol': symbol,
                    'reason': f"Down {pl_pct:.1f}% - Stop loss triggered",
                    'action': 'CLOSE - Cut losses'
                })
            elif -5 <= pl_pct <= 10:
                recommendations['hold'].append({
                    'symbol': symbol,
                    'reason': f"Performing as expected ({pl_pct:+.1f}%)",
                    'action': 'HOLD - Monitor closely'
                })
            else:
                recommendations['hold'].append({
                    'symbol': symbol,
                    'reason': f"Within normal range ({pl_pct:+.1f}%)",
                    'action': 'HOLD'
                })
        
        # Add new micro-cap opportunities from today's research
        recommendations['add'].extend([
            {
                'symbol': 'RCAT',
                'reason': 'Unusual call flow, bullish options activity',
                'action': 'BUY - Momentum catalyst play'
            }
        ])
        
        # Print recommendations
        print("\n[CLOSE] Positions to Exit:")
        if recommendations['close']:
            for rec in recommendations['close']:
                print(f"  • {rec['symbol']}: {rec['action']}")
                print(f"    Reason: {rec['reason']}")
        else:
            print("  None")
        
        print("\n[TRIM] Positions to Reduce:")
        if recommendations['trim']:
            for rec in recommendations['trim']:
                print(f"  • {rec['symbol']}: {rec['action']}")
                print(f"    Reason: {rec['reason']}")
        else:
            print("  None")
        
        print("\n[ADD] New Positions to Consider:")
        if recommendations['add']:
            for rec in recommendations['add']:
                print(f"  • {rec['symbol']}: {rec['action']}")
                print(f"    Reason: {rec['reason']}")
        else:
            print("  None")
        
        print("\n[HOLD] Positions to Maintain:")
        if recommendations['hold']:
            for rec in recommendations['hold']:
                print(f"  • {rec['symbol']}: {rec['action']}")
        else:
            print("  None")
        
        return recommendations
    
    def check_micro_cap_opportunities(self):
        """Research additional micro-cap opportunities"""
        print("\n" + "="*60)
        print("MICRO-CAP OPPORTUNITIES SCAN")
        print("="*60)
        
        # High-volume micro-caps with recent momentum
        micro_caps = [
            {'symbol': 'RCAT', 'catalyst': 'Unusual options flow', 'market_cap': '$600M'},
            {'symbol': 'VNCE', 'catalyst': 'Already moved +40% yesterday', 'market_cap': '$150M'},
            {'symbol': 'WISA', 'catalyst': 'Wireless audio tech momentum', 'market_cap': '$50M'},
            {'symbol': 'KULR', 'catalyst': 'Battery safety tech, govt contracts', 'market_cap': '$200M'},
            {'symbol': 'DRUG', 'catalyst': 'Pharma play, FDA catalyst pending', 'market_cap': '$120M'}
        ]
        
        print("\nTop Micro-Cap Watchlist:")
        for stock in micro_caps:
            print(f"\n{stock['symbol']} ({stock['market_cap']})")
            print(f"  Catalyst: {stock['catalyst']}")
        
        return micro_caps

def main():
    reviewer = PortfolioReviewer()
    
    # Review current positions
    positions = reviewer.review_current_positions()
    
    # Analyze adjustments
    if positions:
        recommendations = reviewer.analyze_adjustments(positions)
    
    # Check micro-cap opportunities
    micro_caps = reviewer.check_micro_cap_opportunities()
    
    print("\n" + "="*60)
    print("REVIEW COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()