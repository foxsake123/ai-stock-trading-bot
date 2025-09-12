"""
Test OpenAI API Integration
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai_research_fetcher import OpenAIResearchFetcher

def test_openai_integration():
    """Test the OpenAI API integration"""
    
    print("="*60)
    print("TESTING OPENAI API INTEGRATION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        # Initialize fetcher
        fetcher = OpenAIResearchFetcher()
        print("\n[OK] OpenAI API key loaded successfully")
        
        # Test API connection and fetch research
        print("\nFetching research from OpenAI (this may take 10-20 seconds)...")
        research = fetcher.run()
        
        if research:
            print("\n[OK] Successfully fetched research from OpenAI!")
            print(f"\nResearch Summary:")
            print(f"- Date: {research.get('date', 'N/A')}")
            print(f"- Number of trades: {len(research.get('trades', []))}")
            
            if 'trades' in research and research['trades']:
                print(f"\nSample trades:")
                for i, trade in enumerate(research['trades'][:3]):
                    print(f"\n  Trade {i+1}:")
                    print(f"    Symbol: {trade.get('symbol', 'N/A')}")
                    print(f"    Action: {trade.get('action', 'N/A')}")
                    print(f"    Catalyst: {trade.get('catalyst', 'N/A')[:50]}...")
                    print(f"    Entry: ${trade.get('entry_min', 0):.2f} - ${trade.get('entry_max', 0):.2f}")
                    print(f"    Stop: ${trade.get('stop', 0):.2f}")
                    print(f"    Target: ${trade.get('target', 0):.2f}")
            
            if 'market_context' in research:
                print(f"\nMarket Context:")
                for key, value in research['market_context'].items():
                    print(f"  {key}: {value}")
            
            # Check files created
            date_str = datetime.now().strftime('%Y-%m-%d')
            files_created = []
            
            json_file = f"02_data/research/reports/pre_market_daily/{date_str}_openai_research.json"
            if os.path.exists(json_file):
                files_created.append(f"[OK] JSON: {json_file}")
            
            md_file = f"02_data/research/reports/pre_market_daily/{date_str}_pre_market.md"
            if os.path.exists(md_file):
                files_created.append(f"[OK] Markdown: {md_file}")
            
            pdf_file = f"02_data/research/reports/pre_market_daily/{date_str}_pre_market_report.pdf"
            if os.path.exists(pdf_file):
                files_created.append(f"[OK] PDF: {pdf_file}")
            
            if files_created:
                print(f"\nFiles created:")
                for file in files_created:
                    print(f"  {file}")
            
            print("\n" + "="*60)
            print("[SUCCESS] OPENAI INTEGRATION TEST SUCCESSFUL!")
            print("="*60)
            
            return True
        else:
            print("\n[ERROR] Failed to fetch research from OpenAI")
            print("Please check your API key and internet connection")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error during test: {e}")
        print("\nTroubleshooting:")
        print("1. Check that OPENAI_API_KEY is set in .env file")
        print("2. Ensure the API key is valid and has credits")
        print("3. Check internet connection")
        print("4. Try running: pip install openai --upgrade")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    sys.exit(0 if success else 1)