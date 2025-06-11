"""
Security utilities and middleware
"""
import re
import hashlib
import hmac
import time
from typing import Dict, Set, Optional, List
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from utils.errors import SecurityError, RateLimitError


@dataclass
class RateLimitBucket:
    """Rate limit bucket for tracking usage"""
    count: int = 0
    window_start: datetime = None
    
    def reset_if_needed(self, window_duration: int) -> None:
        """Reset bucket if window has expired"""
        now = datetime.utcnow()
        if (self.window_start is None or 
            (now - self.window_start).total_seconds() >= window_duration):
            self.count = 0
            self.window_start = now


class SecurityValidator:
    """Input validation and security checks"""
    
    # Suspicious patterns to detect
    SUSPICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'data:text/html',            # Data URLs
        r'<iframe[^>]*>.*?</iframe>', # Iframes
        r'eval\s*\(',                 # eval() calls
        r'exec\s*\(',                 # exec() calls
        r'__import__\s*\(',           # Python imports
        r'subprocess\.',              # Subprocess calls
        r'os\.',                      # OS module
        r'file://',                   # File URLs
        r'\.\./',                     # Directory traversal
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS]
    
    def validate_message(self, message: str, max_length: int = 4000) -> str:
        """Validate and sanitize user message"""
        if not message or not isinstance(message, str):
            raise SecurityError("Invalid message format")
        
        # Check length
        if len(message) > max_length:
            raise SecurityError(f"Message too long (max {max_length} characters)")
        
        # Check for suspicious patterns
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                self.logger.warning(
                    "Suspicious pattern detected in message",
                    extra={"pattern": pattern.pattern, "message_preview": message[:100]}
                )
                raise SecurityError("Message contains suspicious content")
        
        # Basic sanitization
        sanitized = message.strip()
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')
        
        return sanitized
    
    def validate_user_id(self, user_id: str) -> str:
        """Validate Slack user ID format"""
        if not user_id or not isinstance(user_id, str):
            raise SecurityError("Invalid user ID")
        
        # Slack user IDs start with 'U' and are alphanumeric
        if not re.match(r'^U[A-Z0-9]{8,11}$', user_id):
            raise SecurityError("Invalid user ID format")
        
        return user_id
    
    def validate_channel_id(self, channel_id: str) -> str:
        """Validate Slack channel ID format"""
        if not channel_id or not isinstance(channel_id, str):
            raise SecurityError("Invalid channel ID")
        
        # Slack channel IDs start with 'C' or 'D' and are alphanumeric
        if not re.match(r'^[CD][A-Z0-9]{8,11}$', channel_id):
            raise SecurityError("Invalid channel ID format")
        
        return channel_id


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, requests_per_minute: int = 60, window_duration: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_duration = window_duration
        self.buckets: Dict[str, RateLimitBucket] = defaultdict(RateLimitBucket)
        self.logger = logging.getLogger(__name__)
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        bucket = self.buckets[identifier]
        bucket.reset_if_needed(self.window_duration)
        
        if bucket.count >= self.requests_per_minute:
            self.logger.warning(
                "Rate limit exceeded",
                extra={"identifier": identifier, "count": bucket.count, "limit": self.requests_per_minute}
            )
            raise RateLimitError(
                f"Rate limit exceeded: {bucket.count}/{self.requests_per_minute} requests per minute",
                retry_after=self.window_duration,
                context={"identifier": identifier, "current_count": bucket.count}
            )
        
        bucket.count += 1
        return True
    
    def get_usage(self, identifier: str) -> Dict[str, int]:
        """Get current usage for identifier"""
        bucket = self.buckets[identifier]
        bucket.reset_if_needed(self.window_duration)
        
        return {
            "current_count": bucket.count,
            "limit": self.requests_per_minute,
            "window_duration": self.window_duration,
            "remaining": max(0, self.requests_per_minute - bucket.count)
        }


class SlackSignatureValidator:
    """Validate Slack request signatures"""
    
    def __init__(self, signing_secret: str):
        self.signing_secret = signing_secret.encode()
        self.logger = logging.getLogger(__name__)
    
    def validate_signature(
        self,
        timestamp: str,
        body: str,
        signature: str,
        tolerance: int = 300  # 5 minutes
    ) -> bool:
        """Validate Slack request signature"""
        try:
            # Check timestamp to prevent replay attacks
            request_time = int(timestamp)
            current_time = int(time.time())
            
            if abs(current_time - request_time) > tolerance:
                self.logger.warning(
                    "Request timestamp outside tolerance",
                    extra={"timestamp": timestamp, "tolerance": tolerance}
                )
                raise SecurityError("Request timestamp is too old or too far in the future")
            
            # Create signature
            sig_basestring = f"v0:{timestamp}:{body}"
            computed_signature = 'v0=' + hmac.new(
                self.signing_secret,
                sig_basestring.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures using constant-time comparison
            if not hmac.compare_digest(computed_signature, signature):
                self.logger.warning("Invalid request signature")
                raise SecurityError("Invalid request signature")
            
            return True
            
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Signature validation error: {e}")
            raise SecurityError("Invalid signature format")


class AccessController:
    """Control access to the application"""
    
    def __init__(
        self,
        allowed_users: Optional[List[str]] = None,
        allowed_channels: Optional[List[str]] = None
    ):
        self.allowed_users: Set[str] = set(allowed_users or [])
        self.allowed_channels: Set[str] = set(allowed_channels or [])
        self.logger = logging.getLogger(__name__)
    
    def check_user_access(self, user_id: str) -> bool:
        """Check if user has access"""
        if not self.allowed_users:  # No restrictions if list is empty
            return True
        
        if user_id not in self.allowed_users:
            self.logger.warning(
                "Access denied for user",
                extra={"user_id": user_id}
            )
            raise SecurityError("Access denied")
        
        return True
    
    def check_channel_access(self, channel_id: str) -> bool:
        """Check if channel access is allowed"""
        if not self.allowed_channels:  # No restrictions if list is empty
            return True
        
        if channel_id not in self.allowed_channels:
            self.logger.warning(
                "Access denied for channel",
                extra={"channel_id": channel_id}
            )
            raise SecurityError("Access denied for this channel")
        
        return True
    
    def add_allowed_user(self, user_id: str) -> None:
        """Add user to allowed list"""
        self.allowed_users.add(user_id)
        self.logger.info(f"Added user to allowed list: {user_id}")
    
    def remove_allowed_user(self, user_id: str) -> None:
        """Remove user from allowed list"""
        self.allowed_users.discard(user_id)
        self.logger.info(f"Removed user from allowed list: {user_id}")


class SecurityMiddleware:
    """Combined security middleware"""
    
    def __init__(
        self,
        signing_secret: str,
        rate_limit_per_minute: int = 60,
        max_message_length: int = 4000,
        allowed_users: Optional[List[str]] = None,
        allowed_channels: Optional[List[str]] = None
    ):
        self.validator = SecurityValidator()
        self.rate_limiter = RateLimiter(rate_limit_per_minute)
        self.signature_validator = SlackSignatureValidator(signing_secret)
        self.access_controller = AccessController(allowed_users, allowed_channels)
        self.max_message_length = max_message_length
        self.logger = logging.getLogger(__name__)
    
    def validate_request(
        self,
        user_id: str,
        channel_id: str,
        message: str,
        timestamp: Optional[str] = None,
        signature: Optional[str] = None,
        body: Optional[str] = None
    ) -> Dict[str, str]:
        """Validate entire request"""
        
        # Log security check
        self.logger.debug(
            "Starting security validation",
            extra={"user_id": user_id, "channel_id": channel_id}
        )
        
        # Validate signature if provided
        if timestamp and signature and body:
            self.signature_validator.validate_signature(timestamp, body, signature)
        
        # Validate input formats
        clean_user_id = self.validator.validate_user_id(user_id)
        clean_channel_id = self.validator.validate_channel_id(channel_id)
        clean_message = self.validator.validate_message(message, self.max_message_length)
        
        # Check access permissions
        self.access_controller.check_user_access(clean_user_id)
        self.access_controller.check_channel_access(clean_channel_id)
        
        # Check rate limits
        rate_limit_key = f"{clean_user_id}:{clean_channel_id}"
        self.rate_limiter.check_rate_limit(rate_limit_key)
        
        self.logger.debug(
            "Security validation passed",
            extra={"user_id": clean_user_id, "channel_id": clean_channel_id}
        )
        
        return {
            "user_id": clean_user_id,
            "channel_id": clean_channel_id,
            "message": clean_message
        }