"""
Production-ready logging configuration
"""
import json
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from config import LoggingConfig


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "getMessage", "exc_info",
                "exc_text", "stack_info"
            }
        }
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)


class ContextFilter(logging.Filter):
    """Add context information to log records"""
    
    def __init__(self, app_name: str, version: str, environment: str):
        super().__init__()
        self.app_name = app_name
        self.version = version
        self.environment = environment
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record"""
        record.app_name = self.app_name
        record.version = self.version
        record.environment = self.environment
        return True


def setup_logging(
    config: LoggingConfig,
    app_name: str = "notion-ai-assistant",
    version: str = "1.0.0",
    environment: str = "development"
) -> None:
    """Setup production-ready logging"""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if config.structured_logging:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(config.format)
    
    # Create context filter
    context_filter = ContextFilter(app_name, version, environment)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)
    root_logger.addHandler(console_handler)
    
    # File handler (if configured)
    if config.file_path:
        # Ensure log directory exists
        log_path = Path(config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.file_path,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("slack_bolt").setLevel(logging.WARNING)
    logging.getLogger("slack_sdk").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized",
        extra={
            "app_name": app_name,
            "version": version,
            "environment": environment,
            "log_level": config.level,
            "structured_logging": config.structured_logging,
            "file_logging": config.file_path is not None
        }
    )


class LoggingMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_method_call(self, method_name: str, **kwargs) -> None:
        """Log method call with parameters"""
        self.logger.debug(
            f"Calling {method_name}",
            extra={"method": method_name, "parameters": kwargs}
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error with context"""
        self.logger.error(
            f"Error occurred: {str(error)}",
            exc_info=True,
            extra={"error_type": type(error).__name__, "context": context or {}}
        )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)