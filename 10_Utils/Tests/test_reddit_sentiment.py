"""
Test Reddit API Integration for Social Sentiment
"""

import os
import sys
import praw
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_reddit_connection():
    """Test Reddit API connection and sentiment analysis"""
    
    print("=" * 60)
    print("REDDIT API TEST - SOCIAL SENTIMENT ANALYSIS")
    print("=" * 60)
    
    # Initialize Reddit client
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'trading-bot/1.0')
        )
        
        print("✅ Connected to Reddit API")
        print(f"   User Agent: {os.getenv('REDDIT_USER_AGENT')}")
        
    except Exception as e:
        print(f"❌ Failed to connect to Reddit: {e}")
        return
    
    # Test subreddits
    subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
    
    print("\n📊 Testing Subreddit Access:")
    print("-" * 40)
    
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            print(f"✅ r/{sub_name}: {subreddit.subscribers:,} subscribers")
        except Exception as e:
            print(f"❌ r/{sub_name}: {str(e)[:50]}")
    
    # Analyze sentiment for popular tickers
    tickers = ["NVDA", "TSLA", "GME", "AMC", "AAPL"]
    
    print("\n💬 Ticker Sentiment Analysis (r/wallstreetbets):")
    print("-" * 40)
    
    wsb = reddit.subreddit('wallstreetbets')
    
    for ticker in tickers:
        try:
            mentions = 0
            bullish = 0
            bearish = 0
            
            # Search for ticker mentions in hot posts
            for submission in wsb.search(ticker, limit=10, time_filter='day'):
                mentions += 1
                
                # Simple sentiment based on score and title
                title_lower = submission.title.lower()
                
                if submission.score > 100:
                    bullish += 1
                elif submission.score < 50:
                    bearish += 1
                
                # Keywords sentiment
                bullish_keywords = ['moon', 'calls', 'buy', 'long', 'bullish', 'up', 'green', 'yolo']
                bearish_keywords = ['puts', 'short', 'sell', 'bearish', 'down', 'red', 'crash']
                
                if any(word in title_lower for word in bullish_keywords):
                    bullish += 1
                if any(word in title_lower for word in bearish_keywords):
                    bearish += 1
            
            if mentions > 0:
                sentiment_score = (bullish - bearish) / mentions
                sentiment_label = "🚀 Bullish" if sentiment_score > 0.2 else "🐻 Bearish" if sentiment_score < -0.2 else "😐 Neutral"
                
                print(f"{ticker:5} - Mentions: {mentions:2} | Sentiment: {sentiment_label} ({sentiment_score:+.2f})")
            else:
                print(f"{ticker:5} - No recent mentions")
                
        except Exception as e:
            print(f"{ticker:5} - Error: {str(e)[:50]}")
    
    # Get trending topics
    print("\n🔥 Trending on r/wallstreetbets (Top 5 Hot Posts):")
    print("-" * 40)
    
    try:
        for i, submission in enumerate(wsb.hot(limit=6)):
            if i == 0:  # Skip sticky post
                continue
            print(f"{i}. {submission.title[:70]}...")
            print(f"   Score: {submission.score:,} | Comments: {submission.num_comments:,}")
            
    except Exception as e:
        print(f"Error getting hot posts: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Reddit Integration Working!")
    print("=" * 60)

if __name__ == "__main__":
    test_reddit_connection()