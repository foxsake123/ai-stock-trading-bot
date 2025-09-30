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

# Configuration
DATA_DIR = "scripts-and-data"
PERFORMANCE_JSON = f"{DATA_DIR}/data/json/performance_history.json"
RESULTS_PATH = Path("performance_results.png")

# Alpaca API Configuration
DEE_BOT_API_KEY = 'PK6FZK4DAQVTD7DYVH78'
DEE_BOT_SECRET = 'JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt'
SHORGAN_API_KEY = 'PKJRLSB2MFEJUSK6UK2E'
SHORGAN_SECRET = 'QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic'
BASE_URL = 'https://paper-api.alpaca.markets'

# Starting capital
INITIAL_CAPITAL_DEE = 100000.0
INITIAL_CAPITAL_SHORGAN = 100000.0
INITIAL_CAPITAL_COMBINED = 200000.0

def get_current_portfolio_values():
    """Fetch current portfolio values from Alpaca"""
    try:
        dee_api = tradeapi.REST(DEE_BOT_API_KEY, DEE_BOT_SECRET, BASE_URL, api_version='v2')
        shorgan_api = tradeapi.REST(SHORGAN_API_KEY, SHORGAN_SECRET, BASE_URL, api_version='v2')

        dee_account = dee_api.get_account()
        shorgan_account = shorgan_api.get_account()

        dee_value = float(dee_account.portfolio_value)
        shorgan_value = float(shorgan_account.portfolio_value)

        return {
            'dee_bot': dee_value,
            'shorgan_bot': shorgan_value,
            'combined': dee_value + shorgan_value
        }
    except Exception as e:
        print(f"Error fetching portfolio values: {e}")
        return None

def load_performance_history():
    """Load historical performance data from JSON file"""
    try:
        with open(PERFORMANCE_JSON, 'r') as f:
            data = json.load(f)

        records = []
        for record in data.get('daily_records', []):
            records.append({
                'date': pd.to_datetime(record['date']),
                'dee_value': record['dee_bot']['value'],
                'shorgan_value': record['shorgan_bot']['value'],
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
    """Create or load portfolio performance dataframe with baseline"""
    df = load_performance_history()

    # Add baseline data point (starting capital)
    if df is not None and not df.empty:
        start_date = df['date'].min()
    else:
        start_date = pd.Timestamp("2025-09-10")
        df = pd.DataFrame()

    # Create baseline row (one day before first data point)
    baseline_date = start_date - pd.Timedelta(days=1)
    baseline_row = pd.DataFrame({
        'date': [baseline_date],
        'dee_value': [INITIAL_CAPITAL_DEE],
        'shorgan_value': [INITIAL_CAPITAL_SHORGAN],
        'combined_value': [INITIAL_CAPITAL_COMBINED]
    })

    # Get current values
    current_values = get_current_portfolio_values()
    if current_values:
        today_row = pd.DataFrame({
            'date': [pd.Timestamp.now()],
            'dee_value': [current_values['dee_bot']],
            'shorgan_value': [current_values['shorgan_bot']],
            'combined_value': [current_values['combined']]
        })
        df = pd.concat([df, today_row], ignore_index=True)

    # Combine baseline with historical data
    df = pd.concat([baseline_row, df], ignore_index=True)
    df = df.drop_duplicates(subset=['date'], keep='last').sort_values('date').reset_index(drop=True)

    return df

def download_sp500(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """Download S&P 500 prices and normalize to starting capital baseline"""

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

    # Method 2: Try Alpaca API (limited for paper accounts)
    try:
        print("Attempting to fetch SPY data from Alpaca API...")
        alpaca_api = tradeapi.REST(
            SHORGAN_API_KEY,
            SHORGAN_SECRET,
            BASE_URL,
            api_version='v2'
        )

        # Fetch SPY bars from Alpaca
        bars = alpaca_api.get_bars(
            'SPY',
            tradeapi.TimeFrame.Day,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            adjustment='all'
        ).df

        if not bars.empty:
            print(f"Successfully downloaded SPY data from Alpaca API ({len(bars)} bars)")

            # Convert to expected format
            sp500 = pd.DataFrame({
                'date': bars.index,
                'Close': bars['close']
            })

            # Normalize to match starting capital
            sp500_baseline = sp500['Close'].iloc[0]
            sp500['sp500_value'] = (sp500['Close'] / sp500_baseline) * INITIAL_CAPITAL_COMBINED

            return sp500[['date', 'sp500_value']].reset_index(drop=True)

    except Exception as e:
        print(f"Alpaca API failed: {e}")

    # Method 2: Fallback to yfinance (currently broken but keep for future)
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

def calculate_performance_metrics(df):
    """Calculate key performance metrics"""
    if df.empty:
        return None

    metrics = {}

    # DEE-BOT metrics
    dee_return = ((df['dee_value'].iloc[-1] - INITIAL_CAPITAL_DEE) / INITIAL_CAPITAL_DEE) * 100
    metrics['dee_return_pct'] = dee_return
    metrics['dee_final_value'] = df['dee_value'].iloc[-1]

    # SHORGAN-BOT metrics
    shorgan_return = ((df['shorgan_value'].iloc[-1] - INITIAL_CAPITAL_SHORGAN) / INITIAL_CAPITAL_SHORGAN) * 100
    metrics['shorgan_return_pct'] = shorgan_return
    metrics['shorgan_final_value'] = df['shorgan_value'].iloc[-1]

    # Combined metrics
    combined_return = ((df['combined_value'].iloc[-1] - INITIAL_CAPITAL_COMBINED) / INITIAL_CAPITAL_COMBINED) * 100
    metrics['combined_return_pct'] = combined_return
    metrics['combined_final_value'] = df['combined_value'].iloc[-1]

    # S&P 500 metrics (if available)
    if 'sp500_value' in df.columns:
        sp500_return = ((df['sp500_value'].iloc[-1] - INITIAL_CAPITAL_COMBINED) / INITIAL_CAPITAL_COMBINED) * 100
        metrics['sp500_return_pct'] = sp500_return
        metrics['sp500_final_value'] = df['sp500_value'].iloc[-1]

    return metrics

def plot_performance_comparison(df):
    """Generate performance comparison graph matching reference style"""

    # Create figure with professional styling
    fig, ax = plt.subplots(figsize=(14, 8))

    # Calculate indexed values (starting at $100 for each)
    df['combined_indexed'] = (df['combined_value'] / df['combined_value'].iloc[0]) * 100
    df['dee_indexed'] = (df['dee_value'] / df['dee_value'].iloc[0]) * 100
    df['shorgan_indexed'] = (df['shorgan_value'] / df['shorgan_value'].iloc[0]) * 100

    if 'sp500_value' in df.columns:
        df['sp500_indexed'] = (df['sp500_value'] / df['sp500_value'].iloc[0]) * 100

    # Plot each portfolio (indexed)
    ax.plot(df['date'], df['combined_indexed'],
            label='Combined Portfolio (DEE + SHORGAN)',
            linewidth=2.5, color='#2E86AB', marker='o', markersize=4)

    ax.plot(df['date'], df['dee_indexed'],
            label='DEE-BOT (Defensive)',
            linewidth=2, color='#06A77D', linestyle='--', marker='s', markersize=3)

    ax.plot(df['date'], df['shorgan_indexed'],
            label='SHORGAN-BOT (Aggressive)',
            linewidth=2, color='#D62839', linestyle='--', marker='^', markersize=3)

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
        shorgan_indexed_final = df['shorgan_indexed'].iloc[-1]

        metrics_text = f"""
Performance Summary (as of {df['date'].iloc[-1].strftime('%Y-%m-%d')}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Combined:    ${combined_indexed_final:.2f} ({metrics['combined_return_pct']:+.2f}%)
DEE-BOT:     ${dee_indexed_final:.2f} ({metrics['dee_return_pct']:+.2f}%)
SHORGAN:     ${shorgan_indexed_final:.2f} ({metrics['shorgan_return_pct']:+.2f}%)
"""
        if 'sp500_return_pct' in metrics and 'sp500_indexed' in df.columns:
            sp500_indexed_final = df['sp500_indexed'].iloc[-1]
            metrics_text += f"S&P 500:     ${sp500_indexed_final:.2f} ({metrics['sp500_return_pct']:+.2f}%)"

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
        print("\n" + "="*60)
        print("PERFORMANCE METRICS")
        print("="*60)
        print(f"Combined Portfolio:  ${metrics['combined_final_value']:,.2f} ({metrics['combined_return_pct']:+.2f}%)")
        print(f"DEE-BOT (Defensive): ${metrics['dee_final_value']:,.2f} ({metrics['dee_return_pct']:+.2f}%)")
        print(f"SHORGAN-BOT (Aggr.): ${metrics['shorgan_final_value']:,.2f} ({metrics['shorgan_return_pct']:+.2f}%)")
        if 'sp500_return_pct' in metrics:
            print(f"S&P 500 Benchmark:   ${metrics['sp500_final_value']:,.2f} ({metrics['sp500_return_pct']:+.2f}%)")
            print(f"\nAlpha vs S&P 500:    {metrics['combined_return_pct'] - metrics['sp500_return_pct']:+.2f}%")
        print("="*60)

    return fig, metrics

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

    # Merge with portfolio data
    if not sp500_df.empty:
        portfolio_df = pd.merge(portfolio_df, sp500_df, on='date', how='left')
        portfolio_df['sp500_value'] = portfolio_df['sp500_value'].fillna(method='ffill')
        print(f"S&P 500 benchmark data merged successfully")
    else:
        print("S&P 500 data unavailable - generating graph without benchmark")

    # Generate visualization
    fig, metrics = plot_performance_comparison(portfolio_df)

    print("\nPerformance analysis complete!")

if __name__ == "__main__":
    main()