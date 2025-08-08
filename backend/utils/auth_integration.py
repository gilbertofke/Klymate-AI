"""
Authentication Integration Example

This module demonstrates how to integrate Firebase authentication
with JWT tokens for the Klymate AI backend.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from backend.utils.firebase_auth import FirebaseAuth, FirebaseAuthError
from backend.utils.jwt_handler import JWTHandler, JWTError

logger = logging.getLogger(__name__)


class AuthIntegration:
    """Integration layer for Firebase and JWT authentication."""
    
    @staticmethod
    def authenticate_user(firebase_token: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user using Firebase token and generate JWT tokens.
        
        Args:
            firebase_token: Firebase ID token from client
            
        Returns:
            Dict containing user info and JWT tokens, None if authentication fails
        """
        try:
            # Step 1: Verify Firebase token
            decoded_firebase_token = FirebaseAuth.verify_id_token(firebase_token)
            if not decoded_firebase_token:
                logger.warning("Firebase token verification failed")
                return None
            
            # Step 2: Extract user information
            user_info = FirebaseAuth.extract_user_info(decoded_firebase_token)
            
            # Step 3: Prepare user data for JWT (you would typically fetch from database)
            user_data = {
                "user_id": user_info["firebase_uid"],  # This would be your internal user ID
                "firebase_uid": user_info["firebase_uid"],
                "email": user_info["email"]
            }
            
            # Step 4: Generate JWT tokens
            access_token = JWTHandler.generate_access_token(user_data)
            refresh_token = JWTHandler.generate_refresh_token(user_data)
            
            # Step 5: Return complete authentication result
            return {
                "user": user_info,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"
                }
            }
            
        except (FirebaseAuthError, JWTError) as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            return None
    
    @staticmethod
    def validate_request_token(authorization_header: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token from request authorization header.
        
        Args:
            authorization_header: Authorization header value (e.g., "Bearer token")
            
        Returns:
            User information if token is valid, None otherwise
        """
        try:
            # Extract token from header
            if not authorization_header or not authorization_header.startswith("Bearer "):
                logger.warning("Invalid authorization header format")
                return None
            
            token = authorization_header.split(" ")[1]
            
            # Verify JWT token
            payload = JWTHandler.verify_token(token, "access")
            if not payload:
                logger.warning("JWT token verification failed")
                return None
            
            return {
                "user_id": payload.get("user_id"),
                "firebase_uid": payload.get("firebase_uid"),
                "email": payload.get("email")
            }
            
        except JWTError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected token validation error: {str(e)}")
            return None
    
    @staticmethod
    def refresh_user_tokens(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh user tokens using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token pair if successful, None otherwise
        """
        try:
            return JWTHandler.refresh_access_token(refresh_token)
            
        except JWTError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected token refresh error: {str(e)}")
            return None
    
    @staticmethod
    def logout_user(firebase_uid: str) -> bool:
        """
        Logout user by revoking Firebase refresh tokens.
        
        Args:
            firebase_uid: Firebase user UID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            FirebaseAuth.revoke_refresh_tokens(firebase_uid)
            logger.info(f"User logged out successfully: {firebase_uid}")
            return True
            
        except FirebaseAuthError as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected logout error: {str(e)}")
            return False


# Example usage functions for testing
def example_authentication_flow():
    """Example of complete authentication flow."""
    # This would typically be called from your API endpoints
    
    # 1. User sends Firebase token from frontend
    firebase_token = "firebase_id_token_from_client"
    
    # 2. Authenticate and get JWT tokens
    auth_result = AuthIntegration.authenticate_user(firebase_token)
    
    if auth_result:
        print("Authentication successful!")
        print(f"User: {auth_result['user']['email']}")
        print(f"Access Token: {auth_result['tokens']['access_token'][:50]}...")
        return auth_result
    else:
        print("Authentication failed!")
        return None


def example_request_validation():
    """Example of request token validation."""
    # This would typically be used in middleware
    
    authorization_header = "Bearer jwt_access_token_here"
    
    user_info = AuthIntegration.validate_request_token(authorization_header)
    
    if user_info:
        print("Request authorized!")
        print(f"User ID: {user_info['user_id']}")
        print(f"Email: {user_info['email']}")
        return user_info
    else:
        print("Request unauthorized!")
        return None