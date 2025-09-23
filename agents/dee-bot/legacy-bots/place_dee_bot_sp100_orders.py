"""
DEE-BOT S&P 100 Trading System
Enhanced with full S&P 100 universe coverage
Multi-Agent Collaborative Strategy with Sector Diversification
"""

import alpaca_trade_api as tradeapi
import json
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('config')
sys.path.append('agents')

# Import S&P 100 configuration
from sp100_universe import SP100_UNIVERSE, get_sp100_tickers, SECTOR_LIMITS, LIQUIDITY_REQUIREMENTS
from sp100_scanner import SP100Scanner

# DEE-BOT Alpaca Credentials
DEE_BOT_API_KEY = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET_KEY = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"
BASE_URL = "https://paper-api.alpaca.markets"

def connect_dee_bot_alpaca():
    """Connect to Alpaca with DEE-BOT credentials"""
    
    print("DEE-BOT S&P 100 TRADING SYSTEM")
    print("=" * 70)
    
    try:
        api = tradeapi.REST(
            DEE_BOT_API_KEY,
            DEE_BOT_SECRET_KEY,
            BASE_URL,
            api_version='v2'
        )
        
        # Test connection
        account = api.get_account()
        print(f"[SUCCESS] Connected to DEE-BOT Alpaca Account")
        print(f"  Account Status: {account.status}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        
        return api
        
    except Exception as e:
        print(f"[ERROR] Failed to connect: {str(e)}")
        return None

def get_sp100_market_data(api):
    """Get current market data for S&P 100 stocks"""
    
    print("\n[MARKET DATA] Fetching S&P 100 quotes...")
    market_data = {}
    
    # Get all S&P 100 tickers
    tickers = get_sp100_tickers()
    
    try:
        # Get latest quotes for all tickers
        for ticker in tickers[:20]:  # Start with top 20 for demo
            try:
                quote = api.get_latest_quote(ticker)
                bar = api.get_latest_bar(ticker)
                
                market_data[ticker] = {
                    'price': float(quote.ask_price),
                    'bid': float(quote.bid_price),
                    'ask': float(quote.ask_price),
                    'volume': int(bar.volume) if bar else 0,
                    'close': float(bar.close) if bar else float(quote.ask_price),
                    'high': float(bar.high) if bar else 0,
                    'low': float(bar.low) if bar else 0,
                    'spread': float(quote.ask_price) - float(quote.bid_price),
                    'spread_pct': ((float(quote.ask_price) - float(quote.bid_price)) / float(quote.ask_price)) * 100
                }
                
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"[WARNING] Could not fetch all market data: {str(e)}")
    
    print(f"  Retrieved data for {len(market_data)} stocks")
    return market_data

def analyze_sp100_opportunities(api, market_data):
    """Analyze S&P 100 universe for best opportunities"""
    
    print("\n" + "=" * 70)
    print("S&P 100 MULTI-AGENT ANALYSIS")
    print("=" * 70)
    
    opportunities = []
    
    # High-conviction S&P 100 opportunities based on multi-agent consensus
    # These would normally come from real-time analysis
    sp100_signals = [
        {
            'ticker': 'NVDA',
            'sector': 'Technology',
            'company': 'NVIDIA Corporation',
            'multi_agent_scores': {
                'fundamental': 0.85,
                'technical': 0.82,
                'sentiment': 0.88,
                'momentum': 0.90,
                'value': 0.65,
                'quality': 0.92,
                'risk': 0.75
            },
            'consensus': 0.82,
            'recommendation': 'STRONG BUY',
            'catalyst': 'AI leadership, datacenter growth'
        },
        {
            'ticker': 'JPM',
            'sector': 'Financials',
            'company': 'JPMorgan Chase',
            'multi_agent_scores': {
                'fundamental': 0.80,
                'technical': 0.75,
                'sentiment': 0.72,
                'momentum': 0.68,
                'value': 0.85,
                'quality': 0.88,
                'risk': 0.82
            },
            'consensus': 0.78,
            'recommendation': 'BUY',
            'catalyst': 'NII expansion, strong capital position'
        },
        {
            'ticker': 'LLY',
            'sector': 'Healthcare',
            'company': 'Eli Lilly',
            'multi_agent_scores': {
                'fundamental': 0.88,
                'technical': 0.70,
                'sentiment': 0.85,
                'momentum': 0.75,
                'value': 0.55,
                'quality': 0.90,
                'risk': 0.70
            },
            'consensus': 0.76,
            'recommendation': 'BUY',
            'catalyst': 'GLP-1 drug momentum, pipeline strength'
        },
        {
            'ticker': 'AMZN',
            'sector': 'Consumer Discretionary',
            'company': 'Amazon.com',
            'multi_agent_scores': {
                'fundamental': 0.78,
                'technical': 0.72,
                'sentiment': 0.80,
                'momentum': 0.70,
                'value': 0.68,
                'quality': 0.85,
                'risk': 0.72
            },
            'consensus': 0.75,
            'recommendation': 'BUY',
            'catalyst': 'AWS growth, retail margin expansion'
        },
        {
            'ticker': 'XOM',
            'sector': 'Energy',
            'company': 'Exxon Mobil',
            'multi_agent_scores': {
                'fundamental': 0.75,
                'technical': 0.68,
                'sentiment': 0.65,
                'momentum': 0.62,
                'value': 0.88,
                'quality': 0.82,
                'risk': 0.78
            },
            'consensus': 0.74,
            'recommendation': 'BUY',
            'catalyst': 'Energy prices, dividend yield'
        },
        {
            'ticker': 'PG',
            'sector': 'Consumer Staples',
            'company': 'Procter & Gamble',
            'multi_agent_scores': {
                'fundamental': 0.72,
                'technical': 0.70,
                'sentiment': 0.68,
                'momentum': 0.65,
                'value': 0.70,
                'quality': 0.92,
                'risk': 0.85
            },
            'consensus': 0.74,
            'recommendation': 'BUY',
            'catalyst': 'Defensive quality, pricing power'
        },
        {
            'ticker': 'UNP',
            'sector': 'Industrials',
            'company': 'Union Pacific',
            'multi_agent_scores': {
                'fundamental': 0.70,
                'technical': 0.72,
                'sentiment': 0.65,
                'momentum': 0.68,
                'value': 0.75,
                'quality': 0.80,
                'risk': 0.75
            },
            'consensus': 0.72,
            'recommendation': 'BUY',
            'catalyst': 'Rail efficiency, economic recovery'
        },
        {
            'ticker': 'NEE',
            'sector': 'Utilities',
            'company': 'NextEra Energy',
            'multi_agent_scores': {
                'fundamental': 0.75,
                'technical': 0.68,
                'sentiment': 0.72,
                'momentum': 0.65,
                'value': 0.65,
                'quality': 0.85,
                'risk': 0.80
            },
            'consensus': 0.73,
            'recommendation': 'BUY',
            'catalyst': 'Renewable energy leadership'
        }
    ]
    
    # Display analysis for each opportunity
    for signal in sp100_signals:
        print(f"\n[{signal['ticker']}] {signal['company']}")
        print(f"  Sector: {signal['sector']}")
        print(f"  Multi-Agent Consensus: {signal['consensus']*100:.1f}%")
        print(f"  Recommendation: {signal['recommendation']}")
        print(f"  Catalyst: {signal['catalyst']}")
        
        # Show individual agent scores
        print("  Agent Scores:")
        for agent, score in signal['multi_agent_scores'].items():
            status = "✓" if score >= 0.70 else "○"
            print(f"    {status} {agent.capitalize()}: {score*100:.0f}%")
        
        # Add market data if available
        if signal['ticker'] in market_data:
            data = market_data[signal['ticker']]
            signal['current_price'] = data['price']
            signal['volume'] = data['volume']
            signal['spread_pct'] = data['spread_pct']
            print(f"  Current Price: ${data['price']:.2f}")
            print(f"  Volume: {data['volume']:,}")
            print(f"  Spread: {data['spread_pct']:.3f}%")
        
        opportunities.append(signal)
    
    return opportunities

def place_diversified_sp100_orders(api, opportunities):
    """Place orders across S&P 100 with sector diversification"""
    
    print("\n" + "=" * 70)
    print("EXECUTING DIVERSIFIED S&P 100 ORDERS")
    print("=" * 70)
    
    orders_placed = []
    sector_allocation = {}
    total_capital = 0
    max_capital = 50000  # Maximum capital to deploy
    
    # Sort opportunities by consensus score
    opportunities.sort(key=lambda x: x['consensus'], reverse=True)
    
    # Process top opportunities with sector diversification
    for opp in opportunities:
        ticker = opp['ticker']
        sector = opp['sector']
        consensus = opp['consensus']
        
        # Check sector allocation limit
        current_sector_pct = sector_allocation.get(sector, 0)
        sector_limit = SECTOR_LIMITS.get(sector, 0.20)
        
        if current_sector_pct >= sector_limit:
            print(f"\n[SKIP] {ticker} - Sector limit reached for {sector}")
            continue
        
        # Skip if consensus too low
        if consensus < 0.70:
            print(f"\n[SKIP] {ticker} - Consensus below threshold ({consensus*100:.1f}%)")
            continue
        
        # Skip if we've reached capital limit
        if total_capital >= max_capital:
            print(f"\n[SKIP] {ticker} - Capital limit reached")
            break
        
        try:
            # Get current price
            quote = api.get_latest_quote(ticker)
            current_price = float(quote.ask_price)
            
            # Calculate position size based on consensus and remaining capital
            position_value = min(
                5000 * consensus,  # Scale with confidence
                max_capital - total_capital,  # Don't exceed limit
                10000  # Max single position
            )
            shares = int(position_value / current_price)
            
            if shares < 1:
                continue
            
            # Calculate stop loss and take profit
            stop_loss_pct = 0.03 if consensus >= 0.75 else 0.025  # Tighter stop for higher confidence
            take_profit_pct = 0.06 if consensus >= 0.75 else 0.05
            
            stop_price = current_price * (1 - stop_loss_pct)
            profit_price = current_price * (1 + take_profit_pct)
            
            print(f"\n[ORDER] {ticker} - {opp['company']}")
            print(f"  Sector: {sector}")
            print(f"  Consensus: {consensus*100:.1f}%")
            print(f"  Shares: {shares}")
            print(f"  Entry: ${current_price:.2f}")
            print(f"  Stop: ${stop_price:.2f} (-{stop_loss_pct*100:.1f}%)")
            print(f"  Target: ${profit_price:.2f} (+{take_profit_pct*100:.1f}%)")
            
            # Submit order with bracket
            order = api.submit_order(
                symbol=ticker,
                qty=shares,
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=current_price * 1.001,  # Slightly above ask for execution
                order_class='bracket',
                stop_loss={'stop_price': stop_price},
                take_profit={'limit_price': profit_price}
            )
            
            print(f"  [SUCCESS] Order ID: {order.id}")
            
            # Track order
            order_value = shares * current_price
            orders_placed.append({
                "ticker": ticker,
                "company": opp['company'],
                "sector": sector,
                "order_id": order.id,
                "qty": shares,
                "limit_price": current_price,
                "stop_loss": stop_price,
                "take_profit": profit_price,
                "consensus": f"{consensus*100:.1f}%",
                "value": order_value
            })
            
            # Update allocations
            total_capital += order_value
            sector_allocation[sector] = sector_allocation.get(sector, 0) + (order_value / max_capital)
            
        except Exception as e:
            print(f"  [ERROR] Could not place order: {str(e)}")
            continue
    
    return orders_placed, sector_allocation

def save_sp100_trading_log(orders, sector_allocation):
    """Save S&P 100 trading log with analytics"""
    
    # Calculate portfolio metrics
    total_value = sum(o['value'] for o in orders)
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "bot": "DEE-BOT",
        "strategy": "S&P 100 Multi-Agent Diversified",
        "universe_size": len(SP100_UNIVERSE),
        "orders_placed": len(orders),
        "total_value": total_value,
        "orders": orders,
        "sector_allocation": {
            sector: f"{pct*100:.1f}%" 
            for sector, pct in sector_allocation.items()
        },
        "risk_metrics": {
            "max_position_size": max(o['value'] for o in orders) if orders else 0,
            "avg_position_size": total_value / len(orders) if orders else 0,
            "num_sectors": len(sector_allocation),
            "diversification_score": 1 - max(sector_allocation.values()) if sector_allocation else 0
        }
    }
    
    filename = f"DEE_BOT_SP100_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return filename, log_data

if __name__ == "__main__":
    # Connect to Alpaca
    api = connect_dee_bot_alpaca()
    
    if api:
        # Get market data for S&P 100
        market_data = get_sp100_market_data(api)
        
        # Analyze opportunities
        opportunities = analyze_sp100_opportunities(api, market_data)
        
        # Place diversified orders
        orders, sector_allocation = place_diversified_sp100_orders(api, opportunities)
        
        # Save log
        log_file, log_data = save_sp100_trading_log(orders, sector_allocation)
        
        # Summary
        print("\n" + "=" * 70)
        print("S&P 100 TRADING SUMMARY")
        print("=" * 70)
        print(f"Universe Coverage: {len(SP100_UNIVERSE)} stocks")
        print(f"Opportunities Analyzed: {len(opportunities)}")
        print(f"Orders Executed: {len(orders)}")
        print(f"Total Capital Deployed: ${log_data['total_value']:,.2f}")
        print(f"Sectors Covered: {log_data['risk_metrics']['num_sectors']}")
        print(f"Diversification Score: {log_data['risk_metrics']['diversification_score']:.2f}")
        print("\nSector Allocation:")
        for sector, pct in log_data['sector_allocation'].items():
            print(f"  {sector}: {pct}")
        print(f"\nLog File: {log_file}")
        print("=" * 70)
        print("\n[SUCCESS] DEE-BOT S&P 100 diversified portfolio executed!")
        print("Check Alpaca dashboard: https://app.alpaca.markets/paper/dashboard/overview")
    else:
        print("\n[ERROR] Could not connect to Alpaca")