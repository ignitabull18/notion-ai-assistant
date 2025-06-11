"""
Production configuration management for Notion AI Assistant
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///./data/notion_memories.db"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: str
    model: str = "o3"
    max_completion_tokens: int = 65536
    timeout: int = 120
    max_retries: int = 3
    base_url: Optional[str] = None


@dataclass
class SlackConfig:
    """Slack configuration"""
    bot_token: str
    app_token: str
    signing_secret: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    oauth_redirect_url: Optional[str] = None


@dataclass
class ComposioConfig:
    """Composio configuration"""
    api_key: str
    timeout: int = 60
    max_retries: int = 3
    base_url: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    structured_logging: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    allowed_users: list = field(default_factory=list)
    allowed_channels: list = field(default_factory=list)
    rate_limit_per_minute: int = 60
    max_message_length: int = 4000
    enable_user_validation: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_metrics: bool = True
    metrics_port: int = 8080
    health_check_interval: int = 30
    sentry_dsn: Optional[str] = None
    datadog_api_key: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration"""
    environment: str = "development"
    debug: bool = False
    app_name: str = "notion-ai-assistant"
    version: str = "1.0.0"
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    openai: OpenAIConfig = field(default_factory=lambda: OpenAIConfig(api_key=""))
    slack: SlackConfig = field(default_factory=lambda: SlackConfig(bot_token="", app_token="", signing_secret=""))
    composio: ComposioConfig = field(default_factory=lambda: ComposioConfig(api_key=""))
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    def validate(self) -> None:
        """Validate configuration"""
        errors = []
        
        # Required fields validation
        if not self.openai.api_key:
            errors.append("OPENAI_API_KEY is required")
        if not self.slack.bot_token:
            errors.append("SLACK_BOT_TOKEN is required")
        if not self.slack.app_token:
            errors.append("SLACK_APP_TOKEN is required")
        if not self.slack.signing_secret:
            errors.append("SLACK_SIGNING_SECRET is required")
        if not self.composio.api_key:
            errors.append("COMPOSIO_TOKEN is required")
        
        # Production-specific validation
        if self.environment == "production":
            if self.debug:
                errors.append("Debug mode should be disabled in production")
            if not self.monitoring.sentry_dsn:
                errors.append("Sentry DSN recommended for production")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"- {err}" for err in errors))

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables"""
        config = cls()
        
        # Environment
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # OpenAI
        config.openai.api_key = os.getenv("OPENAI_API_KEY", "")
        config.openai.model = os.getenv("OPENAI_MODEL", "o3")
        config.openai.max_completion_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "65536"))
        config.openai.base_url = os.getenv("OPENAI_BASE_URL")
        
        # Slack
        config.slack.bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        config.slack.app_token = os.getenv("SLACK_APP_TOKEN", "")
        config.slack.signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
        config.slack.client_id = os.getenv("SLACK_CLIENT_ID")
        config.slack.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        
        # Composio
        config.composio.api_key = os.getenv("COMPOSIO_TOKEN", "")
        config.composio.base_url = os.getenv("COMPOSIO_BASE_URL")
        
        # Database
        config.database.url = os.getenv("DATABASE_URL", "sqlite:///./data/notion_memories.db")
        
        # Logging
        config.logging.level = os.getenv("LOG_LEVEL", "INFO")
        config.logging.file_path = os.getenv("LOG_FILE_PATH")
        
        # Security
        allowed_users = os.getenv("ALLOWED_USERS", "")
        if allowed_users:
            config.security.allowed_users = [u.strip() for u in allowed_users.split(",")]
        
        allowed_channels = os.getenv("ALLOWED_CHANNELS", "")
        if allowed_channels:
            config.security.allowed_channels = [c.strip() for c in allowed_channels.split(",")]
        
        config.security.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # Monitoring
        config.monitoring.sentry_dsn = os.getenv("SENTRY_DSN")
        config.monitoring.datadog_api_key = os.getenv("DATADOG_API_KEY")
        config.monitoring.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        
        return config


# Global configuration instance
config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global config
    if config is None:
        config = AppConfig.from_env()
        config.validate()
    return config


def init_config(config_override: Optional[AppConfig] = None) -> AppConfig:
    """Initialize configuration"""
    global config
    if config_override:
        config = config_override
    else:
        config = AppConfig.from_env()
    
    config.validate()
    return config