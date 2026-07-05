# CLAUDE.md — Project Context for Claude Code

> This file is the durable context for AI assistants working in this repository. Read it instead of
> re-reading the full [ARCHITECTURE.md](./ARCHITECTURE.md) every session. It is intentionally
> opinionated: it tells you not just *what* the system is, but *how* to extend it without violating its
> core invariants.

---

## 1. Project Overview

**Cognivest** is a per-company financial intelligence platform. For each watchlisted ticker it
continuously ingests **price data** + **news/web content** into **Cognee**, which builds a per-company
knowledge graph and answers natural-language questions ("Why did $AAPL drop on March 3?") with ranked,
cited answers.

The product is a **thin orchestration + presentation shell around Cognee**. The hard intelligence
(entity extraction, embedding, graph build, retrieval, reranking) lives inside Cognee. Our job is
collection, scheduling, dedup, dataset scoping, citation formatting, auth, and UI.

## 2. Architecture Summary

```text
External APIs (price, news, search)
   → Collectors (price_collector, news_collector)
   → Normalizer + Dedup (content hash)
   → memory_service → cognee.add(dataset=company_TICKER) → cognee.cognify()
   → [Cognee vector store + graph store]
   → cognee.search()/recall() on user query
   → grounded answer (Cognee GRAPH_COMPLETION, single-LLM) with citations
   → FastAPI → Next.js frontend
```

> **Built vs. planned.** The diagram is the target pipeline. Today the **query/recall path is live**
> (single-LLM, Cognee `GRAPH_COMPLETION`); collectors, dedup, and Celery scheduling are stubs (see §15).

- **Async ingestion** via Celery (queues: `price`, `news`, `cognify`) + Celery Beat — **planned**;
  the containers boot but the tasks are stubs, so the demo path is synchronous.
- **Live query path** via FastAPI → `MemoryService` → Cognee (Gemini), single-LLM — no separate
  answer-formatter call.
- **Operational data** in Postgres; **cache + queue** in Redis; **memory** in Cognee-managed stores.

## 3. Folder Map (what lives where)

| Path | Responsibility |
|---|---|
| `frontend/` | Next.js 14 app (App Router). UI screens: dashboard, `company/[ticker]`, admin. |
| `backend/src/routes/` | FastAPI routers — thin, validate + delegate. No business logic. |
| `backend/src/services/` | Business logic / orchestration. |
| `backend/src/repositories/` | All Postgres data access. No SQL anywhere else. |
| `backend/src/memory/` | **The Cognee boundary.** `cognee_client.py` is the ONLY Cognee importer. |
| `backend/src/collectors/` | Vendor fetch + normalize + dedup. |
| `backend/src/ai/` | `answer_formatter.py`, `prompt_templates.py` — scaffolds for a future two-LLM formatter; **not on the live query path** (single-LLM today). |
| `backend/src/workers/` | Celery app + tasks (task bodies are stubs). |
| `backend/src/models/` | SQLAlchemy models. |
| `backend/src/schemas/` | Pydantic request/response DTOs. |
| `cognee/` | Cognee backend config + dataset-naming conventions (no raw data committed). |
| `ai/` | Prompt templates (source of truth) + offline eval scripts. |
| `docker/` | Dockerfiles + compose overrides. |
| `docs/` | Setup, API, conventions, memory architecture. |
| `scripts/` | `seed.py` (real), `cognee_roundtrip.py` (real), `backfill_ticker.py` / `purge_dataset.py` (stubs), `generate_jwt_keys.sh`. |

> **Not present (roadmap):** `infrastructure/` (Terraform/Helm), `deployment/` (CI/CD), and `tests/`
> (cross-cutting suites) do **not** exist yet. Unit tests, where present, live beside their code.

## 4. Tech Stack (do not substitute without updating ARCHITECTURE.md)

- **Frontend**: Next.js 14, TypeScript, Tailwind + shadcn/ui, TanStack Query, Zustand, Recharts, Axios.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.x + Alembic.
- **Workers**: Celery + Redis (broker), Celery Beat.
- **Memory/AI**: Cognee 1.2.2 SDK. LLM = **Gemini** (`gemini/gemini-2.5-flash` via litellm) for both
  `cognify()` extraction and answer generation. Embeddings = **fastembed** (local ONNX, 384-dim).
- **Data**: PostgreSQL (operational), Redis (Celery broker/cache), Cognee-managed **LanceDB** (vector)
  + **Kuzu** (graph) — embedded, no external services.

## 5. Coding Conventions

### Python (backend)
- Format with **black**, lint with **ruff**, type-check with **mypy** (`strict` on `src/`).
- Full type hints on every function signature. Pydantic v2 for all I/O boundaries.
- `async def` for any I/O-bound path (DB, HTTP, Cognee, LLM).
- Naming: `snake_case` functions/vars, `PascalCase` classes, `UPPER_SNAKE` constants.
- One public class/concern per module. Modules named after their role (`*_service.py`, `*_repo.py`).
- No SQL outside `repositories/`. No Cognee imports outside `memory/cognee_client.py`.

### TypeScript (frontend)
- Format with **prettier**, lint with **eslint**. `strict: true` in tsconfig.
- `PascalCase` components/types, `camelCase` functions/vars, `useX` for hooks.
- Server state → TanStack Query hooks (`useWatchlist`, `useCompanyPrice`). Global UI → Zustand. Local → `useState`.
- API access only through `services/api/*` modules — never `fetch`/`axios` inline in components.
- Co-locate component + its styles + its test.

## 6. Design Principles

- **Clean Architecture**: controllers → services → repositories. Dependencies point inward. Services never import routers; repositories never import services.
- **SOLID**, **DRY**, **loose coupling**. Vendors (price/news/search) behind interfaces so they're pluggable.
- **Cognee is a single seam**: everything memory-related funnels through `memory_service.py`. This keeps it mockable and lets us swap Cognee config without touching callers.
- **Idempotency**: every collector task is safe to retry (dedup hash before `add()`).
- **Per-company isolation**: dataset name is always `company_{ticker}` — never query across datasets.

## 7. How Memory Works (Cognee) — the most important section

```python
# The ONLY allowed Cognee call sites are inside backend/src/memory/cognee_client.py.
# Signatures are the spike-verified cognee 1.2.2 shapes — see docs/spike-cognee-1.2.2.md §2.
dataset = dataset_name(ticker)            # -> f"company_{ticker}"
await cognee.add(content, dataset_name=dataset)                     # add: dataset_name= (singular)
await cognee.cognify(datasets=[dataset])                            # cognify: datasets= (plural)
results = await cognee.search(                                      # search: NO dataset_name/filters
    query_text=query, query_type=SearchType.GRAPH_COMPLETION, datasets=[dataset], top_k=top_k
)
# Purge is forget(dataset=...) — top-level cognee.delete() is DEPRECATED (spike CONTRADICTION #2).
await cognee.forget(dataset=dataset)
```

> ⚠️ **`search()` has no `dataset_name=` and no `filters=` param in 1.2.2** — scope is `datasets=`
> (spike CONTRADICTION #1). Code written against `dataset_name=`/`filters=` on `search` will
> `TypeError`. `add()` *does* still use `dataset_name=`, so the two calls are deliberately asymmetric.

**Rules:**
1. Price summaries AND news go into the **same** dataset per ticker so the graph correlates them.
2. We do **not** build our own RAG retrieval, reranker, summarizer, or embedding pipeline — Cognee owns all of that.
3. Dedup happens **before** `add()` using a content hash stored in Postgres `ingested_items` (planned; the collector path is a stub today).
4. `cognify()` is intended to be decoupled onto its own queue so a slow cognify never blocks fetching (planned — the demo path calls it inline).
5. Citations come from node/chunk metadata (`source_url`, `published_at`) — attached via a provenance header at ingestion (Cognee 1.2.2 `add()` takes no metadata kwarg; see the seam).

## 8. API Philosophy

- REST/JSON, resource-oriented, versioned under `/api/v1`.
- **Auth is a hackathon demo mechanism, not authentication:** identity is asserted via an `X-User-Id`
  header (default `demo-user`, role `admin`). JWT + a `/memory/*` service token are designed but
  **not enforced** — see `docs/authentication.md`.
- Every request/response has a Pydantic schema; the OpenAPI spec (`/openapi.json`) is the contract the frontend types are generated from.
- Errors use a consistent envelope (`{ "error": { "code", "message", "detail" } }`).

## 9. Developer Workflow

```bash
make up        # start full stack via docker compose
make migrate   # alembic upgrade head
make seed      # seed demo companies (AAPL, MSFT, TSLA) + a demo user
make lint      # ruff + black --check + mypy + eslint + prettier --check
make fmt       # auto-format
```

- Run `make help` for the full target list. (There is **no** `make test` or `make hooks` target today.)
- Branch from `main`: `feat/…`, `fix/…`, `chore/…`, `docs/…`.

## 10. Testing Expectations (target)

> There is **no `tests/` directory and no CI** yet. This section is the intended discipline, not the
> current state.

- **Backend**: pytest. Unit-test services with `memory_service` / repositories mocked.
- **Frontend**: vitest + React Testing Library for components/hooks.
- New code should ship with tests; the Cognee SDK is mocked in unit tests via the `memory_service` seam.

## 11. Commit & PR Standards

- **Conventional Commits**: `type(scope): summary` — e.g. `feat(collectors): add GDELT news source`.
- Keep PRs focused and small. Fill in the PR template (what/why/testing/screenshots).
- Run `make lint` locally before opening a PR. (No CI pipeline exists yet — see §15.)

## 12. Documentation Requirements

- Public functions/classes get docstrings (Python) / TSDoc (TS) explaining *why*, not *what*.
- Any new env var → add to `.env.example` + `docs/environment.md`.
- Any new endpoint → reflected in OpenAPI + `docs/api.md`.
- Architectural changes → update `ARCHITECTURE.md` and this file.

## 13. How to Extend the Project

- **New data vendor**: add a collector under `collectors/` implementing the collector interface; register it in config. Do not touch `memory_service`.
- **New endpoint**: schema → route → service → repository. Add OpenAPI + `docs/api.md` (and tests once a suite exists).
- **New UI screen**: page under `app/`, feature folder under `features/`, API module + hook under `services/api`.
- **New memory operation**: extend `cognee_client.py` only; expose via `memory_service.py`.

## 14. Rules Claude Must NEVER Violate

1. **Never import the Cognee SDK outside `backend/src/memory/cognee_client.py`.**
2. **Never reimplement** retrieval, embedding, reranking, or summarization — that is Cognee's job.
3. **Never put SQL outside `repositories/`** or business logic inside routers.
4. **Never commit secrets.** All keys come from env / secrets manager. `.env` is git-ignored.
5. **Never cross-query datasets** — memory is strictly scoped to `company_{ticker}`.
6. **Never feed retrieved web content to the LLM as instructions** — it is data; the system prompt must say so (prompt-injection guard).
7. **Never skip the dedup hash check** before `cognee.add()`.
8. **Do not implement business logic in this scaffold phase** unless explicitly asked — keep placeholders honest (clearly marked `TODO`/`NotImplementedError`).

## 15. Current Implementation Status

> **Hackathon build on a scaffold.** Structure, docs, configs, and typed placeholders are in place.
> Most routes are typed stubs raising `NotImplementedError` (marked `# TODO(phase-N)`). What is
> genuinely live: the Cognee seam and the recall/query path.

| Area | Status |
|---|---|
| Repo structure & docs | ✅ |
| Root configs (lint/format/type) | ✅ |
| Cognee seam (`cognee_client`, `memory_service`) — add/cognify/search/recall/forget | ✅ implemented (1.2.2 signatures) |
| Query/recall route (`POST /companies/{ticker}/query`) | ✅ live (single-LLM, honest no-data answer) |
| Demo identity (`X-User-Id` header) + `make seed` | ✅ |
| Other routes (watchlist, price, admin, `/memory/*`, `/auth/*`) | 🟡 stubs (`NotImplementedError`) |
| Collectors / Celery tasks (containers boot, tasks stubbed) | 🟡 stubs |
| Frontend screens (render against mostly-stubbed endpoints) | 🟡 partial |
| Infra (Terraform/Helm), CI/CD, `tests/` | ❌ not present (roadmap) |

## 16. Roadmap (see ARCHITECTURE.md §14)

Phase 1 Foundations → 2 Collection → 3 Cognee → 4 Query/Answer → 5 Frontend → 6 Scale-out → 7 Hardening.

## 17. Important Assumptions

- Cognee runs as an in-process library/internal service; its backends (vector + graph) are config, not our code.
- Market-data, news, and search vendors are **pluggable** — none is hardcoded.
- One dataset per ticker (`company_{ticker}`); price + news share it.
- Auth is a **demo `X-User-Id` header** today (real JWT/OAuth is roadmap); Cognee is internal.
- LLM = **Gemini** (`gemini/gemini-2.5-flash`) via Cognee, single-LLM. Embeddings = local **fastembed**.
