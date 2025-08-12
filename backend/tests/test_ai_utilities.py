"""
Tests for AI Utilities and Vector Operations

This module contains unit tests for AI coaching infrastructure,
including LangChain integration, OpenAI API operations, and vector embeddings.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any
import numpy as np

from app.utils.ai_utilities import (
    OpenAIEmbeddingGenerator,
    LangChainManager,
    VectorOperations,
    AIConversationManager
)
from app.models.ai_conversation import AIConversation


class TestOpenAIEmbeddingGenerator:
    """Test cases for OpenAI embedding generation."""
    
    @pytest.fixture
    def embedding_generator(self):
        """Create embedding generator instance for testing."""
        return OpenAIEmbeddingGenerator()
    
    @patch('app.utils.ai_utilities.OpenAI')
    async def test_generate_embedding_success(self, mock_openai, embedding_generator):
        """Test successful embedding generation."""
        # Arrange
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        
        text = "Test text for embedding"
        
        # Act
        result = await embedding_generator.generate_embedding(text)
        
        # Assert
        assert result == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=text
        )
    
    @patch('app.utils.ai_utilities.OpenAI')
    async def test_generate_embedding_failure(self, mock_openai, embedding_generator):
        """Test embedding generation failure handling."""
        # Arrange
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        text = "Test text for embedding"
        
        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            await embedding_generator.generate_embedding(text)
    
    async def test_generate_batch_embeddings(self, embedding_generator):
        """Test batch embedding generation."""
        # Arrange
        texts = ["Text 1", "Text 2", "Text 3"]
        
        with patch.object(embedding_generator, 'generate_embedding') as mock_generate:
            mock_generate.side_effect = [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
                [0.7, 0.8, 0.9]
            ]
            
            # Act
            results = await embedding_generator.generate_batch_embeddings(texts)
            
            # Assert
            assert len(results) == 3
            assert results[0] == [0.1, 0.2, 0.3]
            assert results[1] == [0.4, 0.5, 0.6]
            assert results[2] == [0.7, 0.8, 0.9]
            assert mock_generate.call_count == 3


class TestLangChainManager:
    """Test cases for LangChain integration."""
    
    @pytest.fixture
    def langchain_manager(self):
        """Create LangChain manager instance for testing."""
        return LangChainManager()
    
    @patch('app.utils.ai_utilities.ChatOpenAI')
    async def test_initialize_chat_model(self, mock_chat_openai, langchain_manager):
        """Test chat model initialization."""
        # Arrange
        mock_model = Mock()
        mock_chat_openai.return_value = mock_model
        
        # Act
        result = langchain_manager.initialize_chat_model()
        
        # Assert
        assert result == mock_model
        mock_chat_openai.assert_called_once_with(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
    
    @patch('app.utils.ai_utilities.ChatPromptTemplate')
    async def test_create_coaching_prompt(self, mock_prompt_template, langchain_manager):
        """Test coaching prompt creation."""
        # Arrange
        mock_template = Mock()
        mock_prompt_template.from_messages.return_value = mock_template
        
        user_context = {"name": "John", "goals": ["reduce_transport"]}
        
        # Act
        result = langchain_manager.create_coaching_prompt(user_context)
        
        # Assert
        assert result == mock_template
        mock_prompt_template.from_messages.assert_called_once()
    
    async def test_process_conversation(self, langchain_manager):
        """Test conversation processing."""
        # Arrange
        user_message = "How can I reduce my carbon footprint?"
        user_context = {"baseline_footprint": 8000}
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value={"text": "AI response"})
        
        with patch.object(langchain_manager, '_create_conversation_chain', return_value=mock_chain):
            # Act
            result = await langchain_manager.process_conversation(user_message, user_context)
            
            # Assert
            assert result == "AI response"
            mock_chain.ainvoke.assert_called_once()


class TestVectorOperations:
    """Test cases for vector operations."""
    
    @pytest.fixture
    def vector_ops(self):
        """Create vector operations instance for testing."""
        return VectorOperations()
    
    def test_calculate_cosine_similarity(self, vector_ops):
        """Test cosine similarity calculation."""
        # Arrange
        vector1 = [1.0, 0.0, 0.0]
        vector2 = [0.0, 1.0, 0.0]
        vector3 = [1.0, 0.0, 0.0]
        
        # Act
        similarity_orthogonal = vector_ops.calculate_cosine_similarity(vector1, vector2)
        similarity_identical = vector_ops.calculate_cosine_similarity(vector1, vector3)
        
        # Assert
        assert abs(similarity_orthogonal - 0.0) < 1e-6
        assert abs(similarity_identical - 1.0) < 1e-6
    
    def test_find_similar_vectors(self, vector_ops):
        """Test finding similar vectors."""
        # Arrange
        query_vector = [1.0, 0.0, 0.0]
        vector_database = [
            {"id": 1, "vector": [1.0, 0.0, 0.0], "content": "Identical"},
            {"id": 2, "vector": [0.8, 0.6, 0.0], "content": "Similar"},
            {"id": 3, "vector": [0.0, 1.0, 0.0], "content": "Different"}
        ]
        
        # Act
        results = vector_ops.find_similar_vectors(query_vector, vector_database, top_k=2)
        
        # Assert
        assert len(results) == 2
        assert results[0]["id"] == 1  # Most similar
        assert results[1]["id"] == 2  # Second most similar
        assert results[0]["similarity"] > results[1]["similarity"]
    
    def test_normalize_vector(self, vector_ops):
        """Test vector normalization."""
        # Arrange
        vector = [3.0, 4.0, 0.0]
        
        # Act
        normalized = vector_ops.normalize_vector(vector)
        
        # Assert
        magnitude = sum(x**2 for x in normalized)**0.5
        assert abs(magnitude - 1.0) < 1e-6
        assert abs(normalized[0] - 0.6) < 1e-6
        assert abs(normalized[1] - 0.8) < 1e-6


class TestAIConversationManager:
    """Test cases for AI conversation management."""
    
    @pytest.fixture
    def conversation_manager(self):
        """Create conversation manager instance for testing."""
        mock_db = Mock()
        return AIConversationManager(mock_db)
    
    async def test_store_conversation(self, conversation_manager):
        """Test conversation storage."""
        # Arrange
        user_id = 1
        user_message = "Hello"
        ai_response = "Hi there!"
        
        with patch.object(conversation_manager, 'embedding_generator') as mock_embedder:
            mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3]
            
            # Act
            result = await conversation_manager.store_conversation(
                user_id, user_message, ai_response
            )
            
            # Assert
            assert result is True
            assert mock_embedder.generate_embedding.call_count == 2
    
    async def test_get_conversation_history(self, conversation_manager):
        """Test conversation history retrieval."""
        # Arrange
        user_id = 1
        limit = 10
        
        mock_conversations = [
            Mock(id=1, content="Message 1", message_type="user"),
            Mock(id=2, content="Response 1", message_type="assistant")
        ]
        
        with patch.object(conversation_manager.repository, 'get_user_conversations') as mock_get:
            mock_get.return_value = mock_conversations
            
            # Act
            result = await conversation_manager.get_conversation_history(user_id, limit)
            
            # Assert
            assert len(result) == 2
            mock_get.assert_called_once_with(user_id, limit)
    
    async def test_find_similar_conversations(self, conversation_manager):
        """Test finding similar conversations."""
        # Arrange
        query = "How to reduce emissions?"
        user_id = 1
        
        with patch.object(conversation_manager, 'embedding_generator') as mock_embedder:
            mock_embedder.generate_embedding.return_value = [0.1, 0.2, 0.3]
            
            with patch.object(conversation_manager.repository, 'search_similar_conversations') as mock_search:
                mock_search.return_value = [
                    Mock(content="Similar conversation", similarity=0.9)
                ]
                
                # Act
                result = await conversation_manager.find_similar_conversations(query, user_id)
                
                # Assert
                assert len(result) == 1
                mock_embedder.generate_embedding.assert_called_once_with(query)
                mock_search.assert_called_once()


@pytest.mark.asyncio
class TestIntegrationScenarios:
    """Integration test scenarios for AI utilities."""
    
    async def test_full_ai_coaching_workflow(self):
        """Test complete AI coaching workflow."""
        # This would be an integration test that combines all components
        # For now, we'll create a placeholder that shows the expected flow
        
        # Arrange
        user_id = 1
        user_message = "I want to reduce my carbon footprint"
        user_context = {"baseline_footprint": 8000, "goals": ["transport"]}
        
        # Act & Assert
        # 1. Generate embedding for user message
        # 2. Find similar past conversations
        # 3. Process message through LangChain
        # 4. Generate AI response
        # 5. Store conversation with embeddings
        # 6. Return response to user
        
        # This test would verify the entire pipeline works together
        assert True  # Placeholder for actual integration test