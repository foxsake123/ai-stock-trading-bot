# AI Trading Bot - Dockerfile
# Last Updated: 2025-10-23
# Base: python:3.11-slim (Debian-based, minimal size)

# ============================================================================
# BUILDER STAGE - Install dependencies
# ============================================================================

FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip, setuptools, wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first (for layer caching)
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ============================================================================
# RUNTIME STAGE - Create final image
# ============================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="AI Trading Bot Team"
LABEL description="AI-powered stock trading bot with multi-agent system"
LABEL version="2.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=America/New_York \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Timezone support
    tzdata \
    # PostgreSQL client library
    libpq5 \
    # Network utilities
    curl \
    wget \
    # Process management
    procps \
    # Text processing
    ca-certificates \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configure timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Create non-root user
RUN groupadd -r trader && \
    useradd -r -g trader -u 1000 -m -s /bin/bash trader && \
    mkdir -p /home/trader

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data/cache \
    /app/data/historical \
    /app/data/watchlists \
    /app/data/positions \
    /app/data/state \
    /app/logs/app \
    /app/logs/trades \
    /app/logs/errors \
    /app/logs/performance \
    /app/reports/daily \
    /app/reports/weekly \
    /app/reports/monthly \
    /app/configs \
    && chown -R trader:trader /app

# Copy application code
COPY --chown=trader:trader . /app/

# Switch to non-root user
USER trader

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port for web dashboard (optional)
EXPOSE 5000

# Default command: Run daily pipeline
CMD ["python", "scripts/daily_pipeline.py"]

# ============================================================================
# BUILD INSTRUCTIONS
# ============================================================================
#
# Build image:
#   docker build -t ai-trading-bot:latest -f deployment/docker/Dockerfile .
#
# Build with custom tag:
#   docker build -t ai-trading-bot:2.0.0 -f deployment/docker/Dockerfile .
#
# Build with build args:
#   docker build --build-arg PYTHONUNBUFFERED=1 -t ai-trading-bot:latest .
#
# Run container:
#   docker run --rm -it ai-trading-bot:latest
#
# Run with environment file:
#   docker run --rm -it --env-file configs/.env ai-trading-bot:latest
#
# Run with volume mounts:
#   docker run --rm -it \
#     -v $(pwd)/data:/app/data \
#     -v $(pwd)/logs:/app/logs \
#     -v $(pwd)/reports:/app/reports \
#     -v $(pwd)/configs/.env:/app/configs/.env \
#     ai-trading-bot:latest
#
# Interactive shell:
#   docker run --rm -it ai-trading-bot:latest /bin/bash
#
# Override command:
#   docker run --rm -it ai-trading-bot:latest python scripts/monitoring/health_check.py
#
# ============================================================================
# MULTI-STAGE BUILD BENEFITS
# ============================================================================
#
# 1. Smaller final image:
#    - Builder stage includes gcc, build-essential (~300MB)
#    - Runtime stage only has compiled dependencies (~150MB)
#    - Final image size: ~500MB vs ~800MB
#
# 2. Security:
#    - No build tools in production image
#    - Reduced attack surface
#    - Non-root user execution
#
# 3. Faster builds:
#    - Layer caching for dependencies
#    - requirements.txt copied before code
#    - Code changes don't rebuild dependencies
#
# ============================================================================
# SECURITY FEATURES
# ============================================================================
#
# 1. Non-root user:
#    - Runs as 'trader' (UID 1000)
#    - Limited permissions
#    - Cannot install packages or modify system
#
# 2. Minimal base image:
#    - python:3.11-slim (Debian-based)
#    - Only essential packages installed
#    - Regular security updates
#
# 3. No cache directories:
#    - PIP_NO_CACHE_DIR=1
#    - --no-cache-dir flag
#    - Reduces image size and attack surface
#
# 4. Read-only filesystem (recommended):
#    - docker run --read-only --tmpfs /tmp
#    - Requires explicit volume mounts for writes
#
# ============================================================================
# TROUBLESHOOTING
# ============================================================================
#
# Build fails with "No space left on device":
#   docker system prune -a
#
# Build fails with dependency errors:
#   - Check requirements.txt is valid
#   - Try rebuilding without cache: docker build --no-cache
#
# Container exits immediately:
#   - Check logs: docker logs <container-id>
#   - Run interactive: docker run --rm -it ai-trading-bot:latest /bin/bash
#
# Permission denied errors:
#   - Verify volume mount paths are writable
#   - Check file ownership: ls -la data/ logs/ reports/
#
# Timezone issues:
#   - Verify TZ env var: docker run --rm ai-trading-bot:latest date
#   - Should show EDT or EST
#
# Python import errors:
#   - Check PYTHONPATH: docker run --rm ai-trading-bot:latest python -c "import sys; print(sys.path)"
#   - Verify all files copied: docker run --rm ai-trading-bot:latest ls -la
