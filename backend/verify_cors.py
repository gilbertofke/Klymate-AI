#!/usr/bin/env python3
"""
Quick verification script for CORS configuration.
Tests the middleware configuration without requiring a running server.
"""

from app.core.middleware import EnhancedCORSMiddleware
from app.core.config import settings
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cors_middleware_config():
    """Test CORS middleware configuration."""
    logger.info("Testing CORS middleware configuration...")
    
    # Create a simple app
    app = Starlette()
    
    # Add our enhanced CORS middleware
    cors_middleware = EnhancedCORSMiddleware(
        app,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS.split(","),
        allow_headers=settings.ALLOWED_HEADERS.split(","),
        max_age=settings.CORS_MAX_AGE,
        debug_logging=settings.CORS_DEBUG_LOGGING
    )
    
    # Test origin validation
    test_cases = [
        ("http://localhost:3000", True, "Valid localhost origin"),
        ("http://127.0.0.1:3000", True, "Valid 127.0.0.1 origin"),
        ("https://localhost:3000", True, "Valid HTTPS localhost origin"),
        ("http://malicious-site.com", False, "Invalid external origin"),
        ("", False, "Empty origin"),
        ("http://localhost:8080", True, "Valid localhost with different port"),
    ]
    
    logger.info("Testing origin validation:")
    for origin, expected, description in test_cases:
        result = cors_middleware._is_origin_allowed(origin)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        logger.info(f"  {status} - {description}: '{origin}' -> {result}")
    
    # Test configuration values
    logger.info("\nCORS Configuration:")
    logger.info(f"  Allowed Origins: {cors_middleware.allow_origins}")
    logger.info(f"  Allowed Methods: {cors_middleware.allow_methods}")
    logger.info(f"  Allowed Headers: {cors_middleware.allow_headers}")
    logger.info(f"  Allow Credentials: {cors_middleware.allow_credentials}")
    logger.info(f"  Max Age: {cors_middleware.max_age}")
    logger.info(f"  Debug Logging: {cors_middleware.debug_logging}")
    
    # Verify Firebase headers are included
    firebase_headers = [
        "X-Firebase-Auth",
        "Firebase-Instance-ID-Token", 
        "X-Firebase-AppCheck"
    ]
    
    logger.info("\nFirebase Header Support:")
    for header in firebase_headers:
        if header in cors_middleware.allow_headers:
            logger.info(f"  ✅ {header} - Supported")
        else:
            logger.info(f"  ❌ {header} - Missing")
    
    # Verify essential headers
    essential_headers = ["Authorization", "Content-Type", "Accept"]
    logger.info("\nEssential Header Support:")
    for header in essential_headers:
        if header in cors_middleware.allow_headers:
            logger.info(f"  ✅ {header} - Supported")
        else:
            logger.info(f"  ❌ {header} - Missing")
    
    logger.info("\n🎉 CORS middleware configuration verification complete!")

if __name__ == "__main__":
    test_cors_middleware_config()