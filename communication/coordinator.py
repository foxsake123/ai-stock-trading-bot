"""
Multi-Agent Coordinator
Manages consensus building between trading agents
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.fundamental_analyst import FundamentalAnalyst
from src.agents.technical_analyst import TechnicalAnalyst
from src.agents.news_analyst import NewsAnalyst
from src.agents.sentiment_analyst import SentimentAnalyst
from src.agents.bull_analyst import BullAgent  # Updated from bull_agent
from src.agents.bear_analyst import BearAgent  # Updated from bear_agent
from src.agents.risk_manager import RiskManager

class Coordinator:
    """Coordinates multiple trading agents to reach consensus"""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize coordinator with agent weights"""

        # Default weights for consensus calculation
        self.weights = weights or {
            'fundamental': 0.20,
            'technical': 0.20,
            'news': 0.15,
            'sentiment': 0.10,
            'bull': 0.15,
            'bear': 0.15,
            'risk': 0.05
        }

        # Initialize agents
        self.agents = {
            'fundamental': FundamentalAnalyst(),
            'technical': TechnicalAnalyst(),
            'news': NewsAnalyst(),
            'sentiment': SentimentAnalyst(),
            'bull': BullAgent(),
            'bear': BearAgent(),
            'risk': RiskManager()
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def analyze_stock(self, symbol: str) -> Dict:
        """
        Coordinate all agents to analyze a stock
        Returns consensus recommendation
        """
        self.logger.info(f"Starting multi-agent analysis for {symbol}")

        agent_results = {}
        total_weight = 0
        weighted_score = 0

        # Collect analysis from each agent
        for agent_name, agent in self.agents.items():
            try:
                result = agent.analyze(symbol)

                if result:
                    agent_results[agent_name] = result

                    # Convert recommendation to score
                    score = self._recommendation_to_score(result.get('recommendation', 'HOLD'))
                    confidence = result.get('confidence', 0.5)

                    # Apply weight
                    weight = self.weights.get(agent_name, 0.1)
                    weighted_score += score * confidence * weight
                    total_weight += weight

                    self.logger.info(f"{agent_name}: {result.get('recommendation')} (conf: {confidence:.2f})")

            except Exception as e:
                self.logger.error(f"Error in {agent_name} agent: {e}")
                continue

        # Calculate consensus
        if total_weight > 0:
            consensus_score = weighted_score / total_weight
        else:
            consensus_score = 0.5  # Neutral

        # Convert score back to recommendation
        recommendation = self._score_to_recommendation(consensus_score)

        # Check for risk manager veto
        if 'risk' in agent_results:
            risk_result = agent_results['risk']
            if risk_result.get('veto', False):
                self.logger.warning(f"Risk Manager VETO on {symbol}")
                recommendation = 'HOLD'
                consensus_score = 0.5

        # Compile final result
        result = {
            'symbol': symbol,
            'recommendation': recommendation,
            'confidence': abs(consensus_score - 0.5) * 2,  # Convert to 0-1 scale
            'consensus_score': consensus_score,
            'agent_results': agent_results,
            'timestamp': datetime.now().isoformat(),
            'reasoning': self._generate_reasoning(agent_results, recommendation)
        }

        self.logger.info(f"Consensus for {symbol}: {recommendation} (score: {consensus_score:.3f})")
        return result

    def _recommendation_to_score(self, recommendation: str) -> float:
        """Convert text recommendation to numeric score"""
        scores = {
            'STRONG_BUY': 1.0,
            'BUY': 0.75,
            'HOLD': 0.5,
            'SELL': 0.25,
            'STRONG_SELL': 0.0
        }
        return scores.get(recommendation.upper(), 0.5)

    def _score_to_recommendation(self, score: float) -> str:
        """Convert numeric score to recommendation"""
        if score >= 0.8:
            return 'STRONG_BUY'
        elif score >= 0.65:
            return 'BUY'
        elif score <= 0.2:
            return 'STRONG_SELL'
        elif score <= 0.35:
            return 'SELL'
        else:
            return 'HOLD'

    def _generate_reasoning(self, agent_results: Dict, recommendation: str) -> str:
        """Generate human-readable reasoning for the recommendation"""

        reasons = []

        # Collect key points from each agent
        for agent_name, result in agent_results.items():
            if 'reasoning' in result and result['reasoning']:
                reasons.append(f"{agent_name.title()}: {result['reasoning'][:100]}")

        # Create summary
        if recommendation in ['BUY', 'STRONG_BUY']:
            summary = "Bullish consensus based on: "
        elif recommendation in ['SELL', 'STRONG_SELL']:
            summary = "Bearish consensus based on: "
        else:
            summary = "Neutral consensus with mixed signals: "

        summary += "; ".join(reasons[:3])  # Top 3 reasons

        return summary[:500]  # Limit length

    def batch_analyze(self, symbols: List[str]) -> List[Dict]:
        """Analyze multiple stocks in batch"""
        results = []

        for symbol in symbols:
            try:
                result = self.analyze_stock(symbol)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
                continue

        return results

    def save_analysis(self, result: Dict, filepath: str):
        """Save analysis result to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2)
            self.logger.info(f"Analysis saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving analysis: {e}")

    def adjust_weights(self, new_weights: Dict[str, float]):
        """Adjust agent weights for consensus calculation"""
        self.weights.update(new_weights)

        # Normalize weights to sum to 1
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total

        self.logger.info(f"Updated weights: {self.weights}")

# Example usage
if __name__ == "__main__":
    coordinator = Coordinator()

    # Analyze a single stock
    result = coordinator.analyze_stock("AAPL")
    print(json.dumps(result, indent=2))

    # Batch analysis
    symbols = ["MSFT", "GOOGL", "TSLA"]
    results = coordinator.batch_analyze(symbols)

    for r in results:
        print(f"{r['symbol']}: {r['recommendation']} (confidence: {r['confidence']:.2%})")