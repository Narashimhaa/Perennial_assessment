import os
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, limit: int, interval_sec: int):
        self.limit = limit
        self.interval = timedelta(seconds=interval_sec)
        self.access_times = defaultdict(list)
        self.lock = Lock()
        self.last_cleanup = time.time()
        self.cleanup_interval = 300 

    def _cleanup_old_entries(self):
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            with self.lock:
                now = datetime.now()
                ips_to_remove = []
                for ip, times in self.access_times.items():
                    recent_times = [t for t in times if now - t < self.interval * 2]
                    if recent_times:
                        self.access_times[ip] = recent_times
                    else:
                        ips_to_remove.append(ip)

                for ip in ips_to_remove:
                    del self.access_times[ip]

                self.last_cleanup = current_time
                logger.debug(f"Rate limiter cleanup: removed {len(ips_to_remove)} inactive IPs")

    def is_allowed(self, ip: str) -> bool:
        self._cleanup_old_entries()

        with self.lock:
            now = datetime.now()
            access_list = [t for t in self.access_times[ip] if now - t < self.interval]
            self.access_times[ip] = access_list

            if len(access_list) < self.limit:
                self.access_times[ip].append(now)
                return True
            return False

    def record_request(self, ip: str, success: bool = True):
        if not success:
            with self.lock:
                now = datetime.now()
                self.access_times[ip].append(now)

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

limiter = RateLimiter(limit=RATE_LIMIT_REQUESTS, interval_sec=RATE_LIMIT_WINDOW)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        if not self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "detail": f"Rate limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds",
                    "retry_after": RATE_LIMIT_WINDOW
                },
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
            )

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            self.rate_limiter.record_request(client_ip, success=False)
            raise e

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"