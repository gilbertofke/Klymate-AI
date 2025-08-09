from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.middleware import LoggingMiddleware

app = FastAPI(
    title="Klymate-AI",
    description="AI-powered Carbon Footprint Tracking and Coaching",
    version="1.0.0"
)

# Configure Middleware
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Klymate-AI API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Klymate-AI API"
    }

# Include API router
app.include_router(api_router, prefix="/api/v1")
