"""
Custom exceptions for the application.
"""


class AppException(Exception):
    """Base exception for the application."""
    pass


class ConfigurationError(AppException):
    """Raised when there's a configuration error."""
    pass


class DataCollectionError(AppException):
    """Raised when data collection fails."""
    pass


class ProcessingError(AppException):
    """Raised when data processing fails."""
    pass


class StorageError(AppException):
    """Raised when data storage operations fail."""
    pass


class APIError(AppException):
    """Raised when external API calls fail."""
    pass


class ValidationError(AppException):
    """Raised when data validation fails."""
    pass
