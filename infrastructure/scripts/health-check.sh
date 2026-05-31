#!/bin/bash
# ===============================================
# 43V3R CORE - System Health Check Script
# ===============================================

set -e

echo "🔍 Running 43V3R CORE health checks..."
echo ""

# Check API health
echo "📡 Checking API..."
if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "  ✅ API is healthy"
else
    echo "  ❌ API is not responding"
fi

# Check Web health
echo "📡 Checking Web..."
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Web is healthy"
else
    echo "  ❌ Web is not responding"
fi

# Check Database
echo "📡 Checking Database..."
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    echo "  ✅ Database is healthy"
else
    echo "  ❌ Database is not responding"
fi

# Check Redis
echo "📡 Checking Redis..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Redis is healthy"
else
    echo "  ❌ Redis is not responding"
fi

echo ""
echo "✅ Health check complete"