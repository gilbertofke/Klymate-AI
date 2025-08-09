"""
Password Utilities

This module provides utilities for password hashing and verification
using industry-standard bcrypt hashing.
"""

import logging
from typing import Optional
import bcrypt

logger = logging.getLogger(__name__)


class PasswordUtils:
    """Utilities for password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            logger.debug("Password hashed successfully")
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise ValueError(f"Password hashing failed: {str(e)}")
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches hash, False otherwise
        """
        if not password or not hashed_password:
            return False
        
        try:
            # Verify password against hash
            result = bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
            
            logger.debug(f"Password verification result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False
    
    @staticmethod
    def is_password_strong(password: str) -> tuple[bool, list[str]]:
        """
        Check if password meets security requirements.
        
        Args:
            password: Password to check
            
        Returns:
            Tuple of (is_strong: bool, issues: list[str])
        """
        issues = []
        
        if not password:
            issues.append("Password cannot be empty")
            return False, issues
        
        # Check minimum length
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        # Check for uppercase letter
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letter
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        # Check for digit
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        # Check for special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            issues.append("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master"
        ]
        if password.lower() in weak_passwords:
            issues.append("Password is too common and easily guessable")
        
        is_strong = len(issues) == 0
        return is_strong, issues
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a secure random token for password reset, etc.
        
        Args:
            length: Length of token to generate
            
        Returns:
            Secure random token string
        """
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        logger.debug(f"Generated secure token of length {length}")
        return token


# Example usage and testing functions
def example_password_operations():
    """Example of password hashing and verification operations."""
    
    # Example password
    password = "MySecurePassword123!"
    
    # Check password strength
    is_strong, issues = PasswordUtils.is_password_strong(password)
    print(f"Password strength check: {is_strong}")
    if issues:
        print(f"Issues: {issues}")
    
    # Hash password
    hashed = PasswordUtils.hash_password(password)
    print(f"Hashed password: {hashed[:50]}...")
    
    # Verify correct password
    is_valid = PasswordUtils.verify_password(password, hashed)
    print(f"Password verification (correct): {is_valid}")
    
    # Verify incorrect password
    is_valid = PasswordUtils.verify_password("WrongPassword", hashed)
    print(f"Password verification (incorrect): {is_valid}")
    
    # Generate secure token
    token = PasswordUtils.generate_secure_token()
    print(f"Secure token: {token}")


if __name__ == "__main__":
    example_password_operations()