"""
Test script to verify data source API connections
"""

import asyncio
import json
from datetime import datetime
import sys
import os
import time

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.enhanced_providers import EnhancedDataHub as DataProviderHub

async def test_data_sources():
    """Test all configured data sources"""
    print("=" * 60)
    print("Testing Data Source Connections")
    print("=" * 60)
    
    # Initialize data provider hub
    hub = DataProviderHub()
    
    # Test stock to use
    test_ticker = "AAPL"
    
    # 1. Test Market Data
    print("\n1. Testing Market Data Provider...")
    print("-" * 40)
    try:
        market_data = await hub.get_market_data(test_ticker)
        if market_data:
            print(f"✅ Market Data Success for {test_ticker}:")
            print(f"   Current Price: ${market_data.get('price', 'N/A')}")
            print(f"   Volume: {market_data.get('volume', 'N/A'):,}")
            print(f"   Data Source: {market_data.get('source', 'Unknown')}")
        else:
            print("❌ Market Data Failed - No data returned")
    except Exception as e:
        print(f"❌ Market Data Error: {str(e)}")
    
    # 2. Test News Data
    print("\n2. Testing News Data Provider...")
    print("-" * 40)
    try:
        news_data = await hub.get_news(test_ticker, limit=3)
        if news_data:
            print(f"✅ News Data Success - Found {len(news_data)} articles:")
            for i, article in enumerate(news_data[:3], 1):
                print(f"   {i}. {article.get('title', 'No title')[:60]}...")
                print(f"      Source: {article.get('source', 'Unknown')}")
        else:
            print("⚠️ News Data - No articles found")
    except Exception as e:
        print(f"❌ News Data Error: {str(e)}")
    
    # 3. Test Social Sentiment
    print("\n3. Testing Social Sentiment Provider...")
    print("-" * 40)
    try:
        sentiment = await hub.get_social_sentiment(test_ticker)
        if sentiment:
            print(f"✅ Social Sentiment Success:")
            print(f"   Overall Score: {sentiment.get('overall_score', 'N/A')}")
            print(f"   Twitter Score: {sentiment.get('twitter_score', 'N/A')}")
            print(f"   Reddit Score: {sentiment.get('reddit_score', 'N/A')}")
            print(f"   Data Sources: {sentiment.get('sources', [])}")
        else:
            print("⚠️ Social Sentiment - No data available")
    except Exception as e:
        print(f"❌ Social Sentiment Error: {str(e)}")
    
    # 4. Test Options Data
    print("\n4. Testing Options Flow Provider...")
    print("-" * 40)
    try:
        options_data = await hub.get_options_flow(test_ticker)
        if options_data:
            print(f"✅ Options Flow Success:")
            print(f"   Put/Call Ratio: {options_data.get('put_call_ratio', 'N/A')}")
            print(f"   Unusual Activity: {options_data.get('unusual_activity', [])}")
        else:
            print("⚠️ Options Flow - No data available")
    except Exception as e:
        print(f"❌ Options Flow Error: {str(e)}")
    
    # 5. Test Economic Data
    print("\n5. Testing Economic Indicators...")
    print("-" * 40)
    try:
        economic_data = await hub.get_economic_indicators()
        if economic_data:
            print(f"✅ Economic Data Success:")
            for indicator, value in list(economic_data.items())[:3]:
                print(f"   {indicator}: {value}")
        else:
            print("⚠️ Economic Data - No indicators available")
    except Exception as e:
        print(f"❌ Economic Data Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("API Configuration Summary:")
    print("=" * 60)
    
    from config.api_config import APIConfig
    configured, missing = APIConfig.get_required_apis()
    
    print(f"\n✅ Configured APIs: {', '.join(configured) if configured else 'None'}")
    if missing:
        print(f"⚠️ Missing APIs: {', '.join(missing)}")
        print("\nTo add missing APIs:")
        print("1. Sign up for free API keys at:")
        print("   - Polygon.io: https://polygon.io/")
        print("   - NewsAPI: https://newsapi.org/")
        print("   - Reddit: https://www.reddit.com/prefs/apps")
        print("   - FRED: https://fred.stlouisfed.org/docs/api/")
        print("2. Add them to your .env file")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_data_sources())