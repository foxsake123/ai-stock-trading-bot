"""
Professional Report Formatter for Daily Pre-Market Reports
Generates executive-friendly markdown tables with signal strength indicators
"""

from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import pandas as pd


class SignalStrength(Enum):
    """Signal strength indicators"""
    VERY_STRONG_BULLISH = "++"
    STRONG_BULLISH = "+"
    WEAK_BULLISH = "~+"
    NEUTRAL = "○"
    WEAK_BEARISH = "~-"
    STRONG_BEARISH = "-"
    VERY_STRONG_BEARISH = "--"


class Priority(Enum):
    """Trade priority levels"""
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    WATCH = "⚪ WATCH"


class ReportFormatter:
    """
    Professional markdown report formatter for trading reports
    Optimized for executive readability and email/Slack compatibility
    """

    @staticmethod
    def format_signal_strength(score: float) -> str:
        """
        Convert composite score to signal strength indicator

        Args:
            score: Composite score from -100 to +100

        Returns:
            Signal strength indicator string
        """
        if score >= 70:
            return SignalStrength.VERY_STRONG_BULLISH.value
        elif score >= 40:
            return SignalStrength.STRONG_BULLISH.value
        elif score >= 15:
            return SignalStrength.WEAK_BULLISH.value
        elif score > -15:
            return SignalStrength.NEUTRAL.value
        elif score > -40:
            return SignalStrength.WEAK_BEARISH.value
        elif score > -70:
            return SignalStrength.STRONG_BEARISH.value
        else:
            return SignalStrength.VERY_STRONG_BEARISH.value

    @staticmethod
    def format_priority(confidence: float, signal_count: int, alt_data_score: float) -> str:
        """
        Determine trade priority based on multiple factors

        Args:
            confidence: Confidence score (0-100)
            signal_count: Number of confirming signals
            alt_data_score: Alternative data composite score

        Returns:
            Priority indicator string
        """
        # Calculate priority score
        priority_score = (confidence * 0.5) + (signal_count * 5) + (abs(alt_data_score) * 0.3)

        if priority_score >= 80:
            return Priority.CRITICAL.value
        elif priority_score >= 60:
            return Priority.HIGH.value
        elif priority_score >= 40:
            return Priority.MEDIUM.value
        elif priority_score >= 20:
            return Priority.LOW.value
        else:
            return Priority.WATCH.value

    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency with $ and commas"""
        return f"${amount:,.2f}"

    @staticmethod
    def format_percentage(value: float) -> str:
        """Format percentage with sign"""
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.1f}%"

    @staticmethod
    def format_risk_reward(entry: float, target: float, stop: float) -> str:
        """
        Calculate and format risk/reward ratio

        Args:
            entry: Entry price
            target: Target price
            stop: Stop loss price

        Returns:
            Formatted R/R ratio (e.g., "1:3.2")
        """
        if entry == stop:
            return "N/A"

        risk = abs(entry - stop)
        reward = abs(target - entry)

        if risk == 0:
            return "N/A"

        ratio = reward / risk
        return f"1:{ratio:.1f}"

    def generate_executive_summary_table(self, recommendations: List[Dict]) -> str:
        """
        Generate executive summary table with all key metrics

        Args:
            recommendations: List of trade recommendation dictionaries

        Returns:
            Markdown formatted table
        """
        if not recommendations:
            return "*No recommendations available.*\n"

        # Header
        table = "| Ticker | Strategy | Entry | Target | Stop | R/R | Signal | Alt Data | Priority | Action |\n"
        table += "|--------|----------|-------|--------|------|-----|--------|----------|----------|--------|\n"

        # Sort by priority (critical first)
        sorted_recs = sorted(recommendations, key=lambda x: x.get('priority_score', 0), reverse=True)

        for rec in sorted_recs:
            ticker = rec.get('ticker', 'N/A')
            strategy = rec.get('strategy', 'N/A')
            entry = self.format_currency(rec.get('entry_price', 0))
            target = self.format_currency(rec.get('target_price', 0))
            stop = self.format_currency(rec.get('stop_loss', 0))

            # Calculate R/R
            rr = self.format_risk_reward(
                rec.get('entry_price', 0),
                rec.get('target_price', 0),
                rec.get('stop_loss', 0)
            )

            # Format signal strength
            signal = self.format_signal_strength(rec.get('composite_score', 0))

            # Alt data score
            alt_data = self.format_signal_strength(rec.get('alt_data_score', 0))

            # Priority
            priority = self.format_priority(
                rec.get('confidence', 50),
                rec.get('signal_count', 0),
                rec.get('alt_data_score', 0)
            )

            # Action
            action = rec.get('action', 'HOLD')

            table += f"| **{ticker}** | {strategy} | {entry} | {target} | {stop} | {rr} | {signal} | {alt_data} | {priority} | **{action}** |\n"

        return table

    def generate_alt_data_matrix(self, ticker_signals: Dict[str, Dict]) -> str:
        """
        Generate alternative data signals matrix

        Args:
            ticker_signals: Dictionary mapping ticker to source signals

        Returns:
            Markdown formatted matrix
        """
        if not ticker_signals:
            return "*No alternative data signals available.*\n"

        # Header
        table = "| Ticker | Insider | Options | Social | Trends | Composite |\n"
        table += "|--------|---------|---------|--------|--------|----------|\n"

        for ticker, signals in sorted(ticker_signals.items()):
            insider = self.format_signal_strength(signals.get('insider', 0))
            options = self.format_signal_strength(signals.get('options', 0))
            social = self.format_signal_strength(signals.get('social', 0))
            trends = self.format_signal_strength(signals.get('trends', 0))
            composite = self.format_signal_strength(signals.get('composite', 0))

            table += f"| **{ticker}** | {insider} | {options} | {social} | {trends} | **{composite}** |\n"

        # Legend
        table += "\n**Legend**: `++` Very Strong | `+` Strong | `~+` Weak | `○` Neutral | `~-` Weak | `-` Strong | `--` Very Strong\n"

        return table

    def generate_risk_alerts_section(self, macro_factors: Dict, market_conditions: Dict) -> str:
        """
        Generate risk alerts section

        Args:
            macro_factors: Dictionary of macro economic factors
            market_conditions: Current market condition indicators

        Returns:
            Markdown formatted risk alerts
        """
        section = "## ⚠️ Risk Alerts & Macro Factors\n\n"

        # Market conditions
        section += "### Market Conditions\n\n"
        section += f"- **VIX**: {market_conditions.get('vix', 'N/A')} "
        section += f"({self._interpret_vix(market_conditions.get('vix', 0))})\n"
        section += f"- **Market Regime**: {market_conditions.get('regime', 'Unknown')}\n"
        section += f"- **Trend**: {market_conditions.get('trend', 'Unknown')}\n"
        section += f"- **Volatility**: {market_conditions.get('volatility', 'Unknown')}\n\n"

        # Macro factors
        section += "### Key Macro Events Today\n\n"

        if macro_factors:
            for event, details in macro_factors.items():
                impact = details.get('impact', 'MEDIUM')
                time = details.get('time', 'TBD')
                emoji = "🔴" if impact == "HIGH" else "🟡" if impact == "MEDIUM" else "🟢"

                section += f"- {emoji} **{time}** - {event}: {details.get('description', '')}\n"
        else:
            section += "*No major macro events scheduled for today.*\n"

        section += "\n"

        # Risk warnings
        section += "### Active Risk Warnings\n\n"
        warnings = self._get_risk_warnings(market_conditions)

        if warnings:
            for warning in warnings:
                section += f"- ⚠️ {warning}\n"
        else:
            section += "*No active risk warnings.*\n"

        section += "\n"

        return section

    def _interpret_vix(self, vix: float) -> str:
        """Interpret VIX level"""
        if vix < 12:
            return "Very Low - Complacent"
        elif vix < 20:
            return "Low - Normal"
        elif vix < 30:
            return "Elevated - Caution"
        elif vix < 40:
            return "High - Fear"
        else:
            return "Very High - Panic"

    def _get_risk_warnings(self, market_conditions: Dict) -> List[str]:
        """Generate risk warnings based on market conditions"""
        warnings = []

        vix = market_conditions.get('vix', 0)
        if vix > 30:
            warnings.append(f"Elevated volatility (VIX {vix:.1f}) - Reduce position sizes")

        if market_conditions.get('regime') == 'BEARISH':
            warnings.append("Bearish market regime - Favor defensive positions")

        if market_conditions.get('trend') == 'DOWNTREND':
            warnings.append("Market in downtrend - Exercise caution on longs")

        return warnings

    def generate_execution_checklist(self, trading_date: datetime) -> str:
        """
        Generate execution checklist with specific times

        Args:
            trading_date: Date of trading

        Returns:
            Markdown formatted checklist
        """
        section = "## ✅ Execution Checklist\n\n"

        section += f"### {trading_date.strftime('%A, %B %d, %Y')}\n\n"

        section += "#### Pre-Market (7:00 AM - 9:30 AM ET)\n\n"
        section += "- [ ] **7:00 AM** - Review overnight news and international markets\n"
        section += "- [ ] **8:00 AM** - Check pre-market volume and price action\n"
        section += "- [ ] **8:30 AM** - Monitor economic data releases\n"
        section += "- [ ] **9:00 AM** - Final review of trade plan and size adjustments\n"
        section += "- [ ] **9:15 AM** - Set up order entries and alerts\n\n"

        section += "#### Market Open (9:30 AM - 10:30 AM ET)\n\n"
        section += "- [ ] **9:30 AM** - Execute CRITICAL priority trades (if conditions met)\n"
        section += "- [ ] **9:45 AM** - Monitor initial price action for confirmation\n"
        section += "- [ ] **10:00 AM** - Execute HIGH priority trades\n"
        section += "- [ ] **10:15 AM** - Adjust stops based on volatility\n\n"

        section += "#### Mid-Day (10:30 AM - 2:00 PM ET)\n\n"
        section += "- [ ] **11:00 AM** - Execute MEDIUM priority trades (if setups valid)\n"
        section += "- [ ] **12:00 PM** - Review P&L and risk exposure\n"
        section += "- [ ] **1:00 PM** - Monitor for afternoon catalyst trades\n\n"

        section += "#### Power Hour (3:00 PM - 4:00 PM ET)\n\n"
        section += "- [ ] **3:00 PM** - Final trade entries (if planned)\n"
        section += "- [ ] **3:30 PM** - Adjust overnight positions\n"
        section += "- [ ] **3:45 PM** - Prepare closing orders\n"
        section += "- [ ] **4:00 PM** - Log execution results\n\n"

        section += "#### Post-Market (4:00 PM - 5:00 PM ET)\n\n"
        section += "- [ ] **4:15 PM** - Review day's performance\n"
        section += "- [ ] **4:30 PM** - Update trade journal\n"
        section += "- [ ] **4:45 PM** - Plan for next trading day\n\n"

        return section

    def generate_methodology_appendix(self) -> str:
        """
        Generate data source methodology appendix

        Returns:
            Markdown formatted appendix
        """
        section = "## 📊 Data Source Methodology\n\n"

        section += "### Signal Weighting\n\n"
        section += "| Data Source | Weight | Rationale |\n"
        section += "|-------------|--------|----------|\n"
        section += "| Insider Transactions | 25% | C-suite trades are strong signals |\n"
        section += "| Options Flow | 25% | Unusual activity predicts moves |\n"
        section += "| Social Sentiment | 20% | Retail momentum indicator |\n"
        section += "| Google Trends | 15% | Interest spike predictor |\n"
        section += "| Other Sources | 15% | Additional confirmation |\n\n"

        section += "### Composite Score Calculation\n\n"
        section += "The composite score is calculated as a weighted average of all data sources:\n\n"
        section += "```\nComposite Score = Σ(Source Score × Source Weight × Confidence)\n```\n\n"
        section += "- **Range**: -100 (very bearish) to +100 (very bullish)\n"
        section += "- **Interpretation**: >10 = Bullish, <-10 = Bearish, -10 to 10 = Neutral\n\n"

        section += "### Priority Scoring\n\n"
        section += "Trade priority is determined by:\n\n"
        section += "```\nPriority Score = (Confidence × 0.5) + (Signal Count × 5) + (|Alt Data| × 0.3)\n```\n\n"
        section += "- **CRITICAL** (🔴): Score ≥80 - Execute immediately if conditions met\n"
        section += "- **HIGH** (🟠): Score ≥60 - Execute within first hour\n"
        section += "- **MEDIUM** (🟡): Score ≥40 - Execute if setup confirms\n"
        section += "- **LOW** (🟢): Score ≥20 - Watch for better entry\n"
        section += "- **WATCH** (⚪): Score <20 - Monitor only\n\n"

        section += "### Risk/Reward Calculation\n\n"
        section += "```\nRisk = |Entry - Stop Loss|\nReward = |Target - Entry|\nR/R Ratio = Reward / Risk\n```\n\n"
        section += "**Minimum acceptable R/R**: 1:2 (risk $1 to make $2)\n\n"

        section += "### Data Sources\n\n"
        section += "- **Insider Transactions**: SEC Form 4 filings via Financial Datasets API\n"
        section += "- **Options Flow**: Unusual options activity via Yahoo Finance\n"
        section += "- **Social Sentiment**: Reddit WallStreetBets via PRAW (when enabled)\n"
        section += "- **Google Trends**: Search interest via pytrends library\n"
        section += "- **Technical Analysis**: Price action, volume, indicators\n"
        section += "- **Fundamental Analysis**: Financial metrics, valuation ratios\n\n"

        section += "### Disclaimer\n\n"
        section += "> This report is for informational purposes only and does not constitute financial advice.\n"
        section += "> Past performance is not indicative of future results. Trading involves substantial risk.\n"
        section += "> Always perform your own due diligence before making investment decisions.\n\n"

        return section

    def generate_section_divider(self, title: str, emoji: str = "📈") -> str:
        """Generate visually distinct section divider"""
        divider = "\n" + "=" * 80 + "\n"
        divider += f"{emoji} **{title}** {emoji}\n"
        divider += "=" * 80 + "\n\n"
        return divider


class QuickFormatters:
    """Quick formatting utilities for common use cases"""

    @staticmethod
    def quick_table(data: List[List[str]], headers: List[str]) -> str:
        """
        Generate a quick markdown table

        Args:
            data: List of rows (each row is a list of strings)
            headers: List of header strings

        Returns:
            Markdown table string
        """
        # Create header row
        table = "| " + " | ".join(headers) + " |\n"

        # Create separator
        table += "|" + "|".join(["---" for _ in headers]) + "|\n"

        # Create data rows
        for row in data:
            table += "| " + " | ".join(str(cell) for cell in row) + " |\n"

        return table

    @staticmethod
    def quick_bullet_list(items: List[str], indent: int = 0) -> str:
        """Generate a quick bullet list"""
        prefix = "  " * indent
        return "\n".join([f"{prefix}- {item}" for item in items]) + "\n"

    @staticmethod
    def quick_numbered_list(items: List[str], indent: int = 0) -> str:
        """Generate a quick numbered list"""
        prefix = "  " * indent
        return "\n".join([f"{prefix}{i+1}. {item}" for i, item in enumerate(items)]) + "\n"

    @staticmethod
    def quick_alert_box(message: str, alert_type: str = "INFO") -> str:
        """
        Generate an alert box

        Args:
            message: Alert message
            alert_type: INFO, WARNING, ERROR, SUCCESS

        Returns:
            Formatted alert
        """
        emoji_map = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅"
        }

        emoji = emoji_map.get(alert_type, "ℹ️")
        box = f"\n> {emoji} **{alert_type}**\n>\n> {message}\n\n"
        return box
