#!/usr/bin/env python3
"""
Monitored Trade Generation
Wraps generate_todays_trades_v2.py with health monitoring
"""

import sys
import re
import subprocess
from pathlib import Path

def extract_approval_rate(output):
    """Extract approval rate from trade generation output"""
    details = {}

    # Look for OVERALL line: "OVERALL: 15/30 approved (50.0%)"
    overall_match = re.search(r'OVERALL:\s+(\d+)/(\d+)\s+approved\s+\(([\d.]+)%\)', output)
    if overall_match:
        approved = int(overall_match.group(1))
        total = int(overall_match.group(2))
        pct = float(overall_match.group(3))

        details['trades_approved'] = approved
        details['trades_total'] = total
        details['approval_rate'] = f"{pct:.1f}%"

        # Add status indicator
        if pct == 0:
            details['status'] = 'WARNING: 0% approval'
        elif pct == 100:
            details['status'] = 'WARNING: 100% approval'
        elif pct < 20:
            details['status'] = 'CAUTION: Low approval'
        elif pct > 80:
            details['status'] = 'CAUTION: High approval'
        else:
            details['status'] = 'OK'
    else:
        details['output'] = 'Trades generated (rate unknown)'

    return details

def main():
    """Run trade generation with monitoring"""
    health_monitor = Path(__file__).parent.parent / 'monitoring' / 'automation_health_monitor.py'

    try:
        # Run trade generation
        result = subprocess.run(
            [sys.executable, 'scripts/automation/generate_todays_trades_v2.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )

        if result.returncode == 0:
            # Success - parse output for approval rate
            output = result.stdout
            print(output)

            # Extract approval rate details
            approval_details = extract_approval_rate(output)

            # Report success
            subprocess.run([
                sys.executable, str(health_monitor),
                '--task', 'trade-generation',
                '--status', 'success',
                '--details', str(approval_details).replace("'", '"')
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
                '--task', 'trade-generation',
                '--status', 'failure',
                '--error', error_msg
            ])

            return result.returncode

    except subprocess.TimeoutExpired:
        error_msg = 'Trade generation timed out after 10 minutes'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'trade-generation',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

    except Exception as e:
        error_msg = f'Unexpected error: {str(e)[:500]}'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'trade-generation',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

if __name__ == '__main__':
    sys.exit(main())
