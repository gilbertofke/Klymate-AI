"""
Badge Repository Implementation

This module provides repository classes for badge data access operations,
implemented following TDD to satisfy test requirements.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from app.repositories.base_repository import BaseRepository
from app.models.badge import Badge, UserBadge, BadgeCategory
from app.models.user import User

logger = logging.getLogger(__name__)


class BadgeRepository(BaseRepository[Badge]):
    """
    Repository for Badge entity operations.
    
    Handles all database operations related to badge management.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize BadgeRepository with Badge model."""
        super().__init__(Badge, db_session)
    
    async def create_badge(self, badge_data: Dict[str, Any]) -> Badge:
        """
        Create a new badge.
        
        Args:
            badge_data: Dictionary containing badge information
            
        Returns:
            Created Badge instance
        """
        try:
            badge = await self.create(badge_data)
            logger.info(f"Created badge: {badge.name}")
            return badge
            
        except Exception as e:
            logger.error(f"Error creating badge: {str(e)}")
            raise
    
    async def get_active_badges(self, category: Optional[BadgeCategory] = None) -> List[Badge]:
        """
        Get all active badges, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of active Badge instances
        """
        try:
            query = select(Badge).where(
                and_(
                    Badge.is_active == True,
                    Badge.is_deleted == False
                )
            )
            
            # Add category filter if specified
            if category:
                query = query.where(Badge.category == category)
            
            query = query.order_by(Badge.sort_order, Badge.name)
            
            result = await self.db.execute(query)
            badges = result.scalars().all()
            
            logger.debug(f"Retrieved {len(badges)} active badges" + 
                        (f" in category {category.value}" if category else ""))
            return list(badges)
            
        except Exception as e:
            logger.error(f"Error getting active badges: {str(e)}")
            raise
    
    async def get_badges_by_category(self, category: BadgeCategory) -> List[Badge]:
        """
        Get badges filtered by category.
        
        Args:
            category: Badge category to filter by
            
        Returns:
            List of Badge instances in the specified category
        """
        try:
            query = select(Badge).where(
                and_(
                    Badge.category == category,
                    Badge.is_active == True,
                    Badge.is_deleted == False
                )
            ).order_by(Badge.sort_order, Badge.name)
            
            result = await self.db.execute(query)
            badges = result.scalars().all()
            
            logger.debug(f"Retrieved {len(badges)} badges in category {category.value}")
            return list(badges)
            
        except Exception as e:
            logger.error(f"Error getting badges by category {category}: {str(e)}")
            raise
    
    async def search_badges(self, search_term: str) -> List[Badge]:
        """
        Search badges by name or description.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching Badge instances
        """
        try:
            search_pattern = f"%{search_term.lower()}%"
            
            query = select(Badge).where(
                and_(
                    or_(
                        func.lower(Badge.name).like(search_pattern),
                        func.lower(Badge.description).like(search_pattern)
                    ),
                    Badge.is_active == True,
                    Badge.is_deleted == False
                )
            ).order_by(Badge.sort_order, Badge.name)
            
            result = await self.db.execute(query)
            badges = result.scalars().all()
            
            logger.debug(f"Found {len(badges)} badges matching '{search_term}'")
            return list(badges)
            
        except Exception as e:
            logger.error(f"Error searching badges: {str(e)}")
            raise
    
    async def get_badge_by_name(self, name: str) -> Optional[Badge]:
        """
        Get badge by name.
        
        Args:
            name: Badge name
            
        Returns:
            Badge instance or None if not found
        """
        try:
            query = select(Badge).where(
                and_(
                    Badge.name == name,
                    Badge.is_deleted == False
                )
            )
            
            result = await self.db.execute(query)
            badge = result.scalar_one_or_none()
            
            return badge
            
        except Exception as e:
            logger.error(f"Error getting badge by name {name}: {str(e)}")
            raise


class UserBadgeRepository(BaseRepository[UserBadge]):
    """
    Repository for UserBadge entity operations.
    
    Handles all database operations related to user badge management.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize UserBadgeRepository with UserBadge model."""
        super().__init__(UserBadge, db_session)
    
    def _add_relationship_loading(self, query):
        """Add relationship loading for UserBadge queries."""
        return query.options(
            selectinload(UserBadge.badge),
            selectinload(UserBadge.user)
        )
    
    async def award_badge(self, user_id: int, badge_id: int) -> UserBadge:
        """
        Award a badge to a user.
        
        Args:
            user_id: User's ID
            badge_id: Badge ID to award
            
        Returns:
            UserBadge instance
            
        Raises:
            ValueError: If badge already awarded to user
        """
        try:
            # Check if badge already awarded
            existing = await self.get_badge_progress(user_id, badge_id)
            if existing and existing.is_earned():
                raise ValueError("Badge already awarded to this user")
            
            if existing:
                # Update existing progress to earned
                existing.earn_badge()
                await self.db.commit()
                await self.db.refresh(existing)
                return existing
            else:
                # Create new user badge entry
                user_badge_data = {
                    "user_id": user_id,
                    "badge_id": badge_id,
                    "earned_at": datetime.utcnow(),
                    "progress_data": {"current": 1, "target": 1}
                }
                
                user_badge = await self.create(user_badge_data)
                logger.info(f"Awarded badge {badge_id} to user {user_id}")
                return user_badge
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error awarding badge {badge_id} to user {user_id}: {str(e)}")
            raise
    
    async def get_user_badges(self, user_id: int, earned_only: bool = False) -> List[UserBadge]:
        """
        Get all badges for a user.
        
        Args:
            user_id: User's ID
            earned_only: If True, only return earned badges
            
        Returns:
            List of UserBadge instances
        """
        try:
            query = select(UserBadge).where(UserBadge.user_id == user_id)
            
            if earned_only:
                query = query.where(UserBadge.earned_at.isnot(None))
            
            query = self._add_relationship_loading(query)
            query = query.order_by(desc(UserBadge.earned_at), UserBadge.created_at)
            
            result = await self.db.execute(query)
            user_badges = result.scalars().all()
            
            logger.debug(f"Retrieved {len(user_badges)} badges for user {user_id}")
            return list(user_badges)
            
        except Exception as e:
            logger.error(f"Error getting user badges for user {user_id}: {str(e)}")
            raise
    
    async def get_badge_progress(self, user_id: int, badge_id: int) -> Optional[UserBadge]:
        """
        Get badge progress for a specific user and badge.
        
        Args:
            user_id: User's ID
            badge_id: Badge ID
            
        Returns:
            UserBadge instance or None if not found
        """
        try:
            query = select(UserBadge).where(
                and_(
                    UserBadge.user_id == user_id,
                    UserBadge.badge_id == badge_id
                )
            )
            
            query = self._add_relationship_loading(query)
            
            result = await self.db.execute(query)
            user_badge = result.scalar_one_or_none()
            
            return user_badge
            
        except Exception as e:
            logger.error(f"Error getting badge progress for user {user_id}, badge {badge_id}: {str(e)}")
            raise
    
    async def create_or_update_progress(
        self, 
        user_id: int, 
        badge_id: int, 
        progress_data: Dict[str, Any]
    ) -> UserBadge:
        """
        Create or update badge progress for a user.
        
        Args:
            user_id: User's ID
            badge_id: Badge ID
            progress_data: Progress data dictionary
            
        Returns:
            UserBadge instance
        """
        try:
            existing = await self.get_badge_progress(user_id, badge_id)
            
            if existing:
                existing.update_progress(progress_data)
                await self.db.commit()
                await self.db.refresh(existing)
                return existing
            else:
                user_badge_data = {
                    "user_id": user_id,
                    "badge_id": badge_id,
                    "earned_at": None,
                    "progress_data": progress_data
                }
                
                user_badge = await self.create(user_badge_data)
                return user_badge
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating/updating progress for user {user_id}, badge {badge_id}: {str(e)}")
            raise
    
    async def update_progress(
        self, 
        user_id: int, 
        badge_id: int, 
        progress_data: Dict[str, Any]
    ) -> UserBadge:
        """
        Update existing badge progress.
        
        Args:
            user_id: User's ID
            badge_id: Badge ID
            progress_data: New progress data
            
        Returns:
            Updated UserBadge instance
        """
        try:
            user_badge = await self.get_badge_progress(user_id, badge_id)
            
            if not user_badge:
                raise ValueError(f"No badge progress found for user {user_id}, badge {badge_id}")
            
            user_badge.update_progress(progress_data)
            await self.db.commit()
            await self.db.refresh(user_badge)
            
            logger.debug(f"Updated badge progress for user {user_id}, badge {badge_id}")
            return user_badge
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating badge progress: {str(e)}")
            raise
    
    async def get_user_badge_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get badge statistics for a user with optimized queries.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary containing badge statistics
        """
        try:
            # Use a single optimized query to get stats
            stats_query = select(
                func.count(UserBadge.id).label("total_badges"),
                func.count(UserBadge.earned_at).label("earned_badges"),
                func.sum(
                    func.case(
                        (UserBadge.earned_at.isnot(None), Badge.points_value),
                        else_=0
                    )
                ).label("total_points")
            ).select_from(
                UserBadge.__table__.join(Badge.__table__)
            ).where(UserBadge.user_id == user_id)
            
            result = await self.db.execute(stats_query)
            stats_row = result.first()
            
            total_badges = stats_row.total_badges or 0
            earned_badges = stats_row.earned_badges or 0
            total_points = stats_row.total_points or 0
            in_progress_badges = total_badges - earned_badges
            
            # Get category breakdown with separate query
            category_query = select(
                Badge.category,
                func.count(UserBadge.id).label("count")
            ).select_from(
                UserBadge.__table__.join(Badge.__table__)
            ).where(
                and_(
                    UserBadge.user_id == user_id,
                    UserBadge.earned_at.isnot(None)
                )
            ).group_by(Badge.category)
            
            category_result = await self.db.execute(category_query)
            category_counts = {
                row.category.value: row.count 
                for row in category_result
            }
            
            stats = {
                "total_badges": total_badges,
                "earned_badges": earned_badges,
                "in_progress_badges": in_progress_badges,
                "total_points": total_points,
                "category_breakdown": category_counts,
                "completion_rate": (earned_badges / total_badges * 100) if total_badges > 0 else 0,
                "average_points_per_badge": (total_points / earned_badges) if earned_badges > 0 else 0
            }
            
            logger.debug(f"Generated optimized badge stats for user {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user badge stats for user {user_id}: {str(e)}")
            raise
    
    async def batch_update_progress(
        self, 
        progress_updates: List[Dict[str, Any]]
    ) -> List[UserBadge]:
        """
        Batch update multiple badge progress entries for efficiency.
        
        Args:
            progress_updates: List of progress update dictionaries
                Each dict should contain: user_id, badge_id, progress_data
                
        Returns:
            List of updated UserBadge instances
        """
        try:
            updated_badges = []
            
            for update in progress_updates:
                user_id = update["user_id"]
                badge_id = update["badge_id"]
                progress_data = update["progress_data"]
                
                user_badge = await self.create_or_update_progress(
                    user_id, badge_id, progress_data
                )
                updated_badges.append(user_badge)
            
            # Commit all changes at once
            await self.db.commit()
            
            logger.info(f"Batch updated {len(updated_badges)} badge progress entries")
            return updated_badges
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in batch progress update: {str(e)}")
            raise