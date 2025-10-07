#!/usr/bin/env python3
"""
Verify ALL Research Price Discrepancies - CORRECTED
Compare ChatGPT vs Claude recommended prices with current market data
INCLUDES: DEE-BOT (10 stocks) + SHORGAN-BOT (8 stocks)
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

    # CORRECTED ChatGPT DEE-BOT prices from PDF
    chatgpt_dee = {
        'WMT': 102.00,
        'COST': 915.00,
        'MRK': 89.00,
        'UNH': 360.00,
        'NEE': 80.00
    }

    # Claude DEE-BOT prices
    claude_dee = {
        'WMT': 102.60,
        'JNJ': 188.50,
        'PG': 150.53,
        'KO': 66.12,
        'UNH': 359.37,
        'VZ': 41.67,
        'NEE': 82.47,
        'DUK': 124.56,
        'SO': 95.24,
        'T': 25.93,
        'CL': 77.42,
        'MDLZ': 61.87,
        'MO': 65.33
    }

    # CORRECTED ChatGPT SHORGAN-BOT prices from PDF
    chatgpt_shorgan = {
        'ARWR': 38.00,
        'CAR': 155.00,
        'RKT': 17.00,
        'PLUG': 4.50,  # SHORT
        'BYND': 2.50   # SHORT
    }

    # Claude SHORGAN-BOT prices
    claude_shorgan = {
        'ARQT': 19.77,
        'WOLF': 26.11,
        'BYND': 2.35,
        'HIMS': 54.47
    }

    # Combine all unique tickers
    all_tickers = set()
    all_tickers.update(chatgpt_dee.keys())
    all_tickers.update(claude_dee.keys())
    all_tickers.update(chatgpt_shorgan.keys())
    all_tickers.update(claude_shorgan.keys())

    all_tickers = sorted(all_tickers)

    print("\n" + "="*100)
    print("COMPLETE PRICE VERIFICATION: ChatGPT vs Claude (CORRECTED)")
    print("="*100 + "\n")

    try:
        # Get latest market quotes
        request = StockLatestQuoteRequest(symbol_or_symbols=list(all_tickers))
        quotes = data_client.get_stock_latest_quote(request)

        # DEE-BOT Analysis
        print("="*100)
        print("DEE-BOT PRICE VERIFICATION")
        print("="*100 + "\n")

        dee_overlap = set(chatgpt_dee.keys()).intersection(set(claude_dee.keys()))
        chatgpt_only_dee = set(chatgpt_dee.keys()) - set(claude_dee.keys())
        claude_only_dee = set(claude_dee.keys()) - set(chatgpt_dee.keys())

        print(f"OVERLAP: {len(dee_overlap)} stocks (both recommend)")
        print(f"ChatGPT ONLY: {len(chatgpt_only_dee)} stocks")
        print(f"Claude ONLY: {len(claude_only_dee)} stocks\n")

        # Overlapping DEE stocks
        if dee_overlap:
            print("OVERLAPPING DEE-BOT STOCKS:")
            print("-" * 100)
            for ticker in sorted(dee_overlap):
                quote = quotes[ticker]
                ask = float(quote.ask_price)
                bid = float(quote.bid_price)
                mid = (ask + bid) / 2

                chatgpt = chatgpt_dee[ticker]
                claude = claude_dee[ticker]

                chatgpt_diff = abs(mid - chatgpt)
                claude_diff = abs(mid - claude)
                chatgpt_pct = (chatgpt_diff / mid) * 100
                claude_pct = (claude_diff / mid) * 100

                print(f"{ticker} - Market: ${mid:.2f}")
                print(f"  ChatGPT: ${chatgpt:.2f} (diff ${chatgpt_diff:.2f}, {chatgpt_pct:.1f}%)")
                print(f"  Claude:  ${claude:.2f} (diff ${claude_diff:.2f}, {claude_pct:.1f}%)")

                if chatgpt_diff < claude_diff:
                    winner = "ChatGPT"
                else:
                    winner = "Claude"

                max_pct = max(chatgpt_pct, claude_pct)
                if max_pct > 15:
                    status = "CRITICAL"
                elif max_pct > 5:
                    status = "WARNING"
                else:
                    status = "OK"

                print(f"  VERDICT: {winner} closer | STATUS: {status}\n")

        # ChatGPT only DEE stocks
        if chatgpt_only_dee:
            print("\nChatGPT ONLY DEE-BOT STOCKS:")
            print("-" * 100)
            for ticker in sorted(chatgpt_only_dee):
                quote = quotes[ticker]
                mid = (float(quote.ask_price) + float(quote.bid_price)) / 2
                chatgpt = chatgpt_dee[ticker]
                diff = abs(mid - chatgpt)
                pct = (diff / mid) * 100

                status = "CRITICAL" if pct > 15 else "WARNING" if pct > 5 else "OK"
                print(f"{ticker} - Market: ${mid:.2f} | ChatGPT: ${chatgpt:.2f} | Diff: {pct:.1f}% | {status}")

        # Claude only DEE stocks
        if claude_only_dee:
            print("\nClaude ONLY DEE-BOT STOCKS:")
            print("-" * 100)
            for ticker in sorted(claude_only_dee):
                quote = quotes[ticker]
                mid = (float(quote.ask_price) + float(quote.bid_price)) / 2
                claude = claude_dee[ticker]
                diff = abs(mid - claude)
                pct = (diff / mid) * 100

                status = "CRITICAL" if pct > 15 else "WARNING" if pct > 5 else "OK"
                print(f"{ticker} - Market: ${mid:.2f} | Claude: ${claude:.2f} | Diff: {pct:.1f}% | {status}")

        # SHORGAN-BOT Analysis
        print("\n" + "="*100)
        print("SHORGAN-BOT PRICE VERIFICATION")
        print("="*100 + "\n")

        shorgan_overlap = set(chatgpt_shorgan.keys()).intersection(set(claude_shorgan.keys()))
        chatgpt_only_shorgan = set(chatgpt_shorgan.keys()) - set(claude_shorgan.keys())
        claude_only_shorgan = set(claude_shorgan.keys()) - set(chatgpt_shorgan.keys())

        print(f"OVERLAP: {len(shorgan_overlap)} stocks (both recommend)")
        print(f"ChatGPT ONLY: {len(chatgpt_only_shorgan)} stocks")
        print(f"Claude ONLY: {len(claude_only_shorgan)} stocks\n")

        # Overlapping SHORGAN stocks
        if shorgan_overlap:
            print("OVERLAPPING SHORGAN-BOT STOCKS:")
            print("-" * 100)
            for ticker in sorted(shorgan_overlap):
                quote = quotes[ticker]
                mid = (float(quote.ask_price) + float(quote.bid_price)) / 2

                chatgpt = chatgpt_shorgan[ticker]
                claude = claude_shorgan[ticker]

                chatgpt_diff = abs(mid - chatgpt)
                claude_diff = abs(mid - claude)
                chatgpt_pct = (chatgpt_diff / mid) * 100
                claude_pct = (claude_diff / mid) * 100

                # Check if short
                is_short = ticker in ['PLUG', 'BYND'] and chatgpt == chatgpt_shorgan.get(ticker)

                print(f"{ticker} - Market: ${mid:.2f} {'(SHORT POSITION)' if is_short else ''}")
                print(f"  ChatGPT: ${chatgpt:.2f} (diff ${chatgpt_diff:.2f}, {chatgpt_pct:.1f}%)")
                print(f"  Claude:  ${claude:.2f} (diff ${claude_diff:.2f}, {claude_pct:.1f}%)")

                if chatgpt_diff < claude_diff:
                    winner = "ChatGPT"
                else:
                    winner = "Claude"

                max_pct = max(chatgpt_pct, claude_pct)
                if max_pct > 15:
                    status = "CRITICAL"
                elif max_pct > 5:
                    status = "WARNING"
                else:
                    status = "OK"

                print(f"  VERDICT: {winner} closer | STATUS: {status}\n")

        # ChatGPT only SHORGAN stocks
        if chatgpt_only_shorgan:
            print("\nChatGPT ONLY SHORGAN-BOT STOCKS:")
            print("-" * 100)
            for ticker in sorted(chatgpt_only_shorgan):
                quote = quotes[ticker]
                mid = (float(quote.ask_price) + float(quote.bid_price)) / 2
                chatgpt = chatgpt_shorgan[ticker]
                diff = abs(mid - chatgpt)
                pct = (diff / mid) * 100

                is_short = ticker in ['PLUG', 'BYND']
                status = "CRITICAL" if pct > 15 else "WARNING" if pct > 5 else "OK"
                print(f"{ticker} - Market: ${mid:.2f} | ChatGPT: ${chatgpt:.2f} | Diff: {pct:.1f}% | {status} {'[SHORT]' if is_short else ''}")

        # Claude only SHORGAN stocks
        if claude_only_shorgan:
            print("\nClaude ONLY SHORGAN-BOT STOCKS:")
            print("-" * 100)
            for ticker in sorted(claude_only_shorgan):
                quote = quotes[ticker]
                mid = (float(quote.ask_price) + float(quote.bid_price)) / 2
                claude = claude_shorgan[ticker]
                diff = abs(mid - claude)
                pct = (diff / mid) * 100

                status = "CRITICAL" if pct > 15 else "WARNING" if pct > 5 else "OK"
                print(f"{ticker} - Market: ${mid:.2f} | Claude: ${claude:.2f} | Diff: {pct:.1f}% | {status}")

        # SUMMARY
        print("\n" + "="*100)
        print("SUMMARY")
        print("="*100)
        print(f"\nDEE-BOT:")
        print(f"  Overlap: {len(dee_overlap)} stocks (WMT, UNH, NEE)")
        print(f"  ChatGPT unique: {len(chatgpt_only_dee)} (COST, MRK)")
        print(f"  Claude unique: {len(claude_only_dee)} (JNJ, PG, KO, VZ, DUK, SO, T, CL, MDLZ, MO)")

        print(f"\nSHORGAN-BOT:")
        print(f"  Overlap: {len(shorgan_overlap)} stock (BYND)")
        print(f"  ChatGPT unique: {len(chatgpt_only_shorgan)} (ARWR, CAR, RKT, PLUG)")
        print(f"  Claude unique: {len(claude_only_shorgan)} (ARQT, WOLF, HIMS)")

        print(f"\nSHORT POSITIONS IDENTIFIED:")
        print(f"  ChatGPT: PLUG ($4.50), BYND ($2.50)")
        print(f"  Claude: None")

        print("\n" + "="*100)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
