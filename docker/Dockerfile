# FraudGuard — FastAPI Application Dockerfile
# SRS Requirements Covered:
# - FR-019: Uses python slim base image
# - FR-020: Multi-stage build to keep image under 600 MB
# - FR-021: WORKDIR /app, runs as non-root user (appuser)
# - FR-022: Creates /var/log/app and sets ownership
# - FR-023: EXPOSE 8000, CMD uvicorn main:app
# - FR-009: COPY model.pkl into the image

# Note: Use python:3.10-slim to match the project's runtime and current model.pkl.
# Pickles are generally not forward compatible across major/minor Python versions.

# -----------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------
FROM python:3.10-slim AS builder

WORKDIR /build

# Set environment variables to prevent Python from writing .pyc files and
# to keep pip quiet
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for compiling Python packages (if any)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirements
# (Copy only requirements to cache this layer)
COPY app/requirements.txt .
RUN pip install -r requirements.txt


# -----------------------------------------------------------------------
# Stage 2: Final
# -----------------------------------------------------------------------
FROM python:3.10-slim

WORKDIR /code

# FR-021: Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# FR-022: Create logging directory and set permissions
RUN mkdir -p /var/log/app && chown -R appuser:appuser /var/log/app

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY --chown=appuser:appuser app/ /code/app/

# Remove the training dataset from the container just in case it was accidentally 
# added to the app folder, to keep image size small (FR-020)
RUN rm -f /code/app/train.py

# Switch to the non-root user
USER appuser

# FR-023: Expose port 8000
EXPOSE 8000

# FR-023: Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
