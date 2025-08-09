"""
Database Connection and ORM Tests

Tests for database connectivity, session management, and basic ORM functionality.
"""

import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import (
    DatabaseManager,
    get_db,
    get_async_db,
    check_database_connection,
    sync_engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal
)
from app.core.database_init import DatabaseInitializer
from app.models.base import Base, BaseModel, TimestampMixin


class TestDatabaseConnection:
    """Test database connection and basic functionality."""
    
    def test_sync_database_connection(self):
        """Test synchronous database connection."""
        # Test getting a session
        db = DatabaseManager.get_sync_session()
        assert db is not None
        
        # Test basic query
        result = db.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        
        db.close()
    
    @pytest.mark.asyncio
    async def test_async_database_connection(self):
        """Test asynchronous database connection."""
        # Test getting an async session
        db = await DatabaseManager.get_async_session()
        assert db is not None
        
        # Test basic query
        result = await db.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        
        await db.close()
    
    @pytest.mark.asyncio
    async def test_check_database_connection(self):
        """Test database connection check utility."""
        result = await check_database_connection()
        assert result is True
    
    def test_fastapi_db_dependency(self):
        """Test FastAPI database dependency."""
        db_generator = get_db()
        db = next(db_generator)
        
        assert db is not None
        
        # Test basic query
        result = db.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        
        # Close the generator
        try:
            next(db_generator)
        except StopIteration:
            pass  # Expected behavior
    
    @pytest.mark.asyncio
    async def test_fastapi_async_db_dependency(self):
        """Test FastAPI async database dependency."""
        async_gen = get_async_db()
        db = await async_gen.__anext__()
        
        assert db is not None
        
        # Test basic query
        result = await db.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        
        # Close the generator
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass  # Expected behavior


class TestDatabaseInitializer:
    """Test database initialization utilities."""
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check."""
        health = await DatabaseInitializer.check_database_health()
        
        assert health is not None
        assert "status" in health
        assert "connection" in health
        assert health["status"] in ["healthy", "unhealthy"]
        
        if health["status"] == "healthy":
            assert health["connection"] == "ok"
            assert "tables_count" in health
            assert "database" in health
            assert "host" in health


class TestBaseModel:
    """Test base model functionality."""
    
    def test_base_model_creation(self):
        """Test base model class creation."""
        # BaseModel is abstract, so we can't instantiate it directly
        # But we can test its structure
        assert hasattr(BaseModel, 'id')
        assert hasattr(BaseModel, 'created_at')
        assert hasattr(BaseModel, 'updated_at')
        assert hasattr(BaseModel, 'to_dict')
        assert hasattr(BaseModel, 'update_from_dict')
    
    def test_timestamp_mixin(self):
        """Test timestamp mixin functionality."""
        assert hasattr(TimestampMixin, 'created_at')
        assert hasattr(TimestampMixin, 'updated_at')


class TestSessionManagement:
    """Test database session management."""
    
    def test_sync_session_lifecycle(self):
        """Test synchronous session lifecycle."""
        # Create session
        session = SessionLocal()
        assert session is not None
        
        # Use session
        result = session.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        
        # Close session
        session.close()
    
    @pytest.mark.asyncio
    async def test_async_session_lifecycle(self):
        """Test asynchronous session lifecycle."""
        # Create session
        async with AsyncSessionLocal() as session:
            assert session is not None
            
            # Use session
            result = await session.execute(text("SELECT 1 as test"))
            assert result.scalar() == 1
        
        # Session is automatically closed by context manager
    
    def test_multiple_sync_sessions(self):
        """Test multiple synchronous sessions."""
        sessions = []
        
        # Create multiple sessions
        for i in range(3):
            session = SessionLocal()
            sessions.append(session)
            
            # Test each session
            result = session.execute(text(f"SELECT {i+1} as test"))
            assert result.scalar() == i+1
        
        # Close all sessions
        for session in sessions:
            session.close()
    
    @pytest.mark.asyncio
    async def test_multiple_async_sessions(self):
        """Test multiple asynchronous sessions."""
        # Create and test multiple async sessions
        for i in range(3):
            async with AsyncSessionLocal() as session:
                result = await session.execute(text(f"SELECT {i+1} as test"))
                assert result.scalar() == i+1


class TestDatabaseConfiguration:
    """Test database configuration and settings."""
    
    def test_engine_configuration(self):
        """Test database engine configuration."""
        assert sync_engine is not None
        assert async_engine is not None
        
        # Test engine properties
        assert sync_engine.pool is not None
        assert async_engine.pool is not None
    
    def test_base_metadata(self):
        """Test SQLAlchemy Base metadata."""
        assert Base is not None
        assert Base.metadata is not None
        
        # Base should be ready for model registration
        assert hasattr(Base, 'metadata')
        assert hasattr(Base.metadata, 'create_all')
        assert hasattr(Base.metadata, 'drop_all')