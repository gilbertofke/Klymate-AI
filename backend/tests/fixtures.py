"""
Test Fixtures - Task 10 Implementation

This module provides comprehensive test fixtures for database management,
service mocking, and test data generation. Follows best practices for
test isolation and cleanup.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
import json
from datetime import datetime, timedelta

from app.core.database import Base, get_db
from app.core.config import settings
from tests.factories import create_test_dataset


class TestDatabaseManager:
    """Manages test database lifecycle and isolation."""
    
    def __init__(self):
        """Initialize test database manager."""
        self.engine = None
        self.session_factory = None
        self.temp_db_file = None
    
    async def setup_test_database(self) -> AsyncSession:
        """Set up isolated test database."""
        # Create temporary SQLite database for testing
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        test_db_url = f"sqlite+aiosqlite:///{self.temp_db_file.name}"
        
        # Create async engine with proper configuration
        self.engine = create_async_engine(
            test_db_url,
            echo=False,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
            }
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Return session
        return self.session_factory()
    
    async def cleanup_test_database(self):
        """Clean up test database."""
        if self.engine:
            await self.engine.dispose()
        
        if self.temp_db_file:
            try:
                os.unlink(self.temp_db_file.name)
            except (OSError, FileNotFoundError):
                pass
    
    async def reset_database(self, session: AsyncSession):
        """Reset database to clean state."""
        # Drop and recreate all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        # Refresh session
        await session.rollback()
    
    async def seed_test_data(self, session: AsyncSession) -> Dict[str, Any]:
        """Seed database with test data."""
        test_data = create_test_dataset()
        
        # Add all entities to session
        for entity_list in test_data.values():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    session.add(entity)
            else:
                session.add(entity_list)
        
        await session.commit()
        return test_data


class MockServiceManager:
    """Manages mock services for testing external dependencies."""
    
    def __init__(self):
        """Initialize mock service manager."""
        self.active_mocks = {}
        self.patches = {}
    
    def create_mock_service(self, service_name: str) -> Mock:
        """Create a mock service with common methods."""
        mock_service = Mock()
        
        # Add common async methods
        mock_service.get_by_id = AsyncMock()
        mock_service.create = AsyncMock()
        mock_service.update = AsyncMock()
        mock_service.delete = AsyncMock()
        mock_service.get_multi = AsyncMock()
        
        self.active_mocks[service_name] = mock_service
        return mock_service
    
    def mock_firebase_auth(self) -> Mock:
        """Create mock Firebase authentication."""
        mock_firebase = Mock()
        mock_firebase.verify_id_token = Mock(return_value={
            'uid': 'test_uid',
            'email': 'test@example.com',
            'name': 'Test User'
        })
        
        self.active_mocks['firebase'] = mock_firebase
        return mock_firebase
    
    def mock_openai_api(self) -> Mock:
        """Create mock OpenAI API."""
        mock_openai = Mock()
        
        # Mock embeddings
        mock_openai.embeddings.create = Mock(return_value=Mock(
            data=[Mock(embedding=[0.1] * 1536)]
        ))
        
        # Mock chat completions
        mock_openai.chat.completions.create = Mock(return_value=Mock(
            choices=[Mock(message=Mock(content="Mock AI response"))]
        ))
        
        self.active_mocks['openai'] = mock_openai
        return mock_openai
    
    def mock_redis_client(self) -> Mock:
        """Create mock Redis client."""
        mock_redis = Mock()
        
        # Mock Redis operations
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=1)
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.scan_iter = AsyncMock(return_value=[])
        mock_redis.info = AsyncMock(return_value={
            'used_memory': 1024000,
            'keyspace_hits': 100,
            'keyspace_misses': 10
        })
        
        self.active_mocks['redis'] = mock_redis
        return mock_redis
    
    def start_patches(self):
        """Start all mock patches."""
        # Patch Firebase
        if 'firebase' in self.active_mocks:
            self.patches['firebase'] = patch(
                'app.utils.auth_integration.firebase_admin.auth',
                self.active_mocks['firebase']
            )
            self.patches['firebase'].start()
        
        # Patch OpenAI
        if 'openai' in self.active_mocks:
            self.patches['openai'] = patch(
                'app.utils.ai_utilities.OpenAI',
                return_value=self.active_mocks['openai']
            )
            self.patches['openai'].start()
        
        # Patch Redis
        if 'redis' in self.active_mocks:
            self.patches['redis'] = patch(
                'app.utils.cache.redis.from_url',
                return_value=self.active_mocks['redis']
            )
            self.patches['redis'].start()
    
    def stop_patches(self):
        """Stop all mock patches."""
        for patch_obj in self.patches.values():
            patch_obj.stop()
        self.patches.clear()
    
    def cleanup(self):
        """Clean up all mocks."""
        self.stop_patches()
        self.active_mocks.clear()


class TestDataGenerator:
    """Generates test data for various scenarios."""
    
    def generate_user_data(self, **overrides) -> Dict[str, Any]:
        """Generate user test data."""
        base_data = {
            "email": "test@example.com",
            "name": "Test User",
            "display_name": "Test",
            "firebase_uid": "test_firebase_uid",
            "is_active": True,
            "is_verified": True,
            "onboarding_completed": True,
            "baseline_footprint": 12000.0,
            "total_co2_saved": 150.0,
            "eco_score": 750,
            "current_streak": 15
        }
        base_data.update(overrides)
        return base_data
    
    def generate_habit_data(self, **overrides) -> Dict[str, Any]:
        """Generate habit test data."""
        base_data = {
            "category_id": 1,
            "quantity": 5.0,
            "co2_saved": 2.5,
            "logged_date": datetime.utcnow().date(),
            "notes": "Test habit logging",
            "is_verified": True
        }
        base_data.update(overrides)
        return base_data
    
    def generate_badge_data(self, **overrides) -> Dict[str, Any]:
        """Generate badge test data."""
        base_data = {
            "name": "Test Badge",
            "description": "A test badge for validation",
            "category": "milestone",
            "points_value": 50,
            "criteria": {
                "trigger": "habit_logged",
                "count": 10,
                "category": "any"
            },
            "is_active": True
        }
        base_data.update(overrides)
        return base_data
    
    def generate_conversation_data(self, **overrides) -> Dict[str, Any]:
        """Generate AI conversation test data."""
        base_data = {
            "user_id": 1,
            "message_type": "user",
            "content": "How can I reduce my carbon footprint?",
            "session_id": "test_session_123",
            "context_metadata": {
                "user_context": {
                    "total_habits": 10,
                    "current_streak": 5
                }
            }
        }
        base_data.update(overrides)
        return base_data
    
    def generate_api_request_data(self, endpoint: str, **overrides) -> Dict[str, Any]:
        """Generate API request test data."""
        request_data = {
            "habits": {
                "category_id": 1,
                "quantity": 3.0,
                "notes": "Test API request"
            },
            "users": {
                "name": "API Test User",
                "email": "apitest@example.com"
            },
            "analytics": {
                "days_back": 30,
                "include_trends": True
            },
            "ai_chat": {
                "message": "Test AI chat message",
                "session_id": "api_test_session"
            }
        }
        
        base_data = request_data.get(endpoint, {})
        base_data.update(overrides)
        return base_data
    
    def generate_error_scenarios(self) -> List[Dict[str, Any]]:
        """Generate test data for error scenarios."""
        return [
            {
                "scenario": "invalid_email",
                "data": {"email": "invalid-email"},
                "expected_error": "Invalid email format"
            },
            {
                "scenario": "missing_required_field",
                "data": {"name": "Test User"},  # Missing email
                "expected_error": "Email is required"
            },
            {
                "scenario": "negative_quantity",
                "data": {"quantity": -1.0},
                "expected_error": "Quantity must be positive"
            },
            {
                "scenario": "future_date",
                "data": {"logged_date": (datetime.utcnow() + timedelta(days=1)).date()},
                "expected_error": "Cannot log habits for future dates"
            }
        ]


# Pytest fixtures

@pytest_asyncio.fixture(scope="function")
async def test_db_manager() -> AsyncGenerator[TestDatabaseManager, None]:
    """Provide test database manager."""
    manager = TestDatabaseManager()
    try:
        yield manager
    finally:
        await manager.cleanup_test_database()


@pytest_asyncio.fixture(scope="function")
async def isolated_db_session(test_db_manager: TestDatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    """Provide isolated database session for each test."""
    session = await test_db_manager.setup_test_database()
    try:
        yield session
    finally:
        await session.close()
        await test_db_manager.cleanup_test_database()


@pytest.fixture(scope="function")
def mock_services() -> MockServiceManager:
    """Provide mock service manager."""
    manager = MockServiceManager()
    manager.start_patches()
    try:
        yield manager
    finally:
        manager.cleanup()


@pytest.fixture(scope="function")
def test_data_generator() -> TestDataGenerator:
    """Provide test data generator."""
    return TestDataGenerator()


@pytest_asyncio.fixture(scope="function")
async def seeded_db_session(isolated_db_session: AsyncSession, test_db_manager: TestDatabaseManager) -> AsyncGenerator[tuple[AsyncSession, Dict[str, Any]], None]:
    """Provide database session with seeded test data."""
    test_data = await test_db_manager.seed_test_data(isolated_db_session)
    yield isolated_db_session, test_data


@pytest.fixture(scope="function")
def mock_external_services(mock_services: MockServiceManager) -> Dict[str, Mock]:
    """Provide mocked external services."""
    mocks = {
        'firebase': mock_services.mock_firebase_auth(),
        'openai': mock_services.mock_openai_api(),
        'redis': mock_services.mock_redis_client()
    }
    return mocks


@pytest_asyncio.fixture(scope="function")
async def performance_monitor():
    """Provide performance monitoring for tests."""
    import time
    import psutil
    import os
    
    start_time = time.time()
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss
    
    yield {
        'start_time': start_time,
        'start_memory': start_memory,
        'process': process
    }
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    
    # Log performance metrics (could be extended to write to file)
    duration = end_time - start_time
    memory_delta = end_memory - start_memory
    
    if duration > 1.0:  # Log slow tests
        print(f"SLOW TEST: Duration {duration:.2f}s")
    
    if memory_delta > 10 * 1024 * 1024:  # Log high memory usage (10MB+)
        print(f"HIGH MEMORY: Delta {memory_delta / 1024 / 1024:.2f}MB")


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "database_url": "sqlite+aiosqlite:///test.db",
        "redis_url": "redis://localhost:6379/1",
        "environment": "test",
        "debug": True,
        "testing": True,
        "cache_enabled": False,  # Disable caching in tests
        "firebase_project_id": "test-project",
        "openai_api_key": "test-key"
    }


@pytest.fixture(autouse=True)
def test_environment_setup(test_config):
    """Set up test environment variables."""
    import os
    
    # Store original values
    original_env = {}
    for key, value in test_config.items():
        original_env[key.upper()] = os.getenv(key.upper())
        os.environ[key.upper()] = str(value)
    
    yield
    
    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value