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
    async def get_user_habits_summary(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get a summary of user's habits for AI coaching context.
        
        Args:
            user_id: User's ID
            
        Returns:
            List of habit summary dictionaries
        """
        try:
            # Get recent habits (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            habits = await self.get_user_habits(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                limit=50
            )
            
            # Convert to summary format
            summary = []
            for habit in habits:
                summary.append({
                    "category": habit.category.name if habit.category else "Unknown",
                    "category_type": habit.category.category_type.value if habit.category and habit.category.category_type else "general",
                    "quantity": float(habit.quantity),
                    "co2_saved": float(habit.co2_saved),
                    "logged_date": habit.logged_date,
                    "notes": habit.notes
                })
            
            logger.debug(f"Generated habits summary for user {user_id}: {len(summary)} entries")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting habits summary for user {user_id}: {str(e)}")
            return []
    
    async def get_user_habit_trends(self, user_id: int, days_back: int = 30) -> Dict[str, Any]:
        """
        Get user's habit trends for AI analysis.
        
        Args:
            user_id: User's ID
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            # Get habits in the period
            habits = await self.get_user_habits(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if not habits:
                return {
                    "total_habits": 0,
                    "avg_daily_habits": 0,
                    "top_categories": [],
                    "trend_direction": "no_data",
                    "co2_saved_total": 0,
                    "co2_saved_avg_daily": 0
                }
            
            # Calculate basic metrics
            total_habits = len(habits)
            avg_daily_habits = total_habits / days_back
            total_co2_saved = sum(float(habit.co2_saved) for habit in habits)
            avg_daily_co2_saved = total_co2_saved / days_back
            
            # Analyze categories
            category_counts = {}
            for habit in habits:
                category = habit.category.category_type.value if habit.category and habit.category.category_type else "general"
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Get top categories
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            top_categories = [cat[0] for cat in top_categories]
            
            # Simple trend analysis (compare first half vs second half)
            mid_date = start_date + timedelta(days=days_back // 2)
            first_half = [h for h in habits if h.logged_date < mid_date]
            second_half = [h for h in habits if h.logged_date >= mid_date]
            
            if len(first_half) > 0 and len(second_half) > 0:
                first_half_avg = len(first_half) / (days_back // 2)
                second_half_avg = len(second_half) / (days_back - days_back // 2)
                
                if second_half_avg > first_half_avg * 1.1:
                    trend_direction = "improving"
                elif second_half_avg < first_half_avg * 0.9:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "insufficient_data"
            
            trends = {
                "total_habits": total_habits,
                "avg_daily_habits": round(avg_daily_habits, 2),
                "top_categories": top_categories,
                "trend_direction": trend_direction,
                "co2_saved_total": round(total_co2_saved, 2),
                "co2_saved_avg_daily": round(avg_daily_co2_saved, 2),
                "analysis_period_days": days_back,
                "category_breakdown": category_counts
            }
            
            logger.debug(f"Generated habit trends for user {user_id}: {trends}")
            return trends
            
        except Exception as e:
            logger.error(f"Error getting habit trends for user {user_id}: {str(e)}")
            return {}
    
    async def get_user_recent_habits(self, user_id: int, days: int = 7) -> List[UserHabit]:
        """
        Get user's recent habits within specified days.
        
        Args:
            user_id: User's ID
            days: Number of recent days to include
            
        Returns:
            List of recent UserHabit instances
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            return await self.get_user_habits(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            logger.error(f"Error getting recent habits for user {user_id}: {str(e)}")
            return []
    
    async def get_user_habit_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive habit statistics for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary containing comprehensive statistics
        """
        try:
            # Get all-time statistics
            all_time_query = select(
                func.count(UserHabit.id).label("total_habits"),
                func.sum(UserHabit.co2_saved).label("total_co2_saved"),
                func.avg(UserHabit.co2_saved).label("avg_co2_saved")
            ).where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.is_deleted == False
                )
            )
            
            result = await self.db.execute(all_time_query)
            all_time_stats = result.first()
            
            # Get top category
            top_category_query = select(
                HabitCategory.category_type,
                func.count(UserHabit.id).label("count")
            ).join(
                HabitCategory,
                UserHabit.category_id == HabitCategory.id
            ).where(
                and_(
                    UserHabit.user_id == user_id,
                    UserHabit.is_deleted == False
                )
            ).group_by(HabitCategory.category_type).order_by(desc(func.count(UserHabit.id))).limit(1)
            
            top_category_result = await self.db.execute(top_category_query)
            top_category_row = top_category_result.first()
            
            statistics = {
                "total_habits": all_time_stats.total_habits or 0,
                "total_co2_saved": float(all_time_stats.total_co2_saved) if all_time_stats.total_co2_saved else 0.0,
                "avg_co2_saved": float(all_time_stats.avg_co2_saved) if all_time_stats.avg_co2_saved else 0.0,
                "top_category": top_category_row.category_type.value if top_category_row and top_category_row.category_type else "transport"
            }
            
            logger.debug(f"Generated comprehensive statistics for user {user_id}")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting habit statistics for user {user_id}: {str(e)}")
            return {
                "total_habits": 0,
                "total_co2_saved": 0.0,
                "avg_co2_saved": 0.0,
                "top_category": "transport"
            }