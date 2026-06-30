# Cognivest

> Per-company financial intelligence platform powered by [Cognee](https://www.cognee.ai/) — correlating **price action** with **news/web narrative** in a unified, per-ticker knowledge graph.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)

---

## 📖 Overview

Cognivest continuously ingests two data streams per publicly traded company —
**structured price data** and **unstructured web/news content** — and feeds both into
**Cognee**, which owns ingestion (`add()`), knowledge-graph construction (`cognify()`), and
retrieval (`search()` / `recall()`).

The application layer is a **thin orchestration + presentation shell** around Cognee:
scheduling, deduplication, dataset naming, and citation formatting — **not** a reimplementation
of graph/vector logic.

> Answer questions like *"Why did $AAPL drop 8% on March 3rd?"* by automatically correlating a
> price delta with the same-day news that explains it.

### Key capabilities

- 🔄 **Continuous per-ticker collection** of price + broad web/news content.
- 🧠 **Cognee as the single memory layer** — one dataset per company (`company_{ticker}`).
- 💬 **Natural-language, company-scoped Q&A** with ranked, cited answers.
- 📈 **Price chart with correlated news markers** in the UI.
- 🛡️ **Production-ready**: dedup, scheduling, observability, security — not a notebook script.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind + shadcn/ui, TanStack Query, Zustand, Recharts |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy + Alembic |
| **Memory / AI** | Cognee SDK, Anthropic Claude (answer generation) |
| **Workers** | Celery + Redis (broker), Celery Beat (scheduling) |
| **Data** | PostgreSQL (operational), Redis (cache + queue), Cognee-managed vector + graph stores |
| **Infra** | Docker, Kubernetes (Helm), Terraform, GitHub Actions, Vercel (frontend) |

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full Software Architecture Document.

---

## 📂 Repository Structure

```text
cognivest/
├── frontend/          # Next.js web application (dashboard, company detail, admin)
├── backend/           # FastAPI app — controllers, services, repositories, workers
├── cognee/            # Cognee backend configuration + dataset naming conventions
├── ai/                # Prompt templates + offline answer-quality evaluation
├── docs/              # Architecture, setup, API, runbooks, conventions
├── scripts/           # Operational scripts (backfill, purge)
├── config/            # Shared static configuration
└── .github/           # Issue/PR templates
```

Each top-level directory carries its own `README.md` explaining its purpose. See
[docs/folder-structure.md](./docs/folder-structure.md) for the recursive breakdown.

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- [Node.js](https://nodejs.org/) 20+ and [pnpm](https://pnpm.io/) (frontend)
- [Python](https://www.python.org/) 3.11+ and [uv](https://github.com/astral-sh/uv) or `pip` (backend)
- A local Postgres and Redis instance
- API keys for: a market-data vendor, a news API, a web-search API, and Anthropic (see `.env.example`)

### 1. Clone & configure

```bash
git clone https://github.com/your-org/cognivest.git
cd cognivest
cp .env.example .env
# Fill in vendor + LLM API keys + local Postgres/Redis URLs in .env
```

### 2. Install & run

```bash
make install     # install backend + frontend deps
make migrate     # apply Alembic migrations
make seed        # (optional) seed a demo ticker

make backend     # run FastAPI (uvicorn) — http://localhost:8000/docs
make frontend    # run Next.js — http://localhost:3000
make worker      # run a Celery worker (separate terminal)
make beat        # run Celery Beat scheduler (separate terminal)
```

### 3. Common commands

```bash
make help        # list all targets
make lint        # ruff + black + eslint + prettier
make fmt         # auto-format everything
make typecheck   # mypy + tsc
```

See the [setup guide](./docs/setup.md) for the full native workflow.

---

## 🧠 How Memory Works (Cognee)

> ⚠️ **The most important architectural rule:** `backend/src/memory/cognee_client.py` is the
> **only** module permitted to import the Cognee SDK. Everything else goes through
> `memory_service.py`.

```text
collect → normalize → dedup → cognee.add(dataset=company_TICKER)
        → cognee.cognify() → [vector store + graph store]
        → cognee.search()/recall() on query → LLM answer with citations
```

- **One Cognee dataset per company** (`company_{ticker}`) → graphs never bleed across tickers.
- Price summaries and news land in the **same** dataset so the graph can correlate them.
- Retrieval (vector similarity + graph traversal + reranking) is Cognee-internal — the backend
  does **not** run its own RAG retrieval.

Full detail: [docs/memory-architecture.md](./docs/memory-architecture.md).

---

## 🗺️ Roadmap

| Phase | Scope |
|---|---|
| 1 — Foundations | Repo scaffold, schema, auth, FastAPI + Next.js skeleton, Docker Compose |
| 2 — Collection | Price + news collectors, normalizer, dedup, Celery scheduling |
| 3 — Cognee | `memory_service` wrapper, dataset-per-ticker, `add`/`cognify` wiring |
| 4 — Query | `/query` endpoint, `answer_formatter`, citations in UI |
| 5 — Frontend | Dashboard, company detail, watchlist CRUD |
| 6 — Scale-out | Multi-ticker scheduling, DLQ, rate limiting, caching, admin screen |
| 7 — Hardening | Kubernetes, secrets, monitoring, security review, load testing |

See the full [roadmap](./docs/roadmap.md) and [CHANGELOG.md](./CHANGELOG.md).

---

## 🤝 Contributing

Read [CONTRIBUTING.md](./CONTRIBUTING.md) and the [Code of Conduct](./CODE_OF_CONDUCT.md) before
opening a PR. Security issues: see [SECURITY.md](./SECURITY.md).

## 📄 License

[MIT](./LICENSE) © Cognivest contributors.
