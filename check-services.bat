@echo off
echo 🚀 DisplayAds API - Service Status Check
echo =========================================
echo.

echo 📊 Docker Container Status:
docker-compose ps
echo.

echo 🔍 API Health Check:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health/' -UseBasicParsing; Write-Host '✅ API Status:' $response.Content } catch { Write-Host '❌ API not responding:' $_.Exception.Message }"
echo.

echo 🌐 Frontend Status:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5173/' -UseBasicParsing; Write-Host '✅ Frontend is accessible' } catch { Write-Host '❌ Frontend not responding:' $_.Exception.Message }"
echo.

echo 📺 TV Simulator Status:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/' -UseBasicParsing; Write-Host '✅ TV Simulator is accessible' } catch { Write-Host '❌ TV Simulator not responding:' $_.Exception.Message }"
echo.

echo 📱 Service URLs:
echo    • API Backend: http://localhost:8000
echo    • API Documentation: http://localhost:8000/swagger/
echo    • API Health Check: http://localhost:8000/api/health/
echo    • Frontend Dashboard: http://localhost:5173
echo    • TV Simulator: http://localhost:8080
echo    • MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
echo.

echo 🗄️ Database & Cache:
echo    • PostgreSQL: localhost:5432 (displayadsuser/displayadspass123)
echo    • Redis: localhost:6379
echo.

echo 📋 Quick Commands:
echo    • View all logs: docker-compose logs -f
echo    • View API logs: docker-compose logs -f api
echo    • View Frontend logs: docker-compose logs -f frontend
echo    • Stop all services: docker-compose down
echo    • Restart all services: docker-compose restart
echo.

pause