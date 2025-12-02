"""
Comprehensive automation diagnostics - identify why tasks aren't running
"""
import subprocess
import os
from datetime import datetime
from pathlib import Path

def check_task_details(task_name):
    """Get detailed task configuration"""
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/tn', task_name, '/fo', 'LIST', '/v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            config = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Extract important settings
                    if 'Last Run Time' in key:
                        config['Last Run'] = value
                    elif 'Next Run Time' in key:
                        config['Next Run'] = value
                    elif 'Status:' in key:
                        config['Status'] = value
                    elif 'Logon Mode:' in key:
                        config['Logon Mode'] = value
                    elif 'Run As User:' in key:
                        config['Run As'] = value
                    elif 'Power Management' in key or 'wake the computer' in line.lower():
                        config['Wake Computer'] = 'Yes' if 'true' in value.lower() else 'No'
                    elif 'Stop the task if it runs' in key:
                        config['Max Runtime'] = value
            return config
        return None
    except Exception as e:
        print(f"Error checking {task_name}: {e}")
        return None

def check_file_existence():
    """Check if expected files exist"""
    print("\n" + "=" * 80)
    print("FILE EXISTENCE CHECK")
    print("=" * 80)

    files_to_check = [
        ("Research Nov 11", "reports/premarket/2025-11-11/claude_research_dee_bot_2025-11-11.md"),
        ("Research Nov 15", "reports/premarket/2025-11-15/"),
        ("Research Nov 18", "reports/premarket/2025-11-18/"),
        ("Trades Nov 11", "docs/TODAYS_TRADES_2025-11-11.md"),
        ("Trades Nov 14", "docs/TODAYS_TRADES_2025-11-14.md"),
    ]

    for name, path in files_to_check:
        exists = os.path.exists(path)
        status = "[OK] EXISTS" if exists else "[MISSING]"
        print(f"{status}: {name} ({path})")

        if exists and os.path.isfile(path):
            mod_time = datetime.fromtimestamp(os.path.getmtime(path))
            print(f"         Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

def check_power_settings():
    """Check Windows power settings"""
    print("\n" + "=" * 80)
    print("POWER SETTINGS CHECK")
    print("=" * 80)

    try:
        # Check sleep settings
        result = subprocess.run(
            ['powercfg', '/query', 'SCHEME_CURRENT', 'SUB_SLEEP'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout
            if 'Sleep after' in lines:
                print("Current power plan allows sleep")
                print("[!] Computer may sleep and miss scheduled tasks")
            else:
                print("[OK] Power settings checked")
        else:
            print("[!] Could not query power settings")

    except Exception as e:
        print(f"[!] Power check failed: {e}")

def main():
    print("=" * 80)
    print("AI TRADING BOT - AUTOMATION DIAGNOSTICS")
    print("=" * 80)
    print(f"Diagnostic Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check each task
    tasks = [
        "AI Trading - Weekend Research",
        "AI Trading - Morning Trade Generation",
        "AI Trading - Trade Execution",
        "AI Trading - Daily Performance Graph",
    ]

    issues_found = []

    for task_name in tasks:
        print("\n" + "=" * 80)
        print(f"TASK: {task_name}")
        print("=" * 80)

        config = check_task_details(task_name)

        if config:
            for key, value in config.items():
                print(f"{key:.<30} {value}")

            # Check for issues
            if config.get('Last Run') == 'N/A' or '11/30/1999' in config.get('Last Run', ''):
                issues_found.append(f"{task_name}: NEVER RUN")
                print("\n[!] WARNING: This task has NEVER run successfully!")

            if config.get('Status') != 'Ready':
                issues_found.append(f"{task_name}: Status is {config.get('Status')}")
                print(f"\n[!] WARNING: Status is {config.get('Status')}, should be Ready")

            if 'Interactive' in config.get('Logon Mode', ''):
                issues_found.append(f"{task_name}: Only runs when user logged in")
                print("\n[!] WARNING: Task only runs when user is logged in!")
                print("   Fix: Right-click task -> Properties -> General tab")
                print("   Check: 'Run whether user is logged on or not'")

            if config.get('Wake Computer') == 'No':
                issues_found.append(f"{task_name}: Won't wake computer")
                print("\n[!] WARNING: Task won't wake computer from sleep!")
                print("   Fix: Right-click task -> Properties -> Conditions tab")
                print("   Check: 'Wake the computer to run this task'")
        else:
            print("[ERROR] TASK NOT FOUND")
            issues_found.append(f"{task_name}: NOT CONFIGURED")

    # Check file existence
    check_file_existence()

    # Check power settings
    check_power_settings()

    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)

    if issues_found:
        print(f"\n[CRITICAL] FOUND {len(issues_found)} ISSUES:\n")
        for i, issue in enumerate(issues_found, 1):
            print(f"{i}. {issue}")

        print("\n" + "=" * 80)
        print("RECOMMENDED ACTIONS")
        print("=" * 80)
        print("""
1. Open Task Scheduler (Win+R -> taskschd.msc)

2. For EACH "AI Trading" task:
   a. Right-click -> Properties
   b. General tab:
      [X] Run whether user is logged on or not
      [X] Run with highest privileges
   c. Conditions tab:
      [X] Wake the computer to run this task
      [ ] Start the task only if computer is on AC power (UNCHECK)
   d. Settings tab:
      [X] Allow task to be run on demand
      [ ] Stop the task if it runs longer than (UNCHECK or set to 2 hours)
   e. Click OK

3. Configure Windows to not sleep:
   Settings -> System -> Power & Sleep -> Sleep: Never

4. Test weekend research manually:
   python scripts/automation/daily_claude_research.py --force

5. Run diagnostics again:
   python diagnose_automation.py
""")
    else:
        print("\n[OK] NO CRITICAL ISSUES FOUND")
        print("\nTasks appear to be configured correctly.")
        print("If automation still isn't working, check:")
        print("  1. Computer is on during scheduled times")
        print("  2. No error logs in Task Scheduler History")
        print("  3. Scripts can run manually without errors")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
