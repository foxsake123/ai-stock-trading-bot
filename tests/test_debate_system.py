"""
Comprehensive Tests for Bull/Bear Debate System
Tests debate orchestration, analyst argument generation, and moderation
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict

from src.agents.debate_orchestrator import (
    DebateOrchestrator,
    DebatePosition,
    DebateRound,
    DebateArgument,
    DebateConclusion,
    DebateHistory
)
from src.agents.bull_analyst import BullAnalyst
from src.agents.bear_analyst import BearAnalyst
from src.agents.neutral_moderator import NeutralModerator


# Test Fixtures

@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    mock_response = Mock()
    mock_content = Mock()
    mock_content.text = """This is a compelling argument with data citations [P/E: 18.5x] and [Revenue: $100M, +25% YoY].
The thesis is supported by strong fundamentals and technical momentum."""
    mock_response.content = [mock_content]
    return mock_response


@pytest.fixture
def mock_moderator_response():
    """Mock moderator evaluation response"""
    mock_response = Mock()
    mock_content = Mock()
    mock_content.text = """FINAL_POSITION: LONG
CONFIDENCE: 75
BULL_SCORE: 85
BEAR_SCORE: 60

KEY_ARGUMENTS:
- Strong revenue growth of 25% YoY
- P/E ratio attractive at 18.5x
- Positive technical momentum

RISK_FACTORS:
- Market volatility
- Sector competition
- Regulatory concerns

DEBATE_SUMMARY:
The bull case presents stronger arguments with better data support. Revenue growth and valuation metrics favor a long position with moderate confidence."""
    mock_response.content = [mock_content]
    return mock_response


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        'price': 150.00,
        'volume': 1000000,
        'market_cap': '50B',
        'sector': 'Technology'
    }


@pytest.fixture
def sample_fundamental_data():
    """Sample fundamental data for testing"""
    return {
        'revenue': '100M',
        'revenue_growth': '25%',
        'pe_ratio': 18.5,
        'debt_to_equity': 0.5
    }


@pytest.fixture
def sample_technical_data():
    """Sample technical data for testing"""
    return {
        'rsi': 65,
        'macd': 'bullish',
        'trend': 'uptrend',
        'support': 145,
        'resistance': 160
    }


# Test DebateArgument Dataclass

class TestDebateArgument:
    """Test DebateArgument dataclass"""

    def test_create_opening_argument(self):
        """Test creating opening argument"""
        arg = DebateArgument(
            round_type=DebateRound.OPENING,
            side='bull',
            argument="Test argument",
            data_citations=["P/E: 18.5x"]
        )

        assert arg.round_type == DebateRound.OPENING
        assert arg.side == 'bull'
        assert arg.argument == "Test argument"
        assert len(arg.data_citations) == 1
        assert isinstance(arg.timestamp, datetime)

    def test_create_rebuttal_argument(self):
        """Test creating rebuttal argument"""
        arg = DebateArgument(
            round_type=DebateRound.REBUTTAL,
            side='bear',
            argument="Counter argument",
            data_citations=["Debt: $500M", "Margin: -5%"]
        )

        assert arg.round_type == DebateRound.REBUTTAL
        assert arg.side == 'bear'
        assert len(arg.data_citations) == 2


# Test DebateConclusion Dataclass

class TestDebateConclusion:
    """Test DebateConclusion dataclass"""

    def test_create_long_conclusion(self):
        """Test creating LONG position conclusion"""
        conclusion = DebateConclusion(
            ticker="AAPL",
            final_position=DebatePosition.LONG,
            confidence=75.0,
            bull_score=85.0,
            bear_score=60.0,
            key_arguments=["Strong growth", "Low valuation"],
            risk_factors=["Market risk", "Competition"],
            debate_summary="Bull case stronger"
        )

        assert conclusion.ticker == "AAPL"
        assert conclusion.final_position == DebatePosition.LONG
        assert conclusion.confidence == 75.0
        assert conclusion.bull_score > conclusion.bear_score
        assert len(conclusion.key_arguments) == 2
        assert len(conclusion.risk_factors) == 2

    def test_create_neutral_conclusion(self):
        """Test creating NEUTRAL position conclusion"""
        conclusion = DebateConclusion(
            ticker="TSLA",
            final_position=DebatePosition.NEUTRAL,
            confidence=45.0,
            bull_score=55.0,
            bear_score=50.0,
            key_arguments=["Mixed signals"],
            risk_factors=["High uncertainty"],
            debate_summary="No clear winner"
        )

        assert conclusion.final_position == DebatePosition.NEUTRAL
        assert conclusion.confidence < 60.0


# Test BullAnalyst

class TestBullAnalyst:
    """Test BullAnalyst argument generation"""

    @pytest.mark.asyncio
    async def test_generate_opening_argument(
        self,
        mock_anthropic_response,
        sample_market_data,
        sample_fundamental_data,
        sample_technical_data
    ):
        """Test generating bull opening argument"""
        with patch('anthropic.Anthropic') as mock_client:
            mock_client.return_value.messages.create = AsyncMock(return_value=mock_anthropic_response)

            analyst = BullAnalyst(api_key="test_key")

            debate_context = {
                'ticker': 'AAPL',
                'market_data': sample_market_data,
                'fundamental_data': sample_fundamental_data,
                'technical_data': sample_technical_data
            }

            argument = await analyst.generate_opening_argument(debate_context)

            assert isinstance(argument, DebateArgument)
            assert argument.round_type == DebateRound.OPENING
            assert argument.side == 'bull'
            assert len(argument.argument) > 0
            assert len(argument.data_citations) >= 2  # Should extract [P/E: 18.5x] and [Revenue: ...]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
