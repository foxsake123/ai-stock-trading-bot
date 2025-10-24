"""
Test Financial Datasets API Integration
Quick test to verify the fundamental analyst works with the new API
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.fundamental_analyst import FundamentalAnalystAgent
from datetime import datetime

print('='*70)
print('Testing FundamentalAnalystAgent with Financial Datasets API')
print('='*70)

# Create analyst
analyst = FundamentalAnalystAgent()

# Test with AAPL
ticker = 'AAPL'
print(f'\nTesting ticker: {ticker}')
print('-'*70)

# Minimal market data (just price info)
market_data = {
    'current_price': 175.50,
    'volume': 50000000,
    'day_high': 176.00,
    'day_low': 174.50,
    'open': 175.00
}

try:
    result = analyst.analyze(ticker, market_data)

    print(f'\n[OK] Analysis completed successfully!')
    print(f'\nRecommendation: {result.get("action", "N/A")}')
    print(f'Confidence: {result.get("confidence", 0):.3f}')
    print(f'\nReasoning:')
    print(result.get("reasoning", "N/A")[:300])

    print(f'\nKey Factors:')
    key_factors = result.get("key_factors", [])
    for i, factor in enumerate(key_factors[:5], 1):
        print(f'  {i}. {factor}')

    # Check if using real data or fallback
    reasoning = result.get("reasoning", "")
    if "P/E: 20.0" in reasoning or "beta: 1.0" in reasoning:
        print('\n[WARNING] Using fallback/generic data')
        print('   Check if Financial Datasets API is configured correctly')
    else:
        print('\n[OK] Using real fundamental data from Financial Datasets API')

    # Check confidence
    confidence = result.get("confidence", 0)
    if confidence > 0.50:
        print(f'\n[OK] Good confidence ({confidence:.1%}) - agent can validate trades')
    elif confidence > 0.30:
        print(f'\n[WARNING] Moderate confidence ({confidence:.1%}) - some trades may be rejected')
    else:
        print(f'\n[ERROR] Low confidence ({confidence:.1%}) - most trades will be rejected')

except Exception as e:
    print(f'\n[ERROR] Error during analysis: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*70)
print('Test Complete')
print('='*70)
