"""
Unit tests for JWT token handler utilities.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
import jwt
import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.utils.jwt_handler import JWTHandler, JWTError
from app.core.config import settings


class TestJWTHandler:
    """Test cases for JWTHandler class."""
    
    def test_generate_access_token_success(self):
        """Test successful access token generation."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        
        # Act
        token = JWTHandler.generate_access_token(user_data)
        
        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify contents
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        assert decoded['user_id'] == 'test_user_id'
        assert decoded['firebase_uid'] == 'test_firebase_uid'
        assert decoded['email'] == 'test@example.com'
        assert decoded['token_type'] == 'access'
        assert decoded['iss'] == 'klymate-ai-backend'
    
    def test_generate_refresh_token_success(self):
        """Test successful refresh token generation."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        
        # Act
        token = JWTHandler.generate_refresh_token(user_data)
        
        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify contents
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        assert decoded['user_id'] == 'test_user_id'
        assert decoded['firebase_uid'] == 'test_firebase_uid'
        assert decoded['email'] == 'test@example.com'
        assert decoded['token_type'] == 'refresh'
        assert decoded['iss'] == 'klymate-ai-backend'
    
    def test_verify_token_success(self):
        """Test successful token verification."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        token = JWTHandler.generate_access_token(user_data)
        
        # Act
        result = JWTHandler.verify_token(token, 'access')
        
        # Assert
        assert result is not None
        assert result['user_id'] == 'test_user_id'
        assert result['firebase_uid'] == 'test_firebase_uid'
        assert result['email'] == 'test@example.com'
        assert result['token_type'] == 'access'
    
    def test_verify_token_wrong_type(self):
        """Test token verification with wrong token type."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        access_token = JWTHandler.generate_access_token(user_data)
        
        # Act & Assert
        with pytest.raises(JWTError, match="Invalid token type"):
            JWTHandler.verify_token(access_token, 'refresh')
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        
        # Create expired token
        expires_at = datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago
        payload = {
            'user_id': user_data['user_id'],
            'firebase_uid': user_data['firebase_uid'],
            'email': user_data['email'],
            'token_type': 'access',
            'exp': expires_at,
            'iat': datetime.utcnow() - timedelta(minutes=2),
            'iss': 'klymate-ai-backend'
        }
        
        expired_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Act & Assert
        with pytest.raises(JWTError, match="Token has expired"):
            JWTHandler.verify_token(expired_token, 'access')
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        # Act & Assert
        with pytest.raises(JWTError, match="Invalid token"):
            JWTHandler.verify_token('invalid_token', 'access')
    
    def test_refresh_access_token_success(self):
        """Test successful token refresh."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        refresh_token = JWTHandler.generate_refresh_token(user_data)
        
        # Act
        result = JWTHandler.refresh_access_token(refresh_token)
        
        # Assert
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'bearer'
        
        # Verify new tokens are valid
        access_payload = JWTHandler.verify_token(result['access_token'], 'access')
        refresh_payload = JWTHandler.verify_token(result['refresh_token'], 'refresh')
        
        assert access_payload['user_id'] == 'test_user_id'
        assert refresh_payload['user_id'] == 'test_user_id'
    
    def test_refresh_access_token_invalid_refresh_token(self):
        """Test token refresh with invalid refresh token."""
        # Act & Assert
        with pytest.raises(JWTError):
            JWTHandler.refresh_access_token('invalid_refresh_token')
    
    def test_extract_user_from_token_success(self):
        """Test successful user extraction from token."""
        # Arrange
        user_data = {
            'user_id': 'test_user_id',
            'firebase_uid': 'test_firebase_uid',
            'email': 'test@example.com'
        }
        token = JWTHandler.generate_access_token(user_data)
        
        # Act
        result = JWTHandler.extract_user_from_token(token)
        
        # Assert
        assert result is not None
        assert result['user_id'] == 'test_user_id'
        assert result['firebase_uid'] == 'test_firebase_uid'
        assert result['email'] == 'test@example.com'
        assert result['token_type'] == 'access'
    
    def test_extract_user_from_token_invalid(self):
        """Test user extraction from invalid token."""
        # Act
        result = JWTHandler.extract_user_from_token('invalid_token')
        
        # Assert
        assert result is None