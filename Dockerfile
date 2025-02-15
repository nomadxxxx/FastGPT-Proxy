# Stage 1: Build dependencies in venv
FROM python:3.11-slim AS builder

WORKDIR /app

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create user FIRST
RUN useradd -m appuser

# Copy virtual environment with correct chown
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Copy app code
COPY --chown=appuser:appuser ./app /app

# Switch to non-root user
USER appuser

# Start app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.server:app"]