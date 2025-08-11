"""
Habit Integration Tests

This module contains integration tests for the habit tracking functionality.
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user_habit import UserHabit
from app.models.habit import HabitCategory

@pytest.fixture
async def test_habit_category(db: Session):
    """Create a test habit category."""
    category = HabitCategory(
        name="Test Biking",
        description="Biking instead of driving",
        co2_factor=0.2,
        unit="km"
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@pytest.mark.asyncio
async def test_log_habit(
    async_client: AsyncClient,
    test_user_token: str,
    test_habit_category: HabitCategory
):
    """Test logging a new habit entry."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    habit_data = {
        "habit_category_id": test_habit_category.id,
        "quantity": 10.5,
        "unit": "km",
        "notes": "Evening bike ride"
    }

    response = await async_client.post(
        f"{settings.API_V1_STR}/habits",
        headers=headers,
        json=habit_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == habit_data["quantity"]
    assert data["unit"] == habit_data["unit"]
    assert data["notes"] == habit_data["notes"]
    assert data["co2_saved"] > 0

@pytest.mark.asyncio
async def test_get_habits(
    async_client: AsyncClient,
    test_user_token: str,
    test_habit_category: HabitCategory,
    db: Session
):
    """Test retrieving habit history."""
    # Create some test habits
    habits = []
    for i in range(3):
        habit = UserHabit(
            user_id=1,  # Assuming test user has ID 1
            habit_category_id=test_habit_category.id,
            quantity=5.0 * (i + 1),
            unit="km",
            co2_saved=1.0 * (i + 1),
            performed_at=datetime.utcnow() - timedelta(days=i)
        )
        db.add(habit)
        habits.append(habit)
    await db.commit()

    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await async_client.get(
        f"{settings.API_V1_STR}/habits",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["habits"]) >= 3  # Might have more from other tests

@pytest.mark.asyncio
async def test_get_statistics(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test retrieving habit statistics."""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await async_client.get(
        f"{settings.API_V1_STR}/habits/statistics",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_entries" in data
    assert "total_co2_saved" in data
    assert "avg_co2_saved" in data
    assert "categories" in data

@pytest.mark.asyncio
async def test_delete_habit(
    async_client: AsyncClient,
    test_user_token: str,
    test_habit_category: HabitCategory,
    db: Session
):
    """Test deleting a habit entry."""
    # Create a habit to delete
    habit = UserHabit(
        user_id=1,  # Assuming test user has ID 1
        habit_category_id=test_habit_category.id,
        quantity=5.0,
        unit="km",
        co2_saved=1.0
    )
    db.add(habit)
    await db.commit()
    await db.refresh(habit)

    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await async_client.delete(
        f"{settings.API_V1_STR}/habits/{habit.id}",
        headers=headers
    )

    assert response.status_code == 200
    
    # Verify deletion
    deleted_check = await async_client.get(
        f"{settings.API_V1_STR}/habits",
        headers=headers
    )
    habits = deleted_check.json()["habits"]
    assert not any(h["id"] == habit.id for h in habits)
