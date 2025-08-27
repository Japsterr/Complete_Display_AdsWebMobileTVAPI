Deployment guide (CI + Portainer)

This document explains how to set up a best-practice deployment for the DisplayAds project using GitHub Actions to build images and Portainer to run the stack.

Overview
- CI builds images for `api` and `frontend` and pushes them to Docker Hub (or another registry).
- Portainer pulls the images and runs the stack using `docker-compose.prod.yml`.
- Secrets are stored in Portainer and injected into containers.

What this change added to the repo
- `docker-compose.prod.yml` - production-ready compose (replace image names before deploying)
- `.github/workflows/build-and-push.yml` - GitHub Actions workflow that builds and pushes images to Docker Hub
- `README_DEPLOY.md` - this file with instructions

Pre-requisites
- GitHub repository for your code (this repo).
- Docker Hub account (or another registry). If you prefer GHCR, you can adapt the workflow to use `ghcr.io`.
- GitHub repository secrets configured (see below).
- Portainer environment with access to pull images from your registry and the ability to create secrets and stacks.


If you prefer GHCR (recommended when repository is on GitHub):
- `GHCR_TOKEN` - a GitHub personal access token with `write:packages`, `read:packages` scopes (store in GitHub Secrets as `GHCR_TOKEN`).
- The workflow will push to `ghcr.io/<your-org>/displayads-api` and `ghcr.io/<your-org>/displayads-frontend`.

How to use
1) Configure Docker Hub repos

Traefik (optional, recommended for TLS)
- There is a `docker-compose.traefik.yml` in this repo that deploys Traefik as a reverse proxy using the Docker provider and Let's Encrypt.
- Create a Docker network named `traefik` on the host where Portainer runs:

   docker network create traefik

- Deploy the Traefik stack in Portainer first (Stacks -> Add stack -> paste `docker-compose.traefik.yml`).
- Update `docker-compose.prod.yml` `frontend` labels to use your domain (search for `displayads.example.com` and replace).

GHCR-specific notes
- Make sure the GHCR token you create is given to the GitHub Actions workflow as `GHCR_TOKEN` in repository secrets.
- If you want Portainer to pull from GHCR (private repos), create credentials in Portainer for `ghcr.io`.
   - Create two repos in Docker Hub (or your registry): `displayads-api` and `displayads-frontend` in your namespace.

2) Set GitHub secrets
   - Go to your repo Settings -> Secrets -> Actions -> New repository secret and add the values above.

3) Push changes to GitHub
   - The workflow runs for pushes to `main` and `Laptop` branches and will build and push images.

4) Update `docker-compose.prod.yml`
   - Replace `REPLACE_WITH_REGISTRY/displayads-api:latest` and `REPLACE_WITH_REGISTRY/displayads-frontend:latest` with your image paths, e.g. `docker.io/<youruser>/displayads-api:latest`.
   - Alternatively, in Portainer you can override the image names when deploying.

5) Create secrets in Portainer
   - In Portainer, go to the environment -> Secrets -> Add secret
   - Add `postgres_password` and `minio_root_password` (use strong random values)

6) Deploy the stack in Portainer
   - Stacks -> Add stack -> Name it `displayads-prod` -> Paste the contents of `docker-compose.prod.yml` -> Deploy the stack
   - Ensure you attach the created secrets to the stack (Portainer prompts to map secrets)

7) Run DB migrations and collectstatic
   - In Portainer, find the `api` container and open Console (or use `docker exec` on the host)
   - Run:
     - `python manage.py migrate`
     - `python manage.py createsuperuser` (interactive; or use environment-based creation)
     - `python manage.py collectstatic --noinput`

8) (Optional) Configure reverse proxy and TLS
   - For production, deploy Traefik or Nginx Proxy Manager and route `displayads.example.com` to the `frontend` and `api` services.
   - Set `DJANGO_ALLOWED_HOSTS` in `docker-compose.prod.yml` to your domain(s).

9) (Optional) Auto-redeploy via webhook
   - In Portainer, open the stack -> Use the Stack actions menu -> Enable Auto-redeploy -> Copy the webhook URL
   - Add the webhook URL as `PORTAINER_WEBHOOK_URL` in GitHub secrets so the workflow triggers the redeploy after pushing images

Troubleshooting
- If Portainer can't pull images: ensure the host where Portainer runs has network access to the registry and credentials (if private registry) are configured in Portainer.
- If static files are missing: ensure `collectstatic` ran successfully and the `media` volume is mounted properly.
- If the API cannot connect to Postgres: check the DB secret mapping and network; do NOT expose Postgres port publicly if not required.

Next steps I can help with
- Adapt the GitHub Action to use GHCR (GitHub Container Registry) instead of Docker Hub
- Add a `deploy` job that logs into Portainer via its API to trigger a redeploy (currently the workflow triggers an optional webhook)
- Add a Traefik stack and example domain/TLS setup

If you want me to continue, tell me:
- Which container registry do you want to use? (Docker Hub, GHCR, or private)
- The domain you will use for the app (if you want me to prepare Traefik or set ALLOWED_HOSTS)
- Whether you want me to add the workflow and compose directly to your repo (I already wrote files into the repo).
