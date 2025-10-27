"""
Data module for AI Trading Bot
Provides alternative data aggregation and analysis
"""

from src.data.alternative_data_aggregator import (
    AlternativeDataAggregator,
    AlternativeDataSignal,
    SignalType,
    SignalCache,
    analyze_tickers_sync
)

__all__ = [
    "AlternativeDataAggregator",
    "AlternativeDataSignal",
    "SignalType",
    "SignalCache",
    "analyze_tickers_sync"
]
