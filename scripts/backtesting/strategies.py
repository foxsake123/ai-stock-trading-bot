#!/usr/bin/env python3
"""
Trading Strategies for Backtesting
Implements various trading strategies compatible with the backtest engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any


def momentum_strategy(
    data: Dict[str, pd.DataFrame],
    positions: Dict[str, Dict],
    capital: float,
    lookback: int = 20,
    position_size: float = 0.1,
    rsi_oversold: float = 30,
    rsi_overbought: float = 70
) -> List[Dict]:
    """
    Momentum-based trading strategy
    Buys when price crosses above SMA and RSI is oversold
    Sells when price crosses below SMA or RSI is overbought
    """
    signals = []

    for symbol, df in data.items():
        if len(df) < lookback + 1:
            continue

        current = df.iloc[-1]
        previous = df.iloc[-2]

        # Check if we have required indicators
        if 'RSI' not in df.columns or 'SMA_20' not in df.columns:
            continue

        # Skip if NaN values
        if pd.isna(current['RSI']) or pd.isna(current['SMA_20']):
            continue

        # Current position
        current_position = positions.get(symbol, {}).get('shares', 0)

        # Buy signal
        if current_position == 0:
            # Price crosses above SMA and RSI indicates oversold
            if (current['close'] > current['SMA_20'] and
                previous['close'] <= previous['SMA_20'] and
                current['RSI'] < rsi_oversold):

                # Calculate shares to buy
                investment = capital * position_size
                shares = int(investment / current['close'])

                if shares > 0:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'shares': shares
                    })

        # Sell signal
        elif current_position > 0:
            # Price crosses below SMA or RSI indicates overbought
            if (current['close'] < current['SMA_20'] and
                previous['close'] >= previous['SMA_20']) or \
               current['RSI'] > rsi_overbought:

                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

    return signals


def mean_reversion_strategy(
    data: Dict[str, pd.DataFrame],
    positions: Dict[str, Dict],
    capital: float,
    bb_periods: int = 20,
    bb_std: float = 2,
    position_size: float = 0.1,
    stop_loss: float = 0.05
) -> List[Dict]:
    """
    Mean reversion strategy using Bollinger Bands
    Buys when price touches lower band, sells when reaches upper band
    """
    signals = []

    for symbol, df in data.items():
        if len(df) < bb_periods + 1:
            continue

        current = df.iloc[-1]

        # Check for required indicators
        if 'BB_Upper' not in df.columns or 'BB_Lower' not in df.columns:
            continue

        if pd.isna(current['BB_Upper']) or pd.isna(current['BB_Lower']):
            continue

        # Current position
        current_position = positions.get(symbol, {}).get('shares', 0)
        avg_price = positions.get(symbol, {}).get('avg_price', 0)

        # Buy signal - price at lower band
        if current_position == 0:
            if current['close'] <= current['BB_Lower']:
                investment = capital * position_size
                shares = int(investment / current['close'])

                if shares > 0:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'shares': shares
                    })

        # Sell signals
        elif current_position > 0:
            # Take profit at upper band
            if current['close'] >= current['BB_Upper']:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

            # Stop loss
            elif avg_price > 0 and (current['close'] - avg_price) / avg_price < -stop_loss:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

    return signals


def macd_crossover_strategy(
    data: Dict[str, pd.DataFrame],
    positions: Dict[str, Dict],
    capital: float,
    position_size: float = 0.15,
    volume_filter: float = 1.5
) -> List[Dict]:
    """
    MACD crossover strategy with volume confirmation
    Buys on MACD bullish crossover with high volume
    Sells on bearish crossover
    """
    signals = []

    for symbol, df in data.items():
        if len(df) < 27:  # Need enough data for MACD
            continue

        current = df.iloc[-1]
        previous = df.iloc[-2]

        # Check for required indicators
        if 'MACD' not in df.columns or 'MACD_Signal' not in df.columns:
            continue

        if pd.isna(current['MACD']) or pd.isna(current['MACD_Signal']):
            continue

        # Current position
        current_position = positions.get(symbol, {}).get('shares', 0)

        # Buy signal - MACD crosses above signal with volume
        if current_position == 0:
            if (current['MACD'] > current['MACD_Signal'] and
                previous['MACD'] <= previous['MACD_Signal']):

                # Check volume confirmation if available
                volume_confirmed = True
                if 'Volume_Ratio' in df.columns and not pd.isna(current['Volume_Ratio']):
                    volume_confirmed = current['Volume_Ratio'] > volume_filter

                if volume_confirmed:
                    investment = capital * position_size
                    shares = int(investment / current['close'])

                    if shares > 0:
                        signals.append({
                            'symbol': symbol,
                            'action': 'buy',
                            'shares': shares
                        })

        # Sell signal - MACD crosses below signal
        elif current_position > 0:
            if (current['MACD'] < current['MACD_Signal'] and
                previous['MACD'] >= previous['MACD_Signal']):

                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

    return signals


def breakout_strategy(
    data: Dict[str, pd.DataFrame],
    positions: Dict[str, Dict],
    capital: float,
    lookback: int = 20,
    volume_multiplier: float = 2.0,
    position_size: float = 0.2,
    stop_loss: float = 0.03
) -> List[Dict]:
    """
    Breakout strategy
    Buys on price breakout above recent high with volume
    """
    signals = []

    for symbol, df in data.items():
        if len(df) < lookback + 1:
            continue

        current = df.iloc[-1]
        recent_data = df.iloc[-lookback:]

        # Current position
        current_position = positions.get(symbol, {}).get('shares', 0)
        avg_price = positions.get(symbol, {}).get('avg_price', 0)

        # Buy signal - breakout above recent high
        if current_position == 0:
            recent_high = recent_data['high'].max()
            avg_volume = recent_data['volume'].mean()

            # Price breaks above recent high with volume
            if (current['close'] > recent_high and
                current['volume'] > avg_volume * volume_multiplier):

                investment = capital * position_size
                shares = int(investment / current['close'])

                if shares > 0:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'shares': shares
                    })

        # Sell signals
        elif current_position > 0:
            # Stop loss
            if avg_price > 0 and (current['close'] - avg_price) / avg_price < -stop_loss:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

            # Trailing stop - sell if breaks below 20-day low
            recent_low = recent_data['low'].min()
            if current['close'] < recent_low:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

    return signals


def dee_bot_defensive_strategy(
    data: Dict[str, pd.DataFrame],
    positions: Dict[str, Dict],
    capital: float,
    beta_threshold: float = 0.7,
    position_size: float = 0.05,
    max_positions: int = 10,
    rsi_oversold: float = 35,
    stop_loss: float = 0.08
) -> List[Dict]:
    """
    DEE-BOT inspired defensive strategy
    Focuses on low-volatility, defensive positions
    Similar to the actual DEE-BOT implementation
    """
    signals = []
    current_positions_count = len(positions)

    for symbol, df in data.items():
        if len(df) < 50:  # Need sufficient history
            continue

        current = df.iloc[-1]
        recent_data = df.iloc[-20:]

        # Skip if we have max positions
        if current_positions_count >= max_positions and symbol not in positions:
            continue

        # Current position
        current_position = positions.get(symbol, {}).get('shares', 0)
        avg_price = positions.get(symbol, {}).get('avg_price', 0)

        # Calculate simple volatility metric
        returns = recent_data['close'].pct_change().dropna()
        volatility = returns.std()

        # Buy signals for defensive positions
        if current_position == 0:
            # Low volatility + oversold conditions
            low_volatility = volatility < 0.02  # Less than 2% daily volatility

            oversold = False
            if 'RSI' in df.columns and not pd.isna(current['RSI']):
                oversold = current['RSI'] < rsi_oversold

            # Price above 200-day MA (quality filter)
            above_long_ma = False
            if 'SMA_200' in df.columns and not pd.isna(current['SMA_200']):
                above_long_ma = current['close'] > current['SMA_200']

            if low_volatility and oversold and above_long_ma:
                # Conservative position sizing
                investment = capital * position_size
                shares = int(investment / current['close'])

                if shares > 0:
                    signals.append({
                        'symbol': symbol,
                        'action': 'buy',
                        'shares': shares
                    })
                    current_positions_count += 1

        # Sell signals
        elif current_position > 0:
            # Stop loss
            if avg_price > 0 and (current['close'] - avg_price) / avg_price < -stop_loss:
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

            # Take profit if RSI overbought
            elif 'RSI' in df.columns and not pd.isna(current['RSI']):
                if current['RSI'] > 70:
                    signals.append({
                        'symbol': symbol,
                        'action': 'sell',
                        'shares': current_position
                    })

            # Sell if volatility increases significantly
            elif volatility > 0.04:  # More than 4% daily volatility
                signals.append({
                    'symbol': symbol,
                    'action': 'sell',
                    'shares': current_position
                })

    return signals


def pairs_trading_strategy(
    data: Dict[str, pd.DataFrame],
    positions: Dict[str, Dict],
    capital: float,
    lookback: int = 60,
    z_score_threshold: float = 2.0,
    position_size: float = 0.1
) -> List[Dict]:
    """
    Pairs trading strategy
    Trades price divergences between correlated stocks
    """
    signals = []

    # Need at least 2 symbols for pairs trading
    symbols = list(data.keys())
    if len(symbols) < 2:
        return signals

    # For simplicity, we'll pair adjacent symbols
    for i in range(0, len(symbols) - 1, 2):
        symbol1 = symbols[i]
        symbol2 = symbols[i + 1]

        df1 = data[symbol1]
        df2 = data[symbol2]

        # Need sufficient history for both
        if len(df1) < lookback or len(df2) < lookback:
            continue

        # Calculate price ratio
        recent1 = df1.iloc[-lookback:]
        recent2 = df2.iloc[-lookback:]

        # Align dates
        common_dates = recent1.index.intersection(recent2.index)
        if len(common_dates) < lookback * 0.8:  # Need 80% overlap
            continue

        ratio = recent1.loc[common_dates, 'close'] / recent2.loc[common_dates, 'close']
        ratio_mean = ratio.mean()
        ratio_std = ratio.std()

        if ratio_std == 0:
            continue

        current_ratio = df1.iloc[-1]['close'] / df2.iloc[-1]['close']
        z_score = (current_ratio - ratio_mean) / ratio_std

        # Current positions
        pos1 = positions.get(symbol1, {}).get('shares', 0)
        pos2 = positions.get(symbol2, {}).get('shares', 0)

        # Open positions when z-score exceeds threshold
        if pos1 == 0 and pos2 == 0:
            if abs(z_score) > z_score_threshold:
                investment = capital * position_size / 2

                if z_score > z_score_threshold:
                    # Ratio too high - short symbol1, long symbol2
                    shares2 = int(investment / df2.iloc[-1]['close'])
                    if shares2 > 0:
                        signals.append({
                            'symbol': symbol2,
                            'action': 'buy',
                            'shares': shares2
                        })

                elif z_score < -z_score_threshold:
                    # Ratio too low - long symbol1, short symbol2
                    shares1 = int(investment / df1.iloc[-1]['close'])
                    if shares1 > 0:
                        signals.append({
                            'symbol': symbol1,
                            'action': 'buy',
                            'shares': shares1
                        })

        # Close positions when z-score returns to normal
        elif abs(z_score) < 0.5:
            if pos1 > 0:
                signals.append({
                    'symbol': symbol1,
                    'action': 'sell',
                    'shares': pos1
                })
            if pos2 > 0:
                signals.append({
                    'symbol': symbol2,
                    'action': 'sell',
                    'shares': pos2
                })

    return signals