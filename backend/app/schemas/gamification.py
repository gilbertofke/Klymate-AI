"""
Gamification Schemas

This module defines Pydantic schemas for gamification API operations,
including badges, leaderboards, and user progress.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.models.base import BaseSchema, BaseResponseSchema


class LeaderboardEntry(BaseSchema):
    """Schema for individual leaderboard entry."""
    
    rank: int = Field(..., ge=1, description="User's rank in leaderboard")
    user_id: int = Field(..., description="User's ID")
    display_name: str = Field(..., description="User's display name")
    eco_score: int = Field(..., ge=0, description="User's eco score")
    total_co2_saved: Optional[float] = Field(None, description="Total CO2 saved by user")
    weekly_score: Optional[int] = Field(None, description="Weekly score for weekly leaderboards")
    weekly_co2_saved: Optional[float] = Field(None, description="Weekly CO2 saved")


class LeaderboardResponse(BaseSchema):
    """Schema for leaderboard API responses."""
    
    leaderboard_type: str = Field(..., description="Type of leaderboard (global, weekly, monthly)")
    entries: List[LeaderboardEntry] = Field(..., description="Leaderboard entries")
    total_users: int = Field(..., ge=0, description="Total number of users in leaderboard")
    user_rank: Optional[int] = Field(None, description="Current user's rank")
    generated_at: datetime = Field(..., description="When leaderboard was generated")


class BadgeProgressInfo(BaseSchema):
    """Schema for badge progress information."""
    
    is_earned: bool = Field(..., description="Whether badge has been earned")
    earned_at: Optional[datetime] = Field(None, description="When badge was earned")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    current_value: Optional[float] = Field(None, description="Current progress value")
    target_value: Optional[float] = Field(None, description="Target value to earn badge")


class BadgeInfo(BaseSchema):
    """Schema for badge information with user progress."""
    
    id: int = Field(..., description="Badge ID")
    name: str = Field(..., description="Badge name")
    description: str = Field(..., description="Badge description")
    category: str = Field(..., description="Badge category")
    points_value: int = Field(..., ge=0, description="Points awarded for badge")
    icon_url: Optional[str] = Field(None, description="Badge icon URL")
    difficulty: str = Field(..., description="Badge difficulty (easy, medium, hard)")
    user_progress: Optional[BadgeProgressInfo] = Field(None, description="User's progress on this badge")


class BadgesResponse(BaseSchema):
    """Schema for badges list API response."""
    
    badges: List[BadgeInfo] = Field(..., description="List of badges")
    total_badges: int = Field(..., ge=0, description="Total number of badges")
    user_earned: int = Field(..., ge=0, description="Number of badges earned by user")


class BadgeAwardResponse(BaseSchema):
    """Schema for badge award API response."""
    
    success: bool = Field(..., description="Whether badge was awarded successfully")
    badge_id: int = Field(..., description="Badge ID")
    badge_name: str = Field(..., description="Badge name")
    points_awarded: int = Field(..., ge=0, description="Points awarded")
    message: str = Field(..., description="Success or error message")
    awarded_at: Optional[datetime] = Field(None, description="When badge was awarded")


class NextMilestone(BaseSchema):
    """Schema for next milestone information."""
    
    type: str = Field(..., description="Milestone type (badge, streak, score)")
    name: str = Field(..., description="Milestone name")
    description: str = Field(..., description="Milestone description")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress towards milestone")
    target_value: float = Field(..., description="Target value for milestone")
    current_value: float = Field(..., description="Current progress value")


class RecentBadge(BaseSchema):
    """Schema for recently earned badge."""
    
    badge_id: int = Field(..., description="Badge ID")
    badge_name: str = Field(..., description="Badge name")
    points_awarded: int = Field(..., description="Points awarded")
    earned_at: datetime = Field(..., description="When badge was earned")


class UserProgressResponse(BaseSchema):
    """Schema for user progress API response."""
    
    user_id: int = Field(..., description="User ID")
    eco_score: int = Field(..., ge=0, description="User's current eco score")
    current_streak: int = Field(..., ge=0, description="Current activity streak")
    longest_streak: int = Field(..., ge=0, description="Longest streak achieved")
    total_co2_saved: float = Field(..., ge=0, description="Total CO2 saved")
    badges_earned: int = Field(..., ge=0, description="Number of badges earned")
    badges_in_progress: int = Field(..., ge=0, description="Number of badges in progress")
    recent_badges: List[RecentBadge] = Field(..., description="Recently earned badges")
    next_milestones: List[NextMilestone] = Field(..., description="Upcoming milestones")
    leaderboard_rank: Optional[int] = Field(None, description="User's rank in global leaderboard")


class StreakMilestone(BaseSchema):
    """Schema for streak milestone information."""
    
    days: int = Field(..., ge=1, description="Days required for milestone")
    reward: str = Field(..., description="Reward for reaching milestone")


class StreakUpdateResponse(BaseSchema):
    """Schema for streak update API response."""
    
    user_id: int = Field(..., description="User ID")
    current_streak: int = Field(..., ge=0, description="Current streak")
    longest_streak: int = Field(..., ge=0, description="Longest streak achieved")
    streak_start_date: Optional[date] = Field(None, description="When current streak started")
    last_activity_date: Optional[date] = Field(None, description="Last activity date")
    streak_increased: bool = Field(..., description="Whether streak increased")
    streak_broken: Optional[bool] = Field(None, description="Whether streak was broken")
    next_milestone: Optional[StreakMilestone] = Field(None, description="Next streak milestone")


class EcoScoreUpdate(BaseSchema):
    """Schema for eco score update information."""
    
    points_gained: int = Field(..., ge=0, description="Points gained from activity")
    new_score: int = Field(..., ge=0, description="New total eco score")
    bonus_points: int = Field(0, ge=0, description="Bonus points (e.g., from streaks)")
    reason: str = Field(..., description="Reason for score update")


class EcoScoreResponse(BaseSchema):
    """Schema for eco score API response."""
    
    user_id: int = Field(..., description="User ID")
    current_score: int = Field(..., ge=0, description="Current eco score")
    score_history: List[EcoScoreUpdate] = Field(..., description="Recent score updates")
    rank: Optional[int] = Field(None, description="User's rank by eco score")
    percentile: Optional[float] = Field(None, ge=0, le=100, description="User's percentile")


class ActivityProcessingResult(BaseSchema):
    """Schema for activity processing result."""
    
    badges_awarded: List[Dict[str, Any]] = Field(..., description="Badges awarded from activity")
    streak_update: Dict[str, Any] = Field(..., description="Streak update information")
    eco_score_update: Dict[str, Any] = Field(..., description="Eco score update information")
    notifications: List[str] = Field(default_factory=list, description="Notifications for user")


class LeaderboardRequest(BaseSchema):
    """Schema for leaderboard request parameters."""
    
    leaderboard_type: str = Field("global", description="Type of leaderboard")
    limit: int = Field(10, ge=1, le=100, description="Number of entries to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class BadgeRecommendation(BaseSchema):
    """Schema for badge recommendation."""
    
    badge_id: int = Field(..., description="Badge ID")
    badge_name: str = Field(..., description="Badge name")
    description: str = Field(..., description="Badge description")
    points_value: int = Field(..., description="Points awarded")
    progress_percentage: float = Field(..., ge=0, le=100, description="Current progress")
    estimated_completion: str = Field(..., description="Estimated time to complete")
    priority_score: float = Field(..., ge=0, description="Recommendation priority score")


class BadgeRecommendationsResponse(BaseSchema):
    """Schema for badge recommendations API response."""
    
    user_id: int = Field(..., description="User ID")
    recommendations: List[BadgeRecommendation] = Field(..., description="Badge recommendations")
    generated_at: datetime = Field(..., description="When recommendations were generated")


class GamificationStatsResponse(BaseSchema):
    """Schema for gamification statistics."""
    
    total_users: int = Field(..., description="Total number of users")
    total_badges_awarded: int = Field(..., description="Total badges awarded")
    average_eco_score: float = Field(..., description="Average eco score")
    top_streak: int = Field(..., description="Longest streak achieved by any user")
    total_co2_saved: float = Field(..., description="Total CO2 saved by all users")
    most_popular_badge: Optional[str] = Field(None, description="Most frequently earned badge")


# Additional schemas for API compatibility
class BadgeResponse(BaseSchema):
    """Schema for single badge response."""
    
    badge: BadgeInfo = Field(..., description="Badge information")
    message: Optional[str] = Field(None, description="Response message")


class UserBadgeResponse(BaseSchema):
    """Schema for user badge response."""
    
    user_badge: BadgeProgressInfo = Field(..., description="User badge progress")
    badge_info: BadgeInfo = Field(..., description="Badge information")
    message: Optional[str] = Field(None, description="Response message")


class BadgeProgressResponse(BaseSchema):
    """Schema for badge progress response."""
    
    badge_id: int = Field(..., description="Badge ID")
    badge_name: str = Field(..., description="Badge name")
    progress: BadgeProgressInfo = Field(..., description="Progress information")
    message: Optional[str] = Field(None, description="Response message")