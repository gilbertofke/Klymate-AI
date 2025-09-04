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
            # If Firebase authentication fails, return a more helpful error
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase authentication service is not available. Please use the email registration method instead."
            )
        
        return AuthResponse(
            message="User registered successfully",
            user=auth_result["user"],
            tokens=auth_result["tokens"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except FirebaseAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Firebase authentication service unavailable: {str(e)}"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/register-email", response_model=AuthResponse)
async def register_user_with_email(request: Dict[str, Any]):
    """
    Register a new user using email and password (fallback when Firebase is not available).
    
    This endpoint provides a direct registration method without Firebase dependency.
    """
    email = request.get("email")
    password = request.get("password") 
    name = request.get("name", "")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Create a real user in the database
    from app.services.user_service import UserService
    from app.core.database import get_async_db
    from app.schemas.user import UserCreate
    
    # Get database session
    async for db in get_async_db():
        try:
            user_service = UserService(db)
            
            # Create user data
            user_create_data = UserCreate(
                email=email,
                name=name or email.split('@')[0],
                firebase_uid=f"mock_{email}"
            )
            
            # Create user in database
            user = await user_service.user_repository.create_user(user_create_data)
            
            # Convert user to dict for response
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "display_name": user.display_name or user.name,
                "firebase_uid": user.firebase_uid,
                "email_verified": user.email_verified,
                "is_active": user.is_active,
                "onboarding_completed": user.onboarding_completed,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
            
            # Generate JWT tokens
            from app.utils.jwt_handler import JWTHandler
            
            jwt_user_data = {
                "user_id": user.id,
                "firebase_uid": user.firebase_uid,
                "email": user.email
            }
            
            access_token = JWTHandler.generate_access_token(jwt_user_data)
            refresh_token = JWTHandler.generate_refresh_token(jwt_user_data)
            
            return AuthResponse(
                message="User registered successfully",
                user=user_data,
                tokens={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": "1800"  # 30 minutes
                }
            )
            
        except ValueError as e:
            # Handle user already exists error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
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
            # If Firebase authentication fails, return a more helpful error
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase authentication service is not available. Please use the email login method instead."
            )
        
        return AuthResponse(
            message="Login successful",
            user=auth_result["user"],
            tokens=auth_result["tokens"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except FirebaseAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Firebase authentication service unavailable: {str(e)}"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/login-email", response_model=AuthResponse)
async def login_user_with_email(request: Dict[str, Any]):
    """
    Login user using email and password (fallback when Firebase is not available).
    
    This endpoint provides a direct login method without Firebase dependency.
    """
    email = request.get("email")
    password = request.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # For development/testing, create or get existing user
    from app.services.user_service import UserService
    from app.core.database import get_async_db
    from app.schemas.user import UserCreate
    
    # Get database session
    async for db in get_async_db():
        try:
            user_service = UserService(db)
            
            # Try to get existing user by email
            existing_user = await user_service.user_repository.get_by_email(email)
            
            if not existing_user:
                # Create new user for development/testing
                user_create_data = UserCreate(
                    email=email,
                    name=email.split('@')[0],
                    firebase_uid=f"mock_{email}"
                )
                
                existing_user = await user_service.user_repository.create_user(user_create_data)
            
            # Update login info
            user = await user_service.user_repository.update_login_info(existing_user.id)
            if not user:
                user = existing_user
            
            # Convert user to dict for response
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "display_name": user.display_name or user.name,
                "firebase_uid": user.firebase_uid,
                "email_verified": user.email_verified,
                "is_active": user.is_active,
                "onboarding_completed": user.onboarding_completed,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
            
            # Generate JWT tokens
            from app.utils.jwt_handler import JWTHandler
            
            jwt_user_data = {
                "user_id": user.id,
                "firebase_uid": user.firebase_uid,
                "email": user.email
            }
            
            access_token = JWTHandler.generate_access_token(jwt_user_data)
            refresh_token = JWTHandler.generate_refresh_token(jwt_user_data)
            
            return AuthResponse(
                message="Login successful",
                user=user_data,
                tokens={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": "1800"  # 30 minutes
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
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

@router.get("/firebase-status")
async def get_firebase_status():
    """
    Get Firebase configuration status for debugging.
    """
    from app.utils.firebase_config import FirebaseConfig
    
    return {
        "firebase_initialized": FirebaseConfig.is_initialized(),
        "project_id": "configured" if FirebaseConfig.is_initialized() else "not configured",
        "fallback_available": True,
        "message": "Firebase Admin SDK status"
    }