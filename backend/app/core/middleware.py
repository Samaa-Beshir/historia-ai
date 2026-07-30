"""Cross-cutting HTTP middleware: request logging, auth, rate limiting."""
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config.settings import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """No-op unless settings.api_key is set, keeping local dev friction-free."""

    EXEMPT_PATHS = {"/health", "/version", "/docs", "/openapi.json", "/redoc"}

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self._settings = settings

    async def dispatch(self, request: Request, call_next):
        expected = self._settings.api_key
        if expected is None or request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        provided = request.headers.get("x-api-key")
        if provided != expected.get_secret_value():
            return JSONResponse(
                status_code=401,
                content={"error": {"code": "unauthorized", "message": "Missing or invalid X-API-Key."}},
            )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory fixed-window rate limiter, per client IP.

    Good enough for a single-process deployment; a multi-instance
    deployment would swap this for a shared store (e.g. Redis) behind the
    same interface.
    """

    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self._limit = requests_per_minute
        self._window_seconds = 60
        self._hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[client_id]

        while hits and now - hits[0] > self._window_seconds:
            hits.popleft()

        if len(hits) >= self._limit:
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limit_exceeded", "message": "Too many requests."}},
            )

        hits.append(now)
        return await call_next(request)
