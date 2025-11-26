# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies (cached layer)
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY windguru.py ./

# Set Python path
ENV PATH="/app/.venv/bin:$PATH"

# Create output directory
RUN mkdir -p /app/output

# Run as non-root user for security
RUN useradd -m -u 1000 windguru && chown -R windguru:windguru /app
USER windguru

ENTRYPOINT ["python", "windguru.py"]