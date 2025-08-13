"""
Test-Driven Development for Analytics Service

This module contains tests written BEFORE implementation for the
analytics service functionality including dashboard data generation,
carbon footprint trend analysis, and user comparison features.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import AnalyticsService
from app.models.user import User
from app.models.user_habit import UserHabit


class TestAnalyticsService:
    """Test suite for AnalyticsService functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def analytics_service(self, mock_db_session):
        """Create analytics service instance."""
        return AnalyticsService(mock_db_session)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "user_id": 1,
            "baseline_footprint": 12000.0,
            "total_co2_saved": 500.0,
            "current_streak": 15,
            "eco_score": 850,
            "created_at": datetime.utcnow() - timedelta(days=30)
        }
    
    @pytest.fixture
    def sample_habit_data(self):
        """Sample habit data for testing."""
        return [
            {
                "id": 1,
                "user_id": 1,
                "category": "transport",
                "co2_saved": 2.5,
                "logged_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "id": 2,
                "user_id": 1,
                "category": "energy",
                "co2_saved": 1.8,
                "logged_at": datetime.utcnow() - timedelta(days=2)
            }
        ]
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_success(self, analytics_service, sample_user_data):
        """Test successful dashboard data generation."""
        # Mock repository methods
        analytics_service.user_repository.get_by_id = AsyncMock(return_value=Mock(**sample_user_data))
        analytics_service.habit_repository.get_user_habit_statistics = AsyncMock(return_value={
            "total_habits": 25,
            "total_co2_saved": 500.0,
            "categories": {"transport": 15, "energy": 10}
        })
        
        # Call method
        result = await analytics_service.generate_dashboard_data(user_id=1)
        
        # Assertions
        assert result is not None
        assert result["user_id"] == 1
        assert "overview" in result
        assert "trends" in result
        assert "categories" in result
        assert result["overview"]["total_co2_saved"] == 500.0
        assert result["overview"]["current_streak"] == 15
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_user_not_found(self, analytics_service):
        """Test dashboard data generation when user not found."""
        # Mock user not found
        analytics_service.user_repository.get_by_id = AsyncMock(return_value=None)
        
        # Call method and expect exception
        with pytest.raises(ValueError, match="User not found"):
            await analytics_service.generate_dashboard_data(user_id=999)
    
    @pytest.mark.asyncio
    async def test_get_carbon_footprint_trends_success(self, analytics_service, sample_habit_data):
        """Test successful carbon footprint trend analysis."""
        # Mock habit repository
        analytics_service.habit_repository.get_user_habits_by_date_range = AsyncMock(
            return_value=sample_habit_data
        )
        
        # Call method
        result = await analytics_service.get_carbon_footprint_trends(
            user_id=1, 
            days_back=30
        )
        
        # Assertions
        assert result is not None
        assert "daily_trends" in result
        assert "weekly_trends" in result
        assert "category_breakdown" in result
        assert "total_period_savings" in result
        assert result["total_period_savings"] > 0
    
    @pytest.mark.asyncio
    async def test_get_carbon_footprint_trends_no_data(self, analytics_service):
        """Test carbon footprint trends with no habit data."""
        # Mock empty habit data
        analytics_service.habit_repository.get_user_habits_by_date_range = AsyncMock(
            return_value=[]
        )
        
        # Call method
        result = await analytics_service.get_carbon_footprint_trends(
            user_id=1, 
            days_back=30
        )
        
        # Assertions
        assert result is not None
        assert result["total_period_savings"] == 0
        assert len(result["daily_trends"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_user_comparison_success(self, analytics_service):
        """Test successful user comparison and benchmarking."""
        # Mock user repository methods
        analytics_service.user_repository.get_user_percentile = AsyncMock(return_value=75.0)
        analytics_service.user_repository.get_average_metrics = AsyncMock(return_value={
            "avg_co2_saved": 300.0,
            "avg_streak": 8,
            "avg_eco_score": 650
        })
        analytics_service.user_repository.get_by_id = AsyncMock(return_value=Mock(
            total_co2_saved=500.0,
            current_streak=15,
            eco_score=850
        ))
        
        # Call method
        result = await analytics_service.get_user_comparison(user_id=1)
        
        # Assertions
        assert result is not None
        assert "percentile" in result
        assert "comparison" in result
        assert result["percentile"] == 75.0
        assert result["comparison"]["co2_saved"]["user_value"] == 500.0
        assert result["comparison"]["co2_saved"]["average_value"] == 300.0
        assert result["comparison"]["co2_saved"]["performance"] == "above_average"
    
    @pytest.mark.asyncio
    async def test_get_category_analytics_success(self, analytics_service):
        """Test successful category analytics generation."""
        # Mock habit repository
        analytics_service.habit_repository.get_category_statistics = AsyncMock(return_value={
            "transport": {"count": 15, "co2_saved": 45.0, "avg_impact": 3.0},
            "energy": {"count": 10, "co2_saved": 25.0, "avg_impact": 2.5},
            "diet": {"count": 8, "co2_saved": 20.0, "avg_impact": 2.5}
        })
        
        # Call method
        result = await analytics_service.get_category_analytics(user_id=1)
        
        # Assertions
        assert result is not None
        assert "categories" in result
        assert "top_category" in result
        assert "recommendations" in result
        assert result["top_category"]["name"] == "transport"
        assert result["top_category"]["co2_saved"] == 45.0
    
    @pytest.mark.asyncio
    async def test_get_aggregated_data_success(self, analytics_service):
        """Test successful data aggregation with proper indexing."""
        # Mock repository methods
        analytics_service.user_repository.get_total_users = AsyncMock(return_value=1000)
        analytics_service.habit_repository.get_total_habits = AsyncMock(return_value=25000)
        analytics_service.habit_repository.get_total_co2_saved = AsyncMock(return_value=50000.0)
        
        # Call method
        result = await analytics_service.get_aggregated_data()
        
        # Assertions
        assert result is not None
        assert "platform_stats" in result
        assert result["platform_stats"]["total_users"] == 1000
        assert result["platform_stats"]["total_habits"] == 25000
        assert result["platform_stats"]["total_co2_saved"] == 50000.0
    
    @pytest.mark.asyncio
    async def test_error_handling_database_error(self, analytics_service):
        """Test error handling when database operations fail."""
        # Mock database error
        analytics_service.user_repository.get_by_id = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        
        # Call method and expect exception handling
        with pytest.raises(Exception):
            await analytics_service.generate_dashboard_data(user_id=1)
    
    @pytest.mark.asyncio
    async def test_calculate_trend_direction(self, analytics_service):
        """Test trend direction calculation."""
        # Test data with increasing trend
        increasing_data = [10, 15, 20, 25, 30]
        trend = analytics_service._calculate_trend_direction(increasing_data)
        assert trend == "increasing"
        
        # Test data with decreasing trend
        decreasing_data = [30, 25, 20, 15, 10]
        trend = analytics_service._calculate_trend_direction(decreasing_data)
        assert trend == "decreasing"
        
        # Test data with stable trend
        stable_data = [20, 21, 19, 20, 20]
        trend = analytics_service._calculate_trend_direction(stable_data)
        assert trend == "stable"
    
    @pytest.mark.asyncio
    async def test_generate_insights_success(self, analytics_service):
        """Test successful insights generation."""
        # Mock trend data
        trend_data = {
            "daily_trends": [
                {"date": "2024-01-01", "co2_saved": 5.0},
                {"date": "2024-01-02", "co2_saved": 7.0},
                {"date": "2024-01-03", "co2_saved": 6.0}
            ],
            "category_breakdown": {
                "transport": 60,
                "energy": 30,
                "diet": 10
            }
        }
        
        # Call method
        insights = analytics_service._generate_insights(trend_data)
        
        # Assertions
        assert insights is not None
        assert len(insights) > 0
        assert any("transport" in insight.lower() for insight in insights)
    
    def test_validate_date_range(self, analytics_service):
        """Test date range validation."""
        # Valid date range
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        is_valid = analytics_service._validate_date_range(start_date, end_date)
        assert is_valid is True
        
        # Invalid date range (start after end)
        invalid_start = datetime.utcnow()
        invalid_end = datetime.utcnow() - timedelta(days=30)
        
        is_valid = analytics_service._validate_date_range(invalid_start, invalid_end)
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, analytics_service):
        """Test performance metrics calculation."""
        # Mock data
        analytics_service.habit_repository.get_user_habit_statistics = AsyncMock(return_value={
            "total_habits": 50,
            "total_co2_saved": 150.0,
            "avg_daily_habits": 2.5,
            "consistency_score": 0.85
        })
        
        # Call method
        result = await analytics_service.get_performance_metrics(user_id=1, days_back=30)
        
        # Assertions
        assert result is not None
        assert "efficiency_score" in result
        assert "consistency_score" in result
        assert "impact_score" in result
        assert 0 <= result["consistency_score"] <= 1