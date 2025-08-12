"""
AI Utilities and Vector Operations

This module provides comprehensive AI coaching infrastructure including
LangChain integration, OpenAI API operations, and vector embeddings for
semantic search and conversation management.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime
import json

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

# OpenAI direct imports
from openai import OpenAI
import tiktoken

# Vector operations
import numpy as np
from typing import Union

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingGenerator:
    """
    Handles OpenAI embedding generation for semantic search and similarity matching.
    
    This class provides utilities for generating embeddings from text content
    and managing vector operations for the AI coaching system.
    """
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding generator.
        
        Args:
            model: OpenAI embedding model to use
        """
        self.model = model
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Embedding dimensions for different models
        self.embedding_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text input.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of float values representing the embedding vector
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            # Truncate text if too long (max ~8000 tokens for embedding models)
            tokens = self.encoding.encode(text)
            if len(tokens) > 8000:
                text = self.encoding.decode(tokens[:8000])
                logger.warning(f"Text truncated to 8000 tokens for embedding generation")
            
            # Generate embedding
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        try:
            # Process in batches to avoid API limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings for batch
                tasks = [self.generate_embedding(text) for text in batch]
                batch_embeddings = await asyncio.gather(*tasks)
                all_embeddings.extend(batch_embeddings)
                
                # Add small delay to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(all_embeddings)} embeddings in batches")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension size for the current embedding model."""
        return self.embedding_dimensions.get(self.model, 1536)


class LangChainManager:
    """
    Manages LangChain operations for AI coaching conversations.
    
    This class handles chat model initialization, prompt templates,
    and conversation processing using LangChain framework.
    """
    
    def __init__(self):
        """Initialize LangChain manager with OpenAI configuration."""
        self.api_key = settings.OPENAI_API_KEY
        self.chat_model = None
        self.memory = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LangChain components."""
        try:
            # Initialize chat model
            self.chat_model = self.initialize_chat_model()
            
            # Initialize memory for conversation context
            self.memory = ConversationBufferWindowMemory(
                k=10,  # Keep last 10 exchanges
                return_messages=True,
                memory_key="chat_history"
            )
            
            logger.info("LangChain components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LangChain components: {str(e)}")
            raise
    
    def initialize_chat_model(self) -> ChatOpenAI:
        """
        Initialize OpenAI chat model with optimal settings for coaching.
        
        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,  # Balanced creativity and consistency
            max_tokens=1000,  # Reasonable response length
            openai_api_key=self.api_key
        )
    
    def create_coaching_prompt(self, user_context: Dict[str, Any]) -> ChatPromptTemplate:
        """
        Create personalized coaching prompt template.
        
        Args:
            user_context: User profile and context information
            
        Returns:
            Configured ChatPromptTemplate
        """
        system_message = f"""You are Klymate AI, an expert carbon footprint coach helping users reduce their environmental impact.

User Context:
- Baseline Carbon Footprint: {user_context.get('baseline_footprint', 'Unknown')} kg CO2/year
- Current Goals: {', '.join(user_context.get('goals', ['General reduction']))}
- Location: {user_context.get('location', 'Not specified')}
- Interests: {', '.join(user_context.get('interests', ['Environmental sustainability']))}

Your role:
1. Provide personalized, actionable advice for reducing carbon footprint
2. Be encouraging and supportive while being scientifically accurate
3. Suggest specific, measurable actions the user can take
4. Reference their baseline footprint and goals when relevant
5. Keep responses concise but informative (under 200 words)
6. Ask follow-up questions to better understand their situation

Guidelines:
- Focus on the biggest impact areas: transport, energy, diet, consumption
- Provide realistic suggestions that fit their lifestyle
- Celebrate progress and encourage continued improvement
- Use positive, motivating language
- Include specific numbers when possible (CO2 savings, costs, etc.)
"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    async def process_conversation(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process user message and generate AI coaching response.
        
        Args:
            user_message: User's input message
            user_context: User profile and context
            conversation_history: Previous conversation messages
            
        Returns:
            AI-generated coaching response
        """
        try:
            # Create conversation chain
            chain = self._create_conversation_chain(user_context)
            
            # Add conversation history to memory if provided
            if conversation_history:
                self._load_conversation_history(conversation_history)
            
            # Process the conversation
            response = await chain.ainvoke({
                "input": user_message,
                "chat_history": self.memory.chat_memory.messages
            })
            
            # Extract response text
            ai_response = response.get("text", response.get("content", str(response)))
            
            # Update memory with new exchange
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(ai_response)
            
            logger.info(f"Generated AI coaching response ({len(ai_response)} chars)")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error processing conversation: {str(e)}")
            # Return fallback response
            return self._get_fallback_response(user_message)
    
    def _create_conversation_chain(self, user_context: Dict[str, Any]) -> LLMChain:
        """Create LangChain conversation chain."""
        prompt = self.create_coaching_prompt(user_context)
        return LLMChain(
            llm=self.chat_model,
            prompt=prompt,
            memory=self.memory,
            verbose=False
        )
    
    def _load_conversation_history(self, history: List[Dict[str, str]]):
        """Load previous conversation history into memory."""
        try:
            self.memory.clear()  # Clear existing memory
            
            for message in history[-10:]:  # Load last 10 messages
                if message.get("type") == "user":
                    self.memory.chat_memory.add_user_message(message["content"])
                elif message.get("type") == "assistant":
                    self.memory.chat_memory.add_ai_message(message["content"])
            
            logger.debug(f"Loaded {len(history)} messages into conversation memory")
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Generate fallback response when AI processing fails."""
        fallback_responses = [
            "I'm having trouble processing your request right now. Could you try rephrasing your question about carbon footprint reduction?",
            "I apologize for the technical difficulty. In the meantime, consider focusing on the big three: transportation, energy use, and diet choices.",
            "I'm experiencing some issues, but I'm here to help! What specific area of your carbon footprint would you like to work on?",
        ]
        
        # Simple keyword-based fallback selection
        if any(word in user_message.lower() for word in ["transport", "car", "drive", "travel"]):
            return "For transportation, consider walking, cycling, public transit, or carpooling. Even one day per week can make a significant impact!"
        elif any(word in user_message.lower() for word in ["energy", "electric", "power", "heat"]):
            return "For energy savings, try adjusting your thermostat, using LED bulbs, and unplugging devices when not in use. Small changes add up!"
        elif any(word in user_message.lower() for word in ["food", "diet", "eat", "meat"]):
            return "Dietary changes can have a big impact! Try reducing meat consumption, eating locally grown food, and minimizing food waste."
        else:
            return fallback_responses[0]


class VectorOperations:
    """
    Handles vector operations for semantic search and similarity matching.
    
    This class provides utilities for vector calculations, similarity search,
    and managing vector databases for AI conversation context.
    """
    
    def __init__(self):
        """Initialize vector operations utilities."""
        pass
    
    def calculate_cosine_similarity(
        self, 
        vector1: List[float], 
        vector2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vector1: First vector
            vector2: Second vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            # Convert to numpy arrays for efficient computation
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            magnitude1 = np.linalg.norm(v1)
            magnitude2 = np.linalg.norm(v2)
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    def find_similar_vectors(
        self,
        query_vector: List[float],
        vector_database: List[Dict[str, Any]],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find most similar vectors from a database.
        
        Args:
            query_vector: Vector to search for
            vector_database: List of vector entries with metadata
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar vectors with similarity scores
        """
        try:
            similarities = []
            
            for entry in vector_database:
                vector = entry.get("vector", [])
                if not vector:
                    continue
                
                similarity = self.calculate_cosine_similarity(query_vector, vector)
                
                if similarity >= similarity_threshold:
                    result_entry = entry.copy()
                    result_entry["similarity"] = similarity
                    similarities.append(result_entry)
            
            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.debug(f"Found {len(similarities)} similar vectors above threshold {similarity_threshold}")
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar vectors: {str(e)}")
            return []
    
    def normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Normalize vector to unit length.
        
        Args:
            vector: Input vector
            
        Returns:
            Normalized vector
        """
        try:
            v = np.array(vector)
            magnitude = np.linalg.norm(v)
            
            if magnitude == 0:
                return vector
            
            normalized = v / magnitude
            return normalized.tolist()
            
        except Exception as e:
            logger.error(f"Error normalizing vector: {str(e)}")
            return vector
    
    def calculate_vector_distance(
        self, 
        vector1: List[float], 
        vector2: List[float],
        distance_type: str = "euclidean"
    ) -> float:
        """
        Calculate distance between two vectors.
        
        Args:
            vector1: First vector
            vector2: Second vector
            distance_type: Type of distance ('euclidean', 'manhattan', 'cosine')
            
        Returns:
            Distance value
        """
        try:
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            if distance_type == "euclidean":
                return float(np.linalg.norm(v1 - v2))
            elif distance_type == "manhattan":
                return float(np.sum(np.abs(v1 - v2)))
            elif distance_type == "cosine":
                return 1.0 - self.calculate_cosine_similarity(vector1, vector2)
            else:
                raise ValueError(f"Unknown distance type: {distance_type}")
                
        except Exception as e:
            logger.error(f"Error calculating vector distance: {str(e)}")
            return float('inf')


class AIConversationManager:
    """
    Manages AI conversation storage, retrieval, and context management.
    
    This class handles the complete lifecycle of AI conversations including
    embedding generation, storage, and semantic search for context.
    """
    
    def __init__(self, db_session):
        """
        Initialize conversation manager.
        
        Args:
            db_session: Database session for conversation storage
        """
        self.db = db_session
        self.embedding_generator = OpenAIEmbeddingGenerator()
        self.vector_ops = VectorOperations()
        
        # Import repository here to avoid circular imports
        from app.repositories.ai_conversation_repository import AIConversationRepository
        self.repository = AIConversationRepository(db_session)
    
    async def store_conversation(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store conversation with embeddings for future retrieval.
        
        Args:
            user_id: User's ID
            user_message: User's message
            ai_response: AI's response
            context_metadata: Additional context information
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Generate embeddings for both messages
            user_embedding = await self.embedding_generator.generate_embedding(user_message)
            ai_embedding = await self.embedding_generator.generate_embedding(ai_response)
            
            # Store user message
            await self.repository.create_conversation_entry(
                user_id=user_id,
                message_type="user",
                content=user_message,
                embedding=user_embedding,
                context_metadata=context_metadata
            )
            
            # Store AI response
            await self.repository.create_conversation_entry(
                user_id=user_id,
                message_type="assistant",
                content=ai_response,
                embedding=ai_embedding,
                context_metadata=context_metadata
            )
            
            logger.info(f"Stored conversation for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
            return False
    
    async def get_conversation_history(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation history for a user.
        
        Args:
            user_id: User's ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        try:
            conversations = await self.repository.get_user_conversations(user_id, limit)
            
            history = []
            for conv in conversations:
                history.append({
                    "id": conv.id,
                    "type": conv.message_type,
                    "content": conv.content,
                    "timestamp": conv.created_at,
                    "metadata": conv.context_metadata
                })
            
            logger.debug(f"Retrieved {len(history)} conversation messages for user {user_id}")
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    async def find_similar_conversations(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar conversations using semantic search.
        
        Args:
            query: Search query
            user_id: Optional user ID to limit search scope
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar conversations with similarity scores
        """
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Search for similar conversations
            similar_conversations = await self.repository.search_similar_conversations(
                query_embedding=query_embedding,
                user_id=user_id,
                limit=limit * 2,  # Get more results for filtering
                similarity_threshold=similarity_threshold
            )
            
            # Process and rank results
            results = []
            for conv in similar_conversations[:limit]:
                results.append({
                    "id": conv.id,
                    "user_id": conv.user_id,
                    "content": conv.content,
                    "message_type": conv.message_type,
                    "similarity": getattr(conv, 'similarity', 0.0),
                    "timestamp": conv.created_at,
                    "metadata": conv.context_metadata
                })
            
            logger.debug(f"Found {len(results)} similar conversations for query")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar conversations: {str(e)}")
            return []
    
    async def get_conversation_context(
        self,
        user_id: int,
        current_message: str,
        context_window: int = 5
    ) -> Dict[str, Any]:
        """
        Get relevant conversation context for AI processing.
        
        Args:
            user_id: User's ID
            current_message: Current user message
            context_window: Number of recent messages to include
            
        Returns:
            Dictionary containing conversation context
        """
        try:
            # Get recent conversation history
            recent_history = await self.get_conversation_history(user_id, context_window * 2)
            
            # Find similar past conversations
            similar_conversations = await self.find_similar_conversations(
                current_message, user_id, limit=3
            )
            
            # Compile context
            context = {
                "recent_history": recent_history[:context_window * 2],
                "similar_conversations": similar_conversations,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.debug(f"Compiled conversation context for user {user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return {"recent_history": [], "similar_conversations": []}
    
    async def analyze_conversation_patterns(
        self,
        user_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze user's conversation patterns and preferences.
        
        Args:
            user_id: User's ID
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing conversation analysis
        """
        try:
            from datetime import datetime, timedelta
            
            # Get conversations from specified period
            start_date = datetime.utcnow() - timedelta(days=days_back)
            conversations = await self.repository.get_user_conversations_since(
                user_id, start_date
            )
            
            if not conversations:
                return {"message": "No conversations found in specified period"}
            
            # Analyze patterns
            user_messages = [c for c in conversations if c.message_type == "user"]
            ai_messages = [c for c in conversations if c.message_type == "assistant"]
            
            # Calculate metrics
            total_conversations = len(user_messages)
            avg_message_length = sum(len(c.content) for c in user_messages) / len(user_messages) if user_messages else 0
            
            # Topic analysis (simple keyword-based)
            topics = self._analyze_conversation_topics(user_messages)
            
            analysis = {
                "period_days": days_back,
                "total_conversations": total_conversations,
                "avg_message_length": round(avg_message_length, 1),
                "conversation_frequency": round(total_conversations / days_back, 2),
                "top_topics": topics[:5],
                "engagement_level": "high" if total_conversations > days_back * 0.5 else "medium" if total_conversations > days_back * 0.2 else "low"
            }
            
            logger.debug(f"Analyzed conversation patterns for user {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {str(e)}")
            return {}
    
    def _analyze_conversation_topics(self, messages: List) -> List[Dict[str, Any]]:
        """Analyze topics from conversation messages."""
        try:
            # Simple keyword-based topic analysis
            topic_keywords = {
                "transportation": ["car", "drive", "transport", "bike", "walk", "public", "commute", "travel"],
                "energy": ["energy", "electric", "power", "heat", "cooling", "thermostat", "solar", "renewable"],
                "diet": ["food", "eat", "meat", "vegetarian", "vegan", "diet", "cooking", "local"],
                "waste": ["waste", "recycle", "plastic", "packaging", "reduce", "reuse"],
                "lifestyle": ["lifestyle", "habits", "daily", "routine", "changes", "improvement"],
                "goals": ["goal", "target", "achieve", "progress", "plan", "objective"]
            }
            
            topic_counts = {topic: 0 for topic in topic_keywords}
            
            for message in messages:
                content_lower = message.content.lower()
                for topic, keywords in topic_keywords.items():
                    for keyword in keywords:
                        if keyword in content_lower:
                            topic_counts[topic] += 1
                            break
            
            # Sort topics by frequency
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            
            return [{"topic": topic, "frequency": count} for topic, count in sorted_topics if count > 0]
            
        except Exception as e:
            logger.error(f"Error analyzing topics: {str(e)}")
            return []