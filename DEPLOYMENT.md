Production deployment guide

Overview

This document describes how to build and run the ytmp3 service in a production-like environment using Docker Compose. It assumes you have Docker and Docker Compose installed on the host.

Build and run (single-host)

1. Build the image (from repository root):

```bash
# build image and tag
docker-compose -f docker-compose.prod.yml build --no-cache

# run in detached mode
docker-compose -f docker-compose.prod.yml up -d
```

2. Verify service

```bash
# check compose services
docker-compose -f docker-compose.prod.yml ps

# health check
curl -sS http://localhost:8000/health
```

Environment & configuration

- `REDIS_HOST` (default `redis`) — host name for Redis service used by backend.
- `JOB_TTL_SECONDS` (default `3600`) — how long to retain job records and tmpdirs.

Production recommendations

- Use a reverse proxy (nginx/caddy) in front of the service to handle TLS, rate-limiting and client uploads.
- Mount a persistent volume for output files if you plan to keep them longer than job TTL.
- Consider separating the worker from the API server:
  - Run a small worker service (RQ/Celery) that consumes job requests from Redis and executes `yt-dlp`.
  - This allows scaling workers independently and keeps the API responsive.
- Monitor disk usage and periodically clean `/tmp` or the configured `tmpdir` storage.

Security & legal

- `yt-dlp` downloads content from third-party sources. Make sure you comply with terms of service and local laws before running a public service.

Rollback & upgrades

- To deploy a new version, build and tag images then `docker-compose -f docker-compose.prod.yml up -d --no-recreate`.
- Keep an eye on Redis data; if you need to reset job state, stop services and remove `redis_data` volume.

Local development vs production

- The repo includes a development `docker-compose.yml` that mounts local frontend and extension folders for rapid iteration.
- The production compose file `docker-compose.prod.yml` uses image-based deployment without host mounts.

If you want, I can also generate a `systemd` unit or a minimal `nginx` reverse-proxy config next.
