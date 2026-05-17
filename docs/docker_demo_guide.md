# FPMS MVP1 Docker Demo Guide

This guide describes the SQLite-based Docker demo deployment path. It is intended for team laptops and simple cloud container hosts used for demos.

## What This Package Runs

- One container image built from `Dockerfile.demo`.
- Vue frontend served by nginx on container port `80`.
- FastAPI backend running inside the same container on `127.0.0.1:8000`.
- nginx reverse proxy for `/api/*`, `/healthz`, `/docs`, `/redoc`, and `/openapi.json`.
- SQLite database at `/data/fpms_demo.db`.
- Application storage at `/data/storage`.

SQLite is intentionally retained for MVP1 demo use. Run only one container replica against a SQLite volume.

## Files

- `Dockerfile.demo`: single-image demo build for frontend, backend, nginx, SQLite.
- `docker-compose.demo.yml`: local/laptop compose file with persistent `/data` volume.
- `deploy/docker/demo/entrypoint.sh`: migration, seed, API, and nginx startup script.
- `deploy/docker/demo/nginx.conf`: SPA static hosting and API reverse proxy.

## Local Laptop Demo

Prerequisites:

- Docker Desktop or Docker Engine with the Compose plugin.
- Ports `8080` available on the host.

Start the demo:

```bash
docker compose -f docker-compose.demo.yml up --build
```

Open:

```text
http://localhost:8080
```

Health check:

```bash
curl -fsS http://localhost:8080/healthz
```

Default seeded login:

```text
Username: admin
Password: admin123
```

The seed script is idempotent. By default, each container start runs migrations and then runs the seed script. Existing data is preserved in the Docker volume.

## Common Local Commands

Run in the background:

```bash
docker compose -f docker-compose.demo.yml up --build -d
```

View logs:

```bash
docker compose -f docker-compose.demo.yml logs -f fpms-demo
```

Stop while keeping SQLite data:

```bash
docker compose -f docker-compose.demo.yml down
```

Reset the demo database and storage:

```bash
docker compose -f docker-compose.demo.yml down -v
```

Disable automatic seed on startup:

```bash
FPMS_RUN_SEED=0 docker compose -f docker-compose.demo.yml up --build
```

Use a stronger JWT secret:

```bash
JWT_SECRET='replace-with-a-long-random-secret' docker compose -f docker-compose.demo.yml up --build -d
```

## Cloud Container Deployment

Use the same image for simple cloud demo hosts.

Container settings:

- Container port: `80`
- Persistent volume mount: `/data`
- Health check path: `/healthz`
- Replica count: `1`
- TLS: terminate at the cloud load balancer, ingress, or platform edge.

Recommended environment variables:

```bash
FPMS_ENV=demo
DATABASE_URL=sqlite:////data/fpms_demo.db
STORAGE_DIR=/data/storage
JWT_SECRET=<set-a-long-random-secret>
JWT_EXPIRE_MINUTES=480
FPMS_RUN_SEED=1
```

For a public cloud URL, update CORS origins only if the frontend is served from a different origin than the API. The single-container demo serves frontend and API from the same origin, so CORS is usually not involved.

Do not scale this SQLite demo horizontally. SQLite is suitable for one demo container with one persistent volume, not multiple concurrent replicas.

## Build Without Compose

Build the image:

```bash
docker build -f Dockerfile.demo -t fpms-mvp1-demo:sqlite .
```

Run it with a named volume:

```bash
docker run --rm \
  -p 8080:80 \
  -v fpms_demo_data:/data \
  -e JWT_SECRET='replace-with-a-long-random-secret' \
  fpms-mvp1-demo:sqlite
```

## SQLite Backup And Restore

Stop the container before taking a consistent SQLite backup:

```bash
docker compose -f docker-compose.demo.yml down
```

Copy the database out of the named volume:

```bash
mkdir -p backups
docker run --rm \
  -v fpms_demo_data:/data \
  -v "$PWD/backups:/backup" \
  alpine sh -lc 'cp /data/fpms_demo.db /backup/fpms_demo_$(date +%Y%m%d%H%M%S).db'
```

Restore by copying a known-good database back into `/data/fpms_demo.db` while the container is stopped.

## Operational Notes

- Migrations run on every container start through `alembic upgrade head`.
- `backend/scripts/seed_dev.py` runs by default and is expected to be idempotent.
- Uploaded/generated files should live under `/data/storage`.
- If users see 401/403 after changing seed or permissions, log out and log back in so the browser receives a fresh token.
- If the database is reset, the default admin user is recreated by the seed script.

## Troubleshooting

Port already in use:

```bash
docker compose -f docker-compose.demo.yml down
```

Or change the host port in `docker-compose.demo.yml` from `8080:80` to another host port, for example `18080:80`.

Container starts but login fails:

- Check logs for migration or seed errors.
- Confirm `FPMS_RUN_SEED=1` unless you intentionally skipped seeding.
- Reset the volume if the demo database is corrupted or incompatible with the current migrations.

Health check fails:

- Inspect logs with `docker compose -f docker-compose.demo.yml logs -f fpms-demo`.
- Confirm the backend started after migrations.
- Confirm nginx can proxy to `127.0.0.1:8000`.

Cloud deployment cannot persist data:

- Confirm the cloud platform mounts a writable volume at `/data`.
- Confirm the container user can write to `/data`.
- Keep replica count at `1` for SQLite.
