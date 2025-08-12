"""
Test-Driven Development for Gamification Service

This module contains tests written BEFORE implementation for the
gamification service and endpoints (Task 8.2).

Following TDD Red-Green-Refactor cycle:
1. RED: Write failing tests that define requirements
2. GREEN: Write minimal code to make tests pass  
3. REFACTOR: Improve code while keeping tests green
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.services.gamification_service import GamificationService
from app.models.badge import Badge, UserBadge, BadgeCategory
from app.schemas.gamification import (
    BadgeResponse, UserBadgeResponse, LeaderboardResponse,
    BadgeProgressResponse, GamificationStatsResponse
)


class TestGamificationService:
    """Test cases for GamificationService - written BEFORE implementation."""
    
    @pytest.fixture
    async def gamification_service(self, db_session):
        """Create gamification service for testing."""
        return GamificationService(db_session)
    
    @pytest.fixture
    def mock_user_data(self):
        """Mock user data for testing."""
        return {
            "user_id": 1,
            "total_habits": 15,
            "total_co2_saved": 125.5,
            "current_streak": 7,
            "eco_score": 250
        }
    
    async def test_check_and_award_badges(self, gamification_service, mock_user_data):
        """Test automatic badge checking and awarding."""
        # Arrange
        mock_badges = [
            Mock(id=1, name="First Steps", criteria={"trigger": "habit_logged", "count": 1}),
            Mock(id=2, name="Eco Warrior", criteria={"trigger": "co2_saved", "threshold": 100.0}),
            Mock(id=3, name="Week Streak", criteria={"trigger": "streak_achieved", "days": 7})
        ]
        
        with patch.object(gamification_service.badge_repository, 'get_active_badges', return_value=mock_badges):
            with patch.object(gamification_service, '_evaluate_and_award_badge') as mock_award:
                mock_award.return_value = True
                
                # Act
                awarded_badges = await gamification_service.check_and_award_badges(
                    user_id=1, user_data=mock_user_data
                )
                
                # Assert
                assert len(awarded_badges) >= 0
                assert mock_award.call_count == len(mock_badges)
    
    async def test_calculate_eco_score(self, gamification_service):
        """Test eco score calculation based on user activities."""
        # Arrange
        user_stats = {
            "total_co2_saved": 150.0,
            "current_streak": 10,
            "total_habits": 25,
            "badge_points": 200
        }
        
        # Act
        eco_score = await gamification_service.calculate_eco_score(1, user_stats)
        
        # Assert
        assert isinstance(eco_score, int)
        assert eco_score > 0
        # Score should incorporate multiple factors
        assert eco_score > user_stats["badge_points"]  # Should be more than just badge points
    
    async def test_update_user_streak(self, gamification_service):
        """Test streak tracking and updates."""
        user_id = 1
        
        with patch.object(gamification_service.user_repository, 'get_by_id') as mock_get_user:
            mock_user = Mock(current_streak=5, last_activity_date=datetime.utcnow().date())
            mock_get_user.return_value = mock_user
            
            # Act - user logs activity today
            new_streak = await gamification_service.update_user_streak(user_id, activity_date=datetime.utcnow().date())
            
            # Assert
            assert new_streak >= 5  # Streak should continue or increase
    
    async def test_generate_leaderboard(self, gamification_service):
        """Test leaderboard generation with eco scores."""
        # Arrange
        mock_users = [
            Mock(id=1, display_name="User1", eco_score=500, total_co2_saved=200.0),
            Mock(id=2, display_name="User2", eco_score=450, total_co2_saved=180.0),
            Mock(id=3, display_name="User3", eco_score=400, total_co2_saved=160.0)
        ]
        
        with patch.object(gamification_service.user_repository, 'get_leaderboard_users', return_value=mock_users):
            # Act
            leaderboard = await gamification_service.generate_leaderboard(limit=10)
            
            # Assert
            assert len(leaderboard) == 3
            assert leaderboard[0]["eco_score"] >= leaderboard[1]["eco_score"]  # Sorted by score
            assert all("rank" in entry for entry in leaderboard)
            assert all("display_name" in entry for entry in leaderboard)
    
    async def test_get_user_badge_progress(self, gamification_service):
        """Test retrieving user's badge progress."""
        user_id = 1
        
        mock_user_badges = [
            Mock(badge_id=1, is_earned=lambda: True, get_progress_percentage=lambda: 100.0),
            Mock(badge_id=2, is_earned=lambda: False, get_progress_percentage=lambda: 75.0),
            Mock(badge_id=3, is_earned=lambda: False, get_progress_percentage=lambda: 30.0)
        ]
        
        with patch.object(gamification_service.user_badge_repository, 'get_user_badges', return_value=mock_user_badges):
            # Act
            progress = await gamification_service.get_user_badge_progress(user_id)
            
            # Assert
            assert len(progress) == 3
            earned_badges = [p for p in progress if p["is_earned"]]
            in_progress_badges = [p for p in progress if not p["is_earned"]]
            
            assert len(earned_badges) == 1
            assert len(in_progress_badges) == 2
    
    async def test_get_available_badges(self, gamification_service):
        """Test retrieving available badges for users."""
        mock_badges = [
            Mock(id=1, name="Badge1", category=BadgeCategory.MILESTONE, points_value=10),
            Mock(id=2, name="Badge2", category=BadgeCategory.ACHIEVEMENT, points_value=25),
            Mock(id=3, name="Badge3", category=BadgeCategory.STREAK, points_value=15)
        ]
        
        with patch.object(gamification_service.badge_repository, 'get_active_badges', return_value=mock_badges):
            # Act
            badges = await gamification_service.get_available_badges(category=None)
            
            # Assert
            assert len(badges) == 3
            assert all("name" in badge for badge in badges)
            assert all("points_value" in badge for badge in badges)
    
    async def test_get_user_gamification_stats(self, gamification_service):
        """Test comprehensive user gamification statistics."""
        user_id = 1
        
        mock_badge_stats = {
            "total_badges": 10,
            "earned_badges": 6,
            "total_points": 150
        }
        
        with patch.object(gamification_service.user_badge_repository, 'get_user_badge_stats', return_value=mock_badge_stats):
            with patch.object(gamification_service, 'calculate_eco_score', return_value=350):
                # Act
                stats = await gamification_service.get_user_gamification_stats(user_id)
                
                # Assert
                assert stats["user_id"] == user_id
                assert stats["total_badges"] == 10
                assert stats["earned_badges"] == 6
                assert stats["eco_score"] == 350
                assert "completion_rate" in stats
                assert "rank" in stats
    
    async def test_process_habit_logged_event(self, gamification_service):
        """Test processing habit logged events for gamification."""
        # Arrange
        event_data = {
            "user_id": 1,
            "habit_category": "transport",
            "co2_saved": 2.5,
            "logged_date": datetime.utcnow().date()
        }
        
        with patch.object(gamification_service, 'check_and_award_badges') as mock_check_badges:
            with patch.object(gamification_service, 'update_user_streak') as mock_update_streak:
                mock_check_badges.return_value = []
                mock_update_streak.return_value = 8
                
                # Act
                result = await gamification_service.process_habit_logged_event(event_data)
                
                # Assert
                assert result["user_id"] == 1
                assert result["new_streak"] == 8
                assert "badges_awarded" in result
                mock_check_badges.assert_called_once()
                mock_update_streak.assert_called_once()
    
    async def test_get_badge_recommendations(self, gamification_service):
        """Test getting personalized badge recommendations."""
        user_id = 1
        user_stats = {
            "total_habits": 8,
            "total_co2_saved": 45.0,
            "current_streak": 3
        }
        
        # Act
        recommendations = await gamification_service.get_badge_recommendations(user_id, user_stats)
        
        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5  # Should limit recommendations
        
        for rec in recommendations:
            assert "badge" in rec
            assert "progress_needed" in rec
            assert "difficulty" in rec
    
    async def test_celebrate_achievement(self, gamification_service):
        """Test achievement celebration functionality."""
        user_id = 1
        badge_id = 1
        
        # Act
        celebration = await gamification_service.celebrate_achievement(user_id, badge_id)
        
        # Assert
        assert celebration["user_id"] == user_id
        assert celebration["badge_id"] == badge_id
        assert "message" in celebration
        assert "celebration_type" in celebration
        assert celebration["celebration_type"] in ["badge_earned", "milestone_reached", "streak_achieved"]


class TestGamificationEndpoints:
    """Test cases for gamification API endpoints - written BEFORE implementation."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user for endpoint testing."""
        user = Mock()
        user.id = 1
        user.display_name = "Test User"
        return user
    
    async def test_get_user_badges_endpoint(self, client, mock_current_user):
        """Test GET /gamification/badges endpoint."""
        # This would test the actual FastAPI endpoint
        # For now, we define the expected behavior
        
        # Expected: Returns user's badges with progress information
        # Expected: Includes earned and in-progress badges
        # Expected: Proper authentication required
        pass
    
    async def test_get_leaderboard_endpoint(self, client, mock_current_user):
        """Test GET /gamification/leaderboard endpoint."""
        # Expected: Returns top users by eco score
        # Expected: Includes user rankings and stats
        # Expected: Supports pagination
        pass
    
    async def test_get_available_badges_endpoint(self, client, mock_current_user):
        """Test GET /gamification/available-badges endpoint."""
        # Expected: Returns all available badges
        # Expected: Supports category filtering
        # Expected: Includes badge criteria and difficulty
        pass
    
    async def test_get_user_stats_endpoint(self, client, mock_current_user):
        """Test GET /gamification/stats endpoint."""
        # Expected: Returns comprehensive user gamification stats
        # Expected: Includes badges, eco score, rank, streaks
        # Expected: Proper user authentication
        pass
    
    async def test_process_achievement_webhook(self, client):
        """Test POST /gamification/webhook/achievement endpoint."""
        # Expected: Processes achievement events from other services
        # Expected: Updates user progress and awards badges
        # Expected: Returns updated gamification state
        pass


class TestStreakTracking:
    """Test cases for streak tracking functionality - written BEFORE implementation."""
    
    async def test_consecutive_day_streak(self, gamification_service):
        """Test streak calculation for consecutive days."""
        user_id = 1
        
        # Simulate logging activities on consecutive days
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        with patch.object(gamification_service.user_repository, 'get_by_id') as mock_get_user:
            mock_user = Mock(current_streak=5, last_activity_date=yesterday)
            mock_get_user.return_value = mock_user
            
            # Act - log activity today
            new_streak = await gamification_service.update_user_streak(user_id, today)
            
            # Assert
            assert new_streak == 6  # Should increment streak
    
    async def test_broken_streak(self, gamification_service):
        """Test streak reset when days are skipped."""
        user_id = 1
        
        # Simulate gap in activities
        today = datetime.utcnow().date()
        three_days_ago = today - timedelta(days=3)
        
        with patch.object(gamification_service.user_repository, 'get_by_id') as mock_get_user:
            mock_user = Mock(current_streak=5, last_activity_date=three_days_ago)
            mock_get_user.return_value = mock_user
            
            # Act - log activity today after gap
            new_streak = await gamification_service.update_user_streak(user_id, today)
            
            # Assert
            assert new_streak == 1  # Should reset to 1
    
    async def test_same_day_multiple_activities(self, gamification_service):
        """Test that multiple activities on same day don't increase streak."""
        user_id = 1
        today = datetime.utcnow().date()
        
        with patch.object(gamification_service.user_repository, 'get_by_id') as mock_get_user:
            mock_user = Mock(current_streak=3, last_activity_date=today)
            mock_get_user.return_value = mock_user
            
            # Act - log another activity same day
            new_streak = await gamification_service.update_user_streak(user_id, today)
            
            # Assert
            assert new_streak == 3  # Should remain the same


class TestEcoScoreCalculation:
    """Test cases for eco score calculation - written BEFORE implementation."""
    
    async def test_eco_score_components(self, gamification_service):
        """Test that eco score includes all expected components."""
        user_stats = {
            "total_co2_saved": 100.0,
            "current_streak": 5,
            "total_habits": 20,
            "badge_points": 150,
            "social_shares": 3
        }
        
        # Act
        eco_score = await gamification_service.calculate_eco_score(1, user_stats)
        
        # Assert
        assert eco_score > 0
        # Score should be influenced by multiple factors
        # Exact calculation will be defined in implementation
    
    async def test_eco_score_scaling(self, gamification_service):
        """Test eco score scales appropriately with achievements."""
        low_stats = {
            "total_co2_saved": 10.0,
            "current_streak": 1,
            "total_habits": 3,
            "badge_points": 25
        }
        
        high_stats = {
            "total_co2_saved": 500.0,
            "current_streak": 30,
            "total_habits": 100,
            "badge_points": 1000
        }
        
        # Act
        low_score = await gamification_service.calculate_eco_score(1, low_stats)
        high_score = await gamification_service.calculate_eco_score(2, high_stats)
        
        # Assert
        assert high_score > low_score * 2  # Should scale significantly


class TestBadgeRecommendations:
    """Test cases for badge recommendation system - written BEFORE implementation."""
    
    async def test_recommend_achievable_badges(self, gamification_service):
        """Test recommending badges that are close to being earned."""
        user_id = 1
        user_stats = {
            "total_habits": 8,  # Close to 10-habit badge
            "total_co2_saved": 45.0,  # Close to 50kg badge
            "current_streak": 6  # Close to 7-day streak badge
        }
        
        # Act
        recommendations = await gamification_service.get_badge_recommendations(user_id, user_stats)
        
        # Assert
        assert len(recommendations) > 0
        
        # Should prioritize badges that are close to completion
        for rec in recommendations:
            progress_needed = rec["progress_needed"]
            assert progress_needed < 50  # Should be less than 50% progress needed
    
    async def test_recommend_appropriate_difficulty(self, gamification_service):
        """Test that recommendations match user's current level."""
        # Beginner user
        beginner_stats = {
            "total_habits": 2,
            "total_co2_saved": 5.0,
            "current_streak": 1
        }
        
        # Advanced user
        advanced_stats = {
            "total_habits": 50,
            "total_co2_saved": 300.0,
            "current_streak": 20
        }
        
        # Act
        beginner_recs = await gamification_service.get_badge_recommendations(1, beginner_stats)
        advanced_recs = await gamification_service.get_badge_recommendations(2, advanced_stats)
        
        # Assert
        # Beginner should get easier badges
        beginner_difficulties = [rec["difficulty"] for rec in beginner_recs]
        assert "easy" in beginner_difficulties
        
        # Advanced user should get harder badges
        advanced_difficulties = [rec["difficulty"] for rec in advanced_recs]
        assert "hard" in advanced_difficulties or "medium" in advanced_difficulties


# These tests define the expected behavior BEFORE we implement the actual code
# Following TDD principles:
# 1. RED: These tests will fail initially (no implementation exists)
# 2. GREEN: We'll write minimal code to make them pass
# 3. REFACTOR: We'll improve the code while keeping tests green

if __name__ == "__main__":
    print("🔴 TDD RED PHASE: Gamification service tests written before implementation")
    print("Next: Implement minimal code to make these tests pass (GREEN phase)")