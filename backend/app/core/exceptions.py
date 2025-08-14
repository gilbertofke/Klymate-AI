"""
Core Exceptions

This module defines custom exception classes for the application.
"""

from typing import Optional, Dict, Any


class BaseApplicationError(Exception):
    """Base exception class for all application errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseApplicationError):
    """Raised when input validation fails"""
    pass


class NotFoundError(BaseApplicationError):
    """Raised when a requested resource is not found"""
    pass


class DatabaseError(BaseApplicationError):
    """Raised when database operations fail"""
    pass


class BusinessLogicError(BaseApplicationError):
    """Raised when business logic validation fails"""
    pass


class AuthenticationError(BaseApplicationError):
    """Raised when authentication fails"""
    pass


class AuthorizationError(BaseApplicationError):
    """Raised when authorization fails"""
    pass


class ExternalServiceError(BaseApplicationError):
    """Raised when external service calls fail"""
    pass


class ConfigurationError(BaseApplicationError):
    """Raised when configuration is invalid"""
    pass