"""
AI Conversation Schemas

This module defines Pydantic schemas for AI conversation API operations,
including request/response models and validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.base import BaseSchema, BaseResponseSchema, BaseCreateSchema, BaseUpdateSchema


class MessageType(str, Enum):
    """Enumeration for message types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIConversationBase(BaseSchema):
    """Base schema for AI conversation data."""
    
    message_type: MessageType = Field(..., description="Type of message")
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    session_id: Optional[str] = Field(None, max_length=255, description="Session identifier")
    context_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class AIConversationCreate(AIConversationBase, BaseCreateSchema):
    """Schema for creating AI conversation entries."""
    
    user_id: int = Field(..., gt=0, description="User ID")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")
    model_used: Optional[str] = Field(None, max_length=100, description="AI model used for generation")
    
    @validator('embedding')
    def validate_embedding(cls, v):
        """Validate embedding vector."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Embedding must be a list of floats")
            if len(v) == 0:
                raise ValueError("Embedding cannot be empty")
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("Embedding must contain only numeric values")
        return v


class AIConversationUpdate(BaseUpdateSchema):
    """Schema for updating AI conversation entries."""
    
    response_rating: Optional[int] = Field(None, ge=1, le=5, description="Response rating (1-5)")
    response_feedback: Optional[str] = Field(None, max_length=1000, description="Response feedback")
    context_metadata: Optional[Dict[str, Any]] = Field(None, description="Updated context metadata")


class AIConversationResponse(AIConversationBase, BaseResponseSchema):
    """Schema for AI conversation API responses."""
    
    user_id: int = Field(..., description="User ID")
    embedding_dimension: Optional[int] = Field(None, description="Embedding vector dimension")
    response_rating: Optional[int] = Field(None, description="Response rating (1-5)")
    response_feedback: Optional[str] = Field(None, description="Response feedback")
    model_used: Optional[str] = Field(None, description="AI model used")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        from_attributes = True


class ConversationHistoryResponse(BaseSchema):
    """Schema for conversation history responses."""
    
    conversations: List[AIConversationResponse] = Field(..., description="List of conversations")
    total_count: int = Field(..., description="Total number of conversations")
    has_more: bool = Field(..., description="Whether more conversations are available")
    session_info: Optional[Dict[str, Any]] = Field(None, description="Session information")


class ChatRequest(BaseSchema):
    """Schema for chat API requests."""
    
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, max_length=255, description="Session identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    include_history: bool = Field(True, description="Whether to include conversation history")
    
    @validator('message')
    def validate_message(cls, v):
        """Validate chat message."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseSchema):
    """Schema for chat API responses."""
    
    response: str = Field(..., description="AI-generated response")
    session_id: str = Field(..., description="Session identifier")
    conversation_id: int = Field(..., description="Conversation entry ID")
    model_used: str = Field(..., description="AI model used")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Context information used")


class SimilarConversationResponse(BaseSchema):
    """Schema for similar conversation search results."""
    
    conversation_id: int = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(..., description="Message type")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
    created_at: datetime = Field(..., description="Creation timestamp")
    context_metadata: Optional[Dict[str, Any]] = Field(None, description="Context metadata")


class ConversationSearchRequest(BaseSchema):
    """Schema for conversation search requests."""
    
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    similarity_threshold: float = Field(0.7, ge=0, le=1, description="Minimum similarity score")
    message_type: Optional[MessageType] = Field(None, description="Filter by message type")
    user_id: Optional[int] = Field(None, description="Filter by user ID")


class ConversationSearchResponse(BaseSchema):
    """Schema for conversation search responses."""
    
    query: str = Field(..., description="Original search query")
    results: List[SimilarConversationResponse] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")
    search_time_ms: int = Field(..., description="Search processing time")


class ConversationAnalyticsResponse(BaseSchema):
    """Schema for conversation analytics responses."""
    
    period_days: int = Field(..., description="Analysis period in days")
    total_conversations: int = Field(..., description="Total number of conversations")
    user_messages: int = Field(..., description="Number of user messages")
    assistant_messages: int = Field(..., description="Number of assistant messages")
    unique_users: int = Field(..., description="Number of unique users")
    unique_sessions: int = Field(..., description="Number of unique sessions")
    avg_user_message_length: float = Field(..., description="Average user message length")
    avg_assistant_message_length: float = Field(..., description="Average assistant message length")
    conversations_per_day: float = Field(..., description="Average conversations per day")
    avg_conversations_per_user: float = Field(..., description="Average conversations per user")


class TopicAnalysisResponse(BaseSchema):
    """Schema for topic analysis responses."""
    
    topic: str = Field(..., description="Topic name")
    frequency: int = Field(..., description="Number of mentions")
    percentage: float = Field(..., description="Percentage of total conversations")


class ConversationTopicsResponse(BaseSchema):
    """Schema for conversation topics analysis."""
    
    period_days: int = Field(..., description="Analysis period in days")
    total_conversations_analyzed: int = Field(..., description="Total conversations analyzed")
    topics: List[TopicAnalysisResponse] = Field(..., description="Popular topics")


class ConversationRatingRequest(BaseSchema):
    """Schema for rating conversation responses."""
    
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    
    @validator('feedback')
    def validate_feedback(cls, v):
        """Validate feedback text."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class ConversationExportRequest(BaseSchema):
    """Schema for conversation export requests."""
    
    format: str = Field("json", pattern="^(json|csv)$", description="Export format")
    include_embeddings: bool = Field(False, description="Whether to include embedding vectors")
    date_from: Optional[datetime] = Field(None, description="Start date for export")
    date_to: Optional[datetime] = Field(None, description="End date for export")


class ConversationExportResponse(BaseSchema):
    """Schema for conversation export responses."""
    
    user_id: int = Field(..., description="User ID")
    export_date: datetime = Field(..., description="Export timestamp")
    format: str = Field(..., description="Export format")
    total_conversations: int = Field(..., description="Number of conversations exported")
    file_size_bytes: Optional[int] = Field(None, description="Export file size")
    download_url: Optional[str] = Field(None, description="Download URL if applicable")


class SessionInfoResponse(BaseSchema):
    """Schema for conversation session information."""
    
    session_id: str = Field(..., description="Session identifier")
    message_count: int = Field(..., description="Number of messages in session")
    session_start: datetime = Field(..., description="Session start time")
    session_end: datetime = Field(..., description="Session end time")
    duration_minutes: float = Field(..., description="Session duration in minutes")


class UserConversationStatsResponse(BaseSchema):
    """Schema for user conversation statistics."""
    
    user_id: int = Field(..., description="User ID")
    total_conversations: int = Field(..., description="Total number of conversations")
    total_sessions: int = Field(..., description="Total number of sessions")
    avg_messages_per_session: float = Field(..., description="Average messages per session")
    most_active_day: Optional[str] = Field(None, description="Most active day of week")
    favorite_topics: List[TopicAnalysisResponse] = Field(..., description="User's favorite topics")
    engagement_level: str = Field(..., description="User engagement level")
    last_conversation_date: Optional[datetime] = Field(None, description="Last conversation date")


class AICoachingInsightResponse(BaseSchema):
    """Schema for AI coaching insights."""
    
    user_id: int = Field(..., description="User ID")
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in insight")
    actionable_suggestions: List[str] = Field(..., description="Actionable suggestions")
    related_conversations: List[int] = Field(..., description="Related conversation IDs")
    generated_at: datetime = Field(..., description="Insight generation timestamp")


class ConversationContextResponse(BaseSchema):
    """Schema for conversation context information."""
    
    user_id: int = Field(..., description="User ID")
    recent_history: List[AIConversationResponse] = Field(..., description="Recent conversation history")
    similar_conversations: List[SimilarConversationResponse] = Field(..., description="Similar past conversations")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    context_summary: str = Field(..., description="Context summary")
    relevance_score: float = Field(..., ge=0, le=1, description="Context relevance score")


class BatchEmbeddingRequest(BaseSchema):
    """Schema for batch embedding generation requests."""
    
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to embed")
    model: Optional[str] = Field("text-embedding-3-small", description="Embedding model to use")
    
    @validator('texts')
    def validate_texts(cls, v):
        """Validate text list."""
        if not v:
            raise ValueError("Text list cannot be empty")
        
        for i, text in enumerate(v):
            if not text or not text.strip():
                raise ValueError(f"Text at index {i} cannot be empty")
        
        return [text.strip() for text in v]


class BatchEmbeddingResponse(BaseSchema):
    """Schema for batch embedding generation responses."""
    
    embeddings: List[List[float]] = Field(..., description="Generated embeddings")
    model_used: str = Field(..., description="Embedding model used")
    total_tokens: int = Field(..., description="Total tokens processed")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    embedding_dimension: int = Field(..., description="Embedding vector dimension")