"""
API Key authentication for PDF Converter API.
"""

import os
import secrets
from typing import Optional
from fastapi import Security, HTTPException, Depends, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

# API Key header name
API_KEY_NAME = "X-API-Key"
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Load API keys (in a real app, use a database)
API_KEYS = {}

# Default admin API key (for testing only, not for production)
DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY", "test_api_key_12345")

# Add default API key to the dictionary
API_KEYS[DEFAULT_API_KEY] = {
    "user_id": "admin",
    "rate_limit": "1000/day",
    "is_admin": True
}

def get_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> dict:
    """
    Validate API key and return user info.
    
    Args:
        api_key_header: API key from request header
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If API key is invalid
    """
    # Check if API authentication is enabled
    if not settings.ENVIRONMENT == "production":
        # In development mode, allow access without API key
        if not api_key_header:
            return {"user_id": "dev", "rate_limit": "unlimited", "is_admin": True}
    
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    
    if api_key_header not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return API_KEYS[api_key_header]
    
def generate_api_key() -> str:
    """
    Generate a new API key.
    
    Returns:
        New API key
    """
    return secrets.token_urlsafe(32)
