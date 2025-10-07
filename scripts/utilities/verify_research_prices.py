#!/usr/bin/env python3
"""
Verify Research Price Discrepancies
Compare ChatGPT vs Claude recommended prices with current market data
"""

import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

load_dotenv()

def main():
    # Initialize Alpaca data client
    api_key = os.getenv('ALPACA_API_KEY_DEE')
    secret_key = os.getenv('ALPACA_SECRET_KEY_DEE')

    if not api_key or not secret_key:
        print("ERROR: Alpaca API keys not found in .env")
        return

    data_client = StockHistoricalDataClient(api_key, secret_key)

    # Tickers to verify
    tickers = ['WMT', 'JNJ', 'DUK', 'KO', 'PG']

    # Research recommendations
    chatgpt_prices = {
        'WMT': 170.00,
        'JNJ': 160.50,
        'DUK': 92.00,
        'KO': 63.50,
        'PG': 150.00
    }

    claude_prices = {
        'WMT': 102.60,
        'JNJ': 188.50,
        'DUK': 124.56,
        'KO': 66.12,
        'PG': 150.53
    }

    print("\n" + "="*90)
    print("PRICE VERIFICATION: ChatGPT vs Claude Research Recommendations")
    print("="*90 + "\n")

    try:
        # Get latest market quotes
        request = StockLatestQuoteRequest(symbol_or_symbols=tickers)
        quotes = data_client.get_stock_latest_quote(request)

        results = []

        for ticker in tickers:
            quote = quotes[ticker]
            ask = float(quote.ask_price)
            bid = float(quote.bid_price)
            mid = (ask + bid) / 2

            chatgpt = chatgpt_prices[ticker]
            claude = claude_prices[ticker]

            chatgpt_diff = abs(mid - chatgpt)
            claude_diff = abs(mid - claude)
            chatgpt_pct = (chatgpt_diff / mid) * 100
            claude_pct = (claude_diff / mid) * 100

            print(f"{ticker} (Current Market Price: ${mid:.2f})")
            print("-" * 90)
            print(f"  Ask: ${ask:.2f} | Bid: ${bid:.2f}")
            print(f"  ChatGPT Recommendation: ${chatgpt:.2f} (diff: ${chatgpt_diff:.2f}, {chatgpt_pct:.1f}%)")
            print(f"  Claude Recommendation:  ${claude:.2f} (diff: ${claude_diff:.2f}, {claude_pct:.1f}%)")

            # Determine winner
            if chatgpt_diff < claude_diff:
                winner = "ChatGPT"
                winner_diff = chatgpt_diff
                loser_diff = claude_diff
                verdict_msg = f"ChatGPT is ${loser_diff - winner_diff:.2f} closer to market"
            else:
                winner = "Claude"
                winner_diff = claude_diff
                loser_diff = chatgpt_diff
                verdict_msg = f"Claude is ${loser_diff - winner_diff:.2f} closer to market"

            # Flag critical issues
            max_pct_diff = max(chatgpt_pct, claude_pct)
            if max_pct_diff > 15:
                status = "CRITICAL - MAJOR DISCREPANCY"
            elif max_pct_diff > 5:
                status = "WARNING - Moderate discrepancy"
            else:
                status = "OK - Minor difference"

            print(f"  VERDICT: {verdict_msg}")
            print(f"  STATUS: {status}")
            print()

            results.append({
                'ticker': ticker,
                'market': mid,
                'winner': winner,
                'status': status,
                'max_diff_pct': max_pct_diff
            })

        # Summary
        print("="*90)
        print("SUMMARY")
        print("="*90)

        chatgpt_wins = sum(1 for r in results if r['winner'] == 'ChatGPT')
        claude_wins = sum(1 for r in results if r['winner'] == 'Claude')
        critical_count = sum(1 for r in results if 'CRITICAL' in r['status'])

        print(f"ChatGPT closer: {chatgpt_wins}/5")
        print(f"Claude closer: {claude_wins}/5")
        print(f"Critical discrepancies: {critical_count}/5")
        print()

        # Recommendations
        print("="*90)
        print("RECOMMENDATIONS")
        print("="*90)

        for r in results:
            if 'CRITICAL' in r['status']:
                print(f"  {r['ticker']}: Use {r['winner']} price (other source off by {r['max_diff_pct']:.1f}%)")
            else:
                print(f"  {r['ticker']}: Either source acceptable (within {r['max_diff_pct']:.1f}%)")

        print("\n" + "="*90)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
