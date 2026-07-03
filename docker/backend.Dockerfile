# =====================================================================
# Cognivest backend — development image.
#
# ONE image serves all three backend roles (API, Celery worker, Celery
# beat); the compose file selects the role via `command`. Source is
# bind-mounted in dev compose for hot reload, so this image only needs
# the interpreter + installed dependencies.
#
# Build context is the REPOSITORY ROOT (see docker-compose.yml) so we can
# copy backend/ and keep dependency install cached separately from source.
# =====================================================================
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build tools are needed to build wheels for asyncpg / cryptography / bcrypt;
# curl is used by the container healthcheck against /health.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for layer caching. requirements.txt mirrors
# pyproject.toml's runtime deps (see backend/requirements.txt header).
COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy the app source. In dev compose this is overlaid by a bind mount of
# ./backend, so edits on the host hot-reload inside the container.
COPY backend/ ./

# Operational scripts (backfill/purge/seed) live at the repo root, not under
# backend/. Bake them in so standalone/prod containers can run them; the dev
# compose additionally bind-mounts ./scripts over /app/scripts for hot editing.
COPY scripts/ ./scripts/

EXPOSE 8000

# Default role: the FastAPI API with autoreload. Worker/beat override `command`.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
