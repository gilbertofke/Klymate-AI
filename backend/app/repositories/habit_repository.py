"""
Habit Repository

This module provides database access and manipulation for habit-related operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.user_habit import UserHabit
from app.models.habit import HabitCategory

class HabitRepository:
    """Repository for habit-related database operations."""

    def __init__(self, db: Session):
        self.db = db

    async def create_habit_entry(self, user_id: int, habit_data: Dict) -> UserHabit:
        """Create a new habit entry for a user."""
        habit = UserHabit(
            user_id=user_id,
            habit_category_id=habit_data["habit_category_id"],
            quantity=habit_data["quantity"],
            unit=habit_data["unit"],
            co2_saved=habit_data["co2_saved"],
            notes=habit_data.get("notes"),
            performed_at=habit_data.get("performed_at", datetime.utcnow())
        )
        self.db.add(habit)
        await self.db.commit()
        await self.db.refresh(habit)
        return habit

    async def get_user_habits(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_id: Optional[int] = None
    ) -> List[UserHabit]:
        """Get habit entries for a user with optional filtering."""
        query = select(UserHabit).where(UserHabit.user_id == user_id)
        
        if start_date:
            query = query.where(UserHabit.performed_at >= start_date)
        if end_date:
            query = query.where(UserHabit.performed_at <= end_date)
        if category_id:
            query = query.where(UserHabit.habit_category_id == category_id)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_habit_statistics(
        self, 
        user_id: int,
        timeframe: str = "week"  # "day", "week", "month", "year"
    ) -> Dict:
        """Get habit statistics for a user."""
        # Calculate date range
        end_date = datetime.utcnow()
        if timeframe == "day":
            start_date = end_date - timedelta(days=1)
        elif timeframe == "week":
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == "month":
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)

        # Query for statistics
        stats_query = select(
            func.count(UserHabit.id).label("total_entries"),
            func.sum(UserHabit.co2_saved).label("total_co2_saved"),
            func.avg(UserHabit.co2_saved).label("avg_co2_saved")
        ).where(
            UserHabit.user_id == user_id,
            UserHabit.performed_at.between(start_date, end_date)
        )
        
        result = await self.db.execute(stats_query)
        stats = result.first()
        
        # Get category breakdown
        category_query = select(
            HabitCategory.name,
            func.sum(UserHabit.co2_saved).label("co2_saved")
        ).join(
            HabitCategory,
            UserHabit.habit_category_id == HabitCategory.id
        ).where(
            UserHabit.user_id == user_id,
            UserHabit.performed_at.between(start_date, end_date)
        ).group_by(HabitCategory.name)
        
        category_result = await self.db.execute(category_query)
        categories = {row.name: row.co2_saved for row in category_result}

        return {
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "total_entries": stats.total_entries or 0,
            "total_co2_saved": stats.total_co2_saved or 0,
            "avg_co2_saved": stats.avg_co2_saved or 0,
            "categories": categories
        }

    async def delete_habit_entry(self, habit_id: int, user_id: int) -> bool:
        """Delete a habit entry ensuring it belongs to the user."""
        query = select(UserHabit).where(
            UserHabit.id == habit_id,
            UserHabit.user_id == user_id
        )
        result = await self.db.execute(query)
        habit = result.scalar_one_or_none()
        
        if habit:
            await self.db.delete(habit)
            await self.db.commit()
            return True
        return False
