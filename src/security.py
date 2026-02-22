import os
import secrets
import hashlib
from typing import Optional
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class RateLimit:
    requests: int
    window_seconds: int


class SecurityManager:
    def __init__(self):
        self.api_keys: dict = {}
        self.rate_limits: dict = {}
        self.blocked_ips: set = set()
        self._load_config()
    
    def _load_config(self):
        from config import (
            RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW,
            MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS,
            BLOCKED_PATHS
        )
        self.rate_limit_config = RateLimit(
            requests=RATE_LIMIT_REQUESTS,
            window_seconds=RATE_LIMIT_WINDOW
        )
        self.max_content_length = MAX_CONTENT_LENGTH
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.blocked_paths = BLOCKED_PATHS
    
    def generate_api_key(self, name: str = "default") -> str:
        """Generate a secure API key"""
        key = secrets.token_urlsafe(32)
        self.api_keys[key] = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "requests_count": 0
        }
        return key
    
    def validate_api_key(self, key: str) -> bool:
        """Validate an API key"""
        return key in self.api_keys
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier has exceeded rate limit"""
        now = datetime.now()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Clean old requests
        self.rate_limits[identifier] = [
            t for t in self.rate_limits[identifier]
            if now - t < timedelta(seconds=self.rate_limit_config.window_seconds)
        ]
        
        # Check limit
        if len(self.rate_limits[identifier]) >= self.rate_limit_config.requests:
            return False
        
        # Add new request
        self.rate_limits[identifier].append(now)
        return True
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input"""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        if len(text) > self.max_content_length:
            text = text[:self.max_content_length]
        
        return text
    
    def validate_path(self, path: str) -> bool:
        """Validate file path for security"""
        # Block dangerous paths
        dangerous_patterns = [
            '..', '~', '$', '|', ';', '&', '`',
            '\n', '\r', '\0'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in path:
                return False
        
        # Check against blocked paths
        abs_path = os.path.abspath(path)
        for blocked in self.blocked_paths:
            if abs_path.startswith(blocked):
                return False
        
        return True
    
    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip)
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips


security_manager = SecurityManager()


def rate_limit(requests: int = None, window: int = None):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get identifier from request
            identifier = kwargs.get('user_id', 'default')
            
            if not security_manager.check_rate_limit(identifier):
                raise Exception("Rate limit exceeded. Please try again later.")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_api_key(func):
    """Decorator to require API key"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        api_key = kwargs.get('api_key')
        if api_key and not security_manager.validate_api_key(api_key):
            raise Exception("Invalid API key")
        return await func(*args, **kwargs)
    return wrapper
