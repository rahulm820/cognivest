# System Design — overview

A condensed overview of Cognivest. The full design vision is in
[ARCHITECTURE.md](../ARCHITECTURE.md) (with built-vs-target tags throughout); this page is a map into
it. The diagrams below are the **target** architecture — today only the query/recall path is wired
end-to-end (see the README *Limitations* section).

## What it is

Cognivest continuously gathers two streams per company — **structured price data** and
**unstructured web/news content** — and feeds both into **Cognee** as a unified memory layer. Cognee
owns ingestion (`add()`), knowledge-graph construction (`cognify()`), and retrieval (`search()` /
`recall()`). The app is a **thin orchestration + presentation shell** around it: collection,
scheduling, dedup, dataset scoping, citation formatting, auth, and UI.

Users ask natural-language questions scoped to a company and date range
(*"Why did $AAPL drop on March 3?"*) and get **ranked, cited** answers.

## High-level architecture

```mermaid
flowchart TB
    subgraph Sources["External Sources"]
        PRICE[Market Data API]
        NEWS[News APIs / RSS]
        SEARCH[Web Search API]
    end

    subgraph Collection["Collection Layer"]
        SCHED[Scheduler<br/>per-company jobs]
        PCOL[Price Collector]
        NCOL[News/Web Collector]
        DEDUP[Dedup + Normalizer<br/>by URL hash]
    end

    subgraph Memory["Cognee Memory Layer"]
        ADD[cognee.add<br/>dataset=company_TICKER]
        COGNIFY[cognee.cognify<br/>entity + relationship extraction]
        VDB[(Vector Store)]
        GDB[(Graph Store)]
        QUERY[cognee.search / recall]
    end

    subgraph App["Application Layer"]
        API[Backend API]
        AUTH[Auth Service]
        WEB[Frontend Web App]
    end

    PRICE --> PCOL
    NEWS --> NCOL
    SEARCH --> NCOL
    SCHED --> PCOL
    SCHED --> NCOL
    PCOL --> DEDUP
    NCOL --> DEDUP
    DEDUP --> ADD
    ADD --> COGNIFY
    COGNIFY --> VDB
    COGNIFY --> GDB
    VDB --> QUERY
    GDB --> QUERY
    QUERY --> API
    API --> WEB
    AUTH --> API
```

## Component view

```mermaid
flowchart LR
    subgraph FE[Frontend]
        UI[React/Next.js App]
    end
    subgraph BE[Backend Services]
        GW[API Gateway / BFF]
        WATCH[Watchlist Service]
        SCHEDSVC[Scheduler Service]
        COLLECTSVC[Collector Workers]
        MEMSVC[Memory Orchestration Service<br/>wraps Cognee SDK]
        ADMIN[Admin/Observability Service]
    end
    subgraph Data[Data Stores]
        SQLDB[(Relational DB<br/>tickers, users, jobs, audit)]
        CACHE[(Redis Cache)]
        QUEUE[(Job Queue)]
        COGNEEDB[(Cognee Vector + Graph Store)]
    end

    UI --> GW
    GW --> WATCH
    GW --> MEMSVC
    GW --> ADMIN
    WATCH --> SQLDB
    SCHEDSVC --> QUEUE
    QUEUE --> COLLECTSVC
    COLLECTSVC --> MEMSVC
    MEMSVC --> COGNEEDB
    MEMSVC --> CACHE
    ADMIN --> SQLDB
```

## Stack at a glance

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind + shadcn/ui, TanStack Query, Zustand, Recharts, Axios |
| Backend | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.x + Alembic |
| Workers | Celery + Redis broker, Celery Beat (queues: `price`, `news`, `cognify`) — 🎯 tasks stubbed |
| Memory / AI | Cognee 1.2.2 SDK; **Gemini** (`gemini/gemini-2.5-flash`) LLM; **fastembed** (local) embeddings |
| Data | PostgreSQL, Redis, Cognee-managed **LanceDB** (vector) + **Kuzu** (graph) |

## Key invariants

- **Cognee is a single seam** — imported only in `backend/src/memory/cognee_client.py`. ✅
- **One dataset per ticker** — `company_{ticker}`; price + news share it; never cross-query. ✅
- **Single-LLM answers** — Cognee `GRAPH_COMPLETION` (Gemini); no separate answer-formatter. ✅
- **Auth is a demo `X-User-Id` header today** — real JWT/OAuth is roadmap ([authentication.md](./authentication.md)).
- **Retrieved content is data, not instructions** (prompt-injection design stance).

## Where to go next

| Topic | Doc |
|---|---|
| The Cognee memory layer | [memory-architecture.md](./memory-architecture.md) |
| Backend layers & workers | [backend.md](./backend.md) |
| Frontend structure | [frontend.md](./frontend.md) |
| API reference | [api.md](./api.md) |
| Database schema | [database.md](./database.md) |
| Auth model | [authentication.md](./authentication.md) |
| Cognee spike (ground truth) | [spike-cognee-1.2.2.md](./spike-cognee-1.2.2.md) |
| Roadmap | [roadmap.md](./roadmap.md) |
