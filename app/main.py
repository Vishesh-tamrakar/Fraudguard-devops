"""
FraudGuard — FastAPI Application Entry Point
==============================================
SRS Requirements Covered:
- FR-010 to FR-018: /predict, /health, /metrics, /docs endpoints
- FR-016: Structured JSON logging for every prediction
- FR-018: INFO for success, WARN for low-confidence, ERROR for exceptions
- NFR-001: p95 latency < 500ms for single prediction
"""

import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import setup_logging
from app.model import is_model_loaded, load_model, predict
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    PredictionResponse,
    TransactionRequest,
)

# Initialize structured logger (FR-016)
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: load model on startup."""
    logger.info("FraudGuard starting up...")
    success = load_model()
    if not success:
        logger.error("Model failed to load during startup!")
    yield
    logger.info("FraudGuard shutting down...")


# Create FastAPI application
app = FastAPI(
    title="FraudGuard — Fraud Detection API",
    description=(
        "A FastAPI-based fraud detection service using a Random Forest model "
        "trained on the IEEE-CIS Fraud Detection dataset. "
        "Part of the FraudGuard DevOps Platform for CSE 816."
    ),
    version="1.0.0",
    docs_url="/docs",  # FR-186: Swagger UI for evaluation demo
    lifespan=lifespan,
)

# FR-179/FR-182: Prometheus metrics via /metrics endpoint
Instrumentator().instrument(app).expose(app)


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
    summary="Predict fraud on a financial transaction",
    description="FR-010: Accepts transaction features, returns fraud prediction with confidence score.",
)
async def predict_fraud(transaction: TransactionRequest, request: Request):
    """
    FR-010 to FR-015: Main prediction endpoint.
    """
    start_time = time.time()

    # Generate or echo transaction ID (FR-013)
    transaction_id = str(uuid.uuid4())

    # FR-014: Check if model is loaded
    if not is_model_loaded():
        logger.error("Prediction failed: model not loaded", extra={
            "transaction_id": transaction_id,
            "client_ip": request.client.host if request.client else "unknown",
        })
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error="ServiceUnavailable",
                message="ML model is not loaded. Service cannot process predictions.",
            ).model_dump(),
        )

    try:
        # Convert Pydantic model to dict for prediction
        features = transaction.model_dump()

        # Run prediction
        result = predict(features)

        processing_time_ms = round((time.time() - start_time) * 1000, 2)

        # FR-013: Build response
        response = PredictionResponse(
            transaction_id=transaction_id,
            prediction=result["prediction"],
            label=result["label"],
            confidence_score=result["confidence_score"],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # FR-016, FR-018: Structured logging
        log_extra = {
            "transaction_id": transaction_id,
            "prediction": result["prediction"],
            "confidence_score": result["confidence_score"],
            "processing_time_ms": processing_time_ms,
            "client_ip": request.client.host if request.client else "unknown",
            "label": result["label"],
        }

        # FR-018: WARN for low-confidence predictions (< 0.6)
        if result["confidence_score"] < 0.6:
            logger.warning(
                f"Low-confidence prediction: {result['label']} "
                f"(score={result['confidence_score']})",
                extra=log_extra,
            )
        else:
            logger.info(
                f"Prediction: {result['label']} "
                f"(score={result['confidence_score']}, "
                f"time={processing_time_ms}ms)",
                extra=log_extra,
            )

        return response

    except Exception as e:
        processing_time_ms = round((time.time() - start_time) * 1000, 2)

        # FR-015, FR-018: Log full exception at ERROR level
        logger.error(
            f"Prediction exception: {type(e).__name__}: {str(e)}",
            extra={
                "transaction_id": transaction_id,
                "client_ip": request.client.host if request.client else "unknown",
                "processing_time_ms": processing_time_ms,
                "traceback": traceback.format_exc(),
            },
        )

        # FR-015: Return exception type and message (not stack trace)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=type(e).__name__,
                message=str(e),
            ).model_dump(),
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns service health status and model loading state.",
)
async def health_check():
    """
    Health check endpoint for K8s liveness/readiness probes (FR-085).
    Returns 200 if healthy, 503 if model failed to load.
    """
    model_loaded = is_model_loaded()
    status = "healthy" if model_loaded else "unhealthy"
    status_code = 200 if model_loaded else 503

    return JSONResponse(
        status_code=status_code,
        content=HealthResponse(
            status=status,
            model_loaded=model_loaded,
        ).model_dump(),
    )
