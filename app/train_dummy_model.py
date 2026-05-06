"""
Train a small synthetic RandomForest and save artefact to `app/model.pkl`.

This helper is for local development only: it creates a model object with the
same structure expected by the application (`model`, `feature_names`,
`label_encoders`) so unit tests and runtime can run without the full Kaggle
dataset or Python-version-dependent pickle incompatibilities.

Run: python app/train_dummy_model.py
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Minimal feature set (copied from train.py / schemas for compatibility)
FEATURE_NAMES = [
    "TransactionAmt",
    "TransactionDT",
    "ProductCD",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "addr2",
    "dist1",
    "P_emaildomain",
    "R_emaildomain",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "C8",
    "C9",
    "C10",
    "C11",
    "C12",
    "C13",
    "C14",
    "V1",
    "V2",
    "V3",
    "V4",
    "V5",
    "V12",
    "V13",
    "V14",
    "V36",
    "V37",
    "V38",
    "V54",
    "V55",
    "V56",
    "V75",
    "V76",
    "V77",
    "V78",
    "V282",
    "V283",
]

CAT_FEATURES = ["ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain"]


def make_synthetic_df(n_samples: int = 1000):
    rng = np.random.RandomState(42)

    data = {}
    # Numeric features
    for f in FEATURE_NAMES:
        if f in CAT_FEATURES:
            continue
        # create some numeric variance
        data[f] = rng.normal(loc=0.0, scale=1.0, size=n_samples)

    # Create categorical features with a small set of values
    data["ProductCD"] = rng.choice(["W", "H", "C", "S", "R"], size=n_samples)
    data["card4"] = rng.choice(["visa", "mastercard", "discover"], size=n_samples)
    data["card6"] = rng.choice(["credit", "debit"], size=n_samples)
    data["P_emaildomain"] = rng.choice(["gmail.com", "yahoo.com", "hotmail.com", None], size=n_samples)
    data["R_emaildomain"] = rng.choice(["gmail.com", "yahoo.com", None], size=n_samples)

    df = pd.DataFrame(data)

    # Create synthetic binary target with imbalance (~5% fraud)
    y = (rng.rand(n_samples) < 0.05).astype(int)

    return df, y


def build_label_encoders(df: pd.DataFrame):
    encoders = {}
    for col in CAT_FEATURES:
        le = LabelEncoder()
        # Fillna with string for encoder compatibility
        series = df[col].fillna("__missing__").astype(str)
        le.fit(series)
        encoders[col] = le
    return encoders


def prepare_X(df: pd.DataFrame, encoders: dict):
    X = df.copy()
    for col, le in encoders.items():
        X[col] = le.transform(X[col].fillna("__missing__").astype(str))

    # Ensure column ordering
    X = X[FEATURE_NAMES]
    return X


def main():
    print("Training synthetic RF model for local tests...")
    df, y = make_synthetic_df(2000)
    encoders = build_label_encoders(df)
    X = prepare_X(df, encoders)

    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=10,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    artefact = {"model": model, "label_encoders": encoders, "feature_names": FEATURE_NAMES}

    out_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump(artefact, out_path)
    print(f"Wrote synthetic model to: {out_path}")


if __name__ == "__main__":
    main()
