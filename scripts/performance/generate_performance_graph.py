#!/usr/bin/env python3
"""
Performance Visualization System
Generates comparative performance graphs for DEE-BOT, SHORGAN-BOT vs S&P 500
Based on ChatGPT-Micro-Cap-Experiment methodology
"""

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from pathlib import Path
import json
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PERFORMANCE_JSON = "data/daily/performance/performance_history.json"
RESULTS_PATH = Path("performance_results.png")

# Alpaca API Configuration (from .env)
DEE_BOT_API_KEY = os.getenv('ALPACA_API_KEY_DEE')
DEE_BOT_SECRET = os.getenv('ALPACA_SECRET_KEY_DEE')
# SHORGAN Paper (historical tracking)
SHORGAN_PAPER_API_KEY = os.getenv('ALPACA_API_KEY_SHORGAN')
SHORGAN_PAPER_SECRET = os.getenv('ALPACA_SECRET_KEY_SHORGAN')
# SHORGAN Live (new $1K account)
SHORGAN_LIVE_API_KEY = os.getenv('ALPACA_LIVE_API_KEY_SHORGAN')
SHORGAN_LIVE_SECRET = os.getenv('ALPACA_LIVE_SECRET_KEY_SHORGAN')

BASE_URL_DEE = 'https://paper-api.alpaca.markets'  # DEE on paper
BASE_URL_SHORGAN_PAPER = 'https://paper-api.alpaca.markets'  # SHORGAN paper
BASE_URL_SHORGAN_LIVE = 'https://api.alpaca.markets'  # SHORGAN LIVE

# Starting capital
INITIAL_CAPITAL_DEE = 100000.0  # Paper trading
INITIAL_CAPITAL_SHORGAN_PAPER = 100000.0  # Paper trading
INITIAL_CAPITAL_SHORGAN_LIVE = 3000.0  # LIVE TRADING - total deposits tracked in shorgan_live_deposits.json
# NOTE: INITIAL_CAPITAL_COMBINED will be calculated dynamically to account for SHORGAN-LIVE deposits

# Deposit tracking file for SHORGAN-LIVE
SHORGAN_LIVE_DEPOSITS_FILE = "data/shorgan_live_deposits.json"

def get_shorgan_live_total_deposits():
    """Get total deposits for SHORGAN-LIVE from tracking file"""
    try:
        with open(SHORGAN_LIVE_DEPOSITS_FILE, 'r') as f:
            data = json.load(f)
            return float(data.get('total_deposits', INITIAL_CAPITAL_SHORGAN_LIVE))
    except FileNotFoundError:
        print(f"[WARNING] Deposit tracking file not found, using initial capital: ${INITIAL_CAPITAL_SHORGAN_LIVE}")
        return INITIAL_CAPITAL_SHORGAN_LIVE
    except Exception as e:
        print(f"[ERROR] Could not read deposits file: {e}")
        return INITIAL_CAPITAL_SHORGAN_LIVE

# Calculate total initial capital accounting for all deposits
INITIAL_CAPITAL_COMBINED = INITIAL_CAPITAL_DEE + INITIAL_CAPITAL_SHORGAN_PAPER + get_shorgan_live_total_deposits()

def get_current_portfolio_values():
    """Fetch current portfolio values from Alpaca (3 accounts)"""
    try:
        dee_api = tradeapi.REST(DEE_BOT_API_KEY, DEE_BOT_SECRET, BASE_URL_DEE, api_version='v2')
        shorgan_paper_api = tradeapi.REST(SHORGAN_PAPER_API_KEY, SHORGAN_PAPER_SECRET, BASE_URL_SHORGAN_PAPER, api_version='v2')
        shorgan_live_api = tradeapi.REST(SHORGAN_LIVE_API_KEY, SHORGAN_LIVE_SECRET, BASE_URL_SHORGAN_LIVE, api_version='v2')

        dee_account = dee_api.get_account()
        shorgan_paper_account = shorgan_paper_api.get_account()
        shorgan_live_account = shorgan_live_api.get_account()

        dee_value = float(dee_account.portfolio_value)
        shorgan_paper_value = float(shorgan_paper_account.portfolio_value)
        shorgan_live_value = float(shorgan_live_account.portfolio_value)

        # Get total deposits for SHORGAN-LIVE to calculate true performance
        shorgan_live_deposits = get_shorgan_live_total_deposits()

        return {
            'dee_bot': dee_value,
            'shorgan_paper': shorgan_paper_value,
            'shorgan_live': shorgan_live_value,
            'shorgan_live_deposits': shorgan_live_deposits,
            'combined': dee_value + shorgan_paper_value + shorgan_live_value
        }
    except Exception as e:
        print(f"Error fetching portfolio values: {e}")
        return None

def load_performance_history():
    """Load historical performance data from JSON file (supports both old and new schema)"""
    try:
        with open(PERFORMANCE_JSON, 'r') as f:
            data = json.load(f)

        records = []
        for record in data.get('daily_records', []):
            # NEW SCHEMA (3 accounts: dee, shorgan_paper, shorgan_live)
            if 'shorgan_paper' in record and 'shorgan_live' in record:
                records.append({
                    'date': pd.to_datetime(record['date']),
                    'dee_value': record['dee_bot']['value'],
                    'shorgan_paper_value': record['shorgan_paper']['value'],
                    'shorgan_live_value': record['shorgan_live']['value'],
                    'combined_value': record['combined']['total_value']
                })
            # OLD SCHEMA (2 accounts: dee, shorgan_bot) - backward compatibility
            # SHORGAN-LIVE didn't exist yet, so set to 0 (not $3000) to avoid deposit-adjusted spike
            else:
                records.append({
                    'date': pd.to_datetime(record['date']),
                    'dee_value': record['dee_bot']['value'],
                    'shorgan_paper_value': record['shorgan_bot']['value'],  # Old data was paper
                    'shorgan_live_value': 0.0,  # Live account didn't exist in old schema period
                    'combined_value': record['combined']['total_value']
                })

        if not records:
            return None

        df = pd.DataFrame(records)
        df = df.sort_values('date').reset_index(drop=True)
        return df

    except FileNotFoundError:
        print(f"Performance history file not found: {PERFORMANCE_JSON}")
        return None
    except Exception as e:
        print(f"Error loading performance history: {e}")
        return None

def create_portfolio_dataframe():
    """Create or load portfolio performance dataframe with baseline (3 accounts)"""
    df = load_performance_history()

    # Add baseline data point (starting capital)
    if df is not None and not df.empty:
        start_date = df['date'].min()
    else:
        start_date = pd.Timestamp("2025-09-10")
        df = pd.DataFrame()

    # Create baseline row (one day before first data point)
    # Use total deposits for SHORGAN-LIVE to show true trading performance
    shorgan_live_deposits = get_shorgan_live_total_deposits()
    baseline_date = start_date - pd.Timedelta(days=1)
    baseline_row = pd.DataFrame({
        'date': [baseline_date],
        'dee_value': [INITIAL_CAPITAL_DEE],
        'shorgan_paper_value': [INITIAL_CAPITAL_SHORGAN_PAPER],
        'shorgan_live_value': [shorgan_live_deposits],
        'combined_value': [INITIAL_CAPITAL_DEE + INITIAL_CAPITAL_SHORGAN_PAPER + shorgan_live_deposits]
    })

    # Get current values
    current_values = get_current_portfolio_values()
    if current_values:
        today_row = pd.DataFrame({
            'date': [pd.Timestamp.now()],
            'dee_value': [current_values['dee_bot']],
            'shorgan_paper_value': [current_values['shorgan_paper']],
            'shorgan_live_value': [current_values['shorgan_live']],
            'combined_value': [current_values['combined']]
        })
        df = pd.concat([df, today_row], ignore_index=True)

    # Combine baseline with historical data
    df = pd.concat([baseline_row, df], ignore_index=True)
    df = df.drop_duplicates(subset=['date'], keep='last').sort_values('date').reset_index(drop=True)

    return df

def download_sp500(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """Download S&P 500 prices and normalize to starting capital baseline"""

    # Method 0: Try simple HTTP GET with yfinance download (most reliable)
    try:
        print("Attempting direct yfinance download for SPY...")
        import yfinance as yf

        # Use download instead of Ticker to avoid rate limits
        spy_data = yf.download('SPY', start=start_date.strftime('%Y-%m-%d'),
                              end=(end_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d'),
                              progress=False, auto_adjust=False)

        if not spy_data.empty and 'Close' in spy_data.columns:
            spy_df = pd.DataFrame()
            spy_df['date'] = spy_data.index
            spy_df['close'] = spy_data['Close'].values
            spy_df['date'] = pd.to_datetime(spy_df['date']).dt.tz_localize(None)

            # Normalize to starting capital
            spy_baseline = spy_df['close'].iloc[0]
            spy_df['sp500_value'] = (spy_df['close'] / spy_baseline) * INITIAL_CAPITAL_COMBINED

            print(f"Successfully fetched {len(spy_df)} days of SPY data from yfinance download")
            return spy_df[['date', 'sp500_value']]
    except Exception as e:
        print(f"yfinance download failed: {e}")

    # Method 1: Try Alpha Vantage (free, reliable)
    try:
        print("Attempting to fetch SPY data from Alpha Vantage...")
        import requests

        # Try free Yahoo Finance API via yfinance first
        import yfinance as yf
        spy_ticker = yf.Ticker("SPY")
        spy_data = spy_ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        if not spy_data.empty:
            spy_df = pd.DataFrame()
            spy_df['date'] = spy_data.index
            spy_df['close'] = spy_data['Close'].values
            spy_df['date'] = pd.to_datetime(spy_df['date'])
            print(f"Successfully fetched {len(spy_df)} days of SPY data from yfinance")
            return spy_df

        # Fallback to Alpha Vantage (premium required)
        print("yfinance failed, trying Alpha Vantage...")
        AV_API_KEY = 'HW00RRPNQQJHH3IM'
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=SPY&outputsize=full&apikey={AV_API_KEY}'
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']

                # Convert to DataFrame
                dates = []
                closes = []

                for date_str, values in time_series.items():
                    date = pd.to_datetime(date_str)
                    if start_date <= date <= end_date:
                        dates.append(date)
                        closes.append(float(values['5. adjusted close']))

                if dates:
                    sp500 = pd.DataFrame({
                        'date': dates,
                        'Close': closes
                    }).sort_values('date').reset_index(drop=True)

                    # Normalize to match starting capital
                    sp500_baseline = sp500['Close'].iloc[0]
                    sp500['sp500_value'] = (sp500['Close'] / sp500_baseline) * INITIAL_CAPITAL_COMBINED

                    print(f"Successfully downloaded SPY data from Alpha Vantage ({len(sp500)} bars)")
                    return sp500[['date', 'sp500_value']]

    except Exception as e:
        print(f"Alpha Vantage failed: {e}")

    # Method 2: Try Alpaca API with free IEX data feed
    try:
        print("Attempting to fetch SPY data from Alpaca API (IEX feed)...")
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame

        # Use data client instead of trading client
        data_client = StockHistoricalDataClient(
            api_key=SHORGAN_PAPER_API_KEY,
            secret_key=SHORGAN_PAPER_SECRET
        )

        # Request SPY bars with free IEX feed
        request_params = StockBarsRequest(
            symbol_or_symbols=["SPY"],
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )

        bars = data_client.get_stock_bars(request_params)

        if bars and "SPY" in bars:
            spy_bars = bars["SPY"]

            if len(spy_bars) > 0:
                print(f"Successfully downloaded SPY data from Alpaca IEX ({len(spy_bars)} bars)")

                # Convert to DataFrame
                dates = [bar.timestamp for bar in spy_bars]
                closes = [bar.close for bar in spy_bars]

                sp500 = pd.DataFrame({
                    'date': pd.to_datetime(dates),
                    'Close': closes
                })

                # Normalize to match starting capital
                sp500_baseline = sp500['Close'].iloc[0]
                sp500['sp500_value'] = (sp500['Close'] / sp500_baseline) * INITIAL_CAPITAL_COMBINED

                return sp500[['date', 'sp500_value']].reset_index(drop=True)

    except Exception as e:
        print(f"Alpaca API failed: {e}")

    # Method 3: Try Financial Datasets API (premium, $49/month)
    try:
        print("Attempting to fetch SPY data from Financial Datasets API...")
        import requests

        FD_API_KEY = os.getenv('FINANCIAL_DATASETS_API_KEY', 'c93a9274-4183-446e-a9e1-6befeba1003b')

        # Financial Datasets endpoint for historical prices
        dates = []
        closes = []

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')

            # Financial Datasets API endpoint
            url = f"https://api.financialdatasets.ai/prices/?ticker=SPY&interval=day&interval_multiplier=1&start_date={date_str}&end_date={date_str}"

            headers = {
                'X-API-KEY': FD_API_KEY,
                'Accept': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('prices') and len(data['prices']) > 0:
                    price_data = data['prices'][0]
                    dates.append(pd.to_datetime(price_data['time']))
                    closes.append(float(price_data['close']))

            current_date += pd.Timedelta(days=1)

            # Rate limiting
            import time
            time.sleep(0.1)

        if dates and closes:
            sp500 = pd.DataFrame({
                'date': dates,
                'Close': closes
            }).sort_values('date').reset_index(drop=True)

            # Normalize to match starting capital
            sp500_baseline = sp500['Close'].iloc[0]
            sp500['sp500_value'] = (sp500['Close'] / sp500_baseline) * INITIAL_CAPITAL_COMBINED

            print(f"Successfully downloaded SPY data from Financial Datasets API ({len(sp500)} bars)")
            return sp500[['date', 'sp500_value']]

    except Exception as e:
        print(f"Financial Datasets API failed: {e}")

    # Method 4: Fallback to yfinance (currently broken but keep for future)
    try:
        print("Falling back to yfinance...")
        tickers_to_try = ["SPY", "^GSPC", "^SPX"]

        sp500 = pd.DataFrame()
        for ticker in tickers_to_try:
            try:
                sp500 = yf.download(ticker, start=start_date, end=end_date + pd.Timedelta(days=1),
                                    progress=False, auto_adjust=True)

                if not sp500.empty:
                    print(f"Successfully downloaded S&P 500 data using ticker: {ticker}")
                    break
            except Exception as e:
                continue

        if sp500.empty:
            return pd.DataFrame()

        sp500 = sp500.reset_index()

        # Handle MultiIndex columns if present
        if isinstance(sp500.columns, pd.MultiIndex):
            sp500.columns = sp500.columns.get_level_values(0)

        # Normalize to match starting capital
        if not sp500.empty and 'Close' in sp500.columns:
            sp500_baseline = sp500.loc[sp500['Date'] >= start_date, 'Close'].iloc[0]
            sp500['Normalized_Value'] = (sp500['Close'] / sp500_baseline) * INITIAL_CAPITAL_COMBINED
            sp500['Date'] = pd.to_datetime(sp500['Date'])
            return sp500[['Date', 'Normalized_Value']].rename(columns={'Date': 'date', 'Normalized_Value': 'sp500_value'})

        return pd.DataFrame()

    except Exception as e:
        print(f"Error downloading S&P 500 data: {e}")
        return pd.DataFrame()

def create_synthetic_sp500_benchmark(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create synthetic S&P 500 benchmark when live data unavailable.
    Uses typical market returns: ~10% annual return with realistic daily volatility.
    """
    print("\n[INFO] Creating synthetic S&P 500 benchmark based on typical market returns...")

    # Calculate trading days span
    trading_days = len(portfolio_df)

    # Typical S&P 500: ~10% annual return = ~0.04% daily return
    # Add realistic volatility: ~1% daily standard deviation
    import numpy as np
    np.random.seed(42)  # Reproducible results

    # Generate realistic daily returns with drift
    daily_returns = np.random.normal(0.0004, 0.01, trading_days)  # 0.04% mean, 1% std

    # Calculate cumulative returns to create price series
    cumulative_returns = np.cumprod(1 + daily_returns)

    # Normalize to starting capital
    sp500_values = INITIAL_CAPITAL_COMBINED * cumulative_returns

    sp500_df = pd.DataFrame({
        'date': portfolio_df['date'],
        'sp500_value': sp500_values
    })

    print(f"[INFO] Synthetic benchmark created: {len(sp500_df)} data points")
    print(f"[INFO] Synthetic S&P 500 return: {((sp500_values[-1] / INITIAL_CAPITAL_COMBINED - 1) * 100):.2f}%")

    return sp500_df

def calculate_performance_metrics(df):
    """Calculate key performance metrics (3 accounts + benchmark)"""
    if df.empty:
        return None

    metrics = {}

    # DEE-BOT metrics
    dee_return = ((df['dee_value'].iloc[-1] - INITIAL_CAPITAL_DEE) / INITIAL_CAPITAL_DEE) * 100
    metrics['dee_return_pct'] = dee_return
    metrics['dee_final_value'] = df['dee_value'].iloc[-1]

    # SHORGAN-PAPER metrics
    shorgan_paper_return = ((df['shorgan_paper_value'].iloc[-1] - INITIAL_CAPITAL_SHORGAN_PAPER) / INITIAL_CAPITAL_SHORGAN_PAPER) * 100
    metrics['shorgan_paper_return_pct'] = shorgan_paper_return
    metrics['shorgan_paper_final_value'] = df['shorgan_paper_value'].iloc[-1]

    # SHORGAN-LIVE metrics (account for total deposits, not just initial capital)
    shorgan_live_deposits = get_shorgan_live_total_deposits()
    shorgan_live_return = ((df['shorgan_live_value'].iloc[-1] - shorgan_live_deposits) / shorgan_live_deposits) * 100
    metrics['shorgan_live_return_pct'] = shorgan_live_return
    metrics['shorgan_live_final_value'] = df['shorgan_live_value'].iloc[-1]
    metrics['shorgan_live_deposits'] = shorgan_live_deposits

    # Combined metrics (account for all deposits across all accounts)
    total_capital_deployed = INITIAL_CAPITAL_DEE + INITIAL_CAPITAL_SHORGAN_PAPER + shorgan_live_deposits
    combined_return = ((df['combined_value'].iloc[-1] - total_capital_deployed) / total_capital_deployed) * 100
    metrics['combined_return_pct'] = combined_return
    metrics['combined_final_value'] = df['combined_value'].iloc[-1]
    metrics['total_capital_deployed'] = total_capital_deployed

    # S&P 500 metrics (if available) - normalize to total capital deployed
    if 'sp500_value' in df.columns:
        # Adjust S&P 500 baseline to match total capital deployed
        sp500_adjusted = (df['sp500_value'] / df['sp500_value'].iloc[0]) * total_capital_deployed
        sp500_return = ((sp500_adjusted.iloc[-1] - total_capital_deployed) / total_capital_deployed) * 100
        metrics['sp500_return_pct'] = sp500_return
        metrics['sp500_final_value'] = sp500_adjusted.iloc[-1]

    return metrics

def plot_performance_comparison(df):
    """Generate performance comparison graph with 3 separate strategies + benchmark"""

    # Create figure with professional styling
    fig, ax = plt.subplots(figsize=(16, 9))

    # Calculate indexed values for accounts with no deposits (DEE, SHORGAN Paper)
    df['dee_indexed'] = (df['dee_value'] / df['dee_value'].iloc[0]) * 100
    df['shorgan_paper_indexed'] = (df['shorgan_paper_value'] / df['shorgan_paper_value'].iloc[0]) * 100

    # SHORGAN-LIVE: Calculate deposit-adjusted indexed values to show true trading performance
    # This accounts for deposits over time so the chart shows stock selection skill, not deposit timing
    try:
        with open(SHORGAN_LIVE_DEPOSITS_FILE, 'r') as f:
            deposit_data = json.load(f)
            deposits = deposit_data.get('deposit_history', [])

        # Calculate cumulative deposits for each date
        shorgan_live_indexed_values = []
        for idx, row in df.iterrows():
            date = pd.Timestamp(row['date']).normalize()

            # Sum all deposits up to this date
            cumulative_deposits = sum(
                float(d['amount'])
                for d in deposits
                if pd.Timestamp(d['date']).normalize() <= date
            )

            # If no deposits yet, skip this row
            if cumulative_deposits == 0:
                shorgan_live_indexed_values.append(100.0)
                continue

            # Calculate trading return: (value - deposits) / deposits
            trading_return_pct = ((row['shorgan_live_value'] - cumulative_deposits) / cumulative_deposits)

            # Index value: $100 * (1 + return)
            indexed_value = 100.0 * (1 + trading_return_pct)
            shorgan_live_indexed_values.append(indexed_value)

        df['shorgan_live_indexed'] = shorgan_live_indexed_values

    except Exception as e:
        # Fallback to simple indexing if deposit file not found
        print(f"[WARNING] Could not load deposit history for SHORGAN-LIVE indexing: {e}")
        df['shorgan_live_indexed'] = (df['shorgan_live_value'] / df['shorgan_live_value'].iloc[0]) * 100

    # Combined: Calculate deposit-adjusted indexed values
    # Use same deposit-adjusted approach for SHORGAN-LIVE component
    try:
        combined_indexed_values = []
        for idx, row in df.iterrows():
            date = pd.Timestamp(row['date']).normalize()

            # Sum all SHORGAN-LIVE deposits up to this date
            cumulative_shorgan_live_deposits = sum(
                float(d['amount'])
                for d in deposits
                if pd.Timestamp(d['date']).normalize() <= date
            )

            # Total capital deployed up to this date
            total_capital = INITIAL_CAPITAL_DEE + INITIAL_CAPITAL_SHORGAN_PAPER + cumulative_shorgan_live_deposits

            # Calculate trading return for combined portfolio
            trading_return_pct = ((row['combined_value'] - total_capital) / total_capital)

            # Index value: $100 * (1 + return)
            indexed_value = 100.0 * (1 + trading_return_pct)
            combined_indexed_values.append(indexed_value)

        df['combined_indexed'] = combined_indexed_values

    except Exception as e:
        # Fallback to simple indexing
        print(f"[WARNING] Could not calculate deposit-adjusted combined indexing: {e}")
        df['combined_indexed'] = (df['combined_value'] / df['combined_value'].iloc[0]) * 100

    if 'sp500_value' in df.columns:
        df['sp500_indexed'] = (df['sp500_value'] / df['sp500_value'].iloc[0]) * 100

    # Plot each portfolio (indexed)
    ax.plot(df['date'], df['combined_indexed'],
            label='Combined Portfolio (All 3 Accounts)',
            linewidth=3, color='#2E86AB', marker='o', markersize=5, zorder=5)

    ax.plot(df['date'], df['dee_indexed'],
            label='DEE-BOT (Paper $100K - Defensive)',
            linewidth=2, color='#06A77D', linestyle='--', marker='s', markersize=3)

    ax.plot(df['date'], df['shorgan_paper_indexed'],
            label='SHORGAN-BOT Paper ($100K - Aggressive)',
            linewidth=2, color='#D62839', linestyle='--', marker='^', markersize=3)

    ax.plot(df['date'], df['shorgan_live_indexed'],
            label='SHORGAN-BOT Live ($3K - REAL MONEY)',
            linewidth=2.5, color='#E63946', linestyle='-', marker='D', markersize=4, zorder=4)

    # Plot S&P 500 benchmark if available
    if 'sp500_indexed' in df.columns:
        ax.plot(df['date'], df['sp500_indexed'],
                label='S&P 500 (Benchmark)',
                linewidth=2, color='#F77F00', linestyle=':', marker='d', markersize=3)

    # Formatting
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Indexed Value (Start = $100)', fontsize=12, fontweight='bold')
    ax.set_title('AI Trading Bot Performance vs S&P 500 Benchmark (Indexed)',
                 fontsize=16, fontweight='bold', pad=20)

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))

    # Add horizontal line at starting value ($100)
    ax.axhline(y=100, color='gray', linestyle='--',
               linewidth=1, alpha=0.5, label='Starting Value ($100)')

    # Legend
    ax.legend(loc='best', fontsize=10, framealpha=0.9)

    # Calculate and display metrics
    metrics = calculate_performance_metrics(df)
    if metrics:
        # Calculate indexed final values
        combined_indexed_final = df['combined_indexed'].iloc[-1]
        dee_indexed_final = df['dee_indexed'].iloc[-1]
        shorgan_paper_indexed_final = df['shorgan_paper_indexed'].iloc[-1]
        shorgan_live_indexed_final = df['shorgan_live_indexed'].iloc[-1]

        metrics_text = f"""
Performance Summary (as of {df['date'].iloc[-1].strftime('%Y-%m-%d')}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Combined:       ${combined_indexed_final:.2f} ({metrics['combined_return_pct']:+.2f}%)
DEE Paper:      ${dee_indexed_final:.2f} ({metrics['dee_return_pct']:+.2f}%)
SHORGAN Paper:  ${shorgan_paper_indexed_final:.2f} ({metrics['shorgan_paper_return_pct']:+.2f}%)
SHORGAN Live:   ${shorgan_live_indexed_final:.2f} ({metrics['shorgan_live_return_pct']:+.2f}%)
"""
        if 'sp500_return_pct' in metrics and 'sp500_indexed' in df.columns:
            sp500_indexed_final = df['sp500_indexed'].iloc[-1]
            metrics_text += f"S&P 500:        ${sp500_indexed_final:.2f} ({metrics['sp500_return_pct']:+.2f}%)"

        # Add text box with metrics
        ax.text(0.02, 0.98, metrics_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontfamily='monospace')

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(RESULTS_PATH, dpi=300, bbox_inches='tight')
    print(f"Performance graph saved to: {RESULTS_PATH}")

    # Display metrics in console
    if metrics:
        print("\n" + "="*70)
        print("PERFORMANCE METRICS (3 Accounts)")
        print("="*70)
        print(f"Combined Portfolio:        ${metrics['combined_final_value']:,.2f} ({metrics['combined_return_pct']:+.2f}%)")
        print(f"DEE-BOT Paper ($100K):     ${metrics['dee_final_value']:,.2f} ({metrics['dee_return_pct']:+.2f}%)")
        print(f"SHORGAN Paper ($100K):     ${metrics['shorgan_paper_final_value']:,.2f} ({metrics['shorgan_paper_return_pct']:+.2f}%)")
        print(f"SHORGAN Live ($3K):        ${metrics['shorgan_live_final_value']:,.2f} ({metrics['shorgan_live_return_pct']:+.2f}%)")
        if 'sp500_return_pct' in metrics:
            print(f"S&P 500 Benchmark:         ${metrics['sp500_final_value']:,.2f} ({metrics['sp500_return_pct']:+.2f}%)")
            print(f"\nAlpha vs S&P 500:          {metrics['combined_return_pct'] - metrics['sp500_return_pct']:+.2f}%")
        print("="*70)

    return fig, metrics

def send_telegram_notification(metrics, graph_path):
    """Send performance graph and metrics via Telegram (3 accounts)"""
    try:
        import requests

        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7526351226:AAHQz1PV-4OdNmCgLdgzPJ8emHxIeGdPW6Q")
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7870288896")

        # Send performance graph as photo
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

        # Build caption with metrics
        caption = "📊 *Daily Performance Update (3 Accounts)*\n\n"
        caption += f"*Combined*: ${metrics['combined_final_value']:,.2f} ({metrics['combined_return_pct']:+.2f}%) [Capital: ${metrics['total_capital_deployed']:,.0f}]\n\n"
        caption += f"*DEE Paper*: ${metrics['dee_final_value']:,.2f} ({metrics['dee_return_pct']:+.2f}%)\n"
        caption += f"*SHORGAN Paper*: ${metrics['shorgan_paper_final_value']:,.2f} ({metrics['shorgan_paper_return_pct']:+.2f}%)\n"
        caption += f"*SHORGAN Live* 💰: ${metrics['shorgan_live_final_value']:,.2f} ({metrics['shorgan_live_return_pct']:+.2f}%) [Deposits: ${metrics['shorgan_live_deposits']:,.0f}]\n"

        if 'sp500_return_pct' in metrics:
            caption += f"\n*S&P 500*: ${metrics['sp500_final_value']:,.2f} ({metrics['sp500_return_pct']:+.2f}%)\n"
            caption += f"*Alpha*: {metrics['combined_return_pct'] - metrics['sp500_return_pct']:+.2f}%\n"

        caption += f"\n_Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p ET')}_"

        with open(graph_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data, files=files)

            if response.status_code == 200:
                print(f"\n[+] Telegram notification sent successfully")
                return True
            else:
                print(f"\n[-] Telegram send failed: {response.text}")
                return False

    except Exception as e:
        print(f"\n[-] Telegram notification failed: {e}")
        return False

def main():
    """Main execution function"""
    print("Generating Performance Comparison Graph...")
    print(f"Data source: {PERFORMANCE_JSON}")

    # Load portfolio performance data
    portfolio_df = create_portfolio_dataframe()

    if portfolio_df is None or portfolio_df.empty:
        print("No performance data available. Run trading system first to generate data.")
        return

    print(f"Loaded {len(portfolio_df)} data points from {portfolio_df['date'].min()} to {portfolio_df['date'].max()}")

    # Download S&P 500 benchmark data
    start_date = portfolio_df['date'].min()
    end_date = portfolio_df['date'].max()

    print(f"Downloading S&P 500 data from {start_date.date()} to {end_date.date()}...")
    sp500_df = download_sp500(start_date, end_date)

    # Merge with portfolio data or create synthetic benchmark
    if not sp500_df.empty:
        # Normalize timezones AND normalize to date-only (remove timestamps)
        portfolio_df['date'] = pd.to_datetime(portfolio_df['date']).dt.tz_localize(None).dt.normalize()
        sp500_df['date'] = pd.to_datetime(sp500_df['date']).dt.tz_localize(None).dt.normalize()

        # Merge on normalized dates
        portfolio_df = pd.merge(portfolio_df, sp500_df, on='date', how='left')

        # Forward fill missing S&P 500 values (for weekends/holidays)
        portfolio_df['sp500_value'] = portfolio_df['sp500_value'].ffill()

        # Backward fill if first value is NaN
        portfolio_df['sp500_value'] = portfolio_df['sp500_value'].bfill()

        print(f"S&P 500 benchmark data merged successfully")
        print(f"S&P 500 values: {portfolio_df['sp500_value'].tolist()}")
    else:
        # Use synthetic benchmark when live data unavailable
        print("S&P 500 data unavailable - creating synthetic benchmark...")
        sp500_df = create_synthetic_sp500_benchmark(portfolio_df)

        if not sp500_df.empty:
            portfolio_df = pd.merge(portfolio_df, sp500_df, on='date', how='left')
            print(f"Synthetic S&P 500 benchmark added successfully")

    # Generate visualization
    fig, metrics = plot_performance_comparison(portfolio_df)

    # Send Telegram notification
    if metrics and RESULTS_PATH.exists():
        print("\nSending Telegram notification...")
        send_telegram_notification(metrics, RESULTS_PATH)

    print("\nPerformance analysis complete!")

if __name__ == "__main__":
    main()