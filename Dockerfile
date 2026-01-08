# Multi-stage Dockerfile for yt-transcribe
# Optimized for size and security

# Base stage with common dependencies
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 ytuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir yt-dlp

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov pytest-asyncio pytest-mock black mypy

# Copy source code
COPY --chown=ytuser:ytuser . .

# Install package in development mode
RUN pip install -e .

# Switch to non-root user
USER ytuser

# Production stage
FROM base as production

# Copy source code
COPY --chown=ytuser:ytuser src /app/src
COPY --chown=ytuser:ytuser pyproject.toml /app/
COPY --chown=ytuser:ytuser README.md /app/

# Install package
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER ytuser

# Create config directory
RUN mkdir -p /home/ytuser/.yt-transcribe

# Set entrypoint
ENTRYPOINT ["yt-transcribe"]
CMD ["--help"]

# Expose any necessary ports (none for this CLI app)
# EXPOSE 8080

# Health check (optional - for future web UI)
# HEALTHCHECK --interval=30s --timeout=3s \
#   CMD yt-transcribe --version || exit 1
