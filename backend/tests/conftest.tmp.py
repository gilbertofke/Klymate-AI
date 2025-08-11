"""Test configuration and fixtures."""
import os
import sys
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.models.base import Base
from app.models.user import User
from app.models.habit import Habit
from app.models.user_habit import UserHabit
from app.models.carbon_footprint import CarbonFootprint
from app.models.badge import Badge, UserBadge

# Create an async SQLite engine for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create async session factory
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest.fixture(autouse=True)
def mock_firebase():
    """Mock Firebase configuration for tests."""
    # Create mock objects
    mock_auth = Mock()
    mock_credentials = Mock()
    mock_app = Mock()
    mock_app.auth = mock_auth

    # Configure mock auth responses
    mock_auth.verify_id_token.return_value = {
        "uid": "test_uid",
        "email": "test@example.com",
        "email_verified": True
    }
    mock_user = Mock(uid="test_uid", email="test@example.com")
    mock_auth.get_user.return_value = mock_user
    mock_auth.get_user_by_email.return_value = mock_user
    mock_auth.create_custom_token.return_value = b"mock_token"

    # Mock credentials
    mock_credentials.Certificate.return_value = None

    # Apply patches
    patches = [
        patch("firebase_admin.credentials", mock_credentials),
        patch("firebase_admin.auth", mock_auth),
        patch("firebase_admin.initialize_app", return_value=mock_app),
        patch("firebase_admin.get_app", return_value=mock_app),
        patch("app.utils.firebase_config.FirebaseConfig._initialized", True),
        patch("app.utils.firebase_config.FirebaseConfig._app", mock_app)
    ]
    
    for p in patches:
        p.start()
        
    yield mock_auth
    
    for p in patches:
        p.stop()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_app():
    return app
