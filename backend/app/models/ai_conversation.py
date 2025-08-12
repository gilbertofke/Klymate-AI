"""
AI Conversation Model

This module defines the SQLAlchemy model for storing AI conversation history
with vector embeddings for semantic search capabilities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
import json
import logging

from app.models.base import BaseModel, TimestampMixin
from app.models.user import User

logger = logging.getLogger(__name__)


class AIConversation(BaseModel, TimestampMixin):
    """
    Model for storing AI conversation history with vector embeddings.
    
    This model stores individual messages in AI coaching conversations,
    including embeddings for semantic search and context retrieval.
    """
    
    __tablename__ = "ai_conversations"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message details
    message_type = Column(
        Enum("user", "assistant", "system", name="message_type_enum"),
        nullable=False,
        index=True
    )
    content = Column(Text, nullable=False)
    
    # Vector embedding for semantic search (stored as JSON for TiDB compatibility)
    embedding = Column(JSON, nullable=True)
    
    # Context and metadata
    context_metadata = Column(JSON, nullable=True)
    
    # Conversation session tracking
    session_id = Column(String(255), nullable=True, index=True)
    
    # Response quality metrics
    response_rating = Column(Integer, nullable=True)  # 1-5 rating if provided by user
    response_feedback = Column(Text, nullable=True)
    
    # Processing metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ai_conversations")
    
    def __repr__(self) -> str:
        """String representation of AI conversation."""
        return f"<AIConversation(id={self.id}, user_id={self.user_id}, type={self.message_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        base_dict = super().to_dict()
        
        # Parse JSON fields
        if self.context_metadata:
            try:
                base_dict["context_metadata"] = json.loads(self.context_metadata) if isinstance(self.context_metadata, str) else self.context_metadata
            except (json.JSONDecodeError, TypeError):
                base_dict["context_metadata"] = {}
        
        if self.embedding:
            try:
                base_dict["embedding"] = json.loads(self.embedding) if isinstance(self.embedding, str) else self.embedding
            except (json.JSONDecodeError, TypeError):
                base_dict["embedding"] = []
        
        return base_dict
    
    def get_embedding_vector(self) -> List[float]:
        """
        Get embedding as a list of floats.
        
        Returns:
            List of float values representing the embedding vector
        """
        try:
            if not self.embedding:
                return []
            
            if isinstance(self.embedding, str):
                return json.loads(self.embedding)
            elif isinstance(self.embedding, list):
                return self.embedding
            else:
                logger.warning(f"Unexpected embedding type: {type(self.embedding)}")
                return []
                
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing embedding vector: {str(e)}")
            return []
    
    def set_embedding_vector(self, embedding: List[float]) -> None:
        """
        Set embedding vector from list of floats.
        
        Args:
            embedding: List of float values representing the embedding
        """
        try:
            if not embedding:
                self.embedding = None
                return
            
            # Store as JSON for TiDB compatibility
            self.embedding = json.dumps(embedding) if not isinstance(embedding, str) else embedding
            
        except (TypeError, ValueError) as e:
            logger.error(f"Error setting embedding vector: {str(e)}")
            self.embedding = None
    
    def get_context_metadata(self) -> Dict[str, Any]:
        """
        Get context metadata as dictionary.
        
        Returns:
            Dictionary containing context metadata
        """
        try:
            if not self.context_metadata:
                return {}
            
            if isinstance(self.context_metadata, str):
                return json.loads(self.context_metadata)
            elif isinstance(self.context_metadata, dict):
                return self.context_metadata
            else:
                logger.warning(f"Unexpected metadata type: {type(self.context_metadata)}")
                return {}
                
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing context metadata: {str(e)}")
            return {}
    
    def set_context_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set context metadata from dictionary.
        
        Args:
            metadata: Dictionary containing context information
        """
        try:
            if not metadata:
                self.context_metadata = None
                return
            
            # Store as JSON
            self.context_metadata = json.dumps(metadata) if not isinstance(metadata, str) else metadata
            
        except (TypeError, ValueError) as e:
            logger.error(f"Error setting context metadata: {str(e)}")
            self.context_metadata = None
    
    def calculate_similarity(self, other_embedding: List[float]) -> float:
        """
        Calculate cosine similarity with another embedding.
        
        Args:
            other_embedding: Embedding vector to compare with
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        try:
            from app.utils.ai_utilities import VectorOperations
            
            current_embedding = self.get_embedding_vector()
            if not current_embedding or not other_embedding:
                return 0.0
            
            vector_ops = VectorOperations()
            similarity = vector_ops.calculate_cosine_similarity(current_embedding, other_embedding)
            
            # Convert to 0-1 range (cosine similarity is -1 to 1)
            return (similarity + 1) / 2
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_message_summary(self, max_length: int = 100) -> str:
        """
        Get a summary of the message content.
        
        Args:
            max_length: Maximum length of summary
            
        Returns:
            Truncated message content
        """
        if not self.content:
            return ""
        
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length - 3] + "..."
    
    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.message_type == "user"
    
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message."""
        return self.message_type == "assistant"
    
    def is_system_message(self) -> bool:
        """Check if this is a system message."""
        return self.message_type == "system"
    
    def get_conversation_pair(self) -> Optional['AIConversation']:
        """
        Get the corresponding message in the conversation pair.
        For user messages, returns the assistant response.
        For assistant messages, returns the user message.
        
        Returns:
            Corresponding AIConversation instance or None
        """
        try:
            from sqlalchemy.orm import Session
            from sqlalchemy import and_, or_
            
            # This would need to be called with a session context
            # Implementation would depend on how it's used
            # For now, return None as this requires database access
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation pair: {str(e)}")
            return None
    
    def update_response_rating(self, rating: int, feedback: Optional[str] = None) -> None:
        """
        Update response rating and feedback.
        
        Args:
            rating: Rating from 1-5
            feedback: Optional text feedback
        """
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        self.response_rating = rating
        if feedback:
            self.response_feedback = feedback
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """
        Get processing performance metrics.
        
        Returns:
            Dictionary containing processing metrics
        """
        return {
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "processing_time_ms": self.processing_time_ms,
            "has_embedding": bool(self.embedding),
            "content_length": len(self.content) if self.content else 0,
            "has_metadata": bool(self.context_metadata)
        }
    
    def set_processing_metrics(
        self,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ) -> None:
        """
        Set processing performance metrics.
        
        Args:
            model_used: Name of the AI model used
            tokens_used: Number of tokens consumed
            processing_time_ms: Processing time in milliseconds
        """
        if model_used:
            self.model_used = model_used
        if tokens_used is not None:
            self.tokens_used = tokens_used
        if processing_time_ms is not None:
            self.processing_time_ms = processing_time_ms
    
    @classmethod
    def create_user_message(
        cls,
        user_id: int,
        content: str,
        session_id: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> 'AIConversation':
        """
        Factory method to create a user message.
        
        Args:
            user_id: User's ID
            content: Message content
            session_id: Optional session identifier
            context_metadata: Optional context information
            
        Returns:
            New AIConversation instance for user message
        """
        conversation = cls(
            user_id=user_id,
            message_type="user",
            content=content,
            session_id=session_id
        )
        
        if context_metadata:
            conversation.set_context_metadata(context_metadata)
        
        return conversation
    
    @classmethod
    def create_assistant_message(
        cls,
        user_id: int,
        content: str,
        session_id: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None,
        model_used: Optional[str] = None
    ) -> 'AIConversation':
        """
        Factory method to create an assistant message.
        
        Args:
            user_id: User's ID
            content: Message content
            session_id: Optional session identifier
            context_metadata: Optional context information
            model_used: AI model used to generate response
            
        Returns:
            New AIConversation instance for assistant message
        """
        conversation = cls(
            user_id=user_id,
            message_type="assistant",
            content=content,
            session_id=session_id,
            model_used=model_used
        )
        
        if context_metadata:
            conversation.set_context_metadata(context_metadata)
        
        return conversation
    
    @classmethod
    def create_system_message(
        cls,
        user_id: int,
        content: str,
        session_id: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> 'AIConversation':
        """
        Factory method to create a system message.
        
        Args:
            user_id: User's ID
            content: Message content
            session_id: Optional session identifier
            context_metadata: Optional context information
            
        Returns:
            New AIConversation instance for system message
        """
        conversation = cls(
            user_id=user_id,
            message_type="system",
            content=content,
            session_id=session_id
        )
        
        if context_metadata:
            conversation.set_context_metadata(context_metadata)
        
        return conversation