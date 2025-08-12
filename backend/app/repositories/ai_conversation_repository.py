"""
AI Conversation Repository

This module provides the repository class for AI conversation data access,
including vector operations and semantic search capabilities.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import json
import logging

from app.repositories.base_repository import BaseRepository
from app.models.ai_conversation import AIConversation
from app.schemas.ai_conversation import AIConversationCreate, AIConversationUpdate

logger = logging.getLogger(__name__)


class AIConversationRepository(BaseRepository[AIConversation]):
    """
    Repository for AI conversation data access operations.
    
    This repository handles storage, retrieval, and vector operations
    for AI conversation history and semantic search.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize repository with AI conversation model."""
        super().__init__(AIConversation, db_session)
    
    async def create_conversation_entry(
        self,
        user_id: int,
        message_type: str,
        content: str,
        embedding: Optional[List[float]] = None,
        context_metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> AIConversation:
        """
        Create a new conversation entry with embedding.
        
        Args:
            user_id: User's ID
            message_type: Type of message ('user', 'assistant', 'system')
            content: Message content
            embedding: Vector embedding for semantic search
            context_metadata: Additional context information
            session_id: Optional session identifier
            model_used: AI model used (for assistant messages)
            
        Returns:
            Created AIConversation instance
        """
        try:
            # Create conversation entry
            conversation_data = {
                "user_id": user_id,
                "message_type": message_type,
                "content": content,
                "session_id": session_id,
                "model_used": model_used
            }
            
            conversation = await self.create(conversation_data)
            
            # Set embedding and metadata using model methods
            if embedding:
                conversation.set_embedding_vector(embedding)
            
            if context_metadata:
                conversation.set_context_metadata(context_metadata)
            
            # Commit changes
            await self.db.commit()
            await self.db.refresh(conversation)
            
            logger.info(f"Created conversation entry for user {user_id}, type: {message_type}")
            return conversation
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating conversation entry: {str(e)}")
            raise
    
    async def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50,
        message_type: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[AIConversation]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User's ID
            limit: Maximum number of conversations to return
            message_type: Optional filter by message type
            session_id: Optional filter by session ID
            
        Returns:
            List of AIConversation instances
        """
        try:
            query = select(self.model).where(self.model.user_id == user_id)
            
            # Apply filters
            if message_type:
                query = query.where(self.model.message_type == message_type)
            
            if session_id:
                query = query.where(self.model.session_id == session_id)
            
            # Order by creation time (most recent first)
            query = query.order_by(desc(self.model.created_at)).limit(limit)
            
            result = await self.db.execute(query)
            conversations = result.scalars().all()
            
            logger.debug(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return list(conversations)
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise
    
    async def get_user_conversations_since(
        self,
        user_id: int,
        since_date: datetime,
        limit: int = 100
    ) -> List[AIConversation]:
        """
        Get user conversations since a specific date.
        
        Args:
            user_id: User's ID
            since_date: Date to filter from
            limit: Maximum number of conversations
            
        Returns:
            List of AIConversation instances
        """
        try:
            query = select(self.model).where(
                and_(
                    self.model.user_id == user_id,
                    self.model.created_at >= since_date
                )
            ).order_by(desc(self.model.created_at)).limit(limit)
            
            result = await self.db.execute(query)
            conversations = result.scalars().all()
            
            logger.debug(f"Retrieved {len(conversations)} conversations since {since_date}")
            return list(conversations)
            
        except Exception as e:
            logger.error(f"Error getting conversations since date: {str(e)}")
            raise
    
    async def search_similar_conversations(
        self,
        query_embedding: List[float],
        user_id: Optional[int] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        message_type: Optional[str] = None
    ) -> List[AIConversation]:
        """
        Search for similar conversations using vector similarity.
        
        Note: This is a simplified implementation. In production with TiDB,
        you would use vector index operations for better performance.
        
        Args:
            query_embedding: Query vector embedding
            user_id: Optional user ID to limit search scope
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            message_type: Optional filter by message type
            
        Returns:
            List of similar AIConversation instances with similarity scores
        """
        try:
            # Build base query
            query = select(self.model).where(self.model.embedding.isnot(None))
            
            # Apply filters
            if user_id:
                query = query.where(self.model.user_id == user_id)
            
            if message_type:
                query = query.where(self.model.message_type == message_type)
            
            # Get all conversations with embeddings
            result = await self.db.execute(query)
            conversations = result.scalars().all()
            
            # Calculate similarities (in production, this would be done by TiDB vector index)
            similar_conversations = []
            
            for conv in conversations:
                embedding = conv.get_embedding_vector()
                if not embedding:
                    continue
                
                # Calculate cosine similarity
                similarity = self._calculate_cosine_similarity(query_embedding, embedding)
                
                if similarity >= similarity_threshold:
                    # Add similarity as an attribute for sorting
                    conv.similarity = similarity
                    similar_conversations.append(conv)
            
            # Sort by similarity (descending) and limit results
            similar_conversations.sort(key=lambda x: x.similarity, reverse=True)
            
            logger.debug(f"Found {len(similar_conversations)} similar conversations")
            return similar_conversations[:limit]
            
        except Exception as e:
            logger.error(f"Error searching similar conversations: {str(e)}")
            return []
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        try:
            import numpy as np
            
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            magnitude1 = np.linalg.norm(v1)
            magnitude2 = np.linalg.norm(v2)
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return float(dot_product / (magnitude1 * magnitude2))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    async def get_conversation_sessions(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get conversation sessions for a user.
        
        Args:
            user_id: User's ID
            limit: Maximum number of sessions
            
        Returns:
            List of session information dictionaries
        """
        try:
            # Get distinct session IDs with conversation counts
            query = select(
                self.model.session_id,
                func.count(self.model.id).label('message_count'),
                func.min(self.model.created_at).label('session_start'),
                func.max(self.model.created_at).label('session_end')
            ).where(
                and_(
                    self.model.user_id == user_id,
                    self.model.session_id.isnot(None)
                )
            ).group_by(self.model.session_id).order_by(
                desc(func.max(self.model.created_at))
            ).limit(limit)
            
            result = await self.db.execute(query)
            sessions = result.all()
            
            session_list = []
            for session in sessions:
                session_list.append({
                    "session_id": session.session_id,
                    "message_count": session.message_count,
                    "session_start": session.session_start,
                    "session_end": session.session_end,
                    "duration_minutes": (session.session_end - session.session_start).total_seconds() / 60
                })
            
            logger.debug(f"Retrieved {len(session_list)} conversation sessions for user {user_id}")
            return session_list
            
        except Exception as e:
            logger.error(f"Error getting conversation sessions: {str(e)}")
            return []
    
    async def get_conversation_statistics(
        self,
        user_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get conversation statistics for analytics.
        
        Args:
            user_id: Optional user ID to limit scope
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing conversation statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Build base query
            query = select(self.model).where(self.model.created_at >= start_date)
            
            if user_id:
                query = query.where(self.model.user_id == user_id)
            
            result = await self.db.execute(query)
            conversations = result.scalars().all()
            
            # Calculate statistics
            total_conversations = len(conversations)
            user_messages = [c for c in conversations if c.message_type == "user"]
            assistant_messages = [c for c in conversations if c.message_type == "assistant"]
            
            # Calculate averages
            avg_user_message_length = (
                sum(len(c.content) for c in user_messages) / len(user_messages)
                if user_messages else 0
            )
            
            avg_assistant_message_length = (
                sum(len(c.content) for c in assistant_messages) / len(assistant_messages)
                if assistant_messages else 0
            )
            
            # Get unique users and sessions
            unique_users = len(set(c.user_id for c in conversations))
            unique_sessions = len(set(c.session_id for c in conversations if c.session_id))
            
            # Calculate engagement metrics
            conversations_per_day = total_conversations / days_back if days_back > 0 else 0
            
            stats = {
                "period_days": days_back,
                "total_conversations": total_conversations,
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "unique_users": unique_users,
                "unique_sessions": unique_sessions,
                "avg_user_message_length": round(avg_user_message_length, 1),
                "avg_assistant_message_length": round(avg_assistant_message_length, 1),
                "conversations_per_day": round(conversations_per_day, 2),
                "avg_conversations_per_user": round(total_conversations / unique_users, 2) if unique_users > 0 else 0
            }
            
            logger.debug(f"Generated conversation statistics for {days_back} days")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting conversation statistics: {str(e)}")
            return {}
    
    async def update_conversation_rating(
        self,
        conversation_id: int,
        rating: int,
        feedback: Optional[str] = None
    ) -> Optional[AIConversation]:
        """
        Update conversation rating and feedback.
        
        Args:
            conversation_id: Conversation ID
            rating: Rating from 1-5
            feedback: Optional feedback text
            
        Returns:
            Updated AIConversation instance or None
        """
        try:
            conversation = await self.get_by_id(conversation_id)
            if not conversation:
                return None
            
            conversation.update_response_rating(rating, feedback)
            await self.db.commit()
            
            logger.info(f"Updated rating for conversation {conversation_id}: {rating}")
            return conversation
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating conversation rating: {str(e)}")
            raise
    
    async def delete_user_conversations(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        older_than_days: Optional[int] = None
    ) -> int:
        """
        Delete user conversations with optional filters.
        
        Args:
            user_id: User's ID
            session_id: Optional session ID to delete
            older_than_days: Optional age threshold in days
            
        Returns:
            Number of conversations deleted
        """
        try:
            query = select(self.model).where(self.model.user_id == user_id)
            
            # Apply filters
            if session_id:
                query = query.where(self.model.session_id == session_id)
            
            if older_than_days:
                cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
                query = query.where(self.model.created_at < cutoff_date)
            
            # Get conversations to delete
            result = await self.db.execute(query)
            conversations = result.scalars().all()
            
            # Delete conversations
            for conversation in conversations:
                await self.db.delete(conversation)
            
            await self.db.commit()
            
            deleted_count = len(conversations)
            logger.info(f"Deleted {deleted_count} conversations for user {user_id}")
            return deleted_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting user conversations: {str(e)}")
            raise
    
    async def get_popular_topics(
        self,
        days_back: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get popular conversation topics based on content analysis.
        
        Args:
            days_back: Number of days to analyze
            limit: Maximum number of topics to return
            
        Returns:
            List of popular topics with frequencies
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get user messages from the period
            query = select(self.model).where(
                and_(
                    self.model.message_type == "user",
                    self.model.created_at >= start_date
                )
            )
            
            result = await self.db.execute(query)
            conversations = result.scalars().all()
            
            # Simple keyword-based topic analysis
            topic_keywords = {
                "transportation": ["car", "drive", "transport", "bike", "walk", "public", "commute", "travel", "flight"],
                "energy": ["energy", "electric", "power", "heat", "cooling", "thermostat", "solar", "renewable", "electricity"],
                "diet": ["food", "eat", "meat", "vegetarian", "vegan", "diet", "cooking", "local", "organic"],
                "waste": ["waste", "recycle", "plastic", "packaging", "reduce", "reuse", "trash", "garbage"],
                "lifestyle": ["lifestyle", "habits", "daily", "routine", "changes", "improvement", "sustainable"],
                "goals": ["goal", "target", "achieve", "progress", "plan", "objective", "reduce", "save"],
                "home": ["home", "house", "apartment", "insulation", "heating", "cooling", "appliances"],
                "shopping": ["shopping", "buy", "purchase", "consumption", "products", "clothes", "electronics"]
            }
            
            topic_counts = {topic: 0 for topic in topic_keywords}
            
            for conv in conversations:
                content_lower = conv.content.lower()
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content_lower for keyword in keywords):
                        topic_counts[topic] += 1
            
            # Sort topics by frequency
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            
            popular_topics = []
            for topic, count in sorted_topics[:limit]:
                if count > 0:
                    popular_topics.append({
                        "topic": topic,
                        "frequency": count,
                        "percentage": round((count / len(conversations)) * 100, 1) if conversations else 0
                    })
            
            logger.debug(f"Analyzed {len(conversations)} conversations for popular topics")
            return popular_topics
            
        except Exception as e:
            logger.error(f"Error getting popular topics: {str(e)}")
            return []
    
    async def export_user_conversations(
        self,
        user_id: int,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export user conversations for data portability.
        
        Args:
            user_id: User's ID
            format: Export format ('json', 'csv')
            
        Returns:
            Dictionary containing exported conversation data
        """
        try:
            conversations = await self.get_user_conversations(user_id, limit=1000)
            
            if format == "json":
                export_data = {
                    "user_id": user_id,
                    "export_date": datetime.utcnow().isoformat(),
                    "total_conversations": len(conversations),
                    "conversations": []
                }
                
                for conv in conversations:
                    conv_data = {
                        "id": conv.id,
                        "message_type": conv.message_type,
                        "content": conv.content,
                        "session_id": conv.session_id,
                        "created_at": conv.created_at.isoformat(),
                        "context_metadata": conv.get_context_metadata(),
                        "response_rating": conv.response_rating,
                        "model_used": conv.model_used
                    }
                    export_data["conversations"].append(conv_data)
                
                return export_data
            
            else:
                # For other formats, return basic structure
                return {
                    "user_id": user_id,
                    "format": format,
                    "message": f"Export format '{format}' not implemented yet"
                }
                
        except Exception as e:
            logger.error(f"Error exporting user conversations: {str(e)}")
            return {"error": str(e)}