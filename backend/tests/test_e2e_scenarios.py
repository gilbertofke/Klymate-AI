"""
End-to-End Test Scenarios - Task 10 Implementation

This module contains comprehensive end-to-end test scenarios that validate
critical user journeys and system integration points.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import TestHelper, APITestHelper, DatabaseTestHelper
from tests.fixtures import TestDataGenerator


class TestUserJourneyE2E:
    """End-to-end tests for complete user journeys."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_user_onboarding_journey(
        self,
        client: TestClient,
        isolated_db_session: AsyncSession,
        test_data_generator: TestDataGenerator
    ):
        """Test complete user onboarding from registration to first habit."""
        api_helper = APITestHelper()
        
        # Step 1: User registration
        registration_data = test_data_generator.generate_user_data(
            email="newuser@example.com",
            name="New User"
        )
        
        response = client.post("/api/v1/auth/register", json=registration_data)
        api_helper.assert_api_response(response, 201, expected_keys=["id", "email"])
        user_data = response.json()
        
        # Step 2: Complete onboarding survey
        onboarding_data = {
            "baseline_footprint": 12000.0,
            "goals": ["reduce_transport", "save_energy"],
            "preferences": {"notifications": True}
        }
        
        headers = api_helper.create_test_headers(user_data)
        response = client.post(
            f"/api/v1/users/{user_data['id']}/onboarding",
            json=onboarding_data,
            headers=headers
        )
        api_helper.assert_api_response(response, 200)
        
        # Step 3: Log first habit
        habit_data = test_data_generator.generate_habit_data(
            category_id=1,
            quantity=5.0,
            notes="My first eco-friendly habit!"
        )
        
        response = client.post("/api/v1/habits", json=habit_data, headers=headers)
        api_helper.assert_api_response(response, 201, expected_keys=["id", "co2_saved"])
        
        # Step 4: Check dashboard reflects the changes
        response = client.get("/api/v1/analytics/dashboard", headers=headers)
        api_helper.assert_api_response(response, 200, expected_keys=["overview", "trends"])
        
        dashboard = response.json()
        assert dashboard["overview"]["total_habits"] >= 1
        assert dashboard["overview"]["total_co2_saved"] > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ai_coaching_conversation_flow(
        self,
        client: TestClient,
        seeded_db_session: tuple[AsyncSession, Dict[str, Any]],
        mock_external_services: Dict[str, Any]
    ):
        """Test complete AI coaching conversation flow."""
        session, test_data = seeded_db_session
        api_helper = APITestHelper()
        
        user = test_data["users"][0]
        headers = api_helper.create_test_headers({"id": user.id, "email": user.email})
        
        # Step 1: Start conversation
        chat_data = {
            "message": "How can I reduce my carbon footprint?",
            "session_id": "test_session_123"
        }
        
        response = client.post("/api/v1/ai/chat", json=chat_data, headers=headers)
        api_helper.assert_api_response(response, 200, expected_keys=["response", "session_id"])
        
        # Step 2: Continue conversation
        follow_up_data = {
            "message": "What about transportation habits?",
            "session_id": "test_session_123"
        }
        
        response = client.post("/api/v1/ai/chat", json=follow_up_data, headers=headers)
        api_helper.assert_api_response(response, 200)
        
        # Step 3: Get conversation history
        response = client.get("/api/v1/ai/history?session_id=test_session_123", headers=headers)
        api_helper.assert_api_response(response, 200)
        
        history = response.json()
        assert len(history.get("conversations", [])) >= 2
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_gamification_badge_earning_flow(
        self,
        client: TestClient,
        seeded_db_session: tuple[AsyncSession, Dict[str, Any]]
    ):
        """Test badge earning through habit logging."""
        session, test_data = seeded_db_session
        api_helper = APITestHelper()
        
        user = test_data["users"][0]
        headers = api_helper.create_test_headers({"id": user.id, "email": user.email})
        
        # Step 1: Check initial badges
        response = client.get("/api/v1/gamification/badges", headers=headers)
        api_helper.assert_api_response(response, 200)
        initial_badges = response.json()
        
        # Step 2: Log multiple habits to trigger badge
        for i in range(5):
            habit_data = {
                "category_id": 1,
                "quantity": 2.0,
                "notes": f"Habit {i+1} for badge earning"
            }
            response = client.post("/api/v1/habits", json=habit_data, headers=headers)
            api_helper.assert_api_response(response, 201)
        
        # Step 3: Check if badges were awarded
        response = client.get("/api/v1/gamification/badges", headers=headers)
        api_helper.assert_api_response(response, 200)
        updated_badges = response.json()
        
        # Should have more earned badges
        initial_earned = sum(1 for badge in initial_badges if badge.get("is_earned"))
        updated_earned = sum(1 for badge in updated_badges if badge.get("is_earned"))
        assert updated_earned >= initial_earned
        
        # Step 4: Check leaderboard position
        response = client.get("/api/v1/gamification/leaderboard", headers=headers)
        api_helper.assert_api_response(response, 200, expected_keys=["entries"])


class TestSystemIntegrationE2E:
    """End-to-end tests for system integration points."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analytics_caching_integration(
        self,
        client: TestClient,
        seeded_db_session: tuple[AsyncSession, Dict[str, Any]],
        mock_external_services: Dict[str, Any]
    ):
        """Test analytics with caching integration."""
        session, test_data = seeded_db_session
        api_helper = APITestHelper()
        
        user = test_data["users"][0]
        headers = api_helper.create_test_headers({"id": user.id, "email": user.email})
        
        # First request - should hit database
        response1 = client.get("/api/v1/analytics/dashboard", headers=headers)
        api_helper.assert_api_response(response1, 200)
        
        # Second request - should hit cache
        response2 = client.get("/api/v1/analytics/dashboard", headers=headers)
        api_helper.assert_api_response(response2, 200)
        
        # Responses should be identical
        assert response1.json() == response2.json()
        
        # Log new habit - should invalidate cache
        habit_data = {"category_id": 1, "quantity": 3.0, "notes": "Cache invalidation test"}
        response = client.post("/api/v1/habits", json=habit_data, headers=headers)
        api_helper.assert_api_response(response, 201)
        
        # Next request should show updated data
        response3 = client.get("/api/v1/analytics/dashboard", headers=headers)
        api_helper.assert_api_response(response3, 200)
        
        # Should have different data after habit logging
        dashboard3 = response3.json()
        dashboard1 = response1.json()
        assert dashboard3["overview"]["total_habits"] > dashboard1["overview"]["total_habits"]


class TestErrorHandlingE2E:
    """End-to-end tests for error handling scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_authentication_error_handling(self, client: TestClient):
        """Test authentication error handling across endpoints."""
        api_helper = APITestHelper()
        
        # Test unauthenticated requests
        protected_endpoints = [
            ("/api/v1/habits", "POST", {"category_id": 1, "quantity": 1.0}),
            ("/api/v1/analytics/dashboard", "GET", None),
            ("/api/v1/gamification/badges", "GET", None),
            ("/api/v1/ai/chat", "POST", {"message": "test"})
        ]
        
        for endpoint, method, data in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=data)
            
            api_helper.assert_api_response(response, 401, expected_error="authentication")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_validation_error_handling(
        self,
        client: TestClient,
        seeded_db_session: tuple[AsyncSession, Dict[str, Any]]
    ):
        """Test validation error handling."""
        session, test_data = seeded_db_session
        api_helper = APITestHelper()
        
        user = test_data["users"][0]
        headers = api_helper.create_test_headers({"id": user.id, "email": user.email})
        
        # Test invalid habit data
        invalid_habit_data = [
            {"category_id": -1, "quantity": 1.0},  # Invalid category
            {"category_id": 1, "quantity": -1.0},  # Negative quantity
            {"category_id": 1},  # Missing quantity
            {"quantity": 1.0}  # Missing category
        ]
        
        for data in invalid_habit_data:
            response = client.post("/api/v1/habits", json=data, headers=headers)
            api_helper.assert_api_response(response, 422)  # Validation error


class TestPerformanceE2E:
    """End-to-end performance tests."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_requests_handling(
        self,
        client: TestClient,
        seeded_db_session: tuple[AsyncSession, Dict[str, Any]]
    ):
        """Test system handles concurrent requests properly."""
        session, test_data = seeded_db_session
        api_helper = APITestHelper()
        
        user = test_data["users"][0]
        headers = api_helper.create_test_headers({"id": user.id, "email": user.email})
        
        # Make multiple concurrent requests
        import concurrent.futures
        import threading
        
        def make_request():
            return client.get("/api/v1/analytics/dashboard", headers=headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            api_helper.assert_api_response(response, 200)
        
        # All responses should be consistent
        first_response_data = responses[0].json()
        for response in responses[1:]:
            assert response.json() == first_response_data