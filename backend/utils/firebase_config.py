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
from backend.config import settings

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
            # Create service account credentials from environment variables
            service_account_info = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key_id": settings.firebase_private_key_id,
                "private_key": settings.firebase_private_key.replace('\\n', '\n'),
                "client_email": settings.firebase_client_email,
                "client_id": settings.firebase_client_id,
                "auth_uri": settings.firebase_auth_uri,
                "token_uri": settings.firebase_token_uri,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.firebase_client_email}"
            }
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(service_account_info)
            cls._app = firebase_admin.initialize_app(cred)
            cls._initialized = True
            
            logger.info("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise
    
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


# Initialize Firebase on module import
try:
    FirebaseConfig.initialize()
except Exception as e:
    logger.warning(f"Firebase initialization failed on import: {str(e)}")