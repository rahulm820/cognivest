# Cognivest — Documentation

Welcome to the Cognivest documentation. Cognivest is a **per-company financial
intelligence platform powered by [Cognee](https://github.com/topoteretes/cognee)**: for each
watchlisted ticker it ingests **price data** and **news/web content** into Cognee, which builds a
per-company knowledge graph and answers natural-language questions with grounded answers.

> **Hackathon build.** One route is live end-to-end (`POST /companies/{ticker}/query`); many features
> are scaffolds. Docs are tagged ✅ built / 🎯 target where it matters — see the README's *Limitations*
> section and [CLAUDE.md §15](../CLAUDE.md).

> The product is a **thin orchestration + presentation shell around Cognee**. The hard
> intelligence (entity extraction, embedding, graph build, retrieval, reranking) lives inside
> Cognee. See [memory-architecture.md](./memory-architecture.md).

The canonical, exhaustive design lives in [`ARCHITECTURE.md`](../ARCHITECTURE.md) (the Software
Architecture Document) and the durable AI-assistant context lives in [`CLAUDE.md`](../CLAUDE.md).
These docs expand on specific areas and are kept consistent with both.

## Table of Contents

### Getting started
- [Setup](./setup.md) — prerequisites, clone, `.env`, Docker + native paths, first run, troubleshooting.
- [Environment Variables](./environment.md) — every variable in `.env.example` documented.
- [Folder Structure](./folder-structure.md) — what lives in every directory.

### Working in the codebase
- [Development Workflow](./development-workflow.md) — branching, commits, `make` targets, PR flow, debugging.
- [Coding Standards](./coding-standards.md) — Python + TypeScript conventions and layering rules.
- [Contributing](./contributing.md) — pointer to the root contribution guide + the Cognee invariant.

### Architecture
- [System Design](./system-design.md) — condensed system overview with high-level diagrams.
- [Backend](./backend.md) — FastAPI layers, Celery queues, the memory boundary.
- [Frontend](./frontend.md) — Next.js app structure, screens, state management, API services.
- [Memory Architecture](./memory-architecture.md) — **the Cognee deep-dive** (add → cognify → search).
- [Database](./database.md) — operational Postgres schema, indexes, migrations.
- [Authentication](./authentication.md) — the demo `X-User-Id` identity (JWT/OAuth is roadmap).
- [Prompting](./prompting.md) — single-LLM answer generation today; the formatter design is roadmap.

### Reference
- [API Reference](./api.md) — REST API with a live-vs-stubbed status matrix (OpenAPI is the source of truth).
- [Roadmap](./roadmap.md) — the 7-phase roadmap and future enhancements.
- [Cognee 1.2.2 spike](./spike-cognee-1.2.2.md) — verified SDK signatures + round-trip (ground truth).

## The one rule you must never break

The Cognee SDK is imported in **exactly one place**: `backend/src/memory/cognee_client.py`.
Memory is always scoped to a single dataset per ticker, `company_{ticker}`. We never cross-query
datasets and never reimplement retrieval, embedding, reranking, or summarization — that is
Cognee's job. See [CLAUDE.md §14](../CLAUDE.md) and [memory-architecture.md](./memory-architecture.md).
