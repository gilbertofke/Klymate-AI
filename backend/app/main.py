"""
Klymate AI FastAPI Application

This is the main FastAPI application that integrates:
- Rono's FastAPI structure and middleware
- Tangus's comprehensive authentication system
- Industry-standard patterns and practices
"""

from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.middleware import EnhancedCORSMiddleware, LoggingMiddleware, AuthenticationMiddleware
from app.core.config import settings

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered Carbon Footprint Tracking and Coaching with Real Carbon Credits",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Middleware (order matters!)
# 1. Enhanced CORS middleware (first) - handles preflight requests and Firebase tokens
app.add_middleware(
    EnhancedCORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS.split(","),
    allow_headers=settings.ALLOWED_HEADERS.split(","),
    expose_headers=["Content-Length", "Content-Type", "X-Request-ID"],
    max_age=settings.CORS_MAX_AGE,
    debug_logging=settings.CORS_DEBUG_LOGGING
)

# 2. Authentication middleware (using Tangus's comprehensive system)
app.add_middleware(
    AuthenticationMiddleware,
    exclude_paths=[
        "/", "/health", "/docs", "/redoc", "/openapi.json",
        "/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/refresh",
        "/api/v1/auth/register-email", "/api/v1/auth/login-email",
        "/api/v1/users/onboarding"  # Temporarily exclude for debugging
    ]
)

# 3. Logging middleware (last)
app.add_middleware(LoggingMiddleware)

@app.get("/")
async def root():
    """Root endpoint with comprehensive project information."""
    return {
        "message": "Welcome to Klymate-AI API",
        "version": settings.VERSION,
        "status": "active",
        "features": [
            "AI-powered carbon footprint tracking",
            "Personalized coaching with LangChain",
            "Real carbon credits with monetary value",
            "Gamification and achievements",
            "Firebase authentication",
            "TiDB vector database"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Include API router with comprehensive authentication
app.include_router(api_router, prefix=settings.API_V1_STR)
