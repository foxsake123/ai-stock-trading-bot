"""
Unit tests for BearResearcherAgent
Tests bearish analysis and risk identification
"""

import pytest
from src.agents.bear_researcher import BearResearcherAgent


@pytest.fixture
def agent():
    """Create a bear researcher agent instance"""
    return BearResearcherAgent()


@pytest.fixture
def valid_market_data():
    """Sample valid market data"""
    return {
        "price": 150.00,
        "volume": 1000000,
        "market_cap": 500000000000,
        "high": 152.00,
        "low": 148.00
    }


@pytest.fixture
def weak_fundamental_data():
    """Weak fundamental data for bearish case"""
    return {
        "revenue_growth": -0.15,  # -15% decline
        "earnings_growth": -0.20,  # -20% decline
        "return_on_equity": 0.05,  # Low ROE
        "debt_to_equity": 3.0,  # Very high debt
        "margin_trend": -0.05,  # Contracting margins
        "free_cash_flow": -1000000,  # Negative FCF
        "insider_selling_ratio": 3.0,  # Heavy selling
        "pe_ratio": 60,  # Overvalued
        "sector_avg_pe": 20,
        "peg_ratio": 3.5,  # Growth not justifying valuation
        "price_to_sales": 15,  # Very high
        "market_share_trend": -0.1,  # Losing share
        "industry_growth": -0.05  # Industry headwinds
    }


@pytest.fixture
def strong_fundamental_data():
    """Strong fundamental data (not bearish)"""
    return {
        "revenue_growth": 0.25,  # 25% growth
        "earnings_growth": 0.20,
        "return_on_equity": 0.22,
        "debt_to_equity": 0.3,  # Low debt
        "margin_trend": 0.05,  # Expanding margins
        "free_cash_flow": 5000000,  # Positive FCF
        "insider_selling_ratio": 0.5,
        "pe_ratio": 18,
        "sector_avg_pe": 20,
        "peg_ratio": 1.2,
        "price_to_sales": 3,
        "market_share_trend": 0.05,
        "industry_growth": 0.10
    }


@pytest.fixture
def bearish_technical_data():
    """Bearish technical indicators"""
    return {
        "price_change_30d": -0.20,  # -20% decline
        "volume_trend": -0.3,  # Declining volume
        "below_ma200": True,
        "death_cross": True,
        "below_support": True,
        "ma_alignment": "bearish"
    }


@pytest.fixture
def bullish_technical_data():
    """Bullish technical indicators"""
    return {
        "price_change_30d": 0.15,  # 15% gain
        "volume_trend": 0.5,
        "below_ma200": False,
        "death_cross": False,
        "below_support": False,
        "ma_alignment": "bullish"
    }


@pytest.fixture
def bearish_news():
    """Negative news data"""
    return [
        {"title": "Company faces regulatory investigation", "sentiment": "negative"},
        {"title": "SEC probe into accounting practices", "sentiment": "negative"},
        {"title": "Major competitor launches rival product", "sentiment": "negative"}
    ]


@pytest.fixture
def neutral_news():
    """Neutral news data"""
    return [
        {"title": "Company announces quarterly results", "sentiment": "neutral"}
    ]


class TestBearResearcherInitialization:
    """Test agent initialization"""

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized"""
        assert agent.agent_id == "bear_researcher_001"
        assert agent.agent_type == "bear_researcher"
        assert hasattr(agent, 'bearish_factors')
        assert isinstance(agent.bearish_factors, dict)

    def test_bearish_factors_present(self, agent):
        """Test all expected bearish factors are configured"""
        expected_factors = [
            "declining_revenue", "margin_compression", "increasing_debt",
            "market_saturation", "regulatory_risk", "competitive_threats",
            "insider_selling", "technical_breakdown", "valuation_concern",
            "macro_headwinds"
        ]

        for factor in expected_factors:
            assert factor in agent.bearish_factors
            assert 0 < agent.bearish_factors[factor] <= 1.0

    def test_factor_weights_are_reasonable(self, agent):
        """Test factor weights are in reasonable range"""
        for factor, weight in agent.bearish_factors.items():
            assert 0.5 <= weight <= 1.0  # All should be significant factors


class TestRiskFactorIdentification:
    """Test risk factor identification"""

    def test_identify_declining_revenue_risk(self, agent, weak_fundamental_data):
        """Test identification of revenue decline"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], {})

        revenue_risks = [r for r in risks if r['type'] == 'declining_revenue']
        assert len(revenue_risks) > 0
        assert revenue_risks[0]['severity'] > 0.5

    def test_identify_margin_compression(self, agent, weak_fundamental_data):
        """Test identification of margin compression"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], {})

        margin_risks = [r for r in risks if r['type'] == 'margin_compression']
        assert len(margin_risks) > 0

    def test_identify_high_debt_risk(self, agent, weak_fundamental_data):
        """Test identification of high debt levels"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], {})

        debt_risks = [r for r in risks if r['type'] == 'increasing_debt']
        assert len(debt_risks) > 0
        assert debt_risks[0]['severity'] > 0.5

    def test_identify_cash_burn(self, agent, weak_fundamental_data):
        """Test identification of negative cash flow"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], {})

        cash_risks = [r for r in risks if r['type'] == 'cash_burn']
        assert len(cash_risks) > 0
        assert cash_risks[0]['severity'] == 0.9

    def test_identify_regulatory_risk_from_news(self, agent, bearish_news):
        """Test identification of regulatory risks from news"""
        risks = agent._identify_risk_factors({}, bearish_news, {})

        reg_risks = [r for r in risks if r['type'] == 'regulatory_risk']
        assert len(reg_risks) > 0

    def test_identify_insider_selling(self, agent, weak_fundamental_data):
        """Test identification of heavy insider selling"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], {})

        insider_risks = [r for r in risks if r['type'] == 'insider_selling']
        assert len(insider_risks) > 0

    def test_no_risks_for_strong_fundamentals(self, agent, strong_fundamental_data):
        """Test strong fundamentals produce few/no risks"""
        risks = agent._identify_risk_factors(strong_fundamental_data, [], {})

        # Should have 0 or very few risks
        assert len(risks) <= 1

    def test_risk_severity_values(self, agent, weak_fundamental_data):
        """Test risk severity values are in valid range"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], {})

        for risk in risks:
            assert 'severity' in risk
            assert 0 <= risk['severity'] <= 1.0
            assert 'description' in risk


class TestValuationRisks:
    """Test valuation risk analysis"""

    def test_identify_overvaluation_vs_sector(self, agent, weak_fundamental_data, valid_market_data):
        """Test identification of sector overvaluation"""
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)

        assert 'score' in valuation
        assert valuation['score'] > 0.5
        assert "Overvalued vs sector" in valuation['concerns']

    def test_identify_extreme_valuation(self, agent, weak_fundamental_data, valid_market_data):
        """Test identification of extreme P/E"""
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)

        assert "Extreme valuation" in valuation['concerns']

    def test_identify_high_peg_ratio(self, agent, weak_fundamental_data, valid_market_data):
        """Test identification of excessive PEG ratio"""
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)

        assert "Growth not justifying valuation" in valuation['concerns']

    def test_identify_high_price_to_sales(self, agent, weak_fundamental_data, valid_market_data):
        """Test identification of excessive P/S ratio"""
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)

        assert "Excessive P/S ratio" in valuation['concerns']

    def test_fair_valuation_no_concerns(self, agent, strong_fundamental_data, valid_market_data):
        """Test fair valuation produces minimal concerns"""
        valuation = agent._analyze_valuation_risks(strong_fundamental_data, valid_market_data)

        assert valuation['score'] < 0.5
        assert len(valuation['concerns']) <= 1

    def test_overvaluation_level_calculation(self, agent, weak_fundamental_data, valid_market_data):
        """Test overvaluation level is calculated correctly"""
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)

        assert 'overvaluation_level' in valuation
        assert valuation['overvaluation_level'] in ["extreme", "high", "moderate", "fair"]

    def test_valuation_score_range(self, agent, weak_fundamental_data, valid_market_data):
        """Test valuation score is in valid range"""
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)

        assert 0 <= valuation['score'] <= 1.0


class TestTechnicalWeakness:
    """Test technical weakness identification"""

    def test_identify_below_ma200(self, agent, bearish_technical_data, valid_market_data):
        """Test identification of price below 200-day MA"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert "Below 200-day MA" in weakness['weaknesses']
        assert weakness['score'] > 0.3

    def test_identify_death_cross(self, agent, bearish_technical_data, valid_market_data):
        """Test identification of death cross pattern"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert "Death cross pattern" in weakness['weaknesses']

    def test_identify_downtrend(self, agent, bearish_technical_data, valid_market_data):
        """Test identification of strong downtrend"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert "Strong downtrend" in weakness['weaknesses']

    def test_identify_support_breakdown(self, agent, bearish_technical_data, valid_market_data):
        """Test identification of support breakdown"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert "Support level broken" in weakness['weaknesses']

    def test_identify_declining_volume(self, agent, bearish_technical_data, valid_market_data):
        """Test identification of declining volume"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert "Declining volume" in weakness['weaknesses']

    def test_bearish_trend_classification(self, agent, bearish_technical_data, valid_market_data):
        """Test bearish trend is identified"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert weakness['trend'] == "bearish"

    def test_neutral_trend_for_bullish_technicals(self, agent, bullish_technical_data, valid_market_data):
        """Test neutral/no weakness for bullish setup"""
        weakness = agent._identify_technical_weakness(bullish_technical_data, valid_market_data)

        assert weakness['score'] < 0.5
        assert weakness['trend'] == "neutral"

    def test_weakness_score_range(self, agent, bearish_technical_data, valid_market_data):
        """Test weakness score is in valid range"""
        weakness = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)

        assert 0 <= weakness['score'] <= 1.0


class TestCompetitiveThreats:
    """Test competitive threat analysis"""

    def test_identify_market_share_loss(self, agent, weak_fundamental_data):
        """Test identification of market share loss"""
        threats = agent._analyze_competitive_threats(weak_fundamental_data, [])

        assert "Losing market share" in threats['threats']
        assert threats['threat_level'] > 0.3

    def test_identify_competitive_pressure_from_news(self, agent, bearish_news):
        """Test identification of competitive threats from news"""
        threats = agent._analyze_competitive_threats({}, bearish_news)

        assert "Competitive pressure" in threats['threats']

    def test_identify_industry_headwinds(self, agent, weak_fundamental_data):
        """Test identification of industry headwinds"""
        threats = agent._analyze_competitive_threats(weak_fundamental_data, [])

        assert "Industry headwinds" in threats['threats']

    def test_no_threats_for_strong_position(self, agent, strong_fundamental_data):
        """Test strong competitive position produces few threats"""
        threats = agent._analyze_competitive_threats(strong_fundamental_data, [])

        assert len(threats['threats']) == 0
        assert threats['threat_level'] < 0.3

    def test_threat_level_range(self, agent, weak_fundamental_data):
        """Test threat level is in valid range"""
        threats = agent._analyze_competitive_threats(weak_fundamental_data, [])

        assert 0 <= threats['threat_level'] <= 1.0


class TestBearScoreCalculation:
    """Test bear score calculation"""

    def test_calculate_high_bear_score(self, agent, weak_fundamental_data,
                                      bearish_technical_data, valid_market_data, bearish_news):
        """Test high bear score with multiple risks"""
        risks = agent._identify_risk_factors(weak_fundamental_data, bearish_news, valid_market_data)
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)
        technical = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)
        competitive = agent._analyze_competitive_threats(weak_fundamental_data, bearish_news)

        bear_score = agent._calculate_bear_score(risks, valuation, technical, competitive)

        assert bear_score > 0.7  # Should be high

    def test_calculate_low_bear_score(self, agent, strong_fundamental_data,
                                     bullish_technical_data, valid_market_data):
        """Test low bear score with no risks"""
        risks = agent._identify_risk_factors(strong_fundamental_data, [], valid_market_data)
        valuation = agent._analyze_valuation_risks(strong_fundamental_data, valid_market_data)
        technical = agent._identify_technical_weakness(bullish_technical_data, valid_market_data)
        competitive = agent._analyze_competitive_threats(strong_fundamental_data, [])

        bear_score = agent._calculate_bear_score(risks, valuation, technical, competitive)

        assert bear_score < 0.3  # Should be low

    def test_bear_score_range(self, agent, weak_fundamental_data,
                             bearish_technical_data, valid_market_data):
        """Test bear score is always in valid range"""
        risks = agent._identify_risk_factors(weak_fundamental_data, [], valid_market_data)
        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)
        technical = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)
        competitive = agent._analyze_competitive_threats(weak_fundamental_data, [])

        bear_score = agent._calculate_bear_score(risks, valuation, technical, competitive)

        assert 0 <= bear_score <= 1.0

    def test_multiple_risks_boost_score(self, agent, weak_fundamental_data, strong_fundamental_data,
                                       bearish_technical_data, valid_market_data, bearish_news):
        """Test multiple risks increase bear score"""
        many_risks = agent._identify_risk_factors(weak_fundamental_data, bearish_news, valid_market_data)
        few_risks = agent._identify_risk_factors(strong_fundamental_data, [], valid_market_data)

        valuation = agent._analyze_valuation_risks(weak_fundamental_data, valid_market_data)
        technical = agent._identify_technical_weakness(bearish_technical_data, valid_market_data)
        competitive = agent._analyze_competitive_threats(weak_fundamental_data, [])

        score_many = agent._calculate_bear_score(many_risks, valuation, technical, competitive)
        score_few = agent._calculate_bear_score(few_risks, valuation, technical, competitive)

        assert score_many > score_few


class TestRecommendationGeneration:
    """Test recommendation generation"""

    def test_sell_recommendation_for_high_bear_score(self, agent):
        """Test SELL recommendation for high bear score"""
        recommendation = agent._generate_recommendation(0.8, "Multiple severe risks")

        assert recommendation['action'] == "SELL"
        assert recommendation['confidence'] > 0.7

    def test_hold_recommendation_for_low_bear_score(self, agent):
        """Test HOLD recommendation for low bear score"""
        recommendation = agent._generate_recommendation(0.3, "Limited bear case")

        assert recommendation['action'] == "HOLD"

    def test_recommendation_includes_reasoning(self, agent):
        """Test recommendation includes bear thesis"""
        recommendation = agent._generate_recommendation(0.7, "Revenue declining")

        assert 'reasoning' in recommendation
        assert "Revenue declining" in recommendation['reasoning']

    def test_recommendation_has_timeframe(self, agent):
        """Test recommendation includes timeframe"""
        recommendation = agent._generate_recommendation(0.8, "High risk")

        assert 'timeframe' in recommendation
        assert recommendation['timeframe'] in ["short", "medium", "long"]


class TestFullAnalysis:
    """Test complete analysis workflow"""

    def test_analyze_with_bearish_setup(self, agent, valid_market_data, weak_fundamental_data,
                                       bearish_technical_data, bearish_news):
        """Test analysis with strong bearish setup"""
        result = agent.analyze(
            "XYZ",
            valid_market_data,
            fundamental_data=weak_fundamental_data,
            technical_data=bearish_technical_data,
            news_data=bearish_news
        )

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'confidence' in result
        assert result['analysis']['bear_score'] > 0.6

    def test_analyze_with_bullish_setup(self, agent, valid_market_data, strong_fundamental_data,
                                       bullish_technical_data):
        """Test analysis with weak bearish case"""
        result = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data=strong_fundamental_data,
            technical_data=bullish_technical_data,
            news_data=[]
        )

        assert 'recommendation' in result
        assert result['analysis']['bear_score'] < 0.4

    def test_analyze_returns_required_fields(self, agent, valid_market_data):
        """Test analysis returns all required fields"""
        result = agent.analyze("AAPL", valid_market_data)

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'risk_assessment' in result
        assert 'confidence' in result

        assert 'bear_score' in result['analysis']
        assert 'risk_factors' in result['analysis']
        assert 'valuation_risks' in result['analysis']
        assert 'technical_weakness' in result['analysis']

    def test_analyze_handles_missing_optional_data(self, agent, valid_market_data):
        """Test analysis works without optional data"""
        result = agent.analyze("AAPL", valid_market_data)

        assert result is not None
        assert 'bear_score' in result['analysis']

    def test_confidence_increases_with_risks(self, agent, valid_market_data,
                                            weak_fundamental_data, bearish_news):
        """Test confidence increases with more risks"""
        result_many = agent.analyze(
            "XYZ",
            valid_market_data,
            fundamental_data=weak_fundamental_data,
            news_data=bearish_news
        )

        result_few = agent.analyze(
            "XYZ",
            valid_market_data,
            fundamental_data={},
            news_data=[]
        )

        assert result_many['confidence'] > result_few['confidence']

    def test_bear_thesis_generation(self, agent, valid_market_data, weak_fundamental_data):
        """Test bear thesis is generated"""
        result = agent.analyze(
            "XYZ",
            valid_market_data,
            fundamental_data=weak_fundamental_data
        )

        assert 'bear_thesis' in result['analysis']
        assert len(result['analysis']['bear_thesis']) > 0


class TestRiskAssessment:
    """Test risk assessment from bear perspective"""

    def test_high_risk_for_strong_bear_case(self, agent):
        """Test high risk rating for strong bear case"""
        risk_assessment = agent._assess_bearish_risk(0.8, [{"severity": 0.9}] * 4)

        assert risk_assessment['risk_level'] == "HIGH"
        assert risk_assessment['position_size_pct'] == 0.0

    def test_medium_risk_for_moderate_bear_case(self, agent):
        """Test medium risk rating"""
        risk_assessment = agent._assess_bearish_risk(0.5, [{"severity": 0.5}] * 2)

        assert risk_assessment['risk_level'] == "MEDIUM"
        assert risk_assessment['position_size_pct'] > 0

    def test_tight_stop_loss(self, agent):
        """Test bears use tight stop losses"""
        risk_assessment = agent._assess_bearish_risk(0.7, [])

        # Bears use 3% stops (tight)
        assert risk_assessment['stop_loss'] == 97.0

    def test_risk_assessment_includes_volatility(self, agent):
        """Test risk assessment includes volatility estimate"""
        risk_assessment = agent._assess_bearish_risk(0.6, [])

        assert 'volatility' in risk_assessment
        assert risk_assessment['volatility'] > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_analyze_with_empty_market_data(self, agent):
        """Test analysis handles empty market data"""
        result = agent.analyze("AAPL", {})

        # Should still return valid result structure
        assert 'recommendation' in result or 'error' in result

    def test_analyze_with_none_values(self, agent, valid_market_data):
        """Test analysis handles None values in data"""
        result = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data={"revenue_growth": None},
            technical_data={"price_change_30d": None}
        )

        assert result is not None

    def test_analyze_with_extreme_values(self, agent, valid_market_data):
        """Test analysis handles extreme values"""
        extreme_data = {
            "revenue_growth": -1.0,  # -100% (bankruptcy)
            "debt_to_equity": 10.0,  # 10x debt
            "pe_ratio": 500  # Extreme valuation
        }

        result = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data=extreme_data
        )

        # Should cap scores at 1.0
        assert result['analysis']['bear_score'] <= 1.0

    def test_multiple_analyses_independent(self, agent, valid_market_data):
        """Test multiple analyses don't interfere with each other"""
        result1 = agent.analyze("AAPL", valid_market_data)
        result2 = agent.analyze("MSFT", valid_market_data)

        # Results should be independent
        assert result1 is not result2

    def test_overvaluation_level_classification(self, agent):
        """Test overvaluation level classification"""
        assert agent._calculate_overvaluation(60, 4) == "extreme"
        assert agent._calculate_overvaluation(35, 2.5) == "high"
        assert agent._calculate_overvaluation(25, 1.7) == "moderate"
        assert agent._calculate_overvaluation(15, 1.0) == "fair"
