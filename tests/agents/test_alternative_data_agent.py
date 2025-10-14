"""
Comprehensive tests for Alternative Data Agent
Tests alternative data analysis, options flow, social sentiment, and signal generation
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.alternative_data_agent import AlternativeDataAgent, EnhancedMultiAgentSystem


class TestAlternativeDataAgentInit:
    """Test alternative data agent initialization"""

    def test_agent_initialization_default(self):
        """Test agent initializes with default parameters"""
        agent = AlternativeDataAgent()

        assert agent.name == "Alternative Data Agent"
        assert agent.weight == 0.20
        assert hasattr(agent, 'aggregator')
        assert hasattr(agent, 'reddit_scanner')
        assert hasattr(agent, 'options_tracker')
        assert agent.cache == {}
        assert agent.cache_duration == 3600

    def test_agent_has_required_data_sources(self):
        """Test agent has all required data source objects"""
        agent = AlternativeDataAgent()

        assert agent.aggregator is not None
        assert agent.reddit_scanner is not None
        assert agent.options_tracker is not None

    def test_cache_initialization(self):
        """Test cache is properly initialized"""
        agent = AlternativeDataAgent()

        assert isinstance(agent.cache, dict)
        assert len(agent.cache) == 0
        assert isinstance(agent.cache_duration, int)

    def test_weight_in_valid_range(self):
        """Test agent weight is in valid range (0-1)"""
        agent = AlternativeDataAgent()

        assert 0 <= agent.weight <= 1
        assert agent.weight == 0.20


class TestScoreCalculation:
    """Test score calculation from alternative data"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_calculate_score_neutral_default(self, agent):
        """Test score defaults to neutral (50) with no data"""
        score = agent._calculate_score(None, None, None, None)

        assert score == 50

    def test_calculate_score_with_composite(self, agent):
        """Test score calculation with composite score"""
        analysis = {'composite_score': 70}

        score = agent._calculate_score(analysis, None, None, None)

        # 50 * 0.6 + 70 * 0.4 = 30 + 28 = 58
        assert 56 <= score <= 60

    def test_calculate_score_very_bullish_options(self, agent):
        """Test score with very bullish options flow"""
        options_sentiment = {'sentiment': 'VERY_BULLISH'}

        score = agent._calculate_score(None, options_sentiment, None, None)

        # 50 * 0.7 + 90 * 0.3 = 35 + 27 = 62
        assert 60 <= score <= 65

    def test_calculate_score_very_bearish_options(self, agent):
        """Test score with very bearish options flow"""
        options_sentiment = {'sentiment': 'VERY_BEARISH'}

        score = agent._calculate_score(None, options_sentiment, None, None)

        # 50 * 0.7 + 10 * 0.3 = 35 + 3 = 38
        assert 35 <= score <= 40

    def test_calculate_score_bullish_options(self, agent):
        """Test score with bullish options flow"""
        options_sentiment = {'sentiment': 'BULLISH'}

        score = agent._calculate_score(None, options_sentiment, None, None)

        # 50 * 0.7 + 70 * 0.3 = 35 + 21 = 56
        assert 54 <= score <= 58

    def test_calculate_score_bearish_options(self, agent):
        """Test score with bearish options flow"""
        options_sentiment = {'sentiment': 'BEARISH'}

        score = agent._calculate_score(None, options_sentiment, None, None)

        # 50 * 0.7 + 30 * 0.3 = 35 + 9 = 44
        assert 42 <= score <= 46

    def test_calculate_score_with_reddit_sentiment(self, agent):
        """Test score with Reddit sentiment"""
        reddit_data = {'sentiment_score': 80}

        score = agent._calculate_score(None, None, reddit_data, None)

        # 50 * 0.8 + 80 * 0.2 = 40 + 16 = 56
        assert 54 <= score <= 58

    def test_calculate_score_near_support(self, agent):
        """Test score adjustment when near support level"""
        gamma_levels = {
            'current_price': 100,
            'support_levels': [99.5],  # Within 0.5% (< 2%)
            'resistance_levels': [105]
        }

        score = agent._calculate_score(None, None, None, gamma_levels)

        # Base 50 + 5 for near support = 55
        assert score >= 55

    def test_calculate_score_near_resistance(self, agent):
        """Test score adjustment when near resistance level"""
        gamma_levels = {
            'current_price': 100,
            'support_levels': [95],
            'resistance_levels': [100.5]  # Within 0.5% (< 2%)
        }

        score = agent._calculate_score(None, None, None, gamma_levels)

        # Base 50 - 5 for near resistance = 45
        assert score <= 45

    def test_calculate_score_combined_signals(self, agent):
        """Test score with all signals combined"""
        analysis = {'composite_score': 80}
        options_sentiment = {'sentiment': 'VERY_BULLISH'}
        reddit_data = {'sentiment_score': 85}
        gamma_levels = {
            'current_price': 100,
            'support_levels': [99.5],
            'resistance_levels': [105]
        }

        score = agent._calculate_score(analysis, options_sentiment, reddit_data, gamma_levels)

        # Should be highly bullish
        assert score >= 70

    def test_calculate_score_bounded_0_100(self, agent):
        """Test score is always bounded between 0 and 100"""
        # Try to create extreme bullish score
        analysis = {'composite_score': 100}
        options_sentiment = {'sentiment': 'VERY_BULLISH'}
        reddit_data = {'sentiment_score': 100}

        score = agent._calculate_score(analysis, options_sentiment, reddit_data, None)

        assert 0 <= score <= 100


class TestSignalGeneration:
    """Test trading signal generation from scores"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_get_signal_strong_buy(self, agent):
        """Test strong buy signal for high scores"""
        assert agent._get_signal(75) == "STRONG_BUY"
        assert agent._get_signal(90) == "STRONG_BUY"
        assert agent._get_signal(100) == "STRONG_BUY"

    def test_get_signal_buy(self, agent):
        """Test buy signal for moderately high scores"""
        assert agent._get_signal(60) == "BUY"
        assert agent._get_signal(65) == "BUY"
        assert agent._get_signal(74) == "BUY"

    def test_get_signal_hold(self, agent):
        """Test hold signal for neutral scores"""
        assert agent._get_signal(41) == "HOLD"
        assert agent._get_signal(50) == "HOLD"
        assert agent._get_signal(59) == "HOLD"

    def test_get_signal_sell(self, agent):
        """Test sell signal for moderately low scores"""
        assert agent._get_signal(26) == "SELL"
        assert agent._get_signal(35) == "SELL"
        assert agent._get_signal(40) == "SELL"

    def test_get_signal_strong_sell(self, agent):
        """Test strong sell signal for very low scores"""
        assert agent._get_signal(0) == "STRONG_SELL"
        assert agent._get_signal(15) == "STRONG_SELL"
        assert agent._get_signal(25) == "STRONG_SELL"

    def test_get_signal_boundary_values(self, agent):
        """Test signal generation at boundary values"""
        assert agent._get_signal(59.9) == "HOLD"
        assert agent._get_signal(60.0) == "BUY"
        assert agent._get_signal(74.9) == "BUY"
        assert agent._get_signal(75.0) == "STRONG_BUY"


class TestConfidenceCalculation:
    """Test confidence level calculations"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_confidence_no_analysis(self, agent):
        """Test confidence with no analysis data"""
        confidence = agent._calculate_confidence(None)

        assert confidence == 0.3

    def test_confidence_base_level(self, agent):
        """Test base confidence level"""
        analysis = {}

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.3  # Empty analysis returns base confidence

    def test_confidence_with_unusual_activity_low(self, agent):
        """Test confidence with few unusual activities"""
        analysis = {
            'unusual_activity': ['flag1']
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.5  # Base only

    def test_confidence_with_unusual_activity_medium(self, agent):
        """Test confidence with moderate unusual activities"""
        analysis = {
            'unusual_activity': ['flag1', 'flag2']
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.6  # Base + 0.1

    def test_confidence_with_unusual_activity_high(self, agent):
        """Test confidence with many unusual activities"""
        analysis = {
            'unusual_activity': ['flag1', 'flag2', 'flag3']
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.7  # Base + 0.2

    def test_confidence_aligned_buy_signals(self, agent):
        """Test confidence boost when all signals are buy"""
        analysis = {
            'signals': [
                {'type': 'BUY'},
                {'type': 'STRONG_BUY'}
            ]
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.7  # Base + 0.2 for alignment

    def test_confidence_aligned_sell_signals(self, agent):
        """Test confidence boost when all signals are sell"""
        analysis = {
            'signals': [
                {'type': 'SELL'},
                {'type': 'STRONG_SELL'}
            ]
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.7  # Base + 0.2 for alignment

    def test_confidence_mixed_signals(self, agent):
        """Test confidence without boost for mixed signals"""
        analysis = {
            'signals': [
                {'type': 'BUY'},
                {'type': 'SELL'}
            ]
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence == 0.5  # Base only, no alignment bonus

    def test_confidence_max_capped_at_1(self, agent):
        """Test confidence is capped at 1.0"""
        analysis = {
            'unusual_activity': ['flag1', 'flag2', 'flag3', 'flag4'],
            'signals': [
                {'type': 'STRONG_BUY'},
                {'type': 'BUY'},
                {'type': 'BUY'}
            ]
        }

        confidence = agent._calculate_confidence(analysis)

        assert confidence <= 1.0


class TestRedditSentiment:
    """Test Reddit sentiment analysis"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_get_reddit_sentiment_structure(self, agent):
        """Test Reddit sentiment returns correct structure"""
        result = agent._get_reddit_sentiment("AAPL")

        assert 'sentiment' in result
        assert 'sentiment_score' in result
        assert 'mentions' in result
        assert 'trending' in result

    def test_get_reddit_sentiment_defaults(self, agent):
        """Test Reddit sentiment returns neutral defaults"""
        result = agent._get_reddit_sentiment("AAPL")

        assert result['sentiment'] == 'neutral'
        assert result['sentiment_score'] == 50
        assert result['mentions'] == 0
        assert result['trending'] is False

    def test_get_reddit_sentiment_data_types(self, agent):
        """Test Reddit sentiment data types"""
        result = agent._get_reddit_sentiment("TSLA")

        assert isinstance(result['sentiment'], str)
        assert isinstance(result['sentiment_score'], int)
        assert isinstance(result['mentions'], int)
        assert isinstance(result['trending'], bool)


class TestKeyInsights:
    """Test key insights extraction"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_extract_key_insights_empty(self, agent):
        """Test insights extraction with no data"""
        insights = agent._extract_key_insights(None, None, None)

        assert isinstance(insights, list)

    def test_extract_key_insights_unusual_activity(self, agent):
        """Test insights from unusual activity"""
        analysis = {
            'unusual_activity': ['High volume spike', 'Institutional buying', 'News catalyst']
        }

        insights = agent._extract_key_insights(analysis, None, None)

        assert len(insights) >= 1
        assert any('Unusual' in insight for insight in insights)

    def test_extract_key_insights_options_flow(self, agent):
        """Test insights from large options flow"""
        options_sentiment = {
            'sentiment': 'BULLISH',
            'total_premium': 1000000
        }

        insights = agent._extract_key_insights(None, options_sentiment, None)

        assert len(insights) >= 1
        assert any('options flow' in insight.lower() for insight in insights)

    def test_extract_key_insights_social_spike(self, agent):
        """Test insights from social volume spike"""
        analysis = {
            'data_sources': {
                'social_volume': {
                    'is_spiking': True,
                    'spike_ratio': 5.2
                }
            }
        }

        insights = agent._extract_key_insights(analysis, None, None)

        assert len(insights) >= 1
        assert any('Social volume' in insight for insight in insights)

    def test_extract_key_insights_dark_pool(self, agent):
        """Test insights from high dark pool activity"""
        analysis = {
            'data_sources': {
                'dark_pool': {
                    'dark_pool_percent': 45,
                    'net_sentiment': 'bullish'
                }
            }
        }

        insights = agent._extract_key_insights(analysis, None, None)

        assert len(insights) >= 1
        assert any('dark pool' in insight.lower() for insight in insights)

    def test_extract_key_insights_max_5(self, agent):
        """Test insights are limited to top 5"""
        analysis = {
            'unusual_activity': ['flag1', 'flag2', 'flag3', 'flag4', 'flag5', 'flag6'],
            'data_sources': {
                'social_volume': {'is_spiking': True, 'spike_ratio': 3.0},
                'dark_pool': {'dark_pool_percent': 45, 'net_sentiment': 'bullish'}
            }
        }
        options_sentiment = {'sentiment': 'BULLISH', 'total_premium': 1000000}

        insights = agent._extract_key_insights(analysis, options_sentiment, None)

        assert len(insights) <= 5


class TestDefaultResult:
    """Test default result generation"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_default_result_structure(self, agent):
        """Test default result has correct structure"""
        result = agent._default_result("AAPL")

        assert 'symbol' in result
        assert 'score' in result
        assert 'signal' in result
        assert 'confidence' in result
        assert 'alternative_data' in result
        assert 'key_insights' in result

    def test_default_result_values(self, agent):
        """Test default result has neutral values"""
        result = agent._default_result("TSLA")

        assert result['symbol'] == "TSLA"
        assert result['score'] == 50
        assert result['signal'] == 'HOLD'
        assert result['confidence'] == 0.3
        assert isinstance(result['alternative_data'], dict)
        assert isinstance(result['key_insights'], list)

    def test_default_result_insights_message(self, agent):
        """Test default result includes appropriate message"""
        result = agent._default_result("NVDA")

        assert len(result['key_insights']) > 0
        assert 'Limited' in result['key_insights'][0] or 'data' in result['key_insights'][0].lower()


class TestCaching:
    """Test caching mechanism"""

    @pytest.fixture
    def agent(self):
        return AlternativeDataAgent()

    def test_cache_initially_empty(self, agent):
        """Test cache is empty on initialization"""
        assert len(agent.cache) == 0

    def test_cache_stores_results(self, agent):
        """Test cache stores analysis results"""
        symbol = "AAPL"
        result = {'score': 75, 'signal': 'BUY'}

        agent.cache[symbol] = (datetime.now(), result)

        assert symbol in agent.cache
        cached_time, cached_data = agent.cache[symbol]
        assert cached_data == result

    def test_cache_duration_set(self, agent):
        """Test cache duration is properly set"""
        assert agent.cache_duration == 3600  # 1 hour in seconds


class TestEnhancedMultiAgentSystemLogic:
    """Test enhanced multi-agent system logic (without full initialization)"""

    def test_consensus_signal_strong_buy(self):
        """Test consensus signal for high score"""
        # Test the logic directly without initializing the full system
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            assert system._get_consensus_signal(75) == "STRONG_BUY"

    def test_consensus_signal_buy(self):
        """Test consensus signal for moderately high score"""
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            assert system._get_consensus_signal(60) == "BUY"

    def test_consensus_signal_hold(self):
        """Test consensus signal for neutral score"""
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            assert system._get_consensus_signal(50) == "HOLD"

    def test_consensus_signal_sell(self):
        """Test consensus signal for low score"""
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            assert system._get_consensus_signal(35) == "SELL"

    def test_consensus_signal_strong_sell(self):
        """Test consensus signal for very low score"""
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            assert system._get_consensus_signal(25) == "STRONG_SELL"

    def test_calculate_consensus_with_results(self):
        """Test consensus calculation with agent results"""
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            system.weights = {
                'fundamental': 0.20,
                'technical': 0.20,
                'alternative': 0.20
            }

            results = {
                'fundamental': {'score': 70},
                'technical': {'score': 60},
                'alternative': {'score': 80}
            }

            consensus = system._calculate_consensus(results)

            assert 60 <= consensus <= 75  # Weighted average

    def test_calculate_consensus_no_results(self):
        """Test consensus defaults to neutral with no results"""
        with patch.object(EnhancedMultiAgentSystem, '__init__', lambda x: None):
            system = EnhancedMultiAgentSystem()
            system.weights = {}

            consensus = system._calculate_consensus({})

            assert consensus == 50


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
