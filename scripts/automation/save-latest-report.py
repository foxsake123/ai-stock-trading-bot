"""
Save the latest ChatGPT report manually
"""

import json
import os
from datetime import datetime

def save_chatgpt_report():
    """Save the new ChatGPT report with 5+ trades"""
    
    # This is a placeholder structure - you'll need to provide the actual trades
    report = {
        "date": "2025-09-16",
        "time": datetime.now().strftime("%H:%M:%S"),
        "source": "ChatGPT TradingAgents",
        "market_context": "Tuesday, Sep 16, 2025 - Multiple catalyst opportunities across FDA events, insider buying, and earnings plays",
        "trades": [
            {
                "symbol": "PLACEHOLDER1",
                "action": "long",
                "catalyst": "FDA PDUFA date approaching",
                "entry": "market",
                "stop_pct": 10,
                "target": 30,
                "size_pct": 4,
                "confidence": "medium",
                "note": "Binary event - size accordingly"
            },
            {
                "symbol": "PLACEHOLDER2", 
                "action": "long",
                "catalyst": "Insider buying - CEO purchase",
                "entry": "market",
                "stop_pct": 8,
                "target": 25,
                "size_pct": 7,
                "confidence": "high",
                "note": "Strong insider confidence signal"
            },
            {
                "symbol": "PLACEHOLDER3",
                "action": "long",
                "catalyst": "Earnings beat expected",
                "entry": "market",
                "stop_pct": 7,
                "target": 20,
                "size_pct": 6,
                "confidence": "medium",
                "note": "Momentum play on strong guidance"
            },
            {
                "symbol": "PLACEHOLDER4",
                "action": "long",
                "catalyst": "Short squeeze setup",
                "entry": "market",
                "stop_pct": 9,
                "target": 35,
                "size_pct": 5,
                "confidence": "medium",
                "note": "High short interest, catalyst pending"
            },
            {
                "symbol": "PLACEHOLDER5",
                "action": "long",
                "catalyst": "FDA approval expected",
                "entry": "market",
                "stop_pct": 12,
                "target": 40,
                "size_pct": 3,
                "confidence": "low-medium",
                "note": "High risk/reward binary event"
            }
        ],
        "risk_management": {
            "max_position_size_pct": 10,
            "catalyst_high_risk_size_pct": "2-5",
            "stop_loss_mandatory": True,
            "portfolio_hedge": "SPY puts for downside protection"
        },
        "status": "AWAITING_ACTUAL_TRADES",
        "note": "ChatGPT is generating the actual trade recommendations. This is a placeholder structure."
    }
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report template saved to: {filename}")
    print("\n" + "="*60)
    print("IMPORTANT: ChatGPT is generating the actual trades.")
    print("Please update this file with the real recommendations when available.")
    print("="*60)
    
    return filename

def manual_input_mode():
    """Allow manual input of trades"""
    print("\n" + "="*60)
    print("MANUAL TRADE INPUT MODE")
    print("="*60)
    print("\nIf ChatGPT has provided the trades, you can paste them here.")
    print("Otherwise, press Enter to skip and wait for automatic capture.\n")
    
    response = input("Do you have the trade details to input? (y/n): ")
    
    if response.lower() != 'y':
        print("Waiting for automatic capture via browser extension...")
        return
    
    trades = []
    print("\nEnter trade details (enter 'done' when finished):\n")
    
    while True:
        symbol = input("Symbol (or 'done'): ").upper()
        if symbol == 'DONE':
            break
            
        trade = {
            "symbol": symbol,
            "action": input("Action (long/short): ").lower(),
            "catalyst": input("Catalyst: "),
            "entry": input("Entry (market/limit): "),
            "stop_pct": float(input("Stop loss %: ") or 8),
            "target": float(input("Target gain %: ") or 25),
            "size_pct": float(input("Position size %: ") or 5),
            "confidence": input("Confidence (low/medium/high): "),
            "note": input("Additional notes: ")
        }
        trades.append(trade)
        print(f"\nAdded {symbol} to trades list.\n")
    
    if trades:
        # Save the actual report
        report = {
            "date": "2025-09-16",
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": "ChatGPT TradingAgents (Manual Input)",
            "trades": trades,
            "market_context": "Multiple catalyst opportunities for Tuesday, Sep 16, 2025",
            "risk_management": {
                "max_position_size_pct": 10,
                "stop_loss_mandatory": True
            }
        }
        
        filename = "02_data/research/reports/pre_market_daily/2025-09-16_chatgpt_report_manual.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nSaved {len(trades)} trades to: {filename}")
        return filename
    
    return None

if __name__ == "__main__":
    print("ChatGPT Report Manager")
    print("-" * 30)
    print("ChatGPT is preparing 5+ trade recommendations...")
    print("\nOptions:")
    print("1. Wait for automatic capture (browser extension)")
    print("2. Input trades manually")
    print("3. Create placeholder template")
    
    choice = input("\nSelect option (1/2/3): ")
    
    if choice == '2':
        manual_input_mode()
    elif choice == '3':
        save_chatgpt_report()
    else:
        print("\nWaiting for automatic capture...")
        print("Make sure the browser extension is active on ChatGPT.com")
        print("The report will be saved automatically when ChatGPT completes it.")