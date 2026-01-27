"""
Smoke tests for Railway Scheduler
===================================
Verifies that railway_scheduler.py correctly integrates with
circuit breakers, health monitoring, and Telegram notifications.

These tests would have caught the Jan 27 2026 crash caused by
calling non-existent CircuitBreaker methods (can_execute, record_failure
without args).

Run: pytest tests/test_railway_scheduler_smoke.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_telegram():
    """Prevent real Telegram sends in all tests."""
    with patch("railway_scheduler.send_telegram") as mock:
        yield mock


@pytest.fixture
def mock_health_monitor():
    """Mock the global health_monitor used by all task functions."""
    mock_hm = MagicMock()
    # track_task returns a context manager
    mock_tracker = MagicMock()
    mock_hm.track_task.return_value.__enter__ = MagicMock(return_value=mock_tracker)
    mock_hm.track_task.return_value.__exit__ = MagicMock(return_value=False)
    mock_hm.get_system_health.return_value = {
        "overall": "healthy",
        "summary": {"healthy": 5, "failed": 0, "stale": 0, "unknown": 0},
        "issues": [],
    }
    with patch("railway_scheduler.health_monitor", mock_hm):
        yield mock_hm


@pytest.fixture
def fresh_anthropic_circuit():
    """Provide a real CircuitBreaker in CLOSED state."""
    from scripts.core.retry_utils import CircuitBreaker
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=120, name="anthropic_test")
    with patch("railway_scheduler.anthropic_circuit", cb):
        yield cb


@pytest.fixture
def fresh_alpaca_circuit():
    """Provide a real CircuitBreaker in CLOSED state."""
    from scripts.core.retry_utils import CircuitBreaker
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=300, name="alpaca_test")
    with patch("railway_scheduler.alpaca_circuit", cb):
        yield cb


# ---------------------------------------------------------------------------
# run_research() tests
# ---------------------------------------------------------------------------

class TestRunResearch:
    """Tests for the research generation task."""

    def test_success_path(self, mock_health_monitor, fresh_anthropic_circuit):
        """Research succeeds -> circuit records success, Telegram notified."""
        with patch(
            "scripts.automation.daily_claude_research.main"
        ) as mock_main:
            from railway_scheduler import run_research
            run_research()

            mock_main.assert_called_once()
            assert fresh_anthropic_circuit.state == "CLOSED"
            assert fresh_anthropic_circuit._failure_count == 0

    def test_failure_records_to_circuit(self, mock_health_monitor, fresh_anthropic_circuit):
        """Research fails -> circuit records failure with exception arg."""
        with patch(
            "scripts.automation.daily_claude_research.main",
            side_effect=RuntimeError("API error"),
        ):
            from railway_scheduler import run_research
            run_research()  # should not raise

            assert fresh_anthropic_circuit._failure_count == 1

    def test_circuit_open_blocks_research(self, mock_health_monitor, fresh_anthropic_circuit, mock_telegram):
        """When circuit is OPEN, research is blocked without calling main."""
        # Force circuit open
        fresh_anthropic_circuit._state = "OPEN"

        with patch(
            "scripts.automation.daily_claude_research.main"
        ) as mock_main:
            from railway_scheduler import run_research
            run_research()  # should not raise

            mock_main.assert_not_called()
            # Should have sent failure telegram
            failure_calls = [
                c for c in mock_telegram.call_args_list
                if "failed" in str(c).lower() or "OPEN" in str(c)
            ]
            assert len(failure_calls) >= 1

    def test_does_not_crash_on_failure(self, mock_health_monitor, fresh_anthropic_circuit):
        """run_research must never propagate exceptions to the scheduler loop."""
        with patch(
            "scripts.automation.daily_claude_research.main",
            side_effect=Exception("total crash"),
        ):
            from railway_scheduler import run_research
            # This must not raise
            run_research()


# ---------------------------------------------------------------------------
# run_execute() tests
# ---------------------------------------------------------------------------

class TestRunExecute:
    """Tests for the trade execution task."""

    def test_success_path(self, mock_health_monitor, fresh_alpaca_circuit):
        """Execution succeeds -> circuit records success."""
        with patch(
            "scripts.automation.execute_daily_trades.main"
        ) as mock_main:
            from railway_scheduler import run_execute
            run_execute()

            mock_main.assert_called_once()
            assert fresh_alpaca_circuit.state == "CLOSED"

    def test_failure_records_to_circuit(self, mock_health_monitor, fresh_alpaca_circuit):
        """Execution fails -> circuit records failure."""
        with patch(
            "scripts.automation.execute_daily_trades.main",
            side_effect=ConnectionError("Alpaca down"),
        ):
            from railway_scheduler import run_execute
            run_execute()

            assert fresh_alpaca_circuit._failure_count == 1

    def test_circuit_open_blocks_execution(self, mock_health_monitor, fresh_alpaca_circuit):
        """When circuit is OPEN, execution is blocked."""
        fresh_alpaca_circuit._state = "OPEN"

        with patch(
            "scripts.automation.execute_daily_trades.main"
        ) as mock_main:
            from railway_scheduler import run_execute
            run_execute()

            mock_main.assert_not_called()

    def test_sends_critical_alert_on_failure(self, mock_health_monitor, fresh_alpaca_circuit):
        """Execution failure sends CRITICAL alert (not just HIGH)."""
        with patch(
            "scripts.automation.execute_daily_trades.main",
            side_effect=Exception("order failed"),
        ):
            from railway_scheduler import run_execute
            run_execute()

            mock_health_monitor.send_alert.assert_called_once()
            alert_level = mock_health_monitor.send_alert.call_args[0][0]
            from scripts.core import AlertLevel
            assert alert_level == AlertLevel.CRITICAL


# ---------------------------------------------------------------------------
# run_trades() tests
# ---------------------------------------------------------------------------

class TestRunTrades:
    """Tests for the trade generation task."""

    def test_success_path(self, mock_health_monitor):
        """Trade generation succeeds."""
        with patch(
            "scripts.automation.generate_todays_trades_v2.main"
        ) as mock_main:
            from railway_scheduler import run_trades
            run_trades()
            mock_main.assert_called_once()

    def test_does_not_crash_on_failure(self, mock_health_monitor):
        """run_trades must never propagate exceptions."""
        with patch(
            "scripts.automation.generate_todays_trades_v2.main",
            side_effect=KeyError("portfolio_value"),
        ):
            from railway_scheduler import run_trades
            run_trades()


# ---------------------------------------------------------------------------
# run_performance() tests
# ---------------------------------------------------------------------------

class TestRunPerformance:
    """Tests for the performance graph task."""

    def test_success_path(self, mock_health_monitor):
        """Performance update succeeds."""
        with patch(
            "scripts.performance.generate_performance_graph.main"
        ) as mock_main:
            from railway_scheduler import run_performance
            run_performance()
            mock_main.assert_called_once()

    def test_sends_warning_on_failure(self, mock_health_monitor):
        """Performance failure sends WARNING (not CRITICAL)."""
        with patch(
            "scripts.performance.generate_performance_graph.main",
            side_effect=Exception("graph error"),
        ):
            from railway_scheduler import run_performance
            run_performance()

            mock_health_monitor.send_alert.assert_called_once()
            alert_level = mock_health_monitor.send_alert.call_args[0][0]
            from scripts.core import AlertLevel
            assert alert_level == AlertLevel.WARNING


# ---------------------------------------------------------------------------
# heartbeat() tests
# ---------------------------------------------------------------------------

class TestHeartbeat:
    """Tests for the hourly heartbeat."""

    def test_sends_at_9am(self, mock_health_monitor, mock_telegram):
        """Heartbeat sends message at 9:00 AM ET."""
        import pytz
        from datetime import datetime as dt

        mock_time = dt(2026, 1, 28, 9, 2, tzinfo=pytz.timezone("America/New_York"))
        with patch("railway_scheduler.get_et_time", return_value=mock_time):
            from railway_scheduler import heartbeat
            heartbeat()

            # Should have sent a heartbeat message
            assert mock_telegram.called
            msg = mock_telegram.call_args[0][0]
            assert "Railway Scheduler" in msg
            assert "HEALTHY" in msg

    def test_silent_outside_9am(self, mock_health_monitor, mock_telegram):
        """Heartbeat does NOT send outside the 9 AM window."""
        import pytz
        from datetime import datetime as dt

        mock_time = dt(2026, 1, 28, 14, 30, tzinfo=pytz.timezone("America/New_York"))
        with patch("railway_scheduler.get_et_time", return_value=mock_time):
            from railway_scheduler import heartbeat
            heartbeat()

            mock_telegram.assert_not_called()


# ---------------------------------------------------------------------------
# run_health_check() tests
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """Tests for the daily health check."""

    def test_no_alert_when_healthy(self, mock_health_monitor):
        """Healthy system does NOT trigger alert."""
        mock_health_monitor.get_system_health.return_value = {
            "overall": "healthy",
            "issues": [],
        }
        from railway_scheduler import run_health_check
        run_health_check()

        mock_health_monitor.send_alert.assert_not_called()

    def test_alert_when_unhealthy(self, mock_health_monitor):
        """Unhealthy system triggers HIGH alert."""
        mock_health_monitor.get_system_health.return_value = {
            "overall": "unhealthy",
            "issues": ["trade_execution: FAILED - timeout"],
        }
        from railway_scheduler import run_health_check
        run_health_check()

        mock_health_monitor.send_alert.assert_called_once()
        level = mock_health_monitor.send_alert.call_args[0][0]
        from scripts.core import AlertLevel
        assert level == AlertLevel.HIGH

    def test_critical_alert_when_critical(self, mock_health_monitor):
        """Critical system triggers CRITICAL alert."""
        mock_health_monitor.get_system_health.return_value = {
            "overall": "critical",
            "issues": ["research: FAILED", "execution: FAILED"],
        }
        from railway_scheduler import run_health_check
        run_health_check()

        level = mock_health_monitor.send_alert.call_args[0][0]
        from scripts.core import AlertLevel
        assert level == AlertLevel.CRITICAL


# ---------------------------------------------------------------------------
# CircuitBreaker unit tests (the exact API used by scheduler)
# ---------------------------------------------------------------------------

class TestCircuitBreakerAPI:
    """Verify the CircuitBreaker API matches what railway_scheduler.py calls.

    These tests exist because the Jan 27 crash was caused by calling
    methods that don't exist on CircuitBreaker (can_execute, record_failure
    without args). These tests ensure the API contract stays stable.
    """

    def test_state_property_exists(self):
        """CircuitBreaker must have a .state property (not .can_execute())."""
        from scripts.core.retry_utils import CircuitBreaker
        cb = CircuitBreaker(name="test")
        assert hasattr(cb, "state")
        assert cb.state in ("CLOSED", "OPEN", "HALF_OPEN")

    def test_no_can_execute_method(self):
        """CircuitBreaker must NOT have can_execute() - this caused the crash."""
        from scripts.core.retry_utils import CircuitBreaker
        cb = CircuitBreaker(name="test")
        assert not hasattr(cb, "can_execute"), (
            "can_execute() does not exist on CircuitBreaker. "
            "Use .state == 'OPEN' instead."
        )

    def test_record_failure_requires_exception(self):
        """record_failure() must accept an exception argument."""
        from scripts.core.retry_utils import CircuitBreaker
        cb = CircuitBreaker(name="test")
        # This is the correct call signature
        cb.record_failure(RuntimeError("test error"))
        assert cb._failure_count == 1

    def test_record_failure_without_args_raises(self):
        """record_failure() without args must fail - catches misuse."""
        from scripts.core.retry_utils import CircuitBreaker
        cb = CircuitBreaker(name="test")
        with pytest.raises(TypeError):
            cb.record_failure()  # Missing required 'exception' arg

    def test_record_success_no_args(self):
        """record_success() takes no arguments."""
        from scripts.core.retry_utils import CircuitBreaker
        cb = CircuitBreaker(name="test")
        cb.record_success()  # Should not raise

    def test_state_transitions(self):
        """CLOSED -> OPEN after threshold failures."""
        from scripts.core.retry_utils import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=2, name="test")
        assert cb.state == "CLOSED"

        cb.record_failure(RuntimeError("err1"))
        assert cb.state == "CLOSED"  # 1 < threshold

        cb.record_failure(RuntimeError("err2"))
        assert cb.state == "OPEN"  # 2 >= threshold
