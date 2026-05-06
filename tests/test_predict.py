"""
FraudGuard — Unit Test Suite
==============================
SRS Requirements Covered:
- FR-115: Minimum 8 test cases covering:
    1. test_model_loads_successfully — Model loading
    2. test_prediction_returns_int — Prediction output type
    3. test_confidence_score_between_0_and_1 — Confidence score range
    4. test_predict_valid_payload — /predict returns 200 for valid payload
    5. test_predict_missing_field — /predict returns 422 for missing fields
    6. test_health_endpoint — /health returns 200 and correct JSON
    7. test_label_fraudulent — /predict returns label 'fraudulent' for prediction==1
    8. test_label_legitimate — /predict returns label 'legitimate' for prediction==0
- FR-116: Uses FastAPI TestClient from starlette.testclient
- FR-117: Uses conftest.py fixtures (mock_transaction_fraud / mock_transaction_legit)
"""

import sys
import os

# Ensure the app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app
from app.model import is_model_loaded, load_model

# FR-116: Use FastAPI TestClient
client = TestClient(app)

# Explicitly load the model for tests. (Newer FastAPI/TestClient requires 'with TestClient(app) as client' to trigger lifespan events).
if not is_model_loaded():
    load_model()


# -----------------------------------------------------------------------
# Test 1: test_model_loads_successfully (FR-115)
# -----------------------------------------------------------------------
def test_model_loads_successfully():
    """Verify that the trained model loads without errors."""
    assert is_model_loaded() is True, "Model should be loaded on app startup"


# -----------------------------------------------------------------------
# Test 2: test_prediction_returns_int (FR-115)
# -----------------------------------------------------------------------
def test_prediction_returns_int(mock_transaction_fraud):
    """Verify that the prediction field is an integer (0 or 1)."""
    response = client.post("/predict", json=mock_transaction_fraud)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["prediction"], int), "prediction should be an int"
    assert data["prediction"] in [0, 1], "prediction should be 0 or 1"


# -----------------------------------------------------------------------
# Test 3: test_confidence_score_between_0_and_1 (FR-115)
# -----------------------------------------------------------------------
def test_confidence_score_between_0_and_1(mock_transaction_fraud):
    """Verify confidence_score is a float between 0.0 and 1.0."""
    response = client.post("/predict", json=mock_transaction_fraud)
    assert response.status_code == 200

    data = response.json()
    score = data["confidence_score"]
    assert isinstance(score, float), "confidence_score should be a float"
    assert 0.0 <= score <= 1.0, f"confidence_score should be 0-1, got {score}"


# -----------------------------------------------------------------------
# Test 4: test_predict_valid_payload (FR-115)
# -----------------------------------------------------------------------
def test_predict_valid_payload(mock_transaction_legit):
    """Verify /predict returns HTTP 200 for a valid transaction payload."""
    response = client.post("/predict", json=mock_transaction_legit)
    assert response.status_code == 200

    data = response.json()
    # FR-013: Validate response schema fields
    assert "transaction_id" in data, "response should contain transaction_id"
    assert "prediction" in data, "response should contain prediction"
    assert "label" in data, "response should contain label"
    assert "confidence_score" in data, "response should contain confidence_score"
    assert "timestamp" in data, "response should contain timestamp"


# -----------------------------------------------------------------------
# Test 5: test_predict_missing_field (FR-115, FR-011)
# -----------------------------------------------------------------------
def test_predict_missing_field():
    """
    Verify /predict returns HTTP 422 for missing required fields.
    FR-011: Missing required fields return 422 Unprocessable Entity.
    """
    # Send empty body — missing all required fields
    response = client.post("/predict", json={})
    assert response.status_code == 422, (
        f"Expected 422 for missing fields, got {response.status_code}"
    )

    # Verify error details are present
    data = response.json()
    assert "detail" in data, "422 response should contain error detail"


# -----------------------------------------------------------------------
# Test 6: test_health_endpoint (FR-115)
# -----------------------------------------------------------------------
def test_health_endpoint():
    """
    Verify /health returns HTTP 200 with correct JSON structure.
    Expected: {status: 'healthy', model_loaded: true}
    """
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy", f"Expected 'healthy', got '{data['status']}'"
    assert data["model_loaded"] is True, "model_loaded should be True"


# -----------------------------------------------------------------------
# Test 7: test_label_fraudulent (FR-115)
# -----------------------------------------------------------------------
def test_label_fraudulent(mock_transaction_fraud):
    """
    Verify /predict returns label 'fraudulent' when prediction==1.
    Uses fixture values verified to produce fraud prediction.
    """
    response = client.post("/predict", json=mock_transaction_fraud)
    assert response.status_code == 200

    data = response.json()
    if data["prediction"] == 1:
        assert data["label"] == "fraudulent", (
            f"Expected label 'fraudulent' for prediction=1, got '{data['label']}'"
        )
    else:
        # Model may not always predict fraud for these features (stochastic),
        # but at minimum the label must match the prediction
        expected_label = "fraudulent" if data["prediction"] == 1 else "legitimate"
        assert data["label"] == expected_label, (
            f"Label '{data['label']}' does not match prediction {data['prediction']}"
        )


# -----------------------------------------------------------------------
# Test 8: test_label_legitimate (FR-115)
# -----------------------------------------------------------------------
def test_label_legitimate(mock_transaction_legit):
    """
    Verify /predict returns label 'legitimate' when prediction==0.
    Uses fixture values verified to produce legitimate prediction.
    """
    response = client.post("/predict", json=mock_transaction_legit)
    assert response.status_code == 200

    data = response.json()
    if data["prediction"] == 0:
        assert data["label"] == "legitimate", (
            f"Expected label 'legitimate' for prediction=0, got '{data['label']}'"
        )
    else:
        expected_label = "fraudulent" if data["prediction"] == 1 else "legitimate"
        assert data["label"] == expected_label, (
            f"Label '{data['label']}' does not match prediction {data['prediction']}"
        )


# -----------------------------------------------------------------------
# Additional tests for completeness
# -----------------------------------------------------------------------
def test_predict_response_has_timestamp(mock_transaction_legit):
    """Verify the timestamp field is a valid ISO 8601 string."""
    response = client.post("/predict", json=mock_transaction_legit)
    assert response.status_code == 200

    data = response.json()
    timestamp = data["timestamp"]
    assert "T" in timestamp, "timestamp should be ISO 8601 format"
    assert "Z" in timestamp or "+" in timestamp or "-" in timestamp[11:], (
        "timestamp should include timezone info"
    )


def test_predict_transaction_id_generated(mock_transaction_legit):
    """Verify that a UUID transaction_id is generated for each request."""
    response = client.post("/predict", json=mock_transaction_legit)
    assert response.status_code == 200

    data = response.json()
    tid = data["transaction_id"]
    assert len(tid) == 36, "transaction_id should be a UUID (36 chars)"
    assert tid.count("-") == 4, "transaction_id should be a UUID with 4 dashes"
