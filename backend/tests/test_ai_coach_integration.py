"""
Integration Tests for AI Coach Service

This module contains integration tests for AI coaching workflows,
including chat functionality, suggestions, insights, and conversation management.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from app.services.ai_coach_service import AICoachService
from app.schemas.ai_conversation import ChatRequest, ChatResponse


class TestAICoachServiceIntegration:
    """Integration test cases for AI Coach Service."""
    
    @pytest.fixture
    async def ai_coach_service(self, db_session):
        """Create AI coach service instance for testing."""
        return AICoachService(db_session)
    
    @pytest.fixture
    def mock_user_context(self):
        """Mock user context for testing."""
        return {
            "user_id": 1,
            "baseline_footprint": 8000,
            "current_streak": 5,
            "total_co2_saved": 25.5,
            "eco_score": 150,
            "recent_habits": 3,
            "goals": ["reduce_transport", "energy_efficiency"],
            "location": "San Francisco, CA"
        }
    
    @pytest.fixture
    def mock_habit_data(self):
        """Mock habit data for testing."""
        return [
            {
                "category": "transport",
                "quantity": 10.0,
                "co2_saved": 2.3,
                "logged_date": datetime.utcnow().date()
            },
            {
                "category": "energy",
                "quantity": 5.0,
                "co2_saved": 1.8,
                "logged_date": datetime.utcnow().date()
            }
        ]
    
    async def test_process_chat_message_success(self, ai_coach_service, mock_user_context):
        """Test successful chat message processing."""
        # Arrange
        user_id = 1
        message = "How can I reduce my carbon footprint from transportation?"
        
        with patch.object(ai_coach_service, '_get_user_context', return_value=mock_user_context):
            with patch.object(ai_coach_service.langchain_manager, 'process_conversation') as mock_process:
                mock_process.return_value = "Great question! Here are some transportation tips..."
                
                with patch.object(ai_coach_service.conversation_manager, 'store_conversation') as mock_store:
                    mock_store.return_value = True
                    
                    # Act
                    response = await ai_coach_service.process_chat_message(
                        user_id=user_id,
                        message=message
                    )
                    
                    # Assert
                    assert isinstance(response, ChatResponse)
                    assert response.response == "Great question! Here are some transportation tips..."
                    assert response.model_used == "gpt-3.5-turbo"
                    assert response.processing_time_ms > 0
                    
                    # Verify LangChain was called with correct parameters
                    mock_process.assert_called_once()
                    call_args = mock_process.call_args
                    assert call_args[1]["user_message"] == message
                    assert call_args[1]["user_context"] == mock_user_context
                    
                    # Verify conversation was stored
                    mock_store.assert_called_once()
    
    async def test_process_chat_message_with_history(self, ai_coach_service, mock_user_context):
        """Test chat message processing with conversation history."""
        # Arrange
        user_id = 1
        message = "What about energy efficiency?"
        session_id = "test-session-123"
        
        mock_history = [
            {"type": "user", "content": "How can I reduce my footprint?"},
            {"type": "assistant", "content": "Here are some suggestions..."}
        ]
        
        with patch.object(ai_coach_service, '_get_user_context', return_value=mock_user_context):
            with patch.object(ai_coach_service, '_get_recent_conversation_history', return_value=mock_history):
                with patch.object(ai_coach_service.langchain_manager, 'process_conversation') as mock_process:
                    mock_process.return_value = "For energy efficiency, try these tips..."
                    
                    with patch.object(ai_coach_service.conversation_manager, 'store_conversation') as mock_store:
                        mock_store.return_value = True
                        
                        # Act
                        response = await ai_coach_service.process_chat_message(
                            user_id=user_id,
                            message=message,
                            session_id=session_id,
                            include_history=True
                        )
                        
                        # Assert
                        assert response.session_id == session_id
                        
                        # Verify history was included
                        call_args = mock_process.call_args
                        assert call_args[1]["conversation_history"] == mock_history
    
    async def test_process_chat_message_error_handling(self, ai_coach_service):
        """Test chat message processing error handling."""
        # Arrange
        user_id = 1
        message = "Test message"
        
        with patch.object(ai_coach_service, '_get_user_context', side_effect=Exception("Database error")):
            # Act
            response = await ai_coach_service.process_chat_message(
                user_id=user_id,
                message=message
            )
            
            # Assert
            assert "apologize" in response.response.lower()
            assert response.model_used == "fallback"
            assert response.processing_time_ms == 0
    
    async def test_generate_personalized_suggestions(self, ai_coach_service, mock_user_context, mock_habit_data):
        """Test personalized suggestion generation."""
        # Arrange
        user_id = 1
        focus_area = "transport"
        
        mock_footprint_analysis = {
            "total_activities": 15,
            "co2_saved_total": 45.2,
            "most_active_category": "transport",
            "improvement_trend": "improving"
        }
        
        mock_ai_suggestions = """1. Use public transportation for daily commute
2. Try carpooling with colleagues
3. Walk or bike for trips under 2 miles
4. Consider electric vehicle for next car purchase
5. Combine errands into single trips"""
        
        with patch.object(ai_coach_service, '_get_user_context', return_value=mock_user_context):
            with patch.object(ai_coach_service.habit_repository, 'get_user_habits_summary', return_value=mock_habit_data):
                with patch.object(ai_coach_service, '_analyze_user_footprint', return_value=mock_footprint_analysis):
                    with patch.object(ai_coach_service.langchain_manager, 'process_conversation', return_value=mock_ai_suggestions):
                        
                        # Act
                        suggestions = await ai_coach_service.generate_personalized_suggestions(
                            user_id=user_id,
                            focus_area=focus_area,
                            limit=5
                        )
                        
                        # Assert
                        assert len(suggestions) == 5
                        assert all("title" in suggestion for suggestion in suggestions)
                        assert all("category" in suggestion for suggestion in suggestions)
                        assert all("estimated_co2_savings" in suggestion for suggestion in suggestions)
                        
                        # Check that suggestions are transport-focused
                        transport_suggestions = [s for s in suggestions if "transport" in s.get("title", "").lower() or "car" in s.get("title", "").lower()]
                        assert len(transport_suggestions) > 0
    
    async def test_generate_personalized_suggestions_fallback(self, ai_coach_service):
        """Test fallback suggestions when AI generation fails."""
        # Arrange
        user_id = 1
        focus_area = "energy"
        
        with patch.object(ai_coach_service, '_get_user_context', side_effect=Exception("AI service unavailable")):
            # Act
            suggestions = await ai_coach_service.generate_personalized_suggestions(
                user_id=user_id,
                focus_area=focus_area,
                limit=3
            )
            
            # Assert
            assert len(suggestions) <= 3
            assert all("title" in suggestion for suggestion in suggestions)
            
            # Check that energy-focused suggestions are returned
            energy_suggestions = [s for s in suggestions if s.get("category") == "energy"]
            assert len(energy_suggestions) > 0
    
    async def test_generate_carbon_insights(self, ai_coach_service, mock_user_context):
        """Test carbon footprint insights generation."""
        # Arrange
        user_id = 1
        time_period = 30
        
        mock_habit_trends = {
            "total_habits": 25,
            "avg_daily_habits": 0.83,
            "top_categories": ["transport", "energy"],
            "trend_direction": "improving"
        }
        
        mock_ai_insights = """Your carbon footprint analysis shows great progress! 
        Key observations:
        1. 15% reduction in transport emissions
        2. Consistent energy-saving habits
        3. Room for improvement in diet choices
        
        Recommendations for next 30 days:
        - Continue current transport habits
        - Focus on reducing food waste
        - Consider renewable energy options"""
        
        with patch.object(ai_coach_service, '_get_user_context', return_value=mock_user_context):
            with patch.object(ai_coach_service.habit_repository, 'get_user_habit_trends', return_value=mock_habit_trends):
                with patch.object(ai_coach_service.langchain_manager, 'process_conversation', return_value=mock_ai_insights):
                    with patch.object(ai_coach_service, 'generate_personalized_suggestions', return_value=[]):
                        
                        # Act
                        insights = await ai_coach_service.generate_carbon_insights(
                            user_id=user_id,
                            time_period=time_period
                        )
                        
                        # Assert
                        assert insights["user_id"] == user_id
                        assert insights["analysis_period_days"] == time_period
                        assert "generated_at" in insights
                        assert "insights" in insights
                        assert "trends" in insights
                        assert "recommendations" in insights
                        
                        # Check insights structure
                        parsed_insights = insights["insights"]
                        assert "summary" in parsed_insights
                        assert "full_analysis" in parsed_insights
                        assert "key_points" in parsed_insights
                        assert "confidence_score" in parsed_insights
    
    async def test_search_similar_conversations(self, ai_coach_service):
        """Test similar conversation search functionality."""
        # Arrange
        query = "reduce transportation emissions"
        user_id = 1
        
        mock_similar_conversations = [
            {
                "id": 1,
                "content": "How can I reduce my car usage?",
                "similarity": 0.85,
                "timestamp": datetime.utcnow(),
                "type": "user"
            },
            {
                "id": 2,
                "content": "Try using public transportation more often",
                "similarity": 0.78,
                "timestamp": datetime.utcnow(),
                "type": "assistant"
            }
        ]
        
        with patch.object(ai_coach_service.conversation_manager, 'find_similar_conversations', return_value=mock_similar_conversations):
            # Act
            results = await ai_coach_service.search_similar_conversations(
                query=query,
                user_id=user_id,
                limit=5
            )
            
            # Assert
            assert len(results) == 2
            assert all("conversation_id" in result for result in results)
            assert all("content" in result for result in results)
            assert all("similarity_score" in result for result in results)
            
            # Check similarity scores are in correct range
            for result in results:
                assert 0 <= result["similarity_score"] <= 1
    
    async def test_get_conversation_history(self, ai_coach_service):
        """Test conversation history retrieval."""
        # Arrange
        user_id = 1
        session_id = "test-session"
        
        mock_conversations = [
            {
                "id": 1,
                "type": "user",
                "content": "Hello, I need help with my carbon footprint",
                "timestamp": datetime.utcnow()
            },
            {
                "id": 2,
                "type": "assistant",
                "content": "I'd be happy to help! What area would you like to focus on?",
                "timestamp": datetime.utcnow()
            }
        ]
        
        with patch.object(ai_coach_service.ai_conversation_repository, 'get_user_conversations', return_value=mock_conversations):
            # Act
            history = await ai_coach_service.get_conversation_history(
                user_id=user_id,
                session_id=session_id,
                limit=20
            )
            
            # Assert
            assert len(history) == 2
            assert history == mock_conversations
    
    async def test_user_context_generation(self, ai_coach_service):
        """Test user context generation for AI coaching."""
        # Arrange
        user_id = 1
        
        mock_user = Mock()
        mock_user.baseline_footprint = 8500
        mock_user.current_streak = 7
        mock_user.total_co2_saved = 32.1
        mock_user.eco_score = 180
        
        mock_recent_habits = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        with patch.object(ai_coach_service.user_repository, 'get_by_id', return_value=mock_user):
            with patch.object(ai_coach_service.habit_repository, 'get_user_recent_habits', return_value=mock_recent_habits):
                
                # Act
                context = await ai_coach_service._get_user_context(user_id)
                
                # Assert
                assert context["user_id"] == user_id
                assert context["baseline_footprint"] == 8500
                assert context["current_streak"] == 7
                assert context["total_co2_saved"] == 32.1
                assert context["eco_score"] == 180
                assert context["recent_habits"] == 3
                assert "goals" in context
                assert "location" in context
    
    async def test_user_context_generation_no_user(self, ai_coach_service):
        """Test user context generation when user not found."""
        # Arrange
        user_id = 999
        
        with patch.object(ai_coach_service.user_repository, 'get_by_id', return_value=None):
            # Act
            context = await ai_coach_service._get_user_context(user_id)
            
            # Assert
            assert context["user_id"] == user_id
            assert context["baseline_footprint"] == "Unknown"
    
    async def test_footprint_analysis(self, ai_coach_service):
        """Test user footprint analysis functionality."""
        # Arrange
        user_id = 1
        
        mock_habit_stats = {
            "total_habits": 42,
            "total_co2_saved": 125.7,
            "top_category": "transport",
            "avg_daily_habits": 1.4
        }
        
        with patch.object(ai_coach_service.habit_repository, 'get_user_habit_statistics', return_value=mock_habit_stats):
            # Act
            analysis = await ai_coach_service._analyze_user_footprint(user_id)
            
            # Assert
            assert analysis["total_activities"] == 42
            assert analysis["co2_saved_total"] == 125.7
            assert analysis["most_active_category"] == "transport"
            assert "improvement_trend" in analysis
    
    async def test_ai_suggestions_parsing(self, ai_coach_service):
        """Test parsing of AI-generated suggestions."""
        # Arrange
        ai_response = """1. Walk or bike for short trips under 2 miles
This can save approximately 2.3 kg CO2 per week

2. Use public transportation for daily commute
Switching from car to bus/train can reduce emissions by 45%

3. Adjust thermostat by 2 degrees
Lower heating in winter, raise cooling in summer

4. Try one meatless day per week
Plant-based meals have 50% lower carbon footprint

5. Combine errands into single trips
Reduces unnecessary driving and fuel consumption"""
        
        # Act
        suggestions = ai_coach_service._parse_ai_suggestions(ai_response, limit=5)
        
        # Assert
        assert len(suggestions) == 5
        
        # Check first suggestion
        first_suggestion = suggestions[0]
        assert "Walk or bike for short trips under 2 miles" in first_suggestion["title"]
        assert "description" in first_suggestion
        assert "category" in first_suggestion
        assert "estimated_co2_savings" in first_suggestion
        assert "difficulty" in first_suggestion
        assert "timeframe" in first_suggestion
    
    async def test_ai_insights_parsing(self, ai_coach_service):
        """Test parsing of AI-generated insights."""
        # Arrange
        ai_response = """Your carbon footprint analysis shows excellent progress over the past 30 days!

Key observations:
1. 20% reduction in transportation emissions
2. Consistent energy-saving habits established
3. Significant improvement in waste reduction
4. Room for growth in dietary choices

Your current trajectory suggests you'll exceed your annual CO2 reduction goal by 15%. 
Keep up the great work with your sustainable transportation choices!

Recommendations for continued success:
- Maintain current public transit usage
- Consider expanding to 2 meatless days per week
- Look into renewable energy options for your home"""
        
        # Act
        insights = ai_coach_service._parse_ai_insights(ai_response)
        
        # Assert
        assert "summary" in insights
        assert "full_analysis" in insights
        assert "key_points" in insights
        assert "confidence_score" in insights
        
        # Check summary is truncated appropriately
        assert len(insights["summary"]) <= 203  # 200 + "..."
        
        # Check full analysis is preserved
        assert insights["full_analysis"] == ai_response
        
        # Check key points extraction
        key_points = insights["key_points"]
        assert len(key_points) > 0
        assert any("20% reduction" in point for point in key_points)
    
    async def test_fallback_suggestions_by_category(self, ai_coach_service):
        """Test fallback suggestions filtered by category."""
        # Act - Test different categories
        transport_suggestions = ai_coach_service._get_fallback_suggestions("transport", 3)
        energy_suggestions = ai_coach_service._get_fallback_suggestions("energy", 3)
        diet_suggestions = ai_coach_service._get_fallback_suggestions("diet", 3)
        
        # Assert
        assert len(transport_suggestions) <= 3
        assert len(energy_suggestions) <= 3
        assert len(diet_suggestions) <= 3
        
        # Check category filtering
        transport_categories = [s["category"] for s in transport_suggestions]
        assert "transport" in transport_categories
        
        energy_categories = [s["category"] for s in energy_suggestions]
        assert "energy" in energy_categories
        
        diet_categories = [s["category"] for s in diet_suggestions]
        assert "diet" in diet_categories
    
    async def test_key_points_extraction(self, ai_coach_service):
        """Test extraction of key points from AI analysis."""
        # Arrange
        text_with_numbered_list = """Analysis summary:

1. Transportation emissions decreased by 25%
2. Energy usage patterns show improvement
3. Waste reduction efforts are paying off
4. Diet changes needed for further progress
5. Overall trend is very positive

Additional context and recommendations follow..."""
        
        text_with_bullets = """Key findings:

- Significant progress in sustainable transport
- Energy efficiency measures working well
- Food waste reduction showing results
• Consider expanding plant-based meals
• Look into renewable energy options"""
        
        # Act
        numbered_points = ai_coach_service._extract_key_points(text_with_numbered_list)
        bullet_points = ai_coach_service._extract_key_points(text_with_bullets)
        
        # Assert
        assert len(numbered_points) == 5
        assert all(point.startswith(('1.', '2.', '3.', '4.', '5.')) for point in numbered_points)
        
        assert len(bullet_points) == 5
        assert all(point.startswith(('-', '•')) for point in bullet_points)


class TestAICoachEndpointIntegration:
    """Integration tests for AI Coach API endpoints."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user for endpoint testing."""
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        return user
    
    async def test_chat_endpoint_integration(self, client, mock_current_user):
        """Test chat endpoint integration."""
        # This would require setting up the full FastAPI test client
        # and mocking authentication. For now, we'll test the service layer.
        pass
    
    async def test_suggestions_endpoint_integration(self, client, mock_current_user):
        """Test suggestions endpoint integration."""
        # This would require setting up the full FastAPI test client
        # and mocking authentication. For now, we'll test the service layer.
        pass
    
    async def test_insights_endpoint_integration(self, client, mock_current_user):
        """Test insights endpoint integration."""
        # This would require setting up the full FastAPI test client
        # and mocking authentication. For now, we'll test the service layer.
        pass


@pytest.mark.asyncio
class TestAICoachWorkflowScenarios:
    """End-to-end workflow scenario tests."""
    
    async def test_complete_coaching_session_workflow(self, ai_coach_service):
        """Test a complete AI coaching session workflow."""
        # This test would simulate a full user interaction:
        # 1. User starts chat session
        # 2. AI provides personalized advice
        # 3. User asks follow-up questions
        # 4. AI generates insights based on conversation
        # 5. User rates the conversation
        
        # For now, this is a placeholder for the full workflow test
        assert True
    
    async def test_multi_session_context_preservation(self, ai_coach_service):
        """Test that context is preserved across multiple sessions."""
        # This test would verify that the AI coach remembers
        # previous conversations and builds on them appropriately
        
        # For now, this is a placeholder for the context preservation test
        assert True
    
    async def test_personalization_improvement_over_time(self, ai_coach_service):
        """Test that AI coaching becomes more personalized over time."""
        # This test would verify that as more user data is collected,
        # the AI provides increasingly personalized and relevant advice
        
        # For now, this is a placeholder for the personalization test
        assert True