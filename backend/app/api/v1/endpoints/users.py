"""
User API Endpoints

This module provides API endpoints for user management, onboarding,
and statistics functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core.database import get_async_db
from app.services.user_service import UserService
from app.schemas.user import (
    User, UserCreate, UserUpdate, UserProfile, UserOnboarding,
    OnboardingSurvey, CarbonStats, UserPublic, UserStats
)
from app.utils.auth_integration import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(db)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Register a new user.
    
    Creates a new user account with Firebase integration or local authentication.
    """
    try:
        user = await service.register_user(user_data)
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get current user's profile.
    
    Returns detailed profile information including preferences and carbon stats.
    """
    try:
        profile = await service.get_user_profile(current_user["user_id"])
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/profile", response_model=User)
async def update_user_profile(
    update_data: UserUpdate,
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Update current user's profile.
    
    Updates user profile information including preferences.
    """
    try:
        user = await service.update_user_profile(current_user["user_id"], update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.post("/onboarding", response_model=User)
async def complete_onboarding(
    onboarding_data: UserOnboarding,
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    """
    Complete user onboarding process.
    
    Processes onboarding survey data and calculates baseline carbon footprint.
    
    Returns:
        User: Updated user object with onboarding completed
        
    Raises:
        400: Invalid input data or validation errors
        401: Authentication required
        404: User not found
        409: User already completed onboarding
        422: Validation errors in survey data
        500: Internal server error
    """
    try:
        # Validate that user exists and hasn't already completed onboarding
        existing_user = await service.user_repository.get_by_id(current_user["user_id"])
        if not existing_user:
            logger.warning(f"Onboarding attempt for non-existent user: {current_user['user_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "User not found",
                    "message": "The specified user does not exist in the system",
                    "error_code": "USER_NOT_FOUND",
                    "user_id": current_user["user_id"]
                }
            )
        
        if existing_user.onboarding_completed:
            logger.info(f"User {current_user['user_id']} attempted to complete onboarding again")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Onboarding already completed",
                    "message": "This user has already completed the onboarding process",
                    "error_code": "ONBOARDING_ALREADY_COMPLETED",
                    "user_id": current_user["user_id"],
                    "completed_at": existing_user.updated_at.isoformat() if existing_user.updated_at else None
                }
            )
        
        # Convert Pydantic model to dict with validation
        try:
            survey_dict = onboarding_data.survey_data.model_dump()
            logger.info(f"Processing onboarding for user {current_user['user_id']}")
        except Exception as validation_error:
            logger.error(f"Survey data validation failed for user {current_user['user_id']}: {str(validation_error)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Invalid survey data",
                    "message": "The provided survey data contains validation errors",
                    "error_code": "SURVEY_VALIDATION_ERROR",
                    "validation_errors": str(validation_error),
                    "user_id": current_user["user_id"]
                }
            )
        
        # Validate survey data completeness
        validation_errors = _validate_survey_completeness(survey_dict)
        if validation_errors:
            logger.warning(f"Incomplete survey data for user {current_user['user_id']}: {validation_errors}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Incomplete survey data",
                    "message": "Required survey fields are missing or invalid",
                    "error_code": "INCOMPLETE_SURVEY_DATA",
                    "field_errors": validation_errors,
                    "user_id": current_user["user_id"]
                }
            )
        
        # Complete onboarding with proper error handling
        user = await service.complete_user_onboarding(
            current_user["user_id"], 
            survey_dict
        )
        
        if not user:
            logger.error(f"Onboarding completion failed for user {current_user['user_id']} - service returned None")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Onboarding processing failed",
                    "message": "Failed to process onboarding data due to an internal error",
                    "error_code": "ONBOARDING_PROCESSING_FAILED",
                    "user_id": current_user["user_id"]
                }
            )
        
        logger.info(f"Successfully completed onboarding for user {current_user['user_id']}")
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Value error during onboarding for user {current_user.get('user_id', 'unknown')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid input data",
                "message": str(e),
                "error_code": "INVALID_INPUT_DATA",
                "user_id": current_user.get("user_id")
            }
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Unexpected error during onboarding for user {current_user.get('user_id', 'unknown')}: {str(e)}")
        logger.error(f"Onboarding error traceback: {error_trace}")
        
        # Check if it's a database-related error
        if any(db_error in str(e).lower() for db_error in ['database', 'connection', 'timeout', 'constraint']):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Database service unavailable",
                    "message": "The database service is temporarily unavailable. Please try again later.",
                    "error_code": "DATABASE_SERVICE_UNAVAILABLE",
                    "user_id": current_user.get("user_id"),
                    "retry_after": 30
                }
            )
        
        # Generic server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing your onboarding. Please try again or contact support if the problem persists.",
                "error_code": "INTERNAL_SERVER_ERROR",
                "user_id": current_user.get("user_id"),
                "support_reference": f"onboarding_error_{current_user.get('user_id', 'unknown')}_{hash(str(e)) % 10000}"
            }
        )


def _validate_survey_completeness(survey_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate that survey data contains all required fields.
    
    Args:
        survey_data: The survey data dictionary
        
    Returns:
        Dictionary of field errors, empty if validation passes
    """
    errors = {}
    
    # Validate transport section
    transport = survey_data.get("transport", {})
    transport_errors = []
    
    if not isinstance(transport, dict):
        transport_errors.append("Transport data must be an object")
    else:
        # Check for at least one transport method
        transport_methods = [
            transport.get("car_km_per_week", 0),
            transport.get("public_transport_hours_per_week", 0),
            transport.get("bike_km_per_week", 0),
            transport.get("walk_km_per_week", 0)
        ]
        if all(method == 0 for method in transport_methods):
            transport_errors.append("At least one transport method must be specified")
        
        # Validate numeric values
        for field in ["car_km_per_week", "public_transport_hours_per_week", "bike_km_per_week", "walk_km_per_week"]:
            value = transport.get(field)
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                transport_errors.append(f"{field} must be a non-negative number")
        
        # Validate flights per year
        flights = transport.get("flights_per_year")
        if flights is not None and (not isinstance(flights, int) or flights < 0):
            transport_errors.append("flights_per_year must be a non-negative integer")
    
    if transport_errors:
        errors["transport"] = transport_errors
    
    # Validate diet section
    diet = survey_data.get("diet", {})
    diet_errors = []
    
    if not isinstance(diet, dict):
        diet_errors.append("Diet data must be an object")
    else:
        diet_type = diet.get("type")
        if not diet_type:
            diet_errors.append("Diet type is required")
        elif diet_type not in ["vegan", "vegetarian", "pescatarian", "mixed", "meat_heavy"]:
            diet_errors.append("Diet type must be one of: vegan, vegetarian, pescatarian, mixed, meat_heavy")
        
        # Validate optional numeric fields
        for field in ["meals_per_week", "local_food_percentage"]:
            value = diet.get(field)
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                diet_errors.append(f"{field} must be a non-negative number")
    
    if diet_errors:
        errors["diet"] = diet_errors
    
    # Validate energy section
    energy = survey_data.get("energy", {})
    energy_errors = []
    
    if not isinstance(energy, dict):
        energy_errors.append("Energy data must be an object")
    else:
        home_size = energy.get("home_size")
        if not home_size:
            energy_errors.append("Home size is required")
        elif home_size not in ["small", "medium", "large", "very_large"]:
            energy_errors.append("Home size must be one of: small, medium, large, very_large")
        
        energy_source = energy.get("energy_source")
        if not energy_source:
            energy_errors.append("Energy source is required")
        elif energy_source not in ["renewable", "mixed", "fossil"]:
            energy_errors.append("Energy source must be one of: renewable, mixed, fossil")
        
        # Validate optional numeric fields
        monthly_kwh = energy.get("monthly_kwh")
        if monthly_kwh is not None and (not isinstance(monthly_kwh, (int, float)) or monthly_kwh < 0):
            energy_errors.append("monthly_kwh must be a non-negative number")
    
    if energy_errors:
        errors["energy"] = energy_errors
    
    # Validate lifestyle section
    lifestyle = survey_data.get("lifestyle", {})
    lifestyle_errors = []
    
    if not isinstance(lifestyle, dict):
        lifestyle_errors.append("Lifestyle data must be an object")
    else:
        shopping_freq = lifestyle.get("shopping_frequency")
        if not shopping_freq:
            lifestyle_errors.append("Shopping frequency is required")
        elif shopping_freq not in ["minimal", "moderate", "frequent", "excessive"]:
            lifestyle_errors.append("Shopping frequency must be one of: minimal, moderate, frequent, excessive")
    
    if lifestyle_errors:
        errors["lifestyle"] = lifestyle_errors
    
    return errors


@router.get("/recommendations", response_model=List[Dict[str, Any]])
async def get_user_recommendations(
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get personalized carbon reduction recommendations.
    
    Returns recommendations based on user's onboarding data and current habits.
    """
    try:
        recommendations = await service.get_user_recommendations(current_user["user_id"])
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations"
        )


@router.get("/carbon-stats", response_model=CarbonStats)
async def get_user_carbon_stats(
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get user's carbon footprint statistics.
    
    Returns comprehensive carbon footprint data and reduction metrics.
    """
    try:
        stats = await service.get_user_carbon_insights(current_user["user_id"])
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User carbon stats not found"
            )
        
        return CarbonStats(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve carbon statistics"
        )


@router.get("/engagement-metrics", response_model=Dict[str, Any])
async def get_user_engagement_metrics(
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get user's engagement metrics.
    
    Returns engagement score, activity level, and usage patterns.
    """
    try:
        metrics = await service.get_user_engagement_metrics(current_user["user_id"])
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User engagement metrics not found"
            )
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve engagement metrics"
        )


@router.get("/leaderboard", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100, description="Number of top users to retrieve"),
    service: UserService = Depends(get_user_service)
):
    """
    Get user leaderboard.
    
    Returns top users ranked by eco score and CO2 savings.
    """
    try:
        leaderboard = await service.get_user_leaderboard(limit)
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaderboard"
        )


@router.get("/search", response_model=List[UserPublic])
async def search_users(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results"),
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Search users by name, display name, or email.
    
    Returns public user information for matching users.
    """
    try:
        users = await service.search_users(q, limit)
        
        # Convert to public user format
        public_users = []
        for user in users:
            public_user = UserPublic(
                id=user.id,
                display_name=user.display_name,
                name=user.name,
                location=user.location,
                profile_picture_url=user.profile_picture_url,
                eco_score=user.eco_score,
                total_co2_saved=float(user.total_co2_saved),
                current_streak=user.current_streak
            )
            public_users.append(public_user)
        
        return public_users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


# Admin endpoints (require admin privileges)
@router.get("/admin/statistics", response_model=Dict[str, Any])
async def get_admin_user_statistics(
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get comprehensive user statistics for admin dashboard.
    
    Requires admin privileges. Returns detailed analytics and insights.
    """
    # TODO: Add admin privilege check
    try:
        stats = await service.get_user_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin statistics"
        )


@router.get("/admin/cohort-analysis", response_model=Dict[str, Any])
async def get_cohort_analysis(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get cohort analysis for user retention and engagement.
    
    Requires admin privileges. Returns cohort metrics and trends.
    """
    # TODO: Add admin privilege check
    try:
        analysis = await service.get_cohort_analysis(days_back)
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cohort analysis"
        )


@router.get("/admin/users-needing-onboarding", response_model=List[User])
async def get_users_needing_onboarding(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of users to retrieve"),
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get users who haven't completed onboarding.
    
    Requires admin privileges. Returns users who need onboarding assistance.
    """
    # TODO: Add admin privilege check
    try:
        users = await service.user_repository.get_users_needing_onboarding(limit)
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users needing onboarding"
        )


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Deactivate a user account (soft delete).
    
    Requires admin privileges. Soft deletes the user account.
    """
    # TODO: Add admin privilege check
    try:
        success = await service.deactivate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )