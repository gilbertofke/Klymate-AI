"""
Test-Driven Development for Badge and Achievement Models

This module contains tests written BEFORE implementation to define
the expected behavior of the badge and gamification system.

Following TDD Red-Green-Refactor cycle:
1. RED: Write failing tests that define requirements
2. GREEN: Write minimal code to make tests pass  
3. REFACTOR: Improve code while keeping tests green
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List

from app.models.badge import Badge, UserBadge, BadgeCategory, BadgeTrigger
from app.repositories.badge_repository import BadgeRepository, UserBadgeRepository
from app.services.gamification_service import GamificationService


class TestBadgeModel:
    """Test cases for Badge model - written BEFORE implementation."""
    
    def test_badge_creation_with_required_fields(self):
        """Test that Badge can be created with minimum required fields."""
        badge = Badge(
            name="First Steps",
            description="Complete your first carbon-saving activity",
            category=BadgeCategory.MILESTONE,
            points_value=10
        )
        
        assert badge.name == "First Steps"
        assert badge.description == "Complete your first carbon-saving activity"
        assert badge.category == BadgeCategory.MILESTONE
        assert badge.points_value == 10
        assert badge.is_active is True  # Should default to True
        assert badge.icon_url is None  # Should allow None
    
    def test_badge_creation_with_all_fields(self):
        """Test Badge creation with all optional fields."""
        criteria = {
            "trigger": "habit_logged",
            "count": 1,
            "category": "any"
        }
        
        badge = Badge(
            name="Eco Warrior",
            description="Save 100kg of CO2",
            category=BadgeCategory.ACHIEVEMENT,
            points_value=100,
            icon_url="https://example.com/eco-warrior.png",
            criteria=criteria,
            is_active=True,
            sort_order=1
        )
        
        assert badge.name == "Eco Warrior"
        assert badge.points_value == 100
        assert badge.icon_url == "https://example.com/eco-warrior.png"
        assert badge.criteria == criteria
        assert badge.sort_order == 1
    
    def test_badge_criteria_validation(self):
        """Test that badge criteria are properly validated."""
        # Valid criteria should work
        valid_criteria = {
            "trigger": "co2_saved",
            "threshold": 50.0,
            "timeframe": "total"
        }
        
        badge = Badge(
            name="Carbon Saver",
            description="Save 50kg of CO2",
            category=BadgeCategory.ACHIEVEMENT,
            points_value=50,
            criteria=valid_criteria
        )
        
        assert badge.criteria["trigger"] == "co2_saved"
        assert badge.criteria["threshold"] == 50.0
    
    def test_badge_string_representation(self):
        """Test Badge __repr__ method."""
        badge = Badge(
            name="Test Badge",
            description="Test description",
            category=BadgeCategory.MILESTONE,
            points_value=25
        )
        
        repr_str = repr(badge)
        assert "Test Badge" in repr_str
        assert "MILESTONE" in repr_str
    
    def test_badge_to_dict_conversion(self):
        """Test Badge to_dict method."""
        criteria = {"trigger": "streak", "days": 7}
        
        badge = Badge(
            name="Week Warrior",
            description="Maintain a 7-day streak",
            category=BadgeCategory.STREAK,
            points_value=35,
            criteria=criteria
        )
        
        badge_dict = badge.to_dict()
        
        assert badge_dict["name"] == "Week Warrior"
        assert badge_dict["category"] == "STREAK"
        assert badge_dict["points_value"] == 35
        assert badge_dict["criteria"] == criteria
    
    def test_badge_difficulty_calculation(self):
        """Test automatic difficulty calculation based on criteria."""
        # Easy badge (low threshold)
        easy_badge = Badge(
            name="Beginner",
            description="Save 1kg CO2",
            category=BadgeCategory.ACHIEVEMENT,
            points_value=5,
            criteria={"trigger": "co2_saved", "threshold": 1.0}
        )
        
        # Hard badge (high threshold)
        hard_badge = Badge(
            name="Expert",
            description="Save 1000kg CO2",
            category=BadgeCategory.ACHIEVEMENT,
            points_value=500,
            criteria={"trigger": "co2_saved", "threshold": 1000.0}
        )
        
        assert easy_badge.get_difficulty() == "easy"
        assert hard_badge.get_difficulty() == "hard"


class TestUserBadgeModel:
    """Test cases for UserBadge model - written BEFORE implementation."""
    
    def test_user_badge_creation(self):
        """Test UserBadge creation with required fields."""
        user_badge = UserBadge(
            user_id=1,
            badge_id=1,
            earned_at=datetime.utcnow(),
            progress_data={"co2_saved": 25.5}
        )
        
        assert user_badge.user_id == 1
        assert user_badge.badge_id == 1
        assert isinstance(user_badge.earned_at, datetime)
        assert user_badge.progress_data["co2_saved"] == 25.5
    
    def test_user_badge_progress_tracking(self):
        """Test progress tracking functionality."""
        user_badge = UserBadge(
            user_id=1,
            badge_id=2,
            earned_at=None,  # Not earned yet
            progress_data={"current": 3, "target": 10}
        )
        
        # Test progress calculation
        progress_percent = user_badge.get_progress_percentage()
        assert progress_percent == 30.0
        
        # Test if badge is earned
        assert not user_badge.is_earned()
        
        # Update progress
        user_badge.update_progress({"current": 10, "target": 10})
        assert user_badge.get_progress_percentage() == 100.0
    
    def test_user_badge_earning(self):
        """Test badge earning functionality."""
        user_badge = UserBadge(
            user_id=1,
            badge_id=3,
            earned_at=None,
            progress_data={"current": 9, "target": 10}
        )
        
        # Badge not earned initially
        assert not user_badge.is_earned()
        
        # Earn the badge
        user_badge.earn_badge()
        
        assert user_badge.is_earned()
        assert isinstance(user_badge.earned_at, datetime)
    
    def test_user_badge_relationships(self):
        """Test UserBadge relationships with User and Badge."""
        user_badge = UserBadge(
            user_id=1,
            badge_id=1,
            earned_at=datetime.utcnow()
        )
        
        # These will be tested once we have the actual relationships
        # For now, just test that the foreign keys are set correctly
        assert user_badge.user_id == 1
        assert user_badge.badge_id == 1


class TestBadgeRepository:
    """Test cases for BadgeRepository - written BEFORE implementation."""
    
    @pytest.fixture
    async def badge_repository(self, db_session):
        """Create badge repository for testing."""
        return BadgeRepository(db_session)
    
    async def test_create_badge(self, badge_repository):
        """Test badge creation through repository."""
        badge_data = {
            "name": "Test Badge",
            "description": "Test description",
            "category": BadgeCategory.MILESTONE,
            "points_value": 10,
            "criteria": {"trigger": "habit_logged", "count": 1}
        }
        
        badge = await badge_repository.create_badge(badge_data)
        
        assert badge.name == "Test Badge"
        assert badge.category == BadgeCategory.MILESTONE
        assert badge.points_value == 10
        assert badge.id is not None
    
    async def test_get_active_badges(self, badge_repository):
        """Test retrieving only active badges."""
        # Create active badge
        active_badge = await badge_repository.create_badge({
            "name": "Active Badge",
            "description": "Active",
            "category": BadgeCategory.MILESTONE,
            "points_value": 10,
            "is_active": True
        })
        
        # Create inactive badge
        inactive_badge = await badge_repository.create_badge({
            "name": "Inactive Badge", 
            "description": "Inactive",
            "category": BadgeCategory.MILESTONE,
            "points_value": 10,
            "is_active": False
        })
        
        active_badges = await badge_repository.get_active_badges()
        
        badge_names = [badge.name for badge in active_badges]
        assert "Active Badge" in badge_names
        assert "Inactive Badge" not in badge_names
    
    async def test_get_badges_by_category(self, badge_repository):
        """Test filtering badges by category."""
        # Create badges in different categories
        milestone_badge = await badge_repository.create_badge({
            "name": "Milestone Badge",
            "description": "Milestone",
            "category": BadgeCategory.MILESTONE,
            "points_value": 10
        })
        
        achievement_badge = await badge_repository.create_badge({
            "name": "Achievement Badge",
            "description": "Achievement", 
            "category": BadgeCategory.ACHIEVEMENT,
            "points_value": 20
        })
        
        milestone_badges = await badge_repository.get_badges_by_category(BadgeCategory.MILESTONE)
        
        assert len(milestone_badges) >= 1
        assert all(badge.category == BadgeCategory.MILESTONE for badge in milestone_badges)
    
    async def test_badge_search(self, badge_repository):
        """Test badge search functionality."""
        # Create searchable badges
        await badge_repository.create_badge({
            "name": "Carbon Saver",
            "description": "Save carbon dioxide",
            "category": BadgeCategory.ACHIEVEMENT,
            "points_value": 50
        })
        
        search_results = await badge_repository.search_badges("carbon")
        
        assert len(search_results) >= 1
        assert any("carbon" in badge.name.lower() or "carbon" in badge.description.lower() 
                  for badge in search_results)


class TestUserBadgeRepository:
    """Test cases for UserBadgeRepository - written BEFORE implementation."""
    
    @pytest.fixture
    async def user_badge_repository(self, db_session):
        """Create user badge repository for testing."""
        return UserBadgeRepository(db_session)
    
    async def test_award_badge_to_user(self, user_badge_repository):
        """Test awarding a badge to a user."""
        user_id = 1
        badge_id = 1
        
        user_badge = await user_badge_repository.award_badge(user_id, badge_id)
        
        assert user_badge.user_id == user_id
        assert user_badge.badge_id == badge_id
        assert user_badge.is_earned()
        assert isinstance(user_badge.earned_at, datetime)
    
    async def test_get_user_badges(self, user_badge_repository):
        """Test retrieving all badges for a user."""
        user_id = 1
        
        # Award multiple badges
        await user_badge_repository.award_badge(user_id, 1)
        await user_badge_repository.award_badge(user_id, 2)
        
        user_badges = await user_badge_repository.get_user_badges(user_id)
        
        assert len(user_badges) >= 2
        assert all(badge.user_id == user_id for badge in user_badges)
    
    async def test_get_user_badge_progress(self, user_badge_repository):
        """Test retrieving badge progress for a user."""
        user_id = 1
        badge_id = 1
        
        # Create badge progress
        user_badge = await user_badge_repository.create_or_update_progress(
            user_id, badge_id, {"current": 5, "target": 10}
        )
        
        progress = await user_badge_repository.get_badge_progress(user_id, badge_id)
        
        assert progress.get_progress_percentage() == 50.0
        assert not progress.is_earned()
    
    async def test_update_badge_progress(self, user_badge_repository):
        """Test updating badge progress."""
        user_id = 1
        badge_id = 1
        
        # Initial progress
        user_badge = await user_badge_repository.create_or_update_progress(
            user_id, badge_id, {"current": 3, "target": 10}
        )
        
        # Update progress
        updated_badge = await user_badge_repository.update_progress(
            user_id, badge_id, {"current": 7, "target": 10}
        )
        
        assert updated_badge.get_progress_percentage() == 70.0
    
    async def test_check_duplicate_badge_award(self, user_badge_repository):
        """Test that badges can't be awarded twice to the same user."""
        user_id = 1
        badge_id = 1
        
        # Award badge first time
        first_award = await user_badge_repository.award_badge(user_id, badge_id)
        
        # Try to award same badge again
        with pytest.raises(ValueError, match="Badge already awarded"):
            await user_badge_repository.award_badge(user_id, badge_id)


class TestBadgeEnums:
    """Test cases for Badge enums - written BEFORE implementation."""
    
    def test_badge_category_enum(self):
        """Test BadgeCategory enum values."""
        assert BadgeCategory.MILESTONE.value == "milestone"
        assert BadgeCategory.ACHIEVEMENT.value == "achievement"
        assert BadgeCategory.STREAK.value == "streak"
        assert BadgeCategory.SOCIAL.value == "social"
        assert BadgeCategory.SPECIAL.value == "special"
    
    def test_badge_trigger_enum(self):
        """Test BadgeTrigger enum values."""
        assert BadgeTrigger.HABIT_LOGGED.value == "habit_logged"
        assert BadgeTrigger.CO2_SAVED.value == "co2_saved"
        assert BadgeTrigger.STREAK_ACHIEVED.value == "streak_achieved"
        assert BadgeTrigger.SOCIAL_ACTION.value == "social_action"
        assert BadgeTrigger.MILESTONE_REACHED.value == "milestone_reached"


class TestBadgeCriteriaEvaluation:
    """Test cases for badge criteria evaluation - written BEFORE implementation."""
    
    def test_simple_count_criteria(self):
        """Test evaluation of simple count-based criteria."""
        criteria = {
            "trigger": "habit_logged",
            "count": 5
        }
        
        user_data = {
            "total_habits": 3
        }
        
        # Should not meet criteria yet
        assert not Badge.evaluate_criteria(criteria, user_data)
        
        user_data["total_habits"] = 5
        
        # Should meet criteria now
        assert Badge.evaluate_criteria(criteria, user_data)
    
    def test_threshold_criteria(self):
        """Test evaluation of threshold-based criteria."""
        criteria = {
            "trigger": "co2_saved",
            "threshold": 100.0,
            "timeframe": "total"
        }
        
        user_data = {
            "total_co2_saved": 75.5
        }
        
        assert not Badge.evaluate_criteria(criteria, user_data)
        
        user_data["total_co2_saved"] = 150.0
        assert Badge.evaluate_criteria(criteria, user_data)
    
    def test_streak_criteria(self):
        """Test evaluation of streak-based criteria."""
        criteria = {
            "trigger": "streak_achieved",
            "days": 7
        }
        
        user_data = {
            "current_streak": 5
        }
        
        assert not Badge.evaluate_criteria(criteria, user_data)
        
        user_data["current_streak"] = 10
        assert Badge.evaluate_criteria(criteria, user_data)
    
    def test_complex_criteria(self):
        """Test evaluation of complex criteria with multiple conditions."""
        criteria = {
            "trigger": "milestone_reached",
            "conditions": {
                "and": [
                    {"field": "total_habits", "operator": ">=", "value": 10},
                    {"field": "total_co2_saved", "operator": ">=", "value": 50.0},
                    {"field": "current_streak", "operator": ">=", "value": 3}
                ]
            }
        }
        
        user_data = {
            "total_habits": 12,
            "total_co2_saved": 45.0,  # Not enough
            "current_streak": 5
        }
        
        assert not Badge.evaluate_criteria(criteria, user_data)
        
        user_data["total_co2_saved"] = 60.0
        assert Badge.evaluate_criteria(criteria, user_data)


# These tests define the expected behavior BEFORE we implement the actual code
# Following TDD principles:
# 1. RED: These tests will fail initially (no implementation exists)
# 2. GREEN: We'll write minimal code to make them pass
# 3. REFACTOR: We'll improve the code while keeping tests green

if __name__ == "__main__":
    print("🔴 TDD RED PHASE: Tests written before implementation")
    print("Next: Implement minimal code to make these tests pass (GREEN phase)")