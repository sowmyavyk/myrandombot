# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --no-user -r requirements.txt


# ============================================
# Stage 2: Production - Minimal runtime
# ============================================
FROM python:3.11-slim AS production

# Security: Run as non-root user
RUN groupadd -r femicase && useradd -r -g femicase femicase

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY --chown=femicase:femicase . .

# Create data directory with proper permissions
RUN mkdir -p /app/data && chown -R femicase:femicase /app

# Switch to non-root user
USER femicase

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn workers via gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120", "server:app"]
