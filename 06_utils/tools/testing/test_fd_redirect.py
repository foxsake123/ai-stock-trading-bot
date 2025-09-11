#!/usr/bin/env python3
"""
Test to find correct Financial Datasets API URL
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_redirect():
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    print(f"Testing with API key: {api_key[:8]}...{api_key[-4:]}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Test the base API
        response = await client.get(
            "https://api.financialdatasets.ai/prices/snapshot",
            params={"ticker": "AAPL"},
            headers={"X-API-KEY": api_key}
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"URL after redirects: {response.url}")
        
        if response.status_code == 200:
            print(f"Response: {response.text[:500]}")
        else:
            print(f"Response: {response.text[:200]}")

asyncio.run(test_redirect())