
"""Core unit tests that don't require database connectivity."""
import pytest
from decimal import Decimal
from app.models.habit import CategoryType, HabitCategory
from app.schemas.habit import HabitCreate

def test_category_type_enum():
    """Test CategoryType enum values."""
    assert CategoryType.TRANSPORT == "transport"
    assert CategoryType.DIET == "diet"
    assert CategoryType.ENERGY == "energy"
    assert CategoryType.LIFESTYLE == "lifestyle"

def test_co2_calculation():
    """Test CO2 savings calculation."""
    category = HabitCategory()
    category.co2_impact_per_unit = Decimal('2.5')
    result = category.calculate_co2_savings(10.0)
    assert result == Decimal('25.0')

def test_habit_create_schema():
    """Test HabitCreate schema validation."""
    data = {"category_id": 1, "quantity": 10.5}
    habit = HabitCreate(**data)
    assert habit.category_id == 1
    assert habit.quantity == 10.5
