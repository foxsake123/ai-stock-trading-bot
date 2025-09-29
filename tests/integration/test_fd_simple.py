#!/usr/bin/env python3
"""
Simple test for Financial Datasets API
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
api_key = os.getenv('FINANCIAL_DATASETS_API_KEY')
print("=" * 60)
print("FINANCIAL DATASETS API - SIMPLE TEST")
print("=" * 60)
print()
print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")
else:
    print("ERROR: No API key found in .env file")
    exit(1)

# Test a simple request
url = "https://api.financialdatasets.ai/prices"
headers = {
    'X-API-KEY': api_key
}

# Set date range
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

params = {
    'ticker': 'AAPL',
    'interval': 'day',
    'interval_multiplier': 1,
    'start_date': start_date,
    'end_date': end_date,
    'limit': 5
}

print()
print("Making request to:", url)
print("Parameters:")
for key, value in params.items():
    print(f"  {key}: {value}")

print()
print("Sending request...")
try:
    response = requests.get(url, headers=headers, params=params)
    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response type: {type(data)}")
        print(f"Response content: {data}")

        if isinstance(data, list):
            print(f"Success! Received {len(data)} records")
            if len(data) > 0:
                print("\nFirst record:")
                first = data[0]
                for key, value in first.items():
                    print(f"  {key}: {value}")
        elif isinstance(data, dict):
            print("Response is a dictionary:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"Unexpected response type: {type(data)}")
    else:
        print(f"Error Response:")
        print(f"  Headers: {response.headers}")
        print(f"  Body: {response.text[:500] if response.text else 'No body'}")

except Exception as e:
    print(f"Exception occurred: {e}")

print()
print("=" * 60)