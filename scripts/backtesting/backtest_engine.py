#!/usr/bin/env python3
"""
Backtesting Engine using Financial Datasets API
Allows testing trading strategies on historical price data
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from dataclasses import dataclass, asdict

@dataclass
class Trade:
    symbol: str
    date: datetime
    action: str  # 'buy' or 'sell'
    shares: int
    price: float
    value: float

@dataclass
class BacktestResults:
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    trades: List[Trade]
    equity_curve: pd.DataFrame

class FinancialDatasetsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.financialdatasets.ai"
        self.headers = {"X-API-KEY": api_key}

    def get_historical_prices(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "day",
        interval_multiplier: int = 1
    ) -> pd.DataFrame:
        """Fetch historical price data from Financial Datasets API"""
        url = f"{self.base_url}/prices"
        params = {
            "ticker": ticker,
            "interval": interval,
            "interval_multiplier": interval_multiplier,
            "start_date": start_date,
            "end_date": end_date,
            "limit": 5000
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")

            data = response.json()
            # The API returns a dict with 'prices' key containing the array
            if isinstance(data, dict) and 'prices' in data:
                prices = data['prices']
                if prices and isinstance(prices, list):
                    df = pd.DataFrame(prices)
                    if 'time' in df.columns:
                        df['time'] = pd.to_datetime(df['time'])
                        df.set_index('time', inplace=True)
                        return df[['open', 'high', 'low', 'close', 'volume']]

            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

class BacktestEngine:
    def __init__(self, api_key: str, initial_capital: float = 100000):
        self.client = FinancialDatasetsClient(api_key)
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_history = []

    def fetch_data(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        interval: str = "day"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch historical data for multiple tickers"""
        data = {}
        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            data[ticker] = self.client.get_historical_prices(
                ticker, start_date, end_date, interval
            )
        return data

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate common technical indicators"""
        df = df.copy()

        # Simple Moving Averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()

        # Exponential Moving Averages
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

        # Volume indicators
        df['Volume_SMA'] = df['volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['volume'] / df['Volume_SMA']

        return df

    def execute_trade(
        self,
        symbol: str,
        action: str,
        shares: int,
        price: float,
        date: datetime
    ):
        """Execute a trade in the backtest"""
        if action == 'buy':
            cost = shares * price
            if cost > self.capital:
                # Adjust shares if not enough capital
                shares = int(self.capital / price)
                cost = shares * price

            if shares > 0:
                self.capital -= cost
                if symbol not in self.positions:
                    self.positions[symbol] = {'shares': 0, 'avg_price': 0}

                # Update position with weighted average
                total_shares = self.positions[symbol]['shares'] + shares
                if total_shares > 0:
                    avg_price = ((self.positions[symbol]['shares'] * self.positions[symbol]['avg_price']) +
                                (shares * price)) / total_shares
                    self.positions[symbol] = {'shares': total_shares, 'avg_price': avg_price}

                trade = Trade(symbol, date, action, shares, price, cost)
                self.trades.append(trade)

        elif action == 'sell':
            if symbol in self.positions and self.positions[symbol]['shares'] >= shares:
                proceeds = shares * price
                self.capital += proceeds
                self.positions[symbol]['shares'] -= shares

                if self.positions[symbol]['shares'] == 0:
                    del self.positions[symbol]

                trade = Trade(symbol, date, action, shares, price, proceeds)
                self.trades.append(trade)

    def calculate_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Calculate current portfolio value"""
        value = self.capital
        for symbol, position in self.positions.items():
            if symbol in prices:
                value += position['shares'] * prices[symbol]
        return value

    def run_backtest(
        self,
        strategy_func,
        tickers: List[str],
        start_date: str,
        end_date: str,
        **strategy_params
    ) -> BacktestResults:
        """Run backtest with given strategy"""
        # Reset state
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_history = []

        # Fetch and prepare data
        data = self.fetch_data(tickers, start_date, end_date)

        # Add indicators to all dataframes
        for ticker in data:
            data[ticker] = self.calculate_indicators(data[ticker])

        # Get all unique dates
        all_dates = set()
        for ticker_data in data.values():
            all_dates.update(ticker_data.index)
        all_dates = sorted(list(all_dates))

        # Run strategy for each date
        for date in all_dates:
            # Get current prices
            current_prices = {}
            current_data = {}

            for ticker in tickers:
                if date in data[ticker].index:
                    current_prices[ticker] = data[ticker].loc[date, 'close']
                    # Get historical data up to current date
                    current_data[ticker] = data[ticker].loc[:date]

            # Execute strategy
            if current_data:
                signals = strategy_func(
                    current_data,
                    self.positions,
                    self.capital,
                    **strategy_params
                )

                # Execute trades based on signals
                for signal in signals:
                    if signal['symbol'] in current_prices:
                        self.execute_trade(
                            signal['symbol'],
                            signal['action'],
                            signal['shares'],
                            current_prices[signal['symbol']],
                            date
                        )

            # Record equity
            portfolio_value = self.calculate_portfolio_value(current_prices)
            self.equity_history.append({
                'date': date,
                'value': portfolio_value,
                'capital': self.capital,
                'positions_value': portfolio_value - self.capital
            })

        # Calculate metrics
        results = self.calculate_metrics()
        return results

    def calculate_metrics(self) -> BacktestResults:
        """Calculate backtest performance metrics"""
        equity_df = pd.DataFrame(self.equity_history)
        equity_df.set_index('date', inplace=True)

        # Calculate returns
        equity_df['returns'] = equity_df['value'].pct_change()

        # Total return
        total_return = (equity_df['value'].iloc[-1] - self.initial_capital) / self.initial_capital

        # Sharpe ratio (assuming 252 trading days and 2% risk-free rate)
        if len(equity_df['returns']) > 1:
            sharpe_ratio = (equity_df['returns'].mean() * 252 - 0.02) / (equity_df['returns'].std() * np.sqrt(252))
        else:
            sharpe_ratio = 0

        # Max drawdown
        equity_df['cummax'] = equity_df['value'].cummax()
        equity_df['drawdown'] = (equity_df['value'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()

        # Win rate and trade statistics
        trade_returns = []
        for i, trade in enumerate(self.trades):
            if trade.action == 'sell':
                # Find corresponding buy
                buy_price = None
                for j in range(i-1, -1, -1):
                    if self.trades[j].symbol == trade.symbol and self.trades[j].action == 'buy':
                        buy_price = self.trades[j].price
                        break

                if buy_price:
                    trade_return = (trade.price - buy_price) / buy_price
                    trade_returns.append(trade_return)

        if trade_returns:
            winning_trades = sum(1 for r in trade_returns if r > 0)
            losing_trades = sum(1 for r in trade_returns if r <= 0)
            win_rate = winning_trades / len(trade_returns) if trade_returns else 0

            wins = [r for r in trade_returns if r > 0]
            losses = [abs(r) for r in trade_returns if r < 0]

            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            profit_factor = (sum(wins) / sum(losses)) if losses and sum(losses) > 0 else float('inf') if wins else 0
        else:
            winning_trades = losing_trades = 0
            win_rate = avg_win = avg_loss = profit_factor = 0

        return BacktestResults(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(self.trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            trades=self.trades,
            equity_curve=equity_df
        )

    def plot_results(self, results: BacktestResults, save_path: Optional[str] = None):
        """Plot backtest results"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        # Equity curve
        axes[0].plot(results.equity_curve.index, results.equity_curve['value'], label='Portfolio Value')
        axes[0].axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        axes[0].set_title('Portfolio Equity Curve')
        axes[0].set_ylabel('Value ($)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Drawdown
        axes[1].fill_between(
            results.equity_curve.index,
            results.equity_curve['drawdown'] * 100,
            0,
            color='red',
            alpha=0.3
        )
        axes[1].set_title('Drawdown')
        axes[1].set_ylabel('Drawdown (%)')
        axes[1].grid(True, alpha=0.3)

        # Returns distribution
        returns = results.equity_curve['returns'].dropna()
        axes[2].hist(returns * 100, bins=50, edgecolor='black', alpha=0.7)
        axes[2].set_title('Returns Distribution')
        axes[2].set_xlabel('Daily Returns (%)')
        axes[2].set_ylabel('Frequency')
        axes[2].axvline(x=0, color='r', linestyle='--')
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

    def export_results(self, results: BacktestResults, filepath: str):
        """Export backtest results to JSON"""
        export_data = {
            'metrics': {
                'total_return': f"{results.total_return * 100:.2f}%",
                'sharpe_ratio': round(results.sharpe_ratio, 2),
                'max_drawdown': f"{results.max_drawdown * 100:.2f}%",
                'win_rate': f"{results.win_rate * 100:.2f}%",
                'total_trades': results.total_trades,
                'winning_trades': results.winning_trades,
                'losing_trades': results.losing_trades,
                'avg_win': f"{results.avg_win * 100:.2f}%",
                'avg_loss': f"{results.avg_loss * 100:.2f}%",
                'profit_factor': round(results.profit_factor, 2)
            },
            'trades': [
                {
                    'symbol': t.symbol,
                    'date': t.date.isoformat(),
                    'action': t.action,
                    'shares': t.shares,
                    'price': t.price,
                    'value': t.value
                }
                for t in results.trades
            ],
            'equity_curve': results.equity_curve.reset_index().to_dict('records')
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"Results exported to {filepath}")