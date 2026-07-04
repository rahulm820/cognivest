# Backend

**Python 3.11 + FastAPI** application, with **Celery + Redis** for background work and **Postgres**
(SQLAlchemy 2.x + Alembic) for operational data. FastAPI is chosen because the Cognee SDK is
Python-native and FastAPI gives async I/O, automatic OpenAPI, and Pydantic v2 typing. Derived from
[ARCHITECTURE.md §4](../ARCHITECTURE.md) and [CLAUDE.md §3–§6](../CLAUDE.md).

## Layers (clean architecture)

Dependencies point **inward**: controllers → services → repositories.

```text
controllers / routes  →  services  →  repositories  →  Postgres
                              │
                              └──────→  memory_service → cognee_client → Cognee
```

| Layer | Directory | Responsibility |
|---|---|---|
| **Controllers / routes** | `src/controllers/`, `src/routes/` | Thin FastAPI handlers: validate via Pydantic, delegate, return a schema. **No business logic.** |
| **Middleware** | `src/middleware/` | `auth_middleware.py` (demo `X-User-Id` identity today; JWT/RBAC is roadmap — see [authentication.md](./authentication.md)), `rate_limit.py`. |
| **Services** | `src/services/` | Business logic / orchestration. Never import routers. |
| **Repositories** | `src/repositories/` | **All** Postgres access. No SQL anywhere else. Never import services. |
| **Models** | `src/models/` | SQLAlchemy models. |
| **Schemas** | `src/schemas/` | Pydantic request/response DTOs. |
| **Memory** | `src/memory/` | **The Cognee boundary** (see below). |
| **AI** | `src/ai/` | `answer_formatter.py`, `prompt_templates.py` — LLM answer generation. |
| **Collectors** | `src/collectors/` | Vendor fetch + normalize + dedup. |
| **Workers** | `src/workers/` | Celery app + tasks. |
| **Config / utils / database** | `src/config/`, `src/utils/`, `src/database/` | Settings, helpers, session + migrations. |

Routes: `companies.py`, `query.py`, `admin.py`, `auth.py`. Services: `watchlist_service.py`,
`collector_service.py`, `memory_service.py`, `query_service.py`. Repositories: `company_repo.py`,
`ingestion_repo.py`, `user_repo.py`. See [folder-structure.md](./folder-structure.md).

## The memory service boundary

`src/memory/` is the **single Cognee seam**:

- `cognee_client.py` — the **only** module that imports the Cognee SDK. Thin wrapper over
  `add()` / `cognify()` / `search()` / `recall()`.
- `dataset_naming.py` — the `f"company_{ticker}"` convention.
- `memory_service.py` (in `services/`) is the public entry point all callers use; it wraps
  `cognee_client`.

Everything memory-related funnels through here. **Never** import Cognee elsewhere; **never**
reimplement retrieval/embedding/reranking/summarization. See
[memory-architecture.md](./memory-architecture.md) and [CLAUDE.md §14](../CLAUDE.md).

## Request flow examples

### Query (sync) ✅ — the live path

```text
POST /companies/{ticker}/query
  → MemoryService.answer(ticker, question)
  → cognee_client.search(query_text=question, query_type=GRAPH_COMPLETION, datasets=[company_{ticker}])
  → grounded answer (Cognee GRAPH_COMPLETION, single-LLM, Gemini) + honest citations
```

No `dataset_name=`/`filters=` on `search` (cognee 1.2.2) and **no separate answer-formatter LLM** —
the answer is Cognee's `GRAPH_COMPLETION` output.

### Ingestion (async) 🎯 — designed, not built

```text
Celery task → collector_service.run_for_ticker(ticker)          # stub
  → price_collector / news_collector fetch                       # stub
  → normalizer + dedup (content hash vs ingested_items)          # stub
  → memory_service.ingest → cognee_client.add(dataset_name=company_{ticker})
  → cognee_client.cognify(datasets=[company_{ticker}])
```

`MemoryService.ingest` (add + cognify) is implemented on the seam, but no collector or route drives it
yet; the demonstrable round-trip is [`scripts/cognee_roundtrip.py`](../scripts/cognee_roundtrip.py).

## Workers / Celery queues 🎯 (containers boot; task bodies are stubs)

The design uses **Celery + Redis broker** + **Celery Beat**, with three queues that scale/throttle
independently (from [ARCHITECTURE.md §4.7](../ARCHITECTURE.md)):

| Queue | Work |
|---|---|
| `price` | scheduled price collection (`PRICE_COLLECT_CRON`). |
| `news` | scheduled news/web collection (`NEWS_COLLECT_INTERVAL_HOURS`). |
| `cognify` | `cognee.cognify()` runs, decoupled so a slow cognify never blocks fetches. |

Intended properties (roadmap): idempotent tasks (dedup hash before `add()`), exponential-backoff
retries with a dead-letter queue, and per-ticker isolation. Today the `worker`/`beat` containers start
but the tasks are stubs and nothing is scheduled — the demo path is synchronous.

Run locally: `make worker`, `make beat`.

## Config

Settings are loaded from environment (`.env` locally; secrets manager in prod) into a typed Pydantic
settings object in `src/config/`. Every variable is documented in [environment.md](./environment.md);
add new ones to both `.env.example` and that doc.

## API

REST/JSON under `/api/v1`; the **OpenAPI spec is the contract** the frontend types are generated
from. Errors use a consistent envelope. Full reference: [api.md](./api.md). Auth:
[authentication.md](./authentication.md). Schema: [database.md](./database.md).
