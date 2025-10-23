"""
Unit tests for BaseAgent class
Tests the abstract base agent functionality
"""

import pytest
from datetime import datetime
from src.agents.base_agent import BaseAgent


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing abstract BaseAgent"""

    def analyze(self, ticker: str, market_data: dict, **kwargs) -> dict:
        """Concrete implementation of analyze method"""
        if not self.validate_market_data(market_data):
            return {"error": "Invalid market data"}

        return {
            "recommendation": {
                "action": "BUY",
                "quantity": 100,
                "price": market_data.get("price")
            },
            "analysis": {
                "signal_strength": "STRONG"
            },
            "risk_assessment": {
                "risk_level": "MEDIUM"
            },
            "confidence": 0.85
        }


@pytest.fixture
def agent():
    """Create a test agent instance"""
    return ConcreteAgent(agent_id="test_agent_001", agent_type="test_trader")


@pytest.fixture
def valid_market_data():
    """Sample valid market data"""
    return {
        "price": 150.00,
        "volume": 1000000,
        "market_cap": 1000000000,
        "high": 152.00,
        "low": 148.00
    }


@pytest.fixture
def invalid_market_data():
    """Sample invalid market data (missing required fields)"""
    return {
        "price": 150.00,
        "high": 152.00
        # Missing: volume, market_cap
    }


class TestBaseAgentInitialization:
    """Test agent initialization and basic attributes"""

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized"""
        assert agent.agent_id == "test_agent_001"
        assert agent.agent_type == "test_trader"
        assert isinstance(agent.timestamp, datetime)
        assert agent.logger is not None

    def test_agent_info(self, agent):
        """Test get_agent_info returns correct metadata"""
        info = agent.get_agent_info()
        assert info["agent_id"] == "test_agent_001"
        assert info["agent_type"] == "test_trader"
        assert "created_at" in info
        assert isinstance(info["created_at"], str)


class TestMarketDataValidation:
    """Test market data validation"""

    def test_validate_valid_market_data(self, agent, valid_market_data):
        """Test validation passes for valid data"""
        assert agent.validate_market_data(valid_market_data) is True

    def test_validate_invalid_market_data(self, agent, invalid_market_data):
        """Test validation fails for invalid data"""
        assert agent.validate_market_data(invalid_market_data) is False

    def test_validate_empty_market_data(self, agent):
        """Test validation fails for empty data"""
        assert agent.validate_market_data({}) is False

    def test_validate_none_market_data(self, agent):
        """Test validation handles None gracefully"""
        with pytest.raises(TypeError):
            agent.validate_market_data(None)


class TestAnalysis:
    """Test analysis functionality"""

    def test_analyze_with_valid_data(self, agent, valid_market_data):
        """Test analysis works with valid market data"""
        result = agent.analyze("AAPL", valid_market_data)
        assert "recommendation" in result
        assert "analysis" in result
        assert "confidence" in result
        assert result["confidence"] == 0.85

    def test_analyze_with_invalid_data(self, agent, invalid_market_data):
        """Test analysis handles invalid data"""
        result = agent.analyze("AAPL", invalid_market_data)
        assert "error" in result

    def test_analyze_returns_proper_structure(self, agent, valid_market_data):
        """Test analysis returns expected structure"""
        result = agent.analyze("AAPL", valid_market_data)
        assert isinstance(result, dict)
        assert "recommendation" in result
        assert "action" in result["recommendation"]
        assert result["recommendation"]["action"] in ["BUY", "SELL", "HOLD"]


class TestReportGeneration:
    """Test report generation"""

    def test_generate_report_structure(self, agent, valid_market_data):
        """Test generated report has correct structure"""
        analysis = agent.analyze("AAPL", valid_market_data)
        report = agent.generate_report("AAPL", analysis)

        assert "agent_id" in report
        assert "agent_type" in report
        assert "timestamp" in report
        assert "ticker" in report
        assert "recommendation" in report
        assert "analysis" in report
        assert "confidence" in report

    def test_generate_report_values(self, agent, valid_market_data):
        """Test generated report has correct values"""
        analysis = agent.analyze("AAPL", valid_market_data)
        report = agent.generate_report("AAPL", analysis)

        assert report["agent_id"] == "test_agent_001"
        assert report["agent_type"] == "test_trader"
        assert report["ticker"] == "AAPL"
        assert report["confidence"] == 0.85

    def test_generate_report_with_empty_analysis(self, agent):
        """Test report generation with empty analysis"""
        report = agent.generate_report("AAPL", {})

        assert report["ticker"] == "AAPL"
        assert report["confidence"] == 0.0
        assert report["recommendation"] == {}
        assert report["analysis"] == {}

    def test_generate_report_timestamp_format(self, agent, valid_market_data):
        """Test report timestamp is ISO format"""
        analysis = agent.analyze("AAPL", valid_market_data)
        report = agent.generate_report("AAPL", analysis)

        # Verify it's a valid ISO timestamp
        timestamp = datetime.fromisoformat(report["timestamp"])
        assert isinstance(timestamp, datetime)


class TestLogging:
    """Test logging functionality"""

    def test_log_analysis(self, agent, valid_market_data, caplog):
        """Test analysis logging"""
        import logging
        caplog.set_level(logging.INFO)

        result = agent.analyze("AAPL", valid_market_data)
        agent.log_analysis("AAPL", result)

        # Check log contains expected information
        assert "AAPL" in caplog.text or len(caplog.records) > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_multiple_agents_independent(self):
        """Test multiple agent instances are independent"""
        agent1 = ConcreteAgent("agent_001", "trader")
        agent2 = ConcreteAgent("agent_002", "trader")

        assert agent1.agent_id != agent2.agent_id
        assert agent1.timestamp != agent2.timestamp

    def test_agent_with_special_characters_in_id(self):
        """Test agent handles special characters in ID"""
        agent = ConcreteAgent("agent-001_test", "trader@v2")
        assert agent.agent_id == "agent-001_test"
        assert agent.agent_type == "trader@v2"

    def test_analyze_with_extra_kwargs(self, agent, valid_market_data):
        """Test analyze handles extra kwargs"""
        result = agent.analyze(
            "AAPL",
            valid_market_data,
            extra_param="value",
            another_param=123
        )
        assert "recommendation" in result
