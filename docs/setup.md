# Setup

This guide gets Cognivest running locally. There are two paths:

- **Docker path** (recommended) — the whole stack via `docker compose`.
- **Native path** — backend and frontend run directly on your machine against local Postgres + Redis.

> **Phase 0 note.** The repository is currently a scaffold (see [CLAUDE.md §15](../CLAUDE.md)).
> Business logic is intentionally stubbed; these instructions describe the intended developer
> experience and work for the parts that are implemented.

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Docker + Docker Compose | latest | Docker path (Postgres, Redis, backend, worker, beat, frontend) |
| Python | 3.11 | Backend (FastAPI, Celery) |
| Node.js | 20+ | Frontend (Next.js 14) |
| pnpm | 9+ | Frontend package manager |
| `make` | any | Developer task runner ([Makefile](../Makefile)) |
| `openssl` | 1.1+ | Generating the JWT RS256 keypair |
| `pre-commit` | latest | Git hooks (format + lint on staged files) |

You also need API keys for the pluggable vendors (market data, news, web search) and an
**Anthropic API key** for answer generation. See [environment.md](./environment.md).

## 1. Clone

```bash
git clone https://github.com/your-org/cognivest.git
cd cognivest
```

## 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in at least:

- `POSTGRES_PASSWORD` — change from `change_me`.
- `SERVICE_TOKEN` — internal token for `/memory/*` calls; change from the default.
- `ANTHROPIC_API_KEY` — required for the query/answer path.
- `MARKET_DATA_API_KEY`, `NEWS_API_KEY`, `WEB_SEARCH_API_KEY` — vendor keys.

Every variable is documented in [environment.md](./environment.md). **`.env` is git-ignored —
never commit it.**

## 3. Generate JWT signing keys

Auth uses RS256 (asymmetric), so you need a private/public keypair. A helper script generates one
into `./secrets/` (which is git-ignored):

```bash
bash scripts/generate_jwt_keys.sh
```

This produces `secrets/jwt_private.pem` and `secrets/jwt_public.pem`, matching
`JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH` in `.env`. See [authentication.md](./authentication.md).

---

## Docker path (recommended)

Bring up the full stack — Postgres, Redis, the backend API, a Celery worker, Celery Beat, and the
frontend:

```bash
make up        # docker compose up -d --build
make migrate   # apply Alembic migrations (alembic upgrade head)
make seed      # optional: seed a demo ticker
```

Then:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- **Live OpenAPI docs (source of truth): http://localhost:8000/docs**

Useful lifecycle targets:

```bash
make logs      # tail logs from all services
make ps        # show running services
make down      # stop the stack
make restart   # down + up
```

---

## Native path

Run Postgres and Redis yourself (Docker, Homebrew, or system packages), then point `.env` at them
(e.g. `POSTGRES_HOST=localhost`, `REDIS_URL=redis://localhost:6379/0`).

### Backend

```bash
cd backend
pip install -e ".[dev]"                 # or: make install (from repo root)
alembic upgrade head                    # migrations
uvicorn src.main:app --reload --port 8000
```

Run the workers in separate terminals:

```bash
make worker    # celery -A src.workers.celery_app worker -l info
make beat      # celery -A src.workers.celery_app beat -l info
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev                                # http://localhost:3000
```

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` in `.env`.

---

## 4. Install pre-commit hooks

```bash
make hooks     # pre-commit install
```

Hooks run formatting + linting on staged files. Do **not** bypass them with `--no-verify`.

## 5. First run checklist

1. `make up` (or native services) — all containers healthy (`make ps`).
2. `make migrate` succeeds.
3. Visit http://localhost:8000/docs — OpenAPI loads.
4. Visit http://localhost:3000 — dashboard renders.
5. `make seed` — a demo ticker appears in the watchlist.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `connection refused` to Postgres | DB container not ready / wrong host | Wait for healthcheck; check `POSTGRES_HOST` (`postgres` in Docker, `localhost` native). |
| Alembic `target database is not up to date` | Migrations not applied | `make migrate`. |
| Celery worker can't reach broker | `CELERY_BROKER_URL` wrong | Confirm Redis is up; check the broker DB index in the URL. |
| 401 on every request | JWT keys missing/mismatched | Re-run `scripts/generate_jwt_keys.sh`; verify `JWT_*_KEY_PATH`. |
| 401/403 on `/memory/*` | Missing internal service token | Set `SERVICE_TOKEN` and send it on internal calls. See [authentication.md](./authentication.md). |
| Answer endpoint errors | `ANTHROPIC_API_KEY` unset | Set it in `.env`. See [environment.md](./environment.md). |
| Frontend can't reach API | `NEXT_PUBLIC_API_BASE_URL` wrong / CORS | Set the base URL; add the frontend origin to `BACKEND_CORS_ORIGINS`. |
| Port already in use | Another process on 3000/8000/5432/6379 | Stop it or override ports in `docker-compose.yml` / `.env`. |

Still stuck? See [development-workflow.md](./development-workflow.md) for local debugging, and the
[runbooks](./runbooks/README.md) for operational issues.
