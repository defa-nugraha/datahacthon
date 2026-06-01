from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class APIError(Exception):
    """Base exception for controlled API failures."""

    def __init__(self, message: str, *, status_code: int, error_code: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class ArtifactLoadError(APIError):
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, status_code=503, error_code="artifact_load_error", details=details)


class FeatureMismatchError(APIError):
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, status_code=500, error_code="feature_mismatch_error", details=details)


class PredictionError(APIError):
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, status_code=500, error_code="prediction_error", details=details)


class BusinessValidationError(APIError):
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, status_code=400, error_code="business_validation_error", details=details)


def _json_error_response(
    *,
    status_code: int,
    message: str,
    error_code: str,
    details: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error": {
                "code": error_code,
                "message": message,
                "details": details,
            },
        },
    )


def _normalize_validation_errors(errors: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for error in errors:
        location = [str(item) for item in error.get("loc", ())]
        normalized.append(
            {
                "location": ".".join(location),
                "message": error.get("msg", "Invalid request."),
                "type": error.get("type", "validation_error"),
            }
        )
    return normalized


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(_: Request, exc: APIError) -> JSONResponse:
        return _json_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _json_error_response(
            status_code=422,
            message="Request validation failed.",
            error_code="request_validation_error",
            details=_normalize_validation_errors(exc.errors()),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        return _json_error_response(
            status_code=500,
            message="Unexpected internal server error.",
            error_code="internal_server_error",
            details={"exception_type": type(exc).__name__},
        )
