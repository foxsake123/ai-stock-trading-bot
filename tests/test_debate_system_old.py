"""Tests for Bull/Bear Debate System"""

import pytest
from datetime import datetime
from src.agents.debate_system import (
    DebateSystem,
    Argument,
    DebateResult,
    debate_trade
)
from unittest.mock import Mock, patch


@pytest.fixture
def sample_recommendation():
    """Sample trade recommendation for testing"""
    return {
        'ticker': 'AAPL',
        'recommendation': {
            'action': 'BUY',
            'confidence': 0.65
        },
        'analysis': {
            'technical_score': 0.70,
            'fundamental_score': 0.75,
            'sentiment_score': 0.65,
            'valuation_score': 0.55
        },
        'risk_assessment': {
            'risk_level': 'MEDIUM',
            'max_loss': 0.15
        }
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        'price': 150.00,
        'volume': 50000000,
        'market_cap': 2500000000000
    }


@pytest.fixture
def debate_system():
    """Create debate system instance"""
    bull_agent = Mock()
    bear_agent = Mock()
    return DebateSystem(bull_agent, bear_agent)


class TestDebateSystemInitialization:
    """Test debate system initialization"""

    def test_initialization_with_agents(self):
        """Test initialization with bull and bear agents"""
        bull = Mock()
        bear = Mock()
        system = DebateSystem(bull, bear)

        assert system.bull_agent == bull
        assert system.bear_agent == bear
        assert system.max_rounds == 3
        assert system.min_confidence_for_debate == 0.55
        assert system.max_confidence_for_debate == 0.75

    def test_initialization_without_agents(self):
        """Test initialization without agents"""
        system = DebateSystem()

        assert system.bull_agent is None
        assert system.bear_agent is None
        assert system.max_rounds == 3

    def test_debate_parameters(self):
        """Test debate parameters are correctly set"""
        system = DebateSystem()

        assert system.max_rounds > 0
        assert system.min_confidence_for_debate < system.max_confidence_for_debate
        assert 0 < system.min_confidence_for_debate < 1
        assert 0 < system.max_confidence_for_debate < 1


class TestShouldDebate:
    """Test should_debate decision logic"""

    def test_should_debate_borderline_low(self, debate_system):
        """Test debate for borderline low confidence"""
        assert debate_system.should_debate(0.55) is True

    def test_should_debate_borderline_high(self, debate_system):
        """Test debate for borderline high confidence"""
        assert debate_system.should_debate(0.75) is True

    def test_should_debate_middle(self, debate_system):
        """Test debate for middle confidence"""
        assert debate_system.should_debate(0.65) is True

    def test_should_not_debate_too_low(self, debate_system):
        """Test no debate for very low confidence"""
        assert debate_system.should_debate(0.45) is False

    def test_should_not_debate_too_high(self, debate_system):
        """Test no debate for very high confidence"""
        assert debate_system.should_debate(0.85) is False

    def test_should_debate_exact_boundaries(self, debate_system):
        """Test debate at exact boundary values"""
        assert debate_system.should_debate(0.550000) is True
        assert debate_system.should_debate(0.750000) is True
        assert debate_system.should_debate(0.549999) is False
        assert debate_system.should_debate(0.750001) is False


class TestGatherBullArguments:
    """Test bull argument gathering"""

    def test_gather_strong_technical(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bull arguments with strong technical"""
        sample_recommendation['analysis']['technical_score'] = 0.75

        arguments = debate_system._gather_bull_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        assert len(arguments) > 0
        technical_args = [arg for arg in arguments if 'technical' in arg.point.lower()]
        assert len(technical_args) > 0
        assert all(arg.position == 'BULL' for arg in arguments)

    def test_gather_strong_fundamentals(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bull arguments with strong fundamentals"""
        sample_recommendation['analysis']['fundamental_score'] = 0.80

        arguments = debate_system._gather_bull_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        fundamental_args = [arg for arg in arguments if 'fundamental' in arg.point.lower()]
        assert len(fundamental_args) > 0
        assert all(arg.strength > 0 for arg in arguments)

    def test_gather_positive_sentiment(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bull arguments with positive sentiment"""
        sample_recommendation['analysis']['sentiment_score'] = 0.70

        arguments = debate_system._gather_bull_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        sentiment_args = [arg for arg in arguments if 'sentiment' in arg.point.lower()]
        assert len(sentiment_args) > 0

    def test_gather_default_arguments(self, debate_system, sample_market_data):
        """Test default bull arguments when no strong factors"""
        weak_rec = {
            'analysis': {
                'technical_score': 0.4,
                'fundamental_score': 0.4,
                'sentiment_score': 0.4
            }
        }

        arguments = debate_system._gather_bull_arguments(
            'AAPL', weak_rec, sample_market_data
        )

        # Should still return at least one argument
        assert len(arguments) >= 1
        assert arguments[0].position == 'BULL'

    def test_bull_arguments_have_evidence(self, debate_system, sample_recommendation, sample_market_data):
        """Test all bull arguments include evidence"""
        arguments = debate_system._gather_bull_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        for arg in arguments:
            assert len(arg.evidence) > 0
            assert all(isinstance(e, str) for e in arg.evidence)


class TestGatherBearArguments:
    """Test bear argument gathering"""

    def test_gather_high_risk(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bear arguments with high risk"""
        sample_recommendation['risk_assessment']['risk_level'] = 'HIGH'

        arguments = debate_system._gather_bear_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        assert len(arguments) > 0
        risk_args = [arg for arg in arguments if 'risk' in arg.point.lower()]
        assert len(risk_args) > 0
        assert all(arg.position == 'BEAR' for arg in arguments)

    def test_gather_overvalued(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bear arguments when overvalued"""
        sample_recommendation['analysis']['valuation_score'] = 0.30

        arguments = debate_system._gather_bear_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        valuation_args = [arg for arg in arguments if 'overvalued' in arg.point.lower() or 'valuation' in arg.point.lower()]
        assert len(valuation_args) > 0

    def test_gather_weak_technicals(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bear arguments with weak technicals"""
        sample_recommendation['analysis']['technical_score'] = 0.30

        arguments = debate_system._gather_bear_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        technical_args = [arg for arg in arguments if 'technical' in arg.point.lower()]
        assert len(technical_args) > 0

    def test_gather_extreme_risk(self, debate_system, sample_recommendation, sample_market_data):
        """Test gathering bear arguments with extreme risk"""
        sample_recommendation['risk_assessment']['risk_level'] = 'EXTREME'

        arguments = debate_system._gather_bear_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        # Extreme risk should generate strong bear argument
        assert any(arg.strength >= 0.8 for arg in arguments)

    def test_bear_arguments_have_evidence(self, debate_system, sample_recommendation, sample_market_data):
        """Test all bear arguments include evidence"""
        arguments = debate_system._gather_bear_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )

        for arg in arguments:
            assert len(arg.evidence) > 0
            assert all(isinstance(e, str) for e in arg.evidence)


class TestGenerateRebuttals:
    """Test rebuttal generation"""

    def test_generate_rebuttals_bull_to_bear(self, debate_system):
        """Test bull rebuttals to bear arguments"""
        bear_args = [
            Argument(
                position='BEAR',
                point='High risk level',
                evidence=['Elevated volatility'],
                strength=0.7
            )
        ]
        bull_args = []

        rebuttals = debate_system._generate_rebuttals(
            bull_args, bear_args, 'BULL'
        )

        assert len(rebuttals) > 0
        assert all(r.position == 'BULL' for r in rebuttals)
        assert all(r.rebuttal_to is not None for r in rebuttals)

    def test_generate_rebuttals_bear_to_bull(self, debate_system):
        """Test bear rebuttals to bull arguments"""
        bull_args = [
            Argument(
                position='BULL',
                point='Strong technical setup',
                evidence=['Price above support'],
                strength=0.7
            )
        ]
        bear_args = []

        rebuttals = debate_system._generate_rebuttals(
            bear_args, bull_args, 'BEAR'
        )

        assert len(rebuttals) > 0
        assert all(r.position == 'BEAR' for r in rebuttals)
        assert all(r.rebuttal_to is not None for r in rebuttals)

    def test_rebuttals_target_strongest_arguments(self, debate_system):
        """Test rebuttals target strongest opponent arguments"""
        opponent_args = [
            Argument('BULL', 'Weak technical', ['evidence'], 0.3),
            Argument('BULL', 'Strong technical setup', ['evidence'], 0.9),
            Argument('BULL', 'Medium technical', ['evidence'], 0.6)
        ]

        rebuttals = debate_system._generate_rebuttals(
            [], opponent_args, 'BEAR'
        )

        # Should rebut top 2 arguments (or fewer if patterns don't match)
        assert len(rebuttals) <= 2
        # If rebuttals exist, they should target stronger arguments
        if rebuttals:
            rebutted_points = [r.rebuttal_to for r in rebuttals]
            # Strong technical should be rebutted (has 'technical' keyword)
            assert 'Strong technical setup' in rebutted_points

    def test_rebuttal_strength_reasonable(self, debate_system):
        """Test rebuttal strength is in reasonable range"""
        opponent_args = [
            Argument('BULL', 'Technical strength', ['evidence'], 0.8)
        ]

        rebuttals = debate_system._generate_rebuttals(
            [], opponent_args, 'BEAR'
        )

        for rebuttal in rebuttals:
            assert 0 <= rebuttal.strength <= 1.0


class TestCreateRebuttal:
    """Test individual rebuttal creation"""

    def test_create_bull_rebuttal_to_risk(self, debate_system):
        """Test bull rebuttal to risk argument"""
        bear_arg = Argument(
            position='BEAR',
            point='High risk level',
            evidence=['Volatility'],
            strength=0.7
        )

        rebuttal = debate_system._create_rebuttal(bear_arg, 'BULL')

        assert rebuttal is not None
        assert rebuttal.position == 'BULL'
        assert 'risk' in rebuttal.point.lower() or 'stop' in rebuttal.point.lower()
        assert rebuttal.rebuttal_to == bear_arg.point

    def test_create_bull_rebuttal_to_overvalued(self, debate_system):
        """Test bull rebuttal to overvaluation"""
        bear_arg = Argument(
            position='BEAR',
            point='Overvalued',
            evidence=['High P/E'],
            strength=0.7
        )

        rebuttal = debate_system._create_rebuttal(bear_arg, 'BULL')

        assert rebuttal is not None
        assert rebuttal.position == 'BULL'
        assert 'growth' in rebuttal.point.lower() or 'valuation' in rebuttal.point.lower()

    def test_create_bear_rebuttal_to_technical(self, debate_system):
        """Test bear rebuttal to technical argument"""
        bull_arg = Argument(
            position='BULL',
            point='Strong technical setup',
            evidence=['Above MA'],
            strength=0.7
        )

        rebuttal = debate_system._create_rebuttal(bull_arg, 'BEAR')

        assert rebuttal is not None
        assert rebuttal.position == 'BEAR'
        assert 'technical' in rebuttal.point.lower() or 'reverse' in rebuttal.point.lower()

    def test_create_bear_rebuttal_to_fundamental(self, debate_system):
        """Test bear rebuttal to fundamental argument"""
        bull_arg = Argument(
            position='BULL',
            point='Solid fundamentals',
            evidence=['Strong earnings'],
            strength=0.7
        )

        rebuttal = debate_system._create_rebuttal(bull_arg, 'BEAR')

        assert rebuttal is not None
        assert rebuttal.position == 'BEAR'
        assert 'fundamental' in rebuttal.point.lower() or 'priced' in rebuttal.point.lower()

    def test_create_rebuttal_no_match(self, debate_system):
        """Test rebuttal creation with no matching pattern"""
        arg = Argument(
            position='BULL',
            point='Random argument',
            evidence=['Some evidence'],
            strength=0.5
        )

        rebuttal = debate_system._create_rebuttal(arg, 'BEAR')

        # May return None if no pattern matches
        if rebuttal is not None:
            assert rebuttal.position == 'BEAR'


class TestJudgeArguments:
    """Test judge evaluation logic"""

    def test_judge_equal_arguments(self, debate_system):
        """Test judging with equal arguments"""
        bull_args = [
            Argument('BULL', 'Point 1', ['evidence'], 0.7),
            Argument('BULL', 'Point 2', ['evidence'], 0.6)
        ]
        bear_args = [
            Argument('BEAR', 'Point 1', ['evidence'], 0.7),
            Argument('BEAR', 'Point 2', ['evidence'], 0.6)
        ]

        bull_score, bear_score = debate_system._judge_arguments(bull_args, bear_args)

        # Scores should be roughly equal
        assert 0.45 <= bull_score <= 0.55
        assert 0.45 <= bear_score <= 0.55
        assert abs(bull_score + bear_score - 1.0) < 0.01  # Should sum to ~1.0

    def test_judge_bull_stronger(self, debate_system):
        """Test judging with stronger bull case"""
        bull_args = [
            Argument('BULL', 'Point 1', ['evidence'], 0.9),
            Argument('BULL', 'Point 2', ['evidence'], 0.8)
        ]
        bear_args = [
            Argument('BEAR', 'Point 1', ['evidence'], 0.4)
        ]

        bull_score, bear_score = debate_system._judge_arguments(bull_args, bear_args)

        assert bull_score > bear_score
        assert bull_score > 0.6

    def test_judge_bear_stronger(self, debate_system):
        """Test judging with stronger bear case"""
        bull_args = [
            Argument('BULL', 'Point 1', ['evidence'], 0.3)
        ]
        bear_args = [
            Argument('BEAR', 'Point 1', ['evidence'], 0.9),
            Argument('BEAR', 'Point 2', ['evidence'], 0.8)
        ]

        bull_score, bear_score = debate_system._judge_arguments(bull_args, bear_args)

        assert bear_score > bull_score
        assert bear_score > 0.6

    def test_judge_rebuttal_bonus(self, debate_system):
        """Test rebuttals receive bonus points"""
        bull_args = [
            Argument('BULL', 'Point 1', ['evidence'], 0.6),
            Argument('BULL', 'Rebuttal', ['evidence'], 0.6, rebuttal_to='Bear point')
        ]
        bear_args = [
            Argument('BEAR', 'Point 1', ['evidence'], 0.6)
        ]

        bull_score, bear_score = debate_system._judge_arguments(bull_args, bear_args)

        # Bull should score higher due to rebuttal bonus
        assert bull_score > bear_score

    def test_judge_empty_arguments(self, debate_system):
        """Test judging with no arguments"""
        bull_score, bear_score = debate_system._judge_arguments([], [])

        assert bull_score == 0.5
        assert bear_score == 0.5

    def test_judge_scores_sum_to_one(self, debate_system):
        """Test scores always sum to 1.0"""
        bull_args = [Argument('BULL', 'Point', ['evidence'], 0.7)]
        bear_args = [Argument('BEAR', 'Point', ['evidence'], 0.5)]

        bull_score, bear_score = debate_system._judge_arguments(bull_args, bear_args)

        assert abs(bull_score + bear_score - 1.0) < 0.01


class TestDetermineWinner:
    """Test winner determination logic"""

    def test_clear_bull_win(self, debate_system, sample_recommendation):
        """Test clear bull victory"""
        winner, adjustment = debate_system._determine_winner(
            0.75, 0.25, sample_recommendation
        )

        assert winner == 'BULL'
        assert adjustment > 0

    def test_clear_bear_win(self, debate_system, sample_recommendation):
        """Test clear bear victory"""
        winner, adjustment = debate_system._determine_winner(
            0.25, 0.75, sample_recommendation
        )

        assert winner == 'BEAR'
        # Bear win with BUY action should decrease confidence
        assert adjustment < 0

    def test_tie(self, debate_system, sample_recommendation):
        """Test tie scenario"""
        winner, adjustment = debate_system._determine_winner(
            0.52, 0.48, sample_recommendation
        )

        assert winner == 'TIE'
        assert adjustment < 0  # Ties reduce confidence due to uncertainty

    def test_adjustment_range(self, debate_system, sample_recommendation):
        """Test confidence adjustment stays in range"""
        winner, adjustment = debate_system._determine_winner(
            0.90, 0.10, sample_recommendation
        )

        assert -0.10 <= adjustment <= 0.10

    def test_bull_win_buy_action(self, debate_system):
        """Test bull win with buy action increases confidence"""
        rec = {'recommendation': {'action': 'BUY'}}
        winner, adjustment = debate_system._determine_winner(0.70, 0.30, rec)

        assert winner == 'BULL'
        assert adjustment > 0

    def test_bear_win_hold_action(self, debate_system):
        """Test bear win with hold action increases confidence"""
        rec = {'recommendation': {'action': 'HOLD'}}
        winner, adjustment = debate_system._determine_winner(0.30, 0.70, rec)

        assert winner == 'BEAR'
        assert adjustment > 0


class TestGenerateJudgeReasoning:
    """Test judge reasoning generation"""

    def test_reasoning_includes_scores(self, debate_system):
        """Test reasoning includes scores"""
        bull_args = [Argument('BULL', 'Strong point', ['evidence'], 0.8)]
        bear_args = [Argument('BEAR', 'Weak point', ['evidence'], 0.4)]

        reasoning = debate_system._generate_judge_reasoning(
            0.7, 0.3, bull_args, bear_args
        )

        assert '0.70' in reasoning or '0.7' in reasoning
        assert '0.30' in reasoning or '0.3' in reasoning

    def test_reasoning_includes_strongest_arguments(self, debate_system):
        """Test reasoning mentions strongest arguments"""
        bull_args = [
            Argument('BULL', 'Weak', ['evidence'], 0.3),
            Argument('BULL', 'Strong technical', ['evidence'], 0.9)
        ]
        bear_args = [
            Argument('BEAR', 'Strong risk concern', ['evidence'], 0.85)
        ]

        reasoning = debate_system._generate_judge_reasoning(
            0.6, 0.4, bull_args, bear_args
        )

        assert 'Strong technical' in reasoning or 'technical' in reasoning.lower()
        assert 'risk concern' in reasoning.lower() or 'risk' in reasoning.lower()

    def test_reasoning_includes_conclusion(self, debate_system):
        """Test reasoning includes conclusion"""
        bull_args = [Argument('BULL', 'Point', ['evidence'], 0.7)]
        bear_args = [Argument('BEAR', 'Point', ['evidence'], 0.4)]

        reasoning = debate_system._generate_judge_reasoning(
            0.65, 0.35, bull_args, bear_args
        )

        # Should indicate bull case is more compelling
        assert 'bull' in reasoning.lower() and 'compelling' in reasoning.lower()

    def test_reasoning_for_tie(self, debate_system):
        """Test reasoning for tie scenario"""
        bull_args = [Argument('BULL', 'Point', ['evidence'], 0.5)]
        bear_args = [Argument('BEAR', 'Point', ['evidence'], 0.5)]

        reasoning = debate_system._generate_judge_reasoning(
            0.5, 0.5, bull_args, bear_args
        )

        assert 'evenly' in reasoning.lower() or 'balanced' in reasoning.lower()


class TestGenerateDebateSummary:
    """Test debate summary generation"""

    def test_summary_bull_win(self, debate_system):
        """Test summary for bull win"""
        summary = debate_system._generate_debate_summary(
            'AAPL', 'BULL', 0.08, 0.65, 0.35
        )

        assert 'AAPL' in summary
        assert 'Bull' in summary
        assert '65%' in summary or '0.65' in summary
        assert '+' in summary or 'adjusted' in summary.lower()

    def test_summary_bear_win(self, debate_system):
        """Test summary for bear win"""
        summary = debate_system._generate_debate_summary(
            'TSLA', 'BEAR', -0.05, 0.35, 0.65
        )

        assert 'TSLA' in summary
        assert 'Bear' in summary
        assert '65%' in summary or '0.65' in summary

    def test_summary_tie(self, debate_system):
        """Test summary for tie"""
        summary = debate_system._generate_debate_summary(
            'NVDA', 'TIE', -0.03, 0.50, 0.50
        )

        assert 'NVDA' in summary
        assert 'Tie' in summary or 'tie' in summary
        assert '-' in summary or 'adjusted' in summary.lower()

    def test_summary_includes_adjustment(self, debate_system):
        """Test summary includes confidence adjustment"""
        summary = debate_system._generate_debate_summary(
            'AAPL', 'BULL', 0.10, 0.70, 0.30
        )

        # Should show +10.0% or +0.10
        assert '+10' in summary or '+0.10' in summary


class TestConductDebate:
    """Test full debate conduct"""

    def test_conduct_full_debate(self, debate_system, sample_recommendation, sample_market_data):
        """Test conducting full debate"""
        result = debate_system.conduct_debate(
            'AAPL', sample_recommendation, sample_market_data
        )

        assert isinstance(result, DebateResult)
        assert result.ticker == 'AAPL'
        assert 0 <= result.bull_score <= 1
        assert 0 <= result.bear_score <= 1
        assert result.winner in ['BULL', 'BEAR', 'TIE']
        assert -0.10 <= result.confidence_adjustment <= 0.10

    def test_debate_has_arguments(self, debate_system, sample_recommendation, sample_market_data):
        """Test debate generates arguments"""
        result = debate_system.conduct_debate(
            'AAPL', sample_recommendation, sample_market_data
        )

        assert len(result.bull_arguments) > 0
        assert len(result.bear_arguments) > 0

    def test_debate_has_reasoning(self, debate_system, sample_recommendation, sample_market_data):
        """Test debate generates reasoning"""
        result = debate_system.conduct_debate(
            'AAPL', sample_recommendation, sample_market_data
        )

        assert len(result.judge_reasoning) > 0
        assert len(result.debate_summary) > 0

    def test_debate_multiple_rounds(self, debate_system, sample_recommendation, sample_market_data):
        """Test debate conducts multiple rounds"""
        debate_system.max_rounds = 2

        result = debate_system.conduct_debate(
            'AAPL', sample_recommendation, sample_market_data
        )

        # Should have some rebuttals after multiple rounds
        has_rebuttals = any(arg.rebuttal_to is not None for arg in result.bull_arguments)
        has_rebuttals = has_rebuttals or any(arg.rebuttal_to is not None for arg in result.bear_arguments)
        assert has_rebuttals


class TestConvenienceFunction:
    """Test convenience debate_trade function"""

    def test_debate_trade_function(self, sample_recommendation, sample_market_data):
        """Test convenience function"""
        result = debate_trade(
            'AAPL',
            sample_recommendation,
            sample_market_data
        )

        assert isinstance(result, DebateResult)
        assert result.ticker == 'AAPL'

    def test_debate_trade_with_agents(self, sample_recommendation, sample_market_data):
        """Test convenience function with agents"""
        bull = Mock()
        bear = Mock()

        result = debate_trade(
            'AAPL',
            sample_recommendation,
            sample_market_data,
            bull_agent=bull,
            bear_agent=bear
        )

        assert isinstance(result, DebateResult)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_recommendation(self, debate_system, sample_market_data):
        """Test with minimal recommendation"""
        minimal_rec = {
            'recommendation': {'action': 'HOLD'},
            'analysis': {},
            'risk_assessment': {}
        }

        result = debate_system.conduct_debate('AAPL', minimal_rec, sample_market_data)

        # Should still complete without errors
        assert isinstance(result, DebateResult)

    def test_missing_analysis_fields(self, debate_system, sample_market_data):
        """Test with missing analysis fields"""
        rec = {
            'recommendation': {'action': 'BUY'},
            'analysis': {},  # Empty analysis
            'risk_assessment': {}
        }

        # Should not crash
        bull_args = debate_system._gather_bull_arguments('AAPL', rec, sample_market_data)
        assert len(bull_args) > 0  # Should generate default arguments

    def test_missing_risk_assessment(self, debate_system, sample_recommendation, sample_market_data):
        """Test with missing risk assessment"""
        del sample_recommendation['risk_assessment']

        # Should not crash
        bear_args = debate_system._gather_bear_arguments(
            'AAPL', sample_recommendation, sample_market_data
        )
        assert len(bear_args) > 0

    def test_extreme_scores(self, debate_system, sample_recommendation, sample_market_data):
        """Test with extreme scores"""
        sample_recommendation['analysis'] = {
            'technical_score': 1.0,
            'fundamental_score': 1.0,
            'sentiment_score': 1.0,
            'valuation_score': 0.0
        }

        result = debate_system.conduct_debate(
            'AAPL', sample_recommendation, sample_market_data
        )

        # Should handle extreme values
        assert isinstance(result, DebateResult)
        assert -0.10 <= result.confidence_adjustment <= 0.10


class TestDebateConfiguration:
    """Test debate system configuration"""

    def test_custom_max_rounds(self):
        """Test custom max rounds"""
        system = DebateSystem()
        system.max_rounds = 5

        assert system.max_rounds == 5

    def test_custom_confidence_thresholds(self):
        """Test custom confidence thresholds"""
        system = DebateSystem()
        system.min_confidence_for_debate = 0.50
        system.max_confidence_for_debate = 0.80

        assert system.should_debate(0.50) is True
        assert system.should_debate(0.80) is True
        assert system.should_debate(0.45) is False
        assert system.should_debate(0.85) is False

    def test_debate_threshold_validation(self):
        """Test debate thresholds are valid"""
        system = DebateSystem()

        # Min should be less than max
        assert system.min_confidence_for_debate < system.max_confidence_for_debate

        # Both should be valid probabilities
        assert 0 < system.min_confidence_for_debate < 1
        assert 0 < system.max_confidence_for_debate < 1
