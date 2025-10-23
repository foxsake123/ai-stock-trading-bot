"""
Comprehensive tests for report formatter module
Tests all formatting functions, signal strength indicators, and table generation
"""

import pytest
from datetime import datetime
from src.reports.report_formatter import (
    ReportFormatter,
    SignalStrength,
    Priority,
    QuickFormatters
)


class TestSignalStrengthEnum:
    """Test SignalStrength enum values"""

    def test_signal_strength_values(self):
        """Test all signal strength indicator values"""
        assert SignalStrength.VERY_STRONG_BULLISH.value == "++"
        assert SignalStrength.STRONG_BULLISH.value == "+"
        assert SignalStrength.WEAK_BULLISH.value == "~+"
        assert SignalStrength.NEUTRAL.value == "○"
        assert SignalStrength.WEAK_BEARISH.value == "~-"
        assert SignalStrength.STRONG_BEARISH.value == "-"
        assert SignalStrength.VERY_STRONG_BEARISH.value == "--"


class TestPriorityEnum:
    """Test Priority enum values"""

    def test_priority_values(self):
        """Test all priority indicator values"""
        assert Priority.CRITICAL.value == "🔴 CRITICAL"
        assert Priority.HIGH.value == "🟠 HIGH"
        assert Priority.MEDIUM.value == "🟡 MEDIUM"
        assert Priority.LOW.value == "🟢 LOW"
        assert Priority.WATCH.value == "⚪ WATCH"


class TestFormatSignalStrength:
    """Test format_signal_strength static method"""

    def test_very_strong_bullish(self):
        """Test very strong bullish signal (≥70)"""
        assert ReportFormatter.format_signal_strength(70.0) == "++"
        assert ReportFormatter.format_signal_strength(100.0) == "++"
        assert ReportFormatter.format_signal_strength(85.5) == "++"

    def test_strong_bullish(self):
        """Test strong bullish signal (40-69)"""
        assert ReportFormatter.format_signal_strength(40.0) == "+"
        assert ReportFormatter.format_signal_strength(69.9) == "+"
        assert ReportFormatter.format_signal_strength(55.0) == "+"

    def test_weak_bullish(self):
        """Test weak bullish signal (15-39)"""
        assert ReportFormatter.format_signal_strength(15.0) == "~+"
        assert ReportFormatter.format_signal_strength(39.9) == "~+"
        assert ReportFormatter.format_signal_strength(25.0) == "~+"

    def test_neutral(self):
        """Test neutral signal (-14 to 14)"""
        assert ReportFormatter.format_signal_strength(0.0) == "○"
        assert ReportFormatter.format_signal_strength(14.9) == "○"
        assert ReportFormatter.format_signal_strength(-14.9) == "○"
        assert ReportFormatter.format_signal_strength(5.0) == "○"
        assert ReportFormatter.format_signal_strength(-10.0) == "○"

    def test_weak_bearish(self):
        """Test weak bearish signal (-15 to -39)"""
        assert ReportFormatter.format_signal_strength(-15.0) == "~-"
        assert ReportFormatter.format_signal_strength(-39.9) == "~-"
        assert ReportFormatter.format_signal_strength(-25.0) == "~-"

    def test_strong_bearish(self):
        """Test strong bearish signal (-40 to -69)"""
        assert ReportFormatter.format_signal_strength(-40.0) == "-"
        assert ReportFormatter.format_signal_strength(-69.9) == "-"
        assert ReportFormatter.format_signal_strength(-55.0) == "-"

    def test_very_strong_bearish(self):
        """Test very strong bearish signal (≤-70)"""
        assert ReportFormatter.format_signal_strength(-70.0) == "--"
        assert ReportFormatter.format_signal_strength(-100.0) == "--"
        assert ReportFormatter.format_signal_strength(-85.5) == "--"


class TestFormatPriority:
    """Test format_priority static method"""

    def test_critical_priority(self):
        """Test critical priority calculation (≥80)"""
        result = ReportFormatter.format_priority(
            confidence=90.0,
            signal_count=5,
            alt_data_score=50.0
        )
        assert result == "🔴 CRITICAL"

    def test_high_priority(self):
        """Test high priority calculation (60-79)"""
        result = ReportFormatter.format_priority(
            confidence=80.0,
            signal_count=4,
            alt_data_score=30.0
        )
        assert result == "🟠 HIGH"

    def test_medium_priority(self):
        """Test medium priority calculation (40-59)"""
        result = ReportFormatter.format_priority(
            confidence=60.0,
            signal_count=2,
            alt_data_score=10.0
        )
        assert result == "🟡 MEDIUM"

    def test_low_priority(self):
        """Test low priority calculation (20-39)"""
        result = ReportFormatter.format_priority(
            confidence=40.0,
            signal_count=1,
            alt_data_score=5.0
        )
        assert result == "🟢 LOW"

    def test_watch_priority(self):
        """Test watch priority calculation (<20)"""
        result = ReportFormatter.format_priority(
            confidence=20.0,
            signal_count=0,
            alt_data_score=0.0
        )
        assert result == "⚪ WATCH"


class TestFormatCurrency:
    """Test format_currency static method"""

    def test_positive_amount(self):
        """Test positive currency formatting"""
        assert ReportFormatter.format_currency(1234.56) == "$1,234.56"
        assert ReportFormatter.format_currency(100000.00) == "$100,000.00"

    def test_negative_amount(self):
        """Test negative currency formatting"""
        assert ReportFormatter.format_currency(-1234.56) == "$-1,234.56"

    def test_zero_amount(self):
        """Test zero currency formatting"""
        assert ReportFormatter.format_currency(0.0) == "$0.00"

    def test_large_amount(self):
        """Test large amount with commas"""
        assert ReportFormatter.format_currency(1234567.89) == "$1,234,567.89"


class TestFormatPercentage:
    """Test format_percentage static method"""

    def test_positive_percentage(self):
        """Test positive percentage with + sign"""
        assert ReportFormatter.format_percentage(5.5) == "+5.5%"
        assert ReportFormatter.format_percentage(12.34) == "+12.3%"

    def test_negative_percentage(self):
        """Test negative percentage"""
        assert ReportFormatter.format_percentage(-5.5) == "-5.5%"
        assert ReportFormatter.format_percentage(-12.34) == "-12.3%"

    def test_zero_percentage(self):
        """Test zero percentage"""
        assert ReportFormatter.format_percentage(0.0) == "0.0%"


class TestFormatRiskReward:
    """Test format_risk_reward static method"""

    def test_valid_risk_reward(self):
        """Test valid risk/reward calculation"""
        # Entry $100, Target $150, Stop $90 → Risk $10, Reward $50 → 1:5.0
        result = ReportFormatter.format_risk_reward(
            entry=100.0,
            target=150.0,
            stop=90.0
        )
        assert result == "1:5.0"

    def test_short_position(self):
        """Test risk/reward for short position"""
        # Short Entry $100, Target $80, Stop $110 → Risk $10, Reward $20 → 1:2.0
        result = ReportFormatter.format_risk_reward(
            entry=100.0,
            target=80.0,
            stop=110.0
        )
        assert result == "1:2.0"

    def test_zero_risk(self):
        """Test when stop equals entry (zero risk)"""
        result = ReportFormatter.format_risk_reward(
            entry=100.0,
            target=150.0,
            stop=100.0
        )
        assert result == "N/A"

    def test_tight_risk_reward(self):
        """Test tight risk with larger reward"""
        # Entry $50, Target $60, Stop $49 → Risk $1, Reward $10 → 1:10.0
        result = ReportFormatter.format_risk_reward(
            entry=50.0,
            target=60.0,
            stop=49.0
        )
        assert result == "1:10.0"


class TestGenerateExecutiveSummaryTable:
    """Test generate_executive_summary_table method"""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance"""
        return ReportFormatter()

    @pytest.fixture
    def sample_recommendations(self):
        """Sample recommendations for testing"""
        return [
            {
                'ticker': 'AAPL',
                'strategy': 'Tech Growth',
                'action': 'BUY',
                'entry_price': 175.00,
                'target_price': 200.00,
                'stop_loss': 165.00,
                'composite_score': 65.0,
                'alt_data_score': 45.0,
                'confidence': 75.0,
                'signal_count': 4,
                'priority_score': 70.0
            },
            {
                'ticker': 'TSLA',
                'strategy': 'EV Play',
                'action': 'HOLD',
                'entry_price': 250.00,
                'target_price': 300.00,
                'stop_loss': 230.00,
                'composite_score': 25.0,
                'alt_data_score': 15.0,
                'confidence': 60.0,
                'signal_count': 2,
                'priority_score': 45.0
            }
        ]

    def test_table_generation(self, formatter, sample_recommendations):
        """Test table is generated with correct structure"""
        table = formatter.generate_executive_summary_table(sample_recommendations)

        # Check header exists
        assert "| Ticker | Strategy | Entry | Target | Stop | R/R | Signal | Alt Data | Priority | Action |" in table
        assert "|--------|----------|-------|--------|------|-----|--------|----------|----------|--------|" in table

        # Check data rows exist
        assert "AAPL" in table
        assert "TSLA" in table
        assert "Tech Growth" in table
        assert "EV Play" in table

    def test_empty_recommendations(self, formatter):
        """Test with empty recommendations list"""
        table = formatter.generate_executive_summary_table([])
        assert "*No recommendations available.*" in table

    def test_sorting_by_priority(self, formatter, sample_recommendations):
        """Test recommendations are sorted by priority score"""
        table = formatter.generate_executive_summary_table(sample_recommendations)

        # AAPL (priority 70) should appear before TSLA (priority 45)
        aapl_pos = table.find("AAPL")
        tsla_pos = table.find("TSLA")
        assert aapl_pos < tsla_pos


class TestGenerateAltDataMatrix:
    """Test generate_alt_data_matrix method"""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance"""
        return ReportFormatter()

    @pytest.fixture
    def sample_signals(self):
        """Sample ticker signals for testing"""
        return {
            'AAPL': {
                'insider': 50.0,
                'options': 30.0,
                'social': -20.0,
                'trends': 10.0,
                'composite': 25.0
            },
            'TSLA': {
                'insider': -40.0,
                'options': -50.0,
                'social': 60.0,
                'trends': 20.0,
                'composite': 5.0
            }
        }

    def test_matrix_generation(self, formatter, sample_signals):
        """Test matrix is generated with correct structure"""
        matrix = formatter.generate_alt_data_matrix(sample_signals)

        # Check header
        assert "| Ticker | Insider | Options | Social | Trends | Composite |" in matrix

        # Check tickers present
        assert "AAPL" in matrix
        assert "TSLA" in matrix

        # Check legend
        assert "**Legend**" in matrix
        assert "Very Strong" in matrix

    def test_empty_signals(self, formatter):
        """Test with empty signals dictionary"""
        matrix = formatter.generate_alt_data_matrix({})
        assert "*No alternative data signals available.*" in matrix

    def test_signal_strength_indicators(self, formatter, sample_signals):
        """Test signal strength indicators are applied"""
        matrix = formatter.generate_alt_data_matrix(sample_signals)

        # Should contain various signal indicators
        assert "+" in matrix or "~+" in matrix
        assert "-" in matrix or "~-" in matrix
        assert "○" in matrix


class TestGenerateRiskAlertsSection:
    """Test generate_risk_alerts_section method"""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance"""
        return ReportFormatter()

    def test_normal_conditions(self, formatter):
        """Test with normal market conditions"""
        macro_factors = {}
        market_conditions = {
            'vix': 15.0,
            'regime': 'BULLISH',
            'trend': 'UPTREND',
            'volatility': 'LOW'
        }

        section = formatter.generate_risk_alerts_section(macro_factors, market_conditions)

        assert "Risk Alerts" in section
        assert "Market Conditions" in section
        assert "VIX" in section
        assert "15.0" in section

    def test_elevated_vix(self, formatter):
        """Test with elevated VIX"""
        market_conditions = {
            'vix': 35.0,
            'regime': 'BEARISH',
            'trend': 'DOWNTREND',
            'volatility': 'HIGH'
        }

        section = formatter.generate_risk_alerts_section({}, market_conditions)

        assert "35.0" in section
        assert "Elevated volatility" in section or "Risk Warnings" in section


class TestGenerateExecutionChecklist:
    """Test generate_execution_checklist method"""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance"""
        return ReportFormatter()

    def test_checklist_structure(self, formatter):
        """Test checklist has all time periods"""
        trading_date = datetime(2025, 10, 22)
        checklist = formatter.generate_execution_checklist(trading_date)

        assert "Execution Checklist" in checklist
        assert "Pre-Market" in checklist
        assert "Market Open" in checklist
        assert "Mid-Day" in checklist
        assert "Power Hour" in checklist
        assert "Post-Market" in checklist

    def test_specific_times(self, formatter):
        """Test specific times are included"""
        trading_date = datetime(2025, 10, 22)
        checklist = formatter.generate_execution_checklist(trading_date)

        assert "7:00 AM" in checklist
        assert "8:30 AM" in checklist
        assert "9:30 AM" in checklist
        assert "12:00 PM" in checklist
        assert "3:00 PM" in checklist
        assert "4:00 PM" in checklist

    def test_checkboxes(self, formatter):
        """Test checklist items have checkboxes"""
        trading_date = datetime(2025, 10, 22)
        checklist = formatter.generate_execution_checklist(trading_date)

        # Should contain multiple checkbox items
        assert checklist.count("- [ ]") >= 10


class TestGenerateMethodologyAppendix:
    """Test generate_methodology_appendix method"""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance"""
        return ReportFormatter()

    def test_methodology_sections(self, formatter):
        """Test all methodology sections are included"""
        appendix = formatter.generate_methodology_appendix()

        assert "Data Source Methodology" in appendix
        assert "Signal Weighting" in appendix
        assert "Composite Score Calculation" in appendix
        assert "Priority Scoring" in appendix
        assert "Risk/Reward Calculation" in appendix
        assert "Data Sources" in appendix
        assert "Disclaimer" in appendix

    def test_signal_weights(self, formatter):
        """Test signal weights are documented"""
        appendix = formatter.generate_methodology_appendix()

        assert "25%" in appendix  # Insider and Options
        assert "20%" in appendix  # Social
        assert "15%" in appendix  # Trends


class TestQuickFormatters:
    """Test QuickFormatters utility class"""

    def test_quick_table(self):
        """Test quick table generation"""
        data = [
            ['AAPL', '175.00', 'BUY'],
            ['TSLA', '250.00', 'HOLD']
        ]
        headers = ['Ticker', 'Price', 'Action']

        table = QuickFormatters.quick_table(data, headers)

        assert "Ticker" in table
        assert "AAPL" in table
        assert "TSLA" in table
        assert "|---|" in table

    def test_quick_bullet_list(self):
        """Test quick bullet list generation"""
        items = ['First item', 'Second item', 'Third item']

        bullet_list = QuickFormatters.quick_bullet_list(items)

        assert bullet_list.count("- ") == 3
        assert "First item" in bullet_list

    def test_quick_numbered_list(self):
        """Test quick numbered list generation"""
        items = ['First', 'Second', 'Third']

        numbered_list = QuickFormatters.quick_numbered_list(items)

        assert "1. First" in numbered_list
        assert "2. Second" in numbered_list
        assert "3. Third" in numbered_list

    def test_quick_alert_box(self):
        """Test quick alert box generation"""
        message = "This is a warning"

        alert = QuickFormatters.quick_alert_box(message, "WARNING")

        assert "WARNING" in alert
        assert message in alert
        assert "⚠️" in alert


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
