# ===============================================
# 43V3R CORE - Developer Makefile
# ===============================================

.PHONY: help install dev setup build up down logs clean test lint format check db-reset db-migrate backup health

# Default target
help:
	@echo "43V3R CORE - Available Commands"
	@echo ""
	@echo "  make install      - Install dependencies for all packages"
	@echo "  make dev          - Start development environment"
	@echo "  make setup        - Initial setup and configuration"
	@echo "  make build        - Build all Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View service logs"
	@echo "  make clean        - Clean up containers and volumes"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make check        - Run all checks (lint, type-check, tests)"
	@echo "  make db-reset     - Reset database"
	@echo "  make db-migrate   - Run database migrations"
	@echo "  make backup       - Create database backup"
	@echo "  make health       - Run health checks"

# Installation
install:
	@echo "📦 Installing dependencies..."
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install
	cd packages/ui && npm install
	cd packages/types && npm install
	@echo "✅ Installation complete"

# Development environment
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f infrastructure/docker/docker-compose.yml up -d
	@echo "✅ Services started"

# Initial setup
setup:
	@echo "🔧 Running initial setup..."
	bash infrastructure/scripts/setup-dev.sh

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose -f infrastructure/docker/docker-compose.yml build

# Start services
up:
	@echo "📦 Starting services..."
	docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Stop services
down:
	@echo "🛑 Stopping services..."
	docker-compose -f infrastructure/docker/docker-compose.yml down

# View logs
logs:
	docker-compose -f infrastructure/docker/docker-compose.yml logs -f

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f infrastructure/docker/docker-compose.yml down -v
	docker system prune -f
	@echo "✅ Clean complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	cd apps/api && pytest tests/ -v
	cd apps/web && npm run test

# Run linters
lint:
	@echo "🔍 Running linters..."
	cd apps/api && ruff check app/
	cd apps/web && npm run lint

# Format code
format:
	@echo "✨ Formatting code..."
	cd apps/api && ruff format app/
	cd apps/web && npm run format

# Run all checks
check: lint test

# Database reset
db-reset:
	@echo "⚠️  Resetting database..."
	bash infrastructure/scripts/reset-db.sh

# Database migrations
db-migrate:
	@echo "🔄 Running migrations..."
	bash infrastructure/scripts/run-migrations.sh

# Create backup
backup:
	@echo "📦 Creating backup..."
	bash infrastructure/scripts/backup.sh

# Health check
health:
	@echo "🔍 Running health checks..."
	bash infrastructure/scripts/health-check.sh

# Production build
prod-build:
	@echo "🔨 Building production images..."
	docker-compose -f infrastructure/docker/docker-compose.yml -f infrastructure/docker/docker-compose.prod.yml build

# Production up
prod-up:
	@echo "🚀 Starting production environment..."
	docker-compose -f infrastructure/docker/docker-compose.yml -f infrastructure/docker/docker-compose.prod.yml up -d

# Shell into API container
api-shell:
	docker-compose -f infrastructure/docker/docker-compose.yml exec backend /bin/bash

# Shell into worker container
worker-shell:
	docker-compose -f infrastructure/docker/docker-compose.yml exec worker /bin/bash