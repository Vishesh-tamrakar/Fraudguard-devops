"""
FraudGuard Model Training Script
=================================
Trains a Random Forest classifier on the IEEE-CIS Fraud Detection dataset.

SRS Requirements Covered:
- FR-001: Uses IEEE-CIS Fraud Detection dataset (590,540 records, 434 features)
- FR-002: Feature engineering with ≥30 features, median/mode imputation, LabelEncoder
- FR-003: 80:20 train-test split with random_state=42
- FR-004: RandomForestClassifier with specified hyperparameters
- FR-005: Outputs classification report with precision, recall, F1, ROC-AUC
- FR-006: Validates ROC-AUC ≥ 0.85 (exits non-zero if below threshold)
- FR-007: Serializes model with joblib.dump()

Usage:
    python train.py --data-dir ../data --output model.pkl
"""

import argparse
import sys
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import joblib

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# FR-002: Feature Selection — Top 30+ features selected for the model
# ---------------------------------------------------------------------------
SELECTED_FEATURES = [
    # Transaction amount and time
    "TransactionAmt", "TransactionDT",
    # Product code
    "ProductCD",
    # Card features
    "card1", "card2", "card3", "card4", "card5", "card6",
    # Address features
    "addr1", "addr2",
    # Distance
    "dist1",
    # Email domains
    "P_emaildomain", "R_emaildomain",
    # Count features
    "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9",
    "C10", "C11", "C12", "C13", "C14",
    # V features (engineered by Vesta)
    "V1", "V2", "V3", "V4", "V5",
    "V12", "V13", "V14",
    "V36", "V37", "V38",
    "V54", "V55", "V56",
    "V75", "V76", "V77", "V78",
    "V282", "V283",
]

TARGET = "isFraud"


def load_data(data_dir: str) -> pd.DataFrame:
    """Load and merge transaction + identity tables (FR-001, FR-002)."""
    print("[1/6] Loading dataset...")

    transaction_path = os.path.join(data_dir, "train_transaction.csv")
    identity_path = os.path.join(data_dir, "train_identity.csv")

    if not os.path.exists(transaction_path):
        raise FileNotFoundError(f"Transaction file not found: {transaction_path}")
    if not os.path.exists(identity_path):
        raise FileNotFoundError(f"Identity file not found: {identity_path}")

    # Load only the columns we need + TransactionID + target
    transaction_cols = [TARGET, "TransactionID"] + [
        f for f in SELECTED_FEATURES if f in pd.read_csv(transaction_path, nrows=0).columns
    ]
    identity_cols = ["TransactionID"] + [
        f for f in SELECTED_FEATURES if f in pd.read_csv(identity_path, nrows=0).columns
    ]

    df_trans = pd.read_csv(transaction_path, usecols=transaction_cols)
    df_id = pd.read_csv(identity_path, usecols=identity_cols)

    # Merge on TransactionID (FR-002)
    df = df_trans.merge(df_id, on="TransactionID", how="left")
    print(f"    Merged dataset: {len(df)} records, {len(df.columns)} columns")
    print(f"    Fraud rate: {df[TARGET].mean() * 100:.2f}%")

    return df


def engineer_features(df: pd.DataFrame) -> tuple:
    """
    Feature engineering: imputation + encoding (FR-002).

    Returns:
        X: Feature matrix (DataFrame)
        y: Target vector (Series)
        feature_names: List of final feature names
        label_encoders: Dict of fitted LabelEncoders (for inference)
    """
    print("[2/6] Engineering features...")

    # Separate target
    y = df[TARGET].copy()
    X = df.drop(columns=[TARGET, "TransactionID"], errors="ignore")

    # Keep only selected features that exist in the dataframe
    available_features = [f for f in SELECTED_FEATURES if f in X.columns]
    X = X[available_features]

    # Identify numeric and categorical columns
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

    # FR-002: Median imputation for numeric features
    for col in numeric_cols:
        median_val = X[col].median()
        X[col] = X[col].fillna(median_val)

    # FR-002: Mode imputation for categorical features + LabelEncoder
    label_encoders = {}
    for col in categorical_cols:
        mode_val = X[col].mode()[0] if not X[col].mode().empty else "unknown"
        X[col] = X[col].fillna(mode_val)

        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    feature_names = X.columns.tolist()
    print(f"    Final features: {len(feature_names)} "
          f"({len(numeric_cols)} numeric, {len(categorical_cols)} categorical)")

    return X, y, feature_names, label_encoders


def train_model(X_train, y_train) -> RandomForestClassifier:
    """
    Train Random Forest with SRS-specified hyperparameters (FR-004).
    """
    print("[3/6] Training Random Forest classifier...")
    print("    Hyperparameters: n_estimators=100, max_depth=20, "
          "min_samples_split=5, class_weight='balanced', random_state=42")

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        class_weight="balanced",  # Handle class imbalance
        random_state=42,
        n_jobs=-1,  # Use all CPU cores for faster training
    )

    model.fit(X_train, y_train)
    print("    Training complete.")
    return model


def evaluate_model(model, X_test, y_test) -> float:
    """
    Evaluate model and output classification report (FR-005, FR-006).

    Returns:
        roc_auc: ROC-AUC score
    """
    print("[4/6] Evaluating model...")

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # FR-005: Output classification report
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Fraudulent"]))

    # FR-005: ROC-AUC score
    roc_auc = roc_auc_score(y_test, y_proba)
    print(f"ROC-AUC Score: {roc_auc:.4f}")
    print("=" * 60)

    return roc_auc


def save_model(model, label_encoders, feature_names, output_path: str):
    """
    Serialize model artefact using joblib (FR-007).

    Saves a dict containing:
    - model: The trained RandomForestClassifier
    - label_encoders: Dict of LabelEncoders for categorical features
    - feature_names: Ordered list of feature names expected by the model
    """
    print(f"[5/6] Serializing model to {output_path}...")

    artefact = {
        "model": model,
        "label_encoders": label_encoders,
        "feature_names": feature_names,
    }

    joblib.dump(artefact, output_path)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"    Saved: {output_path} ({file_size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="FraudGuard Model Training")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "data"),
        help="Path to directory containing train_transaction.csv and train_identity.csv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "model.pkl"),
        help="Output path for the serialized model",
    )
    parser.add_argument(
        "--min-roc-auc",
        type=float,
        default=0.85,
        help="Minimum ROC-AUC threshold (FR-006, default: 0.85)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("FraudGuard — Model Training Pipeline")
    print("=" * 60)

    # Step 1: Load data (FR-001)
    df = load_data(args.data_dir)

    # Step 2: Feature engineering (FR-002)
    X, y, feature_names, label_encoders = engineer_features(df)

    # Step 3: Train-test split (FR-003): 80:20, random_state=42
    print("[3/6] Splitting data (80:20, random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"    Train: {len(X_train)} | Test: {len(X_test)}")

    # Step 4: Train model (FR-004)
    model = train_model(X_train, y_train)

    # Step 5: Evaluate (FR-005, FR-006)
    roc_auc = evaluate_model(model, X_test, y_test)

    # FR-006: Validate ROC-AUC threshold
    if roc_auc < args.min_roc_auc:
        print(f"\n❌ FAILED: ROC-AUC {roc_auc:.4f} is below threshold {args.min_roc_auc}")
        print("Model will NOT be saved. Exiting with error.")
        sys.exit(1)

    print(f"\n✅ PASSED: ROC-AUC {roc_auc:.4f} >= {args.min_roc_auc}")

    # Step 6: Save model (FR-007)
    save_model(model, label_encoders, feature_names, args.output)

    print("\n[6/6] Training pipeline complete!")
    print(f"    Model saved to: {args.output}")
    print(f"    Features: {len(feature_names)}")
    print(f"    ROC-AUC: {roc_auc:.4f}")


if __name__ == "__main__":
    main()
