"""
External Research Report Parser
================================
Parses Claude Deep Research and ChatGPT Deep Research markdown files
to extract stock recommendations for multi-agent validation.

Author: AI Trading Bot System
Date: October 14, 2025
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StockRecommendation:
    """Represents a stock recommendation from external research"""
    ticker: str
    action: str  # BUY, SELL, SHORT, HOLD
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    shares: Optional[int] = None
    position_size_pct: Optional[float] = None
    catalyst: Optional[str] = None
    catalyst_date: Optional[str] = None
    conviction: Optional[str] = None  # HIGH, MEDIUM, LOW
    rationale: Optional[str] = None
    source: str = "unknown"  # claude, chatgpt
    bot: str = "unknown"  # DEE-BOT, SHORGAN-BOT

    def to_dict(self):
        return {
            'ticker': self.ticker,
            'action': self.action,
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'shares': self.shares,
            'position_size_pct': self.position_size_pct,
            'catalyst': self.catalyst,
            'catalyst_date': self.catalyst_date,
            'conviction': self.conviction,
            'rationale': self.rationale,
            'source': self.source,
            'bot': self.bot
        }


class ExternalReportParser:
    """Parse external AI research reports (Claude, ChatGPT)"""

    def __init__(self):
        self.recommendations = []

    def parse_claude_report(self, report_path: Path, bot_name: str) -> List[StockRecommendation]:
        """
        Parse Claude Deep Research markdown report

        Args:
            report_path: Path to claude_research_*.md file
            bot_name: DEE-BOT or SHORGAN-BOT

        Returns:
            List of StockRecommendation objects
        """
        if not report_path.exists():
            print(f"[WARNING] Claude report not found: {report_path}")
            return []

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        recommendations = []

        # Try parsing ORDER BLOCK section first (old format)
        order_block_pattern = r'## 4\. EXACT ORDER BLOCK(.*?)(?=\n## [^#]|$)'
        match = re.search(order_block_pattern, content, re.DOTALL)

        if match:
            order_block = match.group(1)

            # Extract individual trade blocks
            trade_pattern = r'```\s*(.*?)\s*```'
            trade_blocks = re.findall(trade_pattern, order_block, re.DOTALL)

            for block in trade_blocks:
                rec = self._parse_trade_block(block, 'claude', bot_name)
                if rec:
                    recommendations.append(rec)

        # Also try parsing summary table format (new format)
        table_pattern = r'\| Rank \| Ticker.*?\n\|[-|]+\n((?:\|.+\n)+)'
        table_match = re.search(table_pattern, content)
        if table_match:
            table_rows = table_match.group(1).strip().split('\n')
            for row in table_rows:
                parts = [p.strip() for p in row.split('|') if p.strip()]
                if len(parts) >= 9:  # rank, ticker, direction, entry, target, stop, r/r, catalyst, date, conviction
                    ticker = parts[1]
                    direction = parts[2]
                    entry = parts[3].replace('$', '').replace(',', '')
                    target = parts[4].replace('$', '').replace(',', '')
                    stop = parts[5].replace('$', '').replace(',', '')
                    catalyst = parts[7]
                    catalyst_date = parts[8]
                    conviction = parts[9] if len(parts) > 9 else 'MEDIUM'

                    # Handle entry ranges like "$75-78"
                    if '-' in entry:
                        entry = entry.split('-')[0]

                    rec = StockRecommendation(
                        ticker=ticker,
                        action='SHORT' if 'SHORT' in direction.upper() else 'BUY',
                        entry_price=float(entry) if entry else None,
                        target_price=float(target) if target else None,
                        stop_loss=float(stop) if stop else None,
                        catalyst=catalyst,
                        catalyst_date=catalyst_date,
                        conviction=conviction.upper() if conviction else 'MEDIUM',
                        source='claude',
                        bot=bot_name
                    )
                    recommendations.append(rec)

        # Also parse narrative sections for additional context
        if bot_name == "SHORGAN-BOT":
            # Look for "Trade X: TICKER" format
            trade_pattern = r'### Trade \d+: (\w+)(.*?)(?=### Trade \d+:|## |$)'
            matches = re.findall(trade_pattern, content, re.DOTALL)

            for ticker, trade_content in matches:
                # See if we already have this from ORDER BLOCK
                existing = [r for r in recommendations if r.ticker == ticker]
                if existing:
                    # Enhance with additional context
                    self._enhance_recommendation(existing[0], trade_content)
                else:
                    # Create new recommendation from narrative
                    rec = self._parse_narrative_trade(ticker, trade_content, 'claude', bot_name)
                    if rec:
                        recommendations.append(rec)

        elif bot_name == "DEE-BOT":
            # Parse DEE-BOT holdings section - look for "**Ticker (SYMBOL) | X% allocation"
            holdings_pattern = r'\*\*([^(]+)\((\w+)\) \| ([\d.]+)% allocation \| \$([,\d]+)\*\*(.*?)(?=\*\*[A-Z]|\n##|\Z)'
            matches = re.findall(holdings_pattern, content, re.DOTALL)

            for company_name, ticker, allocation_pct, dollar_amount, holding_content in matches:
                rec = StockRecommendation(
                    ticker=ticker,
                    action='BUY',
                    position_size_pct=float(allocation_pct),
                    source='claude',
                    bot='DEE-BOT'
                )

                # Extract additional details from content
                price_match = re.search(r'Recent price:\s*\$?([\d.]+)', holding_content)
                if price_match:
                    try:
                        price_str = price_match.group(1).rstrip('.')
                        rec.entry_price = float(price_str)
                    except ValueError:
                        pass

                rationale_match = re.search(r'\*\*Rationale:\*\*(.+?)(?:\n\n|\Z)', holding_content, re.DOTALL)
                if rationale_match:
                    rec.rationale = rationale_match.group(1).strip()[:200]

                recommendations.append(rec)

            # Also try older format: "#### TICKER -"
            if not recommendations:
                holdings_pattern = r'#### (\w+) -[^#]+(.*?)(?=####|##|$)'
                matches = re.findall(holdings_pattern, content, re.DOTALL)

                for ticker, holding_content in matches:
                    rec = self._parse_narrative_trade(ticker, holding_content, 'claude', bot_name)
                    if rec:
                        recommendations.append(rec)

        print(f"[INFO] Parsed {len(recommendations)} recommendations from Claude {bot_name} report")
        return recommendations

    def parse_chatgpt_report(self, report_path: Path) -> List[StockRecommendation]:
        """
        Parse ChatGPT Deep Research markdown report

        Args:
            report_path: Path to chatgpt_research_*.md file

        Returns:
            List of StockRecommendation objects
        """
        if not report_path.exists():
            print(f"[WARNING] ChatGPT report not found: {report_path}")
            return []

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        recommendations = []

        # Parse summary table
        table_pattern = r'\| (Shorgan|Dee)‑Bot \| \*\*(\w+)\*\* \| (Long|Short) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| \*\*([\d.]+)%?\*\* \|'
        matches = re.findall(table_pattern, content)

        for bot, ticker, action, entry, stop, target, size in matches:
            rec = StockRecommendation(
                ticker=ticker,
                action='BUY' if action == 'Long' else 'SHORT',
                entry_price=float(entry),
                stop_loss=float(stop),
                target_price=float(target),
                position_size_pct=float(size),
                source='chatgpt',
                bot=f"{bot.upper()}-BOT"
            )
            recommendations.append(rec)

        # Enhance with details from narrative sections
        for rec in recommendations:
            # Find detailed section for this ticker
            ticker_section_pattern = rf'### \*\*{rec.ticker}\*\*(.*?)(?=###|\Z)'
            match = re.search(ticker_section_pattern, content, re.DOTALL)

            if match:
                section = match.group(1)

                # Extract catalyst
                catalyst_match = re.search(r'\*\*Catalyst\*\*:(.+?)(?:\n|$)', section)
                if catalyst_match:
                    rec.catalyst = catalyst_match.group(1).strip()

                # Extract rationale
                rationale_match = re.search(r'\*\*Rationale\*\*:(.+?)(?:\n\*\*|$)', section, re.DOTALL)
                if rationale_match:
                    rec.rationale = rationale_match.group(1).strip()[:200]

        print(f"[INFO] Parsed {len(recommendations)} recommendations from ChatGPT report")
        return recommendations

    def _parse_trade_block(self, block: str, source: str, bot: str) -> Optional[StockRecommendation]:
        """Parse individual trade block from ORDER BLOCK section"""
        data = {'source': source, 'bot': bot}

        for line in block.strip().split('\n'):
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()

            if key == 'action':
                data['action'] = value.upper()
            elif key == 'ticker':
                data['ticker'] = value.upper()
            elif key == 'shares':
                try:
                    data['shares'] = int(value)
                except ValueError:
                    pass
            elif key == 'limit_price':
                try:
                    data['entry_price'] = float(value.replace('$', '').replace(',', ''))
                except ValueError:
                    pass
            elif key == 'stop_loss':
                if not value.upper().startswith('N/A'):
                    try:
                        data['stop_loss'] = float(value.replace('$', '').replace(',', ''))
                    except ValueError:
                        pass
            elif key == 'target_price':
                if not value.upper().startswith('N/A'):
                    try:
                        data['target_price'] = float(value.replace('$', '').replace(',', ''))
                    except ValueError:
                        pass
            elif key == 'catalyst_date':
                if value.upper() != 'N/A':
                    data['catalyst_date'] = value
            elif key == 'one-line_rationale':
                data['rationale'] = value

        if data.get('ticker') and data.get('action'):
            return StockRecommendation(**data)

        return None

    def _parse_narrative_trade(self, ticker: str, content: str, source: str, bot: str) -> Optional[StockRecommendation]:
        """Parse trade from narrative section"""
        data = {
            'ticker': ticker,
            'source': source,
            'bot': bot
        }

        # Determine action
        if 'SHORT' in content.upper() or 'SELL SHORT' in content.upper():
            data['action'] = 'SHORT'
        elif 'BUY' in content.upper() or 'LONG' in content.upper():
            data['action'] = 'BUY'
        else:
            data['action'] = 'HOLD'

        # Extract prices
        entry_match = re.search(r'Entry Price.*?\$?([\d.,-]+)', content, re.IGNORECASE)
        if entry_match:
            try:
                data['entry_price'] = float(entry_match.group(1).replace(',', '').replace('$', '').split('-')[0])
            except ValueError:
                pass

        target_match = re.search(r'Target Price.*?\$?([\d.,-]+)', content, re.IGNORECASE)
        if target_match:
            try:
                data['target_price'] = float(target_match.group(1).replace(',', '').replace('$', ''))
            except ValueError:
                pass

        stop_match = re.search(r'Stop Loss.*?\$?([\d.,-]+)', content, re.IGNORECASE)
        if stop_match:
            try:
                data['stop_loss'] = float(stop_match.group(1).replace(',', '').replace('$', ''))
            except ValueError:
                pass

        # Extract position size
        size_match = re.search(r'Position Size.*?([\d.]+)[-–]?([\d.]+)?%', content, re.IGNORECASE)
        if size_match:
            try:
                data['position_size_pct'] = float(size_match.group(1))
            except ValueError:
                pass

        # Extract conviction
        conviction_match = re.search(r'Conviction.*?:.*?(HIGH|MEDIUM|LOW)', content, re.IGNORECASE)
        if conviction_match:
            data['conviction'] = conviction_match.group(1).upper()

        # Extract catalyst
        catalyst_match = re.search(r'Catalyst.*?:(.+?)(?:\n\*\*|$)', content, re.IGNORECASE)
        if catalyst_match:
            data['catalyst'] = catalyst_match.group(1).strip()[:100]

        # Extract rationale
        rationale_match = re.search(r'Rationale.*?:(.+?)(?:\n\*\*|$)', content, re.DOTALL | re.IGNORECASE)
        if rationale_match:
            data['rationale'] = rationale_match.group(1).strip()[:200]

        return StockRecommendation(**data)

    def _enhance_recommendation(self, rec: StockRecommendation, content: str):
        """Enhance existing recommendation with additional context"""
        if not rec.catalyst:
            catalyst_match = re.search(r'Catalyst.*?:(.+?)(?:\n|$)', content, re.IGNORECASE)
            if catalyst_match:
                rec.catalyst = catalyst_match.group(1).strip()[:100]

        if not rec.conviction:
            conviction_match = re.search(r'Conviction.*?:.*?(HIGH|MEDIUM|LOW)', content, re.IGNORECASE)
            if conviction_match:
                rec.conviction = conviction_match.group(1).upper()

        if not rec.rationale or len(rec.rationale) < 50:
            rationale_match = re.search(r'Rationale.*?:(.+?)(?:\n\*\*|$)', content, re.DOTALL | re.IGNORECASE)
            if rationale_match:
                rec.rationale = rationale_match.group(1).strip()[:200]

    def get_recommendations_for_bot(self, bot_name: str, claude_path: Path, chatgpt_path: Path) -> List[StockRecommendation]:
        """
        Get all recommendations for a specific bot from both research sources

        Args:
            bot_name: DEE-BOT or SHORGAN-BOT
            claude_path: Path to Claude research report
            chatgpt_path: Path to ChatGPT research report

        Returns:
            Combined list of recommendations from both sources
        """
        recommendations = []

        # Parse Claude report
        if claude_path.exists():
            claude_recs = self.parse_claude_report(claude_path, bot_name)
            recommendations.extend(claude_recs)

        # Parse ChatGPT report
        if chatgpt_path.exists():
            chatgpt_recs = self.parse_chatgpt_report(chatgpt_path)
            # Filter for this bot
            bot_recs = [r for r in chatgpt_recs if r.bot == bot_name]
            recommendations.extend(bot_recs)

        return recommendations


def main():
    """Test the parser"""
    import sys
    from datetime import datetime

    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')

    base_dir = Path(f"reports/premarket/{date}")

    claude_dee = base_dir / "claude_research.md"  # Or specific bot file
    claude_shorgan = base_dir / "claude_research.md"
    chatgpt = base_dir / "chatgpt_research.md"

    parser = ExternalReportParser()

    print("="*70)
    print("EXTERNAL RESEARCH PARSER TEST")
    print("="*70)

    # Parse DEE-BOT
    dee_recs = parser.get_recommendations_for_bot("DEE-BOT", claude_dee, chatgpt)
    print(f"\nDEE-BOT Recommendations: {len(dee_recs)}")
    for rec in dee_recs:
        print(f"  {rec.ticker} - {rec.action} @ ${rec.entry_price} (source: {rec.source})")

    # Parse SHORGAN-BOT
    shorgan_recs = parser.get_recommendations_for_bot("SHORGAN-BOT", claude_shorgan, chatgpt)
    print(f"\nSHORGAN-BOT Recommendations: {len(shorgan_recs)}")
    for rec in shorgan_recs:
        print(f"  {rec.ticker} - {rec.action} @ ${rec.entry_price} (source: {rec.source})")


if __name__ == "__main__":
    main()
