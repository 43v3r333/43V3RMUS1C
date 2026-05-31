#!/bin/bash
# ===============================================
# 43V3R CORE - Database Migration Script
# ===============================================

set -e

cd "$(dirname "$0")/../apps/api"

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Generate initial migration if needed
if [ "$1" == "--generate" ]; then
    echo "📝 Generating new migration..."
    alembic revision --autogenerate -m "$2"
fi

echo "✅ Migrations complete"