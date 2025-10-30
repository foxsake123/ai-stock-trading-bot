import re
from pathlib import Path

report_path = Path('reports/premarket/2025-10-30/claude_research_dee_bot_2025-10-30.md')
with open(report_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Test the ORDER BLOCK pattern
pattern = r'##\s*(?:\d+\.\s*)?(?:EXACT\s+|Exact\s+)?ORDER\s+BLOCK(.*?)(?=\n##\s+[A-Z]|$)'
match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

if match:
    print('ORDER BLOCK section found')
    order_block = match.group(1)
    print(f'Length: {len(order_block)} characters')
    print(f'First 300 chars: {order_block[:300]}')

    # Test trade block pattern
    trade_pattern = r'```\s*(.*?)\s*```'
    trades = re.findall(trade_pattern, order_block, re.DOTALL)
    print(f'\nFound {len(trades)} trade blocks')
    if trades:
        print(f'\nFirst trade block:\n{trades[0][:200]}')
else:
    print('ORDER BLOCK section NOT found')

    # Try to find what sections exist
    sections = re.findall(r'^## (.+)$', content, re.MULTILINE)
    print(f'Available sections ({len(sections)}):')
    for i, sec in enumerate(sections[:15]):
        print(f'  {i+1}. {sec}')
