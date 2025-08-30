#!/bin/bash

# System Status Monitor Script
# Check the health of all Display Ads API services

echo "🔍 Display Ads API - System Status"
echo "=================================="
echo "Timestamp: $(date)"
echo ""

# Check Docker service
echo "🐋 Docker Status:"
if systemctl is-active --quiet docker; then
    echo "✅ Docker service is running"
else
    echo "❌ Docker service is not running"
    exit 1
fi

echo ""

# Check container status
echo "📦 Container Status:"
cd ~/Complete_Display_AdsWebMobileTVAPI || cd ~/project 2>/dev/null || true

if [ -f "docker-compose.production.yml" ]; then
    docker-compose -f docker-compose.production.yml ps
elif [ -f "docker-compose.yml" ]; then
    docker-compose ps
else
    echo "⚠️ No docker-compose file found, showing all containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

echo ""

# Check system resources
echo "💻 System Resources:"
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print "  " $2}' || echo "  Unable to get CPU info"

echo "Memory Usage:"
free -h | awk 'NR==2{printf "  Used: %s/%s (%.1f%%)\n", $3,$2,$3*100/$2}'

echo "Disk Usage:"
df -h | awk '$NF=="/" {printf "  Root: %s/%s (%s used)\n", $3,$2,$5}'

echo ""

# Check network connectivity
echo "🌐 Network Status:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ | grep -q "200"; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
fi

if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
        echo "✅ Redis connection successful"
    else
        echo "❌ Redis connection failed"
    fi
else
    echo "⚠️ redis-cli not available for testing"
fi

echo ""

# Check logs for errors
echo "📋 Recent Errors (last 10):"
if [ -f "docker-compose.production.yml" ]; then
    docker-compose -f docker-compose.production.yml logs --tail=50 2>/dev/null | grep -i error | tail -10 || echo "  No recent errors found"
elif [ -f "docker-compose.yml" ]; then
    docker-compose logs --tail=50 2>/dev/null | grep -i error | tail -10 || echo "  No recent errors found"
else
    echo "  Unable to check logs - no docker-compose file found"
fi

echo ""

# Storage usage
echo "💾 Storage Usage:"
if [ -d "media" ]; then
    echo "  Media files: $(du -sh media 2>/dev/null | cut -f1 || echo 'Unknown')"
fi
if [ -d "logs" ]; then
    echo "  Log files: $(du -sh logs 2>/dev/null | cut -f1 || echo 'Unknown')"
fi
if [ -d "backups" ]; then
    echo "  Backups: $(du -sh backups 2>/dev/null | cut -f1 || echo 'Unknown')"
fi

echo ""
echo "✨ Status check complete!"

# Return appropriate exit code
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ | grep -q "200"; then
    exit 0
else
    exit 1
fi