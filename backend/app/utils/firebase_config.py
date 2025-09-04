"""
Firebase Admin SDK Configuration

This module handles Firebase Admin SDK initialization and configuration
for user authentication and token verification.
"""

import json
import logging
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings

logger = logging.getLogger(__name__)


class FirebaseConfig:
    """Firebase Admin SDK configuration and initialization."""
    
    _app: Optional[firebase_admin.App] = None
    _initialized: bool = False
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize Firebase Admin SDK with service account credentials."""
        if cls._initialized:
            logger.info("Firebase Admin SDK already initialized")
            return
        
        try:
            # Check if we have real Firebase credentials (not placeholder values)
            if (settings.FIREBASE_PROJECT_ID == "your_actual_project_id" or 
                "your_actual" in settings.FIREBASE_PROJECT_ID or
                "dev-key" in settings.FIREBASE_PRIVATE_KEY_ID):
                logger.warning("Firebase Admin SDK credentials are placeholder values. Skipping initialization.")
                cls._initialized = False
                return
            
            # Create service account credentials from environment variables
            service_account_info = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": settings.FIREBASE_AUTH_URI,
                "token_uri": settings.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
            }
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(service_account_info)
            cls._app = firebase_admin.initialize_app(cred)
            cls._initialized = True
            
            logger.info("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            cls._initialized = False
            # Don't raise the exception, just log it
    
    @classmethod
    def get_app(cls) -> firebase_admin.App:
        """Get the Firebase app instance."""
        if not cls._initialized:
            cls.initialize()
        return cls._app
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if Firebase Admin SDK is initialized."""
        return cls._initialized


# Initialize Firebase on module import (skip in test mode)
try:
    if not settings.TESTING_MODE:
        FirebaseConfig.initialize()
    else:
        logger.info("Skipping Firebase initialization in test mode")
except Exception as e:
    logger.warning(f"Firebase initialization failed on import: {str(e)}")