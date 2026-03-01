from __future__ import annotations

import logging
import time
import uuid

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.errors import to_error_response
from app.core.logging import (
    get_correlation_id,
    reset_correlation_id,
    set_correlation_id,
)

_REQUEST_ID_HEADER = "X-Request-ID"
_logger = logging.getLogger("app.request")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        incoming = request.headers.get(_REQUEST_ID_HEADER)
        request_id = incoming or str(uuid.uuid4())
        request.state.request_id = request_id
        token = set_correlation_id(request_id)
        try:
            try:
                response = await call_next(request)
            except Exception:
                _logger.exception(
                    "unhandled exception",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "request_id": request_id,
                    },
                )
                response = JSONResponse(
                    status_code=500,
                    content=to_error_response(
                        "INTERNAL_SERVER_ERROR",
                        "Internal server error",
                        None,
                    ),
                )
            response.headers[_REQUEST_ID_HEADER] = request_id
            return response
        finally:
            reset_correlation_id(token)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        _logger.info(
            "request complete",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "request_id": get_correlation_id(),
            },
        )
        return response
