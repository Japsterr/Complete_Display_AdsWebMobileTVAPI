#!/bin/bash

# Backup Script for Display Ads API
# Creates backups of database, media files, and configuration

set -e

BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="$HOME/Complete_Display_AdsWebMobileTVAPI"

echo "💾 Display Ads API - Backup Script"
echo "=================================="
echo "Starting backup: $DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"
cd "$PROJECT_DIR" || exit 1

# Database backup
echo "📊 Backing up database..."
if [ -f "docker-compose.production.yml" ]; then
    docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U displayads_user displayads_prod > "$BACKUP_DIR/db_backup_$DATE.sql"
elif [ -f "docker-compose.yml" ]; then
    docker-compose exec -T postgres pg_dump -U postgres displayads > "$BACKUP_DIR/db_backup_$DATE.sql"
else
    echo "❌ No docker-compose file found"
    exit 1
fi

if [ -s "$BACKUP_DIR/db_backup_$DATE.sql" ]; then
    echo "✅ Database backup created: db_backup_$DATE.sql"
    gzip "$BACKUP_DIR/db_backup_$DATE.sql"
    echo "✅ Database backup compressed"
else
    echo "❌ Database backup failed"
    rm -f "$BACKUP_DIR/db_backup_$DATE.sql"
    exit 1
fi

# Media files backup
echo "📁 Backing up media files..."
if [ -d "media" ] && [ "$(ls -A media)" ]; then
    tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" media/
    echo "✅ Media backup created: media_backup_$DATE.tar.gz"
else
    echo "⚠️ No media files to backup"
fi

# Configuration backup
echo "⚙️ Backing up configuration..."
CONFIG_FILES=""
[ -f ".env.production" ] && CONFIG_FILES="$CONFIG_FILES .env.production"
[ -f "docker-compose.production.yml" ] && CONFIG_FILES="$CONFIG_FILES docker-compose.production.yml"
[ -f "docker-compose.yml" ] && CONFIG_FILES="$CONFIG_FILES docker-compose.yml"
[ -d "nginx" ] && CONFIG_FILES="$CONFIG_FILES nginx/"
[ -f "Dockerfile.prod" ] && CONFIG_FILES="$CONFIG_FILES Dockerfile.prod"

if [ -n "$CONFIG_FILES" ]; then
    tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" $CONFIG_FILES
    echo "✅ Configuration backup created: config_backup_$DATE.tar.gz"
else
    echo "⚠️ No configuration files found to backup"
fi

# Create backup manifest
echo "📋 Creating backup manifest..."
cat > "$BACKUP_DIR/backup_manifest_$DATE.txt" << EOF
Display Ads API Backup Manifest
==============================
Date: $(date)
Host: $(hostname)
User: $(whoami)
Project Directory: $PROJECT_DIR

Files included:
EOF

ls -la "$BACKUP_DIR"/*_$DATE.* >> "$BACKUP_DIR/backup_manifest_$DATE.txt" 2>/dev/null || true

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR"/*_$DATE.* 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "Unknown")
echo "Total backup size: $TOTAL_SIZE" >> "$BACKUP_DIR/backup_manifest_$DATE.txt"

# Cleanup old backups (keep last 7 days)
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.txt" -mtime +7 -delete

# Show backup summary
echo ""
echo "✅ Backup completed successfully!"
echo "Backup files:"
ls -la "$BACKUP_DIR"/*_$DATE.* 2>/dev/null || echo "No backup files found"

echo ""
echo "📊 Backup Summary:"
echo "- Database: $([ -f "$BACKUP_DIR/db_backup_$DATE.sql.gz" ] && echo "✅ Success" || echo "❌ Failed")"
echo "- Media: $([ -f "$BACKUP_DIR/media_backup_$DATE.tar.gz" ] && echo "✅ Success" || echo "⚠️ Skipped")"
echo "- Config: $([ -f "$BACKUP_DIR/config_backup_$DATE.tar.gz" ] && echo "✅ Success" || echo "⚠️ Skipped")"

echo ""
echo "💡 Backup location: $BACKUP_DIR"
echo "📄 Manifest: backup_manifest_$DATE.txt"

# Optional: Upload to cloud storage
if command -v rclone >/dev/null 2>&1 && rclone config show >/dev/null 2>&1; then
    echo ""
    echo "☁️ Uploading to cloud storage..."
    rclone sync "$BACKUP_DIR" remote:displayads-backups --include "*_$DATE.*"
    echo "✅ Cloud backup completed"
fi