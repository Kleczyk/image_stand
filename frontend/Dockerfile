# Dockerfile for Streamlit frontend
FROM python:3.12-slim

# Copy uv from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src
COPY frontend ./frontend

# Create images directory
RUN mkdir -p /app/images

# Install dependencies
RUN uv pip install --system streamlit requests pillow

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

