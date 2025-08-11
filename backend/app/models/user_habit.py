"""
User Habit Model

This module defines the UserHabit model for tracking user's habit activities and their CO2 savings.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from app.models.habit import Habit

class UserHabit(Base, TimestampMixin):
    """
    UserHabit model for tracking individual habit activities.
    
    Attributes:
        id: Unique identifier for the habit log
        user_id: Foreign key to the User who logged the habit
        habit_id: Foreign key to the Habit that was logged
        quantity: The amount or duration of the habit activity (e.g., kilometers cycled)
        notes: Optional notes about the activity
        logged_at: When the activity was performed
        co2_saved: Calculated CO2 savings in kilograms
    """
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False)
    notes = Column(Text)
    logged_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    co2_saved = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="habits")
    habit = relationship("Habit", back_populates="user_habits")

    def __init__(self, **kwargs):
        """Initialize the UserHabit with validation."""
        super().__init__(**kwargs)
        if self.quantity is not None and self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.habit_id is None:
            raise ValueError("Habit ID cannot be None")
        if not self.logged_at:
            self.logged_at = datetime.now(timezone.utc)
        self.co2_saved = self.calculate_carbon_impact()

    def calculate_carbon_impact(self) -> float:
        """
        Calculate the CO2 savings for this habit activity.
        
        Returns:
            float: CO2 savings in kilograms
        """
        if not hasattr(self, 'habit') or not self.habit:
            return 0.0
        
        return self.quantity * self.habit.carbon_impact

    def to_dict(self) -> dict:
        """
        Convert the UserHabit instance to a dictionary.
        
        Returns:
            dict: Dictionary representation of the UserHabit
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "habit_id": self.habit_id,
            "quantity": self.quantity,
            "notes": self.notes,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
            "co2_saved": self.co2_saved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "habit": self.habit.to_dict() if self.habit else None
        }

    def __repr__(self) -> str:
        """String representation of the UserHabit."""
        return f"<UserHabit(id={self.id}, user_id={self.user_id}, habit_id={self.habit_id}, quantity={self.quantity}, co2_saved={self.co2_saved}kg)>"
