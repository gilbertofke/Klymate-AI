"""
Tests for User Statistics Aggregation

This module tests the user statistics functionality including
analytics, aggregation methods, and reporting features.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository


class TestUserRepositoryStatistics:
    """Test user repository statistics methods."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def user_repository(self, mock_db_session):
        """Create UserRepository instance with mocked session."""
        return UserRepository(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_user_statistics_comprehensive(self, user_repository, mock_db_session):
        """Test comprehensive user statistics retrieval."""
        # Mock database query results
        mock_results = [
            Mock(scalar=Mock(return_value=1000)),  # total_users
            Mock(scalar=Mock(return_value=850)),   # active_users
            Mock(scalar=Mock(return_value=600)),   # verified_users
            Mock(scalar=Mock(return_value=750)),   # onboarded_users
            Mock(scalar=Mock(return_value=50)),    # new_users_30d
            Mock(scalar=Mock(return_value=8500.0)) # avg_baseline_footprint
        ]
        
        mock_db_session.execute.side_effect = mock_results
        
        stats = await user_repository.get_user_statistics()
        
        assert stats["total_users"] == 1000
        assert stats["active_users"] == 850
        assert stats["verified_users"] == 600
        assert stats["onboarded_users"] == 750
        assert stats["new_users_30d"] == 50
        assert stats["avg_baseline_footprint"] == 8500.0
        assert stats["onboarding_completion_rate"] == 75.0  # 750/1000 * 100
        assert stats["verification_rate"] == 60.0  # 600/1000 * 100
        
        # Verify correct number of database queries
        assert mock_db_session.execute.call_count == 6
    
    @pytest.mark.asyncio
    async def test_get_user_statistics_zero_users(self, user_repository, mock_db_session):
        """Test statistics when no users exist."""
        # Mock database query results for zero users
        mock_results = [
            Mock(scalar=Mock(return_value=0)),     # total_users
            Mock(scalar=Mock(return_value=0)),     # active_users
            Mock(scalar=Mock(return_value=0)),     # verified_users
            Mock(scalar=Mock(return_value=0)),     # onboarded_users
            Mock(scalar=Mock(return_value=0)),     # new_users_30d
            Mock(scalar=Mock(return_value=None))   # avg_baseline_footprint
        ]
        
        mock_db_session.execute.side_effect = mock_results
        
        stats = await user_repository.get_user_statistics()
        
        assert stats["total_users"] == 0
        assert stats["onboarding_completion_rate"] == 0
        assert stats["verification_rate"] == 0
        assert stats["avg_baseline_footprint"] is None
    
    @pytest.mark.asyncio
    async def test_get_active_users(self, user_repository, mock_db_session):
        """Test getting active users."""
        # Create mock users
        mock_users = [
            Mock(spec=User, id=1, email="user1@example.com", is_active=True),
            Mock(spec=User, id=2, email="user2@example.com", is_active=True),
            Mock(spec=User, id=3, email="user3@example.com", is_active=True)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db_session.execute.return_value = mock_result
        
        users = await user_repository.get_active_users(limit=10)
        
        assert len(users) == 3
        assert all(user.is_active for user in users)
    
    @pytest.mark.asyncio
    async def test_get_users_by_location(self, user_repository, mock_db_session):
        """Test getting users by location."""
        # Create mock users in specific location
        mock_users = [
            Mock(spec=User, id=1, location="New York", email="user1@example.com"),
            Mock(spec=User, id=2, location="New York City", email="user2@example.com")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db_session.execute.return_value = mock_result
        
        users = await user_repository.get_users_by_location("New York")
        
        assert len(users) == 2
        assert all("New York" in user.location for user in users)
    
    @pytest.mark.asyncio
    async def test_search_users(self, user_repository, mock_db_session):
        """Test user search functionality."""
        # Create mock search results
        mock_users = [
            Mock(spec=User, id=1, name="John Doe", email="john@example.com"),
            Mock(spec=User, id=2, name="Jane Doe", email="jane@example.com")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db_session.execute.return_value = mock_result
        
        users = await user_repository.search_users("Doe", limit=10)
        
        assert len(users) == 2
        assert all("Doe" in user.name for user in users)
    
    @pytest.mark.asyncio
    async def test_get_users_needing_onboarding(self, user_repository, mock_db_session):
        """Test getting users who need onboarding."""
        # Create mock users needing onboarding
        mock_users = [
            Mock(spec=User, id=1, onboarding_completed=False, is_active=True),
            Mock(spec=User, id=2, onboarding_completed=False, is_active=True)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_db_session.execute.return_value = mock_result
        
        users = await user_repository.get_users_needing_onboarding()
        
        assert len(users) == 2
        assert all(not user.onboarding_completed for user in users)
        assert all(user.is_active for user in users)


class TestUserServiceStatistics:
    """Test user service statistics methods."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def user_service(self, mock_db_session):
        """Create UserService instance with mocked dependencies."""
        return UserService(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_user_statistics_with_insights(self, user_service):
        """Test getting user statistics with computed insights."""
        # Mock repository statistics
        mock_stats = {
            "total_users": 1000,
            "active_users": 850,
            "verified_users": 600,
            "onboarded_users": 800,
            "new_users_30d": 75,
            "avg_baseline_footprint": 8500.0,
            "onboarding_completion_rate": 80.0,
            "verification_rate": 60.0
        }
        
        user_service.user_repository.get_user_statistics = AsyncMock(return_value=mock_stats)
        
        stats = await user_service.get_user_statistics()
        
        # Check base statistics
        assert stats["total_users"] == 1000
        assert stats["new_users_30d"] == 75
        
        # Check computed insights
        assert "insights" in stats
        insights = stats["insights"]
        
        assert insights["growth_trend"] == "positive"  # new_users_30d > 0
        assert insights["engagement_level"] == "high"  # onboarding_completion_rate > 70
        assert insights["verification_status"] == "needs_improvement"  # verification_rate <= 50
    
    @pytest.mark.asyncio
    async def test_get_user_statistics_low_engagement(self, user_service):
        """Test statistics with low engagement metrics."""
        mock_stats = {
            "total_users": 100,
            "active_users": 50,
            "verified_users": 30,
            "onboarded_users": 40,
            "new_users_30d": 0,
            "avg_baseline_footprint": 9000.0,
            "onboarding_completion_rate": 40.0,
            "verification_rate": 30.0
        }
        
        user_service.user_repository.get_user_statistics = AsyncMock(return_value=mock_stats)
        
        stats = await user_service.get_user_statistics()
        
        insights = stats["insights"]
        assert insights["growth_trend"] == "stable"  # new_users_30d == 0
        assert insights["engagement_level"] == "medium"  # onboarding_completion_rate <= 70
        assert insights["verification_status"] == "needs_improvement"  # verification_rate <= 50
    
    @pytest.mark.asyncio
    async def test_search_users_business_logic(self, user_service):
        """Test user search with business logic filtering."""
        # Mock repository search results
        mock_users = [
            Mock(spec=User, id=1, name="Active User", is_active=True),
            Mock(spec=User, id=2, name="Inactive User", is_active=False)
        ]
        
        user_service.user_repository.search_users = AsyncMock(return_value=mock_users)
        
        users = await user_service.search_users("User", limit=10)
        
        # Verify repository was called with correct parameters
        user_service.user_repository.search_users.assert_called_once_with(
            query="User",
            limit=10,
            include_inactive=False
        )
        
        assert users == mock_users


class TestUserAnalytics:
    """Test user analytics and aggregation functionality."""
    
    def test_user_carbon_stats_calculation(self):
        """Test carbon statistics calculation."""
        user = User(email="test@example.com")
        user.baseline_footprint = Decimal("10000")
        user.current_footprint = Decimal("7500")
        user.total_co2_saved = Decimal("2500")
        user.current_streak = 30
        user.longest_streak = 45
        user.eco_score = 2000
        
        stats = user.get_carbon_stats()
        
        assert stats["baseline_footprint"] == 10000.0
        assert stats["current_footprint"] == 7500.0
        assert stats["total_co2_saved"] == 2500.0
        assert stats["reduction_percentage"] == 25.0  # (10000-7500)/10000 * 100
        assert stats["current_streak"] == 30
        assert stats["longest_streak"] == 45
        assert stats["eco_score"] == 2000
    
    def test_user_carbon_stats_no_baseline(self):
        """Test carbon statistics when no baseline exists."""
        user = User(email="test@example.com")
        user.baseline_footprint = None
        user.current_footprint = None
        user.total_co2_saved = Decimal("500")
        
        stats = user.get_carbon_stats()
        
        assert stats["baseline_footprint"] is None
        assert stats["current_footprint"] is None
        assert stats["total_co2_saved"] == 500.0
        assert stats["reduction_percentage"] is None
    
    def test_eco_score_comprehensive_calculation(self):
        """Test comprehensive eco score calculation."""
        user = User(email="test@example.com")
        user.total_co2_saved = Decimal("1500")  # 1500 points
        user.current_streak = 25                # 250 points (25 * 10)
        user.baseline_footprint = Decimal("12000")
        user.current_footprint = Decimal("9000") # 25% reduction = 250 points (25 * 10)
        
        score = user.calculate_eco_score()
        
        # Expected: 1500 + 250 + 250 = 2000
        assert score == 2000
        assert user.eco_score == 2000
    
    def test_eco_score_no_baseline(self):
        """Test eco score calculation without baseline footprint."""
        user = User(email="test@example.com")
        user.total_co2_saved = Decimal("800")
        user.current_streak = 15
        user.baseline_footprint = None
        user.current_footprint = None
        
        score = user.calculate_eco_score()
        
        # Expected: 800 + 150 + 0 = 950
        assert score == 950
    
    def test_eco_score_negative_prevention(self):
        """Test that eco score cannot be negative."""
        user = User(email="test@example.com")
        user.total_co2_saved = Decimal("-100")  # Somehow negative
        user.current_streak = 0
        user.baseline_footprint = Decimal("5000")
        user.current_footprint = Decimal("6000")  # Increased footprint
        
        score = user.calculate_eco_score()
        
        assert score == 0  # Should not be negative
        assert user.eco_score == 0


class TestUserAggregationMethods:
    """Test user data aggregation methods."""
    
    def test_user_preferences_json_handling(self):
        """Test user preferences JSON serialization/deserialization."""
        user = User(email="test@example.com")
        
        preferences = {
            "notifications": {
                "email": True,
                "push": False
            },
            "privacy": {
                "share_stats": True,
                "public_profile": False
            },
            "goals": ["reduce_transport", "eat_less_meat"]
        }
        
        user.set_preferences(preferences)
        retrieved_preferences = user.get_preferences()
        
        assert retrieved_preferences == preferences
        assert retrieved_preferences["notifications"]["email"] is True
        assert len(retrieved_preferences["goals"]) == 2
    
    def test_user_preferences_invalid_json(self):
        """Test handling of invalid JSON in preferences."""
        user = User(email="test@example.com")
        user.preferences = "invalid json string"
        
        result = user.get_preferences()
        
        assert result is None
    
    def test_user_onboarding_data_complex(self):
        """Test complex onboarding data handling."""
        user = User(email="test@example.com")
        
        complex_data = {
            "transport": {
                "primary_mode": "car",
                "secondary_modes": ["bike", "walk"],
                "weekly_distances": {
                    "car": 150,
                    "bike": 30,
                    "walk": 10
                }
            },
            "diet": {
                "type": "flexitarian",
                "restrictions": ["no_beef"],
                "local_preference": 0.7
            },
            "energy": {
                "home_type": "apartment",
                "efficiency_rating": "B",
                "renewable_sources": ["solar", "wind"]
            },
            "goals": {
                "primary": "reduce_carbon_footprint",
                "secondary": ["save_money", "health"],
                "target_reduction": 0.3
            }
        }
        
        user.set_onboarding_data(complex_data)
        retrieved_data = user.get_onboarding_data()
        
        assert retrieved_data == complex_data
        assert retrieved_data["transport"]["weekly_distances"]["car"] == 150
        assert "solar" in retrieved_data["energy"]["renewable_sources"]
        assert retrieved_data["goals"]["target_reduction"] == 0.3


class TestUserStatisticsIntegration:
    """Test integration of user statistics across the system."""
    
    @pytest.fixture
    def sample_users(self):
        """Create sample users for testing."""
        users = []
        
        # High-performing user
        user1 = User(
            id=1,
            email="eco_champion@example.com",
            is_active=True,
            is_verified=True,
            onboarding_completed=True,
            baseline_footprint=Decimal("12000"),
            current_footprint=Decimal("8000"),
            total_co2_saved=Decimal("4000"),
            current_streak=60,
            longest_streak=60,
            eco_score=5000
        )
        users.append(user1)
        
        # Average user
        user2 = User(
            id=2,
            email="average_user@example.com",
            is_active=True,
            is_verified=False,
            onboarding_completed=True,
            baseline_footprint=Decimal("8000"),
            current_footprint=Decimal("7000"),
            total_co2_saved=Decimal("1000"),
            current_streak=10,
            longest_streak=15,
            eco_score=1200
        )
        users.append(user2)
        
        # New user (not onboarded)
        user3 = User(
            id=3,
            email="new_user@example.com",
            is_active=True,
            is_verified=False,
            onboarding_completed=False,
            baseline_footprint=None,
            current_footprint=None,
            total_co2_saved=Decimal("0"),
            current_streak=0,
            longest_streak=0,
            eco_score=0
        )
        users.append(user3)
        
        return users
    
    def test_user_performance_categorization(self, sample_users):
        """Test categorizing users by performance."""
        high_performer = sample_users[0]
        average_user = sample_users[1]
        new_user = sample_users[2]
        
        # Test eco score categorization
        assert high_performer.eco_score >= 3000  # High performer
        assert 500 <= average_user.eco_score < 3000  # Average performer
        assert new_user.eco_score < 500  # New/low performer
        
        # Test streak categorization
        assert high_performer.current_streak >= 30  # Consistent user
        assert 5 <= average_user.current_streak < 30  # Moderate user
        assert new_user.current_streak < 5  # Inactive user
    
    def test_carbon_reduction_analysis(self, sample_users):
        """Test carbon footprint reduction analysis."""
        high_performer = sample_users[0]
        average_user = sample_users[1]
        
        # Calculate reduction percentages
        high_reduction = ((high_performer.baseline_footprint - high_performer.current_footprint) / 
                         high_performer.baseline_footprint) * 100
        
        average_reduction = ((average_user.baseline_footprint - average_user.current_footprint) / 
                           average_user.baseline_footprint) * 100
        
        assert high_reduction > 30  # High performer has >30% reduction
        assert 10 <= average_reduction <= 30  # Average user has moderate reduction
    
    def test_user_engagement_metrics(self, sample_users):
        """Test user engagement metrics calculation."""
        total_users = len(sample_users)
        active_users = sum(1 for user in sample_users if user.is_active)
        onboarded_users = sum(1 for user in sample_users if user.onboarding_completed)
        verified_users = sum(1 for user in sample_users if user.is_verified)
        
        # Calculate engagement rates
        onboarding_rate = (onboarded_users / total_users) * 100
        verification_rate = (verified_users / total_users) * 100
        
        assert onboarding_rate == 66.67  # 2/3 users onboarded (rounded)
        assert verification_rate == 33.33  # 1/3 users verified (rounded)
        assert active_users == 3  # All users active


if __name__ == "__main__":
    pytest.main([__file__])