# Use a slim Python 3.13 image as the base
FROM python:3.13-slim

# Copy the uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies needed for Playwright / Firefox / Camoufox
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy files needed for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies (without dev dependencies)
RUN uv sync --frozen --no-install-project --no-dev

# Place the virtual environment's bin folder at the beginning of the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Install Firefox system dependencies for Playwright/Camoufox
#RUN playwright install-deps firefox

# Fetch the Camoufox browser binaries
#RUN python -m camoufox fetch

# Copy the rest of the application code
COPY app/ ./app/
COPY main.py ./

# Expose the API port
EXPOSE 8000

# Set environment variables (can be overridden at runtime)
ENV LOG_LEVEL="INFO"

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
