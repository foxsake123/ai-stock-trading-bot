"""
S&P 100 Scanner Agent for DEE-BOT
Scans and ranks S&P 100 stocks based on multi-agent consensus
"""

import sys
sys.path.append('../config')
from sp100_universe import SP100_UNIVERSE, SECTOR_LIMITS, SCREENING_CRITERIA
from datetime import datetime
import json
from typing import Dict, List, Tuple

class SP100Scanner:
    """Scanner for S&P 100 universe with multi-agent analysis"""
    
    def __init__(self):
        self.universe = SP100_UNIVERSE
        self.sector_limits = SECTOR_LIMITS
        self.screening_criteria = SCREENING_CRITERIA
        self.scan_results = []
        
    def scan_universe(self, market_data: Dict) -> List[Dict]:
        """
        Scan entire S&P 100 universe and rank stocks
        
        Args:
            market_data: Dictionary with current market data for all stocks
            
        Returns:
            List of ranked stock recommendations
        """
        scan_timestamp = datetime.now().isoformat()
        ranked_stocks = []
        
        print(f"\n[SP100 SCANNER] Scanning {len(self.universe)} stocks...")
        print("=" * 60)
        
        # Scan each stock in universe
        for ticker, info in self.universe.items():
            if ticker in ['SPY', 'QQQ']:  # Skip ETFs in main scan
                continue
                
            stock_data = market_data.get(ticker, {})
            if not stock_data:
                continue
                
            # Multi-agent scoring
            score = self._calculate_multi_agent_score(ticker, stock_data)
            
            if score['composite_score'] >= 0.65:  # Minimum 65% consensus
                ranked_stocks.append({
                    'ticker': ticker,
                    'name': info['name'],
                    'sector': info['sector'],
                    'composite_score': score['composite_score'],
                    'agent_scores': score,
                    'price': stock_data.get('price', 0),
                    'volume': stock_data.get('volume', 0),
                    'recommendation': self._get_recommendation(score['composite_score'])
                })
        
        # Sort by composite score
        ranked_stocks.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Apply sector diversification limits
        diversified_picks = self._apply_sector_limits(ranked_stocks)
        
        self.scan_results = {
            'scan_timestamp': scan_timestamp,
            'total_scanned': len(self.universe),
            'stocks_passing_filter': len(ranked_stocks),
            'top_picks': diversified_picks[:20],  # Top 20 opportunities
            'sector_distribution': self._get_sector_distribution(diversified_picks)
        }
        
        return diversified_picks
    
    def _calculate_multi_agent_score(self, ticker: str, data: Dict) -> Dict:
        """Calculate multi-agent consensus score for a stock"""
        
        scores = {
            'fundamental': self._fundamental_score(data),
            'technical': self._technical_score(data),
            'sentiment': self._sentiment_score(data),
            'momentum': self._momentum_score(data),
            'value': self._value_score(data),
            'quality': self._quality_score(data),
            'risk': self._risk_score(data)
        }
        
        # Weighted average of all agent scores
        weights = {
            'fundamental': 0.25,
            'technical': 0.20,
            'sentiment': 0.15,
            'momentum': 0.15,
            'value': 0.10,
            'quality': 0.10,
            'risk': 0.05
        }
        
        composite = sum(scores[agent] * weights[agent] for agent in scores)
        scores['composite_score'] = composite
        
        return scores
    
    def _fundamental_score(self, data: Dict) -> float:
        """Calculate fundamental analysis score"""
        score = 0.5  # Base score
        
        # Revenue growth
        if data.get('revenue_growth', 0) > 0.10:  # >10% growth
            score += 0.15
        elif data.get('revenue_growth', 0) > 0.05:  # >5% growth
            score += 0.10
            
        # Earnings growth
        if data.get('earnings_growth', 0) > 0.15:  # >15% growth
            score += 0.15
        elif data.get('earnings_growth', 0) > 0.08:  # >8% growth
            score += 0.10
            
        # Profit margins
        if data.get('net_margin', 0) > 0.15:  # >15% net margin
            score += 0.10
            
        # ROE
        if data.get('roe', 0) > 0.20:  # >20% ROE
            score += 0.10
            
        return min(score, 1.0)
    
    def _technical_score(self, data: Dict) -> float:
        """Calculate technical analysis score"""
        score = 0.5  # Base score
        
        # Price above moving averages
        if data.get('price', 0) > data.get('ma_50', 0):
            score += 0.15
        if data.get('price', 0) > data.get('ma_200', 0):
            score += 0.15
            
        # RSI in favorable range
        rsi = data.get('rsi', 50)
        if 30 < rsi < 70:  # Not overbought/oversold
            score += 0.10
        if 40 < rsi < 60:  # Neutral momentum
            score += 0.05
            
        # MACD signal
        if data.get('macd_signal', '') == 'bullish':
            score += 0.10
            
        return min(score, 1.0)
    
    def _sentiment_score(self, data: Dict) -> float:
        """Calculate sentiment analysis score"""
        score = 0.5  # Base score
        
        # News sentiment
        news_sentiment = data.get('news_sentiment', 0)
        if news_sentiment > 0.6:
            score += 0.20
        elif news_sentiment > 0.3:
            score += 0.10
            
        # Social media sentiment
        social_sentiment = data.get('social_sentiment', 0)
        if social_sentiment > 0.6:
            score += 0.15
        elif social_sentiment > 0.3:
            score += 0.08
            
        # Analyst ratings
        analyst_score = data.get('analyst_consensus', 0)
        if analyst_score > 4.0:  # Strong Buy
            score += 0.15
        elif analyst_score > 3.5:  # Buy
            score += 0.10
            
        return min(score, 1.0)
    
    def _momentum_score(self, data: Dict) -> float:
        """Calculate momentum score"""
        score = 0.5  # Base score
        
        # Price momentum (various timeframes)
        if data.get('return_1m', 0) > 0.05:  # >5% monthly return
            score += 0.15
        if data.get('return_3m', 0) > 0.10:  # >10% quarterly return
            score += 0.15
        if data.get('return_6m', 0) > 0.15:  # >15% semi-annual return
            score += 0.10
            
        # Volume momentum
        if data.get('volume_ratio', 1.0) > 1.5:  # 50% above avg volume
            score += 0.10
            
        return min(score, 1.0)
    
    def _value_score(self, data: Dict) -> float:
        """Calculate value score"""
        score = 0.5  # Base score
        
        # P/E ratio
        pe = data.get('pe_ratio', 999)
        if 0 < pe < 15:  # Low P/E
            score += 0.20
        elif 15 <= pe < 25:  # Moderate P/E
            score += 0.10
            
        # P/B ratio
        pb = data.get('pb_ratio', 999)
        if 0 < pb < 1.5:  # Trading below 1.5x book
            score += 0.15
            
        # PEG ratio
        peg = data.get('peg_ratio', 999)
        if 0 < peg < 1.0:  # PEG < 1 (undervalued growth)
            score += 0.15
            
        return min(score, 1.0)
    
    def _quality_score(self, data: Dict) -> float:
        """Calculate quality score"""
        score = 0.5  # Base score
        
        # Debt metrics
        debt_to_equity = data.get('debt_to_equity', 999)
        if debt_to_equity < 0.5:  # Low debt
            score += 0.15
        elif debt_to_equity < 1.0:  # Moderate debt
            score += 0.08
            
        # Free cash flow
        if data.get('fcf_yield', 0) > 0.05:  # >5% FCF yield
            score += 0.15
            
        # Earnings quality
        if data.get('earnings_consistency', 0) > 0.8:  # Consistent earnings
            score += 0.10
            
        # Market cap (prefer large caps for quality)
        if data.get('market_cap', 0) > 100_000_000_000:  # >$100B
            score += 0.10
            
        return min(score, 1.0)
    
    def _risk_score(self, data: Dict) -> float:
        """Calculate risk score (higher = lower risk = better)"""
        score = 0.5  # Base score
        
        # Beta (prefer lower volatility)
        beta = data.get('beta', 1.0)
        if beta < 0.8:
            score += 0.20
        elif beta < 1.2:
            score += 0.10
            
        # Volatility
        volatility = data.get('volatility_30d', 999)
        if volatility < 0.20:  # <20% annualized vol
            score += 0.15
        elif volatility < 0.30:  # <30% annualized vol
            score += 0.08
            
        # Maximum drawdown
        max_dd = data.get('max_drawdown_1y', -999)
        if max_dd > -0.15:  # Less than 15% drawdown
            score += 0.15
            
        return min(score, 1.0)
    
    def _get_recommendation(self, score: float) -> str:
        """Convert score to recommendation"""
        if score >= 0.80:
            return "STRONG BUY"
        elif score >= 0.70:
            return "BUY"
        elif score >= 0.60:
            return "WEAK BUY"
        elif score >= 0.50:
            return "HOLD"
        else:
            return "AVOID"
    
    def _apply_sector_limits(self, stocks: List[Dict]) -> List[Dict]:
        """Apply sector diversification limits"""
        diversified = []
        sector_allocations = {sector: 0 for sector in SECTOR_LIMITS}
        
        for stock in stocks:
            sector = stock['sector']
            if sector_allocations[sector] < SECTOR_LIMITS[sector]:
                diversified.append(stock)
                # Assume equal weight for simplicity
                sector_allocations[sector] += 1 / len(stocks)
                
                if len(diversified) >= 30:  # Max 30 positions
                    break
        
        return diversified
    
    def _get_sector_distribution(self, stocks: List[Dict]) -> Dict:
        """Calculate sector distribution of selected stocks"""
        distribution = {}
        for stock in stocks:
            sector = stock['sector']
            distribution[sector] = distribution.get(sector, 0) + 1
        return distribution
    
    def get_top_opportunities(self, n: int = 10) -> List[Dict]:
        """Get top N opportunities from last scan"""
        if self.scan_results:
            return self.scan_results['top_picks'][:n]
        return []
    
    def save_scan_results(self, filename: str = None):
        """Save scan results to file"""
        if not filename:
            filename = f"sp100_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.scan_results, f, indent=2)
        
        print(f"\n[SAVED] Scan results saved to {filename}")
        return filename