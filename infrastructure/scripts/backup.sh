#!/bin/bash
# ===============================================
# 43V3R CORE - Backup Script
# ===============================================

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="verse_backup_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

# Database backup
echo "📦 Backing up database..."
docker-compose exec -T postgres pg_dump -U verse > "${BACKUP_DIR}/${BACKUP_NAME}_db.sql"

# Compress backup
echo "📦 Compressing backup..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
    "${BACKUP_DIR}/${BACKUP_NAME}_db.sql"

# Clean up SQL file
rm "${BACKUP_DIR}/${BACKUP_NAME}_db.sql"

# Clean old backups (keep last 7)
cd "$BACKUP_DIR"
ls -t | tail -n +8 | xargs -r rm -f

echo "✅ Backup complete: ${BACKUP_NAME}.tar.gz"