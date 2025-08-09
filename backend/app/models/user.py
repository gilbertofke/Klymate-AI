"""
User Models

This module defines the User model and related database structures
for the Klymate AI application.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, SoftDeleteMixin, AuditMixin
from app.utils.password_utils import PasswordUtils


class User(BaseModel, SoftDeleteMixin, AuditMixin):
    """User model for storing user account information."""
    
    __tablename__ = "users"
    
    # Firebase integration
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    name = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    
    # Profile information
    profile_picture_url = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Authentication metadata
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Password reset (for local auth if needed)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
    
    # Local password hash (backup/alternative auth)
    password_hash = Column(String(255), nullable=True)
    
    # Carbon footprint tracking
    baseline_footprint = Column(Numeric(10, 4), nullable=True)  # kg CO2 per year
    current_footprint = Column(Numeric(10, 4), nullable=True)  # kg CO2 per year
    total_co2_saved = Column(Numeric(12, 4), default=0, nullable=False)  # Total CO2 saved
    
    # Gamification
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    eco_score = Column(Integer, default=0, nullable=False)
    
    # Onboarding and preferences
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_data = Column(Text, nullable=True)  # JSON string for survey responses
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    
    def set_password(self, password: str) -> None:
        """
        Set user password with proper hashing.
        
        Args:
            password: Plain text password to hash and store
            
        Raises:
            ValueError: If password doesn't meet security requirements
        """
        # Check password strength
        is_strong, issues = PasswordUtils.is_password_strong(password)
        if not is_strong:
            raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        
        # Hash and store password
        self.password_hash = PasswordUtils.hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        if not self.password_hash:
            return False
        
        return PasswordUtils.verify_password(password, self.password_hash)
    
    def set_password_reset_token(self) -> str:
        """
        Generate and set password reset token.
        
        Returns:
            Generated reset token
        """
        token = PasswordUtils.generate_secure_token(64)
        self.password_reset_token = token
        # Token expires in 1 hour
        self.password_reset_expires_at = datetime.utcnow().replace(
            hour=datetime.utcnow().hour + 1
        )
        return token
    
    def clear_password_reset_token(self) -> None:
        """Clear password reset token after use."""
        self.password_reset_token = None
        self.password_reset_expires_at = None
    
    def is_password_reset_token_valid(self, token: str) -> bool:
        """
        Check if password reset token is valid.
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid and not expired
        """
        if not self.password_reset_token or not self.password_reset_expires_at:
            return False
        
        if self.password_reset_token != token:
            return False
        
        if datetime.utcnow() > self.password_reset_expires_at:
            return False
        
        return True
    
    def update_login_info(self) -> None:
        """Update login information."""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1
    
    def set_onboarding_data(self, survey_data: Dict[str, Any]) -> None:
        """
        Store onboarding survey data.
        
        Args:
            survey_data: Dictionary containing survey responses
        """
        self.onboarding_data = json.dumps(survey_data)
    
    def get_onboarding_data(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve onboarding survey data.
        
        Returns:
            Dictionary containing survey responses or None
        """
        if not self.onboarding_data:
            return None
        try:
            return json.loads(self.onboarding_data)
        except json.JSONDecodeError:
            return None
    
    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Store user preferences.
        
        Args:
            preferences: Dictionary containing user preferences
        """
        self.preferences = json.dumps(preferences)
    
    def get_preferences(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve user preferences.
        
        Returns:
            Dictionary containing preferences or None
        """
        if not self.preferences:
            return None
        try:
            return json.loads(self.preferences)
        except json.JSONDecodeError:
            return None
    
    def calculate_baseline_footprint(self, survey_data: Dict[str, Any]) -> float:
        """
        Calculate baseline carbon footprint from survey data.
        
        Args:
            survey_data: Onboarding survey responses
            
        Returns:
            Baseline carbon footprint in kg CO2 per year
        """
        # Carbon footprint calculation based on survey responses
        footprint = 0.0
        
        # Transport emissions (kg CO2/year)
        transport = survey_data.get('transport', {})
        car_km_per_week = transport.get('car_km_per_week', 0)
        public_transport_hours_per_week = transport.get('public_transport_hours_per_week', 0)
        flights_per_year = transport.get('flights_per_year', 0)
        
        # Car: ~0.2 kg CO2 per km
        footprint += car_km_per_week * 52 * 0.2
        
        # Public transport: ~0.05 kg CO2 per hour
        footprint += public_transport_hours_per_week * 52 * 0.05
        
        # Flights: ~500 kg CO2 per flight (average)
        footprint += flights_per_year * 500
        
        # Diet emissions (kg CO2/year)
        diet = survey_data.get('diet', {})
        diet_type = diet.get('type', 'mixed')
        
        diet_emissions = {
            'vegan': 1500,
            'vegetarian': 2000,
            'pescatarian': 2500,
            'mixed': 3000,
            'meat_heavy': 4000
        }
        footprint += diet_emissions.get(diet_type, 3000)
        
        # Energy emissions (kg CO2/year)
        energy = survey_data.get('energy', {})
        home_size = energy.get('home_size', 'medium')
        energy_source = energy.get('energy_source', 'mixed')
        
        # Base energy consumption by home size
        energy_base = {
            'small': 2000,
            'medium': 3000,
            'large': 4500,
            'very_large': 6000
        }
        
        # Energy source multiplier
        energy_multiplier = {
            'renewable': 0.1,
            'mixed': 1.0,
            'fossil': 1.5
        }
        
        footprint += energy_base.get(home_size, 3000) * energy_multiplier.get(energy_source, 1.0)
        
        # Lifestyle emissions (kg CO2/year)
        lifestyle = survey_data.get('lifestyle', {})
        shopping_frequency = lifestyle.get('shopping_frequency', 'moderate')
        
        shopping_emissions = {
            'minimal': 500,
            'moderate': 1000,
            'frequent': 2000,
            'excessive': 3000
        }
        footprint += shopping_emissions.get(shopping_frequency, 1000)
        
        return round(footprint, 2)
    
    def complete_onboarding(self, survey_data: Dict[str, Any]) -> None:
        """
        Complete user onboarding with survey data.
        
        Args:
            survey_data: Dictionary containing survey responses
        """
        self.set_onboarding_data(survey_data)
        self.baseline_footprint = self.calculate_baseline_footprint(survey_data)
        self.current_footprint = self.baseline_footprint
        self.onboarding_completed = True
    
    def update_streak(self, increment: bool = True) -> None:
        """
        Update user's habit streak.
        
        Args:
            increment: Whether to increment or reset the streak
        """
        if increment:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0
    
    def add_co2_savings(self, co2_saved: float) -> None:
        """
        Add CO2 savings to user's total.
        
        Args:
            co2_saved: Amount of CO2 saved in kg
        """
        self.total_co2_saved += co2_saved
        # Update current footprint (reduce from baseline)
        if self.baseline_footprint:
            self.current_footprint = max(0, self.baseline_footprint - self.total_co2_saved)
    
    def calculate_eco_score(self) -> int:
        """
        Calculate user's eco score based on activities.
        
        Returns:
            Calculated eco score
        """
        score = 0
        
        # Base score from CO2 savings (1 point per kg CO2 saved)
        score += int(self.total_co2_saved)
        
        # Streak bonus (10 points per day in current streak)
        score += self.current_streak * 10
        
        # Footprint reduction bonus
        if self.baseline_footprint and self.current_footprint:
            reduction_percentage = ((self.baseline_footprint - self.current_footprint) / self.baseline_footprint) * 100
            score += int(reduction_percentage * 10)  # 10 points per 1% reduction
        
        self.eco_score = max(0, score)
        return self.eco_score
    
    def get_carbon_stats(self) -> Dict[str, Any]:
        """
        Get user's carbon footprint statistics.
        
        Returns:
            Dictionary containing carbon statistics
        """
        stats = {
            'baseline_footprint': float(self.baseline_footprint) if self.baseline_footprint else None,
            'current_footprint': float(self.current_footprint) if self.current_footprint else None,
            'total_co2_saved': float(self.total_co2_saved),
            'reduction_percentage': None,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'eco_score': self.eco_score
        }
        
        if self.baseline_footprint and self.baseline_footprint > 0:
            stats['reduction_percentage'] = round(
                ((self.baseline_footprint - (self.current_footprint or self.baseline_footprint)) / self.baseline_footprint) * 100, 2
            )
        
        return stats
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, firebase_uid={self.firebase_uid})>"
