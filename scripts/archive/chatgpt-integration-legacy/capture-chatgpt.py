"""
Capture ChatGPT Trading Recommendations
Interactive tool to input the 5+ trades from ChatGPT
"""

import json
import os
from datetime import datetime

def capture_trades():
    """Interactively capture trade recommendations from ChatGPT"""
    
    print("\n" + "="*70)
    print("CHATGPT TRADE CAPTURE TOOL")
    print("="*70)
    print("\nPlease enter the trade recommendations from ChatGPT.")
    print("I'll guide you through each trade step by step.\n")
    
    trades = []
    trade_num = 1
    
    while True:
        print(f"\n--- TRADE #{trade_num} ---")
        print("(Type 'done' for symbol when finished entering trades)\n")
        
        symbol = input("Symbol/Ticker: ").upper().strip()
        if symbol == 'DONE' or symbol == '':
            break
        
        print(f"\nEntering details for {symbol}:")
        
        # Get trade details with defaults
        action = input("Action (long/short) [default: long]: ").lower().strip() or "long"
        
        catalyst = input("Catalyst/Reason: ").strip()
        
        # Position sizing
        size_input = input("Position size (% of portfolio) [default: 5]: ").strip()
        size_pct = float(size_input) if size_input else 5.0
        
        # Entry
        entry = input("Entry type (market/limit/specific price) [default: market]: ").strip() or "market"
        
        # Stop loss
        stop_input = input("Stop loss (% below entry) [default: 8]: ").strip()
        stop_pct = float(stop_input) if stop_input else 8.0
        
        # Targets
        target1_input = input("Target 1 (% gain) [default: 20]: ").strip()
        target1 = float(target1_input) if target1_input else 20.0
        
        target2_input = input("Target 2 (% gain, or press Enter to skip): ").strip()
        target2 = float(target2_input) if target2_input else None
        
        # Confidence
        confidence = input("Confidence level (low/medium/high) [default: medium]: ").strip() or "medium"
        
        # Options strategy (if any)
        options = input("Options strategy (or press Enter to skip): ").strip()
        
        # Additional notes
        notes = input("Additional notes (or press Enter to skip): ").strip()
        
        # Build trade object
        trade = {
            "symbol": symbol,
            "action": action,
            "catalyst": catalyst,
            "entry": entry,
            "stop_pct": stop_pct,
            "target": target1,
            "size_pct": size_pct,
            "confidence": confidence
        }
        
        if target2:
            trade["target2"] = target2
        if options:
            trade["options_strategy"] = options
        if notes:
            trade["note"] = notes
            
        trades.append(trade)
        trade_num += 1
        
        print(f"\n✅ Added {symbol} to trade list")
    
    if not trades:
        print("\nNo trades entered. Exiting...")
        return None
    
    # Get market context
    print("\n" + "-"*50)
    print("MARKET CONTEXT")
    print("-"*50)
    market_context = input("\nMarket context/summary (or press Enter for default): ").strip()
    if not market_context:
        market_context = "Multiple catalyst opportunities across FDA events, insider buying, and earnings plays for Tuesday, September 16, 2025"
    
    # Build complete report
    report = {
        "date": "2025-09-16",
        "time": datetime.now().strftime("%H:%M:%S"),
        "source": "ChatGPT TradingAgents",
        "market_context": market_context,
        "trades": trades,
        "risk_management": {
            "max_position_size_pct": 10,
            "catalyst_high_risk_size_pct": "2-5",
            "options_max_loss_pct": 1,
            "portfolio_hedge": "SPY puts for downside protection",
            "stop_loss_mandatory": True,
            "profit_taking_rules": {
                "move_to_breakeven_at_pct": 20,
                "trailing_stop_volatile_pct": 9,
                "trailing_stop_stable_pct": 6
            }
        },
        "execution_notes": [
            "No single trade exceeds 10% of portfolio",
            "Biotech/binary events limited to 2-5%",
            "Exit before binary events unless high conviction",
            "Use technical support for stop placement"
        ]
    }
    
    # Save the report
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_trades_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also overwrite the main file for pipeline processing
    main_file = "02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report.json"
    with open(main_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*70)
    print("CAPTURE COMPLETE!")
    print("="*70)
    print(f"\n✅ Saved {len(trades)} trades to:")
    print(f"   {filename}")
    print(f"   {main_file}")
    
    # Display summary
    print("\nTRADE SUMMARY:")
    print("-"*50)
    for i, trade in enumerate(trades, 1):
        print(f"{i}. {trade['symbol']} - {trade['action'].upper()} - {trade['size_pct']}% position")
        print(f"   Catalyst: {trade['catalyst']}")
        print(f"   Stop: -{trade['stop_pct']}% | Target: +{trade['target']}%")
    
    total_allocation = sum(t['size_pct'] for t in trades)
    print(f"\nTotal Portfolio Allocation: {total_allocation}%")
    
    return filename

if __name__ == "__main__":
    print("ChatGPT Trade Capture Tool")
    print("Version 1.0")
    
    filename = capture_trades()
    
    if filename:
        print("\n✅ Ready to process trades through the pipeline!")
        print("\nNext steps:")
        print("1. Run multi-agent analysis")
        print("2. Execute approved trades")
        print("3. Generate and send reports")
        
        run_pipeline = input("\nRun the trading pipeline now? (y/n): ").lower()
        if run_pipeline == 'y':
            print("\nStarting pipeline...")
            import subprocess
            subprocess.run(["python", "01_trading_system/automation/daily_pre_market_pipeline.py", "--bot", "SHORGAN"])