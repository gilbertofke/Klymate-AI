"""
Klymate AI FastAPI Application

This is the main FastAPI application that integrates:
- Rono's FastAPI structure and middleware
- Tangus's comprehensive authentication system
- Industry-standard patterns and practices
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.middleware import LoggingMiddleware, AuthenticationMiddleware
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
# 1. CORS middleware (first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS.split(",") if settings.ALLOWED_METHODS != "*" else ["*"],
    allow_headers=settings.ALLOWED_HEADERS.split(",") if settings.ALLOWED_HEADERS != "*" else ["*"],
)

# 2. Authentication middleware (using Tangus's comprehensive system)
app.add_middleware(
    AuthenticationMiddleware,
    exclude_paths=[
        "/", "/health", "/docs", "/redoc", "/openapi.json",
        "/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/refresh"
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
