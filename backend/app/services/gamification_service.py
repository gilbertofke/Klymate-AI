"""
Gamification Service - Task 8.2 Implementation

This module provides the gamification service that handles badge awarding,
streak tracking, leaderboards, and eco score calculations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date

from app.repositories.badge_repository import BadgeRepository, UserBadgeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.habit_repository import HabitRepository
from app.models.badge import Badge
from app.utils.cache import cache_result, CacheInvalidationStrategy
from app.utils.cache import cache_invalidate, cached

logger = logging.getLogger(__name__)


class GamificationService:
    """Service for gamification functionality."""
    
    def __init__(self, db_session):
        """Initialize gamification service."""
        self.db = db_session
        self.badge_repository = BadgeRepository(db_session)
        self.user_badge_repository = UserBadgeRepository(db_session)
        self.user_repository = UserRepository(db_session)
        self.habit_repository = HabitRepository(db_session)
        logger.info("Gamification Service initialized")
    
    @cache_invalidate("dashboard:*", "comparison:*", "categories:*")
    async def check_and_award_badges(self, user_id: int, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check and award eligible badges."""
        try:
            active_badges = await self.badge_repository.get_active_badges()
            awarded_badges = []
            
            for badge in active_badges:
                existing_badge = await self.user_badge_repository.get_badge_progress(user_id, badge.id)
                if existing_badge and existing_badge.is_earned():
                    continue
                
                if Badge.evaluate_criteria(badge.criteria or {}, user_data):
                    await self.user_badge_repository.award_badge(user_id, badge.id)
                    awarded_badges.append({
                        "badge_id": badge.id,
                        "badge_name": badge.name,
                        "points_value": badge.points_value,
                        "category": badge.category.value if badge.category else "general"
                    })
            
            return awarded_badges
        except Exception as e:
            logger.error(f"Error awarding badges: {str(e)}")
            return []
    
    @cache_result(ttl=900, key_prefix="leaderboard")  # 15 minutes cache
    async def get_leaderboard(self, limit: int = 10, timeframe: str = "all_time") -> List[Dict[str, Any]]:
        """Generate leaderboard."""
        try:
            users = await self.user_repository.get_top_users_by_eco_score(limit)
            leaderboard = []
            
            for rank, user in enumerate(users, 1):
                user_badges = await self.user_badge_repository.get_user_badges(user.id, earned_only=True)
                leaderboard.append({
                    "rank": rank,
                    "user_id": user.id,
                    "display_name": user.display_name or f"User {user.id}",
                    "eco_score": user.eco_score or 0,
                    "total_co2_saved": float(user.total_co2_saved or 0),
                    "current_streak": user.current_streak or 0,
                    "badge_count": len(user_badges)
                })
            
            return leaderboard
        except Exception as e:
            logger.error(f"Error generating leaderboard: {str(e)}")
            return []