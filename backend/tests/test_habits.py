"""
Habit Integration Tests

This module contains comprehensive tests for the habit tracking functionality,
following Task 5 patterns and using proper async testing.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import HabitCategory, CategoryType
from app.models.user_habit import UserHabit
from app.repositories.habit_repository import HabitRepository, HabitCategoryRepository
from app.services.habit_service import HabitService
from app.schemas.habit import HabitCreate


class TestHabitModels:
    """Test cases for Habit model functionality."""
    
    @pytest.mark.asyncio
    async def test_habit_category_creation(self, async_db_session):
        """Test creating a habit category."""
        category = HabitCategory(
            name="Test Cycling",
            description="Cycling instead of driving",
            category_type=CategoryType.TRANSPORT,
            co2_impact_per_unit=Decimal("0.21"),
            unit_type="km"
        )
        
        async_db_session.add(category)
        await async_db_session.commit()
        await async_db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Test Cycling"
        assert category.category_type == CategoryType.TRANSPORT
        assert category.co2_impact_per_unit == Decimal("0.21")
        assert category.unit_type == "km"
    
    @pytest.mark.asyncio
    async def test_user_habit_creation(self, async_db_session, sample_user, sample_habit_category):
        """Test creating a user habit entry."""
        habit = UserHabit(
            user_id=sample_user.id,
            category_id=sample_habit_category.id,
            quantity=Decimal("10.5"),
            co2_saved=Decimal("2.205"),  # 10.5 * 0.21
            logged_date=date.today(),
            notes="Morning bike ride"
        )
        
        async_db_session.add(habit)
        await async_db_session.commit()
        await async_db_session.refresh(habit)
        
        assert habit.id is not None
        assert habit.user_id == sample_user.id
        assert habit.category_id == sample_habit_category.id
        assert habit.quantity == Decimal("10.5")
        assert habit.notes == "Morning bike ride"
    
    @pytest.mark.asyncio
    async def test_co2_calculation(self, sample_habit_category):
        """Test CO2 savings calculation."""
        quantity = 15.0
        expected_savings = Decimal("3.15")  # 15.0 * 0.21
        
        calculated_savings = sample_habit_category.calculate_co2_savings(quantity)
        
        assert calculated_savings == expected_savings


class TestHabitRepository:
    """Test cases for HabitRepository functionality."""
    
    @pytest.mark.asyncio
    async def test_create_habit_entry(self, async_db_session, sample_user, sample_habit_category):
        """Test creating a habit entry through repository."""
        repository = HabitRepository(async_db_session)
        
        habit_data = {
            "category_id": sample_habit_category.id,
            "quantity": 8.5,
            "co2_saved": 1.785,  # 8.5 * 0.21
            "notes": "Evening commute"
        }
        
        habit = await repository.create_habit_entry(sample_user.id, habit_data)
        
        assert habit.id is not None
        assert habit.user_id == sample_user.id
        assert habit.category_id == sample_habit_category.id
        assert float(habit.quantity) == 8.5
        assert habit.notes == "Evening commute"
    
    @pytest.mark.asyncio
    async def test_get_user_habits(self, async_db_session, sample_user, sample_habit_category):
        """Test retrieving user habits."""
        repository = HabitRepository(async_db_session)
        
        # Create test habits
        for i in range(3):
            habit_data = {
                "category_id": sample_habit_category.id,
                "quantity": 5.0 * (i + 1),
                "co2_saved": 5.0 * (i + 1) * 0.21,
                "logged_date": date.today() - timedelta(days=i)
            }
            await repository.create_habit_entry(sample_user.id, habit_data)
        
        # Retrieve habits
        habits = await repository.get_user_habits(sample_user.id)
        
        assert len(habits) == 3
        assert all(habit.user_id == sample_user.id for habit in habits)
    
    @pytest.mark.asyncio
    async def test_get_habit_statistics(self, async_db_session, sample_user, sample_habit_category):
        """Test getting habit statistics."""
        repository = HabitRepository(async_db_session)
        
        # Create test habits
        total_co2 = 0
        for i in range(5):
            co2_saved = (i + 1) * 0.5
            total_co2 += co2_saved
            habit_data = {
                "category_id": sample_habit_category.id,
                "quantity": i + 1,
                "co2_saved": co2_saved,
                "logged_date": date.today() - timedelta(days=i)
            }
            await repository.create_habit_entry(sample_user.id, habit_data)
        
        # Get statistics
        stats = await repository.get_habit_statistics(sample_user.id, "week")
        
        assert stats["total_entries"] == 5
        assert abs(stats["total_co2_saved"] - total_co2) < 0.01
        assert stats["timeframe"] == "week"
        assert "categories" in stats


class TestHabitService:
    """Test cases for HabitService functionality."""
    
    @pytest.mark.asyncio
    async def test_log_habit(self, async_db_session, sample_user, sample_habit_category):
        """Test logging a habit through service."""
        service = HabitService(async_db_session)
        
        habit_data = HabitCreate(
            category_id=sample_habit_category.id,
            quantity=12.0,
            notes="Test ride"
        )
        
        habit = await service.log_habit(sample_user.id, habit_data)
        
        assert habit.id is not None
        assert habit.user_id == sample_user.id
        assert float(habit.quantity) == 12.0
        assert float(habit.co2_saved) == 12.0 * 0.21  # Calculated automatically
    
    @pytest.mark.asyncio
    async def test_get_habit_categories(self, async_db_session, sample_habit_category):
        """Test getting habit categories."""
        service = HabitService(async_db_session)
        
        categories = await service.get_habit_categories()
        
        assert len(categories) >= 1
        assert any(cat.id == sample_habit_category.id for cat in categories)
    
    @pytest.mark.asyncio
    async def test_get_user_statistics_with_insights(self, async_db_session, sample_user, sample_habit_category):
        """Test getting statistics with insights."""
        service = HabitService(async_db_session)
        
        # Create habits with significant CO2 savings
        for i in range(10):
            habit_data = HabitCreate(
                category_id=sample_habit_category.id,
                quantity=10.0,
                notes=f"Test habit {i}"
            )
            await service.log_habit(sample_user.id, habit_data)
        
        stats = await service.get_user_statistics(sample_user.id, "week")
        
        assert stats["total_entries"] == 10
        assert stats["total_co2_saved"] > 20  # Should be 21.0 (10 * 10 * 0.21)
        assert "insights" in stats
        assert "performance" in stats["insights"]


# Fixtures for testing
@pytest.fixture
async def sample_habit_category(async_db_session):
    """Create a sample habit category for testing."""
    category = HabitCategory(
        name="Test Cycling Category",
        description="Test category for cycling",
        category_type=CategoryType.TRANSPORT,
        co2_impact_per_unit=Decimal("0.21"),
        unit_type="km"
    )
    
    async_db_session.add(category)
    await async_db_session.commit()
    await async_db_session.refresh(category)
    return category


@pytest.fixture
async def sample_user(async_db_session):
    """Create a sample user for testing."""
    from app.models.user import User
    
    user = User(
        firebase_uid="test_habit_user_123",
        email="habituser@example.com",
        name="Habit Test User"
    )
    
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


# API Integration Tests
class TestHabitAPI:
    """Test cases for Habit API endpoints."""
    
    @pytest.mark.asyncio
    async def test_log_habit_endpoint(self, async_client: AsyncClient, auth_headers, sample_habit_category):
        """Test the log habit API endpoint."""
        habit_data = {
            "category_id": sample_habit_category.id,
            "quantity": 15.5,
            "notes": "API test ride"
        }
        
        response = await async_client.post(
            "/api/v1/habits/log",
            headers=auth_headers,
            json=habit_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["quantity"] == habit_data["quantity"]
        assert data["notes"] == habit_data["notes"]
        assert data["co2_saved"] > 0
    
    @pytest.mark.asyncio
    async def test_get_habit_categories_endpoint(self, async_client: AsyncClient, sample_habit_category):
        """Test the get habit categories API endpoint."""
        response = await async_client.get("/api/v1/habits/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_habit_statistics_endpoint(self, async_client: AsyncClient, auth_headers):
        """Test the get habit statistics API endpoint."""
        response = await async_client.get(
            "/api/v1/habits/statistics?timeframe=week",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        assert "total_co2_saved" in data
        assert "insights" in data


@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing."""
    return {"Authorization": "Bearer test_token_123"}
