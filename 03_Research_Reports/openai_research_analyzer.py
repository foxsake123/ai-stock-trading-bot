"""
OpenAI-Powered Pre-Market Research Analyzer
Generates comprehensive market analysis using GPT-4
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI
import yfinance as yf
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openai_research")

class OpenAIResearchAnalyzer:
    """
    Generates pre-market research using OpenAI's GPT-4
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # or "gpt-4" or "gpt-3.5-turbo"
        
    def get_market_context(self) -> Dict[str, Any]:
        """Get current market context for analysis"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'market_status': 'pre-market' if datetime.now().hour < 9.5 else 'open',
            'indices': {},
            'vix': None,
            'dollar_index': None
        }
        
        # Get major indices
        indices = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ',
            'DIA': 'Dow Jones',
            'IWM': 'Russell 2000',
            'VIX': 'Volatility Index'
        }
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change_pct = ((current - prev) / prev) * 100
                    
                    context['indices'][symbol] = {
                        'name': name,
                        'price': current,
                        'change_pct': change_pct,
                        '5d_trend': 'up' if hist['Close'].iloc[-1] > hist['Close'].iloc[0] else 'down'
                    }
            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")
        
        return context
    
    def generate_watchlist_analysis(self, tickers: List[str]) -> str:
        """Generate analysis for a watchlist using GPT-4"""
        
        # Gather data for each ticker
        ticker_data = []
        for ticker in tickers[:10]:  # Limit to 10 to manage token usage
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1mo")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    month_ago = hist['Close'].iloc[0]
                    month_change = ((current_price - month_ago) / month_ago) * 100
                    
                    # Get recent news
                    news = stock.news[:3] if hasattr(stock, 'news') else []
                    news_summary = [n.get('title', '') for n in news]
                    
                    ticker_data.append({
                        'symbol': ticker,
                        'price': current_price,
                        'month_change_pct': month_change,
                        'volume': hist['Volume'].iloc[-1],
                        'avg_volume': hist['Volume'].mean(),
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 0),
                        'sector': info.get('sector', 'Unknown'),
                        'recent_news': news_summary
                    })
            except Exception as e:
                logger.warning(f"Error analyzing {ticker}: {e}")
        
        # Create prompt for GPT-4
        prompt = f"""
        You are a professional stock market analyst preparing a pre-market research report.
        Analyze the following stocks and provide actionable trading recommendations.
        
        Market Context:
        {json.dumps(self.get_market_context(), indent=2)}
        
        Stocks to Analyze:
        {json.dumps(ticker_data, indent=2)}
        
        Please provide:
        1. Overall market sentiment and key themes
        2. Top 3 BUY recommendations with entry points and stop losses
        3. Top 3 stocks to AVOID today with reasons
        4. Key catalysts to watch (earnings, economic data, etc.)
        5. Risk factors for today's session
        
        Format your response as a structured JSON with these sections:
        - market_outlook (bullish/neutral/bearish with explanation)
        - buy_recommendations (list of ticker, entry, stop_loss, target, reasoning)
        - avoid_list (list of ticker, reason)
        - key_catalysts (list of events)
        - risk_factors (list of risks)
        - trading_strategy (recommended approach for the day)
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior equity analyst with 20 years of experience in institutional trading."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def analyze_single_stock(self, ticker: str, strategy: str = "swing") -> Dict[str, Any]:
        """Deep analysis of a single stock"""
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="3mo")
            
            # Prepare comprehensive data
            stock_data = {
                'symbol': ticker,
                'company': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'price': hist['Close'].iloc[-1] if not hist.empty else 0,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'eps': info.get('trailingEps', 0),
                'dividend_yield': info.get('dividendYield', 0),
                '52w_high': info.get('fiftyTwoWeekHigh', 0),
                '52w_low': info.get('fiftyTwoWeekLow', 0),
                'avg_volume': info.get('averageVolume', 0),
                'short_ratio': info.get('shortRatio', 0),
                'beta': info.get('beta', 1),
                'price_history': hist['Close'].tolist()[-20:] if not hist.empty else []
            }
            
            # Create analysis prompt
            prompt = f"""
            Perform a comprehensive {strategy} trading analysis for {ticker}.
            
            Stock Data:
            {json.dumps(stock_data, indent=2)}
            
            Provide a detailed analysis including:
            1. Technical Analysis (support/resistance, trend, momentum)
            2. Fundamental Assessment (valuation, growth prospects)
            3. Entry Strategy (specific price levels and conditions)
            4. Risk Management (stop loss, position sizing)
            5. Price Targets (3 targets with timeframes)
            6. Catalysts & Risks (upcoming events, concerns)
            7. Overall Rating (1-10 scale)
            8. Specific Trade Setup
            
            Return as JSON with these keys:
            - technical_analysis
            - fundamental_analysis
            - entry_points (list of price, condition)
            - stop_loss
            - targets (list of price, timeframe)
            - catalysts
            - risks
            - rating
            - trade_setup (specific instructions)
            - recommendation (BUY/HOLD/SELL)
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert {strategy} trader analyzing stocks for optimal entry and exit points."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['symbol'] = ticker
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return None
    
    def generate_morning_brief(self, 
                              dee_bot_tickers: List[str],
                              shorgan_bot_tickers: List[str]) -> Dict[str, Any]:
        """Generate comprehensive morning brief for both bots"""
        
        logger.info("Generating morning brief via OpenAI...")
        
        # Get market context
        context = self.get_market_context()
        
        # Create comprehensive prompt
        prompt = f"""
        Generate a comprehensive pre-market trading brief for two trading strategies:
        
        1. DEE-BOT (Institutional Strategy) - Focus on S&P 100 stocks, value investing
        2. SHORGAN-BOT (Catalyst Strategy) - Focus on momentum, news catalysts, short squeezes
        
        Market Context:
        {json.dumps(context, indent=2)}
        
        DEE-BOT Watchlist: {dee_bot_tickers[:10]}
        SHORGAN-BOT Watchlist: {shorgan_bot_tickers[:10]}
        
        Provide a structured analysis with:
        
        For DEE-BOT:
        - Top 3 institutional accumulation plays
        - Value opportunities with strong fundamentals
        - Dividend aristocrats on sale
        - Risk/reward setups over 3:1
        
        For SHORGAN-BOT:
        - Top 3 catalyst plays for today
        - Momentum breakouts
        - Short squeeze candidates
        - News-driven opportunities
        
        General:
        - Market direction bias
        - Key levels for SPY and QQQ
        - Economic events today
        - Sector rotation insights
        
        Format as JSON with these sections:
        - market_outlook
        - dee_bot_trades (list with ticker, entry, stop, target, reasoning)
        - shorgan_bot_trades (list with ticker, entry, stop, target, catalyst)
        - key_levels (SPY, QQQ support/resistance)
        - economic_calendar
        - risk_warnings
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are the head of trading at a hedge fund, preparing the morning brief for your trading team."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            brief = json.loads(response.choices[0].message.content)
            brief['generated_at'] = datetime.now().isoformat()
            brief['model'] = self.model
            
            # Save the brief
            filename = f"03_Research_Reports/Daily/morning_brief_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(brief, f, indent=2)
            
            logger.info(f"Morning brief saved to {filename}")
            
            return brief
            
        except Exception as e:
            logger.error(f"Error generating morning brief: {e}")
            return None
    
    def analyze_market_sentiment(self) -> Dict[str, Any]:
        """Analyze overall market sentiment using GPT-4"""
        
        prompt = """
        Based on current market conditions, provide a sentiment analysis:
        
        1. Overall market sentiment (1-10, 10 being most bullish)
        2. Fear & Greed indicators
        3. Sector rotation (what's hot, what's not)
        4. Risk on vs Risk off assessment
        5. Recommended portfolio positioning
        
        Consider:
        - Recent Fed actions
        - Economic data trends
        - Geopolitical events
        - Technical market structure
        
        Return as JSON with numerical scores and explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a market sentiment analyst specializing in behavioral finance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None


def generate_pre_market_research():
    """Main function to generate pre-market research"""
    
    print("=" * 70)
    print("OPENAI PRE-MARKET RESEARCH GENERATOR")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = OpenAIResearchAnalyzer()
    
    # Define watchlists
    dee_bot_watchlist = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",
        "BRK.B", "JPM", "V", "JNJ", "WMT"
    ]
    
    shorgan_bot_watchlist = [
        "NVDA", "TSLA", "AMD", "PLTR", "COIN",
        "GME", "AMC", "SOFI", "RIVN", "LCID"
    ]
    
    # Generate morning brief
    print("\nGenerating comprehensive morning brief...")
    brief = analyzer.generate_morning_brief(dee_bot_watchlist, shorgan_bot_watchlist)
    
    if brief:
        print("\n✅ Morning Brief Generated Successfully!")
        print("\n" + "=" * 50)
        print("MARKET OUTLOOK:", brief.get('market_outlook', 'N/A'))
        print("=" * 50)
        
        # Display DEE-BOT recommendations
        print("\n📊 DEE-BOT INSTITUTIONAL TRADES:")
        for trade in brief.get('dee_bot_trades', [])[:3]:
            print(f"  {trade['ticker']}: Entry ${trade['entry']}, Stop ${trade['stop']}, Target ${trade['target']}")
            print(f"    Reasoning: {trade['reasoning']}")
        
        # Display SHORGAN-BOT recommendations
        print("\n🚀 SHORGAN-BOT CATALYST TRADES:")
        for trade in brief.get('shorgan_bot_trades', [])[:3]:
            print(f"  {trade['ticker']}: Entry ${trade['entry']}, Stop ${trade['stop']}, Target ${trade['target']}")
            print(f"    Catalyst: {trade['catalyst']}")
        
        print("\n📈 KEY LEVELS:")
        levels = brief.get('key_levels', {})
        for symbol, data in levels.items():
            print(f"  {symbol}: Support {data.get('support', 'N/A')}, Resistance {data.get('resistance', 'N/A')}")
        
        return brief
    else:
        print("❌ Failed to generate morning brief")
        return None


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please add OPENAI_API_KEY to your .env file")
        print("   Get your API key from: https://platform.openai.com/api-keys")
    else:
        generate_pre_market_research()