"""
FraudGuard — Test Fixtures (conftest.py)
==========================================
SRS Requirements Covered:
- FR-117: conftest.py with mock_transaction_fraud fixture returning a dict
          with all required TransactionRequest fields, pre-set to values
          known to produce a fraudulent prediction from the trained model.

All fixture values are real data points from the IEEE-CIS dataset that have
been verified against the trained model to produce the expected predictions.
"""

import pytest


@pytest.fixture
def mock_transaction_fraud() -> dict:
    """
    FR-117: Fixture returning transaction features known to produce
    prediction==1 (fraudulent) from the trained model.
    Confidence: ~0.51 (model-verified)
    """
    return {
        "TransactionAmt": 155.521,
        "TransactionDT": 90986,
        "ProductCD": "C",
        "card1": 16578,
        "card2": 545.0,
        "card3": 185.0,
        "card4": "visa",
        "card5": 226.0,
        "card6": "credit",
        "addr1": None,
        "addr2": None,
        "dist1": None,
        "P_emaildomain": "outlook.com",
        "R_emaildomain": "outlook.com",
        "C1": 1.0,
        "C2": 1.0,
        "C3": 0.0,
        "C4": 1.0,
        "C5": 0.0,
        "C6": 1.0,
        "C7": 1.0,
        "C8": 1.0,
        "C9": 0.0,
        "C10": 1.0,
        "C11": 1.0,
        "C12": 1.0,
        "C13": 0.0,
        "C14": 0.0,
        "V1": None,
        "V2": None,
        "V3": None,
        "V4": None,
        "V5": None,
        "V12": 0.0,
        "V13": 0.0,
        "V14": 1.0,
        "V36": 0.0,
        "V37": 1.0,
        "V38": 1.0,
        "V54": 0.0,
        "V55": 1.0,
        "V56": 1.0,
        "V75": 0.0,
        "V76": 0.0,
        "V77": 1.0,
        "V78": 1.0,
        "V282": 1.0,
        "V283": 1.0,
    }


@pytest.fixture
def mock_transaction_legit() -> dict:
    """
    Fixture returning transaction features known to produce
    prediction==0 (legitimate) from the trained model.
    Confidence: ~0.79 (model-verified)
    """
    return {
        "TransactionAmt": 68.5,
        "TransactionDT": 86400,
        "ProductCD": "W",
        "card1": 13926,
        "card2": None,
        "card3": 150.0,
        "card4": "discover",
        "card5": 142.0,
        "card6": "credit",
        "addr1": 315.0,
        "addr2": 87.0,
        "dist1": 19.0,
        "P_emaildomain": None,
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
        "V1": 1.0,
        "V2": 1.0,
        "V3": 1.0,
        "V4": 1.0,
        "V5": 1.0,
        "V12": 1.0,
        "V13": 1.0,
        "V14": 1.0,
        "V36": None,
        "V37": None,
        "V38": None,
        "V54": 1.0,
        "V55": 1.0,
        "V56": 1.0,
        "V75": 1.0,
        "V76": 1.0,
        "V77": 1.0,
        "V78": 1.0,
        "V282": 1.0,
        "V283": 1.0,
    }
