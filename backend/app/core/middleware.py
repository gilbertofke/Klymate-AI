"""
Middleware for Klymate AI Backend

This module provides comprehensive middleware including logging,
authentication, and request processing.
"""

import logging
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Import our comprehensive authentication system
from app.utils.auth_integration import AuthIntegration
from app.utils.jwt_handler import JWTError
from app.utils.firebase_auth import FirebaseAuthError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        await self.log_request(request)
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        status_code = response.status_code
        await self.log_response(request, status_code, process_time)
        
        return response

    async def log_request(self, request: Request):
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Client: {request.client.host if request.client else 'Unknown'}")

    async def log_response(self, request: Request, status_code: int, process_time: float):
        logger.info(f"Response: {request.method} {request.url} - Status: {status_code}")
        logger.info(f"Process Time: {process_time:.2f}s")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT token authentication using Tangus's comprehensive system."""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/", "/health", "/docs", "/redoc", "/openapi.json",
            "/api/v1/auth/register", "/api/v1/auth/login"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Extract authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Authorization header required"}
            )
        
        try:
            # Validate token using our comprehensive auth system
            user_info = AuthIntegration.validate_request_token(authorization)
            
            if not user_info:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid or expired token"}
                )
            
            # Add user info to request state
            request.state.user = user_info
            
            # Continue with request
            response = await call_next(request)
            return response
            
        except (JWTError, FirebaseAuthError) as e:
            logger.warning(f"Authentication failed: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Authentication failed"}
            )
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )


# Security scheme for FastAPI docs
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user.
    Uses Tangus's comprehensive authentication system.
    """
    try:
        authorization_header = f"Bearer {credentials.credentials}"
        user_info = AuthIntegration.validate_request_token(authorization_header)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_info
        
    except (JWTError, FirebaseAuthError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
