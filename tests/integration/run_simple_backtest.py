#!/usr/bin/env python3
"""
Simple backtest using Financial Datasets API
Test basic functionality with a few stocks
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts-and-data', 'automation'))

from financial_datasets_integration import FinancialDatasetsAPI
from datetime import datetime, timedelta
import pandas as pd

def simple_momentum_strategy(data_dict, positions, capital, **params):
    """Simple momentum strategy for backtesting"""
    signals = []

    position_size = params.get('position_size', 0.1)
    rsi_oversold = params.get('rsi_oversold', 30)
    rsi_overbought = params.get('rsi_overbought', 70)

    for symbol, df in data_dict.items():
        if len(df) < 20:  # Need enough data for indicators
            continue

        latest = df.iloc[-1]

        # Calculate simple RSI
        if len(df) >= 14:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]

            # Buy signal: RSI oversold and price above 20-day MA
            if current_rsi < rsi_oversold and len(df) >= 20:
                sma_20 = df['close'].rolling(20).mean().iloc[-1]
                if latest['close'] > sma_20 and symbol not in positions:
                    shares = int((capital * position_size) / latest['close'])
                    if shares > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'buy',
                            'shares': shares
                        })

            # Sell signal: RSI overbought or take profit
            elif symbol in positions and (current_rsi > rsi_overbought):
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': positions[symbol]['shares']
                })

    return signals

def run_simple_backtest():
    """Run a simple backtest with Financial Datasets API"""

    print("=" * 60)
    print("SIMPLE BACKTEST WITH FINANCIAL DATASETS API")
    print("=" * 60)

    # Initialize API
    fd_api = FinancialDatasetsAPI()

    # Simple test with 3 stocks
    tickers = ['AAPL', 'MSFT', 'GOOGL']

    # 6-month backtest
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

    print(f"Testing tickers: {tickers}")
    print(f"Period: {start_date} to {end_date}")
    print()

    # Fetch data for all tickers
    all_data = {}

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        df = fd_api.get_historical_prices(ticker, interval='day',
                                         start_date=start_date,
                                         end_date=end_date,
                                         limit=200)
        if not df.empty:
            all_data[ticker] = df
            print(f"  Retrieved {len(df)} days of data")
        else:
            print(f"  No data retrieved for {ticker}")

    if not all_data:
        print("No data retrieved. Exiting.")
        return

    print(f"\nSuccessfully retrieved data for {len(all_data)} tickers")

    # Run simple backtest simulation
    initial_capital = 100000
    capital = initial_capital
    positions = {}
    trades = []

    # Get all unique dates
    all_dates = set()
    for ticker_data in all_data.values():
        all_dates.update(ticker_data.index)
    all_dates = sorted(list(all_dates))

    print(f"Backtesting over {len(all_dates)} trading days...")

    # Simple backtest loop
    for i, date in enumerate(all_dates):
        if i % 30 == 0:  # Progress update every 30 days
            print(f"  Processing day {i+1}/{len(all_dates)}: {date.strftime('%Y-%m-%d')}")

        # Get current prices and data up to this date
        current_prices = {}
        current_data = {}

        for ticker in tickers:
            if ticker in all_data and date in all_data[ticker].index:
                current_prices[ticker] = all_data[ticker].loc[date, 'close']
                # Get historical data up to current date
                current_data[ticker] = all_data[ticker].loc[:date]

        # Execute strategy
        if current_data:
            signals = simple_momentum_strategy(
                current_data,
                positions,
                capital,
                position_size=0.2,
                rsi_oversold=35,
                rsi_overbought=65
            )

            # Process signals
            for signal in signals:
                ticker = signal['symbol']
                action = signal['action']
                shares = signal['shares']

                if ticker in current_prices:
                    price = current_prices[ticker]

                    if action == 'buy' and shares * price <= capital:
                        cost = shares * price
                        capital -= cost
                        positions[ticker] = {'shares': shares, 'avg_price': price}
                        trades.append({
                            'date': date,
                            'ticker': ticker,
                            'action': action,
                            'shares': shares,
                            'price': price,
                            'value': cost
                        })
                        print(f"    BUY: {shares} shares of {ticker} at ${price:.2f}")

                    elif action == 'sell' and ticker in positions:
                        proceeds = shares * price
                        capital += proceeds
                        cost = positions[ticker]['shares'] * positions[ticker]['avg_price']
                        profit = proceeds - cost
                        del positions[ticker]
                        trades.append({
                            'date': date,
                            'ticker': ticker,
                            'action': action,
                            'shares': shares,
                            'price': price,
                            'value': proceeds,
                            'profit': profit
                        })
                        print(f"    SELL: {shares} shares of {ticker} at ${price:.2f} (P&L: ${profit:.2f})")

    # Calculate final portfolio value
    final_portfolio_value = capital
    for ticker, position in positions.items():
        if ticker in all_data and len(all_data[ticker]) > 0:
            final_price = all_data[ticker]['close'].iloc[-1]
            final_portfolio_value += position['shares'] * final_price

    # Results
    total_return = (final_portfolio_value - initial_capital) / initial_capital

    print("\n" + "=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"Total Return: {total_return*100:.2f}%")
    print(f"Cash Remaining: ${capital:,.2f}")
    print(f"Positions Value: ${final_portfolio_value - capital:,.2f}")
    print(f"Total Trades: {len(trades)}")

    if trades:
        profits = [t.get('profit', 0) for t in trades if t.get('profit')]
        if profits:
            winning_trades = sum(1 for p in profits if p > 0)
            losing_trades = sum(1 for p in profits if p <= 0)
            win_rate = winning_trades / len(profits) if profits else 0
            avg_profit = sum(profits) / len(profits) if profits else 0

            print(f"Winning Trades: {winning_trades}")
            print(f"Losing Trades: {losing_trades}")
            print(f"Win Rate: {win_rate*100:.1f}%")
            print(f"Average Profit per Trade: ${avg_profit:.2f}")

    print(f"\nRemaining Positions:")
    for ticker, position in positions.items():
        if ticker in all_data:
            current_price = all_data[ticker]['close'].iloc[-1]
            market_value = position['shares'] * current_price
            unrealized_pnl = market_value - (position['shares'] * position['avg_price'])
            print(f"  {ticker}: {position['shares']} shares @ ${position['avg_price']:.2f} "
                  f"(Current: ${current_price:.2f}, Value: ${market_value:.2f}, "
                  f"P&L: ${unrealized_pnl:.2f})")

if __name__ == "__main__":
    run_simple_backtest()