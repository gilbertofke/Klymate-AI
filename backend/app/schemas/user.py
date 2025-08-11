"""
User Schemas

Pydantic models for user data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from app.utils.password_utils import PasswordUtils


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: Optional[str] = None
    display_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: Optional[str] = Field(None, description="Password for local authentication (optional with Firebase)")
    firebase_uid: Optional[str] = Field(None, description="Firebase UID for Firebase authentication")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength if provided."""
        if v is not None:
            is_strong, issues = PasswordUtils.is_password_strong(v)
            if not is_strong:
                raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        return v
    
    @validator('firebase_uid')
    def validate_firebase_or_password(cls, v, values):
        """Ensure either Firebase UID or password is provided."""
        if not v and not values.get('password'):
            raise ValueError("Either firebase_uid or password must be provided")
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    name: Optional[str] = None
    display_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserPasswordUpdate(BaseModel):
    """Schema for password updates."""
    current_password: Optional[str] = Field(None, description="Current password (required for local auth)")
    new_password: str = Field(..., description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        is_strong, issues = PasswordUtils.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset requests."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate new password strength."""
        is_strong, issues = PasswordUtils.is_password_strong(v)
        if not is_strong:
            raise ValueError(f"Password does not meet security requirements: {', '.join(issues)}")
        return v


class User(UserBase):
    """Schema for user responses."""
    id: int
    firebase_uid: Optional[str] = None
    email_verified: bool
    is_active: bool
    is_verified: bool
    onboarding_completed: bool
    last_login_at: Optional[datetime] = None
    login_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(User):
    """Extended user profile schema."""
    profile_picture_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# Onboarding Survey Schemas
class TransportSurvey(BaseModel):
    """Transport habits survey schema."""
    car_km_per_week: Optional[float] = Field(0, ge=0, description="Kilometers driven per week")
    public_transport_hours_per_week: Optional[float] = Field(0, ge=0, description="Hours of public transport per week")
    flights_per_year: Optional[int] = Field(0, ge=0, description="Number of flights per year")
    bike_km_per_week: Optional[float] = Field(0, ge=0, description="Kilometers biked per week")
    walk_km_per_week: Optional[float] = Field(0, ge=0, description="Kilometers walked per week")


class DietSurvey(BaseModel):
    """Diet habits survey schema."""
    type: str = Field(..., description="Diet type: vegan, vegetarian, pescatarian, mixed, meat_heavy")
    meals_per_week: Optional[int] = Field(21, ge=1, le=35, description="Number of meals per week")
    local_food_percentage: Optional[float] = Field(50, ge=0, le=100, description="Percentage of locally sourced food")
    
    @validator('type')
    def validate_diet_type(cls, v):
        """Validate diet type."""
        valid_types = ['vegan', 'vegetarian', 'pescatarian', 'mixed', 'meat_heavy']
        if v not in valid_types:
            raise ValueError(f"Diet type must be one of: {', '.join(valid_types)}")
        return v


class EnergySurvey(BaseModel):
    """Energy consumption survey schema."""
    home_size: str = Field(..., description="Home size: small, medium, large, very_large")
    energy_source: str = Field(..., description="Energy source: renewable, mixed, fossil")
    heating_type: Optional[str] = Field("mixed", description="Heating type: electric, gas, oil, renewable")
    monthly_kwh: Optional[float] = Field(None, ge=0, description="Monthly energy consumption in kWh")
    
    @validator('home_size')
    def validate_home_size(cls, v):
        """Validate home size."""
        valid_sizes = ['small', 'medium', 'large', 'very_large']
        if v not in valid_sizes:
            raise ValueError(f"Home size must be one of: {', '.join(valid_sizes)}")
        return v
    
    @validator('energy_source')
    def validate_energy_source(cls, v):
        """Validate energy source."""
        valid_sources = ['renewable', 'mixed', 'fossil']
        if v not in valid_sources:
            raise ValueError(f"Energy source must be one of: {', '.join(valid_sources)}")
        return v


class LifestyleSurvey(BaseModel):
    """Lifestyle habits survey schema."""
    shopping_frequency: str = Field(..., description="Shopping frequency: minimal, moderate, frequent, excessive")
    waste_reduction_practices: Optional[List[str]] = Field([], description="List of waste reduction practices")
    recycling_frequency: Optional[str] = Field("sometimes", description="Recycling frequency: never, sometimes, often, always")
    
    @validator('shopping_frequency')
    def validate_shopping_frequency(cls, v):
        """Validate shopping frequency."""
        valid_frequencies = ['minimal', 'moderate', 'frequent', 'excessive']
        if v not in valid_frequencies:
            raise ValueError(f"Shopping frequency must be one of: {', '.join(valid_frequencies)}")
        return v


class OnboardingSurvey(BaseModel):
    """Complete onboarding survey schema."""
    transport: TransportSurvey
    diet: DietSurvey
    energy: EnergySurvey
    lifestyle: LifestyleSurvey
    goals: Optional[List[str]] = Field([], description="User's carbon reduction goals")
    motivation: Optional[str] = Field(None, description="User's motivation for reducing carbon footprint")


class UserOnboarding(BaseModel):
    """Schema for completing user onboarding."""
    survey_data: OnboardingSurvey


# Enhanced User Schemas
class CarbonStats(BaseModel):
    """Carbon footprint statistics schema."""
    baseline_footprint: Optional[float] = Field(None, description="Baseline carbon footprint in kg CO2/year")
    current_footprint: Optional[float] = Field(None, description="Current carbon footprint in kg CO2/year")
    total_co2_saved: float = Field(0, description="Total CO2 saved in kg")
    reduction_percentage: Optional[float] = Field(None, description="Percentage reduction from baseline")
    current_streak: int = Field(0, description="Current habit streak in days")
    longest_streak: int = Field(0, description="Longest habit streak in days")
    eco_score: int = Field(0, description="User's eco score")


class UserProfile(User):
    """Extended user profile schema."""
    profile_picture_url: Optional[str] = None
    baseline_footprint: Optional[float] = None
    current_footprint: Optional[float] = None
    total_co2_saved: float = 0
    current_streak: int = 0
    longest_streak: int = 0
    eco_score: int = 0
    preferences: Optional[Dict[str, Any]] = None
    carbon_stats: Optional[CarbonStats] = None


class UserPublic(BaseModel):
    """Public user information schema (for leaderboards, etc.)."""
    id: int
    display_name: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    profile_picture_url: Optional[str] = None
    eco_score: int = 0
    total_co2_saved: float = 0
    current_streak: int = 0

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics schema."""
    total_users: int
    active_users: int
    completed_onboarding: int
    total_co2_saved: float
    average_eco_score: float
