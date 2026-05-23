# ===============================================
# Development Environment Setup Script
# ===============================================
#!/bin/bash
set -e

echo "=========================================="
echo "43V3R CORE - Development Environment"
echo "=========================================="

# Check for required tools
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed."; exit 1; }

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp backend/.env.example .env
    echo "Please edit .env with your preferred settings"
fi

# Create necessary directories
echo "Creating storage directories..."
mkdir -p storage/media storage/assets storage/temp

# Start services
echo "Starting Docker services..."
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "Running database migrations..."
docker-compose -f infrastructure/docker/docker-compose.yml exec backend alembic upgrade head

echo ""
echo "=========================================="
echo "Development environment is ready!"
echo ""
echo "Services:"
echo "  - Backend API:  http://localhost:8000"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - Frontend:     http://localhost:3000"
echo "  - PostgreSQL:   localhost:5432"
echo "  - Redis:        localhost:6379"
echo "=========================================="