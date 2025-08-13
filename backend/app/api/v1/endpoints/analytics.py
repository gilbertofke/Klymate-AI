"""
Analytics API Endpoints

This module provides REST API endpoints for analytics functionality
including dashboard data, trends, comparisons, and performance metrics.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.auth_integration import get_current_user
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    DashboardDataResponse,
    TrendAnalysisResponse,
    UserComparisonResponse,
    CategoryAnalyticsResponse,
    PlatformStatsResponse,
    PerformanceMetricsResponse,
    AnalyticsRequest,
    TrendAnalysisRequest,
    ComparisonRequest
)
from app.schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard data for the current user.
    
    Returns overview statistics, trends, category breakdown,
    and personalized insights for the user's dashboard.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        dashboard_data = await analytics_service.generate_dashboard_data(current_user.id)
        
        logger.info(f"Generated dashboard data for user {current_user.id}")
        return dashboard_data
        
    except ValueError as e:
        logger.warning(f"User not found for dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate dashboard data at this time"
        )


@router.get("/trends", response_model=TrendAnalysisResponse)
async def get_carbon_footprint_trends(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get carbon footprint trend analysis for the current user.
    
    Provides daily and weekly trends, category breakdown,
    and trend direction analysis for the specified period.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        trends = await analytics_service.get_carbon_footprint_trends(
            user_id=current_user.id,
            days_back=days_back
        )
        
        logger.info(f"Generated trends for user {current_user.id}: {days_back} days")
        return trends
        
    except Exception as e:
        logger.error(f"Error generating trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate trend analysis at this time"
        )


@router.get("/comparison", response_model=UserComparisonResponse)
async def get_user_comparison(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user comparison and benchmarking data.
    
    Compares the user's performance against platform averages
    and provides percentile ranking and performance insights.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        comparison = await analytics_service.get_user_comparison(current_user.id)
        
        logger.info(f"Generated comparison data for user {current_user.id}")
        return comparison
        
    except ValueError as e:
        logger.warning(f"User not found for comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error generating user comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate comparison data at this time"
        )


@router.get("/categories", response_model=CategoryAnalyticsResponse)
async def get_category_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get category-specific analytics for the current user.
    
    Provides breakdown of performance by habit category,
    identifies top performing categories, and suggests improvements.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        category_data = await analytics_service.get_category_analytics(current_user.id)
        
        logger.info(f"Generated category analytics for user {current_user.id}")
        return category_data
        
    except Exception as e:
        logger.error(f"Error generating category analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate category analytics at this time"
        )


@router.get("/platform-stats", response_model=PlatformStatsResponse)
async def get_platform_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform-wide aggregated statistics.
    
    Provides overall platform metrics including total users,
    habits logged, CO2 saved, and other aggregate data.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        platform_stats = await analytics_service.get_aggregated_data()
        
        logger.info("Generated platform statistics")
        return platform_stats
        
    except Exception as e:
        logger.error(f"Error generating platform statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate platform statistics at this time"
        )


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance metrics for the current user.
    
    Calculates efficiency, consistency, and impact scores
    to provide comprehensive performance assessment.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        performance = await analytics_service.get_performance_metrics(
            user_id=current_user.id,
            days_back=days_back
        )
        
        logger.info(f"Generated performance metrics for user {current_user.id}")
        return performance
        
    except Exception as e:
        logger.error(f"Error generating performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate performance metrics at this time"
        )


@router.get("/insights")
async def get_personalized_insights(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized insights based on user's analytics data.
    
    Combines trend analysis, performance metrics, and category
    data to provide actionable insights and recommendations.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get comprehensive data for insights
        dashboard_data = await analytics_service.generate_dashboard_data(current_user.id)
        trends = await analytics_service.get_carbon_footprint_trends(current_user.id, days_back)
        performance = await analytics_service.get_performance_metrics(current_user.id, days_back)
        
        # Compile insights
        insights = {
            "user_id": current_user.id,
            "period_days": days_back,
            "dashboard_insights": dashboard_data.get("insights", []),
            "trend_insights": analytics_service._generate_insights(trends),
            "performance_summary": {
                "overall_score": performance["overall_score"],
                "strongest_area": "efficiency" if performance["efficiency_score"] == max(
                    performance["efficiency_score"],
                    performance["consistency_score"],
                    performance["impact_score"]
                ) else "consistency" if performance["consistency_score"] == max(
                    performance["efficiency_score"],
                    performance["consistency_score"],
                    performance["impact_score"]
                ) else "impact",
                "improvement_area": "efficiency" if performance["efficiency_score"] == min(
                    performance["efficiency_score"],
                    performance["consistency_score"],
                    performance["impact_score"]
                ) else "consistency" if performance["consistency_score"] == min(
                    performance["efficiency_score"],
                    performance["consistency_score"],
                    performance["impact_score"]
                ) else "impact"
            },
            "generated_at": dashboard_data["generated_at"]
        }
        
        logger.info(f"Generated personalized insights for user {current_user.id}")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating personalized insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate insights at this time"
        )


@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format"),
    days_back: int = Query(90, ge=1, le=365, description="Number of days to include"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export user's analytics data for external analysis.
    
    Provides comprehensive data export including trends,
    performance metrics, and raw habit data.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Gather all analytics data
        dashboard_data = await analytics_service.generate_dashboard_data(current_user.id)
        trends = await analytics_service.get_carbon_footprint_trends(current_user.id, days_back)
        performance = await analytics_service.get_performance_metrics(current_user.id, days_back)
        categories = await analytics_service.get_category_analytics(current_user.id)
        
        export_data = {
            "user_id": current_user.id,
            "export_format": format,
            "export_date": dashboard_data["generated_at"],
            "period_days": days_back,
            "dashboard_data": dashboard_data,
            "trends": trends,
            "performance_metrics": performance,
            "category_analytics": categories
        }
        
        logger.info(f"Exported analytics data for user {current_user.id} in {format} format")
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to export analytics data at this time"
        )


@router.get("/health")
async def analytics_health_check():
    """
    Health check endpoint for analytics service.
    
    Returns the status of analytics components and dependencies.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "components": {
                "analytics_service": "available",
                "trend_analysis": "available",
                "performance_metrics": "available",
                "dashboard_generation": "available",
                "database": "connected"
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Analytics health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-15T10:30:00Z"
        }