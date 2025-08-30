@echo off
echo 🚀 Starting DisplayAds API with PostgreSQL and Redis...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo 📊 Service Status:
docker-compose ps

echo.
echo 🎉 Services are starting up!
echo.
echo 📱 Access points:
echo    • API Backend: http://localhost:8000
echo    • API Documentation: http://localhost:8000/swagger/
echo    • Frontend Dashboard: http://localhost:5173
echo    • TV Simulator: http://localhost:8080
echo    • MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
echo    • PostgreSQL: localhost:5432 (displayadsuser/displayadspass123)
echo    • Redis: localhost:6379
echo.
echo 🔍 To view logs:
echo    docker-compose logs -f [service_name]
echo.
echo    Available services: postgres, redis, api, frontend, minio, tv-simulator
echo.
echo 🛑 To stop all services:
echo    docker-compose down
echo.
pause