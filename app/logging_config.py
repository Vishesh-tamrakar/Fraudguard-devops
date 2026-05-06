"""
FraudGuard — JSON Structured Logging Configuration
====================================================
SRS Requirements Covered:
- FR-016: JSON formatter using python-json-logger. Every log record includes:
          timestamp, level, message, module, and for predictions:
          transaction_id, prediction, confidence_score, processing_time_ms, client_ip
- FR-017: Log output to both stdout and /var/log/app/fraud.log
- FR-018: INFO for successful predictions, WARN for low-confidence (<0.6),
          ERROR for exceptions
"""

import logging
import os
import sys
from datetime import datetime, timezone

from pythonjsonlogger import json as json_logger


class FraudGuardJsonFormatter(json_logger.JsonFormatter):
    """Custom JSON log formatter for structured logging (FR-016)."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Always include timestamp in ISO 8601 UTC (FR-016)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["module"] = record.module

        # Remove default fields we've replaced
        if "levelname" in log_record:
            del log_record["levelname"]
        if "asctime" in log_record:
            del log_record["asctime"]


def setup_logging() -> logging.Logger:
    """
    Configure application logging with JSON output (FR-016, FR-017).

    Returns:
        Logger instance configured for FraudGuard
    """
    logger = logging.getLogger("fraudguard")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on reload
    if logger.handlers:
        return logger

    formatter = FraudGuardJsonFormatter(
        fmt="%(timestamp)s %(level)s %(message)s %(module)s"
    )

    # FR-017: Handler 1 — stdout (for container runtime capture)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # FR-017: Handler 2 — File at /var/log/app/fraud.log
    log_dir = "/var/log/app"
    log_file = os.path.join(log_dir, "fraud.log")

    # In local dev, fall back to a local directory if /var/log/app doesn't exist
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except PermissionError:
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "fraud.log")

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("FraudGuard logging initialized", extra={"log_file": log_file})

    return logger
