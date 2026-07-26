# 🚀 Deployment Guide - TerraForge Studio

How to run TerraForge Studio somewhere other than your laptop.

**What it needs:** a Python runtime, disk, and outbound HTTPS. That is the
whole list. There is no database, no cache server and no task broker —
generation state lives in the process that started it, results are cached on
disk under `CACHE_DIR`, and the batch queue is in memory. Earlier revisions of
this guide walked through installing PostgreSQL and Redis and running Alembic
migrations; nothing in the codebase has ever connected to any of them.

**What it does not need:** API keys. SRTM elevation and Overpass vector data
are both key-free, so a default deployment produces real terrain out of the
box. Credentials only unlock the additional providers.

---

## 📋 Table of Contents

1. [Requirements](#requirements)
2. [Docker (recommended)](#docker-recommended)
3. [From source](#from-source)
4. [Configuration](#configuration)
5. [TLS](#tls)
6. [Kubernetes](#kubernetes)
7. [Monitoring](#monitoring)
8. [Backups](#backups)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## Requirements

| | |
|---|---|
| **Python** | 3.10 – 3.12 |
| **Node.js** | 18 or 20, to build the frontend |
| **CPU** | 2 cores minimum; generation is CPU bound and parallelises |
| **RAM** | 4 GB minimum, 8 GB comfortable — a 8192² heightmap is ~500 MB in flight |
| **Disk** | Depends on retention. A 2048² map exported to UE5, Unity and GLTF measures ~37 MB, and the result cache keeps a copy |
| **Network** | Outbound HTTPS to `s3.amazonaws.com` (elevation tiles) and the Overpass endpoints |

---

## Docker (recommended)

The image builds the frontend and serves it alongside the API from one
container.

```bash
docker compose up -d --build
```

That is the whole deployment: <http://localhost:8000>.

Three named volumes keep state across rebuilds:

| Volume | Holds |
|---|---|
| `terraforge_output` | Generated maps |
| `terraforge_cache` | Result and elevation-tile cache — safe to delete |
| `terraforge_data` | User accounts and the credential encryption key — **not** safe to delete |

Add a reverse proxy on port 80 with rate limiting and generation-length
timeouts:

```bash
docker compose --profile proxy up -d
```

### Production stack

`docker-compose.prod.yml` adds nginx terminating TLS and an optional
Prometheus/Grafana pair:

```bash
cp .env.example .env          # set what you need, then
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml --profile monitoring up -d
```

Put your certificate in `./ssl` as `fullchain.pem` and `privkey.pem`, and set
`server_name` in `nginx.prod.conf` to your domain.

---

## From source

```bash
git clone https://github.com/bobberdolle1/TerraForge-Studio.git
cd TerraForge-Studio

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cd frontend-new && npm ci && npm run build && cd ..
```

The API serves `frontend-new/dist` at `/` when that directory exists, so the
build output needs no separate web server.

### Running it

```bash
uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Generation is CPU bound, so workers help. Note that each worker keeps its own
task registry — see [Scaling](#scaling).

### systemd

```ini
# /etc/systemd/system/terraforge.service
[Unit]
Description=TerraForge Studio
After=network-online.target
Wants=network-online.target

[Service]
Type=exec
User=terraforge
WorkingDirectory=/opt/terraforge
EnvironmentFile=/opt/terraforge/.env
ExecStart=/opt/terraforge/.venv/bin/uvicorn realworldmapgen.api.main:app \
          --host 127.0.0.1 --port 8000 --workers 4
Restart=on-failure
RestartSec=5

# The service writes only to its own directories.
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/terraforge/output /opt/terraforge/cache /opt/terraforge/temp /opt/terraforge/data

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now terraforge
sudo systemctl status terraforge
```

### Optional extras

GeoTIFF export and the osmnx vector path need the geospatial stack, which
pulls in GDAL:

```bash
sudo apt-get install -y gdal-bin libgdal-dev
pip install -r requirements-optional.txt
```

Without them everything else still works; a GeoTIFF export reports its own
failure while the other formats succeed.

---

## Configuration

Every setting is an environment variable or a line in `.env`. `.env.example`
documents all of them; the ones that matter for a deployment:

```bash
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# Where output, cache and credentials live. Keep the last one off any volume
# you might clear.
OUTPUT_DIR=/var/lib/terraforge/output
CACHE_DIR=/var/lib/terraforge/cache
TEMP_DIR=/var/lib/terraforge/temp
AUTH_STORAGE_FILE=/var/lib/terraforge/data/users.json
SETTINGS_STORAGE_FILE=/var/lib/terraforge/data/settings.json
SECRET_KEY_FILE=/var/lib/terraforge/data/.secret_key

# Only the origins your frontend is actually served from.
CORS_ORIGINS=https://terrain.example.com

LOG_LEVEL=INFO
LOG_FORMAT=json

# Guard rails for a public instance.
MAX_AREA_KM2=100
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
# Enable ONLY behind a proxy that overwrites X-Forwarded-For.
RATE_LIMIT_TRUST_FORWARDED_FOR=true
```

Settings not listed in `.env.example` are ignored rather than rejected, so a
typo'd variable name fails silently — check the name against that file if
something appears not to take effect.

### Locking the instance down

Two independent mechanisms, either or both:

```bash
# A shared key in front of the whole API.
API_KEY_ENABLED=true
API_KEYS=generate-a-long-random-string,and-another-for-rotation
```

```bash
# Per-user accounts with roles, for the administrative endpoints.
# See docs/API_EXAMPLES.md#authentication-and-users
```

`/api/health`, `/health*`, `/metrics` and the schema endpoints stay reachable
without a key so orchestrator probes keep working.

### Credential storage

Provider API keys entered through the settings UI are encrypted with a Fernet
key generated at first start and written to `SECRET_KEY_FILE` with `0600`
permissions.

- **Back that file up.** Without it the stored credentials cannot be decrypted.
- **Do not commit it.** `data/` is in `.gitignore`.
- If it was created by a build before the key became random, treat the stored
  credentials as exposed and rotate them — see
  [SETTINGS_GUIDE.md](SETTINGS_GUIDE.md#-security).

---

## TLS

Terminate TLS at nginx and keep the application on localhost. `nginx.prod.conf`
is a complete configuration; with certbot:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d terrain.example.com
```

Renewal is installed as a systemd timer by the certbot package — check it with
`systemctl list-timers | grep certbot`.

Two things the proxy must get right, both already in `nginx.prod.conf`:

- **`proxy_read_timeout`** well above a minute. Generating a large area takes
  minutes, and a 60 second timeout cuts the request off at the proxy while the
  work continues on the server.
- **`X-Forwarded-For`** overwritten, not appended blindly, if you set
  `RATE_LIMIT_TRUST_FORWARDED_FOR=true`. Otherwise a client can rotate the
  header to sidestep the rate limit.

---

## Kubernetes

`k8s/deployment.yml` contains a namespace, a PVC, one deployment, and a
ClusterIP service:

```bash
docker build -t terraforge/studio:latest .
kubectl apply -f k8s/deployment.yml
kubectl -n terraforge-prod rollout status deploy/terraforge
```

The probes are the real ones:

- `/health/live` — the process is up.
- `/health/ready` — the output directory is writable **and** an elevation
  source answers. A pod without egress therefore stays out of the Service,
  which is correct: it could not serve a generation anyway.

Provider credentials come from an optional Secret; without it the pod starts
anyway and uses the key-free sources:

```bash
kubectl -n terraforge-prod create secret generic terraforge-credentials \
  --from-literal=opentopography-api-key=…
```

---

## Monitoring

`/metrics` returns JSON — application version, uptime, task counts by status,
and process CPU/memory when `psutil` is installed:

```bash
curl http://localhost:8000/metrics
```

`prometheus.yml` scrapes it directly; no exporter sidecar is involved. Bring it
up with the `monitoring` profile shown above.

Logs go to stdout, so `journalctl -u terraforge -f` or `docker compose logs -f`
is the whole story. Set `LOG_FORMAT=json` for structured output.

---

## Backups

Three directories, with very different value:

| Path | Back up? | Why |
|---|---|---|
| `data/` | **Yes** | Accounts and the credential encryption key. Small. Irreplaceable. |
| `output/` | Your call | Regenerable from the same request, at the cost of time |
| `cache/` | No | Purely derived; deleting it costs a re-fetch |

```bash
#!/usr/bin/env bash
# /usr/local/bin/terraforge-backup
set -euo pipefail

BACKUP_DIR=/var/backups/terraforge
STAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

tar czf "$BACKUP_DIR/terraforge-$STAMP.tar.gz" \
    -C /var/lib/terraforge data output

find "$BACKUP_DIR" -name 'terraforge-*.tar.gz' -mtime +7 -delete
```

```bash
sudo crontab -e
# 0 2 * * * /usr/local/bin/terraforge-backup
```

Restoring is untarring the archive back into place and restarting.

---

## Scaling

**Scale up before scaling out.** Generation is CPU and memory bound, and both
`--workers N` and multiple replicas hit the same wall: the task registry lives
in the process that accepted the request. A client polling
`/api/status/{task_id}` against a different worker gets a 404.

Practical options today:

- One instance with `--workers 4` behind a proxy with sticky sessions
  (`ip_hash` in nginx), so a client stays on the worker holding its task.
- One instance and vertical scaling — this is what `k8s/deployment.yml` does,
  with `replicas: 1` and a comment saying why.

Genuine horizontal scaling needs shared task state, which does not exist yet.
Anything that claims otherwise is describing a system that was never built.

---

## Troubleshooting

**`/health/ready` returns 503.** Look at the response body — it names the
failing check. Either the output directory is not writable (permissions on the
volume) or no elevation source answered (egress blocked, or every source
disabled in configuration).

**Generation always returns synthetic terrain.** `result.elevation.synthetic`
is `true` when every real source failed and the procedural fallback ran. Check
`SRTM_ENABLED` and outbound access to `s3.amazonaws.com`. Set
`ALLOW_SYNTHETIC_FALLBACK=false` to make the failure loud instead.

**A setting appears to do nothing.** Unknown keys are ignored by design, so a
misspelled variable is silent. Compare against `.env.example`.

**Roads and buildings come back empty.** Overpass is a shared public service
and refuses large areas; `OVERPASS_MAX_AREA_KM2` caps requests at 25 km² by
default. It also rate limits — the client already retries on 429 across
several endpoints.

**Everything 401s after enabling the API key gate.** `API_KEY_ENABLED=true`
with an empty `API_KEYS` rejects every request rather than failing open. Set a
key.

**Users cannot log in after a restore.** Check that `data/users.json` came back
with the deployment; accounts are stored there, not in the cache.

**GeoTIFF export fails while other formats succeed.** `rasterio` is not
installed — see [Optional extras](#optional-extras). Each format reports
independently, so this does not fail the task.

---

<div align="center">

[Back to Docs](README.md) • [API Examples](API_EXAMPLES.md) • [Settings](SETTINGS_GUIDE.md)

</div>
