"""
Test database configuration using TiDB
"""

import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

# TiDB Cloud test configuration
TIDB_HOST = "gateway01.us-west-2.prod.aws.tidbcloud.com"
TIDB_PORT = 4000
TIDB_USER = "4AUZ2qQ2S6Pst2e.root"
TIDB_PASSWORD = "GOUxxWdF4sxe3dVP"
TIDB_DATABASE = "klymate_ai_tangus"  # Using the actual database

# SSL Certificate path
CA_CERT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "tidb-ca.pem"))

print(f"Using CA certificate path: {CA_CERT_PATH}")
print(f"Certificate exists: {os.path.exists(CA_CERT_PATH)}")

# TiDB Cloud connection URL with SSL configuration
TEST_DATABASE_URL = (
    f"mysql+aiomysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}"
    "?charset=utf8mb4&ssl=true"
)

# Create an SSL context explicitly
ssl_context = ssl.create_default_context(cafile=CA_CERT_PATH)
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create test engine with TiDB configuration
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={
        "ssl": ssl_context
    }
)

# Create test session
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_test_db():
    """Initialize test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_test_db():
    """Get test database session."""
    async with TestingSessionLocal() as session:
        yield session
