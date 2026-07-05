# Setup

This guide gets Cognivest running locally. Two paths:

- **Docker path** (recommended) — the whole stack via `docker compose`.
- **Native path** — backend and frontend run directly against a local Postgres + Redis.

> **Scope note.** This is a hackathon build. One route is live end-to-end
> (`POST /api/v1/companies/{ticker}/query`); most others are typed stubs. See
> [CLAUDE.md §15](../CLAUDE.md) and the README's *Limitations* section.

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Docker + Docker Compose | latest | Docker path (Postgres, Redis, backend, worker, beat, frontend) |
| Python | 3.11 | Native backend |
| Node.js | 20+ | Native frontend |
| pnpm | 9+ | Frontend package manager |
| `make` | any | Developer task runner ([Makefile](../Makefile)) |

You need **one Gemini API key** ([Google AI Studio](https://aistudio.google.com/), free tier) for the
query/answer path. Vendor keys (market data, news, web search) are only needed once the collectors are
built — not for the demo. See [environment.md](./environment.md).

## 1. Clone & configure

```bash
git clone https://github.com/your-org/cognivest.git
cd cognivest
cp .env.example .env
```

Set **one** value in `.env`:

- `LLM_API_KEY` — your Gemini key. (`LLM_PROVIDER=gemini`, `LLM_MODEL=gemini/gemini-2.5-flash`, and
  `EMBEDDING_PROVIDER=fastembed` are already correct in the template.)

Optionally change `POSTGRES_PASSWORD` from `change_me`. Every variable is documented in
[environment.md](./environment.md). **`.env` is git-ignored — never commit it.**

> **Upgrading an older checkout?** Re-copy the template (`cp .env.example .env`) before booting. Stale
> `.env` files carry a dead Anthropic/`claude-opus` LLM config that no longer works.

---

## Docker path (recommended)

```bash
docker compose up -d --build                                             # postgres, redis, backend, worker, beat, frontend
docker compose exec backend alembic upgrade head                         # apply Alembic migrations
docker compose exec backend python -m scripts.seed                       # demo companies (AAPL, MSFT, TSLA) + a demo user
docker compose exec backend python -m scripts.backfill_ticker --ticker AAPL   # live price action (yfinance) → Cognee
docker compose exec backend python -m scripts.ingest_demo_corpus --ticker AAPL # curated AAPL news corpus → Cognee
```

> These are also wrapped as `make` targets (`make up`, `make migrate`, `make seed`,
> `make backfill t=AAPL`) — the `docker compose exec` form above is the canonical path.
> The final `cognify` inside each ingest step takes ~30–60s; give it a moment before querying.

Then:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- **Live OpenAPI docs (source of truth): http://localhost:8000/docs**

> **Gemini free-tier quota (`429`/`503`).** The free tier is ~20 requests/day per model. Swap `LLM_MODEL`
> between `gemini/gemini-2.5-flash` and `gemini/gemini-2.5-flash-lite` (separate quotas), or use a fresh
> key from a different Google Cloud project, then `docker compose up -d` to restart. Local fastembed
> embeddings are unaffected, so no re-ingest is needed.

Useful lifecycle targets:

```bash
make logs      # tail logs from all services
make ps        # show running services
make down      # stop the stack
make restart   # down + up
```

---

## Native path

Run Postgres and Redis yourself, then point `.env` at them (e.g. `POSTGRES_HOST=localhost`,
`REDIS_URL=redis://localhost:6379/0`).

### Backend

```bash
cd backend
pip install -e ".[dev]"                 # or: make install (from repo root)
alembic upgrade head                    # migrations
uvicorn src.main:app --reload --port 8000
```

Celery worker/beat (optional — task bodies are stubs today):

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

## First-run checklist

1. `docker compose up -d --build` — all containers healthy (`docker compose ps`).
2. `alembic upgrade head` succeeds.
3. http://localhost:8000/docs — OpenAPI loads; `GET /health` returns `{"status":"ok"}`.
4. `python -m scripts.seed` — demo companies + user inserted.
5. `python -m scripts.backfill_ticker --ticker AAPL` then `python -m scripts.ingest_demo_corpus --ticker AAPL`
   — AAPL price + news land in Cognee (each ends with a ~30–60s `cognify`).
6. http://localhost:3000 — dashboard renders (watchlist/price come from stubbed endpoints, so most
   panels are empty). Open the AAPL company page and ask a question — after step 5 the query box returns
   a grounded, cited answer; before it (or for MSFT/TSLA) it honestly answers "no data ingested yet."

Quality checks: `make lint` (ruff + black + mypy + eslint + prettier), `make fmt` (auto-format),
`make typecheck` (mypy + tsc). There is no `make test` target yet.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `connection refused` to Postgres | DB container not ready / wrong host | Wait for healthcheck; check `POSTGRES_HOST` (`postgres` in Docker, `localhost` native). |
| Alembic `target database is not up to date` | Migrations not applied | `make migrate`. |
| Query path errors on the LLM | `LLM_API_KEY` unset or quota-exhausted | Set a valid Gemini key; see the README fallback note. |
| Celery worker can't reach broker | `CELERY_BROKER_URL` wrong | Confirm Redis is up; check the broker DB index in the URL. |
| Frontend can't reach API | `NEXT_PUBLIC_API_BASE_URL` wrong / CORS | Set the base URL; add the frontend origin to `BACKEND_CORS_ORIGINS`. |
| `501`/`NotImplementedError` on a route | That route is a stub | Expected — only `/health` and `/companies/{ticker}/query` are live. |
| Port already in use | Another process on 3000/8000/5432/6379 | Stop it or override ports in `docker-compose.yml` / `.env`. |

See [development-workflow.md](./development-workflow.md) for day-to-day work.
