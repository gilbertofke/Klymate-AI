"""
Unit tests for Firebase authentication utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    from backend.utils.firebase_auth import FirebaseAuth, FirebaseAuthError
    from backend.utils.firebase_config import FirebaseConfig
except ImportError:
    # Fallback for different environments
    from utils.firebase_auth import FirebaseAuth, FirebaseAuthError
    from utils.firebase_config import FirebaseConfig


class TestFirebaseAuth:
    """Test cases for FirebaseAuth class."""
    
    @patch('backend.utils.firebase_auth.auth.verify_id_token')
    @patch.object(FirebaseConfig, 'get_app')
    def test_verify_id_token_success(self, mock_get_app, mock_verify_token):
        """Test successful token verification."""
        # Arrange
        mock_get_app.return_value = Mock()
        mock_decoded_token = {
            'uid': 'test_uid',
            'email': 'test@example.com',
            'email_verified': True
        }
        mock_verify_token.return_value = mock_decoded_token
        
        # Act
        result = FirebaseAuth.verify_id_token('valid_token')
        
        # Assert
        assert result == mock_decoded_token
        mock_verify_token.assert_called_once_with('valid_token')
    
    @patch('backend.utils.firebase_auth.auth.verify_id_token')
    @patch.object(FirebaseConfig, 'get_app')
    def test_verify_id_token_expired(self, mock_get_app, mock_verify_token):
        """Test token verification with expired token."""
        # Arrange
        mock_get_app.return_value = Mock()
        from firebase_admin.auth import ExpiredIdTokenError
        mock_verify_token.side_effect = ExpiredIdTokenError('Token expired', None)
        
        # Act & Assert
        with pytest.raises(FirebaseAuthError, match="Token has expired"):
            FirebaseAuth.verify_id_token('expired_token')
    
    @patch('backend.utils.firebase_auth.auth.verify_id_token')
    @patch.object(FirebaseConfig, 'get_app')
    def test_verify_id_token_invalid(self, mock_get_app, mock_verify_token):
        """Test token verification with invalid token."""
        # Arrange
        mock_get_app.return_value = Mock()
        from firebase_admin.auth import InvalidIdTokenError
        mock_verify_token.side_effect = InvalidIdTokenError('Invalid token', None)
        
        # Act & Assert
        with pytest.raises(FirebaseAuthError, match="Invalid token"):
            FirebaseAuth.verify_id_token('invalid_token')
    
    @patch('backend.utils.firebase_auth.auth.get_user')
    @patch.object(FirebaseConfig, 'get_app')
    def test_get_user_by_uid_success(self, mock_get_app, mock_get_user):
        """Test successful user retrieval by UID."""
        # Arrange
        mock_get_app.return_value = Mock()
        mock_user_record = Mock()
        mock_user_record.uid = 'test_uid'
        mock_user_record.email = 'test@example.com'
        mock_get_user.return_value = mock_user_record
        
        # Act
        result = FirebaseAuth.get_user_by_uid('test_uid')
        
        # Assert
        assert result == mock_user_record
        mock_get_user.assert_called_once_with('test_uid')
    
    @patch('backend.utils.firebase_auth.auth.get_user')
    @patch.object(FirebaseConfig, 'get_app')
    def test_get_user_by_uid_not_found(self, mock_get_app, mock_get_user):
        """Test user retrieval with non-existent UID."""
        # Arrange
        mock_get_app.return_value = Mock()
        from firebase_admin.auth import UserNotFoundError
        mock_get_user.side_effect = UserNotFoundError('User not found')
        
        # Act
        result = FirebaseAuth.get_user_by_uid('nonexistent_uid')
        
        # Assert
        assert result is None
    
    @patch('backend.utils.firebase_auth.auth.get_user_by_email')
    @patch.object(FirebaseConfig, 'get_app')
    def test_get_user_by_email_success(self, mock_get_app, mock_get_user_by_email):
        """Test successful user retrieval by email."""
        # Arrange
        mock_get_app.return_value = Mock()
        mock_user_record = Mock()
        mock_user_record.uid = 'test_uid'
        mock_user_record.email = 'test@example.com'
        mock_get_user_by_email.return_value = mock_user_record
        
        # Act
        result = FirebaseAuth.get_user_by_email('test@example.com')
        
        # Assert
        assert result == mock_user_record
        mock_get_user_by_email.assert_called_once_with('test@example.com')
    
    @patch('backend.utils.firebase_auth.auth.create_custom_token')
    @patch.object(FirebaseConfig, 'get_app')
    def test_create_custom_token_success(self, mock_get_app, mock_create_token):
        """Test successful custom token creation."""
        # Arrange
        mock_get_app.return_value = Mock()
        mock_create_token.return_value = b'custom_token_bytes'
        
        # Act
        result = FirebaseAuth.create_custom_token('test_uid')
        
        # Assert
        assert result == 'custom_token_bytes'
        mock_create_token.assert_called_once_with('test_uid', None)
    
    def test_extract_user_info(self):
        """Test user information extraction from decoded token."""
        # Arrange
        decoded_token = {
            'uid': 'test_uid',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'picture': 'https://example.com/photo.jpg',
            'firebase': {'sign_in_provider': 'google.com'},
            'auth_time': 1640995200,
            'iat': 1640995200,
            'exp': 1640998800
        }
        
        # Act
        result = FirebaseAuth.extract_user_info(decoded_token)
        
        # Assert
        expected = {
            'firebase_uid': 'test_uid',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'picture': 'https://example.com/photo.jpg',
            'provider': 'google.com',
            'auth_time': 1640995200,
            'issued_at': 1640995200,
            'expires_at': 1640998800
        }
        assert result == expected