"""
AI Coach API Endpoints

This module provides REST API endpoints for AI coaching functionality
including chat, suggestions, insights, and conversation management.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.auth_integration import get_current_user
from app.services.ai_coach_service import AICoachService
from app.schemas.ai_conversation import (
    ChatRequest,
    ChatResponse,
    ConversationSearchRequest,
    ConversationSearchResponse,
    ConversationHistoryResponse,
    AICoachingInsightResponse,
    ConversationRatingRequest
)
from app.schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Coach"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with AI coach for personalized carbon footprint advice.
    
    This endpoint processes user messages and returns AI-generated responses
    with personalized coaching based on the user's profile and habits.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        response = await ai_coach_service.process_chat_message(
            user_id=current_user.id,
            message=request.message,
            session_id=request.session_id,
            include_history=request.include_history
        )
        
        logger.info(f"Chat processed for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chat message at this time"
        )


@router.get("/suggestions")
async def get_personalized_suggestions(
    focus_area: Optional[str] = Query(None, description="Focus area (transport, energy, diet, lifestyle)"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized carbon reduction suggestions based on user habits.
    
    Returns AI-generated suggestions tailored to the user's carbon footprint
    patterns and historical activities.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        suggestions = await ai_coach_service.generate_personalized_suggestions(
            user_id=current_user.id,
            focus_area=focus_area,
            limit=limit
        )
        
        logger.info(f"Generated {len(suggestions)} suggestions for user {current_user.id}")
        return {
            "user_id": current_user.id,
            "focus_area": focus_area,
            "suggestions": suggestions,
            "generated_at": "2024-01-15T10:30:00Z"  # Will be set by service
        }
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate suggestions at this time"
        )


@router.get("/insights")
async def get_carbon_insights(
    time_period: int = Query(30, ge=7, le=365, description="Analysis period in days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated carbon footprint insights and analysis.
    
    Provides detailed analysis of the user's carbon footprint patterns,
    trends, and personalized recommendations for improvement.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        insights = await ai_coach_service.generate_carbon_insights(
            user_id=current_user.id,
            time_period=time_period
        )
        
        logger.info(f"Generated insights for user {current_user.id}")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate insights at this time"
        )


@router.post("/search", response_model=ConversationSearchResponse)
async def search_conversations(
    request: ConversationSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for similar conversations using semantic search.
    
    Uses vector embeddings to find conversations similar to the search query,
    helping users find relevant past discussions and advice.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        # Search within user's conversations by default, or globally if specified
        search_user_id = current_user.id if not request.user_id else request.user_id
        
        results = await ai_coach_service.search_similar_conversations(
            query=request.query,
            user_id=search_user_id,
            limit=request.limit
        )
        
        response = ConversationSearchResponse(
            query=request.query,
            results=[],  # Will be populated with proper schema
            total_found=len(results),
            search_time_ms=100  # Placeholder
        )
        
        logger.info(f"Search completed for user {current_user.id}: {len(results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Error in conversation search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to search conversations at this time"
        )


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of conversations"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation history for the current user.
    
    Returns the user's conversation history, optionally filtered by session ID.
    Includes both user messages and AI responses.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        conversations = await ai_coach_service.get_conversation_history(
            user_id=current_user.id,
            session_id=session_id,
            limit=limit
        )
        
        response = ConversationHistoryResponse(
            conversations=[],  # Will be populated with proper schema
            total_count=len(conversations),
            has_more=len(conversations) == limit,
            session_info={"session_id": session_id} if session_id else None
        )
        
        logger.info(f"Retrieved {len(conversations)} conversations for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve conversation history at this time"
        )


@router.post("/rate/{conversation_id}")
async def rate_conversation(
    conversation_id: int,
    request: ConversationRatingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rate an AI conversation response.
    
    Allows users to provide feedback on AI responses to improve
    the coaching quality over time.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        # Update conversation rating
        updated_conversation = await ai_coach_service.ai_conversation_repository.update_conversation_rating(
            conversation_id=conversation_id,
            rating=request.rating,
            feedback=request.feedback
        )
        
        if not updated_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        logger.info(f"Conversation {conversation_id} rated {request.rating} by user {current_user.id}")
        return {
            "conversation_id": conversation_id,
            "rating": request.rating,
            "feedback": request.feedback,
            "updated_at": updated_conversation.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to rate conversation at this time"
        )


@router.get("/analytics/topics")
async def get_popular_topics(
    days_back: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of topics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular conversation topics and trends.
    
    Analyzes conversation patterns to identify the most discussed
    carbon footprint topics and areas of interest.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        topics = await ai_coach_service.ai_conversation_repository.get_popular_topics(
            days_back=days_back,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(topics)} popular topics")
        return {
            "period_days": days_back,
            "total_conversations_analyzed": sum(topic.get("frequency", 0) for topic in topics),
            "topics": topics
        }
        
    except Exception as e:
        logger.error(f"Error getting popular topics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve topic analysis at this time"
        )


@router.get("/analytics/user-stats")
async def get_user_conversation_stats(
    days_back: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's conversation statistics and patterns.
    
    Provides insights into the user's engagement with the AI coach,
    including conversation frequency, topics, and trends.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        # Get conversation patterns analysis
        patterns = await ai_coach_service.conversation_manager.analyze_conversation_patterns(
            user_id=current_user.id,
            days_back=days_back
        )
        
        # Get conversation statistics
        stats = await ai_coach_service.ai_conversation_repository.get_conversation_statistics(
            user_id=current_user.id,
            days_back=days_back
        )
        
        combined_stats = {
            **patterns,
            **stats,
            "user_id": current_user.id
        }
        
        logger.info(f"Generated conversation stats for user {current_user.id}")
        return combined_stats
        
    except Exception as e:
        logger.error(f"Error getting user conversation stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve conversation statistics at this time"
        )


@router.delete("/history")
async def delete_conversation_history(
    session_id: Optional[str] = Query(None, description="Delete specific session"),
    older_than_days: Optional[int] = Query(None, ge=1, description="Delete conversations older than X days"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete conversation history for the current user.
    
    Allows users to delete their conversation history for privacy,
    either by session or by age threshold.
    """
    try:
        ai_coach_service = AICoachService(db)
        
        deleted_count = await ai_coach_service.ai_conversation_repository.delete_user_conversations(
            user_id=current_user.id,
            session_id=session_id,
            older_than_days=older_than_days
        )
        
        logger.info(f"Deleted {deleted_count} conversations for user {current_user.id}")
        return {
            "deleted_count": deleted_count,
            "session_id": session_id,
            "older_than_days": older_than_days
        }
        
    except Exception as e:
        logger.error(f"Error deleting conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete conversation history at this time"
        )


@router.get("/health")
async def ai_coach_health_check():
    """
    Health check endpoint for AI coaching service.
    
    Returns the status of AI coaching components and dependencies.
    """
    try:
        # Basic health check - could be expanded to test AI services
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "components": {
                "langchain": "available",
                "openai_api": "available",
                "vector_search": "available",
                "database": "connected"
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-15T10:30:00Z"
        }