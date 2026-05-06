"""
FraudGuard — Model Loading and Prediction Logic
=================================================
SRS Requirements Covered:
- FR-007: Loads model serialized with joblib
- FR-013: Returns prediction, label, confidence_score
- FR-014: Raises exception if model not loaded
"""

import logging
import os

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger("fraudguard")

# Global model artefact
_model_artefact = None


def load_model(model_path: str = None) -> bool:
    """
    Load the trained model artefact from disk.

    Args:
        model_path: Path to model.pkl (default: /app/model.pkl or local)

    Returns:
        True if model loaded successfully, False otherwise
    """
    global _model_artefact

    if model_path is None:
        # Default path inside Docker container (FR-009)
        model_path = os.environ.get(
            "MODEL_PATH",
            os.path.join(os.path.dirname(__file__), "model.pkl"),
        )

    try:
        _model_artefact = joblib.load(model_path)
        logger.info(
            "Model loaded successfully",
            extra={
                "model_path": model_path,
                "feature_count": len(_model_artefact["feature_names"]),
            },
        )
        return True
    except Exception as e:
        logger.error(
            f"Failed to load model: {type(e).__name__}: {e}",
            extra={"model_path": model_path},
        )
        return False


def is_model_loaded() -> bool:
    """Check if the model is loaded."""
    return _model_artefact is not None


def predict(features: dict) -> dict:
    """
    Run fraud prediction on a single transaction.

    Args:
        features: Dict of transaction features

    Returns:
        Dict with prediction (int), label (str), confidence_score (float)

    Raises:
        RuntimeError: If model is not loaded (FR-014)
        ValueError: If features are incompatible
    """
    if _model_artefact is None:
        raise RuntimeError("Model is not loaded. Cannot make predictions.")

    model = _model_artefact["model"]
    feature_names = _model_artefact["feature_names"]
    label_encoders = _model_artefact["label_encoders"]

    # Build feature vector in the correct order
    feature_values = {}
    for fname in feature_names:
        value = features.get(fname)

        # Apply label encoding for categorical features
        if fname in label_encoders:
            le = label_encoders[fname]
            if value is None:
                # Use the mode (most common class from training)
                value = le.transform([le.classes_[0]])[0]
            else:
                str_val = str(value)
                if str_val in le.classes_:
                    value = le.transform([str_val])[0]
                else:
                    # Unknown category → use most common
                    value = le.transform([le.classes_[0]])[0]
        else:
            # Numeric feature — use 0.0 for missing (median was used in training)
            if value is None:
                value = 0.0
            value = float(value)

        feature_values[fname] = value

    # Create DataFrame with correct column order
    X = pd.DataFrame([feature_values], columns=feature_names)

    # Run prediction
    prediction = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]
    confidence_score = float(probabilities[prediction])

    # FR-013: prediction label
    label = "fraudulent" if prediction == 1 else "legitimate"

    return {
        "prediction": prediction,
        "label": label,
        "confidence_score": round(confidence_score, 4),
    }
