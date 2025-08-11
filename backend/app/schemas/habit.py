"""
Habit Schemas

This module defines the Pydantic models for habit-related request/response validation.
Aligned with Task 5 foundation and updated models.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal

from app.models.base import BaseSchema, TimestampSchema, BaseResponseSchema


class HabitCategoryBase(BaseSchema):
    """Base schema for habit category data."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_type: str = Field(..., description="Category type: transport, diet, energy, lifestyle")
    co2_impact_per_unit: float = Field(..., gt=0, description="CO2 savings per unit in kg")
    unit_type: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")


class HabitCategoryCreate(HabitCategoryBase):
    """Schema for creating a new habit category."""
    pass


class HabitCategoryResponse(HabitCategoryBase, BaseResponseSchema):
    """Schema for habit category responses."""
    
    class Config:
        from_attributes = True


class HabitBase(BaseSchema):
    """Base schema for habit entry data."""
    category_id: int = Field(..., gt=0, description="ID of the habit category")
    quantity: float = Field(..., gt=0, description="Quantity of the habit performed")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes about the activity")
    logged_date: Optional[date] = Field(None, description="Date when the habit was performed")
    
    @validator('logged_date', pre=True, always=True)
    def set_logged_date(cls, v):
        """Set default logged_date to today if not provided."""
        return v or date.today()


class HabitCreate(HabitBase):
    """Schema for creating a new habit entry."""
    pass


class HabitUpdate(BaseSchema):
    """Schema for updating a habit entry."""
    quantity: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=1000)
    logged_date: Optional[date] = None


class HabitResponse(HabitBase, BaseResponseSchema):
    """Schema for habit entry responses."""
    user_id: int
    co2_saved: float = Field(..., description="Calculated CO2 savings in kg")
    category: Optional[HabitCategoryResponse] = None
    
    class Config:
        from_attributes = True


class HabitList(BaseSchema):
    """Schema for list of habits."""
    habits: List[HabitResponse]
    total_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class HabitStatistics(BaseSchema):
    """Schema for habit statistics."""
    timeframe: str = Field(..., description="Time period for statistics")
    start_date: str = Field(..., description="Start date of the period")
    end_date: str = Field(..., description="End date of the period")
    total_entries: int = Field(..., description="Total number of habit entries")
    total_co2_saved: float = Field(..., description="Total CO2 saved in kg")
    avg_co2_saved: float = Field(..., description="Average CO2 saved per entry")
    categories: Dict[str, Dict[str, Any]] = Field(..., description="Breakdown by category")
    insights: Optional[Dict[str, Any]] = Field(None, description="Generated insights")
    
    class Config:
        from_attributes = True


class HabitCategoryList(BaseSchema):
    """Schema for list of habit categories."""
    categories: List[HabitCategoryResponse]
    total_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class HabitInsights(BaseSchema):
    """Schema for habit insights and recommendations."""
    performance: str = Field(..., description="Performance level")
    consistency: str = Field(..., description="Consistency level")
    top_category: Optional[str] = Field(None, description="Top performing category")
    top_category_savings: Optional[float] = Field(None, description="CO2 savings from top category")
    equivalent_trees: Optional[float] = Field(None, description="Equivalent trees planted")
    equivalent_miles: Optional[float] = Field(None, description="Equivalent miles not driven")
    recommendations: Optional[List[str]] = Field(None, description="Personalized recommendations")
    
    class Config:
        from_attributes = True
