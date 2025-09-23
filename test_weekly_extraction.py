"""
Test the weekly ChatGPT extraction process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

print("Testing Weekly ChatGPT Extraction Process")
print("=" * 50)

# Test 1: Generate weekly prompts
print("\n1. Generating weekly prompts...")
try:
    exec(open('scripts-and-data/automation/generate_weekly_prompt.py').read())
    print("✓ Weekly prompts generated successfully")
except Exception as e:
    print(f"✗ Error generating prompts: {e}")

# Test 2: Check if prompts were saved
print("\n2. Checking saved prompts...")
prompt_dir = "weekly-reports/prompts"
if os.path.exists(prompt_dir):
    prompts = os.listdir(prompt_dir)
    recent_prompts = [p for p in prompts if datetime.now().strftime("%Y%m%d") in p]
    if recent_prompts:
        print(f"✓ Found {len(recent_prompts)} prompts from today:")
        for p in recent_prompts:
            print(f"  - {p}")
    else:
        print("✗ No prompts found from today")
else:
    print("✗ Prompt directory not found")

# Test 3: Test extraction tools
print("\n3. Testing extraction tools...")

# Check if ChatGPT server is running
import requests
try:
    response = requests.get("http://localhost:8888/status")
    if response.status_code == 200:
        print("✓ ChatGPT server is running on port 8888")
    else:
        print("✗ ChatGPT server not responding properly")
except:
    print("✗ ChatGPT server is not running")

# Test 4: Test manual extractor
print("\n4. Testing manual extractor availability...")
extractor_path = "scripts-and-data/automation/manual_chatgpt_extractor.py"
if os.path.exists(extractor_path):
    print("✓ Manual extractor available at:", extractor_path)
else:
    print("✗ Manual extractor not found")

# Test 5: Test interactive extractor
print("\n5. Testing interactive extractor availability...")
interactive_path = "scripts-and-data/automation/chatgpt_extractor_interactive.py"
if os.path.exists(interactive_path):
    print("✓ Interactive extractor available at:", interactive_path)
else:
    print("✗ Interactive extractor not found")

print("\n" + "=" * 50)
print("EXTRACTION WORKFLOW:")
print("1. Copy weekly prompt from weekly-reports/prompts/")
print("2. Paste into ChatGPT for deep research")
print("3. Use one of these methods to extract:")
print("   a) Browser extension (if working)")
print("   b) python scripts-and-data/automation/manual_chatgpt_extractor.py")
print("   c) python scripts-and-data/automation/chatgpt_extractor_interactive.py")
print("4. Review extracted trades in weekly-reports/trade_plans/")