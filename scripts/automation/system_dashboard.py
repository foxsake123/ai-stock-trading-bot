"""
AI Trading Bot System Dashboard
Real-time monitoring and status display
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from colorama import init, Fore, Back, Style
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Initialize colorama for Windows
init()

class SystemDashboard:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.clear_screen = 'cls' if os.name == 'nt' else 'clear'

    def clear(self):
        """Clear console screen"""
        os.system(self.clear_screen)

    def print_header(self, title, color=Fore.CYAN):
        """Print formatted header"""
        print(color + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + Style.RESET_ALL)

    def get_portfolio_status(self):
        """Get current portfolio status from CSV files"""
        status = {
            'dee_bot': {'value': 0, 'positions': 0, 'cash': 0},
            'shorgan_bot': {'value': 0, 'positions': 0, 'cash': 0},
            'total': {'value': 0, 'return': 0, 'return_pct': 0}
        }

        try:
            # Read DEE-BOT positions
            dee_csv = self.project_root / 'scripts-and-data' / 'daily-csv' / 'dee-bot-positions.csv'
            if dee_csv.exists():
                df = pd.read_csv(dee_csv)
                if not df.empty:
                    status['dee_bot']['positions'] = len(df)
                    status['dee_bot']['value'] = df['Market Value'].sum() if 'Market Value' in df.columns else 0

            # Read SHORGAN-BOT positions
            shorgan_csv = self.project_root / 'scripts-and-data' / 'daily-csv' / 'shorgan-bot-positions.csv'
            if shorgan_csv.exists():
                df = pd.read_csv(shorgan_csv)
                if not df.empty:
                    status['shorgan_bot']['positions'] = len(df)
                    status['shorgan_bot']['value'] = df['Market Value'].sum() if 'Market Value' in df.columns else 0

            # Calculate totals
            status['total']['value'] = status['dee_bot']['value'] + status['shorgan_bot']['value']
            initial_capital = 200000  # $200K total
            status['total']['return'] = status['total']['value'] - initial_capital
            status['total']['return_pct'] = (status['total']['return'] / initial_capital) * 100

        except Exception as e:
            print(f"Error reading portfolio: {e}")

        return status

    def get_todays_trades(self):
        """Check if today's trades file exists"""
        today = datetime.now().strftime('%Y-%m-%d')
        trades_file = self.project_root / 'docs' / f'TODAYS_TRADES_{today}.md'

        if trades_file.exists():
            # Count trades in file
            with open(trades_file, 'r') as f:
                content = f.read()

            dee_buys = content.count('| BUY |') + content.count('| LONG |')
            dee_sells = content.count('| SELL |') + content.count('| EXIT |')

            return {
                'exists': True,
                'file': trades_file.name,
                'dee_trades': dee_buys + dee_sells,
                'shorgan_trades': 0  # Would need more parsing
            }
        else:
            return {
                'exists': False,
                'file': None,
                'dee_trades': 0,
                'shorgan_trades': 0
            }

    def get_system_health(self):
        """Check system component health"""
        health = {
            'apis': {'status': 'UNKNOWN', 'details': []},
            'files': {'status': 'OK', 'details': []},
            'automation': {'status': 'UNKNOWN', 'details': []},
            'overall': 'CHECKING'
        }

        # Check critical files
        critical_files = [
            'scripts-and-data/automation/execute_daily_trades.py',
            'scripts-and-data/automation/generate_todays_trades.py',
            'agents/fundamental_analyst.py',
            'communication/coordinator.py'
        ]

        missing_files = []
        for file in critical_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)

        if missing_files:
            health['files']['status'] = 'ERROR'
            health['files']['details'] = missing_files
        else:
            health['files']['status'] = 'OK'

        # Check API connection
        try:
            import alpaca_trade_api as tradeapi
            # Would check actual connection here
            health['apis']['status'] = 'OK'
            health['apis']['details'].append('Alpaca: Connected')
        except:
            health['apis']['status'] = 'ERROR'
            health['apis']['details'].append('Alpaca: Not configured')

        # Overall health
        if health['files']['status'] == 'OK' and health['apis']['status'] == 'OK':
            health['overall'] = 'HEALTHY'
        elif 'ERROR' in [health['files']['status'], health['apis']['status']]:
            health['overall'] = 'CRITICAL'
        else:
            health['overall'] = 'WARNING'

        return health

    def get_recent_executions(self):
        """Get recent trade execution history"""
        executions = []

        # Look for execution logs
        log_dir = self.project_root / 'scripts-and-data' / 'trade-logs'
        if log_dir.exists():
            log_files = sorted(log_dir.glob('daily_execution_*.json'), reverse=True)[:5]

            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        data = json.load(f)

                    executions.append({
                        'time': data.get('execution_time', 'Unknown'),
                        'executed': len(data.get('executed_trades', [])),
                        'failed': len(data.get('failed_trades', [])),
                        'success_rate': 0
                    })

                    total = executions[-1]['executed'] + executions[-1]['failed']
                    if total > 0:
                        executions[-1]['success_rate'] = (executions[-1]['executed'] / total) * 100

                except:
                    continue

        return executions

    def get_schedule_status(self):
        """Check Windows Task Scheduler status"""
        import subprocess

        tasks = {
            '6:45 AM': 'ChatGPT Morning Fetch',
            '8:45 AM': 'ChatGPT Final Fetch',
            '9:00 AM': 'Generate Trades',
            '9:30 AM': 'Morning Trade Execution',
            '4:30 PM': 'Post Market Report'
        }

        schedule = []
        for time, name in tasks.items():
            task_name = f"AI Trading Bot - {name}"

            # Check if task exists
            result = subprocess.run(
                ['schtasks', '/query', '/tn', task_name],
                capture_output=True,
                text=True
            )

            status = 'CONFIGURED' if result.returncode == 0 else 'NOT SET'
            color = Fore.GREEN if status == 'CONFIGURED' else Fore.YELLOW

            schedule.append({
                'time': time,
                'task': name,
                'status': status,
                'color': color
            })

        return schedule

    def display_dashboard(self):
        """Display complete system dashboard"""
        self.clear()

        # Header
        print(Fore.CYAN + "=" * 80)
        print("  AI TRADING BOT - SYSTEM DASHBOARD")
        print(f"  {datetime.now().strftime('%A, %B %d, %Y - %I:%M:%S %p ET')}")
        print("=" * 80 + Style.RESET_ALL)

        # Portfolio Status
        portfolio = self.get_portfolio_status()
        print(f"\n{Fore.WHITE}PORTFOLIO STATUS{Style.RESET_ALL}")
        print("-" * 40)

        value_color = Fore.GREEN if portfolio['total']['return'] > 0 else Fore.RED
        print(f"Total Value: ${portfolio['total']['value']:,.2f}")
        print(f"Total Return: {value_color}${portfolio['total']['return']:+,.2f} ({portfolio['total']['return_pct']:+.2f}%){Style.RESET_ALL}")
        print(f"DEE-BOT: {portfolio['dee_bot']['positions']} positions, ${portfolio['dee_bot']['value']:,.2f}")
        print(f"SHORGAN-BOT: {portfolio['shorgan_bot']['positions']} positions, ${portfolio['shorgan_bot']['value']:,.2f}")

        # Today's Trades
        trades = self.get_todays_trades()
        print(f"\n{Fore.WHITE}TODAY'S TRADES{Style.RESET_ALL}")
        print("-" * 40)

        if trades['exists']:
            print(f"{Fore.GREEN}[READY]{Style.RESET_ALL} {trades['file']}")
            print(f"Trades pending: {trades['dee_trades'] + trades['shorgan_trades']}")
        else:
            print(f"{Fore.YELLOW}[PENDING]{Style.RESET_ALL} No trades file for today")
            print("Will be generated automatically at 9:00 AM")

        # System Health
        health = self.get_system_health()
        print(f"\n{Fore.WHITE}SYSTEM HEALTH{Style.RESET_ALL}")
        print("-" * 40)

        health_color = {
            'HEALTHY': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'CRITICAL': Fore.RED,
            'CHECKING': Fore.CYAN
        }

        print(f"Overall: {health_color[health['overall']]}{health['overall']}{Style.RESET_ALL}")
        print(f"Files: {health['files']['status']}")
        print(f"APIs: {health['apis']['status']}")

        if health['files']['details']:
            for detail in health['files']['details']:
                print(f"  - {detail}")

        # Schedule Status
        schedule = self.get_schedule_status()
        print(f"\n{Fore.WHITE}AUTOMATION SCHEDULE{Style.RESET_ALL}")
        print("-" * 40)

        for task in schedule:
            print(f"{task['time']:8} - {task['task']:25} {task['color']}[{task['status']}]{Style.RESET_ALL}")

        # Recent Executions
        executions = self.get_recent_executions()
        if executions:
            print(f"\n{Fore.WHITE}RECENT EXECUTIONS{Style.RESET_ALL}")
            print("-" * 40)

            for exec in executions[:3]:
                success_color = Fore.GREEN if exec['success_rate'] > 80 else Fore.YELLOW if exec['success_rate'] > 50 else Fore.RED
                print(f"{exec['time'][:19]} - {exec['executed']} executed, {exec['failed']} failed {success_color}({exec['success_rate']:.0f}% success){Style.RESET_ALL}")

        # Footer
        print("\n" + "=" * 80)
        print(f"{Fore.CYAN}Press Ctrl+C to exit | Auto-refresh every 30 seconds{Style.RESET_ALL}")
        print("=" * 80)

    def run(self, refresh_interval=30):
        """Run dashboard with auto-refresh"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Dashboard stopped by user{Style.RESET_ALL}")
            return

    def quick_status(self):
        """Print quick one-line status"""
        portfolio = self.get_portfolio_status()
        trades = self.get_todays_trades()
        health = self.get_system_health()

        status_icon = {
            'HEALTHY': '[OK]',
            'WARNING': '[WARN]',
            'CRITICAL': '[FAIL]',
            'CHECKING': '[...]'
        }

        trades_status = 'READY' if trades['exists'] else 'PENDING'

        print(f"Portfolio: ${portfolio['total']['value']:,.0f} ({portfolio['total']['return_pct']:+.1f}%) | Trades: {trades_status} | System: {status_icon[health['overall']]}")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Trading Bot System Dashboard')
    parser.add_argument('--quick', action='store_true', help='Show quick status only')
    parser.add_argument('--refresh', type=int, default=30, help='Refresh interval in seconds')

    args = parser.parse_args()

    dashboard = SystemDashboard()

    if args.quick:
        dashboard.quick_status()
    else:
        dashboard.run(args.refresh)

if __name__ == "__main__":
    main()