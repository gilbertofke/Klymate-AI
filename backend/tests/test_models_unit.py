"""
Unit tests for models without database connectivity.
These tests focus on model logic, validation, and methods.
"""
import pytest
from decimal import Decimal
from datetime import date, datetime
from app.models.habit import CategoryType, HabitCategory
from app.schemas.habit import HabitCreate, HabitUpdate


class TestCategoryType:
    """Test CategoryType enum."""
    
    def test_category_type_values(self):
        """Test that CategoryType has correct values."""
        assert CategoryType.TRANSPORT == "transport"
        assert CategoryType.DIET == "diet"
        assert CategoryType.ENERGY == "energy"
        assert CategoryType.LIFESTYLE == "lifestyle"


class TestHabitCategoryLogic:
    """Test HabitCategory business logic without database."""
    
    def test_calculate_co2_savings(self):
        """Test CO2 savings calculation."""
        # Create a mock category (without database)
        category = HabitCategory()
        category.co2_impact_per_unit = Decimal('2.5')
        
        # Test calculation
        result = category.calculate_co2_savings(10.0)
        assert result == Decimal('25.0')
        
        # Test with decimal quantity
        result = category.calculate_co2_savings(3.5)
        assert result == Decimal('8.75')
    
    def test_to_dict_method(self):
        """Test to_dict conversion."""
        category = HabitCategory()
        category.id = 1
        category.name = "Cycling to work"
        category.description = "Bike instead of driving"
        category.category_type = CategoryType.TRANSPORT
        category.co2_impact_per_unit = Decimal('2.5')
        category.unit_type = "km"
        category.created_at = datetime(2024, 1, 1, 12, 0, 0)
        category.updated_at = datetime(2024, 1, 2, 12, 0, 0)
        
        result = category.to_dict()
        
        expected = {
            "id": 1,
            "name": "Cycling to work",
            "description": "Bike instead of driving",
            "category_type": "transport",
            "co2_impact_per_unit": 2.5,
            "unit_type": "km",
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-02T12:00:00"
        }
        
        assert result == expected
    
    def test_repr_method(self):
        """Test string representation."""
        category = HabitCategory()
        category.id = 1
        category.name = "Cycling"
        category.category_type = CategoryType.TRANSPORT
        category.co2_impact_per_unit = Decimal('2.5')
        category.unit_type = "km"
        
        result = repr(category)
        expected = "<HabitCategory(id=1, name='Cycling', type=CategoryType.TRANSPORT, impact=2.5kg/km)>"
        assert result == expected


class TestHabitSchemas:
    """Test Pydantic schemas for habits."""
    
    def test_habit_create_schema(self):
        """Test HabitCreate schema validation."""
        data = {
            "category_id": 1,
            "quantity": 10.5,
            "logged_date": "2024-01-01",
            "notes": "Cycled to work"
        }
        
        habit = HabitCreate(**data)
        assert habit.category_id == 1
        assert habit.quantity == 10.5
        assert habit.logged_date == date(2024, 1, 1)
        assert habit.notes == "Cycled to work"
    
    def test_habit_create_minimal(self):
        """Test HabitCreate with minimal required fields."""
        data = {
            "category_id": 1,
            "quantity": 5.0
        }
        
        habit = HabitCreate(**data)
        assert habit.category_id == 1
        assert habit.quantity == 5.0
        assert habit.logged_date is None  # Optional field
        assert habit.notes is None  # Optional field
    
    def test_habit_update_schema(self):
        """Test HabitUpdate schema."""
        data = {
            "quantity": 15.0,
            "notes": "Updated notes"
        }
        
        habit_update = HabitUpdate(**data)
        assert habit_update.quantity == 15.0
        assert habit_update.notes == "Updated notes"
    
    def test_habit_create_validation_errors(self):
        """Test validation errors in HabitCreate."""
        # Test negative quantity
        with pytest.raises(ValueError):
            HabitCreate(category_id=1, quantity=-5.0)
        
        # Test missing required fields
        with pytest.raises(ValueError):
            HabitCreate(quantity=5.0)  # Missing category_id


class TestBusinessLogic:
    """Test business logic calculations."""
    
    def test_co2_savings_calculation_precision(self):
        """Test CO2 calculation maintains precision."""
        category = HabitCategory()
        category.co2_impact_per_unit = Decimal('0.123456')
        
        result = category.calculate_co2_savings(7.89)
        # Should maintain decimal precision
        assert isinstance(result, Decimal)
        assert result == Decimal('0.123456') * Decimal('7.89')
    
    def test_different_category_types(self):
        """Test different category types work correctly."""
        categories = [
            (CategoryType.TRANSPORT, "transport"),
            (CategoryType.DIET, "diet"),
            (CategoryType.ENERGY, "energy"),
            (CategoryType.LIFESTYLE, "lifestyle")
        ]
        
        for category_type, expected_value in categories:
            assert category_type.value == expected_value