"""
Core Utilities for AI Trading Bot
=================================
Provides retry logic, health monitoring, order verification, and approval tracking.
"""

from .retry_utils import (
    retry_with_backoff,
    retry_api_call,
    retry_market_data,
    retry_trade_execution,
    CircuitBreaker,
    CircuitBreakerOpenError,
    alpaca_circuit,
    alpaca_dee_circuit,
    alpaca_shorgan_paper_circuit,
    alpaca_shorgan_live_circuit,
    anthropic_circuit,
    financial_datasets_circuit
)

from .health_monitor import (
    HealthMonitor,
    TaskTracker,
    TaskStatus,
    AlertLevel,
    get_health_monitor
)

from .order_verification import (
    OrderVerifier,
    OrderVerificationResult,
    FillStatus,
    reconcile_trades
)

from .approval_tracker import (
    ApprovalTracker,
    ApprovalRecord,
    get_approval_tracker
)

__all__ = [
    # Retry utilities
    'retry_with_backoff',
    'retry_api_call',
    'retry_market_data',
    'retry_trade_execution',
    'CircuitBreaker',
    'CircuitBreakerOpenError',
    'alpaca_circuit',
    'alpaca_dee_circuit',
    'alpaca_shorgan_paper_circuit',
    'alpaca_shorgan_live_circuit',
    'anthropic_circuit',
    'financial_datasets_circuit',

    # Health monitoring
    'HealthMonitor',
    'TaskTracker',
    'TaskStatus',
    'AlertLevel',
    'get_health_monitor',

    # Order verification
    'OrderVerifier',
    'OrderVerificationResult',
    'FillStatus',
    'reconcile_trades',

    # Approval tracking
    'ApprovalTracker',
    'ApprovalRecord',
    'get_approval_tracker',
]
