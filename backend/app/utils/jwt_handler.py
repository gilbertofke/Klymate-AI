"""
JWT Token Handler

This module provides utilities for generating and validating JWT tokens
for internal application authentication after Firebase verification.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.core.config import settings

logger = logging.getLogger(__name__)


class JWTError(Exception):
    """Custom exception for JWT operations."""
    pass


class JWTHandler:
    """JWT token generation and validation utilities."""
    
    @staticmethod
    def generate_access_token(user_data: Dict[str, Any]) -> str:
        """
        Generate JWT access token for authenticated user.
        
        Args:
            user_data: User information to encode in token
            
        Returns:
            JWT access token string
            
        Raises:
            JWTError: If token generation fails
        """
        try:
            # Set token expiration
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
            # Create token payload
            payload = {
                "user_id": user_data.get("user_id"),
                "firebase_uid": user_data.get("firebase_uid"),
                "email": user_data.get("email"),
                "token_type": "access",
                "exp": expires_at,
                "iat": datetime.utcnow(),
                "iss": "klymate-ai-backend"
            }
            
            # Generate token
            token = jwt.encode(
                payload,
                settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )
            
            logger.info(f"Access token generated for user: {user_data.get('email')}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate access token: {str(e)}")
            raise JWTError(f"Token generation failed: {str(e)}")
    
    @staticmethod
    def generate_refresh_token(user_data: Dict[str, Any]) -> str:
        """
        Generate JWT refresh token for authenticated user.
        
        Args:
            user_data: User information to encode in token
            
        Returns:
            JWT refresh token string
            
        Raises:
            JWTError: If token generation fails
        """
        try:
            # Set token expiration
            expires_at = datetime.utcnow() + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            
            # Create token payload
            payload = {
                "user_id": user_data.get("user_id"),
                "firebase_uid": user_data.get("firebase_uid"),
                "email": user_data.get("email"),
                "token_type": "refresh",
                "exp": expires_at,
                "iat": datetime.utcnow(),
                "iss": "klymate-ai-backend"
            }
            
            # Generate token
            token = jwt.encode(
                payload,
                settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )
            
            logger.info(f"Refresh token generated for user: {user_data.get('email')}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate refresh token: {str(e)}")
            raise JWTError(f"Refresh token generation failed: {str(e)}")
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            Decoded token payload if valid, None if invalid
            
        Raises:
            JWTError: If token verification fails
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                issuer="klymate-ai-backend"
            )
            
            # Verify token type
            if payload.get("token_type") != token_type:
                raise JWTError(f"Invalid token type. Expected: {token_type}")
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise JWTError("Token has expired")
            
            logger.info(f"Token verified successfully for user: {payload.get('email')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise JWTError("Token has expired")
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise JWTError("Invalid token")
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise JWTError(f"Token verification failed: {str(e)}")
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict containing new access token and refresh token
            
        Raises:
            JWTError: If token refresh fails
        """
        try:
            # Verify refresh token
            payload = JWTHandler.verify_token(refresh_token, "refresh")
            
            if not payload:
                raise JWTError("Invalid refresh token")
            
            # Extract user data
            user_data = {
                "user_id": payload.get("user_id"),
                "firebase_uid": payload.get("firebase_uid"),
                "email": payload.get("email")
            }
            
            # Generate new tokens
            new_access_token = JWTHandler.generate_access_token(user_data)
            new_refresh_token = JWTHandler.generate_refresh_token(user_data)
            
            logger.info(f"Tokens refreshed for user: {user_data.get('email')}")
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise JWTError(f"Token refresh failed: {str(e)}")
    
    @staticmethod
    def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from JWT token without full verification.
        Useful for getting user info from potentially expired tokens.
        
        Args:
            token: JWT token to decode
            
        Returns:
            User information if extractable, None otherwise
        """
        try:
            # Decode without verification (for expired tokens)
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            return {
                "user_id": payload.get("user_id"),
                "firebase_uid": payload.get("firebase_uid"),
                "email": payload.get("email"),
                "token_type": payload.get("token_type")
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract user from token: {str(e)}")
            return None