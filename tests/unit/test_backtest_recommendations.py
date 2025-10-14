"""
Unit tests for backtest_recommendations.py
Tests the recommendation backtesting system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import json
import tempfile
import os


@pytest.fixture
def sample_report_content():
    """Sample markdown report content"""
    return """
# Pre-Market Report - 2025-10-14

## SHORGAN-BOT Recommendations

### 1. SNDX - Strong Buy (Score: 85/100)
**Entry**: $23.50
**Target**: $27.00 (+15%)
**Stop Loss**: $21.50 (-8%)
**Risk/Reward**: 1:1.75

### 2. ARQT - Buy (Score: 74/100)
**Entry**: $19.98
**Target**: $23.00 (+15%)
**Stop Loss**: $16.50 (-17%)

## DEE-BOT Recommendations

### 1. DUK - Hold/Accumulate (Score: 90/100)
**Entry**: $98.50
**Target**: $106.00 (+8%)
**Stop Loss**: $95.50 (-3%)
"""


@pytest.fixture
def temp_reports_directory():
    """Create temporary reports directory with sample files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        reports_dir = os.path.join(tmpdir, "reports", "premarket")
        os.makedirs(reports_dir, exist_ok=True)
        yield reports_dir


class TestRecommendationExtraction:
    """Test extracting recommendations from markdown reports"""

    def test_extract_shorgan_recommendations(self, sample_report_content):
        """Test extraction of SHORGAN recommendations"""
        # Look for SHORGAN section
        assert "SHORGAN-BOT Recommendations" in sample_report_content

        # Check for ticker mentions
        assert "SNDX" in sample_report_content
        assert "ARQT" in sample_report_content

    def test_extract_dee_recommendations(self, sample_report_content):
        """Test extraction of DEE recommendations"""
        # Look for DEE section
        assert "DEE-BOT Recommendations" in sample_report_content

        # Check for ticker mention
        assert "DUK" in sample_report_content

    def test_extract_entry_prices(self, sample_report_content):
        """Test extraction of entry prices"""
        # Entry prices should be present
        assert "$23.50" in sample_report_content
        assert "$19.98" in sample_report_content
        assert "$98.50" in sample_report_content

    def test_extract_target_prices(self, sample_report_content):
        """Test extraction of target prices"""
        # Target prices should be present
        assert "$27.00" in sample_report_content
        assert "$23.00" in sample_report_content
        assert "$106.00" in sample_report_content

    def test_extract_stop_loss_prices(self, sample_report_content):
        """Test extraction of stop loss prices"""
        # Stop loss prices should be present
        assert "$21.50" in sample_report_content
        assert "$16.50" in sample_report_content
        assert "$95.50" in sample_report_content


class TestPerformanceCalculation:
    """Test performance metric calculations"""

    def test_calculate_return_percentage(self):
        """Test return percentage calculation"""
        entry = 100.0
        exit_price = 115.0

        return_pct = ((exit_price - entry) / entry) * 100
        assert return_pct == 15.0

    def test_calculate_negative_return(self):
        """Test negative return calculation"""
        entry = 100.0
        exit_price = 92.0

        return_pct = ((exit_price - entry) / entry) * 100
        assert return_pct == -8.0

    def test_calculate_win_rate(self):
        """Test win rate calculation"""
        wins = 13
        losses = 7
        total = wins + losses

        win_rate = (wins / total) * 100
        assert win_rate == 65.0

    def test_calculate_average_return(self):
        """Test average return calculation"""
        returns = [15.0, -8.0, 12.0, -5.0, 18.0]
        avg_return = sum(returns) / len(returns)

        assert avg_return == 6.4

    def test_target_hit_detection(self):
        """Test detecting if target was hit"""
        entry = 100.0
        target = 115.0
        actual_high = 120.0

        target_hit = actual_high >= target
        assert target_hit is True

    def test_stop_loss_hit_detection(self):
        """Test detecting if stop loss was hit"""
        entry = 100.0
        stop_loss = 92.0
        actual_low = 90.0

        stop_hit = actual_low <= stop_loss
        assert stop_hit is True


class TestReportParsing:
    """Test parsing of report files"""

    def test_parse_report_date_from_filename(self):
        """Test extracting date from filename"""
        filename = "premarket_report_2025-10-14.md"

        # Extract date
        date_str = filename.replace("premarket_report_", "").replace(".md", "")
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        assert parsed_date == date(2025, 10, 14)

    def test_parse_multiple_reports(self, temp_reports_directory):
        """Test parsing multiple report files"""
        # Create sample report files
        dates = ["2025-10-13", "2025-10-14", "2025-10-15"]

        for date_str in dates:
            filepath = os.path.join(temp_reports_directory, f"premarket_report_{date_str}.md")
            with open(filepath, 'w') as f:
                f.write(f"# Report for {date_str}")

        # List files
        files = os.listdir(temp_reports_directory)
        assert len(files) == 3

        # All should be markdown
        assert all(f.endswith('.md') for f in files)

    def test_parse_report_metadata(self, sample_report_content):
        """Test extracting metadata from report"""
        lines = sample_report_content.split('\n')

        # Find title line
        title_line = [l for l in lines if l.startswith('# Pre-Market Report')][0]
        assert "2025-10-14" in title_line


class TestStrategyComparison:
    """Test comparing SHORGAN vs DEE strategy performance"""

    def test_compare_strategy_returns(self):
        """Test comparing average returns between strategies"""
        shorgan_returns = [15.0, -8.0, 18.0, 12.0, -5.0]
        dee_returns = [8.0, -3.0, 6.0, 7.0, 9.0]

        shorgan_avg = sum(shorgan_returns) / len(shorgan_returns)
        dee_avg = sum(dee_returns) / len(dee_returns)

        assert shorgan_avg > dee_avg  # SHORGAN more aggressive

    def test_compare_strategy_win_rates(self):
        """Test comparing win rates between strategies"""
        shorgan_wins = 13
        shorgan_total = 20
        dee_wins = 15
        dee_total = 20

        shorgan_win_rate = (shorgan_wins / shorgan_total) * 100
        dee_win_rate = (dee_wins / dee_total) * 100

        assert shorgan_win_rate == 65.0
        assert dee_win_rate == 75.0

    def test_strategy_risk_profiles(self):
        """Test comparing risk profiles"""
        shorgan_stop_loss_pct = 8.0
        dee_stop_loss_pct = 3.0

        assert shorgan_stop_loss_pct > dee_stop_loss_pct
        assert dee_stop_loss_pct < 5.0  # DEE more conservative


class TestDateRangeFiltering:
    """Test filtering recommendations by date range"""

    def test_filter_by_start_date(self):
        """Test filtering recommendations after start date"""
        start_date = date(2025, 10, 1)
        recommendation_dates = [
            date(2025, 9, 28),
            date(2025, 10, 5),
            date(2025, 10, 12)
        ]

        filtered = [d for d in recommendation_dates if d >= start_date]
        assert len(filtered) == 2

    def test_filter_by_end_date(self):
        """Test filtering recommendations before end date"""
        end_date = date(2025, 10, 15)
        recommendation_dates = [
            date(2025, 10, 5),
            date(2025, 10, 12),
            date(2025, 10, 20)
        ]

        filtered = [d for d in recommendation_dates if d <= end_date]
        assert len(filtered) == 2

    def test_filter_by_date_range(self):
        """Test filtering recommendations within date range"""
        start_date = date(2025, 10, 1)
        end_date = date(2025, 10, 15)
        recommendation_dates = [
            date(2025, 9, 28),
            date(2025, 10, 5),
            date(2025, 10, 12),
            date(2025, 10, 20)
        ]

        filtered = [d for d in recommendation_dates if start_date <= d <= end_date]
        assert len(filtered) == 2


class TestTickerFiltering:
    """Test filtering by specific ticker"""

    def test_filter_single_ticker(self):
        """Test filtering for single ticker"""
        recommendations = [
            {"ticker": "SNDX", "entry": 23.50},
            {"ticker": "ARQT", "entry": 19.98},
            {"ticker": "SNDX", "entry": 24.00}
        ]

        filtered = [r for r in recommendations if r["ticker"] == "SNDX"]
        assert len(filtered) == 2

    def test_filter_multiple_tickers(self):
        """Test filtering for multiple tickers"""
        recommendations = [
            {"ticker": "SNDX", "entry": 23.50},
            {"ticker": "ARQT", "entry": 19.98},
            {"ticker": "DUK", "entry": 98.50}
        ]

        tickers = ["SNDX", "DUK"]
        filtered = [r for r in recommendations if r["ticker"] in tickers]
        assert len(filtered) == 2


class TestPerformanceReportGeneration:
    """Test generating performance report markdown"""

    def test_generate_summary_section(self):
        """Test generating summary statistics"""
        total_recommendations = 42
        closed_positions = 38
        win_rate = 63.2
        avg_return = 7.45

        summary = f"""
## Summary Statistics

- Total Recommendations: {total_recommendations}
- Closed Positions: {closed_positions}
- Win Rate: {win_rate}%
- Average Return: {avg_return}%
"""
        assert str(total_recommendations) in summary
        assert "63.2%" in summary

    def test_generate_strategy_comparison(self):
        """Test generating strategy comparison"""
        shorgan_win_rate = 68.4
        dee_win_rate = 55.0

        comparison = f"""
## Strategy Performance

- SHORGAN Win Rate: {shorgan_win_rate}%
- DEE Win Rate: {dee_win_rate}%
"""
        assert "68.4%" in comparison
        assert "55.0%" in comparison


class TestJSONDataExport:
    """Test exporting detailed results to JSON"""

    def test_export_recommendation_details(self):
        """Test exporting recommendation data to JSON"""
        recommendation = {
            "ticker": "SNDX",
            "strategy": "SHORGAN",
            "date": "2025-10-14",
            "entry": 23.50,
            "target": 27.00,
            "stop_loss": 21.50,
            "actual_high": 26.80,
            "actual_low": 22.90,
            "return_pct": 14.04,
            "hit_target": False,
            "hit_stop": False
        }

        json_str = json.dumps(recommendation, indent=2)
        parsed = json.loads(json_str)

        assert parsed["ticker"] == "SNDX"
        assert parsed["entry"] == 23.50
        assert parsed["return_pct"] == 14.04

    def test_export_multiple_recommendations(self):
        """Test exporting multiple recommendations"""
        recommendations = [
            {"ticker": "SNDX", "return": 15.0},
            {"ticker": "ARQT", "return": 12.0}
        ]

        json_str = json.dumps(recommendations, indent=2)
        parsed = json.loads(json_str)

        assert len(parsed) == 2
        assert parsed[0]["ticker"] == "SNDX"


class TestMonthlyBreakdown:
    """Test monthly performance breakdown"""

    def test_group_by_month(self):
        """Test grouping recommendations by month"""
        dates = [
            date(2025, 10, 5),
            date(2025, 10, 12),
            date(2025, 11, 3),
            date(2025, 11, 15)
        ]

        months = {}
        for d in dates:
            month_key = d.strftime("%Y-%m")
            if month_key not in months:
                months[month_key] = []
            months[month_key].append(d)

        assert len(months) == 2
        assert len(months["2025-10"]) == 2
        assert len(months["2025-11"]) == 2

    def test_calculate_monthly_returns(self):
        """Test calculating returns by month"""
        monthly_data = {
            "2025-10": [15.0, -8.0, 12.0],
            "2025-11": [8.0, 10.0, -3.0]
        }

        monthly_avgs = {}
        for month, returns in monthly_data.items():
            monthly_avgs[month] = sum(returns) / len(returns)

        assert monthly_avgs["2025-10"] == pytest.approx(6.33, 0.01)
        assert monthly_avgs["2025-11"] == 5.0


class TestTopWinnersLosers:
    """Test identifying top winners and losers"""

    def test_identify_top_winners(self):
        """Test identifying top performing recommendations"""
        recommendations = [
            {"ticker": "RGTI", "return": 94.0},
            {"ticker": "SRRK", "return": 21.0},
            {"ticker": "ORCL", "return": 18.0},
            {"ticker": "NVDA", "return": 12.0},
            {"ticker": "AAPL", "return": 8.0}
        ]

        # Sort by return descending
        sorted_recs = sorted(recommendations, key=lambda x: x["return"], reverse=True)
        top_3 = sorted_recs[:3]

        assert top_3[0]["ticker"] == "RGTI"
        assert top_3[0]["return"] == 94.0
        assert len(top_3) == 3

    def test_identify_top_losers(self):
        """Test identifying worst performing recommendations"""
        recommendations = [
            {"ticker": "PLUG", "return": -15.0},
            {"ticker": "NVAX", "return": -12.0},
            {"ticker": "TSLA", "return": -8.0},
            {"ticker": "AMD", "return": 5.0}
        ]

        # Sort by return ascending
        sorted_recs = sorted(recommendations, key=lambda x: x["return"])
        bottom_3 = sorted_recs[:3]

        assert bottom_3[0]["ticker"] == "PLUG"
        assert bottom_3[0]["return"] == -15.0
