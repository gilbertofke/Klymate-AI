"""
User Service Layer

This module provides the UserService class that implements business logic
for user operations, including registration, profile management, and
carbon footprint calculations.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime
import json

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserProfile
from app.utils.firebase_auth import FirebaseAuth, FirebaseAuthError

logger = logging.getLogger(__name__)


class CarbonFootprintCalculator:
    """
    Utility class for calculating carbon footprints based on user data.
    
    This class contains the business logic for converting user lifestyle
    data into carbon footprint estimates.
    """
    
    # Carbon footprint factors (kg CO2 per unit per year)
    TRANSPORT_FACTORS = {
        "car_km_per_day": 0.21 * 365,  # 0.21 kg CO2 per km * 365 days
        "public_transport_km_per_day": 0.05 * 365,  # 0.05 kg CO2 per km * 365 days
        "flights_per_year": 500,  # 500 kg CO2 per flight (average domestic)
        "bike_km_per_day": 0,  # Zero emissions
        "walk_km_per_day": 0   # Zero emissions
    }
    
    DIET_FACTORS = {
        "meat_heavy": 2500,     # kg CO2 per year
        "meat_moderate": 1900,  # kg CO2 per year
        "meat_light": 1500,     # kg CO2 per year
        "vegetarian": 1200,     # kg CO2 per year
        "vegan": 1000          # kg CO2 per year
    }
    
    ENERGY_FACTORS = {
        "electricity_kwh_per_month": 0.5 * 12,  # 0.5 kg CO2 per kWh * 12 months
        "gas_therms_per_month": 5.3 * 12,      # 5.3 kg CO2 per therm * 12 months
        "renewable_energy_percent": -0.01       # Reduction factor
    }
    
    LIFESTYLE_FACTORS = {
        "shopping_frequency": {
            "high": 1200,      # kg CO2 per year
            "medium": 800,     # kg CO2 per year
            "low": 400         # kg CO2 per year
        },
        "waste_reduction": {
            "high": -200,      # kg CO2 reduction per year
            "medium": -100,    # kg CO2 reduction per year
            "low": 0           # No reduction
        }
    }
    
    @classmethod
    def calculate_baseline_footprint(cls, onboarding_data: Dict[str, Any]) -> float:
        """
        Calculate baseline carbon footprint from onboarding data.
        
        Args:
            onboarding_data: Dictionary containing user's lifestyle data
            
        Returns:
            Baseline carbon footprint in kg CO2 per year
        """
        try:
            total_footprint = 0.0
            
            # Transport emissions
            transport_data = onboarding_data.get("transport", {})
            for transport_type, daily_km in transport_data.items():
                if transport_type in cls.TRANSPORT_FACTORS:
                    total_footprint += daily_km * cls.TRANSPORT_FACTORS[transport_type]
            
            # Add flights
            flights_per_year = onboarding_data.get("flights_per_year", 0)
            total_footprint += flights_per_year * cls.TRANSPORT_FACTORS["flights_per_year"]
            
            # Diet emissions
            diet_type = onboarding_data.get("diet_type", "meat_moderate")
            if diet_type in cls.DIET_FACTORS:
                total_footprint += cls.DIET_FACTORS[diet_type]
            
            # Energy emissions
            energy_data = onboarding_data.get("energy", {})
            electricity_kwh = energy_data.get("electricity_kwh_per_month", 300)
            gas_therms = energy_data.get("gas_therms_per_month", 50)
            renewable_percent = energy_data.get("renewable_energy_percent", 0)
            
            electricity_emissions = electricity_kwh * cls.ENERGY_FACTORS["electricity_kwh_per_month"]
            gas_emissions = gas_therms * cls.ENERGY_FACTORS["gas_therms_per_month"]
            renewable_reduction = electricity_emissions * (renewable_percent / 100) * abs(cls.ENERGY_FACTORS["renewable_energy_percent"])
            
            total_footprint += electricity_emissions + gas_emissions - renewable_reduction
            
            # Lifestyle emissions
            lifestyle_data = onboarding_data.get("lifestyle", {})
            shopping_frequency = lifestyle_data.get("shopping_frequency", "medium")
            waste_reduction = lifestyle_data.get("waste_reduction", "low")
            
            if shopping_frequency in cls.LIFESTYLE_FACTORS["shopping_frequency"]:
                total_footprint += cls.LIFESTYLE_FACTORS["shopping_frequency"][shopping_frequency]
            
            if waste_reduction in cls.LIFESTYLE_FACTORS["waste_reduction"]:
                total_footprint += cls.LIFESTYLE_FACTORS["waste_reduction"][waste_reduction]
            
            # Ensure minimum footprint (can't be negative)
            total_footprint = max(total_footprint, 1000)  # Minimum 1 ton CO2/year
            
            logger.info(f"Calculated baseline footprint: {total_footprint:.2f} kg CO2/year")
            return round(total_footprint, 2)
            
        except Exception as e:
            logger.error(f"Error calculating baseline footprint: {str(e)}")
            # Return average footprint if calculation fails
            return 8000.0  # Average global footprint
    
    @classmethod
    def get_footprint_category(cls, footprint: float) -> str:
        """
        Categorize carbon footprint into performance levels.
        
        Args:
            footprint: Carbon footprint in kg CO2 per year
            
        Returns:
            Category string (excellent, good, average, high, very_high)
        """
        if footprint < 3000:
            return "excellent"
        elif footprint < 5000:
            return "good"
        elif footprint < 8000:
            return "average"
        elif footprint < 12000:
            return "high"
        else:
            return "very_high"
    
    @classmethod
    def get_reduction_recommendations(cls, onboarding_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized carbon reduction recommendations.
        
        Args:
            onboarding_data: User's lifestyle data
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        try:
            # Transport recommendations
            transport_data = onboarding_data.get("transport", {})
            car_km = transport_data.get("car_km_per_day", 0)
            if car_km > 20:
                recommendations.append({
                    "category": "transport",
                    "title": "Reduce Car Usage",
                    "description": "Consider using public transport or cycling for shorter trips",
                    "potential_savings": car_km * 0.1 * 365,  # 10% reduction
                    "difficulty": "medium"
                })
            
            # Diet recommendations
            diet_type = onboarding_data.get("diet_type", "meat_moderate")
            if diet_type in ["meat_heavy", "meat_moderate"]:
                recommendations.append({
                    "category": "diet",
                    "title": "Reduce Meat Consumption",
                    "description": "Try having 1-2 plant-based meals per week",
                    "potential_savings": 300,  # Estimated savings
                    "difficulty": "easy"
                })
            
            # Energy recommendations
            energy_data = onboarding_data.get("energy", {})
            renewable_percent = energy_data.get("renewable_energy_percent", 0)
            if renewable_percent < 50:
                recommendations.append({
                    "category": "energy",
                    "title": "Switch to Renewable Energy",
                    "description": "Consider switching to a renewable energy provider",
                    "potential_savings": 1000,  # Estimated savings
                    "difficulty": "easy"
                })
            
            logger.debug(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []


class UserService:
    """
    Service class for user business logic operations.
    
    This class handles user registration, profile management, onboarding,
    and carbon footprint calculations.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize UserService with database session."""
        self.db = db_session
        self.user_repository = UserRepository(db_session)
        self.footprint_calculator = CarbonFootprintCalculator()
    
    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user with validation and Firebase integration.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created User instance
            
        Raises:
            ValueError: If validation fails or user already exists
            FirebaseAuthError: If Firebase operations fail
        """
        try:
            # Validate Firebase UID if provided
            if user_data.firebase_uid:
                try:
                    firebase_user = FirebaseAuth.get_user_by_uid(user_data.firebase_uid)
                    if not firebase_user:
                        raise ValueError("Invalid Firebase UID")
                    
                    # Ensure email matches Firebase user
                    if firebase_user.email and firebase_user.email.lower() != user_data.email.lower():
                        raise ValueError("Email does not match Firebase user")
                        
                except FirebaseAuthError as e:
                    logger.error(f"Firebase validation failed: {str(e)}")
                    raise ValueError(f"Firebase validation failed: {str(e)}")
            
            # Create user through repository
            user = await self.user_repository.create_user(user_data)
            
            logger.info(f"Successfully registered user: {user.email}")
            return user
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Get user profile with additional computed fields.
        
        Args:
            user_id: User's ID
            
        Returns:
            UserProfile instance if found, None otherwise
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return None
            
            # Parse preferences JSON
            preferences = {}
            if user.preferences:
                try:
                    preferences = json.loads(user.preferences)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in user preferences for user {user_id}")
            
            # Create profile with computed fields
            profile_data = {
                **user.to_dict(),
                "preferences": preferences,
                "footprint_category": self.footprint_calculator.get_footprint_category(
                    user.baseline_footprint or 8000
                ) if user.baseline_footprint else None
            }
            
            return UserProfile(**profile_data)
            
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {str(e)}")
            raise
    
    async def update_user_profile(self, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """
        Update user profile with validation.
        
        Args:
            user_id: User's ID
            update_data: Profile update data
            
        Returns:
            Updated User instance if found, None otherwise
        """
        try:
            # Convert preferences to JSON string if provided
            update_dict = update_data.model_dump(exclude_unset=True)
            if "preferences" in update_dict:
                update_dict["preferences"] = json.dumps(update_dict["preferences"])
            
            user = await self.user_repository.update(user_id, update_dict)
            
            if user:
                logger.info(f"Updated profile for user {user_id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {str(e)}")
            raise
    
    async def complete_user_onboarding(
        self, 
        user_id: int, 
        onboarding_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Complete user onboarding with carbon footprint calculation.
        
        Args:
            user_id: User's ID
            onboarding_data: Onboarding survey responses
            
        Returns:
            Updated User instance if found, None otherwise
        """
        try:
            # Calculate baseline carbon footprint
            baseline_footprint = self.footprint_calculator.calculate_baseline_footprint(onboarding_data)
            
            # Complete onboarding in repository
            user = await self.user_repository.complete_onboarding(user_id, onboarding_data)
            if not user:
                return None
            
            # Update baseline footprint
            user = await self.user_repository.update_baseline_footprint(user_id, baseline_footprint)
            
            logger.info(f"Completed onboarding for user {user_id} with baseline footprint {baseline_footprint}")
            return user
            
        except Exception as e:
            logger.error(f"Error completing onboarding for user {user_id}: {str(e)}")
            raise
    
    async def get_user_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get personalized carbon reduction recommendations for user.
        
        Args:
            user_id: User's ID
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user or not user.preferences:
                return []
            
            # Parse onboarding data
            try:
                onboarding_data = json.loads(user.preferences)
            except json.JSONDecodeError:
                logger.warning(f"Invalid preferences JSON for user {user_id}")
                return []
            
            # Generate recommendations
            recommendations = self.footprint_calculator.get_reduction_recommendations(onboarding_data)
            
            logger.debug(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
            raise
    
    async def authenticate_user(self, firebase_uid: str) -> Optional[User]:
        """
        Authenticate user by Firebase UID and update login info.
        
        Args:
            firebase_uid: Firebase user identifier
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            user = await self.user_repository.get_by_firebase_uid(firebase_uid)
            if not user:
                return None
            
            # Update login information
            await self.user_repository.update_login_info(user.id)
            
            logger.info(f"Authenticated user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error authenticating user with Firebase UID {firebase_uid}: {str(e)}")
            raise
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive user statistics for analytics.
        
        Returns:
            Dictionary containing user statistics and insights
        """
        try:
            # Get basic statistics from repository
            stats = await self.user_repository.get_user_statistics()
            
            # Add computed insights
            stats["insights"] = {
                "growth_trend": "positive" if stats["new_users_30d"] > 0 else "stable",
                "engagement_level": "high" if stats["onboarding_completion_rate"] > 70 else "medium",
                "verification_status": "good" if stats["verification_rate"] > 50 else "needs_improvement"
            }
            
            logger.debug("Retrieved comprehensive user statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise
    
    async def search_users(self, query: str, limit: int = 50) -> List[User]:
        """
        Search users with business logic filtering.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching User instances
        """
        try:
            # Only search active, non-deleted users
            users = await self.user_repository.search_users(
                query=query,
                limit=limit,
                include_inactive=False
            )
            
            logger.debug(f"Found {len(users)} users matching search query")
            return users
            
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            raise
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate user account (soft delete).
        
        Args:
            user_id: User's ID
            
        Returns:
            True if deactivated successfully, False if user not found
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False
            
            # Soft delete using the model's method
            if hasattr(user, 'soft_delete'):
                user.soft_delete()
            else:
                user.is_active = False
            
            await self.db.commit()
            
            logger.info(f"Deactivated user account: {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            raise