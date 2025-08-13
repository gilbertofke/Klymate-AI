"""
Analytics Service - Task 9.1 Implementation

This module provides comprehensive analytics functionality including
dashboard data generation, carbon footprint trend analysis, user
comparison and benchmarking, and performance metrics.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from statistics import mean, median
import asyncio

from app.repositories.user_repository import UserRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.badge_repository import UserBadgeRepository
from app.utils.cache import cache_result, CacheInvalidationStrategy

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for analytics and reporting functionality.
    
    This service handles dashboard data generation, trend analysis,
    user comparisons, and performance metrics calculation.
    """
    
    def __init__(self, db_session):
        """
        Initialize analytics service with database session.
        
        Args:
            db_session: Database session for data access
        """
        self.db = db_session
        
        # Initialize repositories
        self.user_repository = UserRepository(db_session)
        self.habit_repository = HabitRepository(db_session)
        self.badge_repository = UserBadgeRepository(db_session)
        
        logger.info("Analytics Service initialized")
    
    @cache_result(ttl=1800, key_prefix="dashboard")  # 30 minutes cache
    async def generate_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary containing dashboard data
            
        Raises:
            ValueError: If user not found
            Exception: For database or processing errors
        """
        try:
            # Get user data
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get habit statistics
            habit_stats = await self.habit_repository.get_user_habit_statistics(user_id)
            
            # Get recent trends (last 30 days)
            trends = await self.get_carbon_footprint_trends(user_id, days_back=30)
            
            # Get category breakdown
            category_analytics = await self.get_category_analytics(user_id)
            
            # Compile dashboard data
            dashboard_data = {
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "overview": {
                    "total_co2_saved": float(user.total_co2_saved or 0),
                    "current_streak": user.current_streak or 0,
                    "eco_score": user.eco_score or 0,
                    "total_habits": habit_stats.get("total_habits", 0),
                    "baseline_footprint": float(user.baseline_footprint or 0)
                },
                "trends": {
                    "daily_average": trends.get("daily_average", 0),
                    "weekly_average": trends.get("weekly_average", 0),
                    "trend_direction": trends.get("trend_direction", "stable"),
                    "recent_performance": trends.get("recent_performance", "stable")
                },
                "categories": category_analytics.get("categories", {}),
                "top_category": category_analytics.get("top_category", {}),
                "insights": self._generate_dashboard_insights(user, habit_stats, trends)
            }
            
            logger.info(f"Generated dashboard data for user {user_id}")
            return dashboard_data
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error generating dashboard data for user {user_id}: {str(e)}")
            raise
    
    @cache_result(ttl=3600, key_prefix="trends")  # 1 hour cache
    async def get_carbon_footprint_trends(
        self,
        user_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze carbon footprint trends for a user.
        
        Args:
            user_id: User's ID
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            # Get habit data for the period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            habits = await self.habit_repository.get_user_habits_by_date_range(
                user_id, start_date, end_date
            )
            
            if not habits:
                return {
                    "daily_trends": [],
                    "weekly_trends": [],
                    "category_breakdown": {},
                    "total_period_savings": 0,
                    "daily_average": 0,
                    "weekly_average": 0,
                    "trend_direction": "stable",
                    "recent_performance": "stable"
                }
            
            # Process daily trends
            daily_trends = self._calculate_daily_trends(habits, start_date, end_date)
            
            # Process weekly trends
            weekly_trends = self._calculate_weekly_trends(daily_trends)
            
            # Calculate category breakdown
            category_breakdown = self._calculate_category_breakdown(habits)
            
            # Calculate totals and averages
            total_savings = sum(habit.get("co2_saved", 0) for habit in habits)
            daily_average = total_savings / days_back if days_back > 0 else 0
            weekly_average = daily_average * 7
            
            # Determine trend direction
            daily_values = [day["co2_saved"] for day in daily_trends]
            trend_direction = self._calculate_trend_direction(daily_values)
            
            # Assess recent performance (last 7 days vs previous 7 days)
            recent_performance = self._assess_recent_performance(daily_trends)
            
            result = {
                "daily_trends": daily_trends,
                "weekly_trends": weekly_trends,
                "category_breakdown": category_breakdown,
                "total_period_savings": round(total_savings, 2),
                "daily_average": round(daily_average, 2),
                "weekly_average": round(weekly_average, 2),
                "trend_direction": trend_direction,
                "recent_performance": recent_performance
            }
            
            logger.debug(f"Calculated trends for user {user_id}: {days_back} days")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating trends for user {user_id}: {str(e)}")
            raise
    
    @cache_result(ttl=7200, key_prefix="comparison")  # 2 hours cache
    async def get_user_comparison(self, user_id: int) -> Dict[str, Any]:
        """
        Generate user comparison and benchmarking data.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary containing comparison data
        """
        try:
            # Get user data
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get user percentile ranking
            percentile = await self.user_repository.get_user_percentile(user_id)
            
            # Get platform averages
            averages = await self.user_repository.get_average_metrics()
            
            # Calculate comparisons
            comparison_data = {
                "co2_saved": self._compare_metric(
                    user.total_co2_saved or 0,
                    averages.get("avg_co2_saved", 0),
                    "CO2 Saved"
                ),
                "streak": self._compare_metric(
                    user.current_streak or 0,
                    averages.get("avg_streak", 0),
                    "Current Streak"
                ),
                "eco_score": self._compare_metric(
                    user.eco_score or 0,
                    averages.get("avg_eco_score", 0),
                    "Eco Score"
                )
            }
            
            result = {
                "user_id": user_id,
                "percentile": round(percentile, 1) if percentile else 50.0,
                "comparison": comparison_data,
                "rank_category": self._get_rank_category(percentile),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.debug(f"Generated comparison data for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating user comparison for user {user_id}: {str(e)}")
            raise   
 
    async def get_category_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Generate category-specific analytics for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary containing category analytics
        """
        try:
            # Get category statistics
            category_stats = await self.habit_repository.get_category_statistics(user_id)
            
            if not category_stats:
                return {
                    "categories": {},
                    "top_category": {},
                    "recommendations": []
                }
            
            # Find top performing category
            top_category = max(
                category_stats.items(),
                key=lambda x: x[1].get("co2_saved", 0)
            )
            
            # Generate category recommendations
            recommendations = self._generate_category_recommendations(category_stats)
            
            result = {
                "categories": category_stats,
                "top_category": {
                    "name": top_category[0],
                    "co2_saved": top_category[1].get("co2_saved", 0),
                    "count": top_category[1].get("count", 0),
                    "avg_impact": top_category[1].get("avg_impact", 0)
                },
                "recommendations": recommendations
            }
            
            logger.debug(f"Generated category analytics for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating category analytics for user {user_id}: {str(e)}")
            raise
    
    @cache_result(ttl=7200, key_prefix="platform_stats")  # 2 hours cache
    async def get_aggregated_data(self) -> Dict[str, Any]:
        """
        Get platform-wide aggregated data with proper indexing.
        
        Returns:
            Dictionary containing aggregated platform statistics
        """
        try:
            # Get platform statistics
            total_users = await self.user_repository.get_total_users()
            total_habits = await self.habit_repository.get_total_habits()
            total_co2_saved = await self.habit_repository.get_total_co2_saved()
            
            # Get additional metrics
            active_users_30d = await self.user_repository.get_active_users_count(days=30)
            avg_habits_per_user = total_habits / total_users if total_users > 0 else 0
            
            result = {
                "platform_stats": {
                    "total_users": total_users,
                    "total_habits": total_habits,
                    "total_co2_saved": round(total_co2_saved, 2),
                    "active_users_30d": active_users_30d,
                    "avg_habits_per_user": round(avg_habits_per_user, 2)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Generated aggregated platform data")
            return result
            
        except Exception as e:
            logger.error(f"Error generating aggregated data: {str(e)}")
            raise
    
    async def get_performance_metrics(
        self,
        user_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate performance metrics for a user.
        
        Args:
            user_id: User's ID
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # Get habit statistics
            habit_stats = await self.habit_repository.get_user_habit_statistics(user_id)
            
            # Calculate efficiency score (CO2 saved per habit)
            total_habits = habit_stats.get("total_habits", 0)
            total_co2_saved = habit_stats.get("total_co2_saved", 0)
            efficiency_score = total_co2_saved / total_habits if total_habits > 0 else 0
            
            # Get consistency score
            consistency_score = habit_stats.get("consistency_score", 0)
            
            # Calculate impact score (normalized CO2 savings)
            impact_score = min(1.0, total_co2_saved / 1000.0)  # Normalize to 1000kg
            
            result = {
                "user_id": user_id,
                "efficiency_score": round(efficiency_score, 2),
                "consistency_score": round(consistency_score, 2),
                "impact_score": round(impact_score, 2),
                "overall_score": round((efficiency_score + consistency_score + impact_score) / 3, 2),
                "period_days": days_back,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.debug(f"Calculated performance metrics for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics for user {user_id}: {str(e)}")
            raise    

    def _calculate_daily_trends(
        self,
        habits: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Calculate daily CO2 savings trends."""
        try:
            daily_data = {}
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            # Initialize all dates with zero
            while current_date <= end_date_only:
                daily_data[current_date.isoformat()] = 0.0
                current_date += timedelta(days=1)
            
            # Aggregate habits by date
            for habit in habits:
                habit_date = habit.get("logged_at")
                if habit_date:
                    date_key = habit_date.date().isoformat()
                    if date_key in daily_data:
                        daily_data[date_key] += habit.get("co2_saved", 0)
            
            # Convert to list format
            daily_trends = []
            for date_str, co2_saved in sorted(daily_data.items()):
                daily_trends.append({
                    "date": date_str,
                    "co2_saved": round(co2_saved, 2)
                })
            
            return daily_trends
            
        except Exception as e:
            logger.error(f"Error calculating daily trends: {str(e)}")
            return []
    
    def _calculate_weekly_trends(self, daily_trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate weekly aggregated trends from daily data."""
        try:
            if not daily_trends:
                return []
            
            weekly_data = {}
            
            for day in daily_trends:
                date_obj = datetime.fromisoformat(day["date"]).date()
                # Get Monday of the week (ISO week)
                week_start = date_obj - timedelta(days=date_obj.weekday())
                week_key = week_start.isoformat()
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = {"total": 0.0, "days": 0}
                
                weekly_data[week_key]["total"] += day["co2_saved"]
                weekly_data[week_key]["days"] += 1
            
            # Convert to list format
            weekly_trends = []
            for week_start, data in sorted(weekly_data.items()):
                weekly_trends.append({
                    "week_start": week_start,
                    "total_co2_saved": round(data["total"], 2),
                    "average_daily": round(data["total"] / data["days"], 2) if data["days"] > 0 else 0,
                    "active_days": data["days"]
                })
            
            return weekly_trends
            
        except Exception as e:
            logger.error(f"Error calculating weekly trends: {str(e)}")
            return []
    
    def _calculate_category_breakdown(self, habits: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate CO2 savings breakdown by category."""
        try:
            category_totals = {}
            
            for habit in habits:
                category = habit.get("category", "other")
                co2_saved = habit.get("co2_saved", 0)
                
                if category not in category_totals:
                    category_totals[category] = 0.0
                
                category_totals[category] += co2_saved
            
            # Convert to percentages
            total_savings = sum(category_totals.values())
            if total_savings > 0:
                category_percentages = {
                    category: round((amount / total_savings) * 100, 1)
                    for category, amount in category_totals.items()
                }
            else:
                category_percentages = {}
            
            return category_percentages
            
        except Exception as e:
            logger.error(f"Error calculating category breakdown: {str(e)}")
            return {}   
 
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """
        Calculate trend direction from a series of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        try:
            if len(values) < 2:
                return "stable"
            
            # Calculate linear regression slope
            n = len(values)
            x_values = list(range(n))
            
            # Calculate slope using least squares
            x_mean = mean(x_values)
            y_mean = mean(values)
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            if denominator == 0:
                return "stable"
            
            slope = numerator / denominator
            
            # Determine trend based on slope
            if slope > 0.1:  # Threshold for significant increase
                return "increasing"
            elif slope < -0.1:  # Threshold for significant decrease
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating trend direction: {str(e)}")
            return "stable"
    
    def _assess_recent_performance(self, daily_trends: List[Dict[str, Any]]) -> str:
        """Assess recent performance compared to previous period."""
        try:
            if len(daily_trends) < 14:  # Need at least 14 days
                return "stable"
            
            # Get last 7 days and previous 7 days
            recent_7_days = daily_trends[-7:]
            previous_7_days = daily_trends[-14:-7]
            
            recent_avg = mean([day["co2_saved"] for day in recent_7_days])
            previous_avg = mean([day["co2_saved"] for day in previous_7_days])
            
            if previous_avg == 0:
                return "stable"
            
            change_percent = ((recent_avg - previous_avg) / previous_avg) * 100
            
            if change_percent > 10:
                return "improving"
            elif change_percent < -10:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error assessing recent performance: {str(e)}")
            return "stable"
    
    def _compare_metric(
        self,
        user_value: float,
        average_value: float,
        metric_name: str
    ) -> Dict[str, Any]:
        """Compare user metric to platform average."""
        try:
            if average_value == 0:
                performance = "average"
                difference_percent = 0
            else:
                difference_percent = ((user_value - average_value) / average_value) * 100
                
                if difference_percent > 20:
                    performance = "excellent"
                elif difference_percent > 0:
                    performance = "above_average"
                elif difference_percent > -20:
                    performance = "average"
                else:
                    performance = "below_average"
            
            return {
                "metric_name": metric_name,
                "user_value": round(user_value, 2),
                "average_value": round(average_value, 2),
                "difference_percent": round(difference_percent, 1),
                "performance": performance
            }
            
        except Exception as e:
            logger.error(f"Error comparing metric {metric_name}: {str(e)}")
            return {
                "metric_name": metric_name,
                "user_value": user_value,
                "average_value": average_value,
                "difference_percent": 0,
                "performance": "average"
            }
    
    def _get_rank_category(self, percentile: Optional[float]) -> str:
        """Get rank category based on percentile."""
        if not percentile:
            return "average"
        
        if percentile >= 90:
            return "top_performer"
        elif percentile >= 75:
            return "high_performer"
        elif percentile >= 50:
            return "above_average"
        elif percentile >= 25:
            return "average"
        else:
            return "needs_improvement"
    
    def _generate_category_recommendations(
        self,
        category_stats: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on category performance."""
        try:
            recommendations = []
            
            if not category_stats:
                return ["Start logging habits to get personalized recommendations"]
            
            # Find underperforming categories
            total_co2 = sum(stats.get("co2_saved", 0) for stats in category_stats.values())
            
            for category, stats in category_stats.items():
                co2_saved = stats.get("co2_saved", 0)
                count = stats.get("count", 0)
                
                # Low activity in important categories
                if category == "transport" and count < 5:
                    recommendations.append("Consider logging more transportation habits for bigger impact")
                elif category == "energy" and co2_saved < total_co2 * 0.2:
                    recommendations.append("Focus on energy-saving habits for consistent daily impact")
                elif category == "diet" and count == 0:
                    recommendations.append("Try logging dietary changes - they can have significant impact")
            
            # If no specific recommendations, provide general ones
            if not recommendations:
                top_category = max(category_stats.items(), key=lambda x: x[1].get("co2_saved", 0))
                recommendations.append(f"Great work with {top_category[0]} habits! Consider expanding to other categories")
            
            return recommendations[:3]  # Limit to 3 recommendations
            
        except Exception as e:
            logger.error(f"Error generating category recommendations: {str(e)}")
            return ["Keep up the great work with your carbon reduction efforts!"]
    
    def _generate_dashboard_insights(
        self,
        user: Any,
        habit_stats: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate insights for dashboard display."""
        try:
            insights = []
            
            # Streak insights
            streak = user.current_streak or 0
            if streak >= 30:
                insights.append(f"Amazing! You've maintained a {streak}-day streak!")
            elif streak >= 7:
                insights.append(f"Great consistency with your {streak}-day streak!")
            elif streak == 0:
                insights.append("Start a new streak by logging a habit today!")
            
            # CO2 savings insights
            total_saved = user.total_co2_saved or 0
            if total_saved >= 100:
                insights.append(f"You've saved {total_saved:.1f}kg of CO2 - equivalent to planting {int(total_saved/22)} trees!")
            elif total_saved >= 10:
                insights.append(f"You've saved {total_saved:.1f}kg of CO2 - keep up the great work!")
            
            # Trend insights
            trend_direction = trends.get("trend_direction", "stable")
            if trend_direction == "increasing":
                insights.append("Your carbon savings are trending upward - excellent progress!")
            elif trend_direction == "decreasing":
                insights.append("Your recent activity has decreased - try to get back on track!")
            
            return insights[:3]  # Limit to 3 insights
            
        except Exception as e:
            logger.error(f"Error generating dashboard insights: {str(e)}")
            return ["Keep making a positive impact on the environment!"]
    
    def _generate_insights(self, trend_data: Dict[str, Any]) -> List[str]:
        """Generate insights from trend data."""
        try:
            insights = []
            
            # Category insights
            category_breakdown = trend_data.get("category_breakdown", {})
            if category_breakdown:
                top_category = max(category_breakdown.items(), key=lambda x: x[1])
                insights.append(f"Your strongest category is {top_category[0]} with {top_category[1]}% of your impact")
            
            # Daily trends insights
            daily_trends = trend_data.get("daily_trends", [])
            if daily_trends:
                recent_days = daily_trends[-7:]  # Last 7 days
                avg_recent = mean([day["co2_saved"] for day in recent_days])
                if avg_recent > 2:
                    insights.append("You're averaging over 2kg CO2 saved per day - fantastic!")
                elif avg_recent > 1:
                    insights.append("Good daily impact with over 1kg CO2 saved per day on average")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    def _validate_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        """
        Validate that date range is logical.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return start_date <= end_date
        except Exception:
            return False