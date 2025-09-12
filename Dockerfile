# Metapython v0.8 - Production Meta-Analysis Platform
FROM python:3.11-slim

LABEL maintainer="PyMeta-CBAMM Development Team <pymeta-cbamm@example.com>"
LABEL version="0.8.0"
LABEL description="Production-ready meta-analysis platform"

# Security: Create non-root user
RUN groupadd -r metapython && useradd -r -g metapython metapython

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .[all]

# Copy application code
COPY metapython.py ./

# Create directories for data and outputs
RUN mkdir -p /app/data /app/outputs && \
    chown -R metapython:metapython /app

# Switch to non-root user
USER metapython

# Environment configuration
ENV PYTHONPATH=/app
ENV METAPYTHON_TELEMETRY=false
ENV METAPYTHON_PRIVACY_MODE=strict

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import metapython; print('OK')" || exit 1

# Expose port for web interface (if enabled)
EXPOSE 8501

# Default command
CMD ["python", "-c", "import metapython; print(f'Metapython v{metapython.__version__} ready')"]