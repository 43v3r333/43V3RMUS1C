#!/bin/bash
# ===============================================
# 43V3R CORE - Database Reset Script
# ===============================================

set -e

echo "⚠️  This will reset the database. All data will be lost."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

cd "$(dirname "$0")/../apps/api"

# Downgrade all migrations
echo "🔄 Reverting all migrations..."
alembic downgrade base

# Upgrade to latest
echo "🔄 Running migrations..."
alembic upgrade head

echo "✅ Database reset complete"