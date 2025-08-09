"""
Database Initialization Utilities

This module provides utilities for initializing the database,
creating tables, and managing database lifecycle.
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import (
    async_engine, 
    sync_engine, 
    Base, 
    AsyncSessionLocal, 
    SessionLocal,
    check_database_connection
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Database initialization and management utilities."""
    
    @staticmethod
    async def create_database_if_not_exists():
        """Create database if it doesn't exist (for development)."""
        try:
            # For TiDB Cloud, database should already exist
            # This is mainly for local development
            logger.info(f"Connecting to database: {settings.TIDB_DATABASE}")
            
            # Test connection
            connection_ok = await check_database_connection()
            if connection_ok:
                logger.info("Database connection successful")
            else:
                logger.error("Database connection failed")
                raise Exception("Cannot connect to database")
                
        except Exception as e:
            logger.error(f"Database creation/connection failed: {str(e)}")
            raise
    
    @staticmethod
    async def create_tables():
        """Create all database tables."""
        try:
            async with async_engine.begin() as conn:
                # Import all models to ensure they're registered
                # from app.models import user  # Will be created later
                # Add other model imports here
                
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
    @staticmethod
    async def drop_tables():
        """Drop all database tables (for testing/development)."""
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Database tables dropped successfully")
                
        except Exception as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            raise
    
    @staticmethod
    async def reset_database():
        """Reset database by dropping and recreating tables."""
        try:
            await DatabaseInitializer.drop_tables()
            await DatabaseInitializer.create_tables()
            logger.info("Database reset completed successfully")
            
        except Exception as e:
            logger.error(f"Database reset failed: {str(e)}")
            raise
    
    @staticmethod
    async def check_database_health() -> dict:
        """Check database health and return status."""
        try:
            async with AsyncSessionLocal() as session:
                # Test basic query
                result = await session.execute(text("SELECT 1 as health_check"))
                health_check = result.scalar()
                
                # Test table existence
                tables_result = await session.execute(
                    text("SHOW TABLES")
                )
                tables = [row[0] for row in tables_result.fetchall()]
                
                return {
                    "status": "healthy",
                    "connection": "ok",
                    "health_check": health_check,
                    "tables_count": len(tables),
                    "tables": tables,
                    "database": settings.TIDB_DATABASE,
                    "host": settings.TIDB_HOST
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e),
                "database": settings.TIDB_DATABASE,
                "host": settings.TIDB_HOST
            }
    
    @staticmethod
    async def initialize_for_development():
        """Initialize database for development environment."""
        try:
            logger.info("Initializing database for development...")
            
            # Check/create database
            await DatabaseInitializer.create_database_if_not_exists()
            
            # Create tables
            await DatabaseInitializer.create_tables()
            
            logger.info("Development database initialization completed")
            
        except Exception as e:
            logger.error(f"Development database initialization failed: {str(e)}")
            raise
    
    @staticmethod
    async def initialize_for_testing():
        """Initialize database for testing environment."""
        try:
            logger.info("Initializing database for testing...")
            
            # Reset database for clean tests
            await DatabaseInitializer.reset_database()
            
            logger.info("Testing database initialization completed")
            
        except Exception as e:
            logger.error(f"Testing database initialization failed: {str(e)}")
            raise


# CLI functions for database management
async def init_db():
    """Initialize database (CLI command)."""
    try:
        await DatabaseInitializer.initialize_for_development()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise


async def reset_db():
    """Reset database (CLI command)."""
    try:
        await DatabaseInitializer.reset_database()
        print("✅ Database reset successfully")
    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        raise


async def check_db():
    """Check database health (CLI command)."""
    try:
        health = await DatabaseInitializer.check_database_health()
        print(f"Database Status: {health['status']}")
        print(f"Connection: {health['connection']}")
        print(f"Database: {health['database']}")
        print(f"Host: {health['host']}")
        if health['status'] == 'healthy':
            print(f"Tables: {health['tables_count']}")
            if health['tables']:
                print(f"Table list: {', '.join(health['tables'])}")
        else:
            print(f"Error: {health.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Database health check failed: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python database_init.py [init|reset|check]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        asyncio.run(init_db())
    elif command == "reset":
        asyncio.run(reset_db())
    elif command == "check":
        asyncio.run(check_db())
    else:
        print("Invalid command. Use: init, reset, or check")
        sys.exit(1)