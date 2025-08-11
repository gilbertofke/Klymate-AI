"""
User API Endpoints

This module provides API endpoints for user management, onboarding,
and statistics functionality.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.services.user_service import UserService
from app.schemas.user import (
    User, UserCreate, UserUpdate, UserProfile, UserOnboarding,
    OnboardingSurvey, CarbonStats, UserPublic, UserStats
)
from app.utils.auth_integration import get_current_user

router = APIRouter()


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
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Complete user onboarding process.
    
    Processes onboarding survey data and calculates baseline carbon footprint.
    """
    try:
        # Convert Pydantic model to dict
        survey_dict = onboarding_data.survey_data.model_dump()
        
        user = await service.complete_user_onboarding(
            current_user["user_id"], 
            survey_dict
        )
        
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
            detail="Failed to complete onboarding"
        )


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