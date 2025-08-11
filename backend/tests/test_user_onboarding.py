"""
Tests for User Onboarding Functionality

This module tests the user onboarding process, baseline carbon footprint
calculations, and user statistics aggregation methods.
"""

import pytest
import json
from decimal import Decimal
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user_service import UserService, CarbonFootprintCalculator
from app.repositories.user_repository import UserRepository
from app.schemas.user import OnboardingSurvey, TransportSurvey, DietSurvey, EnergySurvey, LifestyleSurvey


class TestCarbonFootprintCalculator:
    """Test carbon footprint calculation logic."""
    
    def test_calculate_baseline_footprint_comprehensive(self):
        """Test comprehensive baseline footprint calculation."""
        # Comprehensive onboarding data
        onboarding_data = {
            "transport": {
                "car_km_per_day": 30,  # High car usage
                "public_transport_km_per_day": 10,  # Some public transport
                "bike_km_per_day": 5,  # Some cycling
                "walk_km_per_day": 2   # Some walking
            },
            "flights_per_year": 4,  # 4 flights per year
            "diet_type": "meat_moderate",
            "energy": {
                "electricity_kwh_per_month": 400,  # Above average
                "gas_therms_per_month": 60,        # Above average
                "renewable_energy_percent": 20     # Some renewable
            },
            "lifestyle": {
                "shopping_frequency": "medium",
                "waste_reduction": "medium"
            }
        }
        
        footprint = CarbonFootprintCalculator.calculate_baseline_footprint(onboarding_data)
        
        # Expected calculation:
        # Car: 30 * 365 * 0.21 = 2299.5
        # Public transport: 10 * 365 * 0.05 = 182.5
        # Flights: 4 * 500 = 2000
        # Diet: 1900 (meat_moderate)
        # Electricity: 400 * 12 * 0.5 = 2400
        # Gas: 60 * 12 * 5.3 = 3816
        # Renewable reduction: 2400 * 0.2 * 0.01 = 4.8
        # Shopping: 800
        # Waste reduction: -100
        # Total: ~13293.2
        
        assert footprint > 10000  # Should be high due to car usage and flights
        assert footprint < 15000  # But not excessive
        assert isinstance(footprint, float)
    
    def test_calculate_baseline_footprint_eco_friendly(self):
        """Test baseline calculation for eco-friendly lifestyle."""
        onboarding_data = {
            "transport": {
                "car_km_per_day": 0,     # No car
                "public_transport_km_per_day": 15,  # Public transport
                "bike_km_per_day": 10,   # Lots of cycling
                "walk_km_per_day": 5     # Walking
            },
            "flights_per_year": 0,  # No flights
            "diet_type": "vegan",
            "energy": {
                "electricity_kwh_per_month": 200,  # Low usage
                "gas_therms_per_month": 20,        # Low usage
                "renewable_energy_percent": 80     # Mostly renewable
            },
            "lifestyle": {
                "shopping_frequency": "low",
                "waste_reduction": "high"
            }
        }
        
        footprint = CarbonFootprintCalculator.calculate_baseline_footprint(onboarding_data)
        
        # Should be much lower for eco-friendly lifestyle
        assert footprint < 5000
        assert footprint >= 1000  # Minimum footprint
    
    def test_calculate_baseline_footprint_high_impact(self):
        """Test baseline calculation for high-impact lifestyle."""
        onboarding_data = {
            "transport": {
                "car_km_per_day": 80,    # Very high car usage
                "public_transport_km_per_day": 0,
                "bike_km_per_day": 0,
                "walk_km_per_day": 0
            },
            "flights_per_year": 12,  # Frequent flyer
            "diet_type": "meat_heavy",
            "energy": {
                "electricity_kwh_per_month": 800,  # Very high usage
                "gas_therms_per_month": 120,       # Very high usage
                "renewable_energy_percent": 0      # No renewable
            },
            "lifestyle": {
                "shopping_frequency": "high",
                "waste_reduction": "low"
            }
        }
        
        footprint = CarbonFootprintCalculator.calculate_baseline_footprint(onboarding_data)
        
        # Should be very high for high-impact lifestyle
        assert footprint > 20000
    
    def test_calculate_baseline_footprint_missing_data(self):
        """Test baseline calculation with missing data."""
        onboarding_data = {
            "diet_type": "vegetarian"
            # Missing most data
        }
        
        footprint = CarbonFootprintCalculator.calculate_baseline_footprint(onboarding_data)
        
        # Should still return a reasonable value
        assert footprint >= 1000
        assert footprint < 10000
    
    def test_calculate_baseline_footprint_invalid_data(self):
        """Test baseline calculation with invalid data."""
        onboarding_data = {
            "transport": "invalid",  # Invalid structure
            "diet_type": "invalid_diet",  # Invalid diet type
            "energy": {
                "electricity_kwh_per_month": -100  # Negative value
            }
        }
        
        # Should handle gracefully and return default
        footprint = CarbonFootprintCalculator.calculate_baseline_footprint(onboarding_data)
        assert footprint == 8000.0  # Default average footprint
    
    def test_get_footprint_category(self):
        """Test footprint categorization."""
        assert CarbonFootprintCalculator.get_footprint_category(2000) == "excellent"
        assert CarbonFootprintCalculator.get_footprint_category(4000) == "good"
        assert CarbonFootprintCalculator.get_footprint_category(6000) == "average"
        assert CarbonFootprintCalculator.get_footprint_category(10000) == "high"
        assert CarbonFootprintCalculator.get_footprint_category(15000) == "very_high"
    
    def test_get_reduction_recommendations_high_car_usage(self):
        """Test recommendations for high car usage."""
        onboarding_data = {
            "transport": {
                "car_km_per_day": 50  # High car usage
            },
            "diet_type": "meat_heavy",
            "energy": {
                "renewable_energy_percent": 10  # Low renewable
            }
        }
        
        recommendations = CarbonFootprintCalculator.get_reduction_recommendations(onboarding_data)
        
        # Should get transport, diet, and energy recommendations
        assert len(recommendations) >= 2
        
        # Check for transport recommendation
        transport_rec = next((r for r in recommendations if r["category"] == "transport"), None)
        assert transport_rec is not None
        assert "car" in transport_rec["title"].lower()
        assert transport_rec["potential_savings"] > 0
    
    def test_get_reduction_recommendations_eco_friendly(self):
        """Test recommendations for already eco-friendly user."""
        onboarding_data = {
            "transport": {
                "car_km_per_day": 5,  # Low car usage
                "bike_km_per_day": 20  # High cycling
            },
            "diet_type": "vegan",
            "energy": {
                "renewable_energy_percent": 90  # High renewable
            }
        }
        
        recommendations = CarbonFootprintCalculator.get_reduction_recommendations(onboarding_data)
        
        # Should get fewer recommendations
        assert len(recommendations) <= 1
    
    def test_get_reduction_recommendations_error_handling(self):
        """Test recommendations with invalid data."""
        onboarding_data = {
            "invalid": "data"
        }
        
        recommendations = CarbonFootprintCalculator.get_reduction_recommendations(onboarding_data)
        
        # Should handle gracefully
        assert isinstance(recommendations, list)


class TestUserOnboardingIntegration:
    """Test user onboarding integration with database."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def user_service(self, mock_db_session):
        """Create UserService instance with mocked dependencies."""
        return UserService(mock_db_session)
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        user = User(
            id=1,
            email="test@example.com",
            firebase_uid="test_firebase_uid",
            name="Test User",
            is_active=True,
            onboarding_completed=False
        )
        return user
    
    @pytest.fixture
    def sample_onboarding_data(self):
        """Create sample onboarding data."""
        return {
            "transport": {
                "car_km_per_day": 20,
                "public_transport_km_per_day": 5,
                "bike_km_per_day": 3,
                "walk_km_per_day": 2
            },
            "flights_per_year": 2,
            "diet_type": "meat_moderate",
            "energy": {
                "electricity_kwh_per_month": 300,
                "gas_therms_per_month": 40,
                "renewable_energy_percent": 30
            },
            "lifestyle": {
                "shopping_frequency": "medium",
                "waste_reduction": "medium"
            },
            "goals": ["reduce_transport", "eat_less_meat"],
            "motivation": "Help the environment"
        }
    
    @pytest.mark.asyncio
    async def test_complete_user_onboarding_success(
        self, 
        user_service, 
        sample_user, 
        sample_onboarding_data
    ):
        """Test successful user onboarding completion."""
        # Mock repository methods
        user_service.user_repository.get_by_id = Mock(return_value=sample_user)
        user_service.user_repository.complete_onboarding = Mock(return_value=sample_user)
        user_service.user_repository.update_baseline_footprint = Mock(return_value=sample_user)
        
        result = await user_service.complete_user_onboarding(1, sample_onboarding_data)
        
        assert result is not None
        assert result == sample_user
        
        # Verify repository methods were called
        user_service.user_repository.complete_onboarding.assert_called_once_with(1, sample_onboarding_data)
        user_service.user_repository.update_baseline_footprint.assert_called_once()
        
        # Verify baseline footprint was calculated
        call_args = user_service.user_repository.update_baseline_footprint.call_args
        baseline_footprint = call_args[0][1]
        assert isinstance(baseline_footprint, float)
        assert baseline_footprint > 0
    
    @pytest.mark.asyncio
    async def test_complete_user_onboarding_user_not_found(
        self, 
        user_service, 
        sample_onboarding_data
    ):
        """Test onboarding completion when user not found."""
        # Mock repository to return None
        user_service.user_repository.get_by_id = Mock(return_value=None)
        
        result = await user_service.complete_user_onboarding(999, sample_onboarding_data)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_recommendations_success(
        self, 
        user_service, 
        sample_user, 
        sample_onboarding_data
    ):
        """Test getting user recommendations."""
        # Set up user with preferences
        sample_user.preferences = json.dumps(sample_onboarding_data)
        user_service.user_repository.get_by_id = Mock(return_value=sample_user)
        
        recommendations = await user_service.get_user_recommendations(1)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check recommendation structure
        for rec in recommendations:
            assert "category" in rec
            assert "title" in rec
            assert "description" in rec
            assert "potential_savings" in rec
            assert "difficulty" in rec
    
    @pytest.mark.asyncio
    async def test_get_user_recommendations_no_preferences(
        self, 
        user_service, 
        sample_user
    ):
        """Test getting recommendations when user has no preferences."""
        sample_user.preferences = None
        user_service.user_repository.get_by_id = Mock(return_value=sample_user)
        
        recommendations = await user_service.get_user_recommendations(1)
        
        assert recommendations == []
    
    @pytest.mark.asyncio
    async def test_get_user_recommendations_invalid_json(
        self, 
        user_service, 
        sample_user
    ):
        """Test getting recommendations with invalid JSON preferences."""
        sample_user.preferences = "invalid json"
        user_service.user_repository.get_by_id = Mock(return_value=sample_user)
        
        recommendations = await user_service.get_user_recommendations(1)
        
        assert recommendations == []


class TestUserModelOnboarding:
    """Test User model onboarding methods."""
    
    def test_set_onboarding_data(self):
        """Test setting onboarding data."""
        user = User(email="test@example.com")
        survey_data = {
            "transport": {"car_km_per_day": 20},
            "diet_type": "vegetarian"
        }
        
        user.set_onboarding_data(survey_data)
        
        assert user.onboarding_data is not None
        retrieved_data = user.get_onboarding_data()
        assert retrieved_data == survey_data
    
    def test_get_onboarding_data_none(self):
        """Test getting onboarding data when none exists."""
        user = User(email="test@example.com")
        
        result = user.get_onboarding_data()
        
        assert result is None
    
    def test_get_onboarding_data_invalid_json(self):
        """Test getting onboarding data with invalid JSON."""
        user = User(email="test@example.com")
        user.onboarding_data = "invalid json"
        
        result = user.get_onboarding_data()
        
        assert result is None
    
    def test_calculate_baseline_footprint_user_method(self):
        """Test user model baseline footprint calculation."""
        user = User(email="test@example.com")
        survey_data = {
            "transport": {
                "car_km_per_week": 100,
                "public_transport_hours_per_week": 5,
                "flights_per_year": 2
            },
            "diet": {
                "type": "mixed"
            },
            "energy": {
                "home_size": "medium",
                "energy_source": "mixed"
            },
            "lifestyle": {
                "shopping_frequency": "moderate"
            }
        }
        
        footprint = user.calculate_baseline_footprint(survey_data)
        
        assert isinstance(footprint, float)
        assert footprint > 0
        # Expected: car (1040) + transport (13) + flights (1000) + diet (3000) + energy (3000) + lifestyle (1000) = ~9053
        assert 8000 < footprint < 12000
    
    def test_complete_onboarding(self):
        """Test complete onboarding process."""
        user = User(email="test@example.com")
        survey_data = {
            "transport": {"car_km_per_week": 50},
            "diet": {"type": "vegetarian"},
            "energy": {"home_size": "small", "energy_source": "renewable"},
            "lifestyle": {"shopping_frequency": "minimal"}
        }
        
        user.complete_onboarding(survey_data)
        
        assert user.onboarding_completed is True
        assert user.baseline_footprint is not None
        assert user.current_footprint == user.baseline_footprint
        assert user.get_onboarding_data() == survey_data
    
    def test_update_streak_increment(self):
        """Test streak increment."""
        user = User(email="test@example.com")
        user.current_streak = 5
        user.longest_streak = 10
        
        user.update_streak(increment=True)
        
        assert user.current_streak == 6
        assert user.longest_streak == 10  # Unchanged
    
    def test_update_streak_new_record(self):
        """Test streak increment creating new record."""
        user = User(email="test@example.com")
        user.current_streak = 10
        user.longest_streak = 10
        
        user.update_streak(increment=True)
        
        assert user.current_streak == 11
        assert user.longest_streak == 11  # New record
    
    def test_update_streak_reset(self):
        """Test streak reset."""
        user = User(email="test@example.com")
        user.current_streak = 5
        user.longest_streak = 10
        
        user.update_streak(increment=False)
        
        assert user.current_streak == 0
        assert user.longest_streak == 10  # Unchanged
    
    def test_add_co2_savings(self):
        """Test adding CO2 savings."""
        user = User(email="test@example.com")
        user.baseline_footprint = Decimal("10000")
        user.current_footprint = Decimal("10000")
        user.total_co2_saved = Decimal("0")
        
        user.add_co2_savings(500)
        
        assert user.total_co2_saved == 500
        assert user.current_footprint == 9500  # Reduced from baseline
    
    def test_add_co2_savings_no_negative_footprint(self):
        """Test CO2 savings don't create negative footprint."""
        user = User(email="test@example.com")
        user.baseline_footprint = Decimal("1000")
        user.current_footprint = Decimal("1000")
        user.total_co2_saved = Decimal("0")
        
        user.add_co2_savings(1500)  # More than baseline
        
        assert user.total_co2_saved == 1500
        assert user.current_footprint == 0  # Can't go below 0
    
    def test_calculate_eco_score(self):
        """Test eco score calculation."""
        user = User(email="test@example.com")
        user.total_co2_saved = Decimal("1000")
        user.current_streak = 10
        user.baseline_footprint = Decimal("10000")
        user.current_footprint = Decimal("8000")
        
        score = user.calculate_eco_score()
        
        # Expected: 1000 (CO2) + 100 (streak) + 200 (20% reduction * 10) = 1300
        assert score == 1300
        assert user.eco_score == 1300
    
    def test_get_carbon_stats(self):
        """Test getting carbon statistics."""
        user = User(email="test@example.com")
        user.baseline_footprint = Decimal("10000")
        user.current_footprint = Decimal("8000")
        user.total_co2_saved = Decimal("2000")
        user.current_streak = 15
        user.longest_streak = 20
        user.eco_score = 1500
        
        stats = user.get_carbon_stats()
        
        assert stats["baseline_footprint"] == 10000.0
        assert stats["current_footprint"] == 8000.0
        assert stats["total_co2_saved"] == 2000.0
        assert stats["reduction_percentage"] == 20.0
        assert stats["current_streak"] == 15
        assert stats["longest_streak"] == 20
        assert stats["eco_score"] == 1500


class TestOnboardingSchemas:
    """Test onboarding Pydantic schemas."""
    
    def test_transport_survey_valid(self):
        """Test valid transport survey data."""
        data = {
            "car_km_per_week": 100.5,
            "public_transport_hours_per_week": 10.0,
            "flights_per_year": 4,
            "bike_km_per_week": 50.0,
            "walk_km_per_week": 20.0
        }
        
        survey = TransportSurvey(**data)
        
        assert survey.car_km_per_week == 100.5
        assert survey.flights_per_year == 4
    
    def test_transport_survey_negative_values(self):
        """Test transport survey with negative values."""
        with pytest.raises(ValueError):
            TransportSurvey(car_km_per_week=-10)
    
    def test_diet_survey_valid(self):
        """Test valid diet survey data."""
        data = {
            "type": "vegetarian",
            "meals_per_week": 21,
            "local_food_percentage": 75.0
        }
        
        survey = DietSurvey(**data)
        
        assert survey.type == "vegetarian"
        assert survey.local_food_percentage == 75.0
    
    def test_diet_survey_invalid_type(self):
        """Test diet survey with invalid type."""
        with pytest.raises(ValueError):
            DietSurvey(type="invalid_diet")
    
    def test_energy_survey_valid(self):
        """Test valid energy survey data."""
        data = {
            "home_size": "medium",
            "energy_source": "renewable",
            "heating_type": "electric",
            "monthly_kwh": 300.0
        }
        
        survey = EnergySurvey(**data)
        
        assert survey.home_size == "medium"
        assert survey.energy_source == "renewable"
    
    def test_energy_survey_invalid_home_size(self):
        """Test energy survey with invalid home size."""
        with pytest.raises(ValueError):
            EnergySurvey(home_size="invalid", energy_source="mixed")
    
    def test_lifestyle_survey_valid(self):
        """Test valid lifestyle survey data."""
        data = {
            "shopping_frequency": "moderate",
            "waste_reduction_practices": ["recycling", "composting"],
            "recycling_frequency": "often"
        }
        
        survey = LifestyleSurvey(**data)
        
        assert survey.shopping_frequency == "moderate"
        assert len(survey.waste_reduction_practices) == 2
    
    def test_complete_onboarding_survey(self):
        """Test complete onboarding survey."""
        data = {
            "transport": {
                "car_km_per_week": 100,
                "public_transport_hours_per_week": 5,
                "flights_per_year": 2
            },
            "diet": {
                "type": "mixed",
                "meals_per_week": 21
            },
            "energy": {
                "home_size": "medium",
                "energy_source": "mixed"
            },
            "lifestyle": {
                "shopping_frequency": "moderate"
            },
            "goals": ["reduce_transport", "eat_less_meat"],
            "motivation": "Environmental concern"
        }
        
        survey = OnboardingSurvey(**data)
        
        assert survey.transport.car_km_per_week == 100
        assert survey.diet.type == "mixed"
        assert survey.energy.home_size == "medium"
        assert survey.lifestyle.shopping_frequency == "moderate"
        assert len(survey.goals) == 2
        assert survey.motivation == "Environmental concern"


if __name__ == "__main__":
    pytest.main([__file__])