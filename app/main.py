from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Body, FastAPI, Request

from app.core.config import Settings, get_settings
from app.core.exceptions import ArtifactLoadError, register_exception_handlers
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    ModelInfoPayload,
    ZONE_PREDICTION_REQUEST_OPENAPI_EXAMPLES,
    ZonePredictionDebugResponse,
    ZonePredictionRequest,
    ZonePredictionResponse,
)
from app.services.predictor import ZonePredictor


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.predictor = None
        app.state.startup_error = None
        try:
            app.state.predictor = ZonePredictor.from_settings(settings)
            logger.info("Zone prediction service is ready.")
        except Exception as exc:  # pragma: no cover - exercised via health checks and startup_error state
            logger.exception("Zone prediction service failed to initialize.")
            app.state.startup_error = exc
        yield

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=(
            "Inference API for the zone-based vegetation recommendation model. "
            "The main endpoint accepts raw point samples from one zone, aggregates them into zone features, "
            "and predicts the recommended label using the trained zone model."
        ),
        lifespan=lifespan,
    )
    register_exception_handlers(app)

    def _get_predictor(request: Request) -> ZonePredictor:
        startup_error = getattr(request.app.state, "startup_error", None)
        if startup_error is not None:
            raise ArtifactLoadError(
                "The inference service is not ready because artifact loading failed at startup.",
                details={"exception_type": type(startup_error).__name__, "message": str(startup_error)},
            )
        predictor = getattr(request.app.state, "predictor", None)
        if predictor is None:
            raise ArtifactLoadError("The inference service is not ready because the predictor is not initialized.")
        return predictor

    @app.get(
        "/health",
        response_model=HealthResponse,
        responses={503: {"model": ErrorResponse}},
        tags=["system"],
    )
    async def health(request: Request) -> dict[str, Any]:
        startup_error = getattr(request.app.state, "startup_error", None)
        predictor = getattr(request.app.state, "predictor", None)
        if startup_error is not None:
            return {
                "status": "degraded",
                "model_loaded": False,
                "active_model_name": None,
                "detail": f"{type(startup_error).__name__}: {startup_error}",
            }
        if predictor is None:
            return {
                "status": "degraded",
                "model_loaded": False,
                "active_model_name": None,
                "detail": "Predictor not initialized.",
            }
        return {
            "status": "ok",
            "model_loaded": True,
            "active_model_name": predictor.artifacts.model_name,
            "detail": "Inference service is ready.",
        }

    @app.get(
        "/model/info",
        response_model=ModelInfoPayload,
        responses={503: {"model": ErrorResponse}},
        tags=["model"],
    )
    async def model_info(request: Request) -> dict[str, Any]:
        predictor = _get_predictor(request)
        return predictor.get_model_info()

    @app.post(
        "/predict/zone",
        response_model=ZonePredictionResponse,
        responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
        tags=["prediction"],
    )
    async def predict_zone(
        request: Request,
        payload: ZonePredictionRequest = Body(..., openapi_examples=ZONE_PREDICTION_REQUEST_OPENAPI_EXAMPLES),
    ) -> dict[str, Any]:
        predictor = _get_predictor(request)
        return predictor.predict(payload, include_debug=False)

    @app.post(
        "/predict/zone/debug",
        response_model=ZonePredictionDebugResponse,
        responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
        tags=["prediction"],
    )
    async def predict_zone_debug(
        request: Request,
        payload: ZonePredictionRequest = Body(..., openapi_examples=ZONE_PREDICTION_REQUEST_OPENAPI_EXAMPLES),
    ) -> dict[str, Any]:
        predictor = _get_predictor(request)
        return predictor.predict(payload, include_debug=True)

    return app


app = create_app()
