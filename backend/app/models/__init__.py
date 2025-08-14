"""
Models Package

This package contains all SQLAlchemy model definitions for the application,
following the Task 5 BaseModel foundation and design patterns.
"""

from .base import BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin
from .user import User
from .habit import HabitCategory, CategoryType
from .user_habit import UserHabit
from .ai_conversation import AIConversation
from .badge import Badge, UserBadge, BadgeCategory, BadgeTrigger
from .carbon_credit import (
    CarbonCreditRate, UserCarbonCredits, CarbonCreditTransaction,
    CarbonCreditRedemption, CarbonVerificationRule,
    RateType, TransactionType, VerificationStatus, VerificationMethod,
    RedemptionType, RedemptionStatus
)

__all__ = [
    "BaseModel",
    "TimestampMixin", 
    "SoftDeleteMixin",
    "AuditMixin",
    "User",
    "HabitCategory",
    "CategoryType", 
    "UserHabit",
    "AIConversation",
    "Badge",
    "UserBadge",
    "BadgeCategory",
    "BadgeTrigger",
    "CarbonCreditRate",
    "UserCarbonCredits",
    "CarbonCreditTransaction",
    "CarbonCreditRedemption",
    "CarbonVerificationRule",
    "RateType",
    "TransactionType",
    "VerificationStatus",
    "VerificationMethod",
    "RedemptionType",
    "RedemptionStatus"
]