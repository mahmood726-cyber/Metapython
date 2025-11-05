# MetaPython Dockerfile
# Multi-stage build for production deployment

# ========================================
# Stage 1: Base Image with R and Python
# ========================================
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libxml2-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    r-base \
    r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ========================================
# Stage 2: Python Dependencies
# ========================================
FROM base as python-deps

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for production
RUN pip install --no-cache-dir \
    gunicorn \
    uvicorn[standard] \
    psycopg2-binary \
    redis

# ========================================
# Stage 3: R Dependencies
# ========================================
FROM python-deps as r-deps

# Install R packages
RUN R -e "install.packages(c( \
    'metafor', \
    'meta', \
    'netmeta', \
    'gemtc', \
    'mada', \
    'dosresmeta', \
    'shiny', \
    'rjags' \
    ), repos='https://cloud.r-project.org/')"

# ========================================
# Stage 4: Application
# ========================================
FROM r-deps as app

# Copy application code
COPY metapython/ ./metapython/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# Install MetaPython package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 metapython && \
    chown -R metapython:metapython /app

USER metapython

# Expose ports
EXPOSE 8000 3000 3838

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "metapython.web_api.app:app", "--host", "0.0.0.0", "--port", "8000"]

# ========================================
# Stage 5: Frontend (Optional)
# ========================================
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ========================================
# Stage 6: Production
# ========================================
FROM app as production

# Copy built frontend
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=postgresql://metapython:password@postgres:5432/metapython \
    REDIS_URL=redis://redis:6379/0

# Run database migrations on startup
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "metapython.web_api.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
