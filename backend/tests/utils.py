"""
Test Utilities - Task 10 Implementation

This module provides comprehensive test utilities including helpers for
database operations, API testing, mocking, and test data management.
Follows best practices for test maintainability and reusability.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import logging

from app.models.user import User
from app.models.habit import HabitCategory
from app.models.user_habit import UserHabit
from app.models.badge import Badge, UserBadge
from app.models.ai_conversation import AIConversation
from tests.factories import (
    UserFactory, HabitCategoryFactory, UserHabitFactory,
    BadgeFactory, UserBadgeFactory, AIConversationFactory
)


class TestHelper:
    """General test helper utilities."""
    
    def __init__(self):
        """Initialize test helper."""
        self.logger = logging.getLogger('test_helper')
    
    async def create_test_user(self, session: AsyncSession, **overrides) -> User:
        """Create a test user with optional overrides."""
        user_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "firebase_uid": "test_firebase_uid",
            "is_active": True,
            "is_verified": True,
            **overrides
        }
        
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        self.logger.debug(f"Created test user: {user.email}")
        return user
    
    async def create_test_habit(self, session: AsyncSession, user_id: int, category_id: int, **overrides) -> UserHabit:
        """Create a test habit with optional overrides."""
        habit_data = {
            "user_id": user_id,
            "category_id": category_id,
            "quantity": 5.0,
            "co2_saved": Decimal("2.5"),
            "logged_date": datetime.utcnow().date(),
            "notes": "Test habit",
            **overrides
        }
        
        habit = UserHabit(**habit_data)
        session.add(habit)
        await session.commit()
        await session.refresh(habit)
        
        self.logger.debug(f"Created test habit: {habit.id}")
        return habit
    
    async def create_test_category(self, session: AsyncSession, **overrides) -> HabitCategory:
        """Create a test habit category with optional overrides."""
        category_data = {
            "name": "Test Category",
            "description": "A test category",
            "category_type": "transport",
            "co2_per_unit": Decimal("1.5"),
            "unit_name": "km",
            **overrides
        }
        
        category = HabitCategory(**category_data)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        
        self.logger.debug(f"Created test category: {category.name}")
        return category
    
    async def cleanup_test_data(self, session: AsyncSession, user_ids: List[int] = None):
        """Clean up test data for specific users or all test data."""
        try:
            if user_ids:
                # Clean up specific users' data
                for user_id in user_ids:
                    await session.execute(delete(UserHabit).where(UserHabit.user_id == user_id))
                    await session.execute(delete(UserBadge).where(UserBadge.user_id == user_id))
                    await session.execute(delete(AIConversation).where(AIConversation.user_id == user_id))
                    await session.execute(delete(User).where(User.id == user_id))
            else:
                # Clean up all test data
                await session.execute(delete(UserHabit))
                await session.execute(delete(UserBadge))
                await session.execute(delete(AIConversation))
                await session.execute(delete(User))
                await session.execute(delete(Badge))
                await session.execute(delete(HabitCategory))
            
            await session.commit()
            self.logger.debug("Cleaned up test data")
            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error cleaning up test data: {str(e)}")
            raise
    
    def reset_test_database(self):
        """Reset test database to clean state."""
        # This would be implemented based on specific database setup
        raise NotImplementedError("Database reset not implemented yet")
    
    def generate_test_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate a test JWT token for authentication."""
        import jwt
        from app.core.config import settings
        
        payload = {
            "sub": str(user_data.get("id", 1)),
            "email": user_data.get("email", "test@example.com"),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token
    
    def assert_dict_contains(self, actual: Dict[str, Any], expected: Dict[str, Any], path: str = ""):
        """Assert that actual dictionary contains all expected key-value pairs."""
        for key, expected_value in expected.items():
            current_path = f"{path}.{key}" if path else key
            
            assert key in actual, f"Missing key '{current_path}' in actual data"
            
            actual_value = actual[key]
            
            if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                self.assert_dict_contains(actual_value, expected_value, current_path)
            elif isinstance(expected_value, list) and isinstance(actual_value, list):
                assert len(actual_value) == len(expected_value), \
                    f"List length mismatch at '{current_path}': expected {len(expected_value)}, got {len(actual_value)}"
                for i, (exp_item, act_item) in enumerate(zip(expected_value, actual_value)):
                    if isinstance(exp_item, dict):
                        self.assert_dict_contains(act_item, exp_item, f"{current_path}[{i}]")
                    else:
                        assert act_item == exp_item, f"List item mismatch at '{current_path}[{i}]'"
            else:
                assert actual_value == expected_value, \
                    f"Value mismatch at '{current_path}': expected {expected_value}, got {actual_value}"
    
    def wait_for_condition(self, condition: Callable[[], bool], timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Wait for a condition to become true within timeout."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        
        return False
    
    async def wait_for_async_condition(self, condition: Callable[[], bool], timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Wait for a condition to become true within timeout (async version)."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition() if asyncio.iscoroutinefunction(condition) else condition():
                return True
            await asyncio.sleep(interval)
        
        return False


class DatabaseTestHelper:
    """Database-specific test helper utilities."""
    
    def __init__(self):
        """Initialize database test helper."""
        self.logger = logging.getLogger('db_test_helper')
    
    async def create_test_tables(self, session: AsyncSession):
        """Create test tables if they don't exist."""
        # This would be implemented based on specific database setup
        self.logger.debug("Test tables creation not implemented yet")
    
    async def cleanup_test_tables(self, session: AsyncSession):
        """Clean up test tables."""
        # This would be implemented based on specific database setup
        self.logger.debug("Test tables cleanup not implemented yet")
    
    async def seed_test_data(self, session: AsyncSession) -> Dict[str, Any]:
        """Seed database with comprehensive test data."""
        # Create categories
        categories = []
        for i, (name, cat_type) in enumerate([
            ("Walking", "transport"),
            ("Cycling", "transport"),
            ("Vegetarian Meal", "diet"),
            ("LED Bulbs", "energy"),
            ("Recycling", "lifestyle")
        ]):
            category = HabitCategory(
                name=name,
                description=f"Test category: {name}",
                category_type=cat_type,
                co2_per_unit=Decimal(str(1.0 + i * 0.5)),
                unit_name="unit"
            )
            session.add(category)
            categories.append(category)
        
        await session.commit()
        
        # Create users
        users = []
        for i in range(3):
            user = User(
                email=f"testuser{i}@example.com",
                name=f"Test User {i}",
                firebase_uid=f"test_uid_{i}",
                is_active=True,
                is_verified=True,
                baseline_footprint=Decimal("12000.0"),
                total_co2_saved=Decimal(str(50.0 + i * 25.0)),
                eco_score=500 + i * 100,
                current_streak=i * 5
            )
            session.add(user)
            users.append(user)
        
        await session.commit()
        
        # Create habits
        habits = []
        for user in users:
            for j, category in enumerate(categories[:3]):  # Each user gets 3 habits
                habit = UserHabit(
                    user_id=user.id,
                    category_id=category.id,
                    quantity=Decimal(str(2.0 + j)),
                    co2_saved=Decimal(str(1.5 + j * 0.5)),
                    logged_date=datetime.utcnow().date(),
                    notes=f"Test habit {j} for user {user.id}"
                )
                session.add(habit)
                habits.append(habit)
        
        await session.commit()
        
        # Create badges
        badges = []
        for i, name in enumerate(["First Steps", "Eco Warrior", "Green Champion"]):
            badge = Badge(
                name=name,
                description=f"Test badge: {name}",
                category="milestone",
                points_value=25 + i * 25,
                criteria={
                    "trigger": "habit_logged",
                    "count": 5 + i * 5
                }
            )
            session.add(badge)
            badges.append(badge)
        
        await session.commit()
        
        self.logger.info(f"Seeded test data: {len(users)} users, {len(categories)} categories, {len(habits)} habits, {len(badges)} badges")
        
        return {
            "users": users,
            "categories": categories,
            "habits": habits,
            "badges": badges
        }
    
    async def verify_database_state(self, session: AsyncSession, expected_counts: Dict[str, int]):
        """Verify database contains expected number of records."""
        models = {
            "users": User,
            "categories": HabitCategory,
            "habits": UserHabit,
            "badges": Badge,
            "user_badges": UserBadge,
            "conversations": AIConversation
        }
        
        for entity_name, expected_count in expected_counts.items():
            if entity_name in models:
                result = await session.execute(select(models[entity_name]))
                actual_count = len(result.scalars().all())
                assert actual_count == expected_count, \
                    f"Expected {expected_count} {entity_name}, found {actual_count}"
        
        self.logger.debug(f"Database state verified: {expected_counts}")
    
    async def get_database_statistics(self, session: AsyncSession) -> Dict[str, int]:
        """Get current database statistics."""
        stats = {}
        models = {
            "users": User,
            "categories": HabitCategory,
            "habits": UserHabit,
            "badges": Badge,
            "user_badges": UserBadge,
            "conversations": AIConversation
        }
        
        for name, model in models.items():
            result = await session.execute(select(model))
            stats[name] = len(result.scalars().all())
        
        return stats


class APITestHelper:
    """API testing helper utilities."""
    
    def __init__(self):
        """Initialize API test helper."""
        self.logger = logging.getLogger('api_test_helper')
    
    def create_authenticated_client(self, client: TestClient, user_data: Dict[str, Any]) -> TestClient:
        """Create authenticated test client with JWT token."""
        helper = TestHelper()
        token = helper.generate_test_jwt_token(user_data)
        
        # Add authorization header to client
        client.headers.update({"Authorization": f"Bearer {token}"})
        return client
    
    def create_test_headers(self, user_data: Dict[str, Any] = None, **additional_headers) -> Dict[str, str]:
        """Create test headers including authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **additional_headers
        }
        
        if user_data:
            helper = TestHelper()
            token = helper.generate_test_jwt_token(user_data)
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def assert_api_response(
        self,
        response,
        expected_status: int,
        expected_data: Dict[str, Any] = None,
        expected_keys: List[str] = None,
        expected_error: str = None
    ):
        """Assert API response matches expectations."""
        # Check status code
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
        
        # Parse response data
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            if expected_data or expected_keys:
                pytest.fail(f"Expected JSON response, got: {response.text}")
            return
        
        # Check expected data
        if expected_data:
            helper = TestHelper()
            helper.assert_dict_contains(response_data, expected_data)
        
        # Check expected keys
        if expected_keys:
            for key in expected_keys:
                assert key in response_data, f"Missing key '{key}' in response: {response_data}"
        
        # Check expected error
        if expected_error:
            assert "error" in response_data or "detail" in response_data, \
                f"Expected error in response: {response_data}"
            error_message = response_data.get("error", response_data.get("detail", ""))
            assert expected_error.lower() in error_message.lower(), \
                f"Expected error '{expected_error}' not found in '{error_message}'"
        
        self.logger.debug(f"API response assertion passed for status {expected_status}")
    
    def test_api_endpoint_crud(
        self,
        client: TestClient,
        endpoint: str,
        create_data: Dict[str, Any],
        update_data: Dict[str, Any],
        user_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test full CRUD operations for an API endpoint."""
        headers = self.create_test_headers(user_data) if user_data else {}
        results = {}
        
        # Test CREATE
        response = client.post(endpoint, json=create_data, headers=headers)
        self.assert_api_response(response, 201)
        created_item = response.json()
        item_id = created_item.get("id")
        results["created"] = created_item
        
        # Test READ (single)
        response = client.get(f"{endpoint}/{item_id}", headers=headers)
        self.assert_api_response(response, 200)
        results["read"] = response.json()
        
        # Test READ (list)
        response = client.get(endpoint, headers=headers)
        self.assert_api_response(response, 200)
        results["list"] = response.json()
        
        # Test UPDATE
        response = client.put(f"{endpoint}/{item_id}", json=update_data, headers=headers)
        self.assert_api_response(response, 200)
        results["updated"] = response.json()
        
        # Test DELETE
        response = client.delete(f"{endpoint}/{item_id}", headers=headers)
        self.assert_api_response(response, 204)
        results["deleted"] = True
        
        # Verify deletion
        response = client.get(f"{endpoint}/{item_id}", headers=headers)
        self.assert_api_response(response, 404)
        
        self.logger.info(f"CRUD test completed for endpoint: {endpoint}")
        return results
    
    def test_api_pagination(
        self,
        client: TestClient,
        endpoint: str,
        total_items: int,
        page_size: int = 10,
        user_data: Dict[str, Any] = None
    ):
        """Test API pagination functionality."""
        headers = self.create_test_headers(user_data) if user_data else {}
        
        # Test first page
        response = client.get(f"{endpoint}?limit={page_size}&offset=0", headers=headers)
        self.assert_api_response(response, 200)
        first_page = response.json()
        
        # Verify pagination metadata
        assert "items" in first_page or isinstance(first_page, list)
        items = first_page.get("items", first_page)
        assert len(items) <= page_size
        
        if total_items > page_size:
            # Test second page
            response = client.get(f"{endpoint}?limit={page_size}&offset={page_size}", headers=headers)
            self.assert_api_response(response, 200)
            second_page = response.json()
            second_items = second_page.get("items", second_page)
            
            # Verify different items on different pages
            first_ids = [item.get("id") for item in items]
            second_ids = [item.get("id") for item in second_items]
            assert not set(first_ids).intersection(set(second_ids)), \
                "Pages should contain different items"
        
        self.logger.debug(f"Pagination test completed for endpoint: {endpoint}")


class MockHelper:
    """Mock and patching helper utilities."""
    
    def __init__(self):
        """Initialize mock helper."""
        self.active_patches = []
        self.logger = logging.getLogger('mock_helper')
    
    def mock_firebase_auth(self, user_data: Dict[str, Any] = None) -> Mock:
        """Mock Firebase authentication."""
        default_user = {
            "uid": "test_firebase_uid",
            "email": "test@example.com",
            "name": "Test User"
        }
        user_data = user_data or default_user
        
        mock_auth = Mock()
        mock_auth.verify_id_token = Mock(return_value=user_data)
        
        patch_obj = patch('app.utils.auth_integration.firebase_admin.auth', mock_auth)
        self.active_patches.append(patch_obj)
        patch_obj.start()
        
        self.logger.debug("Firebase auth mocked")
        return mock_auth
    
    def mock_openai_api(self, responses: Dict[str, Any] = None) -> Mock:
        """Mock OpenAI API responses."""
        default_responses = {
            "embedding": [0.1] * 1536,
            "chat_response": "This is a mock AI response for testing."
        }
        responses = responses or default_responses
        
        mock_openai = Mock()
        
        # Mock embeddings
        mock_openai.embeddings.create = Mock(return_value=Mock(
            data=[Mock(embedding=responses["embedding"])]
        ))
        
        # Mock chat completions
        mock_openai.chat.completions.create = Mock(return_value=Mock(
            choices=[Mock(message=Mock(content=responses["chat_response"]))]
        ))
        
        patch_obj = patch('app.utils.ai_utilities.OpenAI', return_value=mock_openai)
        self.active_patches.append(patch_obj)
        patch_obj.start()
        
        self.logger.debug("OpenAI API mocked")
        return mock_openai
    
    def mock_redis_client(self, cache_data: Dict[str, Any] = None) -> Mock:
        """Mock Redis client."""
        cache_data = cache_data or {}
        
        mock_redis = Mock()
        
        # Mock Redis operations
        mock_redis.get = AsyncMock(side_effect=lambda key: cache_data.get(key))
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=1)
        mock_redis.exists = AsyncMock(side_effect=lambda key: key in cache_data)
        mock_redis.scan_iter = AsyncMock(return_value=list(cache_data.keys()))
        mock_redis.info = AsyncMock(return_value={
            'used_memory': 1024000,
            'keyspace_hits': 100,
            'keyspace_misses': 10
        })
        
        patch_obj = patch('app.utils.cache.redis.from_url', return_value=mock_redis)
        self.active_patches.append(patch_obj)
        patch_obj.start()
        
        self.logger.debug("Redis client mocked")
        return mock_redis
    
    def mock_external_api(self, api_name: str, responses: Dict[str, Any]) -> Mock:
        """Mock external API with custom responses."""
        mock_api = Mock()
        
        for method_name, response in responses.items():
            if asyncio.iscoroutinefunction(response):
                setattr(mock_api, method_name, AsyncMock(return_value=response))
            else:
                setattr(mock_api, method_name, Mock(return_value=response))
        
        # This would need to be customized based on specific API
        self.logger.debug(f"External API '{api_name}' mocked")
        return mock_api
    
    def cleanup_mocks(self):
        """Clean up all active patches."""
        for patch_obj in self.active_patches:
            patch_obj.stop()
        self.active_patches.clear()
        self.logger.debug("All mocks cleaned up")
    
    def __del__(self):
        """Ensure cleanup on deletion."""
        self.cleanup_mocks()