#!/usr/bin/env python3
"""
Test different Financial Datasets API endpoints
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')
headers = {'X-API-KEY': api_key}

print("=" * 60)
print("FINANCIAL DATASETS API - ENDPOINT TESTING")
print("=" * 60)

# Test different endpoints
endpoints_to_test = [
    {
        'name': 'Financials',
        'url': 'https://api.financialdatasets.ai/financials',
        'params': {'ticker': 'AAPL'}
    },
    {
        'name': 'Earnings',
        'url': 'https://api.financialdatasets.ai/earnings',
        'params': {'ticker': 'AAPL'}
    },
    {
        'name': 'News',
        'url': 'https://api.financialdatasets.ai/news',
        'params': {'ticker': 'AAPL', 'limit': 5}
    },
    {
        'name': 'Estimates',
        'url': 'https://api.financialdatasets.ai/estimates',
        'params': {'ticker': 'AAPL'}
    },
    {
        'name': 'Insider Trades',
        'url': 'https://api.financialdatasets.ai/insider-trades',
        'params': {'ticker': 'AAPL', 'limit': 5}
    },
    {
        'name': 'Institutional Ownership',
        'url': 'https://api.financialdatasets.ai/institutional-ownership',
        'params': {'ticker': 'AAPL'}
    }
]

for endpoint in endpoints_to_test:
    print(f"\n{endpoint['name']} Endpoint:")
    print("-" * 40)
    print(f"URL: {endpoint['url']}")
    print(f"Params: {endpoint['params']}")

    try:
        response = requests.get(endpoint['url'], headers=headers, params=endpoint['params'])
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")

            # Show structure
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                # Show first few items of each key
                for key in list(data.keys())[:3]:
                    value = data[key]
                    if isinstance(value, list) and len(value) > 0:
                        print(f"  {key}: List with {len(value)} items")
                        print(f"    First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
                    elif isinstance(value, dict):
                        print(f"  {key}: Dict with keys {list(value.keys())[:5]}")
                    else:
                        print(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
            elif isinstance(data, list):
                print(f"List length: {len(data)}")
                if len(data) > 0:
                    print(f"First item type: {type(data[0])}")
                    if isinstance(data[0], dict):
                        print(f"First item keys: {list(data[0].keys())}")
        else:
            print(f"Error body: {response.text[:200]}")

    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "=" * 60)