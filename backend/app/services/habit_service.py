"""
Habit Service Layer

This module provides the HabitService class that implements business logic
for habit tracking, CO2 calculations, and statistics generation.
Aligned with Task 5 foundation and async patterns.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime, date
from decimal import Decimal

from app.repositories.habit_repository import HabitRepository, HabitCategoryRepository
from app.models.user_habit import UserHabit
from app.models.habit import HabitCategory, CategoryType
from app.schemas.habit import HabitCreate, HabitResponse

logger = logging.getLogger(__name__)


class HabitService:
    """
    Service class for habit business logic operations.
    
    This class handles habit logging, CO2 calculations, statistics generation,
    and other habit-related business operations.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize HabitService with database session."""
        self.db = db_session
        self.habit_repository = HabitRepository(db_session)
        self.category_repository = HabitCategoryRepository(db_session)
    
    async def log_habit(self, user_id: int, habit_data: HabitCreate) -> UserHabit:
        """
        Log a new habit entry with CO2 savings calculation.
        
        Args:
            user_id: The ID of the user logging the habit
            habit_data: Pydantic model containing habit details
            
        Returns:
            Created UserHabit instance
            
        Raises:
            ValueError: If category not found or validation fails
        """
        try:
            # Get habit category for CO2 calculation
            category = await self.category_repository.get_by_id(habit_data.category_id)
            if not category:
                raise ValueError(f"Habit category {habit_data.category_id} not found")
            
            # Calculate CO2 savings
            co2_saved = category.calculate_co2_savings(habit_data.quantity)
            
            # Prepare habit entry data
            entry_data = {
                "category_id": habit_data.category_id,
                "quantity": habit_data.quantity,
                "co2_saved": co2_saved,
                "logged_date": habit_data.logged_date or date.today(),
                "notes": habit_data.notes
            }
            
            # Create habit entry
            habit_entry = await self.habit_repository.create_habit_entry(user_id, entry_data)
            
            logger.info(f"Logged habit for user {user_id}: {habit_entry.id} ({co2_saved}kg CO2 saved)")
            return habit_entry
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error logging habit for user {user_id}: {str(e)}")
            raise
    
    async def get_user_habit_history(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        limit: int = 100
    ) -> List[UserHabit]:
        """
        Get habit history for a user with optional filtering.
        
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
            habits = await self.habit_repository.get_user_habits(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                category_id=category_id,
                limit=limit
            )
            
            logger.debug(f"Retrieved {len(habits)} habits for user {user_id}")
            return habits
            
        except Exception as e:
            logger.error(f"Error getting habit history for user {user_id}: {str(e)}")
            raise
    
    async def get_user_statistics(
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
            stats = await self.habit_repository.get_habit_statistics(user_id, timeframe)
            
            # Add computed insights
            stats["insights"] = self._generate_insights(stats)
            
            logger.debug(f"Generated statistics for user {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics for user {user_id}: {str(e)}")
            raise
    
    async def delete_habit(self, habit_id: int, user_id: int) -> bool:
        """
        Delete a habit entry.
        
        Args:
            habit_id: Habit entry ID
            user_id: User's ID for ownership verification
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            deleted = await self.habit_repository.delete_habit_entry(habit_id, user_id)
            
            if deleted:
                logger.info(f"Deleted habit {habit_id} for user {user_id}")
            else:
                logger.warning(f"Habit {habit_id} not found or doesn't belong to user {user_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting habit {habit_id}: {str(e)}")
            raise
    
    async def get_habit_categories(self, category_type: Optional[CategoryType] = None) -> List[HabitCategory]:
        """
        Get available habit categories.
        
        Args:
            category_type: Optional filter by category type
            
        Returns:
            List of HabitCategory instances
        """
        try:
            if category_type:
                categories = await self.category_repository.get_by_category_type(category_type)
            else:
                categories = await self.category_repository.get_all_active()
            
            logger.debug(f"Retrieved {len(categories)} habit categories")
            return categories
            
        except Exception as e:
            logger.error(f"Error getting habit categories: {str(e)}")
            raise
    
    async def get_recent_habits(self, user_id: int, limit: int = 10) -> List[UserHabit]:
        """
        Get user's most recent habit entries.
        
        Args:
            user_id: User's ID
            limit: Maximum number of results
            
        Returns:
            List of recent UserHabit instances
        """
        try:
            habits = await self.habit_repository.get_recent_habits(user_id, limit)
            
            logger.debug(f"Retrieved {len(habits)} recent habits for user {user_id}")
            return habits
            
        except Exception as e:
            logger.error(f"Error getting recent habits for user {user_id}: {str(e)}")
            raise
    
    def _generate_insights(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from habit statistics.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Dictionary containing insights
        """
        insights = {}
        
        try:
            total_co2 = stats.get("total_co2_saved", 0)
            total_entries = stats.get("total_entries", 0)
            
            # Performance insights
            if total_co2 > 50:
                insights["performance"] = "excellent"
            elif total_co2 > 20:
                insights["performance"] = "good"
            elif total_co2 > 5:
                insights["performance"] = "fair"
            else:
                insights["performance"] = "needs_improvement"
            
            # Consistency insights
            if total_entries > 20:
                insights["consistency"] = "very_consistent"
            elif total_entries > 10:
                insights["consistency"] = "consistent"
            elif total_entries > 5:
                insights["consistency"] = "somewhat_consistent"
            else:
                insights["consistency"] = "inconsistent"
            
            # Category insights
            categories = stats.get("categories", {})
            if categories:
                top_category = max(categories.keys(), key=lambda k: categories[k]["co2_saved"])
                insights["top_category"] = top_category
                insights["top_category_savings"] = categories[top_category]["co2_saved"]
            
            # Equivalent insights (fun facts)
            if total_co2 > 0:
                insights["equivalent_trees"] = round(total_co2 / 21.77, 1)  # Trees planted equivalent
                insights["equivalent_miles"] = round(total_co2 / 0.404, 1)  # Miles not driven
            
            return insights
            
        except Exception as e:
            logger.warning(f"Error generating insights: {str(e)}")
            return {"error": "Could not generate insights"}
