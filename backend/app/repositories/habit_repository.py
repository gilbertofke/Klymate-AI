"""
Habit Repository Implementation

This module provides the HabitRepository and HabitCategoryRepository classes that handle all database
operations related to habit tracking, extending the base repository pattern from Task 5.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal

from app.repositories.base_repository import BaseRepository
from app.models.habit import HabitCategory, CategoryType
from app.models.user_habit import UserHabit
from app.schemas.habit import HabitCreate

logger = logging.getLogger(__name__)


class HabitCategoryRepository(BaseRepository[HabitCategory]):
    """
    Repository for HabitCategory entity operations.
    
    Extends BaseRepository to provide habit category-specific database operations.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize HabitCategoryRepository with HabitCategory model."""
        super().__init__(HabitCategory, db_session)
    
    async def get_by_category_type(self, category_type: CategoryType) -> List[HabitCategory]:
        """
        Get habit categories by category type.
        
        Args:
            category_type: Type of category (transport, diet, energy, lifestyle)
            
        Returns:
            List of HabitCategory instances
        """
        try:
            query = select(HabitCategory).where(
                and_(
                    HabitCategory.category_type == category_type,
                    HabitCategory.is_deleted == False
                )
            ).order_by(HabitCategory.name)
            
            result = await self.db.execute(query)
            categories = result.scalars().all()
            
            logger.debug(f"Retrieved {len(categories)} categories for type: {category_type}")
            return list(categories)
            
        except Exception as e:
            logger.error(f"Error getting categories by type {category_type}: {str(e)}")
            raise
    
    async def get_all_active(self) -> List[HabitCategory]:
        """
        Get all active habit categories.
        
        Returns:
            List of all active HabitCategory instances
        """
        try:
            return await self.get_multi(
                filters={"is_deleted": False},
                order_by="name"
            )
        except Exception as e:
            logger.error(f"Error getting all active categories: {str(e)}")
            raise


class HabitRepository(BaseRepository[UserHabit]):
    """
    Repository for UserHabit entity operations.
    
    Extends BaseRepository to provide user habit-specific database operations
    including logging, history retrieval, and statistics.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize HabitRepository with UserHabit model."""
        super().__init__(UserHabit, db_session)
    
    def _add_relationship_loading(self, query):
        """Add relationship loading for UserHabit queries."""
        return query.options(selectinload(UserHabit.category))
    
    async def create_habit_entry(self, user_id: int, habit_data: Dict[str, Any]) -> UserHabit:
        """
        Create a new habit entry for a user.
        
        Args:
            user_id: User's ID
            habit_data: Dictionary containing habit entry data
            
        Returns:
            Created UserHabit instance
        """
        try:
            # Prepare habit entry data
            entry_data = {
                "user_id": user_id,
                "category_id": habit_data["category_id"],
                "quantity": Decimal(str(habit_data["quantity"])),
                "logged_date": habit_data.get("logged_date", date.today()),
                "notes": habit_data.get("notes"),
                "co2_saved": Decimal(str(habit_data.get("co2_saved", 0)))
            }
            
            # Set audit fields
            entry_data["created_by"] = str(user_id)
            
            habit_entry = await self.create(entry_data)
            
            logger.info(f"Created habit entry for user {user_id}: {habit_entry.id}")
            return habit_entry
            
        except Exception as e:
            logger.error(f"Error creating habit entry for user {user_id}: {str(e)}")
            raise
    
    async def get_user_habits(
        self, 
        user_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        limit: int = 100
    ) -> List[UserHabit]:
        """
        Get habit entries for a user with optional filtering.
        
        Args:
            user_id: User's ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            category_id: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of UserHabit instances
        """
        try:
            filters = {"user_id": user_id, "is_deleted": False}
            
            # Build query with filters
            query = select(UserHabit).where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.is_deleted == False
                )
            )
            
            if start_date:
                query = query.where(UserHabit.logged_date >= start_date)
            if end_date:
                query = query.where(UserHabit.logged_date <= end_date)
            if category_id:
                query = query.where(UserHabit.category_id == category_id)
            
            # Add relationship loading and ordering
            query = self._add_relationship_loading(query)
            query = query.order_by(desc(UserHabit.logged_date)).limit(limit)
            
            result = await self.db.execute(query)
            habits = result.scalars().all()
            
            logger.debug(f"Retrieved {len(habits)} habits for user {user_id}")
            return list(habits)
            
        except Exception as e:
            logger.error(f"Error getting user habits for user {user_id}: {str(e)}")
            raise
    
    async def get_habit_statistics(
        self, 
        user_id: int,
        timeframe: str = "week"
    ) -> Dict[str, Any]:
        """
        Get habit statistics for a user.
        
        Args:
            user_id: User's ID
            timeframe: Time period ("day", "week", "month", "year")
            
        Returns:
            Dictionary containing habit statistics
        """
        try:
            # Calculate date range
            end_date = date.today()
            if timeframe == "day":
                start_date = end_date - timedelta(days=1)
            elif timeframe == "week":
                start_date = end_date - timedelta(weeks=1)
            elif timeframe == "month":
                start_date = end_date - timedelta(days=30)
            else:  # year
                start_date = end_date - timedelta(days=365)

            # Query for basic statistics
            stats_query = select(
                func.count(UserHabit.id).label("total_entries"),
                func.sum(UserHabit.co2_saved).label("total_co2_saved"),
                func.avg(UserHabit.co2_saved).label("avg_co2_saved")
            ).where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.logged_date.between(start_date, end_date),
                    UserHabit.is_deleted == False
                )
            )
            
            result = await self.db.execute(stats_query)
            stats = result.first()
            
            # Query for category breakdown
            category_query = select(
                HabitCategory.name,
                HabitCategory.category_type,
                func.sum(UserHabit.co2_saved).label("co2_saved"),
                func.count(UserHabit.id).label("entry_count")
            ).join(
                HabitCategory,
                UserHabit.category_id == HabitCategory.id
            ).where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.logged_date.between(start_date, end_date),
                    UserHabit.is_deleted == False
                )
            ).group_by(HabitCategory.name, HabitCategory.category_type)
            
            category_result = await self.db.execute(category_query)
            categories = {}
            for row in category_result:
                categories[row.name] = {
                    "co2_saved": float(row.co2_saved) if row.co2_saved else 0.0,
                    "entry_count": row.entry_count,
                    "category_type": row.category_type.value if row.category_type else None
                }

            statistics = {
                "timeframe": timeframe,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_entries": stats.total_entries or 0,
                "total_co2_saved": float(stats.total_co2_saved) if stats.total_co2_saved else 0.0,
                "avg_co2_saved": float(stats.avg_co2_saved) if stats.avg_co2_saved else 0.0,
                "categories": categories
            }
            
            logger.debug(f"Generated statistics for user {user_id}: {statistics}")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting habit statistics for user {user_id}: {str(e)}")
            raise
    
    async def get_user_habits_by_date_range(
        self, 
        user_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[UserHabit]:
        """
        Get user habits within a specific date range.
        
        Args:
            user_id: User's ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of UserHabit instances
        """
        return await self.get_user_habits(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_recent_habits(self, user_id: int, limit: int = 10) -> List[UserHabit]:
        """
        Get user's most recent habit entries.
        
        Args:
            user_id: User's ID
            limit: Maximum number of results
            
        Returns:
            List of recent UserHabit instances
        """
        return await self.get_user_habits(user_id=user_id, limit=limit)
    
    async def delete_habit_entry(self, habit_id: int, user_id: int) -> bool:
        """
        Soft delete a habit entry ensuring it belongs to the user.
        
        Args:
            habit_id: Habit entry ID
            user_id: User's ID for ownership verification
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            habit = await self.get_by_id(habit_id)
            if not habit or habit.user_id != user_id:
                logger.warning(f"Habit {habit_id} not found or doesn't belong to user {user_id}")
                return False
            
            # Soft delete using the model's method
            habit.soft_delete()
            habit.set_updated_by(str(user_id))
            
            await self.db.commit()
            
            logger.info(f"Soft deleted habit entry {habit_id} for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting habit entry {habit_id}: {str(e)}")
            raise
