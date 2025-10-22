"""
Rate Limiter Middleware
Protects API from abuse with configurable rate limits
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class RateLimitConfig:
    """Rate limit configuration"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day


class RateLimiter:
    """Rate limiter with sliding window"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from auth
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"
    
    def _cleanup_old_requests(self, client_id: str, window: timedelta):
        """Remove requests outside the time window"""
        cutoff = datetime.now() - window
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if ts > cutoff
        ]
    
    def check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        """Check if request should be rate limited"""
        client_id = self._get_client_id(request)
        now = datetime.now()
        
        # Add current request
        self.requests[client_id].append(now)
        
        # Check minute limit
        self._cleanup_old_requests(client_id, timedelta(minutes=1))
        if len(self.requests[client_id]) > self.config.requests_per_minute:
            return self._rate_limit_response("minute", self.config.requests_per_minute)
        
        # Check hour limit
        self._cleanup_old_requests(client_id, timedelta(hours=1))
        if len(self.requests[client_id]) > self.config.requests_per_hour:
            return self._rate_limit_response("hour", self.config.requests_per_hour)
        
        # Check day limit
        self._cleanup_old_requests(client_id, timedelta(days=1))
        if len(self.requests[client_id]) > self.config.requests_per_day:
            return self._rate_limit_response("day", self.config.requests_per_day)
        
        return None
    
    def _rate_limit_response(self, window: str, limit: int) -> JSONResponse:
        """Return rate limit exceeded response"""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {limit} per {window}",
                "retry_after": self._get_retry_after(window)
            }
        )
    
    def _get_retry_after(self, window: str) -> int:
        """Get retry after seconds"""
        if window == "minute":
            return 60
        elif window == "hour":
            return 3600
        else:
            return 86400


# Global rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    
    # Check rate limit
    response = rate_limiter.check_rate_limit(request)
    if response:
        return response
    
    # Continue with request
    response = await call_next(request)
    
    # Add rate limit headers
    client_id = rate_limiter._get_client_id(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.config.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(
        rate_limiter.config.requests_per_minute - len(rate_limiter.requests[client_id])
    )
    
    return response
