"""
Quick test of OpenAI research generation
"""

import os
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / '03_Research_Reports'))

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from openai_research_analyzer import OpenAIResearchAnalyzer

def test_openai():
    """Test OpenAI API connection and generate sample research"""
    
    print("=" * 70)
    print("TESTING OPENAI RESEARCH GENERATION")
    print("=" * 70)
    
    try:
        # Initialize analyzer
        analyzer = OpenAIResearchAnalyzer()
        print("✅ OpenAI client initialized successfully")
        
        # Test 1: Market context
        print("\n📊 Testing market context retrieval...")
        context = analyzer.get_market_context()
        print(f"  Market status: {context['market_status']}")
        print(f"  Indices tracked: {len(context['indices'])}")
        
        # Test 2: Single stock analysis (quick test)
        print("\n🔍 Testing single stock analysis...")
        print("  Analyzing NVDA...")
        analysis = analyzer.analyze_single_stock("NVDA", strategy="day_trade")
        
        if analysis:
            print(f"  ✅ Analysis complete!")
            print(f"    Rating: {analysis.get('rating', 'N/A')}/10")
            print(f"    Recommendation: {analysis.get('recommendation', 'N/A')}")
            if 'entry_points' in analysis and analysis['entry_points']:
                print(f"    Entry points: {analysis['entry_points'][0] if analysis['entry_points'] else 'N/A'}")
            print(f"    Stop loss: {analysis.get('stop_loss', 'N/A')}")
        
        # Test 3: Market sentiment
        print("\n💭 Testing market sentiment analysis...")
        sentiment = analyzer.analyze_market_sentiment()
        if sentiment:
            print(f"  ✅ Sentiment analysis complete!")
            print(f"    Overall sentiment: {sentiment}")
        
        print("\n" + "=" * 70)
        print("✅ OPENAI INTEGRATION WORKING!")
        print("=" * 70)
        print("\nYou can now generate full pre-market research:")
        print("  python 03_Research_Reports/automated_research_pipeline.py --generate")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPossible issues:")
        print("1. Check API key is valid")
        print("2. Check OpenAI account has credits")
        print("3. Check internet connection")

if __name__ == "__main__":
    test_openai()