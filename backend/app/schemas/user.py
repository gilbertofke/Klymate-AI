"""
User Schemas

Pydantic models for user data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.utils.password_utils import PasswordUtils


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: Optional[str] = None
    display_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: Optional[str] = Field(None, description="Password for local authentication (optional with Firebase)")
    firebase_uid: Optional[str] = Field(None, description="Firebase UID for Firebase authentication")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength if provided."""
        if v is not None:
            is_strong, issues = PasswordUtils.is_password_strong(v)
            if not is_strong:
                raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        return v
    
    @validator('firebase_uid')
    def validate_firebase_or_password(cls, v, values):
        """Ensure either Firebase UID or password is provided."""
        if not v and not values.get('password'):
            raise ValueError("Either firebase_uid or password must be provided")
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    name: Optional[str] = None
    display_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserPasswordUpdate(BaseModel):
    """Schema for password updates."""
    current_password: Optional[str] = Field(None, description="Current password (required for local auth)")
    new_password: str = Field(..., description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        is_strong, issues = PasswordUtils.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset requests."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate new password strength."""
        is_strong, issues = PasswordUtils.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        return v


class User(UserBase):
    """Schema for user responses."""
    id: int
    firebase_uid: Optional[str] = None
    email_verified: bool
    is_active: bool
    is_verified: bool
    onboarding_completed: bool
    last_login_at: Optional[datetime] = None
    login_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(User):
    """Extended user profile schema."""
    profile_picture_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserPublic(BaseModel):
    """Public user information schema (for leaderboards, etc.)."""
    id: int
    display_name: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True
