#!/usr/bin/env python3
"""
Test Financial Datasets API with real endpoints
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dee_bot.data.financial_datasets_api import FinancialDatasetsAPI

async def test_api():
    """Test Financial Datasets API endpoints"""
    
    print("Testing Financial Datasets API")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if api_key:
        print(f"[OK] API Key found: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("[ERROR] No API key found")
        return
    
    # Initialize API client
    async with FinancialDatasetsAPI() as api:
        
        # Test 1: Get price snapshot
        print("\n1. Testing Price Snapshot for AAPL...")
        snapshot = await api.get_price_snapshot("AAPL")
        if snapshot:
            print(f"  [OK] Current price: ${snapshot.price:.2f}")
            print(f"       Change: {snapshot.change_percent:.2f}%")
            print(f"       Volume: {snapshot.volume:,}")
        else:
            print("  [ERROR] Failed to get price snapshot")
        
        # Test 2: Get historical prices
        print("\n2. Testing Historical Prices for MSFT...")
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        prices = await api.get_historical_prices(
            "MSFT", 
            start_date=start_date,
            end_date=end_date
        )
        
        if prices:
            print(f"  [OK] Retrieved {len(prices)} price records")
            if prices:
                latest = prices[-1]
                print(f"       Latest: {latest.date.strftime('%Y-%m-%d')} - Close: ${latest.close:.2f}")
        else:
            print("  [ERROR] Failed to get historical prices")
        
        # Test 3: Get financial statements
        print("\n3. Testing Financial Statements for GOOGL...")
        financials = await api.get_financials("GOOGL", period="quarterly")
        
        if financials:
            print(f"  [OK] Retrieved {len(financials)} financial statements")
            if financials:
                latest = financials[0]
                print(f"       Latest quarter: {latest.end_date}")
                if latest.revenue:
                    print(f"       Revenue: ${latest.revenue:,.0f}")
                if latest.net_income:
                    print(f"       Net Income: ${latest.net_income:,.0f}")
        else:
            print("  [ERROR] Failed to get financial statements")
        
        # Test 4: Get insider trades
        print("\n4. Testing Insider Trades for TSLA...")
        trades = await api.get_insider_trades("TSLA", limit=10)
        
        if trades:
            print(f"  [OK] Retrieved {len(trades)} insider trades")
            if trades:
                latest = trades[0]
                print(f"       Latest: {latest.insider_name} - {latest.transaction_type}")
                print(f"       Shares: {latest.shares:,}")
        else:
            print("  [ERROR] Failed to get insider trades")
        
        # Test 5: Get company info
        print("\n5. Testing Company Info for NVDA...")
        company = await api.get_company_info("NVDA")
        
        if company:
            print(f"  [OK] Company: {company.name}")
            print(f"       Sector: {company.sector}")
            print(f"       Industry: {company.industry}")
            if company.market_cap:
                print(f"       Market Cap: ${company.market_cap:,.0f}")
        else:
            print("  [ERROR] Failed to get company info")
        
        # Test 6: Analyze insider sentiment
        print("\n6. Testing Insider Sentiment Analysis for META...")
        sentiment = await api.analyze_insider_sentiment("META")
        
        if sentiment:
            print(f"  [OK] Sentiment: {sentiment['sentiment']}")
            print(f"       Signal: {sentiment['signal']:.2f}")
            print(f"       Buys: {sentiment['buy_count']}, Sells: {sentiment['sell_count']}")
        else:
            print("  [ERROR] Failed to analyze insider sentiment")
        
        # Test 7: Get fundamental metrics
        print("\n7. Testing Fundamental Metrics for AMZN...")
        metrics = await api.get_fundamental_metrics("AMZN")
        
        if metrics:
            print(f"  [OK] Retrieved fundamental metrics")
            if "roe" in metrics:
                print(f"       ROE: {metrics['roe']:.2%}")
            if "profit_margin" in metrics:
                print(f"       Profit Margin: {metrics['profit_margin']:.2%}")
            if "debt_to_equity" in metrics:
                print(f"       Debt/Equity: {metrics['debt_to_equity']:.2f}")
        else:
            print("  [ERROR] Failed to get fundamental metrics")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_api())