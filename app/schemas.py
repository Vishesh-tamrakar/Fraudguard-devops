"""
FraudGuard — Pydantic Request/Response Schemas
================================================
SRS Requirements Covered:
- FR-010: TransactionRequest Pydantic model with top 30 features
- FR-011: Pydantic validation (422 for missing required fields)
- FR-012: Numeric fields accept int/float, categorical accept string
- FR-013: Prediction response with transaction_id, prediction, label,
          confidence_score, timestamp
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    """
    FR-010: POST /predict request schema.
    Fields match the top 30+ features selected during training.
    FR-012: Numeric fields accept int/float, categorical accept string.
    """

    # Transaction amount and time
    TransactionAmt: float = Field(..., description="Transaction amount in USD")
    TransactionDT: float = Field(..., description="Transaction datetime (seconds offset)")

    # Product code (categorical)
    ProductCD: str = Field(..., description="Product code (W, H, C, S, R)")

    # Card features
    card1: float = Field(..., description="Card feature 1")
    card2: Optional[float] = Field(None, description="Card feature 2")
    card3: Optional[float] = Field(None, description="Card feature 3")
    card4: Optional[str] = Field(None, description="Card type (visa, mastercard, etc.)")
    card5: Optional[float] = Field(None, description="Card feature 5")
    card6: Optional[str] = Field(None, description="Card category (debit, credit, etc.)")

    # Address features
    addr1: Optional[float] = Field(None, description="Billing address region")
    addr2: Optional[float] = Field(None, description="Billing address country")

    # Distance
    dist1: Optional[float] = Field(None, description="Distance feature 1")

    # Email domains (categorical)
    P_emaildomain: Optional[str] = Field(None, description="Purchaser email domain")
    R_emaildomain: Optional[str] = Field(None, description="Recipient email domain")

    # Count features (C1-C14)
    C1: Optional[float] = Field(None, description="Count feature 1")
    C2: Optional[float] = Field(None, description="Count feature 2")
    C3: Optional[float] = Field(None, description="Count feature 3")
    C4: Optional[float] = Field(None, description="Count feature 4")
    C5: Optional[float] = Field(None, description="Count feature 5")
    C6: Optional[float] = Field(None, description="Count feature 6")
    C7: Optional[float] = Field(None, description="Count feature 7")
    C8: Optional[float] = Field(None, description="Count feature 8")
    C9: Optional[float] = Field(None, description="Count feature 9")
    C10: Optional[float] = Field(None, description="Count feature 10")
    C11: Optional[float] = Field(None, description="Count feature 11")
    C12: Optional[float] = Field(None, description="Count feature 12")
    C13: Optional[float] = Field(None, description="Count feature 13")
    C14: Optional[float] = Field(None, description="Count feature 14")

    # V features (Vesta engineered features)
    V1: Optional[float] = Field(None, description="V feature 1")
    V2: Optional[float] = Field(None, description="V feature 2")
    V3: Optional[float] = Field(None, description="V feature 3")
    V4: Optional[float] = Field(None, description="V feature 4")
    V5: Optional[float] = Field(None, description="V feature 5")
    V12: Optional[float] = Field(None, description="V feature 12")
    V13: Optional[float] = Field(None, description="V feature 13")
    V14: Optional[float] = Field(None, description="V feature 14")
    V36: Optional[float] = Field(None, description="V feature 36")
    V37: Optional[float] = Field(None, description="V feature 37")
    V38: Optional[float] = Field(None, description="V feature 38")
    V54: Optional[float] = Field(None, description="V feature 54")
    V55: Optional[float] = Field(None, description="V feature 55")
    V56: Optional[float] = Field(None, description="V feature 56")
    V75: Optional[float] = Field(None, description="V feature 75")
    V76: Optional[float] = Field(None, description="V feature 76")
    V77: Optional[float] = Field(None, description="V feature 77")
    V78: Optional[float] = Field(None, description="V feature 78")
    V282: Optional[float] = Field(None, description="V feature 282")
    V283: Optional[float] = Field(None, description="V feature 283")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "TransactionAmt": 75.0,
                    "TransactionDT": 86400,
                    "ProductCD": "W",
                    "card1": 13926,
                    "card2": 361.0,
                    "card3": 185.0,
                    "card4": "visa",
                    "card5": 117.0,
                    "card6": "debit",
                    "addr1": 315.0,
                    "addr2": 87.0,
                    "dist1": 19.0,
                    "P_emaildomain": "gmail.com",
                    "R_emaildomain": None,
                    "C1": 1.0,
                    "C2": 1.0,
                    "C3": 0.0,
                    "C4": 0.0,
                    "C5": 0.0,
                    "C6": 1.0,
                    "C7": 0.0,
                    "C8": 0.0,
                    "C9": 1.0,
                    "C10": 0.0,
                    "C11": 2.0,
                    "C12": 0.0,
                    "C13": 1.0,
                    "C14": 1.0,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """
    FR-013: Successful prediction response schema.
    """

    transaction_id: str = Field(..., description="Transaction ID (echoed or UUID-generated)")
    prediction: int = Field(..., description="Fraud prediction (0 = legitimate, 1 = fraudulent)")
    label: str = Field(..., description="Human-readable label ('legitimate' or 'fraudulent')")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="RF predict_proba confidence score"
    )
    timestamp: str = Field(..., description="Prediction timestamp (ISO 8601 UTC)")


class HealthResponse(BaseModel):
    """
    Health check response for /health endpoint.
    """

    status: str = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")


class ErrorResponse(BaseModel):
    """
    FR-014, FR-015: Error response schema.
    """

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message description")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Error timestamp",
    )
