"""
Habit Models

This module defines the HabitCategory and UserHabit models for the habit tracking system.
Aligned with Task 5 BaseModel foundation and design document.
"""

from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, Text, Decimal as SQLDecimal, Date
from sqlalchemy.orm import relationship
from datetime import date
from app.models.base import BaseModel, TimestampMixin, SoftDeleteMixin

class CategoryType(str, Enum):
    """Categories for different types of eco-friendly habits."""
    TRANSPORT = "transport"
    DIET = "diet"
    ENERGY = "energy"
    LIFESTYLE = "lifestyle"

class HabitCategory(BaseModel, TimestampMixin):
    """
    Predefined habit categories with CO2 impact factors.
    
    This model defines the standard categories of eco-friendly activities
    that users can log, along with their carbon impact calculations.
    """
    __tablename__ = "habit_categories"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category_type = Column(SQLAEnum(CategoryType), nullable=False, index=True)
    co2_impact_per_unit = Column(SQLDecimal(8,4), nullable=False)  # kg CO2 saved per unit
    unit_type = Column(String(50), nullable=False)  # 'km', 'meal', 'kwh', etc.
    
    # Relationships
    user_habits = relationship("UserHabit", back_populates="category", cascade="all, delete-orphan")

    def calculate_co2_savings(self, quantity: float) -> Decimal:
        """Calculate CO2 savings for a given quantity."""
        return Decimal(str(quantity)) * self.co2_impact_per_unit

    def to_dict(self) -> dict:
        """Convert the HabitCategory instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_type": self.category_type.value if self.category_type else None,
            "co2_impact_per_unit": float(self.co2_impact_per_unit) if self.co2_impact_per_unit else 0.0,
            "unit_type": self.unit_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """String representation of the HabitCategory."""
        return f"<HabitCategory(id={self.id}, name='{self.name}', type={self.category_type}, impact={self.co2_impact_per_unit}kg/{self.unit_type})>"
