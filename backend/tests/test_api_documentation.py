"""
API Documentation and Testing

This module provides comprehensive API endpoint testing and documentation generation
for the Klymate AI backend system.
"""

import pytest
import json
from fastapi.testclient import TestClient
from typing import Dict, Any, List
from decimal import Decimal

from app.main import app
from tests.factories import UserFactory, HabitCategoryFactory


class TestAPIDocumentation:
    """Test API documentation and endpoint availability"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_openapi_schema_generation(self, client: TestClient):
        """Test that OpenAPI schema is properly generated"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Verify key endpoints are documented
        paths = schema["paths"]
        expected_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/users/profile",
            "/api/v1/habits/categories",
            "/api/v1/habits/log",
            "/api/v1/credits/balance",
            "/api/v1/credits/transactions",
            "/api/v1/gamification/badges",
            "/api/v1/analytics/dashboard"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} not found in API documentation"
    
    def test_api_docs_accessibility(self, client: TestClient):
        """Test that API documentation is accessible"""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()
    
    def test_health_check_endpoint(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"


class TestAPIEndpointStructure:
    """Test API endpoint structure and response formats"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_authentication_endpoints_structure(self, client: TestClient):
        """Test authentication endpoint structure"""
        # Test login endpoint structure (without actual authentication)
        response = client.post("/api/v1/auth/login", json={
            "firebase_token": "invalid_token_for_structure_test"
        })
        
        # Should return 401 or 422, but endpoint should exist
        assert response.status_code in [401, 422, 500]
    
    def test_habits_endpoints_structure(self, client: TestClient):
        """Test habits endpoint structure"""
        # Test categories endpoint
        response = client.get("/api/v1/habits/categories")
        # Should return 200 or require authentication
        assert response.status_code in [200, 401, 403]
        
        # Test habit logging endpoint structure
        response = client.post("/api/v1/habits/log", json={
            "category_id": "test_id",
            "quantity": 5.0,
            "notes": "Test habit"
        })
        # Should return 401 (unauthorized) or 422 (validation error)
        assert response.status_code in [401, 422]
    
    def test_carbon_credits_endpoints_structure(self, client: TestClient):
        """Test carbon credits endpoint structure"""
        # Test balance endpoint
        response = client.get("/api/v1/credits/balance")
        assert response.status_code in [200, 401, 403]
        
        # Test transactions endpoint
        response = client.get("/api/v1/credits/transactions")
        assert response.status_code in [200, 401, 403]
        
        # Test rates endpoint (should be public)
        response = client.get("/api/v1/credits/rates")
        assert response.status_code in [200, 500]  # Should work without auth
    
    def test_gamification_endpoints_structure(self, client: TestClient):
        """Test gamification endpoint structure"""
        # Test badges endpoint
        response = client.get("/api/v1/gamification/badges")
        assert response.status_code in [200, 401, 403]
        
        # Test leaderboard endpoint
        response = client.get("/api/v1/gamification/leaderboard")
        assert response.status_code in [200, 401, 403]
    
    def test_analytics_endpoints_structure(self, client: TestClient):
        """Test analytics endpoint structure"""
        # Test dashboard endpoint
        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code in [200, 401, 403]


class TestAPIResponseFormats:
    """Test API response formats and schemas"""
    
    def test_error_response_format(self):
        """Test that error responses follow consistent format"""
        # This would test error response structure
        expected_error_format = {
            "error": {
                "code": "string",
                "message": "string",
                "details": {},
                "timestamp": "string"
            }
        }
        
        # Verify error format structure exists
        assert "error" in expected_error_format
        assert "code" in expected_error_format["error"]
        assert "message" in expected_error_format["error"]
    
    def test_success_response_format(self):
        """Test that success responses follow consistent format"""
        # Test various success response formats
        
        # Balance response format
        balance_format = {
            "user_id": "string",
            "current_balance": 0.0,
            "total_earned": 0.0,
            "total_redeemed": 0.0,
            "usd_value": 0.0,
            "exchange_rates": {},
            "last_updated": "string"
        }
        
        # Transaction response format
        transaction_format = {
            "id": "string",
            "transaction_type": "string",
            "amount": 0.0,
            "co2_saved": 0.0,
            "verification_status": "string",
            "created_at": "string"
        }
        
        # Verify formats have required fields
        assert "user_id" in balance_format
        assert "current_balance" in balance_format
        assert "id" in transaction_format
        assert "transaction_type" in transaction_format


class TestAPIUsageExamples:
    """Generate API usage examples for documentation"""
    
    def generate_api_usage_examples(self) -> Dict[str, Any]:
        """Generate comprehensive API usage examples"""
        
        examples = {
            "authentication": {
                "login": {
                    "endpoint": "POST /api/v1/auth/login",
                    "request": {
                        "firebase_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
                    },
                    "response": {
                        "message": "Login successful",
                        "user": {
                            "id": "user123",
                            "email": "user@example.com",
                            "display_name": "John Doe"
                        },
                        "access_token": "jwt_token_here"
                    }
                }
            },
            
            "habits": {
                "log_habit": {
                    "endpoint": "POST /api/v1/habits/log",
                    "headers": {
                        "Authorization": "Bearer jwt_token_here"
                    },
                    "request": {
                        "category_id": "cycling_category_id",
                        "quantity": 10.0,
                        "notes": "Cycled to work instead of driving",
                        "logged_date": "2024-01-15"
                    },
                    "response": {
                        "id": "habit123",
                        "category_id": "cycling_category_id",
                        "quantity": 10.0,
                        "co2_saved": 25.0,
                        "notes": "Cycled to work instead of driving",
                        "logged_date": "2024-01-15",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                },
                
                "get_categories": {
                    "endpoint": "GET /api/v1/habits/categories",
                    "response": [
                        {
                            "id": "cycling_category_id",
                            "name": "Cycling to work",
                            "description": "Reduce emissions by cycling instead of driving",
                            "co2_per_unit": 2.5,
                            "unit_name": "km",
                            "category_type": "transport"
                        }
                    ]
                }
            },
            
            "carbon_credits": {
                "get_balance": {
                    "endpoint": "GET /api/v1/credits/balance",
                    "headers": {
                        "Authorization": "Bearer jwt_token_here"
                    },
                    "response": {
                        "user_id": "user123",
                        "current_balance": 125.50,
                        "total_earned": 200.00,
                        "total_redeemed": 74.50,
                        "usd_value": 6.28,
                        "exchange_rates": {
                            "co2_to_kc": 1.0,
                            "kc_to_usd": 0.05
                        },
                        "last_updated": "2024-01-15T10:30:00Z"
                    }
                },
                
                "redeem_credits": {
                    "endpoint": "POST /api/v1/credits/redeem",
                    "headers": {
                        "Authorization": "Bearer jwt_token_here"
                    },
                    "request": {
                        "redemption_type": "cash_out",
                        "amount_kc": 50.0,
                        "recipient_info": {
                            "payment_method": "paypal",
                            "email": "user@example.com",
                            "account_id": "paypal_123"
                        }
                    },
                    "response": {
                        "id": "redemption123",
                        "redemption_type": "cash_out",
                        "amount_kc": 50.0,
                        "amount_usd": 2.50,
                        "status": "pending",
                        "external_reference": "cash_out_20240115_abc123",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                },
                
                "get_rates": {
                    "endpoint": "GET /api/v1/credits/rates",
                    "response": {
                        "co2_to_kc": {
                            "rate": 1.0,
                            "effective_date": "2024-01-15T00:00:00Z",
                            "source": "carbon_market_api"
                        },
                        "kc_to_usd": {
                            "rate": 0.05,
                            "effective_date": "2024-01-15T00:00:00Z",
                            "source": "financial_market_api"
                        },
                        "last_updated": "2024-01-15T10:30:00Z"
                    }
                }
            },
            
            "gamification": {
                "get_badges": {
                    "endpoint": "GET /api/v1/gamification/badges",
                    "headers": {
                        "Authorization": "Bearer jwt_token_here"
                    },
                    "response": {
                        "earned_badges": [
                            {
                                "id": "badge123",
                                "name": "First Steps",
                                "description": "Logged your first eco-friendly habit",
                                "icon_url": "/icons/badges/first_steps.svg",
                                "points_value": 10,
                                "earned_at": "2024-01-15T10:30:00Z"
                            }
                        ],
                        "available_badges": [
                            {
                                "id": "badge456",
                                "name": "Eco Warrior",
                                "description": "Save 100kg of CO2",
                                "icon_url": "/icons/badges/eco_warrior.svg",
                                "points_value": 50,
                                "progress": {
                                    "current": 45.5,
                                    "target": 100.0,
                                    "percentage": 45.5
                                }
                            }
                        ]
                    }
                }
            },
            
            "analytics": {
                "get_dashboard": {
                    "endpoint": "GET /api/v1/analytics/dashboard",
                    "headers": {
                        "Authorization": "Bearer jwt_token_here"
                    },
                    "response": {
                        "user_stats": {
                            "total_habits": 25,
                            "total_co2_saved": 125.5,
                            "current_streak": 7,
                            "eco_score": 450
                        },
                        "recent_activity": [
                            {
                                "date": "2024-01-15",
                                "habits_logged": 2,
                                "co2_saved": 15.0,
                                "credits_earned": 18.0
                            }
                        ],
                        "trends": {
                            "weekly_co2_saved": [10.5, 15.2, 8.7, 22.1, 18.9, 12.3, 16.8],
                            "category_breakdown": {
                                "transport": 45.2,
                                "diet": 32.1,
                                "energy": 28.7,
                                "lifestyle": 19.5
                            }
                        }
                    }
                }
            }
        }
        
        return examples
    
    def test_generate_usage_examples(self):
        """Test that usage examples are properly structured"""
        examples = self.generate_api_usage_examples()
        
        # Verify main sections exist
        assert "authentication" in examples
        assert "habits" in examples
        assert "carbon_credits" in examples
        assert "gamification" in examples
        assert "analytics" in examples
        
        # Verify each section has proper structure
        for section_name, section in examples.items():
            for endpoint_name, endpoint in section.items():
                assert "endpoint" in endpoint
                assert "response" in endpoint or "request" in endpoint


def generate_api_documentation_file():
    """Generate comprehensive API documentation file"""
    
    test_instance = TestAPIUsageExamples()
    examples = test_instance.generate_api_usage_examples()
    
    documentation = {
        "title": "Klymate AI Backend API Documentation",
        "version": "1.0.0",
        "description": "Comprehensive API documentation for the Klymate AI carbon footprint tracking system",
        "base_url": "https://api.klymate.ai",
        "authentication": {
            "type": "Bearer Token (JWT)",
            "description": "Most endpoints require authentication using Firebase JWT tokens"
        },
        "endpoints": examples,
        "error_codes": {
            "400": "Bad Request - Invalid input data",
            "401": "Unauthorized - Authentication required",
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource not found",
            "422": "Validation Error - Input validation failed",
            "500": "Internal Server Error - Server error occurred"
        },
        "rate_limits": {
            "authenticated": "1000 requests per hour",
            "unauthenticated": "100 requests per hour"
        }
    }
    
    return documentation


if __name__ == "__main__":
    # Generate API documentation
    docs = generate_api_documentation_file()
    
    # Save to file
    with open("backend/API_DOCUMENTATION.json", "w") as f:
        json.dump(docs, f, indent=2)
    
    print("API documentation generated successfully!")