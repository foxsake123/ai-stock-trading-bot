#!/usr/bin/env python3
"""
Monitored Performance Graph Generation
Wraps generate_performance_graph.py with health monitoring
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run performance graph generation with monitoring"""
    health_monitor = Path(__file__).parent.parent / 'monitoring' / 'automation_health_monitor.py'

    try:
        # Run performance graph generation
        result = subprocess.run(
            [sys.executable, 'scripts/performance/generate_performance_graph.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            # Success
            output = result.stdout
            print(output)

            # Report success
            subprocess.run([
                sys.executable, str(health_monitor),
                '--task', 'performance',
                '--status', 'success',
                '--details', '{"output": "Performance graph generated"}'
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
                '--task', 'performance',
                '--status', 'failure',
                '--error', error_msg
            ])

            return result.returncode

    except subprocess.TimeoutExpired:
        error_msg = 'Performance graph generation timed out after 5 minutes'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'performance',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

    except Exception as e:
        error_msg = f'Unexpected error: {str(e)[:500]}'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'performance',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

if __name__ == '__main__':
    sys.exit(main())
