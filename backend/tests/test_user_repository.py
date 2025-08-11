"""
Unit Tests for User Repository

This module contains comprehensive tests for the UserRepository class,
including CRUD operations, search functionality, and statistics.
"""

import pytest
from datetime import datetime, timedelta
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate


class TestUserRepository:
    """Test cases for UserRepository functionality."""
    
    @pytest.fixture
    async def user_repository(self, async_db_session):
        """Create UserRepository instance for testing."""
        return UserRepository(async_db_session)
    
    @pytest.fixture
    async def sample_user_data(self):
        """Sample user data for testing."""
        return UserCreate(
            firebase_uid="test_firebase_uid_123",
            email="test@example.com",
            name="Test User",
            display_name="Tester"
        )
    
    async def test_create_user_success(self, user_repository, sample_user_data):
        """Test successful user creation."""
        user = await user_repository.create_user(sample_user_data)
        
        assert user.id is not None
        assert user.firebase_uid == "test_firebase_uid_123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.display_name == "Tester"
        assert user.is_active is True
        assert user.onboarding_completed is False
        assert user.login_count == 0
    
    async def test_create_user_duplicate_email(self, user_repository, sample_user_data):
        """Test creating user with duplicate email raises error."""
        # Create first user
        await user_repository.create_user(sample_user_data)
        
        # Try to create user with same email
        duplicate_user_data = UserCreate(
            firebase_uid="different_firebase_uid",
            email="test@example.com",  # Same email
            name="Different User"
        )
        
        with pytest.raises(ValueError, match="User with email test@example.com already exists"):
            await user_repository.create_user(duplicate_user_data)
    
    async def test_create_user_duplicate_firebase_uid(self, user_repository, sample_user_data):
        """Test creating user with duplicate Firebase UID raises error."""
        # Create first user
        await user_repository.create_user(sample_user_data)
        
        # Try to create user with same Firebase UID
        duplicate_user_data = UserCreate(
            firebase_uid="test_firebase_uid_123",  # Same Firebase UID
            email="different@example.com",
            name="Different User"
        )
        
        with pytest.raises(ValueError, match="User with Firebase UID test_firebase_uid_123 already exists"):
            await user_repository.create_user(duplicate_user_data)
    
    async def test_get_by_email(self, user_repository, sample_user_data):
        """Test getting user by email."""
        # Create user
        created_user = await user_repository.create_user(sample_user_data)
        
        # Get by email
        found_user = await user_repository.get_by_email("test@example.com")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"
        
        # Test case insensitive search
        found_user_upper = await user_repository.get_by_email("TEST@EXAMPLE.COM")
        assert found_user_upper is not None
        assert found_user_upper.id == created_user.id
        
        # Test non-existent email
        not_found = await user_repository.get_by_email("nonexistent@example.com")
        assert not_found is None
    
    async def test_get_by_firebase_uid(self, user_repository, sample_user_data):
        """Test getting user by Firebase UID."""
        # Create user
        created_user = await user_repository.create_user(sample_user_data)
        
        # Get by Firebase UID
        found_user = await user_repository.get_by_firebase_uid("test_firebase_uid_123")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.firebase_uid == "test_firebase_uid_123"
        
        # Test non-existent Firebase UID
        not_found = await user_repository.get_by_firebase_uid("nonexistent_uid")
        assert not_found is None
    
    async def test_update_login_info(self, user_repository, sample_user_data):
        """Test updating user login information."""
        # Create user
        user = await user_repository.create_user(sample_user_data)
        initial_login_count = user.login_count
        initial_last_login = user.last_login_at
        
        # Update login info
        updated_user = await user_repository.update_login_info(user.id)
        
        assert updated_user is not None
        assert updated_user.login_count == initial_login_count + 1
        assert updated_user.last_login_at is not None
        assert updated_user.last_login_at != initial_last_login
        
        # Test with non-existent user
        not_found = await user_repository.update_login_info(99999)
        assert not_found is None
    
    async def test_complete_onboarding(self, user_repository, sample_user_data):
        """Test completing user onboarding."""
        # Create user
        user = await user_repository.create_user(sample_user_data)
        assert user.onboarding_completed is False
        
        # Complete onboarding
        onboarding_data = {
            "transport": {"car_km_per_day": 20, "bike_km_per_day": 5},
            "diet_type": "vegetarian",
            "energy": {"electricity_kwh_per_month": 300}
        }
        
        updated_user = await user_repository.complete_onboarding(user.id, onboarding_data)
        
        assert updated_user is not None
        assert updated_user.onboarding_completed is True
        assert updated_user.preferences is not None
        
        # Parse and verify stored data
        stored_data = json.loads(updated_user.preferences)
        assert stored_data["transport"]["car_km_per_day"] == 20
        assert stored_data["diet_type"] == "vegetarian"
    
    async def test_update_baseline_footprint(self, user_repository, sample_user_data):
        """Test updating user's baseline carbon footprint."""
        # Create user
        user = await user_repository.create_user(sample_user_data)
        
        # Update baseline footprint
        baseline_footprint = 7500.50
        updated_user = await user_repository.update_baseline_footprint(user.id, baseline_footprint)
        
        assert updated_user is not None
        assert updated_user.baseline_footprint == baseline_footprint
        
        # Test with non-existent user
        not_found = await user_repository.update_baseline_footprint(99999, 5000.0)
        assert not_found is None
    
    async def test_get_active_users(self, user_repository):
        """Test getting active users."""
        # Create multiple users with different statuses
        active_user_data = UserCreate(
            firebase_uid="active_uid",
            email="active@example.com",
            name="Active User"
        )
        active_user = await user_repository.create_user(active_user_data)
        
        inactive_user_data = UserCreate(
            firebase_uid="inactive_uid",
            email="inactive@example.com",
            name="Inactive User"
        )
        inactive_user = await user_repository.create_user(inactive_user_data)
        
        # Make one user inactive
        await user_repository.update(inactive_user.id, {"is_active": False})
        
        # Get active users
        active_users = await user_repository.get_active_users()
        
        assert len(active_users) >= 1
        active_user_ids = [user.id for user in active_users]
        assert active_user.id in active_user_ids
        assert inactive_user.id not in active_user_ids
    
    async def test_get_users_by_location(self, user_repository):
        """Test getting users by location."""
        # Create users in different locations
        sf_user_data = UserCreate(
            firebase_uid="sf_uid",
            email="sf@example.com",
            name="SF User",
            location="San Francisco, CA"
        )
        sf_user = await user_repository.create_user(sf_user_data)
        
        ny_user_data = UserCreate(
            firebase_uid="ny_uid",
            email="ny@example.com",
            name="NY User",
            location="New York, NY"
        )
        await user_repository.create_user(ny_user_data)
        
        # Search by location
        sf_users = await user_repository.get_users_by_location("San Francisco")
        
        assert len(sf_users) >= 1
        sf_user_ids = [user.id for user in sf_users]
        assert sf_user.id in sf_user_ids
        
        # Test partial match
        ca_users = await user_repository.get_users_by_location("CA")
        assert len(ca_users) >= 1
    
    async def test_get_user_statistics(self, user_repository):
        """Test getting user statistics."""
        # Create users with different statuses
        user1_data = UserCreate(
            firebase_uid="stats_uid_1",
            email="stats1@example.com",
            name="Stats User 1"
        )
        user1 = await user_repository.create_user(user1_data)
        
        user2_data = UserCreate(
            firebase_uid="stats_uid_2",
            email="stats2@example.com",
            name="Stats User 2"
        )
        user2 = await user_repository.create_user(user2_data)
        
        # Complete onboarding for one user
        await user_repository.complete_onboarding(user1.id, {"test": "data"})
        
        # Update one user as verified
        await user_repository.update(user2.id, {"is_verified": True})
        
        # Get statistics
        stats = await user_repository.get_user_statistics()
        
        assert "total_users" in stats
        assert "active_users" in stats
        assert "verified_users" in stats
        assert "onboarded_users" in stats
        assert "new_users_30d" in stats
        assert "onboarding_completion_rate" in stats
        assert "verification_rate" in stats
        
        assert stats["total_users"] >= 2
        assert stats["active_users"] >= 2
        assert stats["verified_users"] >= 1
        assert stats["onboarded_users"] >= 1
        assert isinstance(stats["onboarding_completion_rate"], (int, float))
        assert isinstance(stats["verification_rate"], (int, float))
    
    async def test_search_users(self, user_repository):
        """Test user search functionality."""
        # Create users with searchable data
        user1_data = UserCreate(
            firebase_uid="search_uid_1",
            email="john.doe@example.com",
            name="John Doe",
            display_name="Johnny"
        )
        user1 = await user_repository.create_user(user1_data)
        
        user2_data = UserCreate(
            firebase_uid="search_uid_2",
            email="jane.smith@example.com",
            name="Jane Smith",
            display_name="Janie"
        )
        user2 = await user_repository.create_user(user2_data)
        
        # Search by name
        john_results = await user_repository.search_users("John")
        john_ids = [user.id for user in john_results]
        assert user1.id in john_ids
        
        # Search by email
        doe_results = await user_repository.search_users("doe@example")
        doe_ids = [user.id for user in doe_results]
        assert user1.id in doe_ids
        
        # Search by display name
        johnny_results = await user_repository.search_users("Johnny")
        johnny_ids = [user.id for user in johnny_results]
        assert user1.id in johnny_ids
        
        # Search with no results
        no_results = await user_repository.search_users("nonexistent")
        assert len(no_results) == 0
    
    async def test_get_users_needing_onboarding(self, user_repository):
        """Test getting users who need onboarding."""
        # Create users with different onboarding statuses
        onboarded_user_data = UserCreate(
            firebase_uid="onboarded_uid",
            email="onboarded@example.com",
            name="Onboarded User"
        )
        onboarded_user = await user_repository.create_user(onboarded_user_data)
        await user_repository.complete_onboarding(onboarded_user.id, {"test": "data"})
        
        not_onboarded_user_data = UserCreate(
            firebase_uid="not_onboarded_uid",
            email="notonboarded@example.com",
            name="Not Onboarded User"
        )
        not_onboarded_user = await user_repository.create_user(not_onboarded_user_data)
        
        # Get users needing onboarding
        users_needing_onboarding = await user_repository.get_users_needing_onboarding()
        
        user_ids = [user.id for user in users_needing_onboarding]
        assert not_onboarded_user.id in user_ids
        assert onboarded_user.id not in user_ids
    
    async def test_base_repository_methods(self, user_repository, sample_user_data):
        """Test inherited base repository methods."""
        # Test create
        user = await user_repository.create(sample_user_data.model_dump())
        assert user.id is not None
        
        # Test get_by_id
        found_user = await user_repository.get_by_id(user.id)
        assert found_user is not None
        assert found_user.id == user.id
        
        # Test get_by_field
        found_by_email = await user_repository.get_by_field("email", "test@example.com")
        assert found_by_email is not None
        assert found_by_email.id == user.id
        
        # Test update
        updated_user = await user_repository.update(user.id, {"name": "Updated Name"})
        assert updated_user.name == "Updated Name"
        
        # Test get_multi
        users = await user_repository.get_multi(limit=10)
        assert len(users) >= 1
        
        # Test count
        count = await user_repository.count()
        assert count >= 1
        
        # Test exists
        exists = await user_repository.exists(user.id)
        assert exists is True
        
        non_exists = await user_repository.exists(99999)
        assert non_exists is False
        
        # Test delete (soft delete)
        deleted = await user_repository.delete(user.id)
        assert deleted is True
        
        # Verify soft delete
        deleted_user = await user_repository.get_by_id(user.id)
        assert deleted_user.is_deleted is True
    
    async def test_bulk_create(self, user_repository):
        """Test bulk user creation."""
        users_data = [
            {
                "firebase_uid": "bulk_uid_1",
                "email": "bulk1@example.com",
                "name": "Bulk User 1"
            },
            {
                "firebase_uid": "bulk_uid_2",
                "email": "bulk2@example.com",
                "name": "Bulk User 2"
            },
            {
                "firebase_uid": "bulk_uid_3",
                "email": "bulk3@example.com",
                "name": "Bulk User 3"
            }
        ]
        
        created_users = await user_repository.bulk_create(users_data)
        
        assert len(created_users) == 3
        for i, user in enumerate(created_users):
            assert user.id is not None
            assert user.firebase_uid == f"bulk_uid_{i+1}"
            assert user.email == f"bulk{i+1}@example.com"
            assert user.name == f"Bulk User {i+1}"
    
    async def test_error_handling(self, user_repository):
        """Test error handling in repository methods."""
        # Test getting non-existent user
        non_existent = await user_repository.get_by_id(99999)
        assert non_existent is None
        
        # Test updating non-existent user
        not_updated = await user_repository.update(99999, {"name": "New Name"})
        assert not_updated is None
        
        # Test deleting non-existent user
        not_deleted = await user_repository.delete(99999)
        assert not_deleted is False