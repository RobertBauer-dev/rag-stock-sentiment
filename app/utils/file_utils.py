"""
File utility functions for the application.
"""

import os
from pathlib import Path
from typing import Optional, List
import glob


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory_path: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def get_latest_file(pattern: str, directory: str = ".") -> Optional[str]:
    """
    Get the most recent file matching a pattern.
    
    Args:
        pattern: File pattern to match (e.g., "*.csv")
        directory: Directory to search in
        
    Returns:
        Path to the latest file, or None if no files found
    """
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    
    # Return the most recent file
    return max(files, key=os.path.getctime)


def list_files_by_pattern(pattern: str, directory: str = ".") -> List[str]:
    """
    List all files matching a pattern in a directory.
    
    Args:
        pattern: File pattern to match
        directory: Directory to search in
        
    Returns:
        List of matching file paths
    """
    return glob.glob(os.path.join(directory, pattern))


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def is_file_recent(file_path: str, hours: int = 24) -> bool:
    """
    Check if a file was modified within the last N hours.
    
    Args:
        file_path: Path to the file
        hours: Number of hours to check
        
    Returns:
        True if file was modified recently
    """
    import time
    file_time = os.path.getmtime(file_path)
    current_time = time.time()
    return (current_time - file_time) < (hours * 3600)
