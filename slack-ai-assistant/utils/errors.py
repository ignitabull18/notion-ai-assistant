"""
Simple error handling for Slack AI Assistant
"""
import logging
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')
logger = logging.getLogger(__name__)


def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Simple error handler decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper