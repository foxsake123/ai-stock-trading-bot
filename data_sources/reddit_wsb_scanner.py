"""
Reddit WallStreetBets Scanner - Real-time sentiment analysis
Uses PRAW (Python Reddit API Wrapper) for legitimate API access
"""

import praw
import pandas as pd
from datetime import datetime, timedelta
import re
from collections import Counter
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditWSBScanner:
    """Scan Reddit for trading signals and sentiment"""

    def __init__(self):
        # You'll need to create a Reddit app at https://www.reddit.com/prefs/apps
        # Then add your credentials here or in environment variables
        self.reddit = None  # Will be initialized with credentials

        self.subreddits = [
            "wallstreetbets",
            "stocks",
            "options",
            "pennystocks",
            "Shortsqueeze",
            "SPACs",
            "investing",
            "StockMarket"
        ]

        # Common ticker patterns
        self.ticker_pattern = re.compile(r'\b([A-Z]{1,5})\b')

        # Exclude common words that match ticker pattern
        self.exclusions = {
            'I', 'A', 'THE', 'IS', 'IT', 'TO', 'AT', 'BE', 'OF', 'AND',
            'OR', 'FOR', 'WITH', 'AS', 'BY', 'FROM', 'UP', 'ON', 'IN',
            'DD', 'WSB', 'YOLO', 'FOMO', 'IMO', 'LOL', 'WTF', 'USD',
            'CEO', 'CFO', 'IPO', 'ETF', 'FDA', 'EPS', 'PE', 'USA'
        }

        # Sentiment keywords
        self.bullish_keywords = [
            'moon', 'squeeze', 'rocket', 'bull', 'calls', 'tendies', 'diamond hands',
            'buy', 'long', 'breakout', 'gainz', 'printing', 'uppies', 'green',
            'to the moon', 'lfg', "let's go", 'bullish', 'accumulate', 'oversold'
        ]

        self.bearish_keywords = [
            'puts', 'bear', 'short', 'dump', 'crash', 'sell', 'worthless',
            'bag holder', 'bagholder', 'rip', 'guh', 'loss porn', 'red',
            'drill', 'tank', 'bearish', 'overvalued', 'overbought'
        ]

    def init_reddit_client(self, client_id=None, client_secret=None, user_agent=None):
        """Initialize Reddit client with credentials"""
        try:
            self.reddit = praw.Reddit(
                client_id=client_id or "YOUR_CLIENT_ID",
                client_secret=client_secret or "YOUR_CLIENT_SECRET",
                user_agent=user_agent or "TradingBot/1.0"
            )
            logger.info("Reddit client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            return False

    def scan_subreddit(self, subreddit_name, sort='hot', limit=100):
        """Scan a subreddit for ticker mentions and sentiment"""
        if not self.reddit:
            logger.error("Reddit client not initialized")
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            posts_data = []

            # Get posts based on sort method
            if sort == 'hot':
                posts = subreddit.hot(limit=limit)
            elif sort == 'new':
                posts = subreddit.new(limit=limit)
            elif sort == 'top':
                posts = subreddit.top(time_filter='day', limit=limit)
            else:
                posts = subreddit.hot(limit=limit)

            for post in posts:
                # Extract tickers from title and text
                title_tickers = self._extract_tickers(post.title)

                # Get post text (selftext for text posts)
                body_tickers = []
                if hasattr(post, 'selftext') and post.selftext:
                    body_tickers = self._extract_tickers(post.selftext)

                all_tickers = list(set(title_tickers + body_tickers))

                if all_tickers:
                    # Calculate sentiment
                    sentiment = self._analyze_sentiment(
                        post.title + " " + getattr(post, 'selftext', '')
                    )

                    posts_data.append({
                        'subreddit': subreddit_name,
                        'title': post.title,
                        'tickers': all_tickers,
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'url': f"https://reddit.com{post.permalink}",
                        'sentiment': sentiment['sentiment'],
                        'sentiment_score': sentiment['score'],
                        'author': str(post.author) if post.author else 'deleted',
                        'flair': post.link_flair_text,
                        'is_dd': self._is_dd_post(post)
                    })

            return posts_data

        except Exception as e:
            logger.error(f"Error scanning r/{subreddit_name}: {e}")
            return []

    def _extract_tickers(self, text):
        """Extract potential stock tickers from text"""
        if not text:
            return []

        # Find all uppercase words
        potential_tickers = self.ticker_pattern.findall(text)

        # Filter out common words and validate
        tickers = []
        for ticker in potential_tickers:
            if ticker not in self.exclusions and len(ticker) >= 2:
                # Additional validation: check if it appears with $ sign
                if f"${ticker}" in text:
                    tickers.append(ticker)
                # Or if it appears in common stock contexts
                elif any(context in text.lower() for context in
                        [f"{ticker.lower()} stock", f"{ticker.lower()} calls",
                         f"{ticker.lower()} puts", f"buy {ticker.lower()}"]):
                    tickers.append(ticker)
                # Or if it's a known popular ticker (you'd maintain this list)
                elif ticker in ['GME', 'AMC', 'TSLA', 'AAPL', 'SPY', 'NVDA',
                              'BBAI', 'SOUN', 'PLTR', 'SOFI', 'RIOT', 'MARA']:
                    tickers.append(ticker)

        return list(set(tickers))

    def _analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        if not text:
            return {'sentiment': 'neutral', 'score': 50}

        text_lower = text.lower()

        # Count bullish and bearish keywords
        bullish_count = sum(1 for keyword in self.bullish_keywords
                          if keyword in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords
                          if keyword in text_lower)

        # Check for rocket emojis and other indicators
        bullish_count += text.count('🚀') * 2
        bullish_count += text.count('💎') * 2
        bullish_count += text.count('🙌')
        bearish_count += text.count('📉') * 2
        bearish_count += text.count('🔻') * 2

        # Calculate score (0-100)
        total_signals = bullish_count + bearish_count
        if total_signals == 0:
            return {'sentiment': 'neutral', 'score': 50}

        score = (bullish_count / total_signals) * 100

        if score > 65:
            sentiment = 'bullish'
        elif score < 35:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {'sentiment': sentiment, 'score': score}

    def _is_dd_post(self, post):
        """Check if post is Due Diligence"""
        dd_indicators = ['dd', 'due diligence', 'deep dive', 'analysis', 'research']

        # Check flair
        if post.link_flair_text:
            flair_lower = post.link_flair_text.lower()
            if any(ind in flair_lower for ind in dd_indicators):
                return True

        # Check title
        title_lower = post.title.lower()
        if any(ind in title_lower for ind in dd_indicators):
            return True

        # Check if it's a long text post
        if hasattr(post, 'selftext') and len(post.selftext) > 500:
            return True

        return False

    def get_trending_tickers(self, time_window='day', min_mentions=3):
        """Get currently trending tickers across all monitored subreddits"""
        all_posts = []

        for subreddit in self.subreddits:
            logger.info(f"Scanning r/{subreddit}")
            posts = self.scan_subreddit(subreddit, sort='hot', limit=50)
            all_posts.extend(posts)

            # Also check new posts for emerging trends
            new_posts = self.scan_subreddit(subreddit, sort='new', limit=25)
            all_posts.extend(new_posts)

        # Aggregate ticker mentions
        ticker_stats = {}

        for post in all_posts:
            for ticker in post['tickers']:
                if ticker not in ticker_stats:
                    ticker_stats[ticker] = {
                        'mentions': 0,
                        'total_score': 0,
                        'total_comments': 0,
                        'sentiment_sum': 0,
                        'posts': []
                    }

                ticker_stats[ticker]['mentions'] += 1
                ticker_stats[ticker]['total_score'] += post['score']
                ticker_stats[ticker]['total_comments'] += post['num_comments']
                ticker_stats[ticker]['sentiment_sum'] += post['sentiment_score']
                ticker_stats[ticker]['posts'].append({
                    'title': post['title'][:100],
                    'score': post['score'],
                    'url': post['url']
                })

        # Filter and rank
        trending = []
        for ticker, stats in ticker_stats.items():
            if stats['mentions'] >= min_mentions:
                avg_sentiment = stats['sentiment_sum'] / stats['mentions']

                # Calculate trend score
                trend_score = (
                    stats['mentions'] * 10 +
                    stats['total_score'] * 0.1 +
                    stats['total_comments'] * 0.5
                )

                trending.append({
                    'ticker': ticker,
                    'mentions': stats['mentions'],
                    'total_score': stats['total_score'],
                    'total_comments': stats['total_comments'],
                    'avg_sentiment': avg_sentiment,
                    'sentiment': 'bullish' if avg_sentiment > 65 else 'bearish' if avg_sentiment < 35 else 'neutral',
                    'trend_score': trend_score,
                    'top_posts': sorted(stats['posts'], key=lambda x: x['score'], reverse=True)[:3]
                })

        # Sort by trend score
        trending.sort(key=lambda x: x['trend_score'], reverse=True)

        return trending

    def get_dd_posts(self, tickers=None, limit=10):
        """Get recent Due Diligence posts"""
        dd_posts = []

        for subreddit in ['wallstreetbets', 'stocks', 'investing']:
            posts = self.scan_subreddit(subreddit, sort='hot', limit=100)

            for post in posts:
                if post['is_dd']:
                    # If tickers specified, filter for those
                    if tickers:
                        if any(t in post['tickers'] for t in tickers):
                            dd_posts.append(post)
                    else:
                        dd_posts.append(post)

        # Sort by score and recency
        dd_posts.sort(key=lambda x: x['score'], reverse=True)

        return dd_posts[:limit]

    def monitor_ticker(self, ticker, time_window_hours=24):
        """Monitor specific ticker for sentiment changes"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        ticker_data = {
            'ticker': ticker,
            'posts': [],
            'total_mentions': 0,
            'sentiment_scores': [],
            'momentum': 'neutral'
        }

        for subreddit in self.subreddits:
            posts = self.scan_subreddit(subreddit, sort='new', limit=100)

            for post in posts:
                if ticker in post['tickers'] and post['created_utc'] > cutoff_time:
                    ticker_data['posts'].append(post)
                    ticker_data['total_mentions'] += 1
                    ticker_data['sentiment_scores'].append(post['sentiment_score'])

        if ticker_data['sentiment_scores']:
            avg_sentiment = sum(ticker_data['sentiment_scores']) / len(ticker_data['sentiment_scores'])
            ticker_data['avg_sentiment'] = avg_sentiment

            # Determine momentum
            if ticker_data['total_mentions'] > 10 and avg_sentiment > 70:
                ticker_data['momentum'] = 'strong_bullish'
            elif avg_sentiment > 60:
                ticker_data['momentum'] = 'bullish'
            elif avg_sentiment < 30:
                ticker_data['momentum'] = 'bearish'
            else:
                ticker_data['momentum'] = 'neutral'

        return ticker_data

    def save_scan_results(self, results, filename=None):
        """Save scan results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_scan_{timestamp}.json"

        filepath = Path("scripts-and-data/data/reddit_scans") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Saved scan results to {filepath}")
        return filepath

    def generate_report(self, trending_tickers):
        """Generate a formatted report of Reddit sentiment"""
        report = []
        report.append("=" * 60)
        report.append("REDDIT SENTIMENT ANALYSIS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")

        report.append("TOP TRENDING TICKERS:")
        report.append("-" * 40)

        for i, ticker in enumerate(trending_tickers[:10], 1):
            report.append(f"{i}. ${ticker['ticker']}")
            report.append(f"   Mentions: {ticker['mentions']}")
            report.append(f"   Total Score: {ticker['total_score']:,}")
            report.append(f"   Sentiment: {ticker['sentiment']} ({ticker['avg_sentiment']:.1f}/100)")
            report.append(f"   Trend Score: {ticker['trend_score']:.1f}")

            if ticker['top_posts']:
                report.append("   Top Post: " + ticker['top_posts'][0]['title'])
            report.append("")

        return "\n".join(report)

# Example usage
def main():
    """Example usage of Reddit scanner"""
    scanner = RedditWSBScanner()

    # Initialize with credentials (you need to get these from Reddit)
    # scanner.init_reddit_client(
    #     client_id="YOUR_CLIENT_ID",
    #     client_secret="YOUR_CLIENT_SECRET",
    #     user_agent="TradingBot/1.0"
    # )

    # Get trending tickers
    # trending = scanner.get_trending_tickers()
    # print(scanner.generate_report(trending))

    # Monitor specific ticker
    # ticker_data = scanner.monitor_ticker("BBAI")
    # print(f"BBAI Sentiment: {ticker_data}")

    # Get DD posts
    # dd_posts = scanner.get_dd_posts(tickers=["NVDA", "TSLA"])
    # for post in dd_posts:
    #     print(f"DD: {post['title']} - Score: {post['score']}")

if __name__ == "__main__":
    main()