#!/usr/bin/env python3
"""
Check daily trading status and performance
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def check_status():
    """Check trading system status"""
    
    print("=" * 60)
    print(f"Trading Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load execution log
    log_file = Path("data/execution_log.json")
    if log_file.exists():
        with open(log_file, 'r') as f:
            executions = json.load(f)
        
        # Today's trades
        today = datetime.now().date()
        today_trades = [e for e in executions if datetime.fromisoformat(e['timestamp']).date() == today]
        
        print(f"\nToday's Trading Activity ({today}):")
        print("-" * 40)
        print(f"Total Trades Attempted: {len(today_trades)}")
        
        successful = sum(1 for t in today_trades if t.get('success', False))
        print(f"Successful Executions: {successful}")
        print(f"Failed/Rejected: {len(today_trades) - successful}")
        
        # Calculate by bot
        by_bot = defaultdict(list)
        for trade in today_trades:
            by_bot[trade['bot_name']].append(trade)
        
        print(f"\nBy Bot:")
        for bot_name, bot_trades in by_bot.items():
            success_count = sum(1 for t in bot_trades if t.get('success', False))
            print(f"  {bot_name}: {len(bot_trades)} trades ({success_count} successful)")
        
        # Show today's trades
        if today_trades:
            print(f"\nToday's Trade Details:")
            print("-" * 40)
            for trade in today_trades:
                status = "[OK]" if trade.get('success') else "[FAIL]"
                time = datetime.fromisoformat(trade['timestamp']).strftime('%H:%M:%S')
                print(f"{status} {time}: {trade['action']} {trade['shares']} {trade['ticker']}")
                print(f"      Bot: {trade['bot_name']} | Confidence: {trade['confidence']:.0%}")
                print(f"      Message: {trade['message']}")
        
        # Weekly summary
        week_ago = datetime.now().date() - timedelta(days=7)
        week_trades = [e for e in executions if datetime.fromisoformat(e['timestamp']).date() >= week_ago]
        
        if week_trades:
            print(f"\nWeekly Summary (Last 7 Days):")
            print("-" * 40)
            print(f"Total Trades: {len(week_trades)}")
            week_success = sum(1 for t in week_trades if t.get('success', False))
            print(f"Success Rate: {week_success}/{len(week_trades)} ({week_success/len(week_trades)*100:.1f}%)")
            
            # Count by action
            buys = sum(1 for t in week_trades if t['action'] == 'BUY')
            sells = sum(1 for t in week_trades if t['action'] == 'SELL')
            print(f"Buy Orders: {buys}")
            print(f"Sell Orders: {sells}")
    else:
        print("[INFO] No execution log found - no trades executed yet")
    
    # Check signal log
    signal_file = Path("data/signal_log.json")
    if signal_file.exists():
        with open(signal_file, 'r') as f:
            signals = json.load(f)
        
        # Today's signals
        today_str = datetime.now().date().isoformat()
        today_signals = [s for s in signals if s['timestamp'].startswith(today_str)]
        
        print(f"\nSignal Generation:")
        print("-" * 40)
        print(f"Signals Generated Today: {sum(s['count'] for s in today_signals)}")
        
        for signal in today_signals[-5:]:  # Last 5 signal batches
            time = datetime.fromisoformat(signal['timestamp']).strftime('%H:%M:%S')
            print(f"  {time}: {signal['bot']} generated {signal['count']} signals")
    
    # Check for errors in log
    log_file = Path("logs/trading_system.log")
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Count errors and warnings
        errors = [l for l in lines if 'ERROR' in l]
        warnings = [l for l in lines if 'WARNING' in l]
        
        print(f"\nSystem Health:")
        print("-" * 40)
        print(f"Errors Today: {len(errors)}")
        print(f"Warnings Today: {len(warnings)}")
        
        if errors:
            print(f"\nLast Error:")
            print(f"  {errors[-1].strip()}")
    
    # Check configuration
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    print(f"\nCurrent Configuration:")
    print("-" * 40)
    print(f"Execution Mode: {os.getenv('EXECUTION_MODE', 'paper').upper()}")
    print(f"Max Position Size: ${os.getenv('MAX_POSITION_SIZE', '50000')}")
    print(f"Max Daily Trades: {os.getenv('MAX_DAILY_TRADES', '20')}")
    print(f"Max Daily Loss: ${os.getenv('MAX_DAILY_LOSS', '10000')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_status()