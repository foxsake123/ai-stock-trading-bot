#!/usr/bin/env python3
"""
Example script to run backtests using the Financial Datasets API
Shows how to test different strategies and compare results
"""

import os
import json
from datetime import datetime, timedelta
from backtest_engine import BacktestEngine
from strategies import (
    momentum_strategy,
    mean_reversion_strategy,
    macd_crossover_strategy,
    breakout_strategy,
    dee_bot_defensive_strategy,
    pairs_trading_strategy
)


def run_strategy_comparison():
    """Run multiple strategies and compare results"""

    # Configuration
    API_KEY = os.environ.get('FINANCIAL_DATASETS_API_KEY', 'your_api_key_here')
    INITIAL_CAPITAL = 100000

    # Test parameters
    END_DATE = datetime.now().strftime('%Y-%m-%d')
    START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year backtest

    # Test tickers - defensive stocks similar to DEE-BOT preferences
    TICKERS = ['JNJ', 'PG', 'KO', 'PEP', 'WMT', 'COST', 'CVS', 'UNH', 'XLU', 'VZ']

    # Initialize backtest engine
    engine = BacktestEngine(API_KEY, INITIAL_CAPITAL)

    # Define strategies to test
    strategies = [
        {
            'name': 'Momentum Strategy',
            'func': momentum_strategy,
            'params': {
                'lookback': 20,
                'position_size': 0.1,
                'rsi_oversold': 30,
                'rsi_overbought': 70
            }
        },
        {
            'name': 'Mean Reversion Strategy',
            'func': mean_reversion_strategy,
            'params': {
                'bb_periods': 20,
                'bb_std': 2,
                'position_size': 0.1,
                'stop_loss': 0.05
            }
        },
        {
            'name': 'MACD Crossover Strategy',
            'func': macd_crossover_strategy,
            'params': {
                'position_size': 0.15,
                'volume_filter': 1.5
            }
        },
        {
            'name': 'Breakout Strategy',
            'func': breakout_strategy,
            'params': {
                'lookback': 20,
                'volume_multiplier': 2.0,
                'position_size': 0.2,
                'stop_loss': 0.03
            }
        },
        {
            'name': 'DEE-BOT Defensive Strategy',
            'func': dee_bot_defensive_strategy,
            'params': {
                'beta_threshold': 0.7,
                'position_size': 0.05,
                'max_positions': 10,
                'rsi_oversold': 35,
                'stop_loss': 0.08
            }
        }
    ]

    # Run backtests
    results_summary = []

    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Running: {strategy['name']}")
        print(f"{'='*60}")

        try:
            # Run backtest
            results = engine.run_backtest(
                strategy['func'],
                TICKERS,
                START_DATE,
                END_DATE,
                **strategy['params']
            )

            # Display results
            print(f"\nResults for {strategy['name']}:")
            print(f"  Total Return: {results.total_return * 100:.2f}%")
            print(f"  Sharpe Ratio: {results.sharpe_ratio:.2f}")
            print(f"  Max Drawdown: {results.max_drawdown * 100:.2f}%")
            print(f"  Win Rate: {results.win_rate * 100:.2f}%")
            print(f"  Total Trades: {results.total_trades}")
            print(f"  Profit Factor: {results.profit_factor:.2f}")

            # Save detailed results
            output_dir = 'backtest_results'
            os.makedirs(output_dir, exist_ok=True)

            # Export results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{strategy['name'].replace(' ', '_')}_{timestamp}"

            # Save JSON report
            engine.export_results(
                results,
                os.path.join(output_dir, f"{filename}.json")
            )

            # Save plot
            engine.plot_results(
                results,
                os.path.join(output_dir, f"{filename}.png")
            )

            # Add to summary
            results_summary.append({
                'strategy': strategy['name'],
                'total_return': results.total_return,
                'sharpe_ratio': results.sharpe_ratio,
                'max_drawdown': results.max_drawdown,
                'win_rate': results.win_rate,
                'total_trades': results.total_trades,
                'profit_factor': results.profit_factor
            })

        except Exception as e:
            print(f"Error running {strategy['name']}: {e}")
            continue

    # Print comparison summary
    print(f"\n{'='*60}")
    print("STRATEGY COMPARISON SUMMARY")
    print(f"{'='*60}")

    # Sort by total return
    results_summary.sort(key=lambda x: x['total_return'], reverse=True)

    print("\nRanked by Total Return:")
    for i, result in enumerate(results_summary, 1):
        print(f"{i}. {result['strategy']}: {result['total_return']*100:.2f}%")

    # Sort by Sharpe ratio
    results_summary.sort(key=lambda x: x['sharpe_ratio'], reverse=True)

    print("\nRanked by Sharpe Ratio:")
    for i, result in enumerate(results_summary, 1):
        print(f"{i}. {result['strategy']}: {result['sharpe_ratio']:.2f}")

    # Save summary
    summary_path = os.path.join('backtest_results', f"comparison_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(summary_path, 'w') as f:
        json.dump(results_summary, f, indent=2)

    print(f"\nSummary saved to: {summary_path}")


def run_custom_backtest():
    """Example of running a custom backtest with specific parameters"""

    API_KEY = os.environ.get('FINANCIAL_DATASETS_API_KEY', 'your_api_key_here')

    # Custom parameters
    engine = BacktestEngine(API_KEY, initial_capital=50000)

    # Test on specific tickers with longer timeframe
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    start_date = '2022-01-01'
    end_date = '2024-01-01'

    print("Running custom backtest...")
    print(f"Tickers: {tickers}")
    print(f"Period: {start_date} to {end_date}")

    # Run DEE-BOT style defensive strategy
    results = engine.run_backtest(
        dee_bot_defensive_strategy,
        tickers,
        start_date,
        end_date,
        beta_threshold=0.7,
        position_size=0.1,
        max_positions=3,
        rsi_oversold=30,
        stop_loss=0.05
    )

    # Display results
    print("\nBacktest Results:")
    print(f"Total Return: {results.total_return * 100:.2f}%")
    print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {results.max_drawdown * 100:.2f}%")
    print(f"Win Rate: {results.win_rate * 100:.2f}%")
    print(f"Total Trades: {results.total_trades}")

    # Show sample trades
    print("\nFirst 5 trades:")
    for trade in results.trades[:5]:
        print(f"  {trade.date.strftime('%Y-%m-%d')}: {trade.action.upper()} {trade.shares} shares of {trade.symbol} at ${trade.price:.2f}")

    # Plot results
    engine.plot_results(results)


def backtest_with_real_dee_bot_picks():
    """Backtest using actual DEE-BOT stock selections"""

    API_KEY = os.environ.get('FINANCIAL_DATASETS_API_KEY', 'your_api_key_here')

    # Read DEE-BOT positions if available
    dee_bot_file = 'data/portfolio/dee_bot_positions.json'

    if os.path.exists(dee_bot_file):
        with open(dee_bot_file, 'r') as f:
            dee_bot_data = json.load(f)
            tickers = list(dee_bot_data.get('positions', {}).keys())
    else:
        # Default DEE-BOT style picks
        tickers = ['XLU', 'XLP', 'SPLV', 'DVY', 'SDY', 'VIG', 'NOBL', 'USMV']

    print(f"Backtesting DEE-BOT picks: {tickers}")

    engine = BacktestEngine(API_KEY, initial_capital=100000)

    # 6-month backtest
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

    results = engine.run_backtest(
        dee_bot_defensive_strategy,
        tickers,
        start_date,
        end_date,
        beta_threshold=0.7,
        position_size=0.1,
        max_positions=len(tickers),
        rsi_oversold=35,
        stop_loss=0.08
    )

    print(f"\nDEE-BOT Strategy Backtest ({start_date} to {end_date}):")
    print(f"Total Return: {results.total_return * 100:.2f}%")
    print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {results.max_drawdown * 100:.2f}%")
    print(f"Win Rate: {results.win_rate * 100:.2f}%")

    # Save results
    output_path = f"backtest_results/dee_bot_backtest_{datetime.now().strftime('%Y%m%d')}.json"
    engine.export_results(results, output_path)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'compare':
            run_strategy_comparison()
        elif sys.argv[1] == 'custom':
            run_custom_backtest()
        elif sys.argv[1] == 'dee-bot':
            backtest_with_real_dee_bot_picks()
        else:
            print("Usage: python run_backtest.py [compare|custom|dee-bot]")
    else:
        # Default: run strategy comparison
        print("Running strategy comparison (use 'custom' or 'dee-bot' for other modes)")
        run_strategy_comparison()