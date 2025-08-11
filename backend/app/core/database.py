"""
Database Configuration and Connection Management

This module provides comprehensive database connection utilities with both
synchronous and asynchronous support, proper error handling and connection management.
"""

import logging
import os
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, MetaData, event, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Ensure the database directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_db"), exist_ok=True)

# TiDB Cloud connection settings
TIDB_HOST = "gateway01.us-west-2.prod.aws.tidbcloud.com"
TIDB_PORT = 4000
TIDB_USER = "4AUZ2qQ2S6Pst2e.root"
TIDB_PASSWORD = "GOUxxWdF4sxe3dVP"
TIDB_DATABASE = "test"

# Database URLs for TiDB Cloud with SSL configuration
SYNC_DATABASE_URL = (
    f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}"
    "?charset=utf8mb4&ssl_verify_cert=true&ssl_verify_identity=true"
)
ASYNC_DATABASE_URL = SYNC_DATABASE_URL  # Use sync URL for both in hackathon mode

# TiDB Cloud engine configuration with proper SSL handling
CA_CERT_PATH = os.path.join(os.path.dirname(__file__), "tidb-ca.pem")

engine_config = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "echo": settings.DEBUG,
    "connect_args": {
        "ssl": {
            "ca": CA_CERT_PATH,
            "verify_identity": True
        }
    }
}

# Create engines - using sync engine for both in hackathon mode
sync_engine = create_engine(SYNC_DATABASE_URL, **engine_config)
async_engine = sync_engine  # Use sync engine for both in hackathon mode

# Session makers - using sync session for both in hackathon mode
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# No cursor result wrapper needed in hackathon mode - just return results directly

class AsyncSessionWrapper:
    """Wrapper to provide async interface for sync sessions in hackathon mode."""
    def __init__(self, session):
        self.session = session
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    async def execute(self, *args, **kwargs):
        result = self.session.execute(*args, **kwargs)
        class AsyncResult:
            def scalar(self):
                return result.scalar()
        return AsyncResult()
    
    async def close(self):
        self.session.close()
    
    def begin(self):
        return self.session.begin()

def AsyncSessionLocal():
    """Factory for async session wrapper."""
    return AsyncSessionWrapper(SessionLocal())

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


class DatabaseManager:
    """Database connection and session management."""
    
    @staticmethod
    def get_sync_session() -> Session:
        """Get synchronous database session with connection validation."""
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1"))  # Verify connection
            return session
        except Exception as e:
            logger.error(f"Failed to create sync session: {str(e)}")
            raise
    
    @staticmethod
    async def get_async_session() -> AsyncSessionWrapper:
        """Get session with connection validation (using sync session in hackathon mode)."""
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1"))  # Verify connection
            return AsyncSessionWrapper(session)
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise
    
    @staticmethod
    async def close_async_engine():
        """Close async engine connections."""
        try:
            await async_engine.dispose()
        except Exception as e:
            logger.error(f"Failed to close async engine: {str(e)}")
            raise
    
    @staticmethod
    def close_sync_engine():
        """Close sync engine connections."""
        try:
            sync_engine.dispose()
        except Exception as e:
            logger.error(f"Failed to close sync engine: {str(e)}")
            raise


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session for FastAPI endpoints."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))  # Validate connection
        yield db
    except Exception as e:
        logger.error(f"Error in database session: {str(e)}")
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSessionWrapper, None]:
    """Async dependency to get database session for FastAPI endpoints (using sync session in hackathon mode)."""
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
    except Exception as e:
        logger.error(f"Error in database session: {str(e)}")
        raise
    finally:
        if session:
            await session.close()


async def check_database_connection() -> bool:
    """Check database health (using sync session in hackathon mode)."""
    session = None
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
    finally:
        if session:
            session.close()


async def init_database():
    """Initialize database tables (using sync engine in hackathon mode)."""
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def init_database_sync():
    """Initialize database tables synchronously."""
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
