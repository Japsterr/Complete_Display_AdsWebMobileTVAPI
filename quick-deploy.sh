#!/bin/bash

# Quick Deploy Script for Ubuntu Production
# Run this script on your Ubuntu server after following the deployment guide

set -e

echo "🚀 Display Ads API - Quick Deploy Script"
echo "========================================"

# Check if running as displayads user
if [ "$USER" != "displayads" ]; then
    echo "❌ This script should be run as the 'displayads' user"
    echo "   Switch to displayads user: sudo su - displayads"
    exit 1
fi

# Check if in correct directory
if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ docker-compose.production.yml not found"
    echo "   Make sure you're in the project directory"
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production not found"
    echo "   Copy .env.production.example and configure it first"
    exit 1
fi

echo "✅ Pre-checks passed"

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin latest-code

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs nginx/conf.d certbot/{conf,www} backups static media

# Build and start services
echo "🐋 Building and starting Docker services..."
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T api python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
docker-compose -f docker-compose.production.yml exec -T api python manage.py shell -c "
from api.models import User
if not User.objects.filter(email='admin@example.com').exists():
    admin = User.objects.create_superuser('admin@example.com', 'admin123')
    print('✅ Admin user created: admin@example.com/admin123')
else:
    print('✅ Admin user already exists')
"

# Collect static files
echo "📦 Collecting static files..."
docker-compose -f docker-compose.production.yml exec -T api python manage.py collectstatic --noinput

# Show status
echo "📊 Service Status:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo "🌐 API Health: curl http://localhost:8000/health/"
echo "🔐 Admin Panel: http://localhost:8000/admin/"
echo "👤 Admin Login: admin@example.com / admin123"
echo ""
echo "⚠️  Next Steps:"
echo "   1. Configure your domain in nginx/conf.d/default.conf"
echo "   2. Setup SSL certificates with Let's Encrypt"
echo "   3. Update firewall rules for production"
echo "   4. Setup monitoring and backups"
echo ""
echo "📖 Full guide: UBUNTU_DEPLOYMENT_GUIDE.md"