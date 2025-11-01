"""
Alternative Data Agent - Integrates social sentiment, options flow, and insider data
This agent provides an additional signal layer for the multi-agent consensus system
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data.alternative_data_aggregator import AlternativeDataAggregator
from src.data.sources.reddit_wsb_scanner import RedditWSBScanner
from src.data.sources.options_flow_tracker import OptionsFlowTracker
import asyncio
import pandas as pd
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlternativeDataAgent:
    """Agent that analyzes alternative data sources for trading signals"""

    def __init__(self):
        self.name = "Alternative Data Agent"
        self.weight = 0.20  # 20% weight in consensus system

        # Initialize data sources
        self.aggregator = AlternativeDataAggregator()
        self.reddit_scanner = RedditWSBScanner()
        self.options_tracker = OptionsFlowTracker()

        # Cache for recent analyses
        self.cache = {}
        self.cache_duration = 3600  # 1 hour

    async def analyze(self, symbol, data=None):
        """Analyze a symbol using alternative data sources"""
        logger.info(f"{self.name} analyzing {symbol}")

        try:
            # Check cache
            if symbol in self.cache:
                cached_time, cached_data = self.cache[symbol]
                if (datetime.now() - cached_time).seconds < self.cache_duration:
                    logger.info(f"Using cached data for {symbol}")
                    return cached_data

            # Gather all alternative data
            analysis = await self.aggregator.analyze_symbol(symbol)

            # Get options flow
            unusual_options = self.options_tracker.detect_unusual_activity(symbol)
            options_sentiment = self.options_tracker.analyze_flow_sentiment(unusual_options)

            # Get Reddit sentiment (if initialized)
            reddit_data = self._get_reddit_sentiment(symbol)

            # Get gamma levels
            gamma_levels = self.options_tracker.get_gamma_levels(symbol)

            # Calculate comprehensive score
            score = self._calculate_score(analysis, options_sentiment, reddit_data, gamma_levels)

            result = {
                'symbol': symbol,
                'score': score,
                'signal': self._get_signal(score),
                'confidence': self._calculate_confidence(analysis),
                'alternative_data': {
                    'composite_score': analysis.get('composite_score', 50),
                    'unusual_activity': analysis.get('unusual_activity', []),
                    'options_flow': options_sentiment,
                    'reddit_sentiment': reddit_data,
                    'gamma_levels': gamma_levels,
                    'recommendation': analysis.get('recommendation', 'HOLD')
                },
                'key_insights': self._extract_key_insights(analysis, options_sentiment, reddit_data)
            }

            # Cache result
            self.cache[symbol] = (datetime.now(), result)

            return result

        except Exception as e:
            logger.error(f"Error in alternative data analysis for {symbol}: {e}")
            return self._default_result(symbol)

    def _calculate_score(self, analysis, options_sentiment, reddit_data, gamma_levels):
        """Calculate overall score from all alternative data"""
        score = 50  # Start neutral

        # Composite score from aggregator (40% weight)
        if analysis and 'composite_score' in analysis:
            score = score * 0.6 + analysis['composite_score'] * 0.4

        # Options flow sentiment (30% weight)
        if options_sentiment:
            options_score = 50
            if options_sentiment['sentiment'] == 'VERY_BULLISH':
                options_score = 90
            elif options_sentiment['sentiment'] == 'BULLISH':
                options_score = 70
            elif options_sentiment['sentiment'] == 'BEARISH':
                options_score = 30
            elif options_sentiment['sentiment'] == 'VERY_BEARISH':
                options_score = 10

            score = score * 0.7 + options_score * 0.3

        # Reddit sentiment (20% weight)
        if reddit_data and 'sentiment_score' in reddit_data:
            score = score * 0.8 + reddit_data['sentiment_score'] * 0.2

        # Gamma levels adjustment (10% weight)
        if gamma_levels and 'current_price' in gamma_levels:
            current = gamma_levels['current_price']

            # Check if we're near support (bullish) or resistance (bearish)
            support_distance = float('inf')
            resistance_distance = float('inf')

            for support in gamma_levels.get('support_levels', []):
                support_distance = min(support_distance, abs(current - support))

            for resistance in gamma_levels.get('resistance_levels', []):
                resistance_distance = min(resistance_distance, abs(current - resistance))

            if support_distance < resistance_distance and support_distance < current * 0.02:
                score += 5  # Near support, slightly bullish
            elif resistance_distance < support_distance and resistance_distance < current * 0.02:
                score -= 5  # Near resistance, slightly bearish

        return max(0, min(100, score))

    def _get_signal(self, score):
        """Convert score to trading signal"""
        if score >= 75:
            return "STRONG_BUY"
        elif score >= 60:
            return "BUY"
        elif score <= 25:
            return "STRONG_SELL"
        elif score <= 40:
            return "SELL"
        else:
            return "HOLD"

    def _calculate_confidence(self, analysis):
        """Calculate confidence level based on data quality and consistency"""
        if not analysis:
            return 0.3

        confidence = 0.5  # Base confidence

        # Increase confidence if multiple unusual flags
        unusual_count = len(analysis.get('unusual_activity', []))
        if unusual_count >= 3:
            confidence += 0.2
        elif unusual_count >= 2:
            confidence += 0.1

        # Increase confidence if signals align
        if 'signals' in analysis:
            signals = analysis['signals']
            if len(signals) > 1:
                # Check if all signals point same direction
                signal_types = [s.get('type', '') for s in signals]
                if all('BUY' in s for s in signal_types):
                    confidence += 0.2
                elif all('SELL' in s for s in signal_types):
                    confidence += 0.2

        return min(1.0, confidence)

    def _get_reddit_sentiment(self, symbol):
        """Get Reddit sentiment for symbol"""
        try:
            # This would need Reddit API credentials to work
            # For now, return placeholder
            return {
                'sentiment': 'neutral',
                'sentiment_score': 50,
                'mentions': 0,
                'trending': False
            }
        except Exception as e:
            logger.error(f"Error getting Reddit sentiment: {e}")
            return None

    def _extract_key_insights(self, analysis, options_sentiment, reddit_data):
        """Extract actionable insights from alternative data"""
        insights = []

        # Check for unusual activity
        if analysis and 'unusual_activity' in analysis:
            for flag in analysis['unusual_activity'][:3]:  # Top 3 flags
                insights.append(f"Unusual: {flag}")

        # Options flow insight
        if options_sentiment and options_sentiment.get('total_premium', 0) > 500000:
            sentiment = options_sentiment['sentiment']
            premium = options_sentiment['total_premium']
            insights.append(f"Heavy options flow: {sentiment} (${premium:,.0f})")

        # Social momentum
        if analysis and 'data_sources' in analysis:
            social_vol = analysis['data_sources'].get('social_volume', {})
            if social_vol.get('is_spiking'):
                ratio = social_vol.get('spike_ratio', 0)
                insights.append(f"Social volume spike: {ratio:.1f}x normal")

        # Dark pool activity
        if analysis and 'data_sources' in analysis:
            dark_pool = analysis['data_sources'].get('dark_pool', {})
            if dark_pool.get('dark_pool_percent', 0) > 40:
                pct = dark_pool['dark_pool_percent']
                sentiment = dark_pool.get('net_sentiment', 'unknown')
                insights.append(f"High dark pool: {pct}% ({sentiment})")

        return insights[:5]  # Return top 5 insights

    def _default_result(self, symbol):
        """Return default neutral result if analysis fails"""
        return {
            'symbol': symbol,
            'score': 50,
            'signal': 'HOLD',
            'confidence': 0.3,
            'alternative_data': {},
            'key_insights': ['Limited alternative data available']
        }

    def get_market_overview(self):
        """Get overall market sentiment from alternative data"""
        try:
            # Analyze major indices
            spy_analysis = asyncio.run(self.analyze('SPY'))
            qqq_analysis = asyncio.run(self.analyze('QQQ'))

            # Get market movers
            movers = asyncio.run(self.aggregator.get_market_movers())

            return {
                'timestamp': datetime.now().isoformat(),
                'market_sentiment': {
                    'SPY': spy_analysis['signal'],
                    'QQQ': qqq_analysis['signal'],
                },
                'trending_tickers': movers.get('trending_social', [])[:5],
                'unusual_options': movers.get('unusual_options', [])[:5],
                'insider_buying': movers.get('insider_buying', [])[:5]
            }
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {}

    def generate_report(self, symbols):
        """Generate comprehensive alternative data report"""
        report = []
        report.append("=" * 70)
        report.append("ALTERNATIVE DATA ANALYSIS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        for symbol in symbols:
            analysis = asyncio.run(self.analyze(symbol))

            report.append(f"Symbol: {symbol}")
            report.append(f"Score: {analysis['score']:.1f}/100")
            report.append(f"Signal: {analysis['signal']}")
            report.append(f"Confidence: {analysis['confidence']:.1%}")

            if analysis['key_insights']:
                report.append("Key Insights:")
                for insight in analysis['key_insights']:
                    report.append(f"  - {insight}")

            # Options flow details
            alt_data = analysis.get('alternative_data', {})
            if 'options_flow' in alt_data and alt_data['options_flow']:
                flow = alt_data['options_flow']
                report.append(f"Options Flow: {flow.get('sentiment', 'N/A')}")
                if flow.get('total_premium', 0) > 0:
                    report.append(f"  Premium: ${flow['total_premium']:,.0f}")
                    report.append(f"  Call/Put Ratio: {flow.get('call_put_ratio', 0):.2f}")

            report.append("-" * 40)
            report.append("")

        return "\n".join(report)

class EnhancedMultiAgentSystem:
    """Enhanced multi-agent system with alternative data integration"""

    def __init__(self):
        # Load existing agents
        from src.agents.fundamental_agent import FundamentalAgent
        from src.agents.technical_agent import TechnicalAgent
        from src.agents.news_agent import NewsAgent
        from src.agents.sentiment_agent import SentimentAgent

        self.agents = {
            'fundamental': FundamentalAgent(),
            'technical': TechnicalAgent(),
            'news': NewsAgent(),
            'sentiment': SentimentAgent(),
            'alternative': AlternativeDataAgent()  # New agent
        }

        # Updated weights with alternative data
        self.weights = {
            'fundamental': 0.20,
            'technical': 0.20,
            'news': 0.15,
            'sentiment': 0.10,
            'alternative': 0.20,  # Significant weight for alt data
            'risk': 0.15
        }

    async def analyze_with_alternative_data(self, symbol):
        """Analyze symbol with all agents including alternative data"""
        results = {}

        # Run all analyses in parallel
        tasks = []
        for name, agent in self.agents.items():
            if hasattr(agent, 'analyze'):
                tasks.append(self._run_agent(name, agent, symbol))

        agent_results = await asyncio.gather(*tasks)

        for name, result in agent_results:
            results[name] = result

        # Calculate consensus
        consensus_score = self._calculate_consensus(results)

        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'consensus_score': consensus_score,
            'consensus_signal': self._get_consensus_signal(consensus_score),
            'agent_results': results,
            'alternative_insights': results.get('alternative', {}).get('key_insights', [])
        }

    async def _run_agent(self, name, agent, symbol):
        """Run individual agent analysis"""
        try:
            result = await agent.analyze(symbol)
            return (name, result)
        except Exception as e:
            logger.error(f"Error running {name} agent: {e}")
            return (name, None)

    def _calculate_consensus(self, results):
        """Calculate weighted consensus score"""
        total_score = 0
        total_weight = 0

        for agent_name, result in results.items():
            if result and 'score' in result:
                weight = self.weights.get(agent_name, 0.1)
                total_score += result['score'] * weight
                total_weight += weight

        if total_weight > 0:
            return total_score / total_weight
        return 50  # Neutral if no data

    def _get_consensus_signal(self, score):
        """Convert consensus score to signal"""
        if score >= 70:
            return "STRONG_BUY"
        elif score >= 55:
            return "BUY"
        elif score <= 30:
            return "STRONG_SELL"
        elif score <= 45:
            return "SELL"
        else:
            return "HOLD"

# Example usage
async def main():
    """Example usage of alternative data agent"""

    # Initialize agent
    agent = AlternativeDataAgent()

    # Analyze single symbol
    result = await agent.analyze("AAPL")
    print(f"AAPL Analysis: {json.dumps(result, indent=2, default=str)}")

    # Generate report for multiple symbols
    symbols = ["AAPL", "TSLA", "NVDA", "BBAI", "SOUN"]
    report = agent.generate_report(symbols)
    print(report)

    # Test enhanced multi-agent system
    enhanced_system = EnhancedMultiAgentSystem()
    consensus = await enhanced_system.analyze_with_alternative_data("TSLA")
    print(f"\nEnhanced Consensus for TSLA:")
    print(f"Score: {consensus['consensus_score']:.1f}")
    print(f"Signal: {consensus['consensus_signal']}")
    print(f"Alternative Insights: {consensus['alternative_insights']}")

if __name__ == "__main__":
    asyncio.run(main())