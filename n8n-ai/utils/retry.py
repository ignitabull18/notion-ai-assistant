"""
Retry logic and resilience patterns
"""
import asyncio
import time
import random
from typing import Callable, TypeVar, Optional, Type, Tuple, Any, Union, List
from functools import wraps
import logging
from dataclasses import dataclass
from enum import Enum

from utils.errors import BaseAppError

T = TypeVar('T')


class BackoffStrategy(Enum):
    """Backoff strategies for retries"""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    jitter_range: float = 0.1
    retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    non_retriable_exceptions: Tuple[Type[Exception], ...] = ()


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 2
    timeout: float = 30.0


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.logger = logging.getLogger(__name__)
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time < self.config.recovery_timeout:
                self.logger.warning(f"Circuit breaker '{self.name}' is OPEN, rejecting call")
                raise Exception(f"Circuit breaker '{self.name}' is open")
            else:
                # Try to transition to half-open
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        
        try:
            # Execute the function with timeout
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Check for timeout
            if execution_time > self.config.timeout:
                raise TimeoutError(f"Function exceeded timeout of {self.config.timeout}s")
            
            # Success case
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    async def acall(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Async version of call"""
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time < self.config.recovery_timeout:
                self.logger.warning(f"Circuit breaker '{self.name}' is OPEN, rejecting call")
                raise Exception(f"Circuit breaker '{self.name}' is open")
            else:
                # Try to transition to half-open
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        
        try:
            # Execute the function with timeout
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
            
            # Success case
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(
                f"Circuit breaker '{self.name}' tripped to OPEN state "
                f"(failures: {self.failure_count}/{self.config.failure_threshold})"
            )
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time
        }


class RetryHandler:
    """Handle retry logic with various backoff strategies"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        if self.config.backoff_strategy == BackoffStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (2 ** (attempt - 1))
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            base_delay = self.config.base_delay * (2 ** (attempt - 1))
            jitter = base_delay * self.config.jitter_range * (random.random() * 2 - 1)
            delay = base_delay + jitter
        else:
            delay = self.config.base_delay
        
        return min(delay, self.config.max_delay)
    
    def _is_retriable(self, exception: Exception) -> bool:
        """Check if exception is retriable"""
        # Non-retriable exceptions take precedence
        if isinstance(exception, self.config.non_retriable_exceptions):
            return False
        
        # Check if it's a retriable exception
        if isinstance(exception, self.config.retriable_exceptions):
            return True
        
        # For BaseAppError, check retry_possible flag
        if isinstance(exception, BaseAppError):
            return exception.retry_possible
        
        return False
    
    def retry(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for sync functions"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, self.config.max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        self.logger.info(
                            f"Function succeeded on attempt {attempt}",
                            extra={"function": func.__name__, "attempt": attempt}
                        )
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not self._is_retriable(e):
                        self.logger.info(
                            f"Non-retriable exception, not retrying: {type(e).__name__}",
                            extra={"function": func.__name__, "exception": str(e)}
                        )
                        raise
                    
                    if attempt < self.config.max_attempts:
                        delay = self._calculate_delay(attempt)
                        self.logger.warning(
                            f"Attempt {attempt} failed, retrying in {delay:.2f}s",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "delay": delay,
                                "exception": str(e)
                            }
                        )
                        time.sleep(delay)
                    else:
                        self.logger.error(
                            f"All {self.config.max_attempts} attempts failed",
                            extra={"function": func.__name__, "exception": str(e)}
                        )
            
            # All attempts failed
            raise last_exception
        
        return wrapper
    
    def aretry(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for async functions"""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, self.config.max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    if attempt > 1:
                        self.logger.info(
                            f"Async function succeeded on attempt {attempt}",
                            extra={"function": func.__name__, "attempt": attempt}
                        )
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not self._is_retriable(e):
                        self.logger.info(
                            f"Non-retriable exception, not retrying: {type(e).__name__}",
                            extra={"function": func.__name__, "exception": str(e)}
                        )
                        raise
                    
                    if attempt < self.config.max_attempts:
                        delay = self._calculate_delay(attempt)
                        self.logger.warning(
                            f"Async attempt {attempt} failed, retrying in {delay:.2f}s",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "delay": delay,
                                "exception": str(e)
                            }
                        )
                        await asyncio.sleep(delay)
                    else:
                        self.logger.error(
                            f"All {self.config.max_attempts} async attempts failed",
                            extra={"function": func.__name__, "exception": str(e)}
                        )
            
            # All attempts failed
            raise last_exception
        
        return wrapper


# Pre-configured retry handlers for common scenarios
default_retry = RetryHandler(RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER
))

api_retry = RetryHandler(RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=30.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
    retriable_exceptions=(ConnectionError, TimeoutError, Exception),
    non_retriable_exceptions=(ValueError, TypeError)
))

database_retry = RetryHandler(RetryConfig(
    max_attempts=3,
    base_delay=0.5,
    max_delay=10.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL
))


# Global circuit breakers
circuit_breakers = {
    "openai": CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30.0,
        timeout=120.0
    ), "openai"),
    
    "composio": CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0,
        timeout=60.0
    ), "composio"),
    
    "slack": CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=30.0,
        timeout=30.0
    ), "slack")
}


def with_circuit_breaker(name: str):
    """Decorator to add circuit breaker protection"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if name not in circuit_breakers:
                raise ValueError(f"Circuit breaker '{name}' not found")
            return circuit_breakers[name].call(func, *args, **kwargs)
        return wrapper
    return decorator


def with_async_circuit_breaker(name: str):
    """Decorator to add circuit breaker protection for async functions"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if name not in circuit_breakers:
                raise ValueError(f"Circuit breaker '{name}' not found")
            return await circuit_breakers[name].acall(func, *args, **kwargs)
        return wrapper
    return decorator