import re
from typing import Optional

def validate_symbol(symbol: str) -> bool:
    """
    Validate symbol format.
    
    Args:
        symbol: Symbol string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Remove whitespace
    symbol = symbol.strip()
    
    # Check length
    if len(symbol) < 2 or len(symbol) > 20:
        return False
    
    # Check for valid characters (letters, numbers, underscore, dash)
    if not re.match(r'^[A-Za-z0-9_-]+$', symbol):
        return False
    
    return True

def validate_amount(amount: float) -> bool:
    """
    Validate amount value.
    
    Args:
        amount: Amount to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(amount, (int, float)):
        return False
    
    if amount <= 0:
        return False
    
    if amount > 1000000:  # Max 1 million
        return False
    
    return True

def validate_timestamp(timestamp: int) -> bool:
    """
    Validate timestamp.
    
    Args:
        timestamp: Unix timestamp to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(timestamp, int):
        return False
    
    # Check if timestamp is reasonable (not too old, not in future)
    import time
    current_time = int(time.time())
    
    if timestamp < current_time - 86400 * 365:  # Not older than 1 year
        return False
    
    if timestamp > current_time + 86400:  # Not more than 1 day in future
        return False
    
    return True

def sanitize_input(text: str) -> str:
    """
    Sanitize user input.
    
    Args:
        text: Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    return sanitized[:1000]
