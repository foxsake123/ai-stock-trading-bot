#!/usr/bin/env python3
"""
Simple test for Financial Datasets API
"""

import asyncio
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

async def test_api_key():
    """Test the Financial Datasets API key"""
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    print(f"API Key: {api_key[:8]}...{api_key[-4:] if api_key else 'Not found'}")
    
    if not api_key:
        print("ERROR: No API key found in environment")
        return
    
    # Try different possible API endpoints
    endpoints = [
        "https://api.financialdatasets.ai",
        "https://financialdatasets.ai/api",
        "https://mcp.financialdatasets.ai",
    ]
    
    headers_options = [
        {"Authorization": f"Bearer {api_key}"},
        {"X-API-KEY": api_key},
        {"api-key": api_key},
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for base_url in endpoints:
            print(f"\nTrying endpoint: {base_url}")
            
            for headers in headers_options:
                try:
                    # Try to get a simple quote
                    response = await client.get(
                        f"{base_url}/stocks/AAPL/quote",
                        headers=headers
                    )
                    
                    print(f"  Headers: {list(headers.keys())[0]}")
                    print(f"  Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"  SUCCESS! Found working configuration")
                        print(f"  Response: {response.json()}")
                        return
                    elif response.status_code == 401:
                        print(f"  Authentication failed")
                    elif response.status_code == 404:
                        print(f"  Endpoint not found")
                    else:
                        print(f"  Unexpected status: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"  Error: {str(e)[:100]}")
    
    print("\nCould not find working API configuration")
    print("Please check the API documentation at https://financialdatasets.ai")

if __name__ == "__main__":
    print("Testing Financial Datasets API Connection")
    print("=" * 50)
    asyncio.run(test_api_key())