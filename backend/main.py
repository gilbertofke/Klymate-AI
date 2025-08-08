"""
Klymate AI Backend - FastAPI Application Entry Point

This module serves as the main entry point for the Klymate AI backend application.
It initializes the FastAPI application with proper configuration and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Klymate AI Backend",
    description="Carbon footprint tracker with AI-powered coaching capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for basic API verification"""
    return {"message": "Klymate AI Backend is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    return {
        "status": "healthy",
        "service": "klymate-ai-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )