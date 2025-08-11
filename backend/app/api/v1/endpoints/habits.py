"""
Habit API Routes

This module provides the API endpoints for habit tracking functionality.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_async_db
from app.repositories.habit_repository import HabitRepository
from app.services.habit_service import HabitService
from app.schemas.habit import (
    HabitCreate,
    HabitResponse,
    HabitStatistics,
    HabitList
)
from app.core.auth import get_current_user

router = APIRouter()

async def get_habit_service(db: Session = Depends(get_async_db)) -> HabitService:
    """Dependency to get HabitService instance."""
    repository = HabitRepository(db)
    return HabitService(repository)

@router.post("/habits", response_model=HabitResponse)
async def log_habit(
    habit: HabitCreate,
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """Log a new habit entry."""
    try:
        habit_entry = await service.log_habit(
            user_id=current_user.id,
            habit_data=habit.dict()
        )
        return habit_entry
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to log habit: {str(e)}"
        )

@router.get("/habits", response_model=HabitList)
async def get_habits(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    category_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """Get habit history with optional filtering."""
    habits = await service.get_user_habit_history(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )
    return {"habits": habits}

@router.get("/habits/statistics", response_model=HabitStatistics)
async def get_statistics(
    timeframe: str = Query("week", enum=["day", "week", "month", "year"]),
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """Get habit statistics for the user."""
    stats = await service.get_user_statistics(
        user_id=current_user.id,
        timeframe=timeframe
    )
    return stats

@router.delete("/habits/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user = Depends(get_current_user),
    service: HabitService = Depends(get_habit_service)
):
    """Delete a habit entry."""
    deleted = await service.delete_habit(habit_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Habit entry not found or doesn't belong to user"
        )
    return {"message": "Habit entry deleted successfully"}
