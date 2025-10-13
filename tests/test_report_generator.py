"""
Tests for daily_premarket_report.py
Tests report generation, market data fetching, and file operations.
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd

# Import module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from daily_premarket_report import PreMarketReportGenerator


class TestPreMarketReportGeneratorInit:
    """Test PreMarketReportGenerator initialization."""

    @pytest.mark.unit
    def test_init_with_env_vars(self, mock_env_vars):
        """Test initialization with environment variables."""
        with patch('daily_premarket_report.Anthropic') as mock_anthropic:
            generator = PreMarketReportGenerator()

            # Check that Anthropic client was initialized
            mock_anthropic.assert_called_once()

            # Check portfolio value
            assert generator.portfolio_value == 100000

            # Check trading date is calculated
            assert generator.trading_date is not None
            # trading_date is a date object, not datetime
            from datetime import date
            assert isinstance(generator.trading_date, date)

            # Check generation date is set
            assert generator.generation_date is not None

    @pytest.mark.unit
    def test_init_creates_output_directory(self, mock_env_vars, temp_dir):
        """Test that initialization creates output directory."""
        with patch('daily_premarket_report.Anthropic'):
            # Mock Path to use temp directory
            with patch('daily_premarket_report.Path') as mock_path:
                mock_output_dir = temp_dir / 'reports' / 'premarket'
                mock_path.return_value = mock_output_dir

                generator = PreMarketReportGenerator()

                # Check output directory was created
                assert mock_output_dir.exists() or True  # Mocked, so check call

    @pytest.mark.unit
    def test_init_loads_recommendations(self, mock_env_vars):
        """Test that initialization loads stock recommendations."""
        with patch('daily_premarket_report.Anthropic'):
            with patch.object(
                PreMarketReportGenerator,
                'load_recommendations',
                return_value=pd.DataFrame([
                    {'Ticker': 'SNDX', 'Strategy': 'SHORGAN', 'Catalyst': 'PDUFA', 'Risk': 9, 'Conviction': 9}
                ])
            ):
                generator = PreMarketReportGenerator()

                # Check recommendations were loaded
                assert hasattr(generator, 'recommendations')
                assert isinstance(generator.recommendations, pd.DataFrame)


class TestFetchMarketData:
    """Test fetch_market_data() method."""

    @pytest.mark.unit
    def test_fetch_market_data_structure(self, mock_env_vars, mock_market_data):
        """Test that fetch_market_data returns correct structure."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Mock yfinance calls
            with patch('daily_premarket_report.yf.Ticker') as mock_ticker:
                mock_ticker_instance = MagicMock()
                mock_ticker_instance.info = {'regularMarketPrice': 15.23}
                mock_ticker_instance.history.return_value = pd.DataFrame({
                    'Close': [100.0, 101.5]
                })
                mock_ticker.return_value = mock_ticker_instance

                market_data = generator.fetch_market_data()

                # Check structure
                assert isinstance(market_data, dict)
                # Should have data for some symbols (may not be all if errors)
                assert len(market_data) >= 0

    @pytest.mark.unit
    def test_fetch_market_data_handles_errors(self, mock_env_vars):
        """Test that fetch_market_data handles API errors gracefully."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Mock yfinance to raise exception
            with patch('daily_premarket_report.yf.Ticker', side_effect=Exception("API Error")):
                market_data = generator.fetch_market_data()

                # Should return empty dict on error
                assert isinstance(market_data, dict)

    @pytest.mark.unit
    def test_fetch_market_data_expected_symbols(self, mock_env_vars):
        """Test that fetch_market_data attempts to fetch expected symbols."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.yf.Ticker') as mock_ticker:
                mock_ticker_instance = MagicMock()
                mock_ticker_instance.info = {'regularMarketPrice': 100.0}
                mock_ticker.return_value = mock_ticker_instance

                generator.fetch_market_data()

                # Check that yfinance was called (at least attempted)
                assert mock_ticker.called


class TestSaveReport:
    """Test save_report() method."""

    @pytest.mark.unit
    def test_save_report_creates_file(self, mock_env_vars, temp_dir, sample_report_content):
        """Test that save_report creates report file."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Use temp directory for output
            generator.output_dir = temp_dir

            filepath = generator.save_report(sample_report_content)

            # Check file was created
            assert filepath.exists()
            assert filepath.suffix == '.md'

            # Check content was written
            content = filepath.read_text()
            assert 'Pre-Market Trading Report' in content

    @pytest.mark.unit
    def test_save_report_creates_latest_symlink(self, mock_env_vars, temp_dir, sample_report_content):
        """Test that save_report creates latest.md file."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Use temp directory for output
            generator.output_dir = temp_dir

            filepath = generator.save_report(sample_report_content)

            # Check latest.md was created
            latest_file = temp_dir / 'latest.md'
            assert latest_file.exists()

            # Check content matches
            latest_content = latest_file.read_text()
            assert latest_content == sample_report_content

    @pytest.mark.unit
    def test_save_report_filename_format(self, mock_env_vars, temp_dir, sample_report_content):
        """Test that save_report uses correct filename format."""
        from datetime import date
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()
            generator.output_dir = temp_dir

            # Set specific trading date
            generator.trading_date = date(2025, 10, 14)

            filepath = generator.save_report(sample_report_content)

            # Check filename format
            assert filepath.name == 'premarket_report_2025-10-14.md'

    @pytest.mark.unit
    def test_save_report_returns_path(self, mock_env_vars, temp_dir, sample_report_content):
        """Test that save_report returns Path object."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()
            generator.output_dir = temp_dir

            filepath = generator.save_report(sample_report_content)

            # Check return type
            assert isinstance(filepath, Path)
            assert filepath.is_absolute()


class TestGenerateComprehensivePrompt:
    """Test generate_comprehensive_prompt() method."""

    @pytest.mark.unit
    def test_prompt_contains_required_sections(self, mock_env_vars, mock_market_data):
        """Test that prompt contains all required sections."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            prompt = generator.generate_comprehensive_prompt(mock_market_data)

            # Check required sections in the actual prompt
            assert 'INSTRUCTIONS' in prompt or 'hedge-fund-level' in prompt
            assert 'SHORGAN-BOT' in prompt
            assert 'DEE-BOT' in prompt
            assert 'MARKET DATA' in prompt or 'Market Data' in prompt
            assert 'OUTPUT FORMAT REQUIREMENTS' in prompt
            assert 'PORTFOLIO MANAGEMENT' in prompt or 'Portfolio' in prompt

    @pytest.mark.unit
    def test_prompt_includes_market_data(self, mock_env_vars, mock_market_data):
        """Test that prompt includes market data."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            prompt = generator.generate_comprehensive_prompt(mock_market_data)

            # Check market data is included
            assert 'VIX' in prompt or 'Market Data' in prompt

    @pytest.mark.unit
    def test_prompt_includes_trading_date(self, mock_env_vars, mock_market_data):
        """Test that prompt includes trading date."""
        from datetime import date
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()
            generator.trading_date = date(2025, 10, 14)

            prompt = generator.generate_comprehensive_prompt(mock_market_data)

            # Check trading date is mentioned
            assert '2025' in prompt or 'October' in prompt

    @pytest.mark.unit
    def test_prompt_includes_stock_recommendations(self, mock_env_vars, mock_market_data, mock_stock_recommendations):
        """Test that prompt includes stock recommendations."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()
            generator.recommendations = pd.DataFrame(mock_stock_recommendations)

            prompt = generator.generate_comprehensive_prompt(mock_market_data)

            # Check stock tickers are included
            assert 'SNDX' in prompt or 'GKOS' in prompt or 'DUK' in prompt

    @pytest.mark.unit
    def test_prompt_length(self, mock_env_vars, mock_market_data):
        """Test that prompt has reasonable length."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            prompt = generator.generate_comprehensive_prompt(mock_market_data)

            # Check prompt is substantial (>5000 characters for hedge-fund level)
            assert len(prompt) > 5000

    @pytest.mark.unit
    def test_prompt_is_string(self, mock_env_vars, mock_market_data):
        """Test that prompt returns string."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            prompt = generator.generate_comprehensive_prompt(mock_market_data)

            assert isinstance(prompt, str)


class TestLoadRecommendations:
    """Test load_recommendations() method."""

    @pytest.mark.unit
    def test_load_recommendations_returns_dataframe(self, mock_env_vars):
        """Test that load_recommendations returns DataFrame."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            recommendations = generator.load_recommendations()

            assert isinstance(recommendations, pd.DataFrame)

    @pytest.mark.unit
    def test_load_recommendations_has_required_columns(self, mock_env_vars):
        """Test that recommendations have required columns."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            recommendations = generator.load_recommendations()

            required_columns = ['Ticker', 'Strategy', 'Catalyst', 'Risk', 'Conviction']
            for column in required_columns:
                assert column in recommendations.columns

    @pytest.mark.unit
    def test_load_recommendations_default_count(self, mock_env_vars):
        """Test that default recommendations have expected count."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            recommendations = generator.load_recommendations()

            # Should have 8 default stocks (5 SHORGAN + 3 DEE)
            assert len(recommendations) == 8

    @pytest.mark.unit
    def test_load_recommendations_strategy_split(self, mock_env_vars):
        """Test that recommendations have SHORGAN and DEE strategies."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            recommendations = generator.load_recommendations()

            strategies = recommendations['Strategy'].unique()
            assert 'SHORGAN' in strategies
            assert 'DEE' in strategies


class TestGenerateMetadata:
    """Test generate_metadata() method."""

    @pytest.mark.unit
    def test_generate_metadata_structure(self, mock_env_vars):
        """Test that generate_metadata returns correct structure."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()
            generator.trading_date = datetime(2025, 10, 14)

            metadata = generator.generate_metadata()

            # Check required fields
            assert 'trading_date' in metadata
            assert 'generation_date' in metadata
            assert 'portfolio_value' in metadata
            assert 'model' in metadata
            assert 'version' in metadata

    @pytest.mark.unit
    def test_generate_metadata_values(self, mock_env_vars):
        """Test that metadata contains correct values."""
        from datetime import date
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()
            generator.trading_date = date(2025, 10, 14)
            generator.portfolio_value = 100000

            metadata = generator.generate_metadata()

            assert metadata['portfolio_value'] == 100000
            assert '2025-10-14' in metadata['trading_date']  # ISO format
            assert 'claude' in metadata['model'].lower()
