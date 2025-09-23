#!/usr/bin/env python3
"""
Test script for Financial Datasets MCP integration
"""

import asyncio
import os
import sys
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dee_bot.data.market_data import market_data
from dee_bot.agents.fundamental_analyst import FundamentalAnalyst
from dee_bot.config.settings import settings

async def test_mcp_connection():
    """Test MCP connection and basic data retrieval"""
    print("\n" + "="*50)
    print("Testing Financial Datasets MCP Integration")
    print("="*50)
    
    # Connect to market data sources (including MCP)
    print("\n1. Connecting to data sources...")
    await market_data.connect_all()
    
    if market_data.mcp_connected:
        print("[OK] Successfully connected to Financial Datasets MCP")
    else:
        print("[ERROR] Could not connect to MCP (check API key)")
        print("  Set FINANCIAL_DATASETS_API_KEY environment variable")
        return False
    
    return True

async def test_mcp_market_data(symbol: str = "AAPL"):
    """Test retrieving enhanced market data"""
    print(f"\n2. Testing market data for {symbol}...")
    
    # Get MCP enhanced data
    enhanced_data = await market_data.get_mcp_enhanced_data(symbol)
    
    if enhanced_data:
        print(f"[OK] Retrieved MCP enhanced data for {symbol}")
        
        # Display quote data
        if 'mcp_quote' in enhanced_data:
            quote = enhanced_data['mcp_quote']
            print(f"\n  Quote Data:")
            print(f"    Price: ${quote.get('price', 'N/A')}")
            print(f"    P/E Ratio: {quote.get('pe_ratio', 'N/A')}")
            print(f"    Market Cap: ${quote.get('market_cap', 'N/A'):,.0f}" if quote.get('market_cap') else "    Market Cap: N/A")
            print(f"    52W High: ${quote.get('52w_high', 'N/A')}")
            print(f"    52W Low: ${quote.get('52w_low', 'N/A')}")
        
        # Display financial data
        if 'mcp_financials' in enhanced_data:
            financials = enhanced_data['mcp_financials']
            print(f"\n  Financial Data:")
            print(f"    Revenue: ${financials.get('revenue', 'N/A'):,.0f}" if financials.get('revenue') else "    Revenue: N/A")
            print(f"    Net Income: ${financials.get('net_income', 'N/A'):,.0f}" if financials.get('net_income') else "    Net Income: N/A")
            print(f"    Free Cash Flow: ${financials.get('free_cash_flow', 'N/A'):,.0f}" if financials.get('free_cash_flow') else "    Free Cash Flow: N/A")
        
        # Display analyst ratings
        if 'mcp_ratings' in enhanced_data:
            ratings = enhanced_data['mcp_ratings']
            print(f"\n  Analyst Ratings:")
            print(f"    Consensus: {ratings.get('consensus', 'N/A')}")
            print(f"    Target Price: ${ratings.get('target_price', 'N/A')}")
            print(f"    Analyst Count: {ratings.get('analyst_count', 'N/A')}")
        
        # Display insider trading
        if 'mcp_insider_trading' in enhanced_data:
            trades = enhanced_data['mcp_insider_trading']
            if trades:
                print(f"\n  Recent Insider Trading: {len(trades)} transactions")
        
        # Display options flow
        if 'mcp_options_flow' in enhanced_data:
            options = enhanced_data['mcp_options_flow']
            if options:
                print(f"\n  Options Flow Data Available")
                if 'put_call_ratio' in options:
                    print(f"    Put/Call Ratio: {options['put_call_ratio']}")
    else:
        print(f"[ERROR] No MCP data retrieved for {symbol}")
    
    return enhanced_data

async def test_market_movers():
    """Test getting market movers"""
    print("\n3. Testing market movers...")
    
    movers = await market_data.get_market_movers()
    
    if movers:
        print("[OK] Retrieved market movers")
        
        for category in ['gainers', 'losers', 'most_active']:
            if category in movers and movers[category]:
                print(f"\n  Top {category.replace('_', ' ').title()}:")
                for i, mover in enumerate(movers[category][:3], 1):
                    symbol = mover.get('symbol', 'N/A')
                    change = mover.get('change_percent', 0)
                    print(f"    {i}. {symbol}: {change:+.2f}%")
    else:
        print("[ERROR] No market movers data available")

async def test_earnings_calendar():
    """Test getting earnings calendar"""
    print("\n4. Testing earnings calendar...")
    
    earnings = await market_data.get_earnings_calendar(days_ahead=7)
    
    if earnings:
        print(f"[OK] Retrieved {len(earnings)} upcoming earnings")
        
        # Show first 5
        for i, earning in enumerate(earnings[:5], 1):
            symbol = earning.get('symbol', 'N/A')
            date = earning.get('date', 'N/A')
            estimate = earning.get('eps_estimate', 'N/A')
            print(f"    {i}. {symbol} on {date} (Est: ${estimate})")
    else:
        print("[ERROR] No earnings calendar data available")

async def test_economic_indicators():
    """Test getting economic indicators"""
    print("\n5. Testing economic indicators...")
    
    indicators = await market_data.get_economic_indicators()
    
    if indicators:
        print("[OK] Retrieved economic indicators")
        
        for indicator, data in indicators.items():
            if data:
                value = data.get('value', 'N/A')
                date = data.get('date', 'N/A')
                print(f"    {indicator}: {value} (as of {date})")
    else:
        print("[ERROR] No economic indicators available")

async def test_fundamental_analyst_with_mcp():
    """Test fundamental analyst using MCP data"""
    print("\n6. Testing Fundamental Analyst with MCP data...")
    
    # Initialize analyst
    analyst = FundamentalAnalyst()
    
    # Test symbol
    symbol = "MSFT"
    
    # Get enhanced market data
    enhanced_data = await market_data.get_mcp_enhanced_data(symbol)
    
    # Prepare market data with MCP enhancement
    market_data_dict = {
        'current_price': enhanced_data.get('mcp_quote', {}).get('price', 400),
        'mcp_enhanced_data': enhanced_data
    }
    
    # Run analysis
    report = await analyst.analyze(symbol, market_data_dict)
    
    if report:
        print(f"[OK] Fundamental analysis completed for {symbol}")
        print(f"\n  Analysis Results:")
        print(f"    Action: {report.action.value}")
        print(f"    Confidence: {report.confidence:.2%}")
        print(f"    Risk Level: {report.risk_level.value}")
        print(f"    Time Horizon: {report.time_horizon.value}")
        
        if report.target_price:
            print(f"    Target Price: ${report.target_price:.2f}")
        if report.stop_loss:
            print(f"    Stop Loss: ${report.stop_loss:.2f}")
        
        print(f"\n  Key Factors:")
        for factor in report.key_factors[:3]:
            print(f"    - {factor}")
        
        # Check if MCP data was used
        if 'mcp_' in str(report.metrics):
            print(f"\n  [OK] MCP data successfully integrated into analysis")
    else:
        print("[ERROR] Analysis failed")

async def main():
    """Run all tests"""
    try:
        # Test connection
        connected = await test_mcp_connection()
        
        if not connected:
            print("\nNote: To enable MCP integration, set the FINANCIAL_DATASETS_API_KEY environment variable")
            print("You can get an API key from: https://mcp.financialdatasets.ai")
            return
        
        # Run tests
        await test_mcp_market_data("AAPL")
        await test_market_movers()
        await test_earnings_calendar()
        await test_economic_indicators()
        await test_fundamental_analyst_with_mcp()
        
        # Disconnect
        print("\n" + "="*50)
        print("Disconnecting from data sources...")
        await market_data.disconnect_all()
        print("[OK] Tests completed successfully")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure cleanup
        await market_data.disconnect_all()

if __name__ == "__main__":
    print("Financial Datasets MCP Integration Test")
    print("========================================")
    
    # Check for API key
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("\nWarning: FINANCIAL_DATASETS_API_KEY not set")
        print("  The MCP integration will run in limited/demo mode")
        print("  Get your API key at: https://mcp.financialdatasets.ai")
    else:
        print(f"\n[OK] API key configured (length: {len(api_key)})")
    
    # Run tests
    asyncio.run(main())