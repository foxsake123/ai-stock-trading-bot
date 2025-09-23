"""
Simple test of enhanced data providers
"""

import asyncio
import json
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from data.enhanced_providers import EnhancedDataHub

async def test_enhanced_data():
    """Test the enhanced data providers"""
    print("="*60)
    print("ENHANCED DATA PROVIDER TEST")
    print("="*60)
    
    # Initialize data hub
    hub = EnhancedDataHub()
    
    # Test tickers
    test_tickers = ["NVDA", "TSLA", "AMD"]
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Testing {ticker}")
        print(f"{'='*60}")
        
        # 1. Market Data
        print("\n📊 Market Data:")
        print("-" * 40)
        try:
            market_data = await hub.get_market_data(ticker)
            if market_data.get('price', 0) > 0:
                print(f"  Price: ${market_data['price']:.2f}")
                print(f"  Volume: {market_data.get('volume', 'N/A'):,}")
                print(f"  P/E Ratio: {market_data.get('pe_ratio', 'N/A')}")
                print(f"  Source: {market_data.get('source', 'Unknown')}")
            else:
                print(f"  ⚠ No market data available")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
        
        # 2. News
        print("\n📰 Latest News:")
        print("-" * 40)
        try:
            news = await hub.get_news(ticker, limit=3)
            if news:
                for i, article in enumerate(news, 1):
                    title = article.get('title', 'No title')[:80]
                    source = article.get('source', 'Unknown')
                    print(f"  {i}. {title}...")
                    print(f"     Source: {source}")
            else:
                print(f"  ⚠ No news available")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
        
        # 3. Social Sentiment
        print("\n💬 Social Sentiment:")
        print("-" * 40)
        try:
            sentiment = await hub.get_social_sentiment(ticker)
            print(f"  Overall Score: {sentiment['overall_score']:.2f} (0=bearish, 1=bullish)")
            if 'reddit_score' in sentiment:
                print(f"  Reddit Score: {sentiment['reddit_score']:.2f}")
                print(f"  Reddit Mentions: {sentiment.get('reddit_mentions', 0)}")
            if 'twitter_score' in sentiment:
                print(f"  Twitter Score: {sentiment['twitter_score']:.2f}")
            print(f"  Data Sources: {', '.join(sentiment.get('sources', [])) or 'None'}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
        
        # Add small delay between tickers
        await asyncio.sleep(1)
    
    # 4. Economic Indicators
    print(f"\n{'='*60}")
    print("📈 Economic Indicators")
    print("="*60)
    try:
        economic = await hub.get_economic_indicators()
        for indicator, value in economic.items():
            if indicator != 'source':
                print(f"  {indicator.upper()}: {value}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print("="*60)
    
    # Summary of data sources
    print("\n📋 Data Source Summary:")
    print("-" * 40)
    
    from config.api_config import APIConfig
    configured, missing = APIConfig.get_required_apis()
    
    if configured:
        print(f"✅ Configured APIs: {', '.join(configured)}")
    if missing:
        print(f"⚠️  Missing APIs: {', '.join(missing)}")
        print("\n💡 To improve data quality:")
        for api in missing[:3]:  # Show top 3 missing
            if api == 'Polygon':
                print("   • Polygon.io: Real-time market data")
                print("     Sign up at: https://polygon.io/")
            elif api == 'NewsAPI':
                print("   • NewsAPI: Comprehensive news coverage")
                print("     Sign up at: https://newsapi.org/")
            elif api == 'FRED':
                print("   • FRED: Federal Reserve economic data")
                print("     Sign up at: https://fred.stlouisfed.org/docs/api/")

if __name__ == "__main__":
    asyncio.run(test_enhanced_data())