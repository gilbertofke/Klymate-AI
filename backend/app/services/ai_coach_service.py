"""
AI Coach Service

This module provides the AI coaching service that orchestrates conversations,
generates personalized suggestions, and provides carbon footprint insights.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.utils.ai_utilities import (
    LangChainManager, 
    AIConversationManager,
    OpenAIEmbeddingGenerator
)
from app.repositories.user_repository import UserRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.ai_conversation_repository import AIConversationRepository
from app.schemas.ai_conversation import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class AICoachService:
    """
    Service for AI coaching functionality including conversations,
    personalized suggestions, and carbon footprint insights.
    """
    
    def __init__(self, db_session):
        """
        Initialize AI coach service with database session.
        
        Args:
            db_session: Database session for data access
        """
        self.db = db_session
        
        # Initialize repositories
        self.user_repository = UserRepository(db_session)
        self.habit_repository = HabitRepository(db_session)
        self.ai_conversation_repository = AIConversationRepository(db_session)
        
        # Initialize AI utilities
        self.langchain_manager = LangChainManager()
        self.conversation_manager = AIConversationManager(db_session)
        self.embedding_generator = OpenAIEmbeddingGenerator()
        
        logger.info("AI Coach Service initialized")
    
    async def process_chat_message(
        self,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        include_history: bool = True
    ) -> ChatResponse:
        """
        Process a chat message from user and generate AI response.
        
        Args:
            user_id: User's ID
            message: User's message
            session_id: Optional session identifier
            include_history: Whether to include conversation history
            
        Returns:
            ChatResponse with AI-generated response
        """
        try:
            start_time = datetime.utcnow()
            
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Get user context for personalized coaching
            user_context = await self._get_user_context(user_id)
            
            # Get conversation history if requested
            conversation_history = []
            if include_history:
                conversation_history = await self._get_recent_conversation_history(
                    user_id, session_id
                )
            
            # Process message through LangChain
            ai_response = await self.langchain_manager.process_conversation(
                user_message=message,
                user_context=user_context,
                conversation_history=conversation_history
            )
            
            # Store conversation with embeddings
            await self.conversation_manager.store_conversation(
                user_id=user_id,
                user_message=message,
                ai_response=ai_response,
                context_metadata={
                    "session_id": session_id,
                    "user_context": user_context,
                    "processing_timestamp": start_time.isoformat()
                }
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create response
            response = ChatResponse(
                response=ai_response,
                session_id=session_id,
                conversation_id=0,  # Will be set after storage
                model_used="gpt-3.5-turbo",
                processing_time_ms=int(processing_time),
                context_used=user_context
            )
            
            logger.info(f"Processed chat message for user {user_id} in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            # Return fallback response
            return ChatResponse(
                response="I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
                session_id=session_id or str(uuid.uuid4()),
                conversation_id=0,
                model_used="fallback",
                processing_time_ms=0,
                context_used={}
            )
    
    async def generate_personalized_suggestions(
        self,
        user_id: int,
        focus_area: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized carbon reduction suggestions based on user habits.
        
        Args:
            user_id: User's ID
            focus_area: Optional focus area (transport, energy, diet, etc.)
            limit: Maximum number of suggestions
            
        Returns:
            List of personalized suggestions
        """
        try:
            # Get user context and habits
            user_context = await self._get_user_context(user_id)
            user_habits = await self.habit_repository.get_user_habits_summary(user_id)
            
            # Analyze user's carbon footprint patterns
            footprint_analysis = await self._analyze_user_footprint(user_id)
            
            # Generate suggestions using AI
            suggestions_prompt = self._create_suggestions_prompt(
                user_context, user_habits, footprint_analysis, focus_area
            )
            
            ai_suggestions = await self.langchain_manager.process_conversation(
                user_message=suggestions_prompt,
                user_context=user_context
            )
            
            # Parse and structure suggestions
            suggestions = self._parse_ai_suggestions(ai_suggestions, limit)
            
            logger.info(f"Generated {len(suggestions)} personalized suggestions for user {user_id}")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating personalized suggestions: {str(e)}")
            return self._get_fallback_suggestions(focus_area, limit)
    
    async def generate_carbon_insights(
        self,
        user_id: int,
        time_period: int = 30
    ) -> Dict[str, Any]:
        """
        Generate carbon footprint insights using AI analysis.
        
        Args:
            user_id: User's ID
            time_period: Analysis period in days
            
        Returns:
            Dictionary containing carbon footprint insights
        """
        try:
            # Get user data for analysis
            user_context = await self._get_user_context(user_id)
            habit_trends = await self.habit_repository.get_user_habit_trends(
                user_id, days_back=time_period
            )
            
            # Create insights prompt
            insights_prompt = self._create_insights_prompt(
                user_context, habit_trends, time_period
            )
            
            # Generate insights using AI
            ai_insights = await self.langchain_manager.process_conversation(
                user_message=insights_prompt,
                user_context=user_context
            )
            
            # Structure insights response
            insights = {
                "user_id": user_id,
                "analysis_period_days": time_period,
                "generated_at": datetime.utcnow().isoformat(),
                "insights": self._parse_ai_insights(ai_insights),
                "trends": habit_trends,
                "recommendations": await self.generate_personalized_suggestions(user_id, limit=3)
            }
            
            logger.info(f"Generated carbon insights for user {user_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating carbon insights: {str(e)}")
            return {
                "user_id": user_id,
                "error": "Unable to generate insights at this time",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def search_similar_conversations(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar conversations using semantic search.
        
        Args:
            query: Search query
            user_id: Optional user ID to limit search scope
            limit: Maximum number of results
            
        Returns:
            List of similar conversations
        """
        try:
            similar_conversations = await self.conversation_manager.find_similar_conversations(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            # Format results
            results = []
            for conv in similar_conversations:
                results.append({
                    "conversation_id": conv["id"],
                    "content": conv["content"],
                    "similarity_score": conv.get("similarity", 0.0),
                    "timestamp": conv["timestamp"],
                    "message_type": conv["type"]
                })
            
            logger.debug(f"Found {len(results)} similar conversations for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar conversations: {str(e)}")
            return []
    
    async def get_conversation_history(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User's ID
            session_id: Optional session ID filter
            limit: Maximum number of conversations
            
        Returns:
            List of conversation history
        """
        try:
            if session_id:
                conversations = await self.ai_conversation_repository.get_user_conversations(
                    user_id=user_id,
                    limit=limit,
                    session_id=session_id
                )
            else:
                conversations = await self.conversation_manager.get_conversation_history(
                    user_id=user_id,
                    limit=limit
                )
            
            logger.debug(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get user context for personalized coaching."""
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return {"user_id": user_id, "baseline_footprint": "Unknown"}
            
            # Get recent habits for context
            recent_habits = await self.habit_repository.get_user_recent_habits(user_id, days=7)
            
            context = {
                "user_id": user_id,
                "baseline_footprint": user.baseline_footprint or 0,
                "current_streak": user.current_streak or 0,
                "total_co2_saved": user.total_co2_saved or 0,
                "eco_score": user.eco_score or 0,
                "recent_habits": len(recent_habits),
                "goals": ["reduce_carbon_footprint"],  # Default goal
                "location": "Not specified"  # Could be added to user model
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return {"user_id": user_id, "baseline_footprint": "Unknown"}
    
    async def _get_recent_conversation_history(
        self,
        user_id: int,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get recent conversation history for context."""
        try:
            conversations = await self.ai_conversation_repository.get_user_conversations(
                user_id=user_id,
                limit=limit,
                session_id=session_id
            )
            
            history = []
            for conv in conversations:
                history.append({
                    "type": conv.message_type,
                    "content": conv.content
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def _analyze_user_footprint(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's carbon footprint patterns."""
        try:
            # Get habit statistics
            habit_stats = await self.habit_repository.get_user_habit_statistics(user_id)
            
            # Calculate trends and patterns
            analysis = {
                "total_activities": habit_stats.get("total_habits", 0),
                "co2_saved_total": habit_stats.get("total_co2_saved", 0),
                "most_active_category": habit_stats.get("top_category", "transport"),
                "improvement_trend": "stable"  # Could be calculated from trends
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user footprint: {str(e)}")
            return {}
    
    def _create_suggestions_prompt(
        self,
        user_context: Dict[str, Any],
        user_habits: List[Dict[str, Any]],
        footprint_analysis: Dict[str, Any],
        focus_area: Optional[str]
    ) -> str:
        """Create prompt for generating personalized suggestions."""
        
        focus_text = f" focusing on {focus_area}" if focus_area else ""
        
        prompt = f"""Based on this user's profile and habits, generate 5 specific, actionable carbon reduction suggestions{focus_text}:

User Profile:
- Baseline footprint: {user_context.get('baseline_footprint', 'Unknown')} kg CO2/year
- Total CO2 saved so far: {user_context.get('total_co2_saved', 0)} kg
- Current streak: {user_context.get('current_streak', 0)} days
- Recent activities: {user_context.get('recent_habits', 0)} in past week

Activity Analysis:
- Total logged activities: {footprint_analysis.get('total_activities', 0)}
- Most active category: {footprint_analysis.get('most_active_category', 'transport')}

Please provide 5 specific, measurable suggestions with estimated CO2 savings. Format as a numbered list with brief explanations."""
        
        return prompt
    
    def _create_insights_prompt(
        self,
        user_context: Dict[str, Any],
        habit_trends: Dict[str, Any],
        time_period: int
    ) -> str:
        """Create prompt for generating carbon footprint insights."""
        
        prompt = f"""Analyze this user's carbon footprint data from the past {time_period} days and provide insights:

User Profile:
- Baseline footprint: {user_context.get('baseline_footprint', 'Unknown')} kg CO2/year
- Total CO2 saved: {user_context.get('total_co2_saved', 0)} kg
- Current streak: {user_context.get('current_streak', 0)} days

Trends Data:
{habit_trends}

Please provide:
1. Key patterns and trends you observe
2. Areas of strength and improvement
3. Specific recommendations for the next 30 days
4. Estimated impact of suggested changes

Keep the analysis encouraging and actionable."""
        
        return prompt
    
    def _parse_ai_suggestions(self, ai_response: str, limit: int) -> List[Dict[str, Any]]:
        """Parse AI-generated suggestions into structured format."""
        try:
            suggestions = []
            lines = ai_response.split('\n')
            
            current_suggestion = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for numbered suggestions
                if line[0].isdigit() and '.' in line:
                    if current_suggestion:
                        suggestions.append(current_suggestion)
                    
                    current_suggestion = {
                        "title": line.split('.', 1)[1].strip(),
                        "description": "",
                        "category": "general",
                        "estimated_co2_savings": 0,
                        "difficulty": "medium",
                        "timeframe": "1-4 weeks"
                    }
                elif current_suggestion:
                    current_suggestion["description"] += " " + line
            
            # Add the last suggestion
            if current_suggestion:
                suggestions.append(current_suggestion)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error parsing AI suggestions: {str(e)}")
            return self._get_fallback_suggestions(None, limit)
    
    def _parse_ai_insights(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI-generated insights into structured format."""
        try:
            return {
                "summary": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                "full_analysis": ai_response,
                "key_points": self._extract_key_points(ai_response),
                "confidence_score": 0.8  # Could be calculated based on data quality
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI insights: {str(e)}")
            return {
                "summary": "Analysis temporarily unavailable",
                "full_analysis": "",
                "key_points": [],
                "confidence_score": 0.0
            }
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from AI analysis."""
        try:
            # Simple extraction based on numbered lists or bullet points
            key_points = []
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                    key_points.append(line)
            
            return key_points[:5]  # Limit to 5 key points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    def _get_fallback_suggestions(self, focus_area: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Get fallback suggestions when AI generation fails."""
        
        all_suggestions = [
            {
                "title": "Walk or bike for short trips",
                "description": "Replace car trips under 2 miles with walking or cycling",
                "category": "transport",
                "estimated_co2_savings": 2.3,
                "difficulty": "easy",
                "timeframe": "immediate"
            },
            {
                "title": "Adjust thermostat by 2 degrees",
                "description": "Lower heating by 2°F in winter, raise cooling by 2°F in summer",
                "category": "energy",
                "estimated_co2_savings": 1.8,
                "difficulty": "easy",
                "timeframe": "immediate"
            },
            {
                "title": "Reduce meat consumption",
                "description": "Try one meatless day per week to reduce dietary carbon footprint",
                "category": "diet",
                "estimated_co2_savings": 3.2,
                "difficulty": "medium",
                "timeframe": "1-2 weeks"
            },
            {
                "title": "Use LED light bulbs",
                "description": "Replace incandescent bulbs with energy-efficient LEDs",
                "category": "energy",
                "estimated_co2_savings": 0.8,
                "difficulty": "easy",
                "timeframe": "immediate"
            },
            {
                "title": "Reduce food waste",
                "description": "Plan meals and use leftovers to minimize food waste",
                "category": "lifestyle",
                "estimated_co2_savings": 1.5,
                "difficulty": "medium",
                "timeframe": "1-2 weeks"
            }
        ]
        
        # Filter by focus area if specified
        if focus_area:
            filtered_suggestions = [s for s in all_suggestions if s["category"] == focus_area]
            if filtered_suggestions:
                return filtered_suggestions[:limit]
        
        return all_suggestions[:limit]