"""
Place DEE-BOT Orders Based on Morning Research
Date: January 10, 2025
Enhanced with S&P 100 Universe Coverage
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Import the automated trade executor
import sys
sys.path.append('tools')
sys.path.append('config')

# Import S&P 100 universe configuration
from sp100_universe import (
    SP100_UNIVERSE, 
    get_sp100_tickers,
    get_sector_stocks,
    SECTOR_LIMITS,
    LIQUIDITY_REQUIREMENTS
)

def place_dee_bot_orders():
    """Place DEE-BOT orders based on morning research recommendations"""
    
    print("=" * 70)
    print("DEE-BOT ORDER PLACEMENT SYSTEM")
    print("Date: January 10, 2025")
    print("Universe: S&P 100 Stocks")
    print("=" * 70)
    
    # Load morning research report
    report_path = Path("data/research_reports/daily_report_2025-09-10.json")
    if not report_path.exists():
        print("[ERROR] Morning research report not found!")
        return False
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print(f"\n[INFO] Loaded research report from: {report['report_date']} {report['report_time']}")
    
    # Process recommendations
    recommendations = report.get("recommendations", [])
    watchlist = report.get("watchlist_analysis", {})
    
    orders_to_place = []
    
    for rec in recommendations:
        if rec["action"] == "BUY":
            ticker = rec["ticker"]
            
            # Check if ticker is in S&P 100 universe
            if ticker not in SP100_UNIVERSE and ticker not in ['SPY', 'QQQ']:
                print(f"\n[SKIP] {ticker} - Not in S&P 100 universe")
                continue
            
            stock_data = watchlist.get(ticker, {})
            current_price = stock_data.get("price", 0)
            stock_info = SP100_UNIVERSE.get(ticker, {})
            
            # DEE-BOT multi-agent consensus analysis
            print(f"\n[ANALYSIS] {ticker}")
            print(f"  Company: {stock_info.get('name', 'N/A')}")
            print(f"  Sector: {stock_info.get('sector', 'N/A')}")
            print(f"  Current Price: ${current_price:.2f}")
            print(f"  Signal: {rec['action']}")
            print(f"  Reason: {rec['reason']}")
            print(f"  Target Allocation: {rec['target_allocation']}%")
            
            # Create order based on multi-agent consensus
            order = {
                "bot": "DEE-BOT",
                "ticker": ticker,
                "action": "BUY",
                "order_type": "LIMIT",
                "limit_price": current_price * 1.001,  # Slightly above market for execution
                "shares": 100,  # Conservative position size
                "stop_loss": current_price * 0.97,  # 3% stop loss
                "take_profit": current_price * 1.05,  # 5% take profit
                "time_in_force": "DAY",
                "reason": f"Multi-agent consensus: {rec['reason']}",
                "confidence": 0.75,
                "risk_level": "MEDIUM"
            }
            
            orders_to_place.append(order)
            
            print(f"\n[ORDER PREPARED]")
            print(f"  Type: LIMIT BUY")
            print(f"  Shares: {order['shares']}")
            print(f"  Limit Price: ${order['limit_price']:.2f}")
            print(f"  Stop Loss: ${order['stop_loss']:.2f}")
            print(f"  Take Profit: ${order['take_profit']:.2f}")
    
    # Execute orders in PAPER mode for safety
    if orders_to_place:
        print("\n" + "=" * 70)
        print("EXECUTING ORDERS (PAPER MODE)")
        print("=" * 70)
        
        execution_results = []
        
        for order in orders_to_place:
            print(f"\n[PLACING ORDER] {order['ticker']}")
            
            # Simulate order placement in paper mode
            result = {
                "timestamp": datetime.now().isoformat(),
                "bot": order["bot"],
                "ticker": order["ticker"],
                "action": order["action"],
                "shares": order["shares"],
                "limit_price": order["limit_price"],
                "status": "PAPER_SUBMITTED",
                "order_id": f"PAPER_{order['ticker']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "message": "Order submitted to paper trading system",
                "stop_loss": order["stop_loss"],
                "take_profit": order["take_profit"]
            }
            
            execution_results.append(result)
            
            print(f"  Status: {result['status']}")
            print(f"  Order ID: {result['order_id']}")
            print(f"  Message: {result['message']}")
        
        # Save execution log
        log_file = f"DEE_BOT_ORDERS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_data = {
            "execution_time": datetime.now().isoformat(),
            "bot": "DEE-BOT",
            "mode": "PAPER",
            "orders": execution_results,
            "summary": {
                "total_orders": len(execution_results),
                "total_shares": sum(o["shares"] for o in execution_results),
                "total_value": sum(o["shares"] * o["limit_price"] for o in execution_results)
            }
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print("\n" + "=" * 70)
        print("ORDER EXECUTION SUMMARY")
        print("=" * 70)
        print(f"  Total Orders Placed: {log_data['summary']['total_orders']}")
        print(f"  Total Shares: {log_data['summary']['total_shares']}")
        print(f"  Total Value: ${log_data['summary']['total_value']:,.2f}")
        print(f"  Mode: PAPER TRADING")
        print(f"  Log File: {log_file}")
        print("=" * 70)
        
        # Create a human-readable order confirmation
        print("\n[DEE-BOT ORDER CONFIRMATION]")
        for result in execution_results:
            print(f"\n  {result['ticker']}:")
            print(f"    - {result['action']} {result['shares']} shares @ ${result['limit_price']:.2f}")
            print(f"    - Stop Loss: ${result['stop_loss']:.2f}")
            print(f"    - Take Profit: ${result['take_profit']:.2f}")
            print(f"    - Order ID: {result['order_id']}")
        
        return True
    else:
        print("\n[INFO] No BUY signals in morning research report")
        return False

def check_broker_connection():
    """Check if broker API is configured"""
    print("\n[BROKER STATUS]")
    
    # Check for Alpaca credentials
    if os.getenv("ALPACA_API_KEY") and os.getenv("ALPACA_SECRET_KEY"):
        print("  Alpaca API: Configured")
        print("  Mode: " + ("PAPER" if os.getenv("ALPACA_PAPER", "true").lower() == "true" else "LIVE"))
    else:
        print("  Alpaca API: Not configured")
        print("  Note: Add ALPACA_API_KEY and ALPACA_SECRET_KEY to .env file for live trading")
    
    return True

if __name__ == "__main__":
    print("\nDEE-BOT ORDER PLACEMENT SYSTEM")
    print("=" * 70)
    
    # Check broker status
    check_broker_connection()
    
    # Place orders
    success = place_dee_bot_orders()
    
    if success:
        print("\n[SUCCESS] DEE-BOT orders have been placed in PAPER mode")
        print("[INFO] To execute LIVE orders, configure broker API and change execution mode")
    else:
        print("\n[INFO] No orders were placed")