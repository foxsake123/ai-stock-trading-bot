"""
Simple Ticker Extractor from External Research
===============================================
Extracts just ticker symbols + context from external research.
Multi-agent system calculates everything else with FRESH data.

Philosophy:
- External research = IDEA GENERATION (what to look at)
- Multi-agent system = VALIDATION + EXECUTION (how to trade it)

Author: AI Trading Bot System
Date: October 14, 2025
"""

import re
from pathlib import Path
from typing import List, Dict


def extract_tickers_from_markdown(report_path: Path) -> List[Dict]:
    """
    Extract ticker symbols and basic context from any markdown research report

    Returns:
        List of dicts with {ticker, catalyst, conviction, source}
    """
    if not report_path.exists():
        print(f"[WARNING] Report not found: {report_path}")
        return []

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tickers = []
    seen_tickers = set()

    # ONLY look for explicit section headers based on ACTUAL formats:
    # SHORGAN: "## TRADE 1: PTGX —"
    # DEE: "**Johnson & Johnson (JNJ) |"
    # ChatGPT: "### **GKOS**"

    # Pattern 1: SHORGAN trades "## TRADE 1: PTGX —"
    shorgan_pattern = r'##\s+TRADE \d+:\s+([A-Z]{1,5})\s+—'
    shorgan_matches = re.findall(shorgan_pattern, content)

    # Pattern 2: DEE holdings "**Johnson & Johnson (JNJ) | 18.6% allocation**"
    dee_pattern = r'\*\*[^(]+\(([A-Z]{1,5})\)\s+\|\s+[\d.]+%\s+allocation'
    dee_matches = re.findall(dee_pattern, content)

    # Pattern 3: ChatGPT format "### **GKOS**"
    chatgpt_pattern = r'###\s+\*\*([A-Z]{1,5})\*\*'
    chatgpt_matches = re.findall(chatgpt_pattern, content)

    all_matches = shorgan_matches + dee_matches + chatgpt_matches

    for ticker in all_matches:
        ticker = ticker.upper().strip()

        if ticker in seen_tickers:
            continue

        # Extract context for this ticker (always returns dict, just with more/less detail)
        context = extract_context_for_ticker(ticker, content)
        tickers.append(context)
        seen_tickers.add(ticker)

    return tickers


def extract_context_for_ticker(ticker: str, content: str) -> Dict:
    """Extract catalyst and conviction for a specific ticker"""

    # Find section containing this ticker (broader search)
    section_pattern = rf'(?:##|###|####|\*\*).*?{ticker}.*?\n(.*?)(?=\n(?:##|###|####|\*\*)|$)'
    match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    catalyst = None
    conviction = "MEDIUM"  # Default

    if match:
        section = match.group(1)

        # Extract catalyst
        catalyst_match = re.search(r'(?:Catalyst|Event).*?:(.+?)(?:\n|$)', section, re.IGNORECASE)
        if catalyst_match:
            catalyst = catalyst_match.group(1).strip()[:150]

        # If no explicit catalyst, look for key phrases
        if not catalyst:
            if 'FDA' in section or 'PDUFA' in section:
                catalyst = "FDA catalyst"
            elif 'earnings' in section.lower():
                catalyst = "Earnings catalyst"
            elif 'merger' in section.lower() or 'acquisition' in section.lower() or 'M&A' in section:
                catalyst = "M&A catalyst"
            elif 'defensive' in section.lower() or 'dividend' in section.lower():
                catalyst = "Defensive holding"

        # Extract conviction
        conviction_match = re.search(r'Conviction.*?:.*?(HIGH|MEDIUM|LOW)', section, re.IGNORECASE)
        if conviction_match:
            conviction = conviction_match.group(1).upper()

    # Always return a dict (even if minimal info)
    return {
        'ticker': ticker,
        'catalyst': catalyst or "General opportunity",
        'conviction': conviction
    }


def get_all_tickers_from_research(date: str) -> Dict[str, List[Dict]]:
    """
    Get all tickers from both Claude and ChatGPT research for a specific date

    Returns:
        {'claude': [...], 'chatgpt': [...]}
    """
    base_dir = Path(f"reports/premarket/{date}")

    claude_path = base_dir / "claude_research.md"
    chatgpt_path = base_dir / "chatgpt_research.md"

    result = {
        'claude': [],
        'chatgpt': []
    }

    if claude_path.exists():
        result['claude'] = extract_tickers_from_markdown(claude_path)
        for ticker in result['claude']:
            ticker['source'] = 'claude'

    if chatgpt_path.exists():
        result['chatgpt'] = extract_tickers_from_markdown(chatgpt_path)
        for ticker in result['chatgpt']:
            ticker['source'] = 'chatgpt'

    return result


def main():
    """Test the extractor"""
    import sys
    from datetime import datetime

    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')

    print("="*70)
    print("TICKER EXTRACTION FROM EXTERNAL RESEARCH")
    print("="*70)
    print(f"Date: {date}\n")

    tickers = get_all_tickers_from_research(date)

    print(f"Claude Tickers: {len(tickers['claude'])}")
    for t in tickers['claude']:
        print(f"  {t['ticker']:6s} - {t['conviction']:6s} - {t['catalyst'][:60]}")

    print(f"\nChatGPT Tickers: {len(tickers['chatgpt'])}")
    for t in tickers['chatgpt']:
        print(f"  {t['ticker']:6s} - {t['conviction']:6s} - {t['catalyst'][:60]}")

    # Combine and dedupe
    all_tickers = {}
    for t in tickers['claude'] + tickers['chatgpt']:
        ticker = t['ticker']
        if ticker not in all_tickers:
            all_tickers[ticker] = t
        else:
            # If both sources mention it, upgrade conviction
            if t['conviction'] == 'HIGH' or all_tickers[ticker]['conviction'] == 'HIGH':
                all_tickers[ticker]['conviction'] = 'HIGH'
            # Combine catalysts
            if t['catalyst'] not in all_tickers[ticker]['catalyst']:
                all_tickers[ticker]['catalyst'] += f" | {t['catalyst']}"

    print(f"\nTotal Unique Tickers: {len(all_tickers)}")
    for ticker, data in sorted(all_tickers.items()):
        print(f"  {ticker:6s} - {data['conviction']:6s}")


if __name__ == "__main__":
    main()
