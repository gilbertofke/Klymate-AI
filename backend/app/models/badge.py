"""
Badge and Achievement Models

This module implements the badge and gamification models following TDD.
Implementation written to satisfy the test requirements in test_badge_models.py
"""

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin


class BadgeCategory(Enum):
    """Enumeration for badge categories."""
    MILESTONE = "milestone"
    ACHIEVEMENT = "achievement" 
    STREAK = "streak"
    SOCIAL = "social"
    SPECIAL = "special"


class BadgeTrigger(Enum):
    """Enumeration for badge trigger types."""
    HABIT_LOGGED = "habit_logged"
    CO2_SAVED = "co2_saved"
    STREAK_ACHIEVED = "streak_achieved"
    SOCIAL_ACTION = "social_action"
    MILESTONE_REACHED = "milestone_reached"


class Badge(BaseModel, SoftDeleteMixin, AuditMixin):
    """
    Badge model for gamification system.
    
    Represents achievements and milestones that users can earn
    through various carbon-saving activities.
    """
    
    __tablename__ = "badges"
    
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(BadgeCategory), nullable=False, index=True)
    points_value = Column(Integer, nullable=False, default=0)
    icon_url = Column(String(500), nullable=True)
    criteria = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    sort_order = Column(Integer, nullable=True, default=0)
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of Badge."""
        return f"<Badge(name='{self.name}', category='{self.category.value}', points={self.points_value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Badge to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "category": self.category.value if self.category else None,
            "criteria": self.criteria
        })
        return base_dict
    
    def get_difficulty(self) -> str:
        """
        Calculate badge difficulty based on criteria and points.
        
        Returns:
            Difficulty level: 'easy', 'medium', 'hard'
        """
        if not self.criteria:
            # Use points as fallback for difficulty calculation
            if self.points_value <= 25:
                return "easy"
            elif self.points_value <= 100:
                return "medium"
            else:
                return "hard"
        
        # Enhanced difficulty calculation with multiple factors
        difficulty_score = 0
        
        # Factor 1: Threshold-based criteria
        if "threshold" in self.criteria:
            threshold = self.criteria["threshold"]
            if threshold <= 10:
                difficulty_score += 1
            elif threshold <= 100:
                difficulty_score += 2
            else:
                difficulty_score += 3
        
        # Factor 2: Count-based criteria
        if "count" in self.criteria:
            count = self.criteria["count"]
            if count <= 5:
                difficulty_score += 1
            elif count <= 20:
                difficulty_score += 2
            else:
                difficulty_score += 3
        
        # Factor 3: Time-based criteria (streaks, etc.)
        if "days" in self.criteria:
            days = self.criteria["days"]
            if days <= 3:
                difficulty_score += 1
            elif days <= 14:
                difficulty_score += 2
            else:
                difficulty_score += 3
        
        # Factor 4: Complex conditions
        if "conditions" in self.criteria:
            conditions = self.criteria["conditions"]
            if "and" in conditions:
                difficulty_score += len(conditions["and"])
        
        # Convert score to difficulty level
        if difficulty_score <= 2:
            return "easy"
        elif difficulty_score <= 4:
            return "medium"
        else:
            return "hard"
    
    @staticmethod
    def evaluate_criteria(criteria: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """
        Evaluate if user data meets badge criteria.
        
        Args:
            criteria: Badge criteria dictionary
            user_data: User's current data/stats
            
        Returns:
            True if criteria are met, False otherwise
        """
        if not criteria or not user_data:
            return False
        
        trigger = criteria.get("trigger")
        
        # Use strategy pattern for different trigger types
        evaluators = {
            "habit_logged": Badge._evaluate_habit_logged,
            "co2_saved": Badge._evaluate_co2_saved,
            "streak_achieved": Badge._evaluate_streak_achieved,
            "milestone_reached": Badge._evaluate_milestone_reached,
            "social_action": Badge._evaluate_social_action,
        }
        
        evaluator = evaluators.get(trigger)
        if evaluator:
            return evaluator(criteria, user_data)
        
        return False
    
    @staticmethod
    def _evaluate_habit_logged(criteria: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Evaluate habit logging criteria."""
        required_count = criteria.get("count", 1)
        category = criteria.get("category")
        
        if category and category != "any":
            # Check specific category count
            category_key = f"total_habits_{category}"
            user_count = user_data.get(category_key, 0)
        else:
            # Check total habits
            user_count = user_data.get("total_habits", 0)
        
        return user_count >= required_count
    
    @staticmethod
    def _evaluate_co2_saved(criteria: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Evaluate CO2 savings criteria."""
        threshold = criteria.get("threshold", 0)
        timeframe = criteria.get("timeframe", "total")
        
        if timeframe == "total":
            user_saved = user_data.get("total_co2_saved", 0)
        elif timeframe == "monthly":
            user_saved = user_data.get("monthly_co2_saved", 0)
        elif timeframe == "weekly":
            user_saved = user_data.get("weekly_co2_saved", 0)
        else:
            user_saved = user_data.get("total_co2_saved", 0)
        
        return user_saved >= threshold
    
    @staticmethod
    def _evaluate_streak_achieved(criteria: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Evaluate streak achievement criteria."""
        required_days = criteria.get("days", 1)
        user_streak = user_data.get("current_streak", 0)
        return user_streak >= required_days
    
    @staticmethod
    def _evaluate_milestone_reached(criteria: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Evaluate complex milestone criteria."""
        conditions = criteria.get("conditions", {})
        
        if "and" in conditions:
            return all(
                Badge._evaluate_condition(condition, user_data)
                for condition in conditions["and"]
            )
        elif "or" in conditions:
            return any(
                Badge._evaluate_condition(condition, user_data)
                for condition in conditions["or"]
            )
        
        return False
    
    @staticmethod
    def _evaluate_social_action(criteria: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Evaluate social action criteria."""
        action_type = criteria.get("action_type", "share")
        required_count = criteria.get("count", 1)
        
        action_key = f"social_{action_type}_count"
        user_count = user_data.get(action_key, 0)
        
        return user_count >= required_count
    
    @staticmethod
    def _evaluate_condition(condition: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if not all([field, operator, value]):
            return False
        
        user_value = user_data.get(field, 0)
        
        if operator == ">=":
            return user_value >= value
        elif operator == ">":
            return user_value > value
        elif operator == "<=":
            return user_value <= value
        elif operator == "<":
            return user_value < value
        elif operator == "==":
            return user_value == value
        
        return False


class UserBadge(BaseModel, TimestampMixin):
    """
    User Badge model representing badges earned by users.
    
    Tracks badge progress and achievement status for individual users.
    """
    
    __tablename__ = "user_badges"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True)
    earned_at = Column(DateTime, nullable=True)
    progress_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
    
    # Unique constraint to prevent duplicate badge awards
    __table_args__ = (
        {"extend_existing": True}
    )
    
    def __repr__(self) -> str:
        """String representation of UserBadge."""
        status = "earned" if self.is_earned() else "in_progress"
        return f"<UserBadge(user_id={self.user_id}, badge_id={self.badge_id}, status={status})>"
    
    def is_earned(self) -> bool:
        """Check if badge has been earned."""
        return self.earned_at is not None
    
    def get_progress_percentage(self) -> float:
        """
        Calculate progress percentage towards earning the badge.
        
        Returns:
            Progress percentage (0-100)
        """
        if self.is_earned():
            return 100.0
        
        if not self.progress_data:
            return 0.0
        
        current = self.progress_data.get("current", 0)
        target = self.progress_data.get("target", 1)
        
        if target <= 0:
            return 0.0
        
        return min(100.0, (current / target) * 100.0)
    
    def update_progress(self, progress_data: Dict[str, Any]) -> None:
        """
        Update badge progress data.
        
        Args:
            progress_data: New progress data
        """
        self.progress_data = progress_data
        
        # Auto-earn badge if progress reaches 100%
        if self.get_progress_percentage() >= 100.0 and not self.is_earned():
            self.earn_badge()
    
    def earn_badge(self) -> None:
        """Mark badge as earned."""
        if not self.is_earned():
            self.earned_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert UserBadge to dictionary with enhanced information."""
        base_dict = super().to_dict()
        base_dict.update({
            "is_earned": self.is_earned(),
            "progress_percentage": self.get_progress_percentage(),
            "progress_data": self.progress_data,
            "days_to_earn": self.get_days_to_earn(),
            "is_close_to_earning": self.is_close_to_earning()
        })
        return base_dict
    
    def get_days_to_earn(self) -> Optional[int]:
        """
        Calculate days since earning or None if not earned.
        
        Returns:
            Number of days since earning, or None if not earned
        """
        if not self.is_earned():
            return None
        
        delta = datetime.utcnow() - self.earned_at
        return delta.days
    
    def is_close_to_earning(self, threshold: float = 80.0) -> bool:
        """
        Check if user is close to earning the badge.
        
        Args:
            threshold: Progress percentage threshold (default 80%)
            
        Returns:
            True if progress is above threshold but not earned
        """
        if self.is_earned():
            return False
        
        return self.get_progress_percentage() >= threshold
    
    def get_remaining_progress(self) -> Dict[str, Any]:
        """
        Get remaining progress needed to earn the badge.
        
        Returns:
            Dictionary with remaining progress information
        """
        if self.is_earned():
            return {"remaining": 0, "percentage_remaining": 0}
        
        if not self.progress_data:
            return {"remaining": "unknown", "percentage_remaining": 100}
        
        current = self.progress_data.get("current", 0)
        target = self.progress_data.get("target", 1)
        remaining = max(0, target - current)
        percentage_remaining = 100 - self.get_progress_percentage()
        
        return {
            "remaining": remaining,
            "percentage_remaining": round(percentage_remaining, 1),
            "target": target,
            "current": current
        }