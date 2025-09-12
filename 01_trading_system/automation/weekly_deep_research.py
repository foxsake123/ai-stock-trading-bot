"""
Weekly Deep Research Pipeline
Runs Sunday afternoons for comprehensive analysis
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import yfinance as yf
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import requests
import numpy as np

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
log_dir = '09_logs/automation'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/weekly_research_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class WeeklyDeepResearch:
    """Performs weekly deep research on portfolio and watchlist"""
    
    def __init__(self):
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_SHORGAN'),
            os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Telegram settings
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '-4524457329')
        
        # File paths
        self.portfolio_csv = '02_data/portfolio/positions/shorgan_bot_positions.csv'
        self.watchlist_file = '02_data/research/watchlist/shorgan_watchlist.json'
        self.research_output = f'02_data/research/reports/weekly_analysis/week_{datetime.now().strftime("%Y%m%d")}.json'
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.research_output), exist_ok=True)
        os.makedirs(os.path.dirname(self.watchlist_file), exist_ok=True)
        
    def get_current_holdings(self) -> List[str]:
        """Get list of current holdings from Alpaca"""
        try:
            positions = self.api.list_positions()
            holdings = [pos.symbol for pos in positions]
            logging.info(f"Found {len(holdings)} current holdings")
            return holdings
        except Exception as e:
            logging.error(f"Error getting holdings: {e}")
            return []
    
    def get_watchlist(self) -> List[str]:
        """Get watchlist stocks"""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    data = json.load(f)
                    return data.get('symbols', [])
            else:
                # Default watchlist
                default_watchlist = [
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA',
                    'META', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH',
                    'HD', 'DIS', 'MA', 'BAC', 'XOM', 'CVX', 'ABBV'
                ]
                self.save_watchlist(default_watchlist)
                return default_watchlist
        except Exception as e:
            logging.error(f"Error loading watchlist: {e}")
            return []
    
    def save_watchlist(self, symbols: List[str]):
        """Save watchlist to file"""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump({'symbols': symbols, 'updated': datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving watchlist: {e}")
    
    def perform_deep_research(self, symbol: str) -> Dict:
        """Perform comprehensive research on a single stock"""
        research = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'fundamentals': {},
            'technicals': {},
            'sentiment': {},
            'ranking_score': 0,
            'recommendation': 'HOLD'
        }
        
        try:
            # Get stock data from yfinance
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Fundamentals
            research['fundamentals'] = {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'profit_margins': info.get('profitMargins', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1),
                'analyst_rating': info.get('recommendationKey', 'none'),
                'target_price': info.get('targetMeanPrice', 0)
            }
            
            # Technical Analysis (1 month of data)
            hist = stock.history(period="1mo")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                
                # Calculate RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                # Calculate MACD
                exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
                exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                
                research['technicals'] = {
                    'current_price': current_price,
                    'sma_20': sma_20,
                    'price_vs_sma20': ((current_price - sma_20) / sma_20) * 100,
                    'rsi': rsi,
                    'macd': macd.iloc[-1],
                    'macd_signal': signal.iloc[-1],
                    'volume_avg': hist['Volume'].mean(),
                    'volatility': hist['Close'].pct_change().std() * np.sqrt(252),
                    '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                    '52_week_low': info.get('fiftyTwoWeekLow', 0),
                    'price_vs_52w_high': ((current_price - info.get('fiftyTwoWeekHigh', current_price)) / info.get('fiftyTwoWeekHigh', current_price)) * 100
                }
            
            # Calculate ranking score (0-100)
            score = self.calculate_ranking_score(research)
            research['ranking_score'] = score
            
            # Generate recommendation
            if score >= 70:
                research['recommendation'] = 'STRONG BUY'
            elif score >= 60:
                research['recommendation'] = 'BUY'
            elif score >= 40:
                research['recommendation'] = 'HOLD'
            elif score >= 30:
                research['recommendation'] = 'SELL'
            else:
                research['recommendation'] = 'STRONG SELL'
            
            logging.info(f"Research complete for {symbol}: Score={score:.1f}, Rec={research['recommendation']}")
            
        except Exception as e:
            logging.error(f"Error researching {symbol}: {e}")
        
        return research
    
    def calculate_ranking_score(self, research: Dict) -> float:
        """Calculate overall ranking score for a stock"""
        score = 50.0  # Start neutral
        
        fundamentals = research.get('fundamentals', {})
        technicals = research.get('technicals', {})
        
        # Fundamental factors
        pe = fundamentals.get('pe_ratio', 0)
        if 0 < pe < 15:
            score += 10
        elif pe > 30:
            score -= 10
        
        peg = fundamentals.get('peg_ratio', 0)
        if 0 < peg < 1:
            score += 10
        elif peg > 2:
            score -= 10
        
        roe = fundamentals.get('roe', 0)
        if roe > 0.15:
            score += 10
        elif roe < 0.05:
            score -= 10
        
        debt_equity = fundamentals.get('debt_to_equity', 0)
        if debt_equity < 0.5:
            score += 5
        elif debt_equity > 2:
            score -= 10
        
        # Technical factors
        rsi = technicals.get('rsi', 50)
        if 30 < rsi < 70:
            score += 5
        elif rsi < 20 or rsi > 80:
            score -= 10
        
        price_vs_sma = technicals.get('price_vs_sma20', 0)
        if price_vs_sma > 0:
            score += 5
        else:
            score -= 5
        
        macd = technicals.get('macd', 0)
        macd_signal = technicals.get('macd_signal', 0)
        if macd > macd_signal:
            score += 10
        else:
            score -= 5
        
        # Analyst rating
        rating = fundamentals.get('analyst_rating', 'none')
        if rating in ['strong_buy', 'buy']:
            score += 10
        elif rating in ['sell', 'strong_sell']:
            score -= 10
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return score
    
    def rank_all_stocks(self, research_results: List[Dict]) -> List[Dict]:
        """Rank all stocks by score and identify actions"""
        # Sort by ranking score
        ranked = sorted(research_results, key=lambda x: x['ranking_score'], reverse=True)
        
        # Add ranking position
        for i, stock in enumerate(ranked):
            stock['rank'] = i + 1
        
        return ranked
    
    def prepare_adjustments(self, ranked_stocks: List[Dict], current_holdings: List[str]) -> Dict:
        """Prepare portfolio adjustments for Monday"""
        adjustments = {
            'add': [],
            'remove': [],
            'increase': [],
            'decrease': [],
            'hold': []
        }
        
        # Top 10 stocks should be in portfolio
        top_10_symbols = [s['symbol'] for s in ranked_stocks[:10]]
        
        # Stocks to add (in top 10 but not held)
        for symbol in top_10_symbols:
            if symbol not in current_holdings:
                stock = next(s for s in ranked_stocks if s['symbol'] == symbol)
                if stock['ranking_score'] >= 60:
                    adjustments['add'].append({
                        'symbol': symbol,
                        'score': stock['ranking_score'],
                        'recommendation': stock['recommendation']
                    })
        
        # Stocks to remove (held but low score)
        for symbol in current_holdings:
            stock = next((s for s in ranked_stocks if s['symbol'] == symbol), None)
            if stock:
                if stock['ranking_score'] < 40:
                    adjustments['remove'].append({
                        'symbol': symbol,
                        'score': stock['ranking_score'],
                        'recommendation': stock['recommendation']
                    })
                elif stock['ranking_score'] >= 60:
                    adjustments['hold'].append({
                        'symbol': symbol,
                        'score': stock['ranking_score'],
                        'recommendation': stock['recommendation']
                    })
        
        return adjustments
    
    def send_weekly_report(self, ranked_stocks: List[Dict], adjustments: Dict):
        """Send weekly research report via Telegram"""
        try:
            message = f"""📊 WEEKLY DEEP RESEARCH REPORT
            
📅 Week of {datetime.now().strftime('%Y-%m-%d')}
🤖 SHORGAN-BOT Portfolio Analysis

🏆 TOP 10 STOCKS:
"""
            
            # Add top 10
            for stock in ranked_stocks[:10]:
                emoji = "🟢" if stock['ranking_score'] >= 70 else "🟡" if stock['ranking_score'] >= 50 else "🔴"
                message += f"\n{emoji} {stock['rank']}. {stock['symbol']}: {stock['ranking_score']:.1f} - {stock['recommendation']}"
            
            # Portfolio adjustments
            message += "\n\n📈 MONDAY ADJUSTMENTS:"
            
            if adjustments['add']:
                message += "\n\n✅ ADD:"
                for item in adjustments['add'][:3]:  # Top 3 adds
                    message += f"\n• {item['symbol']} (Score: {item['score']:.1f})"
            
            if adjustments['remove']:
                message += "\n\n❌ REMOVE:"
                for item in adjustments['remove']:
                    message += f"\n• {item['symbol']} (Score: {item['score']:.1f})"
            
            if adjustments['hold']:
                message += f"\n\n✓ HOLD: {len(adjustments['hold'])} positions"
            
            # Key metrics
            avg_score = np.mean([s['ranking_score'] for s in ranked_stocks[:20]])
            message += f"""

📊 MARKET METRICS:
• Avg Score (Top 20): {avg_score:.1f}
• Bullish Stocks: {len([s for s in ranked_stocks if s['ranking_score'] >= 60])}
• Bearish Stocks: {len([s for s in ranked_stocks if s['ranking_score'] < 40])}

📝 Full report saved to:
{self.research_output}
"""
            
            # Send message
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logging.info("Weekly report sent via Telegram")
            else:
                logging.error(f"Telegram send failed: {response.text}")
                
        except Exception as e:
            logging.error(f"Error sending weekly report: {e}")
    
    def save_research_results(self, research_results: List[Dict], adjustments: Dict):
        """Save research results to file"""
        try:
            output = {
                'timestamp': datetime.now().isoformat(),
                'week': datetime.now().strftime('%Y-W%U'),
                'stocks_analyzed': len(research_results),
                'research': research_results,
                'adjustments': adjustments
            }
            
            with open(self.research_output, 'w') as f:
                json.dump(output, f, indent=2)
            
            logging.info(f"Research results saved to {self.research_output}")
            
        except Exception as e:
            logging.error(f"Error saving research results: {e}")
    
    def run(self):
        """Main execution for weekly research"""
        logging.info("="*60)
        logging.info("STARTING WEEKLY DEEP RESEARCH")
        logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("="*60)
        
        try:
            # Get current holdings and watchlist
            current_holdings = self.get_current_holdings()
            watchlist = self.get_watchlist()
            
            # Combine for analysis (remove duplicates)
            all_symbols = list(set(current_holdings + watchlist))
            logging.info(f"Analyzing {len(all_symbols)} stocks")
            
            # Perform deep research on each stock
            research_results = []
            for i, symbol in enumerate(all_symbols):
                logging.info(f"Researching {symbol} ({i+1}/{len(all_symbols)})")
                research = self.perform_deep_research(symbol)
                research_results.append(research)
                
                # Rate limiting
                if i < len(all_symbols) - 1:
                    time.sleep(1)  # Avoid overwhelming APIs
            
            # Rank all stocks
            ranked_stocks = self.rank_all_stocks(research_results)
            
            # Prepare portfolio adjustments
            adjustments = self.prepare_adjustments(ranked_stocks, current_holdings)
            
            # Save results
            self.save_research_results(ranked_stocks, adjustments)
            
            # Send Telegram report
            self.send_weekly_report(ranked_stocks, adjustments)
            
            logging.info("="*60)
            logging.info("WEEKLY RESEARCH COMPLETE")
            logging.info(f"Top stock: {ranked_stocks[0]['symbol']} (Score: {ranked_stocks[0]['ranking_score']:.1f})")
            logging.info(f"Recommended adds: {len(adjustments['add'])}")
            logging.info(f"Recommended removes: {len(adjustments['remove'])}")
            logging.info("="*60)
            
        except Exception as e:
            logging.error(f"Weekly research failed: {e}")
            # Send error notification
            self.send_error_notification(str(e))
    
    def send_error_notification(self, error_msg: str):
        """Send error notification via Telegram"""
        try:
            message = f"⚠️ Weekly Research Error\n\n{error_msg}"
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {'chat_id': self.telegram_chat_id, 'text': message}
            requests.post(url, data=payload)
        except:
            pass

if __name__ == "__main__":
    research = WeeklyDeepResearch()
    research.run()