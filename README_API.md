# DisplayAds — API (consolidated)

This file is the canonical API documentation for the DisplayAds project.

Summary
- Purpose: Backend REST API (Django + DRF) providing authentication, campaign/media management, device activation and telemetry.
- Base URL: /api/v1/

Quick start
- Run migrations: python manage.py migrate
- Start dev server: python manage.py runserver 0.0.0.0:8000

Key endpoints
- POST /api/v1/login/ — obtain JWT
- POST /api/v1/register/ — create user
- GET/POST /api/v1/campaigns/ — campaign CRUD
- GET/POST /api/v1/media/ — media uploads
- POST /api/v1/devices/request-activation/ — TV activation flow
- POST /api/v1/devices/activate/ — activate device via code

Notes & troubleshooting
- Use the health endpoint GET /api/v1/health/ to smoke-test the API.
- For media preview problems, verify MINIO_PUBLIC_ENDPOINT and MinIO bucket permissions.

Further reading / archived docs
All legacy and detailed API-related documents (database schema, test reports, migration notes) were consolidated. The originals were removed from the top-level to reduce duplication; they are recoverable from git history.
