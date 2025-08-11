import os
import sys
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.test_db import init_test_db, get_test_db

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_app():
    return app

@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_test_db():
    await init_test_db()
    yield

@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async for session in get_test_db():
        yield session
