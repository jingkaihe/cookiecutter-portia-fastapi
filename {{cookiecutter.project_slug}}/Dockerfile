{%- if cookiecutter.use_docker == 'y' %}
# Use Python {{ cookiecutter.python_version }} slim image for smaller size
FROM python:{{ cookiecutter.python_version }}-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./
# Copy uv.lock if it exists for reproducible builds
COPY uv.lock* ./

# Install Python dependencies (production only, no dev dependencies)
RUN uv sync --no-group dev

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE {{ cookiecutter.port }}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:{{ cookiecutter.port }}/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{{ cookiecutter.port }}"]
{%- else %}
# Docker support not included. To add Docker support, create a Dockerfile.
{%- endif %}