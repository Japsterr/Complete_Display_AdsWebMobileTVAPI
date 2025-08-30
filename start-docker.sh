#!/bin/bash

# DisplayAds API - Docker Startup Script
echo "🚀 Starting DisplayAds API with PostgreSQL and Redis..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove old containers and images (optional - uncomment to clean up)
# docker-compose down --rmi all --volumes --remove-orphans

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Services are starting up!"
echo ""
echo "📱 Access points:"
echo "   • API Backend: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/swagger/"
echo "   • Frontend Dashboard: http://localhost:5173"
echo "   • TV Simulator: http://localhost:8080"
echo "   • MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "   • PostgreSQL: localhost:5432 (displayadsuser/displayadspass123)"
echo "   • Redis: localhost:6379"
echo ""
echo "🔍 To view logs:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "   Available services: postgres, redis, api, frontend, minio, tv-simulator"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"