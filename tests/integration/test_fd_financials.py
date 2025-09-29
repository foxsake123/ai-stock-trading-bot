#!/usr/bin/env python3
"""
Test Financial Datasets financials endpoint specifically
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')
headers = {'X-API-KEY': api_key}

print("=" * 60)
print("TESTING FINANCIALS ENDPOINT")
print("=" * 60)

# Test different period parameters
periods = ['quarterly', 'annual', 'ttm']

for period in periods:
    print(f"\nTesting period: {period}")
    print("-" * 40)

    url = "https://api.financialdatasets.ai/financials"
    params = {
        'ticker': 'AAPL',
        'period': period
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")

            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                if 'financials' in data:
                    financials = data['financials']
                    print(f"  financials type: {type(financials)}")
                    if isinstance(financials, dict):
                        print(f"  financials keys: {list(financials.keys())}")
                        # Show first key's value
                        for key in list(financials.keys())[:1]:
                            print(f"  {key}: {financials[key]}")
                    elif isinstance(financials, list):
                        print(f"  financials: List with {len(financials)} items")
                        if len(financials) > 0:
                            print(f"  First item type: {type(financials[0])}")
                        if isinstance(financials[0], dict):
                            print(f"  First financial keys: {list(financials[0].keys())[:10]}")
                        # Show sample values
                        first = financials[0]
                        print(f"    report_period: {first.get('report_period')}")
                        print(f"    revenue: {first.get('revenue')}")
                        print(f"    net_income: {first.get('net_income')}")
                        print(f"    earnings_per_share: {first.get('earnings_per_share')}")
            elif isinstance(data, list):
                print(f"Direct list with {len(data)} items")
                if len(data) > 0:
                    print(f"First item keys: {list(data[0].keys())[:10]}")
        else:
            print(f"Error: {response.text[:200]}")

    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "=" * 60)