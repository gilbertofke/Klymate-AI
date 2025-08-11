"""
Habit Service

This module handles the business logic for habit tracking and CO2 savings calculations.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.repositories.habit_repository import HabitRepository
from app.models.user_habit import UserHabit

class HabitService:
    """Service layer for habit-related operations."""

    def __init__(self, habit_repository: HabitRepository):
        self.repository = habit_repository

    async def log_habit(self, user_id: int, habit_data: Dict) -> UserHabit:
        """
        Log a new habit entry with CO2 savings calculation.
        
        Args:
            user_id: The ID of the user logging the habit
            habit_data: Dictionary containing habit details:
                - habit_category_id: ID of the habit category
                - quantity: Amount of the habit performed
                - unit: Unit of measurement
                - notes: Optional notes (default: None)
                - performed_at: When the habit was performed (default: now)
        """
        # Calculate CO2 savings based on habit category and quantity
        co2_saved = await self._calculate_co2_savings(
            habit_data["habit_category_id"],
            habit_data["quantity"],
            habit_data["unit"]
        )
        
        # Add calculated CO2 savings to habit data
        habit_data["co2_saved"] = co2_saved
        
        # Create habit entry
        return await self.repository.create_habit_entry(user_id, habit_data)

    async def get_user_habit_history(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_id: Optional[int] = None
    ) -> List[UserHabit]:
        """Get habit history for a user with optional filtering."""
        return await self.repository.get_user_habits(
            user_id, start_date, end_date, category_id
        )

    async def get_user_statistics(
        self,
        user_id: int,
        timeframe: str = "week"
    ) -> Dict:
        """Get habit statistics for a user."""
        return await self.repository.get_habit_statistics(user_id, timeframe)

    async def delete_habit(self, habit_id: int, user_id: int) -> bool:
        """Delete a habit entry."""
        return await self.repository.delete_habit_entry(habit_id, user_id)

    async def _calculate_co2_savings(
        self,
        category_id: int,
        quantity: float,
        unit: str
    ) -> float:
        """
        Calculate CO2 savings for a habit entry.
        
        This is a simplified calculation - in a real implementation,
        we would have more complex calculations based on:
        - Regional carbon intensity factors
        - Seasonal variations
        - More precise conversion factors
        """
        # Example CO2 savings calculations (kg CO2e)
        # These would normally come from a database or environmental API
        SAVINGS_FACTORS = {
            1: {"unit": "km", "factor": 0.2},      # Biking instead of driving
            2: {"unit": "kwh", "factor": 0.5},     # Energy saving
            3: {"unit": "kg", "factor": 2.5},      # Plant-based meal
            4: {"unit": "kg", "factor": 1.0}       # Recycling
        }
        
        if category_id in SAVINGS_FACTORS:
            factor = SAVINGS_FACTORS[category_id]["factor"]
            if unit == SAVINGS_FACTORS[category_id]["unit"]:
                return quantity * factor
            else:
                # Handle unit conversion if needed
                # For now, just return a basic calculation
                return quantity * factor
        
        return 0.0  # Default if category not found
