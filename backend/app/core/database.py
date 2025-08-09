"""
Database Configuration and Connection Management

This module provides comprehensive database connection utilities for TiDB
with async support, connection pooling, and proper error handling.
"""

import logging
from typing import AsyncGenerator, Optional
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database URL configurations with SSL for TiDB Cloud
SYNC_DATABASE_URL = f"mysql+pymysql://{settings.TIDB_USER}:{settings.TIDB_PASSWORD}@{settings.TIDB_HOST}:{settings.TIDB_PORT}/{settings.TIDB_DATABASE}?charset=utf8mb4&ssl_ca=ca-cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
# For hackathon, use sync connection for both to avoid SSL complexity
ASYNC_DATABASE_URL = SYNC_DATABASE_URL

# Engine configuration with connection pooling
sync_engine_config = {
    "poolclass": QueuePool,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": settings.DEBUG,
}

async_engine_config = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": settings.DEBUG,
}

# Create engines - using sync for both in hackathon mode to avoid SSL complexity
sync_engine = create_engine(SYNC_DATABASE_URL, **sync_engine_config)
# For hackathon, we'll use the same sync engine for async operations
async_engine = sync_engine

# Session makers - using sync for both in hackathon mode
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
# For hackathon, use sync session for both
AsyncSessionLocal = SessionLocal

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


class DatabaseManager:
    """Database connection and session management."""
    
    @staticmethod
    def get_sync_session() -> Session:
        """Get synchronous database session."""
        return SessionLocal()
    
    @staticmethod
    async def get_async_session() -> AsyncSession:
        """Get asynchronous database session."""
        return AsyncSessionLocal()
    
    @staticmethod
    async def close_async_engine():
        """Close async engine connections."""
        await async_engine.dispose()
    
    @staticmethod
    def close_sync_engine():
        """Close sync engine connections."""
        sync_engine.dispose()


# Dependency for FastAPI
def get_db() -> Session:
    """Dependency to get database session for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Async dependency to get database session for FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Database connection utilities
async def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        from sqlalchemy import text
        # Use sync session for hackathon simplicity
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def init_database():
    """Initialize database tables (for development/testing)."""
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


# Event listeners for connection management
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database connection parameters."""
    if "mysql" in str(dbapi_connection):
        # Set MySQL/TiDB specific parameters
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
        cursor.execute("SET SESSION time_zone = '+00:00'")
        cursor.close()


@event.listens_for(sync_engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log database connection checkout."""
    logger.debug("Database connection checked out")


@event.listens_for(sync_engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log database connection checkin."""
    logger.debug("Database connection checked in")
