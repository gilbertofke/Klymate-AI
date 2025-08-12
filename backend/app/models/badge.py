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
        Calculate badge difficulty based on criteria.
        
        Returns:
            Difficulty level: 'easy', 'medium', 'hard'
        """
        if not self.criteria:
            return "easy"
        
        # Simple difficulty calculation based on thresholds
        if "threshold" in self.criteria:
            threshold = self.criteria["threshold"]
            if threshold <= 10:
                return "easy"
            elif threshold <= 100:
                return "medium"
            else:
                return "hard"
        
        if "count" in self.criteria:
            count = self.criteria["count"]
            if count <= 5:
                return "easy"
            elif count <= 20:
                return "medium"
            else:
                return "hard"
        
        return "medium"  # Default
    
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
        if not criteria:
            return False
        
        trigger = criteria.get("trigger")
        
        if trigger == "habit_logged":
            required_count = criteria.get("count", 1)
            user_count = user_data.get("total_habits", 0)
            return user_count >= required_count
        
        elif trigger == "co2_saved":
            threshold = criteria.get("threshold", 0)
            user_saved = user_data.get("total_co2_saved", 0)
            return user_saved >= threshold
        
        elif trigger == "streak_achieved":
            required_days = criteria.get("days", 1)
            user_streak = user_data.get("current_streak", 0)
            return user_streak >= required_days
        
        elif trigger == "milestone_reached":
            conditions = criteria.get("conditions", {})
            if "and" in conditions:
                return all(
                    Badge._evaluate_condition(condition, user_data)
                    for condition in conditions["and"]
                )
        
        return False
    
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
        """Convert UserBadge to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "is_earned": self.is_earned(),
            "progress_percentage": self.get_progress_percentage(),
            "progress_data": self.progress_data
        })
        return base_dict