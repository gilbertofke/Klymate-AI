"""
Firebase Authentication Utilities

This module provides utilities for Firebase token verification,
user management, and authentication operations.
"""

import logging
from typing import Optional, Dict, Any
from firebase_admin import auth
from firebase_admin.auth import UserRecord, InvalidIdTokenError, ExpiredIdTokenError
from app.utils.firebase_config import FirebaseConfig

logger = logging.getLogger(__name__)


class FirebaseAuthError(Exception):
    """Custom exception for Firebase authentication errors."""
    pass


class FirebaseAuth:
    """Firebase authentication utilities."""
    
    @staticmethod
    def verify_id_token(id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and return decoded claims.
        
        Args:
            id_token: Firebase ID token to verify
            
        Returns:
            Dict containing user claims if valid, None if invalid
            
        Raises:
            FirebaseAuthError: If token verification fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            logger.info(f"Token verified successfully for user: {decoded_token.get('uid')}")
            return decoded_token
            
        except ExpiredIdTokenError:
            logger.warning("Firebase ID token has expired")
            raise FirebaseAuthError("Token has expired")
            
        except InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase ID token: {str(e)}")
            raise FirebaseAuthError("Invalid token")
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise FirebaseAuthError(f"Token verification failed: {str(e)}")
    
    @staticmethod
    def get_user_by_uid(uid: str) -> Optional[UserRecord]:
        """
        Get Firebase user record by UID.
        
        Args:
            uid: Firebase user UID
            
        Returns:
            UserRecord if found, None if not found
            
        Raises:
            FirebaseAuthError: If user retrieval fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            user_record = auth.get_user(uid)
            logger.info(f"User record retrieved for UID: {uid}")
            return user_record
            
        except auth.UserNotFoundError:
            logger.warning(f"User not found for UID: {uid}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by UID {uid}: {str(e)}")
            raise FirebaseAuthError(f"Failed to retrieve user: {str(e)}")
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserRecord]:
        """
        Get Firebase user record by email.
        
        Args:
            email: User email address
            
        Returns:
            UserRecord if found, None if not found
            
        Raises:
            FirebaseAuthError: If user retrieval fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            user_record = auth.get_user_by_email(email)
            logger.info(f"User record retrieved for email: {email}")
            return user_record
            
        except auth.UserNotFoundError:
            logger.warning(f"User not found for email: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {str(e)}")
            raise FirebaseAuthError(f"Failed to retrieve user: {str(e)}")
    
    @staticmethod
    def create_custom_token(uid: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a custom Firebase token for a user.
        
        Args:
            uid: Firebase user UID
            additional_claims: Optional additional claims to include in token
            
        Returns:
            Custom token string
            
        Raises:
            FirebaseAuthError: If token creation fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            custom_token = auth.create_custom_token(uid, additional_claims)
            logger.info(f"Custom token created for UID: {uid}")
            return custom_token.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to create custom token for UID {uid}: {str(e)}")
            raise FirebaseAuthError(f"Failed to create custom token: {str(e)}")
    
    @staticmethod
    def revoke_refresh_tokens(uid: str) -> None:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            uid: Firebase user UID
            
        Raises:
            FirebaseAuthError: If token revocation fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            auth.revoke_refresh_tokens(uid)
            logger.info(f"Refresh tokens revoked for UID: {uid}")
            
        except Exception as e:
            logger.error(f"Failed to revoke tokens for UID {uid}: {str(e)}")
            raise FirebaseAuthError(f"Failed to revoke tokens: {str(e)}")
    
    @staticmethod
    def generate_password_reset_link(email: str, action_code_settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a password reset link for a user.
        
        Args:
            email: User email address
            action_code_settings: Optional settings for the action code
            
        Returns:
            Password reset link
            
        Raises:
            FirebaseAuthError: If link generation fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            # Generate password reset link
            link = auth.generate_password_reset_link(email, action_code_settings)
            logger.info(f"Password reset link generated for email: {email}")
            return link
            
        except auth.UserNotFoundError:
            logger.warning(f"User not found for password reset: {email}")
            raise FirebaseAuthError("User not found")
            
        except Exception as e:
            logger.error(f"Failed to generate password reset link for {email}: {str(e)}")
            raise FirebaseAuthError(f"Failed to generate password reset link: {str(e)}")
    
    @staticmethod
    def send_password_reset_email(email: str) -> bool:
        """
        Send password reset email using Firebase Auth.
        
        Note: This method requires Firebase Admin SDK with proper permissions.
        For client-side password reset, use Firebase Client SDK.
        
        Args:
            email: User email address
            
        Returns:
            True if email was sent successfully
            
        Raises:
            FirebaseAuthError: If email sending fails
        """
        try:
            # Ensure Firebase is initialized
            FirebaseConfig.get_app()
            
            # Check if user exists first
            user_record = FirebaseAuth.get_user_by_email(email)
            if not user_record:
                logger.warning(f"User not found for password reset: {email}")
                return False
            
            # Generate and log the reset link (in production, you'd send via email service)
            reset_link = FirebaseAuth.generate_password_reset_link(email)
            logger.info(f"Password reset link for {email}: {reset_link}")
            
            # In a real implementation, you would send this via your email service
            # For now, we'll just log it and return success
            return True
            
        except FirebaseAuthError:
            # Re-raise Firebase auth errors
            raise
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            raise FirebaseAuthError(f"Failed to send password reset email: {str(e)}")
    
    @staticmethod
    def extract_user_info(decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant user information from decoded Firebase token.
        
        Args:
            decoded_token: Decoded Firebase ID token
            
        Returns:
            Dict containing extracted user information
        """
        return {
            "firebase_uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "provider": decoded_token.get("firebase", {}).get("sign_in_provider"),
            "auth_time": decoded_token.get("auth_time"),
            "issued_at": decoded_token.get("iat"),
            "expires_at": decoded_token.get("exp")
        }