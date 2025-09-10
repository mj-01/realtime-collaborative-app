"""
Metrics and monitoring middleware.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logging import get_logger

logger = get_logger("metrics")

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        self.request_count += 1
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            self.total_response_time += process_time
            
            # Log response
            logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-Count"] = str(self.request_count)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self.error_count += 1
            
            # Log error
            logger.error(f"Error: {str(e)} - {process_time:.3f}s")
            
            # Re-raise the exception
            raise
    
    def get_metrics(self) -> dict:
        """Get current metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 
            else 0
        )
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "average_response_time": avg_response_time,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0
        }
