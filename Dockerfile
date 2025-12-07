# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Set working directory
WORKDIR /app

# Copy all application code
COPY . .

# Install dependencies with uv
RUN uv pip install .

# Expose ports
EXPOSE 8000 7860

# Default command
CMD ["python", "-m", "src.main"]
