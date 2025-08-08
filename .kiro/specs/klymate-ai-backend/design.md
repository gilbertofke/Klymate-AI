# Design Document

## Overview

The Klymate AI Backend is designed as a modern, scalable FastAPI application that serves as the core engine for a carbon footprint tracking platform with AI-powered coaching. The system follows a layered architecture pattern with clear separation of concerns, leveraging TiDB as the central database for both structured data and vector operations, and integrating advanced AI capabilities through LangChain and OpenAI.

The architecture prioritizes performance, security, and maintainability while supporting rapid development within a 4-week hackathon timeline.

## Architecture

### System Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│                     (FastAPI)                              │
├─────────────────────────────────────────────────────────────┤
│                Authentication Middleware                    │
│              (Firebase Admin SDK + JWT)                    │
├─────────────────────────────────────────────────────────────┤
│                 Business Logic Layer                       │
│               (Services + Domain Logic)                    │
├─────────────────────────────────────────────────────────────┤
│                  Data Access Layer                         │
│                 (Repository Pattern)                       │
├─────────────────────────────────────────────────────────────┤
│  Caching Layer (Redis)  │    AI/ML Layer (LangChain       │
│                         │    + Vector Operations)         │
├─────────────────────────────────────────────────────────────┤
│                    Database Layer                          │
│              (TiDB + Vector Storage)                       │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **API Gateway Layer**: FastAPI application handling HTTP requests, routing, and response formatting
2. **Authentication Layer**: Firebase integration with JWT token management
3. **Business Logic Layer**: Domain services implementing core business rules
4. **Data Access Layer**: Repository pattern abstracting database operations
5. **AI/ML Layer**: LangChain orchestration with OpenAI integration
6. **Database Layer**: TiDB serving both relational and vector data needs
7. **Caching Layer**: Redis for performance optimization

## Components and Interfaces

### API Routes Structure

```python
# Authentication Routes
POST /auth/register          # User registration via Firebase
POST /auth/login            # Login with Firebase token
POST /auth/refresh          # JWT token refresh
GET  /auth/profile          # User profile retrieval

# Habit Tracking Routes
GET  /habits/categories     # List habit categories
POST /habits/log           # Log user habits
GET  /habits/history       # Retrieve habit history
GET  /habits/stats         # User statistics

# AI Coach Routes
POST /ai/chat              # Chat with AI coach
GET  /ai/suggestions       # Personalized recommendations
GET  /ai/insights          # Carbon footprint insights

# Gamification Routes
GET  /gamification/badges       # Available badges
GET  /gamification/leaderboard  # User rankings

# Analytics Routes
GET  /analytics/dashboard  # Dashboard data
GET  /analytics/trends     # Trends and comparisons
```

### Service Layer Architecture

```python
# Core Services
class UserService:
    """Handles user management and onboarding"""
    
class HabitService:
    """Manages habit tracking and carbon calculations"""
    
class AICoachService:
    """Orchestrates AI interactions and coaching"""
    
class GamificationService:
    """Handles badges, streaks, and leaderboards"""
    
class AnalyticsService:
    """Provides insights and trend analysis"""
```

### Repository Pattern

```python
# Base Repository
class BaseRepository:
    """Abstract base for all repositories"""
    
# Specific Repositories
class UserRepository(BaseRepository):
    """User data access operations"""
    
class HabitRepository(BaseRepository):
    """Habit and carbon log operations"""
    
class AIConversationRepository(BaseRepository):
    """AI conversation history and embeddings"""
    
class BadgeRepository(BaseRepository):
    """Gamification data operations"""
```

## Data Models

### Core Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    baseline_footprint DECIMAL(10,2),
    current_streak INTEGER DEFAULT 0,
    total_co2_saved DECIMAL(10,2) DEFAULT 0,
    eco_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Habit Categories Table
```sql
CREATE TABLE habit_categories (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    co2_impact_per_unit DECIMAL(8,4),
    unit_type VARCHAR(50), -- 'km', 'meal', 'kwh', etc.
    category_type ENUM('transport', 'diet', 'energy', 'lifestyle'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### User Habits Table
```sql
CREATE TABLE user_habits (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    category_id UUID REFERENCES habit_categories(id),
    quantity DECIMAL(8,2),
    co2_saved DECIMAL(8,4),
    logged_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_date (user_id, logged_date),
    INDEX idx_category_date (category_id, logged_date)
);
```

#### AI Conversations Table with Vector Support
```sql
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    message_type ENUM('user', 'assistant'),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI embedding dimension
    context_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_id, created_at),
    VECTOR INDEX idx_embedding (embedding)
);
```

#### Badges and Gamification
```sql
CREATE TABLE badges (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    criteria JSON, -- Flexible criteria definition
    points_value INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_badges (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    badge_id UUID REFERENCES badges(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_badge (user_id, badge_id)
);
```

### Vector Operations Schema

TiDB's vector capabilities will be utilized for:
- **Semantic Search**: Finding similar user queries and responses
- **Personalization**: Matching users with similar profiles for recommendations
- **Content Similarity**: Identifying related coaching tips and insights

## Error Handling

### Error Response Format
```python
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "email",
            "reason": "Invalid email format"
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_123456789"
    }
}
```

### Error Categories
- **Authentication Errors**: 401 Unauthorized, 403 Forbidden
- **Validation Errors**: 400 Bad Request with detailed field errors
- **Resource Errors**: 404 Not Found, 409 Conflict
- **Server Errors**: 500 Internal Server Error with sanitized messages
- **Rate Limiting**: 429 Too Many Requests

### Error Handling Strategy
1. **Global Exception Handler**: Centralized error processing
2. **Structured Logging**: Comprehensive error tracking
3. **User-Friendly Messages**: Clear, actionable error responses
4. **Error Recovery**: Graceful degradation for non-critical failures

## Testing Strategy

### Testing Pyramid

#### Unit Tests (70%)
- **Service Layer**: Business logic validation
- **Repository Layer**: Data access operations
- **Utility Functions**: Helper function correctness
- **Model Validation**: Pydantic model testing

#### Integration Tests (20%)
- **API Endpoints**: Full request/response cycles
- **Database Operations**: Repository integration with TiDB
- **AI Service Integration**: LangChain and OpenAI interactions
- **Authentication Flow**: Firebase integration testing

#### End-to-End Tests (10%)
- **User Journeys**: Complete user workflows
- **AI Coaching Sessions**: Full conversation flows
- **Gamification Scenarios**: Badge earning and leaderboard updates

### Testing Tools and Framework
```python
# Testing Stack
pytest                    # Test framework
pytest-asyncio           # Async test support
factory-boy              # Test data factories
httpx                    # HTTP client for API testing
pytest-mock              # Mocking utilities
coverage.py              # Code coverage analysis

# Test Database
TiDB Test Instance       # Isolated test database
Redis Test Instance      # Caching layer testing
```

### Test Data Management
- **Factory Pattern**: Consistent test data generation
- **Database Fixtures**: Clean state for each test
- **Mock External Services**: Isolated testing environment
- **Seed Data**: Realistic test scenarios