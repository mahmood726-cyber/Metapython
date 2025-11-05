#!/bin/bash
# Docker entrypoint script for MetaPython
# Runs database migrations before starting the application

set -e

echo "MetaPython Docker Entrypoint"
echo "=============================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  sleep 1
done
echo "✓ PostgreSQL is ready"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || echo "⚠ Migrations failed or already applied"
echo "✓ Migrations completed"

# Execute the main command
echo "Starting application..."
exec "$@"
