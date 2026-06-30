# Cognivest — Backend

FastAPI backend for **Cognivest**, a per-company financial intelligence platform.
For each watchlisted ticker the system ingests price + news/web content into
**Cognee** (the single memory/intelligence layer), which builds a per-company
knowledge graph and answers natural-language questions with ranked, cited answers.

> This is the **Phase 0 scaffold**. Structure, configs, and typed placeholders are
> in place; business logic is intentionally not implemented. Placeholder functions
> raise `NotImplementedError` or return typed stubs marked `# TODO(phase-N)`.

See the repository-root [`ARCHITECTURE.md`](../ARCHITECTURE.md) and
[`CLAUDE.md`](../CLAUDE.md) for the authoritative design and conventions.

---

## Layered architecture (Clean Architecture)

Dependencies point inward: **routes → services → repositories**. Services never
import routers; repositories never import services.

```text
src/
  main.py            FastAPI app factory (create_app), CORS, routers, /health
  config/            Settings (Pydantic) + structlog setup
  routes/            FastAPI routers — THIN: validate via schema, call a service
  controllers/       (the routes ARE the controllers — see controllers/__init__.py)
  middleware/        JWT verify + RBAC + rate-limit dependencies
  services/          Business logic / orchestration
  repositories/      ALL Postgres data access (no SQL anywhere else)
  models/            SQLAlchemy 2.x models (matches ARCHITECTURE.md §4.5 ER diagram)
  schemas/           Pydantic v2 request/response DTOs
  memory/            THE Cognee boundary — cognee_client.py is the ONLY importer
  ai/                prompt_templates.py + answer_formatter.py (Claude answer gen)
  collectors/        Pluggable vendor fetch → normalize → dedup
  workers/           Celery app + tasks (queues: price, news, cognify)
  utils/             security (jwt/hashing), time helpers
  database/          async engine/session + Alembic migrations
tests/               pytest (unit beside-ish, integration, health)
```

### Core invariants (enforced by structure)

1. **Cognee is a single seam.** The Cognee SDK is imported in **exactly one file**:
   `src/memory/cognee_client.py`. Everything memory-related funnels through
   `services/memory_service.py`.
2. **No SQL outside `repositories/`.** No business logic in routers.
3. **One dataset per ticker:** `dataset_name = f"company_{ticker}"`
   (`src/memory/dataset_naming.py`). Never cross-query datasets.
4. **Dedup before `cognee.add()`** via a content hash stored in Postgres
   `ingested_items` (`collectors/dedup.py` + `repositories/ingestion_repo.py`).
5. **JWT (RS256) auth + RBAC** (`user` / `admin`); internal `/memory/*` endpoints
   additionally require a service token.
6. **Prompt-injection guard:** retrieved web/news content is treated as *data*, not
   instructions (`ai/prompt_templates.py`).

---

## Running

Configuration is read from the repository-root `.env` (template `../.env.example`).
The backend keeps no separate env file — see `.env.example` here.

```bash
# From the repo root, with the full stack:
make up            # postgres, redis, backend, worker, beat, frontend
make migrate       # alembic upgrade head

# Backend only, locally:
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload          # API on :8000

# Workers:
celery -A src.workers.celery_app worker -l info -Q price,news,cognify
celery -A src.workers.celery_app beat -l info
```

Health checks: `GET /health` (liveness) and `GET /api/v1/health` (versioned).

## Quality

```bash
ruff check .        # lint
black --check .     # format
mypy src            # types (strict on src)
pytest              # tests
```

## Conventions

- Python 3.11, full type hints, `async def` for any I/O path (DB, HTTP, Cognee, LLM).
- Pydantic v2 on every request/response boundary.
- `snake_case` functions/vars, `PascalCase` classes, `UPPER_SNAKE` constants.
- One public concern per module; modules named for their role (`*_service.py`, `*_repo.py`).
- Conventional Commits: `type(scope): summary`.
