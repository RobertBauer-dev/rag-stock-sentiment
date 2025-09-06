"""
Centralized logging configuration for the application.
Extracted from scrape_quarterlies.py to avoid code duplication.
"""

import logging
import colorama
from colorama import Fore, Back, Style
from typing import Optional
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels and components."""
    
    # Color mapping for different log levels
    LEVEL_COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize colorama for colored output
        colorama.init(autoreset=True)
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Split the log message into components
        parts = log_message.split(' - ')
        if len(parts) >= 4:
            timestamp = parts[0]
            logger_name = parts[1]
            level = parts[2]
            function_info = parts[3]
            message = ' - '.join(parts[4:]) if len(parts) > 4 else ''
            
            # Add emojis based on log level and message content
            emoji = self._get_emoji(record.levelname, message)
            
            # Color each component
            colored_timestamp = f"{Fore.BLUE}{timestamp}{Style.RESET_ALL}"
            colored_logger = f"{Fore.MAGENTA}{logger_name}{Style.RESET_ALL}"
            
            # Color the level based on its type
            level_color = self.LEVEL_COLORS.get(record.levelname, '')
            colored_level = f"{level_color}{level}{Style.RESET_ALL}"
            
            colored_function = f"{Fore.CYAN}{function_info}{Style.RESET_ALL}"
            colored_message = f"{level_color}{emoji} {message}{Style.RESET_ALL}"
            
            # Reconstruct the colored message
            colored_log_message = f"{colored_timestamp} - {colored_logger} - {colored_level} - {colored_function} - {colored_message}"
            return colored_log_message
        else:
            # Fallback: color the entire message based on level
            level_color = self.LEVEL_COLORS.get(record.levelname, '')
            emoji = self._get_emoji(record.levelname, log_message)
            if level_color:
                return f"{level_color}{emoji} {log_message}{Style.RESET_ALL}"
            return log_message
    
    def _get_emoji(self, level: str, message: str) -> str:
        """Get appropriate emoji based on log level and message content."""
        message_lower = message.lower()
        
        # Level-based emojis
        level_emojis = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        # Content-based emojis (override level emojis for specific messages)
        if any(word in message_lower for word in ['cik', 'ticker', 'looking up']):
            return '🔎'
        elif any(word in message_lower for word in ['found', 'successfully', 'saved', 'downloaded']):
            return '✅'
        elif any(word in message_lower for word in ['fetching', 'downloading', 'processing']):
            return '📥'
        elif any(word in message_lower for word in ['financial', 'income', 'balance', 'cash flow']):
            return '💰'
        elif any(word in message_lower for word in ['table', 'extracting', 'parsing']):
            return '📊'
        elif any(word in message_lower for word in ['error', 'failed', 'exception']):
            return '❌'
        elif any(word in message_lower for word in ['warning', 'caution', 'fallback']):
            return '⚠️'
        elif any(word in message_lower for word in ['starting', 'completed', 'finished']):
            return '🚀'
        elif any(word in message_lower for word in ['listing', 'available', 'documents']):
            return '📋'
        elif any(word in message_lower for word in ['network', 'connection', 'timeout']):
            return '🌐'
        elif any(word in message_lower for word in ['file', 'path', 'directory']):
            return '📁'
        elif any(word in message_lower for word in ['json', 'data', 'metadata']):
            return '📄'
        else:
            return level_emojis.get(level, 'ℹ️')


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, 
                 logger_name: str = "app") -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str, optional): Path to log file. If None, logs only to console.
        logger_name (str): Name of the logger instance
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    plain_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified) - use plain formatter for file
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(plain_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance. If no logger exists, create one with default settings.
    
    Args:
        name (str): Logger name. If None, uses the calling module's name.
    
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'app')
    
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up default logging
    if not logger.handlers:
        setup_logging(logger_name=name)
    
    return logger


# Global logger instance for backward compatibility
logger = get_logger("app")
