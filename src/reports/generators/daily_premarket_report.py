"""
Enhanced Daily Pre-Market Report Generator
Produces executive-friendly reports with summary tables and detailed analysis
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

from src.reports.report_formatter import ReportFormatter, QuickFormatters
from src.data.alternative_data_aggregator import AlternativeDataAggregator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyPreMarketReport:
    """
    Generate comprehensive daily pre-market reports with executive summaries
    """

    def __init__(self, api_client=None):
        """
        Initialize report generator

        Args:
            api_client: Financial Datasets API client (optional)
        """
        self.api_client = api_client
        self.formatter = ReportFormatter()
        self.quick = QuickFormatters()
        self.alt_data_aggregator = AlternativeDataAggregator(api_client=api_client)

        # Load template
        self.template_path = Path(__file__).parent.parent.parent / "templates" / "report_template.md"

    async def generate_report(
        self,
        shorgan_recommendations: List[Dict],
        dee_recommendations: List[Dict],
        portfolio_data: Dict,
        market_data: Dict,
        macro_events: Dict = None
    ) -> str:
        """
        Generate complete daily pre-market report

        Args:
            shorgan_recommendations: SHORGAN-BOT trade recommendations
            dee_recommendations: DEE-BOT trade recommendations
            portfolio_data: Current portfolio status
            market_data: Market conditions and indicators
            macro_events: Macro economic events for the day

        Returns:
            Complete markdown report
        """
        logger.info("Generating daily pre-market report...")

        # Get all tickers for alternative data
        all_tickers = list(set(
            [r['ticker'] for r in shorgan_recommendations] +
            [r['ticker'] for r in dee_recommendations]
        ))

        # Fetch alternative data signals
        alt_data_result = await self.alt_data_aggregator.analyze_tickers(all_tickers)

        # Generate report sections
        report = self._generate_header(datetime.now(), market_data)
        report += self._generate_executive_summary(
            shorgan_recommendations,
            dee_recommendations,
            portfolio_data,
            alt_data_result
        )
        report += self._generate_shorgan_section(shorgan_recommendations, alt_data_result)
        report += self._generate_dee_section(dee_recommendations, alt_data_result)
        report += self._generate_alt_data_section(alt_data_result)
        report += self.formatter.generate_risk_alerts_section(
            macro_events or {},
            market_data
        )
        report += self.formatter.generate_execution_checklist(datetime.now())
        report += self._generate_trade_details(shorgan_recommendations, dee_recommendations)
        report += self._generate_market_context(market_data)
        report += self._generate_position_sizing_guidelines()
        report += self._generate_alerts_section(shorgan_recommendations, dee_recommendations)
        report += self.formatter.generate_methodology_appendix()
        report += self._generate_footer(datetime.now())

        logger.info("Report generation complete")
        return report

    def _generate_header(self, report_date: datetime, market_data: Dict) -> str:
        """Generate report header"""
        header = "# 📊 Daily Pre-Market Report\n"
        header += f"## {report_date.strftime('%B %d, %Y')} - {report_date.strftime('%A')}\n\n"
        header += f"**Generated**: {report_date.strftime('%I:%M %p ET')}\n"
        header += f"**Report Type**: Pre-Market Analysis\n"
        header += f"**Market Status**: {market_data.get('status', 'Pre-Market')}\n\n"
        header += "---\n\n"
        return header

    def _generate_executive_summary(
        self,
        shorgan_recs: List[Dict],
        dee_recs: List[Dict],
        portfolio_data: Dict,
        alt_data_result: Dict
    ) -> str:
        """Generate 30-second executive summary"""
        section = "## 🎯 30-Second Executive Summary\n\n"

        # Portfolio overview table
        section += "### Portfolio Overview\n\n"
        section += self._generate_portfolio_overview_table(portfolio_data)

        # Top opportunities (combined, sorted by priority)
        section += "\n### Top Opportunities Today\n\n"

        all_recs = shorgan_recs + dee_recs
        # Add alternative data scores to recommendations
        for rec in all_recs:
            ticker = rec['ticker']
            if ticker in alt_data_result.get('composite_scores', {}):
                rec['alt_data_score'] = alt_data_result['composite_scores'][ticker]['composite_score']
            else:
                rec['alt_data_score'] = 0

        top_opportunities = self.formatter.generate_executive_summary_table(all_recs[:10])
        section += top_opportunities

        # Key takeaway
        section += "\n**Key Takeaway**: "
        section += self._generate_key_takeaway(shorgan_recs, dee_recs, alt_data_result)
        section += "\n\n---\n\n"

        return section

    def _generate_portfolio_overview_table(self, portfolio_data: Dict) -> str:
        """Generate portfolio overview table"""
        dee = portfolio_data.get('dee_bot', {})
        shorgan = portfolio_data.get('shorgan_bot', {})

        table = "| Bot | Strategy | Cash | Deployed | Total Value | P&L (Today) | Win Rate |\n"
        table += "|-----|----------|------|----------|-------------|-------------|----------|\n"

        # DEE-BOT row
        table += f"| **DEE-BOT** | Beta-Neutral | "
        table += f"{self.formatter.format_currency(dee.get('cash', 0))} | "
        table += f"{self.formatter.format_currency(dee.get('deployed', 0))} | "
        table += f"{self.formatter.format_currency(dee.get('total_value', 0))} | "
        table += f"{self.formatter.format_percentage(dee.get('pnl_pct', 0))} | "
        table += f"{dee.get('win_rate', 0):.1f}% |\n"

        # SHORGAN-BOT row
        table += f"| **SHORGAN-BOT** | Catalyst | "
        table += f"{self.formatter.format_currency(shorgan.get('cash', 0))} | "
        table += f"{self.formatter.format_currency(shorgan.get('deployed', 0))} | "
        table += f"{self.formatter.format_currency(shorgan.get('total_value', 0))} | "
        table += f"{self.formatter.format_percentage(shorgan.get('pnl_pct', 0))} | "
        table += f"{shorgan.get('win_rate', 0):.1f}% |\n"

        # Total row
        total_cash = dee.get('cash', 0) + shorgan.get('cash', 0)
        total_deployed = dee.get('deployed', 0) + shorgan.get('deployed', 0)
        total_value = dee.get('total_value', 0) + shorgan.get('total_value', 0)
        total_pnl = ((total_value / 200000) - 1) * 100 if total_value > 0 else 0
        avg_win_rate = (dee.get('win_rate', 0) + shorgan.get('win_rate', 0)) / 2

        table += f"| **TOTAL** | **COMBINED** | "
        table += f"**{self.formatter.format_currency(total_cash)}** | "
        table += f"**{self.formatter.format_currency(total_deployed)}** | "
        table += f"**{self.formatter.format_currency(total_value)}** | "
        table += f"**{self.formatter.format_percentage(total_pnl)}** | "
        table += f"**{avg_win_rate:.1f}%** |\n\n"

        return table

    def _generate_key_takeaway(
        self,
        shorgan_recs: List[Dict],
        dee_recs: List[Dict],
        alt_data: Dict
    ) -> str:
        """Generate key takeaway message"""
        total_recs = len(shorgan_recs) + len(dee_recs)
        high_priority = sum(1 for r in (shorgan_recs + dee_recs)
                          if r.get('priority_score', 0) >= 60)

        bullish_count = sum(1 for r in (shorgan_recs + dee_recs)
                           if r.get('composite_score', 0) > 10)
        bearish_count = sum(1 for r in (shorgan_recs + dee_recs)
                           if r.get('composite_score', 0) < -10)

        takeaway = f"{total_recs} opportunities identified, "
        takeaway += f"{high_priority} high-priority. "

        if bullish_count > bearish_count:
            takeaway += f"Market bias: BULLISH ({bullish_count} bullish vs {bearish_count} bearish). "
        elif bearish_count > bullish_count:
            takeaway += f"Market bias: BEARISH ({bearish_count} bearish vs {bullish_count} bullish). "
        else:
            takeaway += f"Market bias: NEUTRAL ({bullish_count} bullish, {bearish_count} bearish). "

        # Add alternative data insight
        strong_signals = sum(1 for score in alt_data.get('composite_scores', {}).values()
                           if abs(score['composite_score']) > 40)

        if strong_signals > 0:
            takeaway += f"Alternative data shows {strong_signals} strong signal(s)."

        return takeaway

    def _generate_shorgan_section(self, recommendations: List[Dict], alt_data: Dict) -> str:
        """Generate SHORGAN-BOT section"""
        section = self.formatter.generate_section_divider("SHORGAN-BOT Recommendations", "📈")

        section += "### Catalyst-Driven Trades (Beta ~1.0-1.5)\n\n"
        section += "*Aggressive, high-conviction trades based on specific catalysts*\n\n"

        if not recommendations:
            section += "*No SHORGAN-BOT recommendations for today.*\n\n"
            return section

        # Summary table
        section += self.formatter.generate_executive_summary_table(recommendations)
        section += "\n"

        # Detailed analysis for top 3
        section += "### Detailed Analysis (Top 3)\n\n"
        for i, rec in enumerate(recommendations[:3], 1):
            section += self._generate_detailed_trade_analysis(rec, alt_data, i)

        section += "---\n\n"
        return section

    def _generate_dee_section(self, recommendations: List[Dict], alt_data: Dict) -> str:
        """Generate DEE-BOT section"""
        section = self.formatter.generate_section_divider("DEE-BOT Recommendations", "🛡️")

        section += "### Beta-Neutral Defensive Trades (Beta ~0.4-0.6)\n\n"
        section += "*Conservative, stable trades with focus on capital preservation*\n\n"

        if not recommendations:
            section += "*No DEE-BOT recommendations for today.*\n\n"
            return section

        # Summary table
        section += self.formatter.generate_executive_summary_table(recommendations)
        section += "\n"

        # Detailed analysis for top 3
        section += "### Detailed Analysis (Top 3)\n\n"
        for i, rec in enumerate(recommendations[:3], 1):
            section += self._generate_detailed_trade_analysis(rec, alt_data, i)

        section += "---\n\n"
        return section

    def _generate_detailed_trade_analysis(
        self,
        rec: Dict,
        alt_data: Dict,
        rank: int
    ) -> str:
        """Generate detailed analysis for a single trade"""
        ticker = rec['ticker']

        analysis = f"#### {rank}. {ticker} - {rec.get('strategy', 'N/A')}\n\n"

        # Trade parameters
        analysis += "**Trade Parameters**:\n"
        analysis += f"- **Action**: {rec.get('action', 'N/A')}\n"
        analysis += f"- **Entry**: {self.formatter.format_currency(rec.get('entry_price', 0))}\n"
        analysis += f"- **Target**: {self.formatter.format_currency(rec.get('target_price', 0))}\n"
        analysis += f"- **Stop Loss**: {self.formatter.format_currency(rec.get('stop_loss', 0))}\n"
        analysis += f"- **Risk/Reward**: {self.formatter.format_risk_reward(rec.get('entry_price', 0), rec.get('target_price', 0), rec.get('stop_loss', 0))}\n"
        analysis += f"- **Position Size**: {rec.get('position_size', 0):.1f}%\n\n"

        # Thesis
        analysis += "**Investment Thesis**:\n"
        analysis += f"{rec.get('thesis', 'No thesis provided.')}\n\n"

        # Catalyst
        if rec.get('catalyst'):
            analysis += "**Catalyst**:\n"
            analysis += f"{rec['catalyst']}\n\n"

        # Alternative data
        if ticker in alt_data.get('composite_scores', {}):
            alt_score = alt_data['composite_scores'][ticker]
            analysis += "**Alternative Data**:\n"
            analysis += f"- Composite Score: {alt_score['composite_score']:.1f} "
            analysis += f"({self.formatter.format_signal_strength(alt_score['composite_score'])})\n"
            analysis += f"- Confidence: {alt_score['confidence']:.1f}%\n"
            analysis += f"- Signal Count: {alt_score['signal_count']}\n\n"

        # Risks
        if rec.get('risks'):
            analysis += "**Key Risks**:\n"
            for risk in rec['risks']:
                analysis += f"- {risk}\n"
            analysis += "\n"

        return analysis

    def _generate_alt_data_section(self, alt_data_result: Dict) -> str:
        """Generate alternative data signals section"""
        section = self.formatter.generate_section_divider("Alternative Data Signals Matrix", "🔍")

        # Generate matrix
        ticker_signals = {}
        for ticker, score_data in alt_data_result.get('composite_scores', {}).items():
            breakdown = score_data.get('breakdown', {})
            ticker_signals[ticker] = {
                'insider': breakdown.get('insider', {}).get('strength', 0),
                'options': breakdown.get('options', {}).get('strength', 0),
                'social': breakdown.get('social', {}).get('strength', 0),
                'trends': breakdown.get('trends', {}).get('strength', 0),
                'composite': score_data.get('composite_score', 0)
            }

        section += self.formatter.generate_alt_data_matrix(ticker_signals)
        section += "\n"

        # Signal breakdown
        section += "### Signal Breakdown by Ticker\n\n"
        if alt_data_result.get('report'):
            section += alt_data_result['report']
        else:
            section += "*No alternative data signals available.*\n"

        section += "\n---\n\n"
        return section

    def _generate_trade_details(
        self,
        shorgan_recs: List[Dict],
        dee_recs: List[Dict]
    ) -> str:
        """Generate detailed trade setup information"""
        section = "## 📝 Trade Setup Details\n\n"

        # SHORGAN-BOT details
        section += "### SHORGAN-BOT Setups\n\n"
        if shorgan_recs:
            for rec in shorgan_recs:
                section += self._generate_trade_setup_box(rec)
        else:
            section += "*No SHORGAN-BOT setups for today.*\n\n"

        # DEE-BOT details
        section += "### DEE-BOT Setups\n\n"
        if dee_recs:
            for rec in dee_recs:
                section += self._generate_trade_setup_box(rec)
        else:
            section += "*No DEE-BOT setups for today.*\n\n"

        section += "---\n\n"
        return section

    def _generate_trade_setup_box(self, rec: Dict) -> str:
        """Generate a trade setup box"""
        box = f"#### {rec['ticker']} - {rec.get('action', 'N/A')}\n\n"
        box += f"**Strategy**: {rec.get('strategy', 'N/A')}\n\n"
        box += "```\n"
        box += f"Entry:        {self.formatter.format_currency(rec.get('entry_price', 0))}\n"
        box += f"Target:       {self.formatter.format_currency(rec.get('target_price', 0))}\n"
        box += f"Stop Loss:    {self.formatter.format_currency(rec.get('stop_loss', 0))}\n"
        box += f"Risk/Reward:  {self.formatter.format_risk_reward(rec.get('entry_price', 0), rec.get('target_price', 0), rec.get('stop_loss', 0))}\n"
        box += f"Position:     {rec.get('position_size', 0):.1f}% of portfolio\n"
        box += f"Signal:       {self.formatter.format_signal_strength(rec.get('composite_score', 0))}\n"
        box += "```\n\n"

        if rec.get('entry_conditions'):
            box += "**Entry Conditions**:\n"
            for condition in rec['entry_conditions']:
                box += f"- {condition}\n"
            box += "\n"

        return box

    def _generate_market_context(self, market_data: Dict) -> str:
        """Generate market context section"""
        section = "## 📊 Market Context\n\n"

        # Current market regime
        section += "### Current Market Regime\n\n"
        section += f"- **Trend**: {market_data.get('trend', 'Unknown')}\n"
        section += f"- **Volatility**: {market_data.get('volatility', 'Unknown')} "
        section += f"(VIX: {market_data.get('vix', 'N/A')})\n"
        section += f"- **Regime**: {market_data.get('regime', 'Unknown')}\n"
        section += f"- **Support**: {market_data.get('support', 'N/A')}\n"
        section += f"- **Resistance**: {market_data.get('resistance', 'N/A')}\n\n"

        # Sector performance (if available)
        if market_data.get('sector_performance'):
            section += "### Sector Performance (5-Day)\n\n"
            section += self._generate_sector_performance_table(market_data['sector_performance'])
            section += "\n"

        section += "---\n\n"
        return section

    def _generate_sector_performance_table(self, sector_data: Dict) -> str:
        """Generate sector performance table"""
        table = "| Sector | 5-Day % | Trend | Strength |\n"
        table += "|--------|---------|-------|----------|\n"

        for sector, data in sorted(sector_data.items(), key=lambda x: x[1].get('change', 0), reverse=True):
            change = data.get('change', 0)
            trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            strength = self.formatter.format_signal_strength(change * 10)  # Scale to -100 to 100

            table += f"| {sector} | {self.formatter.format_percentage(change)} | {trend} | {strength} |\n"

        return table

    def _generate_position_sizing_guidelines(self) -> str:
        """Generate position sizing guidelines"""
        section = "## 🎯 Position Sizing Guidelines\n\n"

        section += "### SHORGAN-BOT (Aggressive)\n"
        section += "- **Max Position Size**: 15% per trade\n"
        section += "- **Max Portfolio Exposure**: 80%\n"
        section += "- **Stop Loss**: Mandatory on all positions\n"
        section += "- **Target R/R**: Minimum 1:2\n"
        section += "- **Hold Period**: 1-30 days (catalyst-dependent)\n\n"

        section += "### DEE-BOT (Conservative)\n"
        section += "- **Max Position Size**: 10% per trade\n"
        section += "- **Max Portfolio Exposure**: 60%\n"
        section += "- **Stop Loss**: Mandatory on all positions\n"
        section += "- **Target R/R**: Minimum 1:1.5\n"
        section += "- **Hold Period**: 5-90 days (trend-following)\n\n"

        section += "---\n\n"
        return section

    def _generate_alerts_section(
        self,
        shorgan_recs: List[Dict],
        dee_recs: List[Dict]
    ) -> str:
        """Generate alerts and notifications section"""
        section = "## 🔔 Alerts & Notifications\n\n"

        # Price alerts
        section += "### Price Alerts Set\n\n"
        all_recs = shorgan_recs + dee_recs
        if all_recs:
            for rec in all_recs:
                section += f"- **{rec['ticker']}**: Entry @ {self.formatter.format_currency(rec.get('entry_price', 0))}, "
                section += f"Stop @ {self.formatter.format_currency(rec.get('stop_loss', 0))}\n"
        else:
            section += "*No price alerts set.*\n"
        section += "\n"

        # Catalyst reminders
        section += "### Catalyst Reminders\n\n"
        catalyst_recs = [r for r in all_recs if r.get('catalyst')]
        if catalyst_recs:
            for rec in catalyst_recs:
                section += f"- **{rec['ticker']}**: {rec['catalyst']}\n"
        else:
            section += "*No catalyst reminders.*\n"
        section += "\n"

        section += "---\n\n"
        return section

    def _generate_footer(self, report_date: datetime) -> str:
        """Generate report footer"""
        footer = "## 📞 Emergency Contacts & Resources\n\n"
        footer += "### Kill Switches\n"
        footer += "- **Halt All Trading**: `python scripts/emergency/halt_all_trading.py`\n"
        footer += "- **Close All Positions**: `python scripts/emergency/close_all_positions.py`\n\n"

        footer += "### Monitoring\n"
        footer += "- **Portfolio Status**: `python scripts/performance/get_portfolio_status.py`\n"
        footer += "- **Health Check**: `python health_check.py`\n\n"

        footer += "### Support\n"
        footer += "- **Trading Hours**: 9:30 AM - 4:00 PM ET\n"
        footer += "- **Pre-Market**: 7:00 AM - 9:30 AM ET\n"
        footer += "- **After Hours**: 4:00 PM - 8:00 PM ET\n\n"

        footer += "---\n\n"
        footer += f"**Report End** | Generated by AI Trading Bot v2.0 | {report_date.strftime('%Y-%m-%d %I:%M %p ET')}\n"

        return footer


async def generate_daily_report(
    shorgan_recs: List[Dict] = None,
    dee_recs: List[Dict] = None,
    api_client=None
) -> str:
    """
    Quick function to generate daily report

    Args:
        shorgan_recs: SHORGAN-BOT recommendations
        dee_recs: DEE-BOT recommendations
        api_client: Financial Datasets API client

    Returns:
        Markdown formatted report
    """
    # Mock data for demo
    if shorgan_recs is None:
        shorgan_recs = []
    if dee_recs is None:
        dee_recs = []

    portfolio_data = {
        'dee_bot': {
            'cash': 50000,
            'deployed': 50000,
            'total_value': 101500,
            'pnl_pct': 1.5,
            'win_rate': 62.5
        },
        'shorgan_bot': {
            'cash': 40000,
            'deployed': 60000,
            'total_value': 105000,
            'pnl_pct': 5.0,
            'win_rate': 58.3
        }
    }

    market_data = {
        'status': 'Pre-Market',
        'trend': 'UPTREND',
        'volatility': 'MODERATE',
        'regime': 'BULLISH',
        'vix': 18.5,
        'support': 4450,
        'resistance': 4520
    }

    macro_events = {
        'CPI Release': {
            'time': '8:30 AM ET',
            'impact': 'HIGH',
            'description': 'Consumer Price Index for September'
        }
    }

    generator = DailyPreMarketReport(api_client=api_client)
    report = await generator.generate_report(
        shorgan_recs,
        dee_recs,
        portfolio_data,
        market_data,
        macro_events
    )

    return report
