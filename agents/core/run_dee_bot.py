"""
DEE-BOT Master Execution Script
Orchestrates the complete beta-neutral trading workflow with 2X leverage
"""

import json
import sys
import os
from datetime import datetime, date
from pathlib import Path
import subprocess
import time

def load_config():
    """Load bot configuration"""
    config_file = Path("C:/Users/shorg/ai-stock-trading-bot/01_trading_system/config/dee_bot_config.json")
    
    if not config_file.exists():
        print("[ERROR] Configuration file not found")
        return None
    
    with open(config_file, 'r') as f:
        return json.load(f)

def run_step(step_name, command, config):
    """Execute a workflow step"""
    print("\n" + "=" * 80)
    print(f"STEP: {step_name}")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd="C:/Users/shorg/ai-stock-trading-bot/01_trading_system"
        )
        
        if result.returncode == 0:
            print(f"[SUCCESS] {step_name} completed")
            if result.stdout:
                print("\nOutput Preview:")
                lines = result.stdout.split('\n')[:20]  # Show first 20 lines
                for line in lines:
                    print(line)
            return True
        else:
            print(f"[ERROR] {step_name} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to execute {step_name}: {str(e)}")
        return False

def check_market_status():
    """Check if market is open"""
    from datetime import datetime
    import alpaca_trade_api as tradeapi
    
    config = load_config()
    api_config = config['api_keys']['alpaca']
    
    try:
        api = tradeapi.REST(
            api_config['key_id'],
            api_config['secret_key'],
            api_config['base_url'],
            api_version=api_config['api_version']
        )
        
        clock = api.get_clock()
        
        print("\n" + "=" * 80)
        print("MARKET STATUS")
        print("=" * 80)
        print(f"Market Open: {clock.is_open}")
        print(f"Next Open: {clock.next_open}")
        print(f"Next Close: {clock.next_close}")
        
        return clock.is_open
        
    except Exception as e:
        print(f"[WARNING] Could not check market status: {str(e)}")
        return True  # Assume open for paper trading

def generate_daily_report(config):
    """Generate end-of-day report"""
    print("\n" + "=" * 80)
    print("DAILY REPORT")
    print("=" * 80)
    
    report = {
        'date': str(date.today()),
        'timestamp': datetime.now().isoformat(),
        'bot': 'DEE-BOT',
        'strategy': 'Beta-Neutral with 2X Leverage',
        'steps_completed': [],
        'configuration': {
            'leverage_enabled': config['leverage']['enabled'],
            'leverage_multiplier': config['leverage']['multiplier'],
            'beta_neutral': config['trading_strategy']['enabled'],
            'target_beta': config['trading_strategy']['target_beta']
        }
    }
    
    # Check for today's files
    rec_file = Path(f"C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_recommendations/dee_bot_recommendations_{date.today()}.json")
    
    if rec_file.exists():
        report['steps_completed'].append('recommendations_generated')
        with open(rec_file, 'r') as f:
            rec_data = json.load(f)
            report['recommendations_count'] = len(rec_data.get('top_recommendations', []))
            report['portfolio_beta'] = rec_data.get('portfolio_beta', 0)
    
    # Check for execution logs
    log_dir = Path("C:/Users/shorg/ai-stock-trading-bot/09_logs/trading")
    today_logs = list(log_dir.glob(f"dee_bot_beta_neutral_execution_{date.today().strftime('%Y%m%d')}*.json"))
    
    if today_logs:
        report['steps_completed'].append('trades_executed')
        report['execution_logs'] = len(today_logs)
        
        # Get latest execution summary
        latest_log = sorted(today_logs)[-1]
        with open(latest_log, 'r') as f:
            exec_data = json.load(f)
            report['execution_summary'] = exec_data.get('summary', {})
    
    # Save report
    report_dir = Path("C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"dee_bot_daily_report_{date.today()}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved: {report_file}")
    
    # Display summary
    print("\nSummary:")
    print(f"  Date: {report['date']}")
    print(f"  Strategy: {report['strategy']}")
    print(f"  Steps Completed: {', '.join(report['steps_completed'])}")
    
    if 'recommendations_count' in report:
        print(f"  Recommendations: {report['recommendations_count']}")
        print(f"  Portfolio Beta: {report['portfolio_beta']:.3f}")
    
    if 'execution_summary' in report:
        summary = report['execution_summary']
        print(f"  Trades Executed: {summary.get('total_executed', 0)}")
        print(f"  Portfolio Value: ${summary.get('total_value', 0):,.2f}")
        print(f"  Leverage Used: {summary.get('leverage_used', 1)}x")
    
    return report

def main():
    """Main workflow orchestrator"""
    print("=" * 80)
    print("DEE-BOT BETA-NEUTRAL TRADING SYSTEM")
    print("2X LEVERAGE ENABLED")
    print("=" * 80)
    print(f"Date: {date.today()}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    print(f"\nConfiguration Loaded:")
    print(f"  Strategy: {config['description']}")
    print(f"  Leverage: {config['leverage']['multiplier']}x")
    print(f"  Auto Execute: {config['execution']['auto_execute']}")
    
    # Check market status
    market_open = check_market_status()
    
    if not market_open:
        print("\n[INFO] Market is closed. Running in simulation mode.")
    
    # Workflow steps
    workflow = [
        {
            'name': 'Generate Recommendations',
            'command': 'python generate_dee_bot_recommendations.py',
            'required': True
        },
        {
            'name': 'Test Beta Calculations',
            'command': 'python bots/dee_bot/test_beta_neutral.py',
            'required': False
        },
        {
            'name': 'Risk Assessment',
            'command': 'python bots/dee_bot/risk_manager_leveraged.py',
            'required': True
        },
        {
            'name': 'Execute Beta-Neutral Strategy',
            'command': 'python execute_dee_bot_beta_neutral.py',
            'required': True
        }
    ]
    
    # Execute workflow
    print("\n" + "=" * 80)
    print("EXECUTING WORKFLOW")
    print("=" * 80)
    
    steps_completed = []
    steps_failed = []
    
    for step in workflow:
        if config['execution']['auto_execute'] or step['required']:
            success = run_step(step['name'], step['command'], config)
            
            if success:
                steps_completed.append(step['name'])
            else:
                steps_failed.append(step['name'])
                
                if step['required']:
                    print(f"\n[CRITICAL] Required step '{step['name']}' failed")
                    print("Workflow terminated")
                    break
            
            # Rate limiting
            time.sleep(2)
    
    # Generate daily report
    report = generate_daily_report(config)
    
    # Final summary
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    print(f"Steps Completed: {len(steps_completed)}")
    print(f"Steps Failed: {len(steps_failed)}")
    
    if steps_completed:
        print("\nCompleted:")
        for step in steps_completed:
            print(f"  ✓ {step}")
    
    if steps_failed:
        print("\nFailed:")
        for step in steps_failed:
            print(f"  ✗ {step}")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--auto':
            # Enable auto execution
            config_file = Path("C:/Users/shorg/ai-stock-trading-bot/01_trading_system/config/dee_bot_config.json")
            with open(config_file, 'r') as f:
                config = json.load(f)
            config['execution']['auto_execute'] = True
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("[INFO] Auto-execution enabled")
        elif sys.argv[1] == '--test':
            # Run in test mode
            print("[INFO] Running in test mode")
    
    main()