"""
Analytics Schemas

This module defines Pydantic schemas for analytics API requests and responses.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DashboardDataResponse(BaseModel):
    """Response schema for dashboard data."""
    user_id: int
    generated_at: str
    overview: Dict[str, Any]
    trends: Dict[str, Any]
    categories: Dict[str, Any]
    top_category: Dict[str, Any]
    insights: List[str]


class TrendAnalysisResponse(BaseModel):
    """Response schema for trend analysis."""
    daily_trends: List[Dict[str, Any]]
    weekly_trends: List[Dict[str, Any]]
    category_breakdown: Dict[str, float]
    total_period_savings: float
    daily_average: float
    weekly_average: float
    trend_direction: str
    recent_performance: str


class UserComparisonResponse(BaseModel):
    """Response schema for user comparison."""
    user_id: int
    percentile: float
    comparison: Dict[str, Any]
    rank_category: str
    generated_at: str


class CategoryAnalyticsResponse(BaseModel):
    """Response schema for category analytics."""
    categories: Dict[str, Dict[str, Any]]
    top_category: Dict[str, Any]
    recommendations: List[str]


class PlatformStatsResponse(BaseModel):
    """Response schema for platform statistics."""
    platform_stats: Dict[str, Any]
    generated_at: str


class PerformanceMetricsResponse(BaseModel):
    """Response schema for performance metrics."""
    user_id: int
    efficiency_score: float
    consistency_score: float
    impact_score: float
    overall_score: float
    period_days: int
    generated_at: str


class AnalyticsRequest(BaseModel):
    """Base request schema for analytics."""
    user_id: Optional[int] = None
    days_back: int = Field(default=30, ge=1, le=365)
    include_trends: bool = True
    include_comparisons: bool = True


class TrendAnalysisRequest(BaseModel):
    """Request schema for trend analysis."""
    days_back: int = Field(default=30, ge=1, le=365)
    granularity: str = Field(default="daily", pattern="^(daily|weekly|monthly)$")
    categories: Optional[List[str]] = None


class ComparisonRequest(BaseModel):
    """Request schema for user comparison."""
    comparison_type: str = Field(default="platform", pattern="^(platform|peers|category)$")
    time_period: int = Field(default=30, ge=7, le=365)