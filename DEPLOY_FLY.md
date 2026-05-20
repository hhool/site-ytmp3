Fly / GHCR Deployment Guide

This guide explains how to deploy the backend using GitHub Container Registry (GHCR) and Fly.io. The repository already contains a GitHub Actions workflow that builds the backend image and pushes it to GHCR; optionally the workflow can deploy to Fly if secrets are provided.

Required repository Secrets (set under GitHub -> Settings -> Secrets):

- `FLY_API_TOKEN` — your Fly API token (if you want Actions to automatically deploy to Fly).
- `FLY_APP_NAME` — the Fly app name to deploy to (optional; required for automatic deploy step).

Notes about GHCR:

- The workflow uses `GITHUB_TOKEN` to authenticate to `ghcr.io` and push the image. No extra secret is required for GHCR push from Actions.
- The pushed image will be tagged `ghcr.io/<owner>/site-ytmp3:latest` and `ghcr.io/<owner>/site-ytmp3:<commit-sha>`.

Local deploy steps (manual):

1. Build and push image locally to GHCR (example):

```bash
echo "Login to GHCR"
docker login ghcr.io

# Build and tag
docker build -t ghcr.io/<your-username>/site-ytmp3:latest -f ytmp3/Dockerfile .

# Push
docker push ghcr.io/<your-username>/site-ytmp3:latest
```

2. Deploy to Fly using `flyctl` (manual):

```bash
# Install flyctl if not present: https://fly.io/docs/hands-on/install-flyctl/
flyctl auth login
# create app if not exists
flyctl apps create <your-app-name>
# deploy image from GHCR
flyctl deploy --image ghcr.io/<your-username>/site-ytmp3:latest --app <your-app-name>
```

3. If you prefer Actions to automatically deploy, add `FLY_API_TOKEN` and `FLY_APP_NAME` as repository secrets and push to `main`. The workflow `.github/workflows/backend-deploy.yml` will call `flyctl` to deploy.

Tips:

- Monitor disk usage on the Fly instance; media processing can consume significant disk space. Consider configuring temporary storage or object storage for outputs.
- For production, add authentication, rate-limiting and legal notice before exposing the service publicly.
