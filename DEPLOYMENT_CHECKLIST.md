# Deployment To-Do List

This checklist helps verify the DisplayAds stack is healthy after a deploy.

## Pre-deploy
- [ ] Secrets configured: DJANGO_SECRET_KEY, DB creds, JWT settings
- [ ] Environment set: DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS
- [ ] Storage: MINIO_PUBLIC_ENDPOINT, AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME
- [ ] CORS/CSRF: Allowed origins set for frontend domains

## Build & Migrate
- [ ] Build backend and frontend images
- [ ] Run database migrations
- [ ] Collect static files

## Boot services
- [ ] Start containers: api, postgres, minio, frontend
- [ ] Initialize MinIO (bucket, anonymous download, CORS)

## Smoke tests
- [ ] API health: GET /api/v1/health/ returns status=healthy
- [ ] Auth: register/login works, tokens issued
- [ ] Media upload: image and video upload succeed
- [ ] Media URLs: returned file_url is public (http(s) and resolves in browser)
- [ ] Media previews: visible in Media Library and Campaign Media Editor
- [ ] Campaign CRUD: create campaign, add media, reorder, durations persist
- [ ] TV simulator: plays images and videos, rotates landscape images only
- [ ] Analytics: heartbeat/impressions endpoints accept data

## Production hardening
- [ ] HTTPS enabled (reverse proxy + certificates)
- [ ] Database backups scheduled
- [ ] Monitoring/logging in place
- [ ] Restrict CORS to production domains only
- [ ] Error alerts configured

## Rollback plan
- [ ] Previous images tagged and available
- [ ] Database backup verified
