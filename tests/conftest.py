"""
Pytest Configuration and Fixtures
Provides common test fixtures, mock data, and utilities for testing.
"""

import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    test_vars = {
        'ANTHROPIC_API_KEY': 'test_anthropic_key_12345',
        'ALPACA_API_KEY': 'test_alpaca_key',
        'ALPACA_SECRET_KEY': 'test_alpaca_secret',
        'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
        'EMAIL_ENABLED': 'false',
        'EMAIL_SENDER': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password',
        'EMAIL_RECIPIENT': 'recipient@example.com',
        'SLACK_WEBHOOK': 'https://hooks.slack.com/services/TEST',
        'DISCORD_WEBHOOK': 'https://discord.com/api/webhooks/TEST',
    }

    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

    return test_vars


@pytest.fixture
def mock_trading_date():
    """Mock trading date for consistent testing."""
    # Use a known trading day (Monday, October 14, 2025)
    return datetime(2025, 10, 14, 18, 0, 0)


@pytest.fixture
def mock_market_data():
    """Mock market data response."""
    return {
        '^VIX': {
            'name': 'VIX Index',
            'current_price': 15.23,
            'change_percent': -2.45,
            'after_hours_price': None
        },
        'ES=F': {
            'name': 'S&P 500 Futures',
            'current_price': 4520.50,
            'change_percent': 0.27,
            'after_hours_price': None
        },
        'NQ=F': {
            'name': 'Nasdaq Futures',
            'current_price': 15890.75,
            'change_percent': 0.29,
            'after_hours_price': None
        },
        'RTY=F': {
            'name': 'Russell 2000 Futures',
            'current_price': 2050.30,
            'change_percent': -0.25,
            'after_hours_price': None
        },
        'DX-Y.NYB': {
            'name': 'Dollar Index',
            'current_price': 103.45,
            'change_percent': 0.15,
            'after_hours_price': None
        },
        '^TNX': {
            'name': '10-Year Treasury Yield',
            'current_price': 4.25,
            'change_percent': 1.19,
            'after_hours_price': None
        },
    }


@pytest.fixture
def mock_stock_recommendations():
    """Mock stock recommendations DataFrame data."""
    return [
        {
            'Ticker': 'SNDX',
            'Strategy': 'SHORGAN',
            'Catalyst': 'Oct 25 PDUFA for Revuforj',
            'Risk': 9,
            'Conviction': 9
        },
        {
            'Ticker': 'GKOS',
            'Strategy': 'SHORGAN',
            'Catalyst': 'Oct 20 PDUFA for Epioxa',
            'Risk': 7,
            'Conviction': 7
        },
        {
            'Ticker': 'DUK',
            'Strategy': 'DEE',
            'Catalyst': 'Long-term defensive utility',
            'Risk': 8,
            'Conviction': 8
        },
        {
            'Ticker': 'ED',
            'Strategy': 'DEE',
            'Catalyst': 'Long-term defensive utility',
            'Risk': 9,
            'Conviction': 9
        },
    ]


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = """# Pre-Market Trading Report
**Date:** October 14, 2025
**Generated:** October 13, 2025 at 06:00 PM EDT

## SHORGAN-BOT Recommendations

### SNDX
- **Catalyst**: Oct 25 PDUFA for Revuforj
- **Risk Score**: 9/10
- **Conviction Score**: 9/10

## DEE-BOT Recommendations

### DUK
- **Strategy**: Long-term defensive utility
- **Risk Score**: 8/10
- **Conviction Score**: 8/10
"""
    return mock_response


@pytest.fixture
def mock_alpaca_account():
    """Mock Alpaca account response."""
    mock_account = MagicMock()
    mock_account.portfolio_value = '100000.00'
    mock_account.cash = '50000.00'
    mock_account.buying_power = '50000.00'
    mock_account.equity = '100000.00'
    return mock_account


@pytest.fixture
def mock_email_server():
    """Mock SMTP server for email testing."""
    mock_server = MagicMock()
    mock_server.sendmail = MagicMock(return_value={})
    mock_server.quit = MagicMock()
    return mock_server


@pytest.fixture
def mock_requests_response():
    """Mock requests.Response for webhook testing."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={'ok': True})
    mock_response.text = 'ok'
    mock_response.raise_for_status = MagicMock()
    return mock_response


@pytest.fixture
def sample_report_content():
    """Sample report content for testing."""
    return """# Pre-Market Trading Report
**Date:** October 14, 2025
**Generated:** October 13, 2025 at 06:00 PM EDT
**Portfolio Value:** $100,000

## SHORGAN-BOT Recommendations (5 positions)

### SNDX
- **Catalyst**: Oct 25 PDUFA for Revuforj
- **Risk Score**: 9/10
- **Conviction Score**: 9/10

### GKOS
- **Catalyst**: Oct 20 PDUFA for Epioxa
- **Risk Score**: 7/10
- **Conviction Score**: 7/10

## DEE-BOT Recommendations (3 positions)

### DUK
- **Strategy**: Long-term defensive utility
- **Risk Score**: 8/10
- **Conviction Score**: 8/10

### ED
- **Strategy**: Long-term defensive utility
- **Risk Score**: 9/10
- **Conviction Score**: 9/10

## Risk Disclosures
This is for educational purposes only. Not financial advice.
"""


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime.now() for consistent testing."""
    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            # Monday, October 13, 2025 at 6:00 PM ET
            return datetime(2025, 10, 13, 18, 0, 0)

        @classmethod
        def strftime(cls, format_str):
            return cls.now().strftime(format_str)

    # This would require more complex mocking of datetime module
    # For now, return a fixture that can be used manually
    return datetime(2025, 10, 13, 18, 0, 0)


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring real API calls"
    )
    config.addinivalue_line(
        "markers", "requires_env: mark test as requiring .env file"
    )
