import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
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
