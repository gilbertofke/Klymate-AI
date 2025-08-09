"""
Unit Tests for User Model

This module contains comprehensive tests for the User model,
including validation, methods, and database operations.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import json

from app.models.user import User
from app.utils.password_utils import PasswordUtils


class TestUserModel:
    """Test cases for User model functionality."""
    
    def test_user_creation_with_required_fields(self, db_session):
        """Test creating user with minimum required fields."""
        user = User(
            firebase_uid="test_firebase_uid_123",
            email="test@example.com"
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.firebase_uid == "test_firebase_uid_123"
        assert user.email == "test@example.com"
        assert user.is_active is True  # Default value
        assert user.is_verified is False  # Default value
        assert user.onboarding_completed is False  # Default value
        assert user.login_count == 0  # Default value
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_creation_with_all_fields(self, db_session):
        """Test creating user with all fields populated."""
        user = User(
            firebase_uid="test_firebase_uid_456",
            email="fulluser@example.com",
            email_verified=True,
            name="John Doe",
            display_name="Johnny",
            profile_picture_url="https://example.com/avatar.jpg",
            location="San Francisco, CA",
            bio="Environmental enthusiast",
            is_active=True,
            is_verified=True,
            baseline_footprint=7500.50,
            onboarding_completed=True,
            preferences='{"theme": "dark", "notifications": true}'
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.firebase_uid == "test_firebase_uid_456"
        assert user.email == "fulluser@example.com"
        assert user.email_verified is True
        assert user.name == "John Doe"
        assert user.display_name == "Johnny"
        assert user.profile_picture_url == "https://example.com/avatar.jpg"
        assert user.location == "San Francisco, CA"
        assert user.bio == "Environmental enthusiast"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.baseline_footprint == 7500.50
        assert user.onboarding_completed is True
        assert user.preferences == '{"theme": "dark", "notifications": true}'
    
    def test_user_unique_constraints(self, db_session):
        """Test that unique constraints are enforced."""
        # Create first user
        user1 = User(
            firebase_uid="unique_firebase_uid",
            email="unique@example.com"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create user with same Firebase UID
        user2 = User(
            firebase_uid="unique_firebase_uid",
            email="different@example.com"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create user with same email
        user3 = User(
            firebase_uid="different_firebase_uid",
            email="unique@example.com"
        )
        db_session.add(user3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_set_password_method(self, db_session):
        """Test password setting with validation."""
        user = User(
            firebase_uid="password_test_uid",
            email="password@example.com"
        )
        
        # Test setting strong password
        strong_password = "StrongPassword123!"
        user.set_password(strong_password)
        
        assert user.password_hash is not None
        assert user.password_hash != strong_password  # Should be hashed
        assert len(user.password_hash) > 50  # bcrypt hashes are long
        
        # Test setting weak password should raise error
        with pytest.raises(ValueError, match="Password does not meet security requirements"):
            user.set_password("weak")
    
    def test_verify_password_method(self, db_session):
        """Test password verification."""
        user = User(
            firebase_uid="verify_password_uid",
            email="verify@example.com"
        )
        
        password = "TestPassword123!"
        user.set_password(password)
        
        # Test correct password
        assert user.verify_password(password) is True
        
        # Test incorrect password
        assert user.verify_password("WrongPassword123!") is False
        
        # Test with no password set
        user_no_password = User(
            firebase_uid="no_password_uid",
            email="nopassword@example.com"
        )
        assert user_no_password.verify_password("anypassword") is False
    
    def test_password_reset_token_methods(self, db_session):
        """Test password reset token functionality."""
        user = User(
            firebase_uid="reset_token_uid",
            email="reset@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        # Test setting password reset token
        token = user.set_password_reset_token()
        
        assert token is not None
        assert len(token) == 64  # Token length
        assert user.password_reset_token == token
        assert user.password_reset_expires_at is not None
        
        # Test token validation
        assert user.is_password_reset_token_valid(token) is True
        assert user.is_password_reset_token_valid("invalid_token") is False
        
        # Test token expiration
        user.password_reset_expires_at = datetime.utcnow() - timedelta(hours=2)
        assert user.is_password_reset_token_valid(token) is False
        
        # Test clearing token
        user.clear_password_reset_token()
        assert user.password_reset_token is None
        assert user.password_reset_expires_at is None
    
    def test_update_login_info_method(self, db_session):
        """Test login information update."""
        user = User(
            firebase_uid="login_info_uid",
            email="logininfo@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        initial_login_count = user.login_count
        initial_last_login = user.last_login_at
        
        # Update login info
        user.update_login_info()
        
        assert user.login_count == initial_login_count + 1
        assert user.last_login_at is not None
        assert user.last_login_at != initial_last_login
    
    def test_complete_onboarding_method(self, db_session):
        """Test onboarding completion."""
        user = User(
            firebase_uid="onboarding_uid",
            email="onboarding@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.onboarding_completed is False
        
        user.complete_onboarding()
        
        assert user.onboarding_completed is True
    
    def test_soft_delete_functionality(self, db_session):
        """Test soft delete mixin functionality."""
        user = User(
            firebase_uid="soft_delete_uid",
            email="softdelete@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.is_deleted is False
        assert user.deleted_at is None
        
        # Soft delete
        user.soft_delete()
        
        assert user.is_deleted is True
        assert user.deleted_at is not None
        
        # Restore
        user.restore()
        
        assert user.is_deleted is False
        assert user.deleted_at is None
    
    def test_to_dict_method(self, db_session):
        """Test model to dictionary conversion."""
        user = User(
            firebase_uid="to_dict_uid",
            email="todict@example.com",
            name="Test User",
            baseline_footprint=5000.0
        )
        db_session.add(user)
        db_session.commit()
        
        user_dict = user.to_dict()
        
        assert isinstance(user_dict, dict)
        assert user_dict["firebase_uid"] == "to_dict_uid"
        assert user_dict["email"] == "todict@example.com"
        assert user_dict["name"] == "Test User"
        assert user_dict["baseline_footprint"] == 5000.0
        assert "id" in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
    
    def test_update_from_dict_method(self, db_session):
        """Test updating model from dictionary."""
        user = User(
            firebase_uid="update_dict_uid",
            email="updatedict@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        update_data = {
            "name": "Updated Name",
            "location": "New York, NY",
            "bio": "Updated bio",
            "baseline_footprint": 6000.0
        }
        
        user.update_from_dict(update_data)
        
        assert user.name == "Updated Name"
        assert user.location == "New York, NY"
        assert user.bio == "Updated bio"
        assert user.baseline_footprint == 6000.0
        
        # Test that non-existent fields are ignored
        invalid_update = {"non_existent_field": "value"}
        user.update_from_dict(invalid_update)  # Should not raise error
    
    def test_repr_method(self, db_session):
        """Test string representation of user."""
        user = User(
            firebase_uid="repr_uid",
            email="repr@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        repr_str = repr(user)
        
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert "repr@example.com" in repr_str
        assert "repr_uid" in repr_str
    
    def test_timestamp_fields(self, db_session):
        """Test that timestamp fields are automatically set."""
        user = User(
            firebase_uid="timestamp_uid",
            email="timestamp@example.com"
        )
        
        # Before saving
        assert user.created_at is None
        assert user.updated_at is None
        
        db_session.add(user)
        db_session.commit()
        
        # After saving
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        
        # Test updated_at changes on update
        original_updated_at = user.updated_at
        user.name = "Updated Name"
        db_session.commit()
        
        assert user.updated_at > original_updated_at
    
    def test_audit_fields(self, db_session):
        """Test audit mixin functionality."""
        user = User(
            firebase_uid="audit_uid",
            email="audit@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        # Test setting created_by
        user.set_created_by("admin_user_123")
        assert user.created_by == "admin_user_123"
        
        # Test setting updated_by
        user.set_updated_by("editor_user_456")
        assert user.updated_by == "editor_user_456"
    
    def test_preferences_json_handling(self, db_session):
        """Test handling of JSON preferences field."""
        user = User(
            firebase_uid="json_uid",
            email="json@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        # Test setting valid JSON
        preferences = {
            "theme": "dark",
            "notifications": {
                "email": True,
                "push": False
            },
            "language": "en"
        }
        user.preferences = json.dumps(preferences)
        db_session.commit()
        
        # Test retrieving and parsing JSON
        retrieved_user = db_session.query(User).filter_by(id=user.id).first()
        parsed_preferences = json.loads(retrieved_user.preferences)
        
        assert parsed_preferences["theme"] == "dark"
        assert parsed_preferences["notifications"]["email"] is True
        assert parsed_preferences["language"] == "en"
    
    def test_baseline_footprint_validation(self, db_session):
        """Test baseline footprint field validation."""
        user = User(
            firebase_uid="footprint_uid",
            email="footprint@example.com"
        )
        
        # Test setting valid footprint
        user.baseline_footprint = 7500.50
        db_session.add(user)
        db_session.commit()
        
        assert user.baseline_footprint == 7500.50
        
        # Test setting zero footprint
        user.baseline_footprint = 0.0
        db_session.commit()
        
        assert user.baseline_footprint == 0.0
        
        # Test setting negative footprint (should be allowed for offsets)
        user.baseline_footprint = -100.0
        db_session.commit()
        
        assert user.baseline_footprint == -100.0