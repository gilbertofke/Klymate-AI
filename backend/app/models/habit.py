"""
Habit Models

This module defines the Habit and HabitCategory models for the habit tracking system.
"""

from enum import Enum
from sqlalchemy import Column, Integer, Float, String, Enum as SQLAEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class HabitCategory(str, Enum):
    """Categories for different types of eco-friendly habits."""
    TRANSPORT = "transport"
    ENERGY = "energy"
    FOOD = "food"
    WASTE = "waste"
    LIFESTYLE = "lifestyle"

class Habit(Base, TimestampMixin):
    """
    Habit model for defining eco-friendly activities.
    
    Attributes:
        id: Unique identifier for the habit
        user_id: Foreign key to the User who created the habit
        name: Name of the habit
        description: Detailed description of the habit
        category: Type of habit (transport, energy, etc.)
        carbon_impact: CO2 savings per unit of activity (kg)
        frequency: How often the habit should be performed
    """
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(SQLAEnum(HabitCategory), nullable=False)
    carbon_impact = Column(Float, nullable=False)  # kg CO2 saved per unit
    frequency = Column(String(50))  # daily, weekly, monthly, etc.

    # Relationships
    user = relationship("User", back_populates="created_habits")
    user_habits = relationship("UserHabit", back_populates="habit", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert the Habit instance to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "carbon_impact": self.carbon_impact,
            "frequency": self.frequency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """String representation of the Habit."""
        return f"<Habit(id={self.id}, name='{self.name}', category={self.category}, impact={self.carbon_impact}kg)>"
