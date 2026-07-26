# Multi-stage build for TerraForge Studio.
#
# Stage 1 builds the React frontend, stage 2 installs the Python backend and
# serves both from one container. The image needs no API keys: SRTM elevation
# and Overpass vector data are key-free.

# ---------------------------------------------------------------------------
# Stage 1: frontend
# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend-new/package.json frontend-new/package-lock.json ./
# The full dependency set, not --omit=dev: the build script is `tsc && vite
# build`, and both tools are devDependencies.
RUN npm ci

COPY frontend-new/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: backend
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Core requirements: everything the API, SRTM elevation, Overpass vector data
# and the Unreal/Unity exporters need. GeoTIFF export and the osmnx path live
# in requirements-optional.txt and pull in the GDAL stack; to include them, add
# gdal-bin and libgdal-dev to the apt line above and install that file too.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY realworldmapgen/ ./realworldmapgen/

# main.py serves the SPA from <repo-root>/frontend-new/dist, so the build has
# to land on that exact path to be picked up.
COPY --from=frontend-builder /app/frontend/dist ./frontend-new/dist

# Written to at runtime. data/ holds user accounts and the credential
# encryption key, so mount it if those should outlive the container.
RUN mkdir -p /app/cache /app/output /app/temp /app/data

RUN useradd -m -u 1000 terraforge && chown -R terraforge:terraforge /app
USER terraforge

EXPOSE 8000

# /health/ready verifies a writable output directory and a reachable elevation
# source, which is what "can actually serve a generation" means here.
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8000/health/ready || exit 1

CMD ["uvicorn", "realworldmapgen.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
