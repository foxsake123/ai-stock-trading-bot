"""Check if tasks are configured to run daily on weekdays"""
import subprocess

tasks = [
    "AI Trading - Morning Trade Generation",
    "AI Trading - Trade Execution",
    "AI Trading - Daily Performance Graph",
]

for task in tasks:
    print(f"\n{'='*70}")
    print(f"Task: {task}")
    print('='*70)

    result = subprocess.run(
        ['schtasks', '/query', '/tn', task, '/fo', 'LIST', '/v'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        lines = result.stdout.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['Schedule Type', 'Days:', 'Repeat:', 'Start Time']):
                print(line.strip())
    else:
        print("[ERROR] Task not found")
