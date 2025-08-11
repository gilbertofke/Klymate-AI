"""
User Habit Model

This module defines the UserHabit model for tracking user's habit activities and their CO2 savings.
Aligned with Task 5 BaseModel foundation and design document.
"""

from datetime import date
from decimal import Decimal
from sqlalchemy import Column, Integer, ForeignKey, Text, Decimal as SQLDecimal, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin

class UserHabit(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """
    UserHabit model for tracking individual habit activities.
    
    This model stores user's logged habit activities with calculated CO2 savings,
    following the design document specifications and Task 5 patterns.
    """
    __tablename__ = "user_habits"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("habit_categories.id"), nullable=False, index=True)
    quantity = Column(SQLDecimal(8,2), nullable=False)
    co2_saved = Column(SQLDecimal(8,4), nullable=False)
    logged_date = Column(Date, nullable=False, index=True)
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="user_habits")
    category = relationship("HabitCategory", back_populates="user_habits")

    def __init__(self, **kwargs):
        """Initialize the UserHabit with validation and CO2 calculation."""
        # Set default logged_date if not provided
        if 'logged_date' not in kwargs:
            kwargs['logged_date'] = date.today()
        
        super().__init__(**kwargs)
        
        # Validate quantity
        if self.quantity is not None and self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Calculate CO2 savings if category is available
        if hasattr(self, 'category') and self.category and not kwargs.get('co2_saved'):
            self.co2_saved = self.category.calculate_co2_savings(float(self.quantity))

    def calculate_co2_savings(self) -> Decimal:
        """
        Calculate the CO2 savings for this habit activity.
        
        Returns:
            Decimal: CO2 savings in kilograms
        """
        if not self.category:
            return Decimal('0.0')
        
        return self.category.calculate_co2_savings(float(self.quantity))

    def update_co2_savings(self):
        """Update CO2 savings based on current quantity and category."""
        self.co2_saved = self.calculate_co2_savings()

    def to_dict(self) -> dict:
        """
        Convert the UserHabit instance to a dictionary.
        
        Returns:
            dict: Dictionary representation of the UserHabit
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "quantity": float(self.quantity) if self.quantity else 0.0,
            "co2_saved": float(self.co2_saved) if self.co2_saved else 0.0,
            "logged_date": self.logged_date.isoformat() if self.logged_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "category": self.category.to_dict() if self.category else None
        }

    def __repr__(self) -> str:
        """String representation of the UserHabit."""
        return f"<UserHabit(id={self.id}, user_id={self.user_id}, category_id={self.category_id}, quantity={self.quantity}, co2_saved={self.co2_saved}kg)>"
