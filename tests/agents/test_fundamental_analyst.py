"""
Comprehensive tests for Fundamental Analyst Agent
Tests financial analysis, valuation metrics, and recommendation generation
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.fundamental_analyst import FundamentalAnalystAgent


class TestFundamentalAnalystInit:
    """Test fundamental analyst initialization"""

    def test_agent_initialization(self):
        """Test agent initializes with correct parameters"""
        agent = FundamentalAnalystAgent()

        assert agent.agent_id == "fundamental_analyst_001"
        assert agent.agent_type == "fundamental_analyst"

    def test_valuation_thresholds_set(self):
        """Test valuation thresholds are properly set"""
        agent = FundamentalAnalystAgent()

        assert agent.pe_ratio_max == 30
        assert agent.peg_ratio_max == 2.0
        assert agent.debt_to_equity_max == 2.0
        assert agent.current_ratio_min == 1.0

    def test_agent_has_logger(self):
        """Test agent has logger initialized"""
        agent = FundamentalAnalystAgent()

        assert hasattr(agent, 'logger')
        assert agent.logger is not None


class TestExtractFinancialMetrics:
    """Test financial metrics extraction"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_extract_metrics_structure(self, agent):
        """Test metrics extraction returns correct structure"""
        info = {
            'trailingPE': 25.5,
            'forwardPE': 22.0,
            'pegRatio': 1.5,
            'debtToEquity': 0.8,
            'currentRatio': 2.0
        }

        metrics = agent._extract_financial_metrics(info)

        assert 'pe_ratio' in metrics
        assert 'forward_pe' in metrics
        assert 'peg_ratio' in metrics
        assert 'debt_to_equity' in metrics
        assert 'current_ratio' in metrics

    def test_extract_metrics_with_defaults(self, agent):
        """Test metrics extraction uses defaults for missing data"""
        info = {}

        metrics = agent._extract_financial_metrics(info)

        assert metrics['pe_ratio'] == 0
        assert metrics['peg_ratio'] == 0
        assert metrics['current_ratio'] == 1
        assert metrics['quick_ratio'] == 1

    def test_extract_all_required_metrics(self, agent):
        """Test all required metrics are extracted"""
        info = {
            'trailingPE': 20,
            'forwardPE': 18,
            'pegRatio': 1.2,
            'priceToBook': 3.0,
            'debtToEquity': 1.0,
            'currentRatio': 1.5,
            'quickRatio': 1.2,
            'grossMargins': 0.4,
            'operatingMargins': 0.25,
            'profitMargins': 0.15,
            'returnOnEquity': 0.18,
            'returnOnAssets': 0.08,
            'revenueGrowth': 0.12,
            'earningsGrowth': 0.15,
            'freeCashflow': 1000000000,
            'marketCap': 50000000000,
            'enterpriseValue': 55000000000,
            'beta': 1.2
        }

        metrics = agent._extract_financial_metrics(info)

        assert len(metrics) == 18  # Actual number of metrics extracted
        assert metrics['pe_ratio'] == 20
        assert metrics['return_on_equity'] == 0.18
        assert metrics['revenue_growth'] == 0.12


class TestValuationAnalysis:
    """Test valuation analysis"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_valuation_low_pe_ratio(self, agent):
        """Test valuation with low P/E ratio (good value)"""
        metrics = {'pe_ratio': 15, 'peg_ratio': 1.0, 'price_to_book': 2.0, 'forward_pe': 0}

        score = agent._analyze_valuation(metrics)

        assert score > 0.45  # Good value score with weighted components

    def test_valuation_high_pe_ratio(self, agent):
        """Test valuation with high P/E ratio (expensive)"""
        metrics = {'pe_ratio': 50, 'peg_ratio': 0, 'price_to_book': 0, 'forward_pe': 0}

        score = agent._analyze_valuation(metrics)

        assert score < 0.3  # Should indicate expensive

    def test_valuation_good_peg_ratio(self, agent):
        """Test valuation with good PEG ratio"""
        metrics = {'pe_ratio': 0, 'peg_ratio': 1.0, 'price_to_book': 0, 'forward_pe': 0}

        score = agent._analyze_valuation(metrics)

        assert score > 0.4

    def test_valuation_improving_earnings(self, agent):
        """Test valuation with improving earnings (forward PE < trailing PE)"""
        metrics = {'pe_ratio': 25, 'peg_ratio': 0, 'price_to_book': 0, 'forward_pe': 20}

        score = agent._analyze_valuation(metrics)

        # Forward PE improvement contributes to score
        assert score > 0.15  # Based on actual calculation with weighted components

    def test_valuation_no_data(self, agent):
        """Test valuation with no data returns neutral"""
        metrics = {'pe_ratio': 0, 'peg_ratio': 0, 'price_to_book': 0, 'forward_pe': 0}

        score = agent._analyze_valuation(metrics)

        assert score == 0.5  # Neutral score


class TestFinancialHealthAnalysis:
    """Test financial health analysis"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_health_low_debt(self, agent):
        """Test health analysis with low debt"""
        metrics = {
            'debt_to_equity': 0.5,
            'current_ratio': 2.0,
            'profit_margin': 0.15,
            'return_on_equity': 0.18
        }

        score = agent._analyze_financial_health(metrics)

        assert score > 0.7  # Strong health

    def test_health_high_debt(self, agent):
        """Test health analysis with high debt"""
        metrics = {
            'debt_to_equity': 3.0,
            'current_ratio': 0.8,
            'profit_margin': 0.05,
            'return_on_equity': 0.05
        }

        score = agent._analyze_financial_health(metrics)

        assert score < 0.4  # Poor health

    def test_health_strong_liquidity(self, agent):
        """Test health with strong current ratio"""
        metrics = {
            'debt_to_equity': 0,
            'current_ratio': 3.0,
            'profit_margin': 0,
            'return_on_equity': 0
        }

        score = agent._analyze_financial_health(metrics)

        # High current ratio should contribute positively
        assert score > 0.4

    def test_health_high_profitability(self, agent):
        """Test health with high profit margin"""
        metrics = {
            'debt_to_equity': 0,
            'current_ratio': 0,
            'profit_margin': 0.25,
            'return_on_equity': 0.20
        }

        score = agent._analyze_financial_health(metrics)

        # High profitability should boost score
        assert score > 0.5


class TestGrowthAnalysis:
    """Test growth prospects analysis"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_growth_high_revenue_growth(self, agent):
        """Test growth with high revenue growth"""
        metrics = {
            'revenue_growth': 0.25,
            'earnings_growth': 0.30,
            'free_cash_flow': 1000000000
        }

        score = agent._analyze_growth(metrics)

        assert score > 0.8  # Strong growth

    def test_growth_negative_revenue_growth(self, agent):
        """Test growth with declining revenue"""
        metrics = {
            'revenue_growth': -0.10,
            'earnings_growth': -0.05,
            'free_cash_flow': 0
        }

        score = agent._analyze_growth(metrics)

        assert score < 0.3  # Poor growth

    def test_growth_positive_fcf(self, agent):
        """Test growth with positive free cash flow"""
        metrics = {
            'revenue_growth': 0,
            'earnings_growth': 0,
            'free_cash_flow': 500000000
        }

        score = agent._analyze_growth(metrics)

        # Positive FCF should contribute
        assert score > 0.4

    def test_growth_no_data(self, agent):
        """Test growth with no data returns neutral"""
        metrics = {
            'revenue_growth': 0,
            'earnings_growth': 0,
            'free_cash_flow': 0
        }

        score = agent._analyze_growth(metrics)

        assert score == 0.5  # Neutral


class TestFundamentalScore:
    """Test overall fundamental score calculation"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_calculate_fundamental_score_balanced(self, agent):
        """Test fundamental score with balanced components"""
        score = agent._calculate_fundamental_score(0.8, 0.7, 0.6)

        # Weighted: 0.8*0.35 + 0.7*0.35 + 0.6*0.3 = 0.28 + 0.245 + 0.18 = 0.705
        assert 0.7 <= score <= 0.71

    def test_calculate_fundamental_score_all_high(self, agent):
        """Test fundamental score with all components high"""
        score = agent._calculate_fundamental_score(0.9, 0.9, 0.9)

        assert score == 0.9

    def test_calculate_fundamental_score_all_low(self, agent):
        """Test fundamental score with all components low"""
        score = agent._calculate_fundamental_score(0.2, 0.3, 0.1)

        assert score < 0.3


class TestRecommendationGeneration:
    """Test recommendation generation"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_recommendation_strong_buy(self, agent):
        """Test BUY recommendation for high score"""
        metrics = {'pe_ratio': 15, 'revenue_growth': 0.2, 'debt_to_equity': 0.3}

        recommendation = agent._generate_recommendation(0.75, metrics)

        assert recommendation['action'] == 'BUY'
        assert recommendation['confidence'] >= 0.75
        assert recommendation['timeframe'] == 'long'

    def test_recommendation_hold(self, agent):
        """Test HOLD recommendation for neutral score"""
        metrics = {'pe_ratio': 25, 'revenue_growth': 0.05, 'debt_to_equity': 1.0}

        recommendation = agent._generate_recommendation(0.55, metrics)

        assert recommendation['action'] == 'HOLD'
        assert recommendation['confidence'] == 0.5
        assert recommendation['timeframe'] == 'medium'

    def test_recommendation_sell(self, agent):
        """Test SELL recommendation for low score"""
        metrics = {'pe_ratio': 50, 'revenue_growth': -0.1, 'debt_to_equity': 3.0}

        recommendation = agent._generate_recommendation(0.3, metrics)

        assert recommendation['action'] == 'SELL'
        assert recommendation['timeframe'] == 'medium'

    def test_recommendation_includes_reasoning(self, agent):
        """Test recommendation includes reasoning"""
        metrics = {'pe_ratio': 15, 'revenue_growth': 0.25, 'debt_to_equity': 0.2}

        recommendation = agent._generate_recommendation(0.8, metrics)

        assert 'reasoning' in recommendation
        assert isinstance(recommendation['reasoning'], str)
        assert len(recommendation['reasoning']) > 0


class TestRiskAssessment:
    """Test fundamental risk assessment"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_risk_assessment_low_risk(self, agent):
        """Test risk assessment for low-risk stock"""
        metrics = {
            'debt_to_equity': 0.3,
            'pe_ratio': 20,
            'beta': 0.8,
            'current_price': 100
        }

        risk = agent._assess_fundamental_risk(metrics)

        assert risk['risk_level'] == 'LOW'
        assert risk['position_size_pct'] > 0.03

    def test_risk_assessment_high_risk(self, agent):
        """Test risk assessment for high-risk stock"""
        metrics = {
            'debt_to_equity': 4.0,
            'pe_ratio': 60,
            'beta': 2.0,
            'current_price': 100
        }

        risk = agent._assess_fundamental_risk(metrics)

        assert risk['risk_level'] == 'HIGH'
        assert risk['position_size_pct'] < 0.02

    def test_risk_assessment_includes_stop_loss(self, agent):
        """Test risk assessment includes stop loss"""
        metrics = {
            'debt_to_equity': 1.0,
            'pe_ratio': 25,
            'beta': 1.2,
            'current_price': 100
        }

        risk = agent._assess_fundamental_risk(metrics)

        assert 'stop_loss' in risk
        assert risk['stop_loss'] < 100  # Should be below current price
        assert 'take_profit' in risk
        assert risk['take_profit'] > 100  # Should be above current price

    def test_risk_assessment_volatility_affects_stop(self, agent):
        """Test that higher beta increases stop loss distance"""
        low_beta_metrics = {'debt_to_equity': 1.0, 'pe_ratio': 25, 'beta': 0.5, 'current_price': 100}
        high_beta_metrics = {'debt_to_equity': 1.0, 'pe_ratio': 25, 'beta': 2.0, 'current_price': 100}

        low_beta_risk = agent._assess_fundamental_risk(low_beta_metrics)
        high_beta_risk = agent._assess_fundamental_risk(high_beta_metrics)

        # Higher beta should have wider stop loss
        assert (100 - high_beta_risk['stop_loss']) > (100 - low_beta_risk['stop_loss'])


class TestKeyFactors:
    """Test key factors identification"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_identify_attractive_pe(self, agent):
        """Test identification of attractive P/E ratio"""
        metrics = {'pe_ratio': 15}

        factors = agent._identify_key_factors(metrics, 0.7)

        assert any('P/E' in factor for factor in factors)

    def test_identify_strong_growth(self, agent):
        """Test identification of strong revenue growth"""
        metrics = {'revenue_growth': 0.20}

        factors = agent._identify_key_factors(metrics, 0.7)

        assert any('revenue growth' in factor for factor in factors)

    def test_identify_low_debt(self, agent):
        """Test identification of low debt"""
        metrics = {'debt_to_equity': 0.3}

        factors = agent._identify_key_factors(metrics, 0.7)

        assert any('debt' in factor.lower() for factor in factors)

    def test_identify_high_roe(self, agent):
        """Test identification of high ROE"""
        metrics = {'return_on_equity': 0.20}

        factors = agent._identify_key_factors(metrics, 0.7)

        assert any('ROE' in factor for factor in factors)

    def test_identify_strong_score(self, agent):
        """Test identification of strong fundamental score"""
        metrics = {}

        factors = agent._identify_key_factors(metrics, 0.75)

        assert any('Strong fundamental' in factor for factor in factors)


class TestConfidenceCalculation:
    """Test confidence calculation"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_confidence_high_data_quality(self, agent):
        """Test confidence with complete data"""
        metrics = {
            'pe_ratio': 20,
            'peg_ratio': 1.5,
            'debt_to_equity': 0.8,
            'current_ratio': 2.0,
            'revenue_growth': 0.15,
            'return_on_equity': 0.18
        }

        confidence = agent._calculate_confidence(0.8, metrics)

        assert confidence > 0.7

    def test_confidence_low_data_quality(self, agent):
        """Test confidence with sparse data"""
        metrics = {
            'pe_ratio': 20,
            'peg_ratio': 0,
            'debt_to_equity': 0,
            'current_ratio': 1,
            'revenue_growth': 0,
            'return_on_equity': 0
        }

        confidence = agent._calculate_confidence(0.8, metrics)

        # Sparse data should reduce confidence
        assert confidence < 0.6

    def test_confidence_capped_at_95(self, agent):
        """Test confidence is capped at 0.95"""
        metrics = {k: 1.0 for k in ['pe_ratio', 'peg_ratio', 'debt_to_equity']}

        confidence = agent._calculate_confidence(1.0, metrics)

        assert confidence <= 0.95


class TestReasoningGeneration:
    """Test reasoning generation"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_reasoning_strong_fundamentals(self, agent):
        """Test reasoning for strong fundamentals"""
        metrics = {'pe_ratio': 12, 'revenue_growth': 0.25, 'debt_to_equity': 0.2}

        reasoning = agent._generate_reasoning(0.8, metrics)

        assert 'Strong fundamentals' in reasoning
        assert 'undervalued' in reasoning
        assert 'high growth' in reasoning
        assert 'low debt' in reasoning

    def test_reasoning_moderate_fundamentals(self, agent):
        """Test reasoning for moderate fundamentals"""
        metrics = {'pe_ratio': 20, 'revenue_growth': 0.10, 'debt_to_equity': 1.0}

        reasoning = agent._generate_reasoning(0.6, metrics)

        assert 'Moderate fundamentals' in reasoning

    def test_reasoning_weak_fundamentals(self, agent):
        """Test reasoning for weak fundamentals"""
        metrics = {'pe_ratio': 50, 'revenue_growth': -0.05, 'debt_to_equity': 3.0}

        reasoning = agent._generate_reasoning(0.3, metrics)

        assert 'Weak fundamentals' in reasoning


class TestErrorHandling:
    """Test error handling"""

    @pytest.fixture
    def agent(self):
        return FundamentalAnalystAgent()

    def test_error_result_structure(self, agent):
        """Test error result has correct structure"""
        result = agent._generate_error_result("Test error")

        assert 'recommendation' in result
        assert 'analysis' in result
        assert 'risk_assessment' in result
        assert 'confidence' in result

    def test_error_result_safe_defaults(self, agent):
        """Test error result has safe default values"""
        result = agent._generate_error_result("Test error")

        assert result['recommendation']['action'] == 'HOLD'
        assert result['recommendation']['confidence'] == 0.0
        assert result['risk_assessment']['risk_level'] == 'HIGH'
        assert result['confidence'] == 0.0

    def test_error_result_includes_message(self, agent):
        """Test error result includes error message"""
        error_msg = "Analysis failed"
        result = agent._generate_error_result(error_msg)

        assert error_msg in result['analysis']['error']


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
