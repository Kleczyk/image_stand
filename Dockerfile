# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Install system dependencies required for PyTorch and image processing
# libgomp1 is required for PyTorch's OpenMP support
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Set working directory
WORKDIR /app

# Copy pyproject.toml first for better caching
COPY pyproject.toml ./

# Install only dependencies (not the package itself) to avoid build issues
RUN uv pip install --system \
    fastapi \
    "uvicorn[standard]" \
    httpx \
    pillow \
    python-multipart \
    python-dotenv \
    scikit-image \
    numpy \
    langgraph \
    langchain-core \
    pydantic \
    streamlit \
    torch \
    transformers

# Copy all application code
COPY . .

# Set PYTHONPATH so we can import src modules
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose ports
EXPOSE 8000 7860

# Default command
CMD ["python", "-m", "src.main"]
