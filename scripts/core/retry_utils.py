"""
Retry Utilities for AI Trading Bot
===================================
Implements exponential backoff, circuit breaker pattern, and error handling.

Author: AI Trading Bot System
Date: January 13, 2026
"""

import time
import functools
import logging
from typing import Callable, TypeVar, Any, Optional, List, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for delay after each attempt
        retryable_exceptions: Tuple of exceptions that trigger retry
        non_retryable_exceptions: Tuple of exceptions that should NOT retry
        on_retry: Callback function called on each retry (exception, attempt_num)

    Example:
        @retry_with_backoff(max_attempts=3, initial_delay=2.0)
        def fetch_market_data(ticker):
            return api.get_price(ticker)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except non_retryable_exceptions as e:
                    # Don't retry these - raise immediately
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise

                    # Calculate next delay with jitter
                    jitter = delay * 0.1 * (0.5 - time.time() % 1)  # +/- 10% jitter
                    actual_delay = min(delay + jitter, max_delay)

                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {actual_delay:.1f}s..."
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(actual_delay)
                    delay = min(delay * backoff_factor, max_delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests fail immediately
    - HALF_OPEN: Testing if service recovered

    Example:
        circuit = CircuitBreaker(failure_threshold=3, timeout_seconds=300)

        @circuit.protected
        def call_external_api():
            return api.request()
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(
        self,
        failure_threshold: int = 3,
        success_threshold: int = 2,
        timeout_seconds: float = 300,
        name: str = "default"
    ):
        """
        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open before closing
            timeout_seconds: Time before attempting half-open
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.name = name

        self._state = self.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None

    @property
    def state(self) -> str:
        """Get current circuit state, checking for timeout"""
        if self._state == self.OPEN:
            if self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self._state = self.HALF_OPEN
                    self._success_count = 0
                    logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN (timeout elapsed)")
        return self._state

    def record_success(self):
        """Record a successful call"""
        if self.state == self.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = self.CLOSED
                self._failure_count = 0
                logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED (recovered)")
        elif self.state == self.CLOSED:
            self._failure_count = 0

    def record_failure(self, exception: Exception):
        """Record a failed call"""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        if self.state == self.HALF_OPEN:
            self._state = self.OPEN
            logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN (failure during test)")
        elif self.state == self.CLOSED:
            if self._failure_count >= self.failure_threshold:
                self._state = self.OPEN
                logger.warning(
                    f"Circuit {self.name}: CLOSED -> OPEN "
                    f"(threshold {self.failure_threshold} reached)"
                )

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function through circuit breaker.

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        if self.state == self.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit {self.name} is OPEN. "
                f"Retry after {self.timeout_seconds}s timeout."
            )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            raise

    def protected(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to protect a function with circuit breaker"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return self.call(func, *args, **kwargs)
        return wrapper


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Pre-configured circuit breakers for different services
alpaca_circuit = CircuitBreaker(
    failure_threshold=3,
    timeout_seconds=300,
    name="alpaca"
)

anthropic_circuit = CircuitBreaker(
    failure_threshold=2,
    timeout_seconds=120,
    name="anthropic"
)

financial_datasets_circuit = CircuitBreaker(
    failure_threshold=3,
    timeout_seconds=180,
    name="financial_datasets"
)


# Convenience decorators for common retry patterns
def retry_api_call(func: Callable[..., T]) -> Callable[..., T]:
    """Standard retry for API calls"""
    return retry_with_backoff(
        max_attempts=3,
        initial_delay=2.0,
        max_delay=30.0,
        backoff_factor=2.0
    )(func)


def retry_market_data(func: Callable[..., T]) -> Callable[..., T]:
    """Retry for market data fetches (more patient)"""
    return retry_with_backoff(
        max_attempts=5,
        initial_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0
    )(func)


def retry_trade_execution(func: Callable[..., T]) -> Callable[..., T]:
    """Retry for trade execution (fewer attempts, faster)"""
    return retry_with_backoff(
        max_attempts=2,
        initial_delay=1.0,
        max_delay=5.0,
        backoff_factor=1.5
    )(func)


if __name__ == "__main__":
    # Test the retry decorator
    call_count = 0

    @retry_with_backoff(max_attempts=3, initial_delay=0.5)
    def flaky_function():
        global call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Attempt {call_count} failed")
        return "Success!"

    print("Testing retry decorator...")
    result = flaky_function()
    print(f"Result: {result}")
    print(f"Total calls: {call_count}")

    # Test circuit breaker
    print("\nTesting circuit breaker...")
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=5, name="test")

    @cb.protected
    def failing_function():
        raise ValueError("Always fails")

    for i in range(4):
        try:
            failing_function()
        except CircuitBreakerOpenError as e:
            print(f"Call {i+1}: Circuit open - {e}")
        except ValueError as e:
            print(f"Call {i+1}: Function failed - {e}")
