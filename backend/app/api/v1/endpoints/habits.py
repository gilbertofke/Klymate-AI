"""
Habit API Routes

This module provides the API endpoints for habit tracking functionality.
Aligned with Task 5 foundation and proper async patterns.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.services.habit_service import HabitService
from app.schemas.habit import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitStatistics,
    HabitList,
    HabitCategoryResponse,
    HabitCategoryList
)
from app.core.middleware import get_current_user
from app.models.habit import CategoryType

router = APIRouter()


def get_habit_service(db: AsyncSession = Depends(get_async_db)) -> HabitService:
    """Dependency to get HabitService instance."""
    return HabitService(db)


@router.post("/log", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def log_habit(
    habit_data: HabitCreate,
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """
    Log a new habit entry.
    
    Creates a new habit entry for the authenticated user with automatic
    CO2 savings calculation based on the habit category.
    """
    try:
        habit_entry = await service.log_habit(
            user_id=current_user["user_id"],
            habit_data=habit_data
        )
        return habit_entry
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log habit entry"
        )


@router.get("/history", response_model=HabitList)
async def get_habit_history(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    category_id: Optional[int] = Query(None, description="Filter by habit category ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """
    Get habit history with optional filtering.
    
    Retrieves the user's habit entries with optional date range and category filtering.
    Results are ordered by most recent first.
    """
    try:
        habits = await service.get_user_habit_history(
            user_id=current_user["user_id"],
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            limit=limit
        )
        
        return HabitList(
            habits=habits,
            total_count=len(habits)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve habit history"
        )


@router.get("/recent", response_model=HabitList)
async def get_recent_habits(
    limit: int = Query(10, ge=1, le=50, description="Number of recent habits to retrieve"),
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """
    Get user's most recent habit entries.
    
    Retrieves the user's most recently logged habits for quick access.
    """
    try:
        habits = await service.get_recent_habits(
            user_id=current_user["user_id"],
            limit=limit
        )
        
        return HabitList(
            habits=habits,
            total_count=len(habits)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent habits"
        )


@router.get("/statistics", response_model=HabitStatistics)
async def get_habit_statistics(
    timeframe: str = Query(
        "week", 
        regex="^(day|week|month|year)$",
        description="Time period for statistics"
    ),
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """
    Get habit statistics for the user.
    
    Provides comprehensive statistics including total CO2 savings,
    category breakdown, and personalized insights.
    """
    try:
        stats = await service.get_user_statistics(
            user_id=current_user["user_id"],
            timeframe=timeframe
        )
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve habit statistics"
        )


@router.get("/categories", response_model=HabitCategoryList)
async def get_habit_categories(
    category_type: Optional[str] = Query(
        None,
        regex="^(transport|diet|energy|lifestyle)$",
        description="Filter by category type"
    ),
    service: HabitService = Depends(get_habit_service)
):
    """
    Get available habit categories.
    
    Retrieves all available habit categories that users can log,
    with optional filtering by category type.
    """
    try:
        category_type_enum = None
        if category_type:
            category_type_enum = CategoryType(category_type)
        
        categories = await service.get_habit_categories(category_type_enum)
        
        return HabitCategoryList(
            categories=categories,
            total_count=len(categories)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve habit categories"
        )


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """
    Update a habit entry.
    
    Updates an existing habit entry. Only the habit owner can update their entries.
    """
    try:
        # Get the existing habit to verify ownership
        habit = await service.habit_repository.get_by_id(habit_id)
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit entry not found"
            )
        
        if habit.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this habit entry"
            )
        
        # Update the habit
        update_data = habit_update.model_dump(exclude_unset=True)
        updated_habit = await service.habit_repository.update(habit_id, update_data)
        
        # Recalculate CO2 savings if quantity changed
        if "quantity" in update_data and updated_habit.category:
            updated_habit.update_co2_savings()
            await service.db.commit()
        
        return updated_habit
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update habit entry"
        )


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """
    Delete a habit entry.
    
    Soft deletes a habit entry. Only the habit owner can delete their entries.
    """
    try:
        deleted = await service.delete_habit(habit_id, current_user["user_id"])
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit entry not found or doesn't belong to user"
            )
        
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete habit entry"
        )
