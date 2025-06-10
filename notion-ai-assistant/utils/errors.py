"""
Production-ready error handling and custom exceptions
"""
import traceback
from typing import Optional, Dict, Any, Type
from enum import Enum
import logging


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseAppError(Exception):
    """Base application error with structured information"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        retry_possible: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.context = context or {}
        self.user_message = user_message or "An error occurred. Please try again."
        self.retry_possible = retry_possible
        self.timestamp = None  # Will be set by error handler
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context,
            "user_message": self.user_message,
            "retry_possible": self.retry_possible,
            "traceback": traceback.format_exc()
        }


class ConfigurationError(BaseAppError):
    """Configuration-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            severity=ErrorSeverity.CRITICAL,
            user_message="Service configuration error. Please contact support.",
            **kwargs
        )


class SlackAPIError(BaseAppError):
    """Slack API-related errors"""
    def __init__(self, message: str, api_error: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if api_error:
            context["slack_error"] = api_error
        
        super().__init__(
            message,
            error_code="SLACK_API_ERROR",
            severity=ErrorSeverity.HIGH,
            context=context,
            user_message="Unable to communicate with Slack. Please try again.",
            retry_possible=True,
            **kwargs
        )


class NotionAPIError(BaseAppError):
    """Notion API-related errors"""
    def __init__(self, message: str, notion_error: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if notion_error:
            context["notion_error"] = notion_error
        
        super().__init__(
            message,
            error_code="NOTION_API_ERROR",
            severity=ErrorSeverity.HIGH,
            context=context,
            user_message="Unable to access Notion. Please check your connection.",
            retry_possible=True,
            **kwargs
        )


class OpenAIAPIError(BaseAppError):
    """OpenAI API-related errors"""
    def __init__(self, message: str, openai_error: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if openai_error:
            context["openai_error"] = openai_error
        
        super().__init__(
            message,
            error_code="OPENAI_API_ERROR",
            severity=ErrorSeverity.HIGH,
            context=context,
            user_message="AI service temporarily unavailable. Please try again.",
            retry_possible=True,
            **kwargs
        )


class ComposioAPIError(BaseAppError):
    """Composio API-related errors"""
    def __init__(self, message: str, composio_error: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if composio_error:
            context["composio_error"] = composio_error
        
        super().__init__(
            message,
            error_code="COMPOSIO_API_ERROR",
            severity=ErrorSeverity.HIGH,
            context=context,
            user_message="Integration service unavailable. Please try again.",
            retry_possible=True,
            **kwargs
        )


class SecurityError(BaseAppError):
    """Security-related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="SECURITY_ERROR",
            severity=ErrorSeverity.CRITICAL,
            user_message="Access denied.",
            retry_possible=False,
            **kwargs
        )


class RateLimitError(BaseAppError):
    """Rate limiting errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        context = kwargs.get("context", {})
        if retry_after:
            context["retry_after"] = retry_after
        
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            severity=ErrorSeverity.MEDIUM,
            context=context,
            user_message="Too many requests. Please wait a moment and try again.",
            retry_possible=True,
            **kwargs
        )


class ValidationError(BaseAppError):
    """Input validation errors"""
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            context=context,
            user_message="Invalid input. Please check your request and try again.",
            retry_possible=False,
            **kwargs
        )


class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None
    ) -> BaseAppError:
        """Handle any error and convert to BaseAppError"""
        
        # If already a BaseAppError, just log and return
        if isinstance(error, BaseAppError):
            self._log_error(error, context, user_id, channel_id)
            return error
        
        # Convert other exceptions to BaseAppError
        app_error = self._convert_to_app_error(error, context)
        self._log_error(app_error, context, user_id, channel_id)
        return app_error
    
    def _convert_to_app_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> BaseAppError:
        """Convert standard exceptions to BaseAppError"""
        
        error_message = str(error)
        error_context = context or {}
        error_context["original_error_type"] = type(error).__name__
        
        # Map common exceptions
        if "slack" in error_message.lower():
            return SlackAPIError(error_message, context=error_context)
        elif "notion" in error_message.lower():
            return NotionAPIError(error_message, context=error_context)
        elif "openai" in error_message.lower():
            return OpenAIAPIError(error_message, context=error_context)
        elif "composio" in error_message.lower():
            return ComposioAPIError(error_message, context=error_context)
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return BaseAppError(
                error_message,
                error_code="CONNECTION_ERROR",
                severity=ErrorSeverity.HIGH,
                context=error_context,
                user_message="Connection error. Please try again.",
                retry_possible=True
            )
        elif isinstance(error, ValueError):
            return ValidationError(error_message, context=error_context)
        else:
            return BaseAppError(
                error_message,
                error_code="UNKNOWN_ERROR",
                severity=ErrorSeverity.HIGH,
                context=error_context,
                user_message="An unexpected error occurred. Please try again.",
                retry_possible=True
            )
    
    def _log_error(
        self,
        error: BaseAppError,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None
    ) -> None:
        """Log error with full context"""
        
        log_context = {
            **error.to_dict(),
            **(context or {}),
            "user_id": user_id,
            "channel_id": channel_id
        }
        
        # Choose log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {error.message}", extra=log_context)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {error.message}", extra=log_context)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {error.message}", extra=log_context)
        else:
            self.logger.info(f"Low severity error: {error.message}", extra=log_context)


# Global error handler instance
error_handler = ErrorHandler()