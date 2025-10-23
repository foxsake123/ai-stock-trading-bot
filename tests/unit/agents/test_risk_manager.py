"""
Unit tests for RiskManagerAgent
Tests risk analysis, veto decisions, and position sizing
"""

import pytest
from src.agents.risk_manager import RiskManagerAgent


@pytest.fixture
def agent():
    """Create a risk manager agent instance"""
    return RiskManagerAgent()


@pytest.fixture
def valid_market_data():
    """Sample valid market data"""
    return {
        "price": 150.00,
        "volume": 500000,
        "avg_volume": 400000,
        "volatility": 0.25,
        "beta": 1.0,
        "support_level": 145.00,
        "sector": "Technology",
        "proposed_position_size": 5000
    }


@pytest.fixture
def high_risk_market_data():
    """High risk market data"""
    return {
        "price": 50.00,
        "volume": 50000,  # Low liquidity
        "avg_volume": 60000,
        "volatility": 0.8,  # Very high volatility
        "beta": 2.5,  # High beta
        "support_level": 35.00,
        "sector": "Technology",
        "proposed_position_size": 10000  # Large position
    }


@pytest.fixture
def safe_portfolio_data():
    """Safe portfolio with few positions"""
    return {
        "total_value": 100000,
        "positions": [
            {"ticker": "AAPL", "value": 5000, "sector": "Technology"},
            {"ticker": "MSFT", "value": 5000, "sector": "Technology"}
        ],
        "portfolio_volatility": 0.15,
        "max_drawdown": 0.10
    }


@pytest.fixture
def risky_portfolio_data():
    """Risky portfolio with high concentration"""
    return {
        "total_value": 100000,
        "positions": [
            {"ticker": "AAPL", "value": 20000, "sector": "Technology"},
            {"ticker": "MSFT", "value": 20000, "sector": "Technology"},
            {"ticker": "GOOGL", "value": 15000, "sector": "Technology"},
            {"ticker": "NVDA", "value": 15000, "sector": "Technology"}
        ],
        "portfolio_volatility": 0.35,
        "max_drawdown": 0.25
    }


@pytest.fixture
def consensus_bullish():
    """Strong bullish consensus"""
    return [
        {"recommendation": {"action": "BUY"}, "confidence": 0.85},
        {"recommendation": {"action": "BUY"}, "confidence": 0.80},
        {"recommendation": {"action": "BUY"}, "confidence": 0.75},
        {"recommendation": {"action": "HOLD"}, "confidence": 0.60}
    ]


@pytest.fixture
def consensus_mixed():
    """Mixed/divergent consensus"""
    return [
        {"recommendation": {"action": "BUY"}, "confidence": 0.60},
        {"recommendation": {"action": "SELL"}, "confidence": 0.65},
        {"recommendation": {"action": "HOLD"}, "confidence": 0.50},
        {"recommendation": {"action": "BUY"}, "confidence": 0.55}
    ]


class TestRiskManagerInitialization:
    """Test risk manager initialization"""

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized"""
        assert agent.agent_id == "risk_manager_001"
        assert agent.agent_type == "risk_manager"

    def test_risk_limits_configured(self, agent):
        """Test risk limits are set"""
        assert agent.max_position_size == 0.05  # 5%
        assert agent.max_portfolio_risk == 0.15  # 15%
        assert agent.max_correlation == 0.7
        assert agent.max_daily_loss == 0.02
        assert agent.max_volatility == 0.5

    def test_risk_weights_configured(self, agent):
        """Test risk scoring weights are configured"""
        expected_weights = [
            "volatility", "liquidity", "correlation",
            "concentration", "fundamental", "technical"
        ]
        for weight in expected_weights:
            assert weight in agent.risk_weights
            assert 0 < agent.risk_weights[weight] <= 1.0


class TestPositionRiskCalculation:
    """Test individual position risk calculation"""

    def test_calculate_position_risk_basic(self, agent, valid_market_data):
        """Test basic position risk calculation"""
        risk = agent._calculate_position_risk("AAPL", valid_market_data)

        assert 'volatility_risk' in risk
        assert 'liquidity_risk' in risk
        assert 'price_risk' in risk
        assert 'beta_risk' in risk
        assert 'overall_risk' in risk

    def test_high_volatility_increases_risk(self, agent, high_risk_market_data):
        """Test high volatility increases position risk"""
        risk = agent._calculate_position_risk("RISKY", high_risk_market_data)

        assert risk['volatility_risk'] > 0.5
        assert risk['volatility'] == 0.8

    def test_low_liquidity_increases_risk(self, agent, high_risk_market_data):
        """Test low liquidity increases risk"""
        risk = agent._calculate_position_risk("ILLIQUID", high_risk_market_data)

        assert risk['liquidity_risk'] >= 0.5

    def test_beta_risk_calculation(self, agent, valid_market_data):
        """Test beta risk is calculated"""
        market_data_high_beta = valid_market_data.copy()
        market_data_high_beta['beta'] = 2.0

        risk = agent._calculate_position_risk("AAPL", market_data_high_beta)

        assert risk['beta_risk'] > 0
        assert risk['beta'] == 2.0

    def test_price_risk_calculation(self, agent, valid_market_data):
        """Test price distance from support"""
        risk = agent._calculate_position_risk("AAPL", valid_market_data)

        assert 'price_risk' in risk
        assert 0 <= risk['price_risk'] <= 1.0

    def test_overall_risk_range(self, agent, valid_market_data):
        """Test overall risk is in valid range"""
        risk = agent._calculate_position_risk("AAPL", valid_market_data)

        assert 0 <= risk['overall_risk'] <= 1.0


class TestPortfolioRiskAssessment:
    """Test portfolio-level risk assessment"""

    def test_concentration_risk_small_position(self, agent, safe_portfolio_data, valid_market_data):
        """Test low concentration risk for small position"""
        risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        assert risk['concentration_risk'] <= 1.0  # Within limits

    def test_concentration_risk_large_position(self, agent, safe_portfolio_data, high_risk_market_data):
        """Test high concentration risk for large position"""
        risk = agent._assess_portfolio_risk(safe_portfolio_data, "RISKY", high_risk_market_data)

        assert risk['concentration_risk'] > 1.0  # Exceeds 5% limit

    def test_sector_concentration_calculation(self, agent, risky_portfolio_data, valid_market_data):
        """Test sector concentration is calculated"""
        risk = agent._assess_portfolio_risk(risky_portfolio_data, "AAPL", valid_market_data)

        assert 'sector_concentration' in risk
        assert risk['sector_concentration'] > 0.5  # High tech concentration

    def test_correlation_risk_assessment(self, agent, safe_portfolio_data, valid_market_data):
        """Test correlation risk is assessed"""
        risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        assert 'correlation_risk' in risk
        assert 0 <= risk['correlation_risk'] <= 2.0

    def test_volatility_increase_calculation(self, agent, safe_portfolio_data, high_risk_market_data):
        """Test portfolio volatility increase"""
        risk = agent._assess_portfolio_risk(safe_portfolio_data, "RISKY", high_risk_market_data)

        assert 'volatility_increase' in risk

    def test_position_count_tracking(self, agent, safe_portfolio_data, valid_market_data):
        """Test position count is tracked"""
        risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        assert risk['position_count'] == 3  # 2 existing + 1 new

    def test_expected_drawdown_estimation(self, agent, safe_portfolio_data, valid_market_data):
        """Test drawdown is estimated"""
        risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        assert 'expected_drawdown' in risk
        assert 0 <= risk['expected_drawdown'] <= 1.0


class TestRiskLimitChecking:
    """Test risk limit violation checking"""

    def test_no_violations_for_safe_position(self, agent, safe_portfolio_data, valid_market_data):
        """Test no violations for safe position"""
        # Use different ticker (GOOGL) to avoid correlation with existing AAPL
        googl_data = valid_market_data.copy()
        googl_data['sector'] = "Consumer"  # Different sector

        position_risk = agent._calculate_position_risk("GOOGL", googl_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "GOOGL", googl_data)

        violations = agent._check_risk_limits(position_risk, portfolio_risk, googl_data)

        assert len(violations) == 0

    def test_position_size_violation(self, agent, safe_portfolio_data, high_risk_market_data):
        """Test position size limit violation"""
        position_risk = agent._calculate_position_risk("RISKY", high_risk_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "RISKY", high_risk_market_data)

        violations = agent._check_risk_limits(position_risk, portfolio_risk, high_risk_market_data)

        size_violations = [v for v in violations if v['type'] == 'position_size']
        assert len(size_violations) > 0
        assert size_violations[0]['severity'] == 'CRITICAL'

    def test_volatility_violation(self, agent, safe_portfolio_data, high_risk_market_data):
        """Test volatility limit violation"""
        position_risk = agent._calculate_position_risk("RISKY", high_risk_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "RISKY", high_risk_market_data)

        violations = agent._check_risk_limits(position_risk, portfolio_risk, high_risk_market_data)

        vol_violations = [v for v in violations if v['type'] == 'volatility']
        assert len(vol_violations) > 0

    def test_liquidity_violation(self, agent, safe_portfolio_data):
        """Test liquidity limit violation"""
        low_liquidity_data = {
            "price": 50.00,
            "volume": 50000,  # Below 100k minimum
            "volatility": 0.2,
            "proposed_position_size": 2000
        }

        position_risk = agent._calculate_position_risk("ILLIQUID", low_liquidity_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "ILLIQUID", low_liquidity_data)

        violations = agent._check_risk_limits(position_risk, portfolio_risk, low_liquidity_data)

        liq_violations = [v for v in violations if v['type'] == 'liquidity']
        assert len(liq_violations) > 0

    def test_sector_concentration_violation(self, agent, risky_portfolio_data, valid_market_data):
        """Test sector concentration violation"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(risky_portfolio_data, "AAPL", valid_market_data)

        violations = agent._check_risk_limits(position_risk, portfolio_risk, valid_market_data)

        sector_violations = [v for v in violations if v['type'] == 'sector_concentration']
        assert len(sector_violations) > 0

    def test_violation_severity_levels(self, agent, safe_portfolio_data, high_risk_market_data):
        """Test violations have proper severity levels"""
        position_risk = agent._calculate_position_risk("RISKY", high_risk_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "RISKY", high_risk_market_data)

        violations = agent._check_risk_limits(position_risk, portfolio_risk, high_risk_market_data)

        for violation in violations:
            assert 'severity' in violation
            assert violation['severity'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']


class TestConsensusRiskAnalysis:
    """Test agent consensus risk analysis"""

    def test_analyze_strong_consensus(self, agent, consensus_bullish):
        """Test strong consensus analysis"""
        consensus = agent._analyze_consensus_risk(consensus_bullish)

        assert consensus['consensus_quality'] > 0.5  # Adjusted threshold
        assert consensus['disagreement'] < 0.5
        assert consensus['buy_votes'] == 3

    def test_analyze_mixed_consensus(self, agent, consensus_mixed):
        """Test mixed consensus increases risk"""
        consensus = agent._analyze_consensus_risk(consensus_mixed)

        assert consensus['disagreement'] > 0.4
        assert consensus['consensus_quality'] < 0.6

    def test_empty_consensus(self, agent):
        """Test handling of empty agent reports"""
        consensus = agent._analyze_consensus_risk([])

        assert consensus['consensus_quality'] == 0.5
        assert consensus['disagreement'] == 0.5

    def test_consensus_confidence_average(self, agent, consensus_bullish):
        """Test average confidence calculation"""
        consensus = agent._analyze_consensus_risk(consensus_bullish)

        assert 'confidence_avg' in consensus
        assert 0 < consensus['confidence_avg'] < 1.0

    def test_vote_counting(self, agent, consensus_mixed):
        """Test vote counting accuracy"""
        consensus = agent._analyze_consensus_risk(consensus_mixed)

        total_votes = (consensus['buy_votes'] + consensus['sell_votes'] +
                      consensus['hold_votes'])
        assert total_votes == 4


class TestRiskScoring:
    """Test overall risk score calculation"""

    def test_calculate_low_risk_score(self, agent, safe_portfolio_data, valid_market_data, consensus_bullish):
        """Test low risk score for safe position"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)
        consensus_risk = agent._analyze_consensus_risk(consensus_bullish)
        violations = []

        score = agent._calculate_risk_score(position_risk, portfolio_risk, consensus_risk, violations)

        assert score < 0.5

    def test_calculate_high_risk_score(self, agent, risky_portfolio_data, high_risk_market_data, consensus_mixed):
        """Test high risk score for risky position"""
        position_risk = agent._calculate_position_risk("RISKY", high_risk_market_data)
        portfolio_risk = agent._assess_portfolio_risk(risky_portfolio_data, "RISKY", high_risk_market_data)
        consensus_risk = agent._analyze_consensus_risk(consensus_mixed)
        violations = [
            {"severity": "CRITICAL", "type": "position_size"},
            {"severity": "HIGH", "type": "volatility"}
        ]

        score = agent._calculate_risk_score(position_risk, portfolio_risk, consensus_risk, violations)

        assert score > 0.6

    def test_risk_score_range(self, agent, safe_portfolio_data, valid_market_data):
        """Test risk score is always in valid range"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)
        consensus_risk = agent._analyze_consensus_risk([])
        violations = []

        score = agent._calculate_risk_score(position_risk, portfolio_risk, consensus_risk, violations)

        assert 0 <= score <= 1.0

    def test_violations_increase_score(self, agent, safe_portfolio_data, valid_market_data):
        """Test violations increase risk score"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)
        consensus_risk = agent._analyze_consensus_risk([])

        score_no_violations = agent._calculate_risk_score(
            position_risk, portfolio_risk, consensus_risk, []
        )

        violations = [{"severity": "CRITICAL", "type": "test"}]
        score_with_violations = agent._calculate_risk_score(
            position_risk, portfolio_risk, consensus_risk, violations
        )

        assert score_with_violations > score_no_violations


class TestVetoDecisions:
    """Test veto decision making"""

    def test_veto_for_critical_violation(self, agent):
        """Test veto for critical risk limit violation"""
        violations = [{"severity": "CRITICAL", "type": "position_size", "message": "Too large"}]

        veto = agent._make_veto_decision(0.5, violations)

        assert veto['veto'] is True
        assert "Critical" in veto['reason']
        assert veto['override_possible'] is False

    def test_veto_for_extreme_risk(self, agent):
        """Test veto for extreme risk score"""
        veto = agent._make_veto_decision(0.85, [])

        assert veto['veto'] is True
        assert "Excessive" in veto['reason']
        assert veto['override_possible'] is True

    def test_veto_for_multiple_violations(self, agent):
        """Test veto for multiple violations"""
        violations = [
            {"severity": "HIGH", "type": "volatility"},
            {"severity": "MEDIUM", "type": "liquidity"},
            {"severity": "MEDIUM", "type": "sector"}
        ]

        veto = agent._make_veto_decision(0.5, violations)

        assert veto['veto'] is True
        assert "Multiple" in veto['reason']

    def test_no_veto_for_low_risk(self, agent):
        """Test no veto for acceptable risk"""
        veto = agent._make_veto_decision(0.4, [])

        assert veto['veto'] is False
        assert veto['reason'] is None

    def test_override_possible_varies(self, agent):
        """Test override_possible flag is set correctly"""
        # Critical violation - no override
        veto_critical = agent._make_veto_decision(0.5, [{"severity": "CRITICAL", "type": "test"}])
        assert veto_critical['override_possible'] is False

        # High risk - override possible
        veto_high_risk = agent._make_veto_decision(0.85, [])
        assert veto_high_risk['override_possible'] is True


class TestRecommendationGeneration:
    """Test recommendation generation"""

    def test_hold_recommendation_for_veto(self, agent):
        """Test HOLD recommendation when vetoed"""
        veto = {"veto": True, "reason": "Critical violation", "override_possible": False}

        recommendation = agent._generate_recommendation(0.8, veto, [])

        assert recommendation['action'] == "HOLD"
        assert recommendation['confidence'] == 1.0
        assert "VETO" in recommendation['reasoning']

    def test_proceed_recommendation_for_low_risk(self, agent):
        """Test PROCEED recommendation for low risk"""
        veto = {"veto": False, "reason": None, "override_possible": False}

        recommendation = agent._generate_recommendation(0.2, veto, [])

        assert recommendation['action'] == "PROCEED"
        assert "acceptable" in recommendation['reasoning'].lower()

    def test_hold_recommendation_for_high_risk(self, agent):
        """Test HOLD recommendation for high risk"""
        veto = {"veto": False, "reason": None, "override_possible": False}

        recommendation = agent._generate_recommendation(0.7, veto, [])

        assert recommendation['action'] == "HOLD"
        assert "risk score" in recommendation['reasoning'].lower()

    def test_violation_warnings_in_reasoning(self, agent):
        """Test violation warnings added to reasoning"""
        veto = {"veto": False, "reason": None, "override_possible": False}
        violations = [
            {"severity": "MEDIUM", "type": "liquidity"},
            {"severity": "MEDIUM", "type": "sector"}
        ]

        recommendation = agent._generate_recommendation(0.5, veto, violations)

        assert "Warnings" in recommendation['reasoning']


class TestRiskMetrics:
    """Test risk metrics calculation"""

    def test_calculate_risk_level(self, agent, safe_portfolio_data, valid_market_data):
        """Test risk level classification"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        metrics = agent._calculate_risk_metrics(position_risk, portfolio_risk, valid_market_data)

        assert 'risk_level' in metrics
        assert metrics['risk_level'] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    def test_position_size_based_on_risk(self, agent, safe_portfolio_data, valid_market_data, high_risk_market_data):
        """Test position size decreases with risk"""
        # Low risk position
        low_risk_data = valid_market_data.copy()
        low_risk_data['volatility'] = 0.15
        position_risk_low = agent._calculate_position_risk("SAFE", low_risk_data)
        portfolio_risk_low = agent._assess_portfolio_risk(safe_portfolio_data, "SAFE", low_risk_data)
        metrics_low = agent._calculate_risk_metrics(position_risk_low, portfolio_risk_low, low_risk_data)

        # High risk position
        position_risk_high = agent._calculate_position_risk("RISKY", high_risk_market_data)
        portfolio_risk_high = agent._assess_portfolio_risk(safe_portfolio_data, "RISKY", high_risk_market_data)
        metrics_high = agent._calculate_risk_metrics(position_risk_high, portfolio_risk_high, high_risk_market_data)

        assert metrics_low['position_size_pct'] > metrics_high['position_size_pct']

    def test_stop_loss_calculation(self, agent, safe_portfolio_data, valid_market_data):
        """Test stop loss is calculated"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        metrics = agent._calculate_risk_metrics(position_risk, portfolio_risk, valid_market_data)

        assert 'stop_loss' in metrics
        assert metrics['stop_loss'] < valid_market_data['price']

    def test_take_profit_calculation(self, agent, safe_portfolio_data, valid_market_data):
        """Test take profit is calculated"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        metrics = agent._calculate_risk_metrics(position_risk, portfolio_risk, valid_market_data)

        assert 'take_profit' in metrics
        assert metrics['take_profit'] > valid_market_data['price']

    def test_max_loss_calculation(self, agent, safe_portfolio_data, valid_market_data):
        """Test max loss is calculated"""
        position_risk = agent._calculate_position_risk("AAPL", valid_market_data)
        portfolio_risk = agent._assess_portfolio_risk(safe_portfolio_data, "AAPL", valid_market_data)

        metrics = agent._calculate_risk_metrics(position_risk, portfolio_risk, valid_market_data)

        assert 'max_loss' in metrics
        assert metrics['max_loss'] >= 0


class TestFullAnalysis:
    """Test complete risk analysis workflow"""

    def test_analyze_safe_position(self, agent, valid_market_data, safe_portfolio_data, consensus_bullish):
        """Test analysis of safe position"""
        result = agent.analyze(
            "AAPL",
            valid_market_data,
            portfolio_data=safe_portfolio_data,
            agent_reports=consensus_bullish
        )

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'risk_assessment' in result
        assert result['analysis']['veto_decision']['veto'] is False

    def test_analyze_risky_position(self, agent, high_risk_market_data, risky_portfolio_data, consensus_mixed):
        """Test analysis of risky position"""
        result = agent.analyze(
            "RISKY",
            high_risk_market_data,
            portfolio_data=risky_portfolio_data,
            agent_reports=consensus_mixed
        )

        assert 'recommendation' in result
        assert result['analysis']['risk_score'] > 0.5
        assert len(result['analysis']['limit_violations']) > 0

    def test_analyze_returns_required_fields(self, agent, valid_market_data):
        """Test analysis returns all required fields"""
        result = agent.analyze("AAPL", valid_market_data)

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'risk_assessment' in result
        assert 'confidence' in result

        assert 'risk_score' in result['analysis']
        assert 'veto_decision' in result['analysis']
        assert 'risk_metrics' in result['analysis']

    def test_veto_authority_exercised(self, agent, high_risk_market_data, safe_portfolio_data):
        """Test veto authority is exercised for dangerous trades"""
        # Create conditions for guaranteed veto
        dangerous_data = high_risk_market_data.copy()
        dangerous_data['proposed_position_size'] = 15000  # 15% of portfolio

        result = agent.analyze(
            "DANGEROUS",
            dangerous_data,
            portfolio_data=safe_portfolio_data
        )

        assert result['analysis']['veto_decision']['veto'] is True
        assert result['recommendation']['action'] == "HOLD"

    def test_confidence_high_for_veto(self, agent, high_risk_market_data, safe_portfolio_data):
        """Test confidence is high when vetoing"""
        dangerous_data = high_risk_market_data.copy()
        dangerous_data['proposed_position_size'] = 15000

        result = agent.analyze(
            "DANGEROUS",
            dangerous_data,
            portfolio_data=safe_portfolio_data
        )

        assert result['confidence'] > 0.9


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_analyze_with_empty_market_data(self, agent):
        """Test analysis handles empty market data"""
        result = agent.analyze("AAPL", {})

        assert 'recommendation' in result or 'error' in result

    def test_analyze_with_none_values(self, agent, valid_market_data):
        """Test analysis handles None values"""
        market_data_with_none = valid_market_data.copy()
        market_data_with_none['volatility'] = None

        result = agent.analyze("AAPL", market_data_with_none)

        assert result is not None

    def test_analyze_without_portfolio_data(self, agent, valid_market_data):
        """Test analysis works without portfolio data"""
        result = agent.analyze("AAPL", valid_market_data)

        assert result is not None
        assert 'risk_score' in result['analysis']

    def test_analyze_without_agent_reports(self, agent, valid_market_data):
        """Test analysis works without agent reports"""
        result = agent.analyze("AAPL", valid_market_data)

        assert result is not None
        assert 'consensus_risk' in result['analysis']

    def test_multiple_analyses_independent(self, agent, valid_market_data):
        """Test multiple analyses don't interfere"""
        result1 = agent.analyze("AAPL", valid_market_data)
        result2 = agent.analyze("MSFT", valid_market_data)

        assert result1 is not result2


class TestHelperFunctions:
    """Test helper calculation functions"""

    def test_correlation_calculation(self, agent):
        """Test correlation estimation"""
        # Same ticker = 1.0 correlation
        corr_same = agent._calculate_correlation("AAPL", "AAPL")
        assert corr_same == 1.0

        # Different tickers = lower correlation
        corr_diff = agent._calculate_correlation("AAPL", "MSFT")
        assert 0 <= corr_diff < 1.0

    def test_drawdown_estimation(self, agent):
        """Test drawdown estimation"""
        drawdown_low_vol = agent._estimate_drawdown(0.15)
        drawdown_high_vol = agent._estimate_drawdown(0.40)

        assert drawdown_high_vol > drawdown_low_vol
        assert drawdown_high_vol <= 0.5  # Capped at 50%

    def test_portfolio_volatility_calculation(self, agent):
        """Test new portfolio volatility calculation"""
        new_vol = agent._calculate_new_portfolio_volatility(
            current_vol=0.15,
            new_vol=0.30,
            weight=0.05
        )

        assert new_vol > 0.15  # Should increase
        assert new_vol < 0.30  # But less than new asset volatility
