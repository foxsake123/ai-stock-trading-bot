#!/usr/bin/env python3
"""
Monitored Trade Execution
Wraps execute_daily_trades.py with health monitoring
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run trade execution with monitoring"""
    health_monitor = Path(__file__).parent.parent / 'monitoring' / 'automation_health_monitor.py'

    try:
        # Run trade execution
        result = subprocess.run(
            [sys.executable, 'scripts/automation/execute_daily_trades.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )

        if result.returncode == 0:
            # Success - parse output for execution stats
            output = result.stdout
            print(output)

            # Try to extract execution stats
            exec_details = {}
            if 'Successful trades:' in output:
                # Extract success count (simple parsing)
                exec_details['output'] = 'Trades executed'

            # Report success
            subprocess.run([
                sys.executable, str(health_monitor),
                '--task', 'trade-execution',
                '--status', 'success',
                '--details', str(exec_details).replace("'", '"')
            ])

            return 0
        else:
            # Failure
            print(result.stdout)
            print(result.stderr, file=sys.stderr)

            # Report failure
            error_msg = result.stderr[:500] if result.stderr else 'Unknown error'
            subprocess.run([
                sys.executable, str(health_monitor),
                '--task', 'trade-execution',
                '--status', 'failure',
                '--error', error_msg
            ])

            return result.returncode

    except subprocess.TimeoutExpired:
        error_msg = 'Trade execution timed out after 10 minutes'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'trade-execution',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

    except Exception as e:
        error_msg = f'Unexpected error: {str(e)[:500]}'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'trade-execution',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

if __name__ == '__main__':
    sys.exit(main())
