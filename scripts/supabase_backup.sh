#!/bin/bash
# Supabase Database Backup Script
# Generated by IGN Scripts Data Integration System

set -e

# Configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="ignition"
DB_USER="postgres"
BACKUP_DIR="supabase-data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/supabase_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create database backup
echo "Creating Supabase database backup..."
PGPASSWORD="ignition-supabase" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --verbose \
    --clean \
    --no-owner \
    --no-privileges \
    > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE.gz"

# Clean up old backups (keep last 7 days)
find "$BACKUP_DIR" -name "supabase_backup_*.sql.gz" -mtime +7 -delete
echo "Cleaned up old backups"

echo "Supabase backup completed successfully!"
