"""
Update import statements for repository reorganization
Converts old imports to new src/ structure
"""

import os
import re
from pathlib import Path

def update_imports_in_file(filepath):
    """Update imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Update agent imports
        content = re.sub(r'from agents\.', 'from src.agents.', content)
        content = re.sub(r'import agents\.', 'import src.agents.', content)

        # Update data imports
        content = re.sub(r'from data\.', 'from src.data.', content)
        content = re.sub(r'import data\.', 'import src.data.', content)

        # Update risk imports
        content = re.sub(r'from risk\.', 'from src.risk.', content)
        content = re.sub(r'import risk\.', 'import src.risk.', content)

        # Update communication imports
        content = re.sub(r'from communication\.', 'from src.agents.communication.', content)

        # Update src.src. double prefix (if it happens)
        content = re.sub(r'from src\.src\.', 'from src.', content)
        content = re.sub(r'import src\.src\.', 'import src.', content)

        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def update_all_imports():
    """Update imports in all Python files"""
    updated_count = 0
    checked_count = 0

    # Directories to process
    dirs_to_process = [
        'scripts',
        'src',
        'tests',
        'backtesting'
    ]

    for dir_name in dirs_to_process:
        if not os.path.exists(dir_name):
            continue

        for root, dirs, files in os.walk(dir_name):
            # Skip __pycache__ and .git
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv']]

            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    checked_count += 1

                    if update_imports_in_file(filepath):
                        updated_count += 1
                        print(f"Updated: {filepath}")

    print(f"\nSummary:")
    print(f"Files checked: {checked_count}")
    print(f"Files updated: {updated_count}")

if __name__ == "__main__":
    print("Updating imports for repository reorganization...")
    update_all_imports()
    print("Import update complete!")
