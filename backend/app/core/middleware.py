"""
Middleware for Klymate AI Backend

This module provides comprehensive middleware including logging,
authentication, CORS handling, and request processing.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

# Import our comprehensive authentication system
from app.utils.auth_integration import AuthIntegration
from app.utils.jwt_handler import JWTError
from app.utils.firebase_auth import FirebaseAuthError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCORSMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with proper preflight handling and Firebase token support.
    
    This middleware provides comprehensive CORS support including:
    - Proper preflight request handling
    - Firebase authentication token headers
    - Development environment configuration
    - CORS error logging for debugging
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = True,
        expose_headers: List[str] = None,
        max_age: int = 600,
        debug_logging: bool = True
    ):
        super().__init__(app)
        self.allow_origins = allow_origins or [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://localhost:3000"
        ]
        self.allow_methods = allow_methods or [
            "GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"
        ]
        self.allow_headers = allow_headers or [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Firebase-Auth",
            "Firebase-Instance-ID-Token",
            "X-Firebase-AppCheck",
            "Access-Control-Allow-Credentials",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Origin"
        ]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        self.debug_logging = debug_logging
        
        # Log configuration on startup
        logger.info("Enhanced CORS Middleware initialized")
        logger.info(f"Allowed origins: {self.allow_origins}")
        logger.info(f"Allowed methods: {self.allow_methods}")
        logger.info(f"Allowed headers: {self.allow_headers}")
        logger.info(f"Allow credentials: {self.allow_credentials}")
        logger.info(f"Max age: {self.max_age}")
        logger.info(f"Debug logging: {self.debug_logging}")
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Enhanced CORS request logging for debugging
        if self.debug_logging and origin:
            logger.info(f"CORS request from origin: {origin}")
            logger.info(f"Request method: {request.method}")
            logger.info(f"Request path: {request.url.path}")
            
            # Log relevant headers for debugging
            relevant_headers = {
                k: v for k, v in request.headers.items() 
                if k.lower() in ['authorization', 'content-type', 'x-firebase-auth', 'firebase-instance-id-token']
            }
            if relevant_headers:
                logger.info(f"Relevant request headers: {relevant_headers}")
        
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            return self._handle_preflight_request(request, origin)
        
        # Process the actual request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"CORS middleware - Error processing request from {origin}: {str(e)}")
            logger.error(f"Request details - Method: {request.method}, Path: {request.url.path}")
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "detail": "CORS middleware error"}
            )
        
        # Add CORS headers to response
        return self._add_cors_headers(response, origin)
    
    def _handle_preflight_request(self, request: Request, origin: str) -> Response:
        """Handle CORS preflight OPTIONS requests."""
        
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            logger.error(f"CORS PREFLIGHT REJECTED - Origin not allowed: {origin}")
            logger.error(f"Allowed origins: {self.allow_origins}")
            return Response(
                status_code=403,
                content="CORS preflight request rejected - origin not allowed"
            )
        
        # Get requested method and headers
        requested_method = request.headers.get("access-control-request-method")
        requested_headers = request.headers.get("access-control-request-headers", "")
        
        logger.info(f"CORS PREFLIGHT SUCCESS - Origin: {origin}, Method: {requested_method}, Headers: {requested_headers}")
        
        # Validate requested method
        if requested_method and requested_method not in self.allow_methods:
            logger.error(f"CORS PREFLIGHT REJECTED - Method not allowed: {requested_method}")
            logger.error(f"Allowed methods: {self.allow_methods}")
            return Response(
                status_code=405,
                content="CORS preflight request rejected - method not allowed"
            )
        
        # Create preflight response
        response = Response(status_code=200)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        # Add Vary header for proper caching
        response.headers["Vary"] = "Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
        
        if self.debug_logging:
            logger.info(f"CORS preflight response headers: {dict(response.headers)}")
        
        return response
    
    def _add_cors_headers(self, response: Response, origin: str) -> Response:
        """Add CORS headers to actual response."""
        
        if not self._is_origin_allowed(origin):
            logger.error(f"CORS RESPONSE REJECTED - Origin not allowed: {origin}")
            logger.error(f"Allowed origins: {self.allow_origins}")
            return response
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        # Add Vary header
        response.headers["Vary"] = "Origin"
        
        if self.debug_logging:
            logger.info(f"CORS response headers added for origin: {origin}")
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if the origin is allowed."""
        if not origin:
            if self.debug_logging:
                logger.warning("CORS check failed - No origin header provided")
            return False
        
        # Allow all origins if "*" is in the list
        if "*" in self.allow_origins:
            if self.debug_logging:
                logger.info(f"CORS allowed - Wildcard origin policy for: {origin}")
            return True
        
        # Check exact match
        if origin in self.allow_origins:
            if self.debug_logging:
                logger.info(f"CORS allowed - Exact match for origin: {origin}")
            return True
        
        # For development, be more permissive with localhost variations
        localhost_patterns = [
            "http://localhost:",
            "http://127.0.0.1:",
            "https://localhost:",
            "https://127.0.0.1:"
        ]
        
        for pattern in localhost_patterns:
            if origin.startswith(pattern):
                # Extract port and validate it's a reasonable development port
                try:
                    port_part = origin.split(":")[-1]
                    port = int(port_part.split("/")[0])  # Remove any path
                    if 3000 <= port <= 9999:  # Common development port range
                        if self.debug_logging:
                            logger.info(f"CORS allowed - Development localhost pattern for: {origin}")
                        return True
                except (ValueError, IndexError):
                    pass
        
        logger.error(f"CORS DENIED - Origin not in allowed list: {origin}")
        logger.error(f"Allowed origins: {self.allow_origins}")
        return False


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
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
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
