"""
Habit Schemas

This module defines the Pydantic models for habit-related request/response validation.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class HabitBase(BaseModel):
    """Base schema for habit data."""
    habit_category_id: int
    quantity: float = Field(..., gt=0)
    unit: str
    notes: Optional[str] = None
    performed_at: Optional[datetime] = None

class HabitCreate(HabitBase):
    """Schema for creating a new habit entry."""
    pass

class HabitResponse(HabitBase):
    """Schema for habit entry responses."""
    id: int
    user_id: int
    co2_saved: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HabitList(BaseModel):
    """Schema for list of habits."""
    habits: List[HabitResponse]

    class Config:
        from_attributes = True

class HabitStatistics(BaseModel):
    """Schema for habit statistics."""
    timeframe: str
    start_date: datetime
    end_date: datetime
    total_entries: int
    total_co2_saved: float
    avg_co2_saved: float
    categories: Dict[str, float]

    class Config:
        from_attributes = True
