"""
Verify Task Scheduler tasks are configured for AI Trading Bot
"""
import subprocess
import sys

def check_task_exists(task_name):
    """Check if a scheduled task exists"""
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/tn', task_name, '/fo', 'LIST'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking task '{task_name}': {e}")
        return False

def get_task_info(task_name):
    """Get detailed info about a task"""
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/tn', task_name, '/fo', 'LIST', '/v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Extract key lines
            lines = result.stdout.split('\n')
            info = {}
            for line in lines:
                if 'Status:' in line:
                    info['Status'] = line.split(':', 1)[1].strip()
                elif 'Next Run Time:' in line:
                    info['Next Run'] = line.split(':', 1)[1].strip()
                elif 'Last Run Time:' in line:
                    info['Last Run'] = line.split(':', 1)[1].strip()
                elif 'Task To Run:' in line:
                    info['Command'] = line.split(':', 1)[1].strip()
            return info
        return None
    except Exception as e:
        print(f"Error getting info for '{task_name}': {e}")
        return None

def main():
    print("=" * 70)
    print("AI TRADING BOT - TASK SCHEDULER VERIFICATION")
    print("=" * 70)
    print()

    # Expected tasks
    tasks = [
        "AI Trading - Weekend Research",
        "AI Trading - Morning Trade Generation",
        "AI Trading - Trade Execution",
        "AI Trading - Daily Performance Graph",
        "AI Trading - Stop Loss Monitor",
        "AI Trading - Profit Taking Manager"
    ]

    found_count = 0
    missing_count = 0

    for task_name in tasks:
        exists = check_task_exists(task_name)

        if exists:
            print(f"[OK] {task_name}")
            info = get_task_info(task_name)
            if info:
                for key, value in info.items():
                    print(f"     {key}: {value}")
            found_count += 1
        else:
            print(f"[MISSING] {task_name}")
            missing_count += 1
        print()

    print("=" * 70)
    print(f"SUMMARY: {found_count} tasks configured, {missing_count} missing")
    print("=" * 70)
    print()

    if missing_count > 0:
        print("ACTION REQUIRED:")
        print("1. Right-click on 'setup_week1_tasks.bat'")
        print("2. Select 'Run as administrator'")
        print("3. Wait for tasks to be created")
        print("4. Run this script again to verify")
        return 1
    else:
        print("SUCCESS! All automation tasks are configured.")
        print("The system will now run automatically:")
        print("  - Weekend Research: Saturday 12:00 PM")
        print("  - Trade Generation: Weekdays 8:30 AM")
        print("  - Trade Execution: Weekdays 9:30 AM")
        print("  - Performance Graph: Weekdays 4:30 PM")
        print("  - Stop Loss Monitor: Every 5 minutes")
        print("  - Profit Taking: Hourly")
        return 0

if __name__ == "__main__":
    sys.exit(main())
