"""
User Models

This module defines the User model and related database structures
for the Klymate AI application.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, SoftDeleteMixin, AuditMixin
from app.utils.password_utils import PasswordUtils


class User(BaseModel, SoftDeleteMixin, AuditMixin):
    """User model for storing user account information."""
    
    __tablename__ = "users"
    
    # Firebase integration
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    name = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    
    # Profile information
    profile_picture_url = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Authentication metadata
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Password reset (for local auth if needed)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
    
    # Local password hash (backup/alternative auth)
    password_hash = Column(String(255), nullable=True)
    
    # Onboarding and preferences
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    
    def set_password(self, password: str) -> None:
        """
        Set user password with proper hashing.
        
        Args:
            password: Plain text password to hash and store
            
        Raises:
            ValueError: If password doesn't meet security requirements
        """
        # Check password strength
        is_strong, issues = PasswordUtils.is_password_strong(password)
        if not is_strong:
            raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        
        # Hash and store password
        self.password_hash = PasswordUtils.hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        if not self.password_hash:
            return False
        
        return PasswordUtils.verify_password(password, self.password_hash)
    
    def set_password_reset_token(self) -> str:
        """
        Generate and set password reset token.
        
        Returns:
            Generated reset token
        """
        token = PasswordUtils.generate_secure_token(64)
        self.password_reset_token = token
        # Token expires in 1 hour
        self.password_reset_expires_at = datetime.utcnow().replace(
            hour=datetime.utcnow().hour + 1
        )
        return token
    
    def clear_password_reset_token(self) -> None:
        """Clear password reset token after use."""
        self.password_reset_token = None
        self.password_reset_expires_at = None
    
    def is_password_reset_token_valid(self, token: str) -> bool:
        """
        Check if password reset token is valid.
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid and not expired
        """
        if not self.password_reset_token or not self.password_reset_expires_at:
            return False
        
        if self.password_reset_token != token:
            return False
        
        if datetime.utcnow() > self.password_reset_expires_at:
            return False
        
        return True
    
    def update_login_info(self) -> None:
        """Update login information."""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1
    
    def complete_onboarding(self) -> None:
        """Mark user onboarding as completed."""
        self.onboarding_completed = True
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, firebase_uid={self.firebase_uid})>"
