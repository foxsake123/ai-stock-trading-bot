"""
Unit tests for BullResearcherAgent
Tests bullish analysis and recommendation generation
"""

import pytest
from src.agents.bull_researcher import BullResearcherAgent


@pytest.fixture
def agent():
    """Create a bull researcher agent instance"""
    return BullResearcherAgent()


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
def strong_fundamental_data():
    """Strong fundamental data for bullish case"""
    return {
        "revenue_growth": 0.25,  # 25% growth
        "earnings_growth": 0.20,  # 20% growth
        "return_on_equity": 0.22,  # 22% ROE
        "debt_to_equity": 0.3,  # Low debt
        "gross_margin_trend": 0.05,  # Expanding margins
        "international_revenue_pct": 0.25,  # Room for expansion
        "sector_avg_market_cap": 300000000000,
        "sector_avg_growth": 0.10
    }


@pytest.fixture
def weak_fundamental_data():
    """Weak fundamental data"""
    return {
        "revenue_growth": 0.05,  # Low growth
        "earnings_growth": 0.02,
        "return_on_equity": 0.08,
        "debt_to_equity": 1.5,  # High debt
        "gross_margin_trend": -0.02,  # Contracting margins
        "international_revenue_pct": 0.60,
        "sector_avg_market_cap": 600000000000,
        "sector_avg_growth": 0.15
    }


@pytest.fixture
def bullish_technical_data():
    """Bullish technical indicators"""
    return {
        "price_change_30d": 0.15,  # 15% gain
        "volume_ratio": 1.8,  # Volume surge
        "above_resistance": True,
        "ma_alignment": "bullish"
    }


@pytest.fixture
def bearish_technical_data():
    """Bearish technical indicators"""
    return {
        "price_change_30d": -0.10,  # 10% loss
        "volume_ratio": 0.8,
        "above_resistance": False,
        "ma_alignment": "bearish"
    }


@pytest.fixture
def bullish_news():
    """Positive news data"""
    return [
        {"title": "Company announces breakthrough innovation", "sentiment": "positive"},
        {"title": "Patent granted for new technology", "sentiment": "positive"},
        {"title": "Expanding into new markets", "sentiment": "positive"}
    ]


@pytest.fixture
def neutral_news():
    """Neutral news data"""
    return [
        {"title": "Company announces quarterly results", "sentiment": "neutral"}
    ]


class TestBullResearcherInitialization:
    """Test agent initialization"""

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized"""
        assert agent.agent_id == "bull_researcher_001"
        assert agent.agent_type == "bull_researcher"
        assert hasattr(agent, 'bullish_factors')
        assert isinstance(agent.bullish_factors, dict)

    def test_bullish_factors_present(self, agent):
        """Test all expected bullish factors are configured"""
        expected_factors = [
            "revenue_growth", "market_expansion", "product_innovation",
            "competitive_advantage", "insider_buying", "institutional_accumulation",
            "technical_breakout", "sector_leadership", "earnings_momentum",
            "margin_expansion"
        ]

        for factor in expected_factors:
            assert factor in agent.bullish_factors
            assert 0 < agent.bullish_factors[factor] <= 1.0

    def test_factor_weights_are_reasonable(self, agent):
        """Test factor weights are in reasonable range"""
        for factor, weight in agent.bullish_factors.items():
            assert 0.5 <= weight <= 1.0  # All should be significant factors


class TestGrowthCatalysts:
    """Test growth catalyst identification"""

    def test_identify_revenue_growth_catalyst(self, agent, strong_fundamental_data):
        """Test identification of strong revenue growth"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, [])

        revenue_catalysts = [c for c in catalysts if c['type'] == 'revenue_growth']
        assert len(revenue_catalysts) > 0
        assert revenue_catalysts[0]['strength'] > 0.5

    def test_identify_earnings_momentum(self, agent, strong_fundamental_data):
        """Test identification of earnings momentum"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, [])

        earnings_catalysts = [c for c in catalysts if c['type'] == 'earnings_momentum']
        assert len(earnings_catalysts) > 0

    def test_identify_market_expansion_opportunity(self, agent, strong_fundamental_data):
        """Test identification of international expansion opportunity"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, [])

        expansion_catalysts = [c for c in catalysts if c['type'] == 'market_expansion']
        assert len(expansion_catalysts) > 0

    def test_identify_product_innovation_from_news(self, agent, bullish_news):
        """Test identification of product innovation catalyst from news"""
        catalysts = agent._identify_growth_catalysts({}, bullish_news)

        innovation_catalysts = [c for c in catalysts if c['type'] == 'product_innovation']
        assert len(innovation_catalysts) > 0

    def test_identify_margin_expansion(self, agent, strong_fundamental_data):
        """Test identification of margin expansion catalyst"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, [])

        margin_catalysts = [c for c in catalysts if c['type'] == 'margin_expansion']
        assert len(margin_catalysts) > 0

    def test_no_catalysts_for_weak_fundamentals(self, agent, weak_fundamental_data):
        """Test weak fundamentals produce few/no catalysts"""
        catalysts = agent._identify_growth_catalysts(weak_fundamental_data, [])

        # Should have 0 or very few catalysts
        assert len(catalysts) <= 1

    def test_catalyst_strength_values(self, agent, strong_fundamental_data):
        """Test catalyst strength values are in valid range"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, [])

        for catalyst in catalysts:
            assert 'strength' in catalyst
            assert 0 <= catalyst['strength'] <= 1.0
            assert 'description' in catalyst


class TestCompetitivePosition:
    """Test competitive position analysis"""

    def test_analyze_market_leader_position(self, agent, strong_fundamental_data, valid_market_data):
        """Test identification of market leadership"""
        position = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)

        assert 'score' in position
        assert 'strengths' in position
        assert position['score'] > 0.5  # Should be strong
        assert "Market leader" in position['strengths']

    def test_analyze_high_roe_strength(self, agent, strong_fundamental_data, valid_market_data):
        """Test identification of high ROE strength"""
        position = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)

        assert "High ROE" in position['strengths']

    def test_analyze_above_sector_growth(self, agent, strong_fundamental_data, valid_market_data):
        """Test identification of above-sector growth"""
        position = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)

        assert "Above-sector growth" in position['strengths']

    def test_analyze_strong_balance_sheet(self, agent, strong_fundamental_data, valid_market_data):
        """Test identification of strong balance sheet"""
        position = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)

        assert "Strong balance sheet" in position['strengths']

    def test_weak_competitive_position(self, agent, weak_fundamental_data, valid_market_data):
        """Test weak competitive position"""
        weak_market_data = valid_market_data.copy()
        weak_market_data['market_cap'] = 100000000000  # Below sector avg

        position = agent._analyze_competitive_position(weak_fundamental_data, weak_market_data)

        assert position['score'] <= 0.7  # Should be weak/neutral
        assert len(position['strengths']) <= 2

    def test_competitive_score_range(self, agent, strong_fundamental_data, valid_market_data):
        """Test competitive score is in valid range"""
        position = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)

        assert 0 <= position['score'] <= 1.0

    def test_moat_rating_present(self, agent, strong_fundamental_data, valid_market_data):
        """Test moat rating is calculated"""
        position = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)

        assert 'moat_rating' in position


class TestMomentumFactors:
    """Test momentum factor identification"""

    def test_identify_strong_price_momentum(self, agent, bullish_technical_data, valid_market_data):
        """Test identification of strong price momentum"""
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        assert momentum['score'] > 0.5
        assert "Strong price momentum" in momentum['factors']

    def test_identify_volume_surge(self, agent, bullish_technical_data, valid_market_data):
        """Test identification of volume surge"""
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        assert "Increasing volume" in momentum['factors']

    def test_identify_technical_breakout(self, agent, bullish_technical_data, valid_market_data):
        """Test identification of technical breakout"""
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        assert "Technical breakout" in momentum['factors']

    def test_identify_bullish_ma_alignment(self, agent, bullish_technical_data, valid_market_data):
        """Test identification of bullish MA alignment"""
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        assert "Bullish MA alignment" in momentum['factors']

    def test_bullish_trend_classification(self, agent, bullish_technical_data, valid_market_data):
        """Test bullish trend is identified"""
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        assert momentum['trend'] == "bullish"

    def test_weak_momentum(self, agent, bearish_technical_data, valid_market_data):
        """Test weak/bearish momentum"""
        momentum = agent._identify_momentum_factors(bearish_technical_data, valid_market_data)

        assert momentum['score'] < 0.5
        assert momentum['trend'] == "neutral"

    def test_momentum_score_range(self, agent, bullish_technical_data, valid_market_data):
        """Test momentum score is in valid range"""
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        assert 0 <= momentum['score'] <= 1.0


class TestBullScoreCalculation:
    """Test bull score calculation"""

    def test_calculate_high_bull_score(self, agent, strong_fundamental_data,
                                      bullish_technical_data, valid_market_data, bullish_news):
        """Test high bull score with strong catalysts"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, bullish_news)
        competitive = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        bull_score = agent._calculate_bull_score(catalysts, competitive, momentum)

        assert bull_score > 0.7  # Should be high

    def test_calculate_low_bull_score(self, agent, weak_fundamental_data,
                                     bearish_technical_data, valid_market_data):
        """Test low bull score with weak catalysts"""
        catalysts = agent._identify_growth_catalysts(weak_fundamental_data, [])

        weak_market = valid_market_data.copy()
        weak_market['market_cap'] = 100000000000
        competitive = agent._analyze_competitive_position(weak_fundamental_data, weak_market)
        momentum = agent._identify_momentum_factors(bearish_technical_data, valid_market_data)

        bull_score = agent._calculate_bull_score(catalysts, competitive, momentum)

        assert bull_score < 0.5  # Should be low

    def test_bull_score_range(self, agent, strong_fundamental_data,
                             bullish_technical_data, valid_market_data):
        """Test bull score is always in valid range"""
        catalysts = agent._identify_growth_catalysts(strong_fundamental_data, [])
        competitive = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        bull_score = agent._calculate_bull_score(catalysts, competitive, momentum)

        assert 0 <= bull_score <= 1.0

    def test_multiple_catalysts_boost_score(self, agent, strong_fundamental_data,
                                           weak_fundamental_data, bullish_technical_data,
                                           valid_market_data, bullish_news):
        """Test multiple catalysts increase score"""
        many_catalysts = agent._identify_growth_catalysts(strong_fundamental_data, bullish_news)
        few_catalysts = agent._identify_growth_catalysts(weak_fundamental_data, [])

        competitive = agent._analyze_competitive_position(strong_fundamental_data, valid_market_data)
        momentum = agent._identify_momentum_factors(bullish_technical_data, valid_market_data)

        score_many = agent._calculate_bull_score(many_catalysts, competitive, momentum)
        score_few = agent._calculate_bull_score(few_catalysts, competitive, momentum)

        assert score_many > score_few


class TestFullAnalysis:
    """Test complete analysis workflow"""

    def test_analyze_with_bullish_setup(self, agent, valid_market_data, strong_fundamental_data,
                                       bullish_technical_data, bullish_news):
        """Test analysis with strong bullish setup"""
        result = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data=strong_fundamental_data,
            technical_data=bullish_technical_data,
            news_data=bullish_news
        )

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'confidence' in result
        assert result['analysis']['bull_score'] > 0.6

    def test_analyze_with_bearish_setup(self, agent, valid_market_data, weak_fundamental_data,
                                       bearish_technical_data):
        """Test analysis with weak/bearish setup"""
        result = agent.analyze(
            "XYZ",
            valid_market_data,
            fundamental_data=weak_fundamental_data,
            technical_data=bearish_technical_data,
            news_data=[]
        )

        assert 'recommendation' in result
        assert result['analysis']['bull_score'] < 0.5

    def test_analyze_returns_required_fields(self, agent, valid_market_data):
        """Test analysis returns all required fields"""
        result = agent.analyze("AAPL", valid_market_data)

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'risk_assessment' in result
        assert 'confidence' in result

        assert 'bull_score' in result['analysis']
        assert 'growth_catalysts' in result['analysis']
        assert 'competitive_strength' in result['analysis']
        assert 'momentum_factors' in result['analysis']

    def test_analyze_handles_missing_optional_data(self, agent, valid_market_data):
        """Test analysis works without optional data"""
        result = agent.analyze("AAPL", valid_market_data)

        assert result is not None
        assert 'bull_score' in result['analysis']

    def test_confidence_increases_with_catalysts(self, agent, valid_market_data,
                                                strong_fundamental_data, bullish_news):
        """Test confidence increases with more catalysts"""
        result_many = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data=strong_fundamental_data,
            news_data=bullish_news
        )

        result_few = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data={},
            news_data=[]
        )

        assert result_many['confidence'] > result_few['confidence']


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
            "revenue_growth": 10.0,  # 1000% growth
            "return_on_equity": 5.0,  # 500% ROE
            "debt_to_equity": 0.0
        }

        result = agent.analyze(
            "AAPL",
            valid_market_data,
            fundamental_data=extreme_data
        )

        # Should cap scores at 1.0
        assert result['analysis']['bull_score'] <= 1.0

    def test_multiple_analyses_independent(self, agent, valid_market_data):
        """Test multiple analyses don't interfere with each other"""
        result1 = agent.analyze("AAPL", valid_market_data)
        result2 = agent.analyze("MSFT", valid_market_data)

        # Results should be independent
        assert result1 is not result2
