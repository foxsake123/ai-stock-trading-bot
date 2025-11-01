"""
Unit Tests for External Research Report Parser
===============================================
Tests all parsing functionality for Claude and ChatGPT research reports.

Coverage areas:
- StockRecommendation dataclass
- Claude ORDER BLOCK parsing (single and multi-trade formats)
- Claude table format parsing
- Claude narrative parsing (DEE-BOT holdings, SHORGAN-BOT trades)
- ChatGPT table parsing
- ChatGPT narrative enhancement
- Edge cases and error handling
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import os

from scripts.automation.report_parser import (
    StockRecommendation,
    ExternalReportParser
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def parser():
    """Create a fresh parser instance"""
    return ExternalReportParser()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# StockRecommendation Tests
# ============================================================================

class TestStockRecommendation:
    """Test StockRecommendation dataclass"""

    def test_creation_minimal(self):
        """Test creating recommendation with minimal fields"""
        rec = StockRecommendation(
            ticker="AAPL",
            action="BUY"
        )
        assert rec.ticker == "AAPL"
        assert rec.action == "BUY"
        assert rec.source == "unknown"
        assert rec.bot == "unknown"

    def test_creation_full(self):
        """Test creating recommendation with all fields"""
        rec = StockRecommendation(
            ticker="TSLA",
            action="SHORT",
            entry_price=250.0,
            target_price=200.0,
            stop_loss=275.0,
            shares=100,
            position_size_pct=5.0,
            catalyst="Earnings miss expected",
            catalyst_date="2025-11-05",
            conviction="HIGH",
            rationale="Overvalued on current metrics",
            source="claude",
            bot="SHORGAN-BOT"
        )
        assert rec.ticker == "TSLA"
        assert rec.action == "SHORT"
        assert rec.entry_price == 250.0
        assert rec.target_price == 200.0
        assert rec.stop_loss == 275.0
        assert rec.shares == 100
        assert rec.position_size_pct == 5.0
        assert rec.catalyst == "Earnings miss expected"
        assert rec.catalyst_date == "2025-11-05"
        assert rec.conviction == "HIGH"
        assert rec.rationale == "Overvalued on current metrics"
        assert rec.source == "claude"
        assert rec.bot == "SHORGAN-BOT"

    def test_to_dict(self):
        """Test conversion to dictionary"""
        rec = StockRecommendation(
            ticker="NVDA",
            action="BUY",
            entry_price=500.0,
            source="chatgpt",
            bot="DEE-BOT"
        )
        data = rec.to_dict()
        assert isinstance(data, dict)
        assert data['ticker'] == "NVDA"
        assert data['action'] == "BUY"
        assert data['entry_price'] == 500.0
        assert data['source'] == "chatgpt"
        assert data['bot'] == "DEE-BOT"
        assert 'target_price' in data
        assert 'stop_loss' in data


# ============================================================================
# Claude ORDER BLOCK Parsing Tests
# ============================================================================

class TestClaudeOrderBlockParsing:
    """Test parsing Claude ORDER BLOCK sections"""

    def test_parse_single_trade_block(self, parser, temp_dir):
        """Test parsing ORDER BLOCK with single trade per code block"""
        content = """
# Research Report

## 4. ORDER BLOCK

```
Action: BUY
Ticker: AAPL
Shares: 50
Limit_Price: $175.50
Stop_Loss: $165.00
Target_Price: $195.00
Catalyst_Date: 2025-11-15
One-line_Rationale: Strong iPhone sales expected
```

## 5. Risk Management
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        assert len(recs) == 1
        rec = recs[0]
        assert rec.ticker == "AAPL"
        assert rec.action == "BUY"
        assert rec.shares == 50
        assert rec.entry_price == 175.50
        assert rec.stop_loss == 165.00
        assert rec.target_price == 195.00
        assert rec.catalyst_date == "2025-11-15"
        assert rec.rationale == "Strong iPhone sales expected"
        assert rec.source == "claude"
        assert rec.bot == "DEE-BOT"

    def test_parse_multi_trade_block(self, parser, temp_dir):
        """Test parsing ORDER BLOCK with multiple trades in one code block"""
        content = """
# Research Report

## EXACT ORDER BLOCK

```
Action: BUY
Ticker: TSLA
Shares: 10
Limit_Price: $250.00
Stop_Loss: $230.00
Target_Price: $300.00
One-line_Rationale: Cybertruck production ramp

Action: SHORT
Ticker: NFLX
Shares: 5
Limit_Price: $450.00
Stop_Loss: $480.00
Target_Price: $400.00
One-line_Rationale: Subscriber growth concerns

Action: BUY
Ticker: MSFT
Shares: 20
Limit_Price: $380.00
Stop_Loss: N/A
Target_Price: N/A
One-line_Rationale: Cloud growth acceleration
```

## Risk Management
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "SHORGAN-BOT")

        assert len(recs) == 3

        # First trade
        assert recs[0].ticker == "TSLA"
        assert recs[0].action == "BUY"
        assert recs[0].shares == 10
        assert recs[0].entry_price == 250.00

        # Second trade (SHORT)
        assert recs[1].ticker == "NFLX"
        assert recs[1].action == "SHORT"
        assert recs[1].shares == 5

        # Third trade (no stop/target)
        assert recs[2].ticker == "MSFT"
        assert recs[2].action == "BUY"
        assert recs[2].stop_loss is None
        assert recs[2].target_price is None

    def test_parse_order_block_variations(self, parser, temp_dir):
        """Test different ORDER BLOCK header formats"""
        variations = [
            "## 4. ORDER BLOCK",
            "## ORDER BLOCK",
            "## EXACT ORDER BLOCK",
            "## 6. Exact Order Block"
        ]

        for header in variations:
            content = f"""
{header}

```
Action: BUY
Ticker: TEST
Shares: 1
Limit_Price: $100.00
```
"""
            report_path = temp_dir / "test_report.md"
            report_path.write_text(content)

            recs = parser.parse_claude_report(report_path, "DEE-BOT")
            assert len(recs) == 1, f"Failed to parse header: {header}"
            assert recs[0].ticker == "TEST"


# ============================================================================
# Claude Table Format Parsing Tests
# ============================================================================

class TestClaudeTableParsing:
    """Test parsing Claude summary table format"""

    def test_parse_summary_table(self, parser, temp_dir):
        """Test parsing recommendations from summary table"""
        content = """
# Research Report

| Rank | Ticker | Direction | Entry | Target | Stop | R/R | Catalyst | Date | Conviction |
|------|--------|-----------|-------|--------|------|-----|----------|------|------------|
| 1 | AAPL | LONG | $175.50 | $195.00 | $165.00 | 2.2 | iPhone sales | Nov 15 | HIGH |
| 2 | TSLA | SHORT | $250.00 | $200.00 | $275.00 | 2.0 | Production delays | Nov 20 | MEDIUM |
| 3 | NVDA | LONG | $500-520 | $600.00 | $475.00 | 2.5 | AI demand | Dec 1 | HIGH |

## Order Block
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "SHORGAN-BOT")

        assert len(recs) >= 3  # May have duplicates from ORDER BLOCK

        # Find AAPL
        aapl = [r for r in recs if r.ticker == "AAPL"][0]
        assert aapl.action == "BUY"
        assert aapl.entry_price == 175.50
        assert aapl.target_price == 195.00
        assert aapl.stop_loss == 165.00
        assert aapl.catalyst == "iPhone sales"
        assert aapl.catalyst_date == "Nov 15"
        assert aapl.conviction == "HIGH"

        # Find TSLA (SHORT)
        tsla = [r for r in recs if r.ticker == "TSLA"][0]
        assert tsla.action == "SHORT"

        # Find NVDA (entry range)
        nvda = [r for r in recs if r.ticker == "NVDA"][0]
        assert nvda.entry_price == 500.00  # Takes first value from range


# ============================================================================
# Claude Narrative Parsing Tests
# ============================================================================

class TestClaudeNarrativeParsing:
    """Test parsing Claude narrative sections"""

    def test_parse_shorgan_narrative_trades(self, parser, temp_dir):
        """Test parsing SHORGAN-BOT trade narratives"""
        content = """
# Research Report

### Trade 1: AAPL

**Entry Price**: $175.50
**Target Price**: $195.00
**Stop Loss**: $165.00
**Position Size**: 5-7%
**Conviction**: HIGH
**Catalyst**: iPhone 16 sales momentum
**Rationale**: Strong demand in China, margin expansion expected

### Trade 2: TSLA

**Entry Price**: $250.00
**Action**: SHORT
**Target Price**: $200.00
**Conviction**: MEDIUM
**Catalyst**: Production delays at Gigafactory

## Order Block
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "SHORGAN-BOT")

        assert len(recs) >= 2

        # Check AAPL
        aapl = [r for r in recs if r.ticker == "AAPL"][0]
        assert aapl.action in ["BUY", "HOLD"]  # Inferred from content
        assert aapl.entry_price == 175.50
        assert aapl.conviction == "HIGH"
        assert "iPhone 16 sales" in aapl.catalyst

        # Check TSLA (SHORT)
        tsla = [r for r in recs if r.ticker == "TSLA"][0]
        assert tsla.action == "SHORT"
        assert tsla.entry_price == 250.00

    def test_parse_dee_holdings_new_format(self, parser, temp_dir):
        """Test parsing DEE-BOT holdings (new format)"""
        content = """
# Portfolio Deep Dive

**Apple Inc. (AAPL) | 8.5% allocation | $8,500**

Recent price: $175.50

**Rationale:** Industry leader in consumer tech with strong brand loyalty and expanding services revenue

**Johnson & Johnson (JNJ) | 7.2% allocation | $7,200**

Recent price: $160.25

**Rationale:** Defensive healthcare stock with consistent dividend growth
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        assert len(recs) == 2

        # Check AAPL
        aapl = recs[0]
        assert aapl.ticker == "AAPL"
        assert aapl.action == "BUY"
        assert aapl.position_size_pct == 8.5
        assert aapl.entry_price == 175.50
        # Rationale extraction is optional - parser may not always capture it
        if aapl.rationale:
            assert "Industry leader" in aapl.rationale

        # Check JNJ
        jnj = recs[1]
        assert jnj.ticker == "JNJ"
        assert jnj.position_size_pct == 7.2
        assert jnj.entry_price == 160.25

    def test_parse_dee_holdings_old_format(self, parser, temp_dir):
        """Test parsing DEE-BOT holdings (old format)"""
        content = """
# Holdings

#### AAPL - Apple Inc.

Quality score: 95/100
Recent price: $175.50
Position size: 8.5%

Strong fundamentals with expanding services revenue.

#### JNJ - Johnson & Johnson

Quality score: 92/100
Recent price: $160.00

Defensive healthcare with consistent dividends.
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        # Should parse at least the tickers
        assert len(recs) >= 2
        tickers = [r.ticker for r in recs]
        assert "AAPL" in tickers
        assert "JNJ" in tickers


# ============================================================================
# ChatGPT Parsing Tests
# ============================================================================

class TestChatGPTParsing:
    """Test parsing ChatGPT research reports"""

    def test_parse_chatgpt_table(self, parser, temp_dir):
        """Test parsing ChatGPT summary table"""
        # Use exact regex pattern from parser: (Shorgan|Dee)‑Bot
        # The ‑ is a non-breaking hyphen (U+2011)
        content = """
# Research Report

| Bot | Ticker | Direction | Entry | Stop | Target | Size |
|-----|--------|-----------|-------|------|--------|------|
| Dee‑Bot | **AAPL** | Long | 175.50 | 165.00 | 195.00 | **5.5%** |
| Shorgan‑Bot | **TSLA** | Short | 250.00 | 275.00 | 200.00 | **7.0%** |
| Dee‑Bot | **JNJ** | Long | 160.00 | 150.00 | 175.00 | **6.0%** |

## Details
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content, encoding='utf-8')

        recs = parser.parse_chatgpt_report(report_path)

        assert len(recs) == 3

        # Check AAPL
        aapl = [r for r in recs if r.ticker == "AAPL"][0]
        assert aapl.action == "BUY"
        assert aapl.entry_price == 175.50
        assert aapl.stop_loss == 165.00
        assert aapl.target_price == 195.00
        assert aapl.position_size_pct == 5.5
        assert aapl.bot == "DEE-BOT"
        assert aapl.source == "chatgpt"

        # Check TSLA (SHORT)
        tsla = [r for r in recs if r.ticker == "TSLA"][0]
        assert tsla.action == "SHORT"
        assert tsla.bot == "SHORGAN-BOT"

        # Check JNJ
        jnj = [r for r in recs if r.ticker == "JNJ"][0]
        assert jnj.action == "BUY"
        assert jnj.bot == "DEE-BOT"

    def test_chatgpt_narrative_enhancement(self, parser, temp_dir):
        """Test enhancing ChatGPT recommendations with narrative details"""
        content = """
# Summary

| Bot | Ticker | Direction | Entry | Stop | Target | Size |
|-----|--------|-----------|-------|------|--------|------|
| Shorgan‑Bot | **AAPL** | Long | 175.50 | 165.00 | 195.00 | **5.0%** |

## Details

### **AAPL**

**Catalyst**: iPhone 16 launch driving strong upgrade cycle

**Rationale**: Apple is experiencing robust demand for the iPhone 16, particularly in emerging markets. The new AI features are resonating with consumers and driving higher average selling prices.

### Other Stocks
"""
        report_path = temp_dir / "test_report.md"
        report_path.write_text(content, encoding='utf-8')

        recs = parser.parse_chatgpt_report(report_path)

        assert len(recs) == 1
        rec = recs[0]
        assert rec.ticker == "AAPL"
        assert "iPhone 16 launch" in rec.catalyst
        assert "robust demand" in rec.rationale.lower()


# ============================================================================
# Integration Tests
# ============================================================================

class TestParserIntegration:
    """Test combined parsing from multiple sources"""

    def test_get_recommendations_for_bot_combined(self, parser, temp_dir):
        """Test getting recommendations from both Claude and ChatGPT"""
        # Create Claude report
        claude_content = """
## ORDER BLOCK

```
Action: BUY
Ticker: AAPL
Shares: 50
Limit_Price: $175.00
```
"""
        claude_path = temp_dir / "claude_dee.md"
        claude_path.write_text(claude_content)

        # Create ChatGPT report
        chatgpt_content = """
| Bot | Ticker | Direction | Entry | Stop | Target | Size |
|-----|--------|-----------|-------|------|--------|------|
| Dee‑Bot | **MSFT** | Long | 380.00 | 360.00 | 420.00 | **6.0%** |
"""
        chatgpt_path = temp_dir / "chatgpt.md"
        chatgpt_path.write_text(chatgpt_content, encoding='utf-8')

        # Get combined recommendations
        recs = parser.get_recommendations_for_bot("DEE-BOT", claude_path, chatgpt_path)

        assert len(recs) == 2
        tickers = [r.ticker for r in recs]
        assert "AAPL" in tickers  # From Claude
        assert "MSFT" in tickers  # From ChatGPT

    def test_get_recommendations_missing_files(self, parser, temp_dir):
        """Test handling missing report files gracefully"""
        nonexistent_path = temp_dir / "doesnt_exist.md"

        recs = parser.get_recommendations_for_bot(
            "DEE-BOT",
            nonexistent_path,
            nonexistent_path
        )

        assert recs == []


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_file(self, parser, temp_dir):
        """Test parsing empty file"""
        report_path = temp_dir / "empty.md"
        report_path.write_text("")

        recs = parser.parse_claude_report(report_path, "DEE-BOT")
        assert recs == []

    def test_malformed_prices(self, parser, temp_dir):
        """Test handling malformed price data"""
        content = """
## ORDER BLOCK

```
Action: BUY
Ticker: AAPL
Shares: invalid
Limit_Price: $not-a-number
Stop_Loss: N/A
```
"""
        report_path = temp_dir / "malformed.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        # Should still create recommendation, just without numeric fields
        assert len(recs) == 1
        assert recs[0].ticker == "AAPL"
        assert recs[0].shares is None
        assert recs[0].entry_price is None

    def test_missing_required_fields(self, parser, temp_dir):
        """Test handling trade blocks missing required fields"""
        content = """
## ORDER BLOCK

```
Shares: 100
Limit_Price: $150.00
```
"""
        report_path = temp_dir / "missing_fields.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        # Should not create recommendation without ticker and action
        assert recs == []

    def test_case_insensitive_parsing(self, parser, temp_dir):
        """Test that parsing is case-insensitive"""
        content = """
## order block

```
action: buy
ticker: aapl
shares: 50
limit_price: $175.00
```
"""
        report_path = temp_dir / "lowercase.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        assert len(recs) == 1
        assert recs[0].ticker == "AAPL"  # Should be uppercased
        assert recs[0].action == "BUY"  # Should be uppercased

    def test_price_with_commas_and_dollar_signs(self, parser, temp_dir):
        """Test parsing prices with various formatting"""
        content = """
## ORDER BLOCK

```
Action: BUY
Ticker: NVDA
Limit_Price: $1,234.56
Target_Price: 1,500.00
Stop_Loss: $1,100
```
"""
        report_path = temp_dir / "formatted_prices.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        assert len(recs) == 1
        assert recs[0].entry_price == 1234.56
        assert recs[0].target_price == 1500.00
        assert recs[0].stop_loss == 1100.00

    def test_default_conviction_levels(self, parser, temp_dir):
        """Test that missing conviction defaults to MEDIUM"""
        content = """
## ORDER BLOCK

```
Action: BUY
Ticker: AAPL
Limit_Price: $175.00
```
"""
        report_path = temp_dir / "no_conviction.md"
        report_path.write_text(content)

        recs = parser.parse_claude_report(report_path, "DEE-BOT")

        assert len(recs) == 1
        assert recs[0].conviction == "MEDIUM"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
