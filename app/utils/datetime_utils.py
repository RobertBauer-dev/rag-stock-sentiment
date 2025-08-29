"""
Date and time utility functions for the application.
"""

from datetime import datetime
from typing import Optional


def format_timestamp(timestamp: Optional[datetime] = None, format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Format a timestamp to a string.
    
    Args:
        timestamp: Datetime object to format, uses current time if None
        format_str: Format string for the timestamp
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def generate_dataset_name(stock_symbol: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate a dataset name for a stock with timestamp.
    
    Args:
        stock_symbol: Stock symbol (e.g., "AAPL")
        timestamp: Datetime object, uses current time if None
        
    Returns:
        Dataset name (e.g., "aapl_20241201_143022")
    """
    formatted_time = format_timestamp(timestamp)
    return f"{stock_symbol.lower()}_{formatted_time}"


def parse_dataset_name(dataset_name: str) -> tuple[str, datetime]:
    """
    Parse a dataset name to extract stock symbol and timestamp.
    
    Args:
        dataset_name: Dataset name (e.g., "aapl_20241201_143022")
        
    Returns:
        Tuple of (stock_symbol, datetime)
    """
    try:
        # Split by underscore and get the last part as timestamp
        parts = dataset_name.split("_")
        if len(parts) < 3:
            raise ValueError("Invalid dataset name format")
        
        stock_symbol = parts[0].upper()
        timestamp_str = "_".join(parts[1:])
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        
        return stock_symbol, timestamp
    except Exception as e:
        raise ValueError(f"Could not parse dataset name '{dataset_name}': {str(e)}")


def is_timestamp_recent(timestamp: datetime, hours: int = 24) -> bool:
    """
    Check if a timestamp is within the last N hours.
    
    Args:
        timestamp: Datetime to check
        hours: Number of hours to check
        
    Returns:
        True if timestamp is recent
    """
    now = datetime.now()
    time_diff = now - timestamp
    return time_diff.total_seconds() < (hours * 3600)


def get_human_readable_time_diff(timestamp: datetime) -> str:
    """
    Get a human-readable time difference from a timestamp.
    
    Args:
        timestamp: Datetime to compare against now
        
    Returns:
        Human-readable string (e.g., "2 hours ago", "3 days ago")
    """
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"
