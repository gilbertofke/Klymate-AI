"""
Tests for Password Utilities

This module contains tests for password hashing, verification,
and security validation functionality.
"""

import pytest
from app.utils.password_utils import PasswordUtils


class TestPasswordUtils:
    """Test cases for PasswordUtils class."""
    
    def test_hash_password_success(self):
        """Test successful password hashing."""
        password = "TestPassword123!"
        hashed = PasswordUtils.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Ensure it's actually hashed
    
    def test_hash_password_empty_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            PasswordUtils.hash_password("")
        
        with pytest.raises(ValueError, match="Password cannot be empty"):
            PasswordUtils.hash_password(None)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = PasswordUtils.hash_password(password)
        
        assert PasswordUtils.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = PasswordUtils.hash_password(password)
        
        assert PasswordUtils.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        assert PasswordUtils.verify_password("", "hash") is False
        assert PasswordUtils.verify_password("password", "") is False
        assert PasswordUtils.verify_password(None, "hash") is False
        assert PasswordUtils.verify_password("password", None) is False
    
    def test_is_password_strong_valid(self):
        """Test password strength validation with strong password."""
        strong_password = "MySecurePassword123!"
        is_strong, issues = PasswordUtils.is_password_strong(strong_password)
        
        assert is_strong is True
        assert len(issues) == 0
    
    def test_is_password_strong_too_short(self):
        """Test password strength validation with short password."""
        short_password = "Abc1!"
        is_strong, issues = PasswordUtils.is_password_strong(short_password)
        
        assert is_strong is False
        assert "Password must be at least 8 characters long" in issues
    
    def test_is_password_strong_no_uppercase(self):
        """Test password strength validation without uppercase."""
        password = "mysecurepassword123!"
        is_strong, issues = PasswordUtils.is_password_strong(password)
        
        assert is_strong is False
        assert "Password must contain at least one uppercase letter" in issues
    
    def test_is_password_strong_no_lowercase(self):
        """Test password strength validation without lowercase."""
        password = "MYSECUREPASSWORD123!"
        is_strong, issues = PasswordUtils.is_password_strong(password)
        
        assert is_strong is False
        assert "Password must contain at least one lowercase letter" in issues
    
    def test_is_password_strong_no_digit(self):
        """Test password strength validation without digit."""
        password = "MySecurePassword!"
        is_strong, issues = PasswordUtils.is_password_strong(password)
        
        assert is_strong is False
        assert "Password must contain at least one digit" in issues
    
    def test_is_password_strong_no_special_char(self):
        """Test password strength validation without special character."""
        password = "MySecurePassword123"
        is_strong, issues = PasswordUtils.is_password_strong(password)
        
        assert is_strong is False
        assert "Password must contain at least one special character" in issues
    
    def test_is_password_strong_common_password(self):
        """Test password strength validation with common password."""
        common_password = "password123"
        is_strong, issues = PasswordUtils.is_password_strong(common_password)
        
        assert is_strong is False
        assert "Password is too common and easily guessable" in issues
    
    def test_is_password_strong_empty(self):
        """Test password strength validation with empty password."""
        is_strong, issues = PasswordUtils.is_password_strong("")
        
        assert is_strong is False
        assert "Password cannot be empty" in issues
        
        is_strong, issues = PasswordUtils.is_password_strong(None)
        
        assert is_strong is False
        assert "Password cannot be empty" in issues
    
    def test_generate_secure_token_default_length(self):
        """Test secure token generation with default length."""
        token = PasswordUtils.generate_secure_token()
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) == 32  # Default length
        assert token.isalnum()  # Should only contain letters and digits
    
    def test_generate_secure_token_custom_length(self):
        """Test secure token generation with custom length."""
        length = 64
        token = PasswordUtils.generate_secure_token(length)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) == length
        assert token.isalnum()
    
    def test_generate_secure_token_uniqueness(self):
        """Test that generated tokens are unique."""
        token1 = PasswordUtils.generate_secure_token()
        token2 = PasswordUtils.generate_secure_token()
        
        assert token1 != token2
    
    def test_password_hashing_consistency(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "TestPassword123!"
        hash1 = PasswordUtils.hash_password(password)
        hash2 = PasswordUtils.hash_password(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert PasswordUtils.verify_password(password, hash1) is True
        assert PasswordUtils.verify_password(password, hash2) is True


if __name__ == "__main__":
    pytest.main([__file__])