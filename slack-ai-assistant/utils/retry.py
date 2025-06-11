"""
Simple retry logic for Slack AI Assistant
"""
import time
from typing import Callable, TypeVar
from functools import wraps
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)


def with_retry(max_attempts: int = 3, delay: float = 1.0):
    """Simple retry decorator"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
            
            raise last_exception
        
        return wrapper
    return decorator