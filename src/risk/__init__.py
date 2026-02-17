"""
Risk Management Module

Contains:
- AdvancedPositionSizer: Kelly Criterion and risk-adjusted position sizing
- CircuitBreaker: Portfolio-level trading halts during adverse conditions (planned)
"""

from .position_sizer import (
    AdvancedPositionSizer,
    PositionSizeResult,
    TradeStats,
    SizingMethod
)

__all__ = [
    'AdvancedPositionSizer',
    'PositionSizeResult', 
    'TradeStats',
    'SizingMethod'
]
