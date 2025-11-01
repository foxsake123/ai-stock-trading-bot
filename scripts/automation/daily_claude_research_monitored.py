#!/usr/bin/env python3
"""
Monitored Research Generation
Wraps daily_claude_research.py with health monitoring
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Run research generation with monitoring"""
    health_monitor = Path(__file__).parent.parent / 'monitoring' / 'automation_health_monitor.py'

    try:
        # Run research generation
        result = subprocess.run(
            [sys.executable, 'scripts/automation/daily_claude_research.py', '--force'],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes
        )

        if result.returncode == 0:
            # Success
            print(result.stdout)

            # Report success
            subprocess.run([
                sys.executable, str(health_monitor),
                '--task', 'research',
                '--status', 'success',
                '--details', '{"output": "Research generated successfully"}'
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
                '--task', 'research',
                '--status', 'failure',
                '--error', error_msg
            ])

            return result.returncode

    except subprocess.TimeoutExpired:
        # Timeout
        error_msg = 'Research generation timed out after 30 minutes'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'research',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

    except Exception as e:
        # Unexpected error
        error_msg = f'Unexpected error: {str(e)[:500]}'
        print(error_msg, file=sys.stderr)

        subprocess.run([
            sys.executable, str(health_monitor),
            '--task', 'research',
            '--status', 'failure',
            '--error', error_msg
        ])

        return 1

if __name__ == '__main__':
    sys.exit(main())
