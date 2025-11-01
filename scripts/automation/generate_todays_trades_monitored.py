#!/usr/bin/env python3
"""
Monitored Trade Generation
Wraps generate_todays_trades_v2.py with health monitoring
"""

import sys
import subprocess
from pathlib import Path

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

            # Try to extract approval rate from output
            approval_details = {}
            if 'approved' in output.lower():
                # Simple extraction (can be enhanced)
                approval_details['output'] = 'Trades generated successfully'

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
