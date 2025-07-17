"""
Upload Token Manager for Two-Step Photo Upload System

This module handles the generation, validation, and management of secure upload tokens
that allow users to upload photos to existing log entries through a simple web interface.

Key Features:
- Secure token generation using secrets module
- Token expiration (24 hours default)
- One-time use tokens to prevent replay attacks
- In-memory storage (can be extended to Redis later)
- Log ID association for linking photos to correct entries
"""

import secrets
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Token configuration
TOKEN_LENGTH = 32  # Length of random token string
DEFAULT_EXPIRATION_HOURS = 24  # Token expires after 24 hours

# In-memory storage for upload tokens
_token_storage: Dict[str, Dict[str, Any]] = {}

def generate_upload_token(log_id: str, plant_name: str, expiration_hours: int = DEFAULT_EXPIRATION_HOURS) -> str:
    """
    Generate a secure upload token for a specific log entry.
    
    Args:
        log_id (str): The log entry ID this token is for
        plant_name (str): Name of the plant for display purposes
        expiration_hours (int): Hours until token expires
        
    Returns:
        str: Secure upload token
    """
    # Generate cryptographically secure random token
    token = secrets.token_urlsafe(TOKEN_LENGTH)
    
    # Calculate expiration timestamp
    expiration_time = datetime.now() + timedelta(hours=expiration_hours)
    
    # Create token data
    token_data = {
        'log_id': log_id,
        'plant_name': plant_name,
        'created_at': datetime.now().isoformat(),
        'expires_at': expiration_time.isoformat(),
        'used': False,
        'ip_address': "",  # Will be set when token is used
        'uploaded_at': ""
    }
    
    # Store in memory
    _token_storage[token] = token_data
    logger.info(f"Upload token generated for log {log_id}, expires in {expiration_hours} hours")
    
    return token

def validate_upload_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate an upload token and return associated log information.
    
    Args:
        token (str): Upload token to validate
        
    Returns:
        Tuple[bool, Optional[Dict], Optional[str]]: (is_valid, token_data, error_message)
    """
    if not token:
        return False, None, "Token is required"
    
    try:
        # Check if token exists in storage
        if token not in _token_storage:
            return False, None, "Invalid or expired token"
        
        token_data = _token_storage[token]
        
        # Check expiration
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() > expires_at:
            # Remove expired token
            del _token_storage[token]
            return False, None, "Token has expired"
        
        # Check if token has already been used
        if token_data.get('used', False):
            return False, None, "Token has already been used"
        
        # Token is valid
        return True, token_data, None
        
    except Exception as e:
        logger.error(f"Error validating upload token: {e}")
        return False, None, "Token validation error"

def mark_token_used(token: str, ip_address: str = "") -> bool:
    """
    Mark a token as used to prevent reuse.
    
    Args:
        token (str): Upload token to mark as used
        ip_address (str): IP address of the user who used the token
        
    Returns:
        bool: True if successfully marked as used
    """
    try:
        if token not in _token_storage:
            return False
        
        # Update token data
        _token_storage[token].update({
            'used': True,
            'uploaded_at': datetime.now().isoformat(),
            'ip_address': ip_address
        })
        
        logger.info(f"Marked upload token as used for log {_token_storage[token].get('log_id')}")
        return True
        
    except Exception as e:
        logger.error(f"Error marking token as used: {e}")
        return False

def generate_upload_url(token: str, base_url: str = "https://plant-database-api.onrender.com") -> str:
    """
    Generate the complete upload URL for a token.
    
    Args:
        token (str): Upload token
        base_url (str): Base URL of the API
        
    Returns:
        str: Complete upload URL
    """
    return f"{base_url}/upload/{token}"

def cleanup_expired_tokens() -> int:
    """
    Clean up expired tokens from storage.
    Should be called periodically to prevent memory leaks.
    
    Returns:
        int: Number of tokens cleaned up
    """
    if not _token_storage:
        return 0
    
    cleaned_count = 0
    current_time = datetime.now()
    expired_tokens = []
    
    for token, token_data in _token_storage.items():
        try:
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if current_time > expires_at:
                expired_tokens.append(token)
        except Exception as e:
            logger.warning(f"Error checking token expiration: {e}")
            expired_tokens.append(token)  # Remove malformed tokens
    
    for token in expired_tokens:
        del _token_storage[token]
        cleaned_count += 1
    
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} expired upload tokens")
    
    return cleaned_count

def get_token_info(token: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a token (for debugging/admin purposes).
    
    Args:
        token (str): Upload token
        
    Returns:
        Optional[Dict]: Token information or None if not found
    """
    try:
        return _token_storage.get(token)
    except Exception as e:
        logger.error(f"Error getting token info: {e}")
        return None

def get_active_token_count() -> int:
    """
    Get the number of active (non-expired) tokens.
    
    Returns:
        int: Number of active tokens
    """
    cleanup_expired_tokens()  # Clean up first
    return len(_token_storage) 