# Folder Structure

This document explains every top-level directory in the repository and its key subdirectories.
The structure derives from [ARCHITECTURE.md](../ARCHITECTURE.md) §3–§4 and the folder map in
[CLAUDE.md §3](../CLAUDE.md).

```text
cognivest/
├── frontend/          # Next.js 14 app (App Router) — UI
├── backend/           # FastAPI + Celery — API, workers, the Cognee boundary
├── cognee/            # Cognee backend config + dataset-naming conventions (no raw data)
├── ai/                # Prompt templates (source of truth) + offline evaluation
├── infrastructure/    # Terraform (IaC) + Helm charts
├── deployment/        # GitHub Actions + ArgoCD definitions
├── docker/            # Dockerfiles + compose overrides
├── docs/              # This documentation tree
├── scripts/           # Operational CLI scripts (backfill, purge, seed, key-gen)
├── tests/             # Cross-cutting integration / e2e / performance / memory tests
├── config/            # Shared, non-secret configuration (lint/format/type/test roots)
├── .github/           # Issue/PR templates + CI workflow definitions
├── secrets/           # Git-ignored: generated JWT keys, local-only secrets
├── ARCHITECTURE.md    # The Software Architecture Document (single source of truth)
├── CLAUDE.md          # Durable AI-assistant context + invariants
├── CONTRIBUTING.md    # Contribution guide
├── Makefile           # Developer task runner
├── docker-compose.yml # Local full-stack orchestration
└── .env.example       # Environment template (copy to .env)
```

## `frontend/` — Next.js 14 web app

The presentation layer (App Router, TypeScript, Tailwind + shadcn/ui).

```text
frontend/
  src/
    app/                  # Next.js App Router pages (file-based routing)
      (auth)/             # login / OAuth callback routes
      dashboard/          # watchlist overview screen
      company/[ticker]/   # company detail: price chart + query box
      admin/              # ingestion health / ops screen (admin only)
    components/
      ui/                 # shadcn primitives (Button, Input, Badge, Spinner)
      charts/             # PriceChart, NewsMarkerOverlay
      layout/             # AppShell, Sidebar, TopNav
    features/             # vertical feature slices
      watchlist/
      company-query/
      ingestion-status/
    hooks/                # React hooks (useWatchlist, useCompanyPrice, ...)
    contexts/             # React contexts
    services/
      api/                # axios client + per-resource endpoint modules (ONLY API seam)
    store/                # Zustand stores (selected ticker, date range, theme)
    types/                # OpenAPI-generated + hand-written types
    utils/
    constants/
    styles/
```

See [frontend.md](./frontend.md) for screen-by-screen detail.

## `backend/` — FastAPI + Celery

The application and orchestration layer. Clean architecture: controllers → services →
repositories, dependencies pointing inward.

```text
backend/
  src/
    controllers/        # FastAPI route handlers (thin)
    routes/             # router modules: companies.py, query.py, admin.py, auth.py
    middleware/         # auth_middleware.py, rate_limit.py
    services/           # business logic / orchestration
      watchlist_service.py
      collector_service.py
      memory_service.py   # the public memory boundary (wraps cognee_client)
      query_service.py
    repositories/       # ALL Postgres data access (no SQL anywhere else)
      company_repo.py
      ingestion_repo.py
      user_repo.py
    models/             # SQLAlchemy models
    schemas/            # Pydantic request/response DTOs
    memory/             # THE Cognee boundary
      cognee_client.py    # the ONLY module that imports the Cognee SDK
      dataset_naming.py   # f"company_{ticker}" convention
    ai/                 # LLM answer generation
      answer_formatter.py
      prompt_templates.py
    collectors/         # vendor fetch + normalize + dedup
      price_collector.py
      news_collector.py
      normalizer.py
      dedup.py
    workers/            # Celery app + tasks
      celery_app.py
      tasks.py
    utils/
    config/
    database/
      session.py
      migrations/         # Alembic migrations
```

See [backend.md](./backend.md). The `memory/` directory is the single Cognee seam — see
[memory-architecture.md](./memory-architecture.md).

## `cognee/` — Cognee configuration

Holds **Cognee backend configuration and dataset-naming conventions only**. No raw data is ever
committed here. The Cognee SDK itself is used inside the backend
(`backend/src/memory/cognee_client.py`), not here.

```text
cognee/
  config/                       # env-driven vector + graph backend configuration
    cognee.config.example.yaml
  datasets/                     # documents the company_{ticker} convention (data git-ignored)
    .gitkeep
```

See [`cognee/README.md`](../cognee/README.md).

## `ai/` — Prompts + evaluation

The **source of truth for prompt templates** (mirrored into `backend/src/ai/prompt_templates.py`)
plus offline evaluation of answer quality and citation accuracy.

```text
ai/
  prompts/
    system_prompt.md            # canonical financial-news-analyst system prompt
    answer_generation.md        # answer-generation user/template prompt
    README.md                   # how prompts map into the backend
  eval/
    run_eval.py                 # offline eval harness (citation accuracy, groundedness, latency)
    datasets/                   # fixture question sets (git-ignored payloads)
      .gitkeep
```

See [`ai/README.md`](../ai/README.md) and [prompting.md](./prompting.md).

## `infrastructure/` — Infrastructure as code

Terraform modules (RDS Postgres, ElastiCache Redis, secrets, networking) and Helm charts for the
backend API, Celery workers, and Celery Beat. See [deployment.md](./deployment.md).

## `deployment/` — CI/CD + GitOps

GitHub Actions workflow definitions and ArgoCD application manifests that deploy the Helm charts.
Vercel handles frontend deploys directly from Git.

## `docker/` — Container build context

Dockerfiles for the backend API and worker images plus Docker Compose overrides for local
development. The root `docker-compose.yml` wires the local full stack.

## `docs/` — Documentation

This tree. Indexed by [docs/README.md](./README.md): setup, API, conventions, memory architecture,
deployment, and on-call [runbooks](./runbooks/README.md).

## `scripts/` — Operational CLIs

Admin and ops scripts: `backfill_ticker.py`, `purge_dataset.py`, `seed.py`, and
`generate_jwt_keys.sh`. See [`scripts/README.md`](../scripts/README.md).

## `tests/` — Cross-cutting tests

Integration, e2e (Playwright), performance (k6), and Cognee memory-contract tests. **Unit tests
live beside the code they test** (inside `backend/` and `frontend/`); this directory holds only
cross-cutting suites. See [`tests/README.md`](../tests/README.md).

## `config/` — Shared configuration

Non-secret shared configuration roots referenced by tooling (lint/format/type/test). Project-level
tool config (ruff, black, mypy, eslint, prettier) lives alongside each app; this directory holds
configuration shared across apps.

## `.github/` — GitHub metadata

Issue templates, the pull-request template, and CI workflow definitions (lint → type → test →
build → deploy). Referenced by [development-workflow.md](./development-workflow.md).
