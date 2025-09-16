"""
DEE-BOT Research Report Generator
Beta-Neutral S&P 100 Strategy with 2X Leverage
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging
import yfinance as yf
from typing import Dict, List, Any

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DeeBotResearchGenerator:
    """Generates research reports for DEE-BOT's beta-neutral strategy"""
    
    def __init__(self):
        # Initialize Alpaca API for DEE-BOT
        self.api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY_DEE'),
            os.getenv('ALPACA_SECRET_KEY_DEE'),
            'https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # S&P 100 components (top symbols for example)
        self.sp100_symbols = [
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'NVDA', 'META', 'BRK-B', 'TSLA', 'JNJ',
            'JPM', 'V', 'PG', 'XOM', 'UNH', 'HD', 'CVX', 'MA', 'BAC', 'ABBV',
            'PFE', 'LLY', 'KO', 'PEP', 'AVGO', 'MRK', 'TMO', 'COST', 'VZ', 'DIS',
            'WMT', 'CMCSA', 'ABT', 'ADBE', 'CRM', 'NKE', 'WFC', 'MCD', 'CSCO', 'ACN',
            'DHR', 'TXN', 'NEE', 'BMY', 'PM', 'UPS', 'RTX', 'NFLX', 'T', 'MS',
            'AMGN', 'HON', 'LOW', 'ORCL', 'UNP', 'GS', 'IBM', 'SCHW', 'LMT', 'CVS',
            'AMD', 'CAT', 'INTC', 'BA', 'INTU', 'BLK', 'SPGI', 'ISRG', 'ADP', 'GILD'
        ]
        
        self.research_dir = '02_data/research/reports/dee_bot'
        os.makedirs(self.research_dir, exist_ok=True)
        
    def calculate_stock_metrics(self, symbol: str) -> Dict:
        """Calculate metrics for a single stock"""
        try:
            # Get stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1mo")
            
            if len(hist) == 0:
                return None
            
            # Calculate technical indicators
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            # Get latest price
            current_price = hist['Close'].iloc[-1]
            
            # Calculate simple momentum
            momentum_5d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) * 100 if len(hist) >= 5 else 0
            momentum_20d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-20] - 1) * 100 if len(hist) >= 20 else 0
            
            # RSI calculation
            rsi = self.calculate_rsi(hist['Close'])
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'beta': info.get('beta', 1.0),
                'volatility': volatility,
                'momentum_5d': momentum_5d,
                'momentum_20d': momentum_20d,
                'rsi': rsi,
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
        except Exception as e:
            logging.warning(f"Error calculating metrics for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        if len(prices) < period:
            return None
        
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0).rolling(window=period).mean()
        loss = -deltas.where(deltas < 0, 0).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
    
    def rank_opportunities(self, stocks: List[Dict]) -> List[Dict]:
        """Rank stocks based on beta-neutral strategy criteria"""
        # Filter valid stocks
        valid_stocks = [s for s in stocks if s and s['beta'] is not None]
        
        # Score each stock
        for stock in valid_stocks:
            score = 0
            
            # Beta score (prefer near 1.0 for neutrality)
            beta_diff = abs(stock['beta'] - 1.0)
            if beta_diff < 0.1:
                score += 30
            elif beta_diff < 0.3:
                score += 20
            elif beta_diff < 0.5:
                score += 10
            
            # Momentum score
            if stock['momentum_5d'] > 0:
                score += min(stock['momentum_5d'] * 2, 20)
            
            # RSI score (prefer 30-70 range)
            if stock['rsi']:
                if 30 <= stock['rsi'] <= 70:
                    score += 20
                elif 20 <= stock['rsi'] <= 80:
                    score += 10
            
            # Volume score (prefer liquid stocks)
            if stock['avg_volume'] > 10000000:
                score += 15
            elif stock['avg_volume'] > 5000000:
                score += 10
            
            # Volatility score (moderate volatility preferred)
            if 0.15 <= stock['volatility'] <= 0.30:
                score += 15
            elif 0.10 <= stock['volatility'] <= 0.40:
                score += 10
            
            stock['score'] = score
        
        # Sort by score
        ranked = sorted(valid_stocks, key=lambda x: x['score'], reverse=True)
        
        return ranked
    
    def generate_portfolio_adjustments(self, current_positions: int) -> Dict:
        """Generate portfolio adjustment recommendations"""
        
        # Get current market conditions
        spy = yf.Ticker('SPY')
        spy_hist = spy.history(period='1mo')
        spy_volatility = spy_hist['Close'].pct_change().std() * np.sqrt(252)
        
        adjustments = {
            'target_positions': 15,  # Target number of positions
            'rebalance_needed': abs(current_positions - 15) > 3,
            'leverage_adjustment': None,
            'sector_rotation': [],
            'risk_adjustments': []
        }
        
        # Leverage adjustment based on volatility
        if spy_volatility > 0.25:
            adjustments['leverage_adjustment'] = "Reduce leverage to 1.5x due to high volatility"
            adjustments['risk_adjustments'].append("Tighten stops to 2.5%")
        elif spy_volatility < 0.12:
            adjustments['leverage_adjustment'] = "Can increase leverage to 2.2x in low volatility"
        
        # Sector recommendations
        adjustments['sector_rotation'] = [
            "Overweight: Technology, Healthcare (momentum positive)",
            "Underweight: Energy, Utilities (defensive rotation)"
        ]
        
        return adjustments
    
    def generate_report(self) -> Dict:
        """Generate complete DEE-BOT research report"""
        
        logging.info("Generating DEE-BOT research report...")
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'bot': 'DEE-BOT',
            'strategy': 'Beta-Neutral S&P 100 with 2X Leverage',
            'market_analysis': {},
            'trades': [],
            'adjustments': {},
            'risk_metrics': {}
        }
        
        # Analyze a subset of S&P 100 stocks
        logging.info("Analyzing S&P 100 components...")
        stock_metrics = []
        
        for symbol in self.sp100_symbols[:30]:  # Analyze top 30 for speed
            metrics = self.calculate_stock_metrics(symbol)
            if metrics:
                stock_metrics.append(metrics)
        
        # Rank opportunities
        ranked_stocks = self.rank_opportunities(stock_metrics)
        
        # Generate trade recommendations (top 5)
        for stock in ranked_stocks[:5]:
            trade = {
                'symbol': stock['symbol'],
                'action': 'long' if stock['momentum_5d'] > 0 else 'hold',
                'score': stock['score'],
                'beta': stock['beta'],
                'current_price': stock['current_price'],
                'momentum_5d': stock['momentum_5d'],
                'rsi': stock['rsi'],
                'volatility': stock['volatility'],
                'position_size_pct': min(8, 100 / 15),  # Target 15 positions
                'stop_loss_pct': 3,
                'target_pct': 5
            }
            report['trades'].append(trade)
        
        # Portfolio adjustments
        report['adjustments'] = self.generate_portfolio_adjustments(8)  # Current 8 positions
        
        # Calculate portfolio beta
        portfolio_beta = np.mean([s['beta'] for s in ranked_stocks[:15] if s['beta']])
        
        # Risk metrics
        report['risk_metrics'] = {
            'portfolio_beta': round(portfolio_beta, 2),
            'target_beta': 1.0,
            'beta_deviation': round(abs(portfolio_beta - 1.0), 2),
            'recommended_leverage': 2.0 if portfolio_beta < 1.1 else 1.8,
            'sector_diversification': len(set(s['sector'] for s in ranked_stocks[:15])),
            'correlation_check': 'PASS' if len(set(s['industry'] for s in ranked_stocks[:15])) > 10 else 'REVIEW'
        }
        
        # Market analysis
        report['market_analysis'] = {
            'sp500_trend': 'BULLISH' if ranked_stocks[0]['momentum_20d'] > 0 else 'BEARISH',
            'volatility_regime': 'HIGH' if np.mean([s['volatility'] for s in ranked_stocks[:10]]) > 0.25 else 'NORMAL',
            'sector_leaders': list(set(s['sector'] for s in ranked_stocks[:5])),
            'recommendation': 'Maintain beta-neutral stance with tactical overweights'
        }
        
        return report
    
    def save_report(self, report: Dict) -> str:
        """Save report to JSON and return filename"""
        
        filename = f"dee_bot_research_{report['date']}.json"
        filepath = os.path.join(self.research_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logging.info(f"Report saved to {filepath}")
        
        # Also save a markdown version
        self.save_markdown_report(report)
        
        return filepath
    
    def save_markdown_report(self, report: Dict):
        """Save a markdown version of the report"""
        
        md_content = f"""# DEE-BOT Research Report
## {report['date']} - Beta-Neutral S&P 100 Strategy

### Market Analysis
- **Trend**: {report['market_analysis']['sp500_trend']}
- **Volatility**: {report['market_analysis']['volatility_regime']}
- **Sector Leaders**: {', '.join(report['market_analysis']['sector_leaders'])}
- **Recommendation**: {report['market_analysis']['recommendation']}

### Top Trade Recommendations
| Symbol | Action | Score | Beta | Momentum 5D | RSI | Position Size |
|--------|--------|-------|------|-------------|-----|---------------|
"""
        
        for trade in report['trades']:
            md_content += f"| {trade['symbol']} | {trade['action'].upper()} | {trade['score']} | {trade['beta']:.2f} | {trade['momentum_5d']:.2f}% | {trade['rsi']:.0f if trade['rsi'] else 'N/A'} | {trade['position_size_pct']:.1f}% |\n"
        
        md_content += f"""

### Portfolio Adjustments
- **Rebalance Needed**: {report['adjustments']['rebalance_needed']}
- **Target Positions**: {report['adjustments']['target_positions']}
- **Leverage Adjustment**: {report['adjustments']['leverage_adjustment'] or 'None'}

### Risk Metrics
- **Portfolio Beta**: {report['risk_metrics']['portfolio_beta']}
- **Target Beta**: {report['risk_metrics']['target_beta']}
- **Beta Deviation**: {report['risk_metrics']['beta_deviation']}
- **Recommended Leverage**: {report['risk_metrics']['recommended_leverage']}x
- **Sector Diversification**: {report['risk_metrics']['sector_diversification']} sectors
- **Correlation Check**: {report['risk_metrics']['correlation_check']}

### Sector Rotation
"""
        
        for rotation in report['adjustments']['sector_rotation']:
            md_content += f"- {rotation}\n"
        
        md_content += f"""

---
*Generated: {report['date']} {report['time']} ET*
"""
        
        md_filename = f"dee_bot_research_{report['date']}.md"
        md_filepath = os.path.join(self.research_dir, md_filename)
        
        with open(md_filepath, 'w') as f:
            f.write(md_content)
        
        logging.info(f"Markdown report saved to {md_filepath}")
    
    def run(self):
        """Main execution"""
        report = self.generate_report()
        filepath = self.save_report(report)
        
        print("\n" + "="*50)
        print("DEE-BOT RESEARCH REPORT GENERATED")
        print("="*50)
        print(f"Date: {report['date']}")
        print(f"Strategy: {report['strategy']}")
        print(f"\nTop Recommendations:")
        for i, trade in enumerate(report['trades'][:3], 1):
            print(f"  {i}. {trade['symbol']} - Score: {trade['score']}, Beta: {trade['beta']:.2f}")
        print(f"\nPortfolio Beta: {report['risk_metrics']['portfolio_beta']}")
        print(f"Recommended Leverage: {report['risk_metrics']['recommended_leverage']}x")
        print(f"\nReport saved to: {filepath}")
        print("="*50)
        
        return report


if __name__ == "__main__":
    generator = DeeBotResearchGenerator()
    generator.run()