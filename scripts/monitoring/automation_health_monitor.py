#!/usr/bin/env python3
"""
Automation Health Monitor
Monitors all scheduled automation tasks and sends Telegram alerts on failure

Usage:
  python automation_health_monitor.py --task research
  python automation_health_monitor.py --task trade-generation
  python automation_health_monitor.py --task trade-execution
  python automation_health_monitor.py --task performance

This script should be called by each automation task to report success/failure
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load environment
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
STATUS_FILE = Path('data/automation_status.json')

# Task definitions
TASKS = {
    'research': {
        'name': 'Weekend Research Generation',
        'schedule': 'Saturday 12:00 PM',
        'critical': True
    },
    'trade-generation': {
        'name': 'Morning Trade Generation',
        'schedule': 'Weekdays 8:30 AM',
        'critical': True
    },
    'trade-execution': {
        'name': 'Trade Execution',
        'schedule': 'Weekdays 9:30 AM',
        'critical': True
    },
    'performance': {
        'name': 'Performance Graph Update',
        'schedule': 'Weekdays 4:30 PM',
        'critical': False
    }
}

def send_telegram_alert(message, priority='HIGH'):
    """Send alert to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print('[WARNING] Telegram credentials not configured')
        return False

    # Add priority indicator
    if priority == 'CRITICAL':
        prefix = '🚨 CRITICAL ALERT'
    elif priority == 'HIGH':
        prefix = '⚠️ ALERT'
    else:
        prefix = '✅ INFO'

    full_message = f"{prefix}\n\n{message}"

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': full_message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f'[OK] Telegram alert sent: {priority}')
            return True
        else:
            print(f'[FAIL] Telegram alert failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'[ERROR] Failed to send Telegram alert: {e}')
        return False

def load_status():
    """Load automation status from file"""
    if not STATUS_FILE.exists():
        return {}

    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f'[WARNING] Could not load status file: {e}')
        return {}

def save_status(status):
    """Save automation status to file"""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(status, f, indent=2)
        return True
    except Exception as e:
        print(f'[ERROR] Could not save status file: {e}')
        return False

def report_success(task_name, details=None):
    """Report successful task completion"""
    if task_name not in TASKS:
        print(f'[ERROR] Unknown task: {task_name}')
        return False

    task_info = TASKS[task_name]
    status = load_status()

    # Update status
    status[task_name] = {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'details': details or {},
        'consecutive_failures': 0
    }

    save_status(status)

    print(f'[OK] {task_info["name"]}: Success')

    # Send success notification for critical tasks
    if task_info['critical']:
        message = f"""*{task_info["name"]}*
Status: ✅ *SUCCESS*
Time: {datetime.now().strftime('%I:%M %p %Z')}
Schedule: {task_info["schedule"]}"""

        if details:
            message += "\n\n*Details:*\n"
            for key, value in details.items():
                message += f"• {key}: {value}\n"

        send_telegram_alert(message, priority='INFO')

    return True

def report_failure(task_name, error_message, details=None):
    """Report task failure"""
    if task_name not in TASKS:
        print(f'[ERROR] Unknown task: {task_name}')
        return False

    task_info = TASKS[task_name]
    status = load_status()

    # Get previous status
    prev_status = status.get(task_name, {})
    consecutive_failures = prev_status.get('consecutive_failures', 0) + 1

    # Update status
    status[task_name] = {
        'status': 'failure',
        'timestamp': datetime.now().isoformat(),
        'error': error_message,
        'details': details or {},
        'consecutive_failures': consecutive_failures
    }

    save_status(status)

    print(f'[FAIL] {task_info["name"]}: {error_message}')

    # Determine priority based on consecutive failures and criticality
    if task_info['critical'] and consecutive_failures >= 2:
        priority = 'CRITICAL'
    elif task_info['critical']:
        priority = 'HIGH'
    else:
        priority = 'HIGH'

    # Send failure alert
    message = f"""*{task_info["name"]} FAILED*

*Error:* {error_message}

*Schedule:* {task_info["schedule"]}
*Time:* {datetime.now().strftime('%I:%M %p %Z')}
*Consecutive Failures:* {consecutive_failures}"""

    if details:
        message += "\n\n*Details:*\n"
        for key, value in details.items():
            message += f"• {key}: {value}\n"

    message += f"\n\n*Action Required:* Check automation logs and fix issue"

    if consecutive_failures >= 2:
        message += f"\n\n⚠️ *{consecutive_failures} consecutive failures* - Immediate attention needed!"

    send_telegram_alert(message, priority=priority)

    return True

def check_task_health(task_name):
    """Check if a task has run recently"""
    if task_name not in TASKS:
        print(f'[ERROR] Unknown task: {task_name}')
        return None

    status = load_status()
    task_status = status.get(task_name)

    if not task_status:
        return {
            'status': 'never_run',
            'message': 'Task has never been reported'
        }

    # Check how long ago it ran
    last_run = datetime.fromisoformat(task_status['timestamp'])
    age = datetime.now() - last_run

    return {
        'status': task_status['status'],
        'last_run': last_run.strftime('%Y-%m-%d %I:%M %p'),
        'age_hours': age.total_seconds() / 3600,
        'consecutive_failures': task_status.get('consecutive_failures', 0),
        'details': task_status.get('details', {})
    }

def get_overall_health():
    """Get overall automation health status"""
    status = load_status()

    if not status:
        return {
            'health': 'unknown',
            'message': 'No automation status available'
        }

    # Check each task
    issues = []
    warnings = []

    for task_name, task_info in TASKS.items():
        task_status = status.get(task_name, {})

        if not task_status:
            if task_info['critical']:
                issues.append(f'{task_info["name"]}: Never run')
            continue

        # Check status
        if task_status['status'] == 'failure':
            failures = task_status.get('consecutive_failures', 1)
            if task_info['critical']:
                issues.append(f'{task_info["name"]}: Failed ({failures}x)')
            else:
                warnings.append(f'{task_info["name"]}: Failed ({failures}x)')

        # Check age
        last_run = datetime.fromisoformat(task_status['timestamp'])
        age = datetime.now() - last_run

        # Research should run weekly
        if task_name == 'research' and age > timedelta(days=8):
            warnings.append(f'{task_info["name"]}: Last run {age.days} days ago')

        # Daily tasks should run within 26 hours
        elif task_name in ['trade-generation', 'trade-execution', 'performance']:
            if age > timedelta(hours=26):
                if task_info['critical']:
                    issues.append(f'{task_info["name"]}: Last run {age.days} days ago')
                else:
                    warnings.append(f'{task_info["name"]}: Last run {age.days} days ago')

    # Determine overall health
    if issues:
        health = 'critical'
        message = f'{len(issues)} critical issue(s), {len(warnings)} warning(s)'
    elif warnings:
        health = 'warning'
        message = f'{len(warnings)} warning(s)'
    else:
        health = 'good'
        message = 'All systems operational'

    return {
        'health': health,
        'message': message,
        'issues': issues,
        'warnings': warnings,
        'tasks': {name: check_task_health(name) for name in TASKS.keys()}
    }

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Automation Health Monitor')
    parser.add_argument('--task', choices=list(TASKS.keys()), help='Task name')
    parser.add_argument('--status', choices=['success', 'failure'], help='Task status')
    parser.add_argument('--error', help='Error message (for failures)')
    parser.add_argument('--details', help='Additional details (JSON string)')
    parser.add_argument('--check', action='store_true', help='Check overall health')

    args = parser.parse_args()

    if args.check:
        # Check overall health
        health = get_overall_health()
        print(f"\nOverall Health: {health['health'].upper()}")
        print(f"Message: {health['message']}")

        if health.get('issues'):
            print("\nCritical Issues:")
            for issue in health['issues']:
                print(f"  - {issue}")

        if health.get('warnings'):
            print("\nWarnings:")
            for warning in health['warnings']:
                print(f"  - {warning}")

        if 'tasks' in health:
            print("\nTask Status:")
            for task_name, task_status in health['tasks'].items():
                print(f"  {TASKS[task_name]['name']}: {task_status['status']}")
                if task_status['status'] != 'never_run':
                    print(f"    Last run: {task_status['last_run']}")

        return 0

    if not args.task or not args.status:
        parser.print_help()
        return 1

    # Parse details if provided
    details = None
    if args.details:
        try:
            details = json.loads(args.details)
        except:
            print('[WARNING] Could not parse details JSON')

    # Report status
    if args.status == 'success':
        report_success(args.task, details)
    else:
        if not args.error:
            print('[ERROR] --error required for failure status')
            return 1
        report_failure(args.task, args.error, details)

    return 0

if __name__ == '__main__':
    sys.exit(main())
