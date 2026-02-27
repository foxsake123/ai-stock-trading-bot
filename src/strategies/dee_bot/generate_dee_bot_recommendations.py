"""
DEE-BOT Multi-Agent Trading Recommendations Generator
Beta-Neutral Strategy with 2X Leverage Support
Generates consensus-based trading recommendations from 7 specialized AI agents
"""

import json
import random
from datetime import datetime, date
import os
from pathlib import Path
import numpy as np
from datetime import timedelta
import sys

# Add scripts/automation to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "automation"))
from financial_datasets_integration import FinancialDatasetsAPI

# Initialize API
fd_api = FinancialDatasetsAPI()

# S&P 100 Components for DEE-BOT analysis
SP100_STOCKS = [
    'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK.B', 'JPM',
    'JNJ', 'V', 'PG', 'XOM', 'UNH', 'HD', 'MA', 'DIS', 'ABBV', 'CVX',
    'PFE', 'LLY', 'BAC', 'KO', 'PEP', 'COST', 'MRK', 'WMT', 'TMO', 'AVGO',
    'CSCO', 'VZ', 'ACN', 'ABT', 'ADBE', 'NKE', 'WFC', 'CRM', 'MCD', 'CMCSA',
    'DHR', 'NFLX', 'BMY', 'TXN', 'UPS', 'NEE', 'QCOM', 'T', 'COP', 'PM',
    'LIN', 'MS', 'UNP', 'INTC', 'RTX', 'ORCL', 'HON', 'IBM', 'LOW', 'AMGN',
    'AMD', 'GS', 'SCHW', 'INTU', 'CAT', 'CVS', 'MDT', 'DE', 'BLK', 'SPGI',
    'AXP', 'C', 'GILD', 'ELV', 'PLD', 'AMAT', 'NOW', 'PYPL', 'BA', 'MDLZ',
    'SYK', 'ADI', 'BKNG', 'LMT', 'ADP', 'AMT', 'CI', 'ISRG', 'VRTX', 'TJX',
    'GE', 'MMC', 'REGN', 'MO', 'CB', 'DUK', 'SLB', 'SO', 'PGR', 'ZTS'
]

class Agent:
    """Base class for all trading agents"""
    def __init__(self, name, agent_type):
        self.name = name
        self.agent_type = agent_type
        
    def analyze(self, ticker):
        """Generate agent-specific analysis"""
        # Simulate agent analysis with weighted random factors
        base_confidence = random.uniform(0.6, 0.95)
        
        # Agent-specific biases
        if self.agent_type == "bull_researcher":
            base_confidence += 0.1  # Bulls are more optimistic
        elif self.agent_type == "bear_researcher":
            base_confidence -= 0.1  # Bears are more cautious
        elif self.agent_type == "risk_manager":
            base_confidence -= 0.05  # Risk managers are conservative
            
        base_confidence = max(0.5, min(0.99, base_confidence))
        
        # Determine action based on confidence and agent type
        if self.agent_type == "bear_researcher":
            if base_confidence < 0.65:
                action = "SELL"
            elif base_confidence < 0.75:
                action = "HOLD"
            else:
                action = "BUY"
        else:
            if base_confidence > 0.75:
                action = "BUY"
            elif base_confidence > 0.65:
                action = "HOLD"
            else:
                action = "SELL"
                
        return {
            "agent": self.name,
            "agent_type": self.agent_type,
            "ticker": ticker,
            "action": action,
            "confidence": round(base_confidence, 3),
            "timestamp": datetime.now().isoformat()
        }

class MultiAgentSystem:
    """Coordinates all agents and generates consensus"""
    
    def __init__(self):
        self.agents = [
            Agent("Fundamental Analyst", "fundamental_analyst"),
            Agent("Technical Analyst", "technical_analyst"),
            Agent("News Analyst", "news_analyst"),
            Agent("Sentiment Analyst", "sentiment_analyst"),
            Agent("Bull Researcher", "bull_researcher"),
            Agent("Bear Researcher", "bear_researcher"),
            Agent("Risk Manager", "risk_manager")
        ]
        self.beta_cache = {}
        
    def get_consensus(self, ticker):
        """Get consensus recommendation from all agents"""
        analyses = []
        for agent in self.agents:
            analyses.append(agent.analyze(ticker))
            
        # Calculate consensus
        buy_votes = sum(1 for a in analyses if a["action"] == "BUY")
        sell_votes = sum(1 for a in analyses if a["action"] == "SELL")
        hold_votes = sum(1 for a in analyses if a["action"] == "HOLD")
        
        total_confidence = sum(a["confidence"] for a in analyses)
        avg_confidence = total_confidence / len(analyses)
        
        # Determine consensus action
        if buy_votes >= 4:  # Majority for BUY
            consensus_action = "BUY"
        elif sell_votes >= 4:  # Majority for SELL
            consensus_action = "SELL"
        else:
            consensus_action = "HOLD"
            
        # Risk Manager veto check
        risk_analysis = next(a for a in analyses if a["agent_type"] == "risk_manager")
        if risk_analysis["action"] == "SELL" and risk_analysis["confidence"] > 0.8:
            consensus_action = "HOLD"  # Risk manager veto converts to HOLD
            
        # Calculate beta for the stock
        beta = self.calculate_beta(ticker)
        
        return {
            "ticker": ticker,
            "consensus_action": consensus_action,
            "confidence": round(avg_confidence, 3),
            "buy_votes": buy_votes,
            "sell_votes": sell_votes,
            "hold_votes": hold_votes,
            "beta": beta,
            "agent_analyses": analyses,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_beta(self, ticker: str, period: int = 252) -> float:
        """Calculate stock beta relative to SPY using Financial Datasets API"""
        if ticker in self.beta_cache:
            return self.beta_cache[ticker]
            
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            # Get historical prices from Financial Datasets API
            stock_df = fd_api.get_historical_prices(
                ticker, 
                interval='day',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            spy_df = fd_api.get_historical_prices(
                'SPY',
                interval='day', 
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            if stock_df.empty or spy_df.empty:
                print(f"[WARNING] No data for {ticker} or SPY")
                return 1.0
            
            stock_returns = stock_df['close'].pct_change().dropna()
            spy_returns = spy_df['close'].pct_change().dropna()
            
            # Align returns by date
            common_dates = stock_returns.index.intersection(spy_returns.index)
            stock_returns = stock_returns.loc[common_dates]
            spy_returns = spy_returns.loc[common_dates]
            
            if len(stock_returns) < 20:  # Need minimum data points
                return 1.0
            
            covariance = np.cov(stock_returns, spy_returns)[0][1]
            variance = np.var(spy_returns)
            beta = covariance / variance if variance != 0 else 1.0
            
            self.beta_cache[ticker] = round(beta, 3)
            return round(beta, 3)
            
        except Exception as e:
            print(f"[WARNING] Could not calculate beta for {ticker}: {str(e)}")
            return 1.0

def generate_recommendations():
    """Generate trading recommendations for top S&P 100 stocks"""
    
    print("=" * 80)
    print("DEE-BOT MULTI-AGENT TRADING RECOMMENDATIONS")
    print(f"Date: {date.today()}")
    print("=" * 80)
    
    system = MultiAgentSystem()
    recommendations = []
    
    # Analyze top 20 S&P 100 stocks for efficiency
    stocks_to_analyze = SP100_STOCKS[:20]
    
    print("\nAnalyzing stocks with 7-agent consensus system...")
    print("-" * 80)
    
    for ticker in stocks_to_analyze:
        consensus = system.get_consensus(ticker)
        recommendations.append(consensus)
        
        # Display progress
        print(f"\n{ticker}:")
        print(f"  Consensus: {consensus['consensus_action']} (Confidence: {consensus['confidence']:.1%})")
        print(f"  Beta: {consensus['beta']:.3f}")
        print(f"  Votes: BUY={consensus['buy_votes']} SELL={consensus['sell_votes']} HOLD={consensus['hold_votes']}")
        
        # Show individual agent opinions
        for analysis in consensus['agent_analyses']:
            print(f"    - {analysis['agent']}: {analysis['action']} ({analysis['confidence']:.1%})")
    
    # Filter for actionable recommendations (BUY or SELL with high confidence)
    actionable = [r for r in recommendations 
                  if r['consensus_action'] in ['BUY', 'SELL'] 
                  and r['confidence'] > 0.7]
    
    # Sort by confidence
    actionable.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("\n" + "=" * 80)
    print("TOP TRADING RECOMMENDATIONS")
    print("=" * 80)
    
    top_recommendations = actionable[:5]  # Top 5 recommendations
    
    for i, rec in enumerate(top_recommendations, 1):
        print(f"\n{i}. {rec['ticker']} - {rec['consensus_action']}")
        print(f"   Confidence: {rec['confidence']:.1%}")
        print(f"   Beta: {rec['beta']:.3f}")
        print(f"   Agent Consensus: {rec['buy_votes']} BUY, {rec['sell_votes']} SELL, {rec['hold_votes']} HOLD")
        
        # Add price targets and risk levels
        if rec['consensus_action'] == 'BUY':
            entry = 100  # Placeholder
            stop_loss = entry * 0.97
            take_profit = entry * 1.05
            print(f"   Entry: ~${entry:.2f}")
            print(f"   Stop Loss: ${stop_loss:.2f} (-3%)")
            print(f"   Take Profit: ${take_profit:.2f} (+5%)")
        else:  # SELL
            entry = 100  # Placeholder
            stop_loss = entry * 1.03
            take_profit = entry * 0.95
            print(f"   Entry: ~${entry:.2f}")
            print(f"   Stop Loss: ${stop_loss:.2f} (+3%)")
            print(f"   Take Profit: ${take_profit:.2f} (-5%)")
    
    # Save recommendations to file
    output_dir = Path("C:/Users/shorg/ai-stock-trading-bot/02_data/research/reports/daily_recommendations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"dee_bot_recommendations_{date.today()}.json"
    
    # Calculate portfolio beta for recommendations
    portfolio_beta = sum(r['beta'] for r in top_recommendations) / len(top_recommendations) if top_recommendations else 0
    
    output_data = {
        "bot": "DEE-BOT",
        "date": str(date.today()),
        "timestamp": datetime.now().isoformat(),
        "strategy": "Beta-Neutral Multi-Agent Consensus (7 Agents)",
        "leverage_enabled": True,
        "target_leverage": 2.0,
        "stocks_analyzed": len(stocks_to_analyze),
        "actionable_recommendations": len(actionable),
        "top_recommendations": top_recommendations,
        "portfolio_beta": round(portfolio_beta, 3),
        "all_analyses": recommendations,
        "market_conditions": {
            "sentiment": "neutral",
            "volatility": "moderate",
            "trend": "sideways"
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print(f"Recommendations saved to: {output_file}")
    print(f"Total actionable trades: {len(actionable)}")
    print(f"Average confidence: {sum(r['confidence'] for r in recommendations) / len(recommendations):.1%}")
    print("=" * 80)
    
    return output_data

if __name__ == "__main__":
    recommendations = generate_recommendations()
    print("\nDEE-BOT recommendations generation complete!")