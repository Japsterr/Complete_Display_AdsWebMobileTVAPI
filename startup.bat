@echo off
setlocal enabledelayedexpansion

REM Ensure script runs from repo root (script location)
cd /d "%~dp0"

echo ==========================================
echo DisplayAds - startup script
echo ==========================================

REM Check Docker is available
docker version >nul 2>&1
if errorlevel 1 (
  echo Docker not found. Please start Docker Desktop and re-run this script.
  pause
  exit /b 1
)

REM Choose compose command (docker compose preferred, fallback to docker-compose)
docker compose version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  set "COMPOSE_CMD=docker compose"
) else (
  set "COMPOSE_CMD=docker-compose"
)

echo Using: %COMPOSE_CMD%

REM Start Traefik stack if present (creates external network if missing)
if exist "docker-compose.traefik.yml" (
  echo Found docker-compose.traefik.yml, ensuring 'traefik' network exists...
  docker network inspect traefik >nul 2>&1 || (
    echo Creating docker network 'traefik'...
    docker network create traefik >nul 2>&1 || (
      echo Failed to create 'traefik' network. You may need to create it manually.
    )
  )
  echo Starting Traefik...
  %COMPOSE_CMD% -f docker-compose.traefik.yml up -d
)

REM Start main development stack (build API and frontend locally)
echo Starting main stack (postgres, minio, api, frontend)...
%COMPOSE_CMD% -f docker-compose.yml up --build -d

REM Wait for MinIO container to appear and be running (container_name: minio)
echo Waiting for MinIO to appear (container name: minio)...
set COUNT=0
set MINIO_ID=
:wait_minio
for /f "delims=" %%i in ('docker ps -f "name=minio" -q') do set "MINIO_ID=%%i"
if defined MINIO_ID (
  echo MinIO container detected: %MINIO_ID%
) else (
  set /a COUNT+=1
  if %COUNT% GEQ 60 (
    echo Timeout waiting for MinIO. Continue and you can run the setup manually later.
    goto after_minio_wait
  )
  timeout /t 1 >nul
  goto wait_minio
)

REM Run the minio-setup job once to create buckets and CORS
echo Running MinIO setup job to create bucket and configure CORS...
%COMPOSE_CMD% -f docker-compose.yml run --rm minio-setup

:after_minio_wait
echo
echo Stack status:
%COMPOSE_CMD% -f docker-compose.yml ps

echo
echo To stop the stack: %COMPOSE_CMD% -f docker-compose.yml down
echo To view logs: %COMPOSE_CMD% -f docker-compose.yml logs -f

pause
