"""
Authentication endpoints using Tangus's comprehensive Firebase/JWT system.

This module provides authentication endpoints that integrate with the
comprehensive authentication system built by Tangus.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
import sys
import os

# Import Tangus's comprehensive authentication system
from app.utils.auth_integration import AuthIntegration
from app.utils.firebase_auth import FirebaseAuthError
from app.utils.jwt_handler import JWTError
from app.core.middleware import get_current_user

router = APIRouter()

# Request/Response Models
class FirebaseTokenRequest(BaseModel):
    """Request model for Firebase token authentication."""
    firebase_token: str

class AuthResponse(BaseModel):
    """Response model for successful authentication."""
    message: str
    user: Dict[str, Any]
    tokens: Dict[str, str]

class TokenRefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Request model for password reset."""
    email: EmailStr

class PasswordResetResponse(BaseModel):
    """Response model for password reset."""
    message: str
    success: bool

class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    user_id: str
    firebase_uid: str
    email: str

@router.post("/register", response_model=AuthResponse)
async def register_user(request: FirebaseTokenRequest):
    """
    Register a new user using Firebase token.
    
    This endpoint uses Tangus's comprehensive authentication system
    to verify Firebase tokens and generate JWT tokens.
    """
    try:
        # Use Tangus's authentication integration
        auth_result = AuthIntegration.authenticate_user(request.firebase_token)
        
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )
        
        return AuthResponse(
            message="User registered successfully",
            user=auth_result["user"],
            tokens=auth_result["tokens"]
        )
        
    except FirebaseAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(request: FirebaseTokenRequest):
    """
    Login user using Firebase token.
    
    This endpoint uses Tangus's comprehensive authentication system
    to verify Firebase tokens and generate JWT tokens.
    """
    try:
        # Use Tangus's authentication integration
        auth_result = AuthIntegration.authenticate_user(request.firebase_token)
        
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )
        
        return AuthResponse(
            message="Login successful",
            user=auth_result["user"],
            tokens=auth_result["tokens"]
        )
        
    except FirebaseAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh")
async def refresh_tokens(request: TokenRefreshRequest):
    """
    Refresh access token using refresh token.
    
    Uses Tangus's comprehensive JWT token refresh system.
    """
    try:
        # Use Tangus's token refresh system
        new_tokens = AuthIntegration.refresh_user_tokens(request.refresh_token)
        
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "message": "Tokens refreshed successfully",
            "tokens": new_tokens
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile.
    
    This endpoint is protected by Tangus's authentication middleware.
    """
    return UserProfileResponse(
        user_id=current_user["user_id"],
        firebase_uid=current_user["firebase_uid"],
        email=current_user["email"]
    )

@router.post("/password-reset", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """
    Request password reset email via Firebase.
    
    This endpoint triggers Firebase to send a password reset email
    to the user's registered email address.
    """
    try:
        # Use Firebase's password reset functionality
        success = AuthIntegration.request_password_reset(request.email)
        
        if success:
            return PasswordResetResponse(
                message="Password reset email sent successfully",
                success=True
            )
        else:
            # For security, we don't reveal if email exists or not
            return PasswordResetResponse(
                message="If the email exists in our system, a password reset link has been sent",
                success=True
            )
            
    except Exception as e:
        # For security, we don't reveal specific errors
        return PasswordResetResponse(
            message="If the email exists in our system, a password reset link has been sent",
            success=True
        )

@router.post("/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user by revoking Firebase refresh tokens.
    
    Uses Tangus's comprehensive logout system.
    """
    try:
        # Use Tangus's logout system
        success = AuthIntegration.logout_user(current_user["firebase_uid"])
        
        if success:
            return {"message": "Logout successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )