#!/usr/bin/env python3
"""
Improved ChatGPT Report Parser
Handles mixed text/number formats and complex report structures
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class ImprovedReportParser:
    """Enhanced parser for ChatGPT trading reports"""

    def __init__(self):
        self.symbol_pattern = re.compile(r'\b[A-Z]{1,5}\b')
        self.price_patterns = [
            re.compile(r'\$?([\d,]+\.?\d*)'),  # $123.45 or 123.45
            re.compile(r'([\d,]+\.?\d*)\s*(?:dollars?|usd)', re.I),  # 123 dollars
            re.compile(r'(?:at|@)\s*\$?([\d,]+\.?\d*)'),  # at $123 or @123
        ]
        self.percentage_pattern = re.compile(r'([\d.]+)\s*%')
        self.size_pattern = re.compile(r'([\d.]+)\s*(?:%|percent|pct)', re.I)

        # Common symbol exclusions
        self.exclude_symbols = {'USD', 'ET', 'AM', 'PM', 'CEO', 'CFO', 'FDA', 'EPS', 'PE', 'IPO'}

    def extract_number(self, text: str, patterns: List = None) -> Optional[float]:
        """Extract a number from text using multiple patterns"""
        if patterns is None:
            patterns = self.price_patterns

        for pattern in patterns:
            match = pattern.search(text)
            if match:
                try:
                    # Remove commas and convert to float
                    num_str = match.group(1).replace(',', '')
                    return float(num_str)
                except (ValueError, AttributeError):
                    continue
        return None

    def extract_percentage(self, text: str) -> Optional[float]:
        """Extract percentage from text"""
        match = self.percentage_pattern.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def parse_trade_block(self, text_block: str) -> Optional[Dict]:
        """Parse a single trade block"""
        trade = {}
        lines = text_block.strip().split('\n')

        # Find symbol
        for line in lines:
            symbols = self.symbol_pattern.findall(line)
            valid_symbols = [s for s in symbols if s not in self.exclude_symbols]
            if valid_symbols:
                trade['symbol'] = valid_symbols[0]
                break

        if 'symbol' not in trade:
            return None

        # Combine all lines for analysis
        full_text = ' '.join(lines).lower()

        # Determine action
        if 'short' in full_text:
            trade['action'] = 'short'
        elif 'long' in full_text or 'buy' in full_text:
            trade['action'] = 'long'
        else:
            trade['action'] = 'long'  # Default

        # Extract catalyst
        catalyst_keywords = ['catalyst', 'event', 'earnings', 'fda', 'pdufa', 'approval',
                           'data', 'results', 'announcement', 'merger', 'buyout']
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in catalyst_keywords):
                trade['catalyst'] = line.strip()
                break

        # Extract entry price
        for line in lines:
            line_lower = line.lower()
            if 'entry' in line_lower or 'buy at' in line_lower or 'enter' in line_lower:
                price = self.extract_number(line)
                if price:
                    trade['entry'] = price
                    break

        # Extract stop loss
        for line in lines:
            line_lower = line.lower()
            if 'stop' in line_lower:
                # Check for percentage stop
                pct = self.extract_percentage(line)
                if pct:
                    trade['stop_pct'] = pct
                else:
                    price = self.extract_number(line)
                    if price:
                        trade['stop'] = price

        # Extract target
        for line in lines:
            line_lower = line.lower()
            if 'target' in line_lower or 'take profit' in line_lower or 'tp' in line_lower:
                price = self.extract_number(line)
                if price:
                    trade['target'] = price

        # Extract position size
        for line in lines:
            line_lower = line.lower()
            if 'size' in line_lower or 'position' in line_lower or 'allocate' in line_lower:
                pct = self.extract_percentage(line)
                if pct:
                    trade['size_pct'] = pct
                    break

        # Extract confidence/risk
        confidence_map = {
            'high': 'high',
            'medium-high': 'medium-high',
            'medium': 'medium',
            'low-medium': 'low-medium',
            'low': 'low'
        }

        for conf_key, conf_val in confidence_map.items():
            if conf_key in full_text:
                trade['confidence'] = conf_val
                break

        # Default values
        if 'size_pct' not in trade:
            trade['size_pct'] = 5  # Default 5% position
        if 'confidence' not in trade:
            trade['confidence'] = 'medium'

        return trade

    def parse_report(self, text: str) -> Dict:
        """Parse complete ChatGPT report"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': 'ChatGPT',
            'trades': [],
            'market_context': '',
            'parsing_errors': []
        }

        # Split text into potential trade blocks
        # Look for patterns like "1.", "Trade 1:", bullet points, etc.
        trade_patterns = [
            re.compile(r'(?:^|\n)(?:\d+\.|\*|-).*?(?=(?:^|\n)(?:\d+\.|\*|-)|$)', re.MULTILINE | re.DOTALL),
            re.compile(r'Trade\s*\d+:.*?(?=Trade\s*\d+:|$)', re.IGNORECASE | re.DOTALL),
            re.compile(r'Symbol:.*?(?=Symbol:|$)', re.IGNORECASE | re.DOTALL)
        ]

        trades_found = False
        for pattern in trade_patterns:
            matches = pattern.findall(text)
            if matches:
                for match in matches:
                    trade = self.parse_trade_block(match)
                    if trade:
                        report['trades'].append(trade)
                        trades_found = True

                if trades_found:
                    break

        # If no structured trades found, try paragraph-based parsing
        if not trades_found:
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                # Look for paragraphs with stock symbols
                symbols = self.symbol_pattern.findall(para)
                valid_symbols = [s for s in symbols if s not in self.exclude_symbols]

                if valid_symbols:
                    trade = self.parse_trade_block(para)
                    if trade:
                        report['trades'].append(trade)

        # Extract market context (first substantial paragraph)
        lines = text.split('\n')
        context_lines = []
        for line in lines[:30]:  # Check first 30 lines
            line = line.strip()
            if len(line) > 50 and not any(kw in line.lower() for kw in ['trade', 'symbol', 'entry', 'stop']):
                context_lines.append(line)
                if len(context_lines) >= 3:
                    break

        report['market_context'] = ' '.join(context_lines)

        # Add parsing statistics
        report['stats'] = {
            'trades_parsed': len(report['trades']),
            'parser_version': '2.0',
            'timestamp': datetime.now().isoformat()
        }

        return report

    def validate_trade(self, trade: Dict) -> bool:
        """Validate a parsed trade has required fields"""
        required = ['symbol']
        return all(field in trade for field in required)

    def save_parsed_report(self, report: Dict, output_path: str = None) -> str:
        """Save parsed report to JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"parsed_report_{timestamp}.json"

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return output_path


def test_parser():
    """Test the improved parser with sample data"""

    parser = ImprovedReportParser()

    # Test with problematic format
    test_text = """
    Market Analysis for September 16, 2025

    Trade 1: AAPL
    Entry: Buy at market (around $175.50)
    Stop Loss: 3% below entry
    Target: $185
    Position Size: 5% of portfolio
    Confidence: High
    Catalyst: iPhone 16 launch exceeding expectations

    Trade 2: TSLA
    Action: Long
    Entry: $245.
    Stop: 5% (percentage stop)
    Target: 280 dollars
    Size: 3.5%
    Risk: Medium-high
    Catalyst: Q3 deliveries beat
    """

    result = parser.parse_report(test_text)

    print("Parsed Report:")
    print(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    # Run test
    result = test_parser()

    print("\n" + "="*50)
    print(f"Successfully parsed {len(result['trades'])} trades")
    for trade in result['trades']:
        print(f"  - {trade.get('symbol')}: {trade.get('action', 'long')} @ "
              f"{trade.get('entry', 'market')} (size: {trade.get('size_pct')}%)")