# Roadmap

The development roadmap and future enhancements, from [ARCHITECTURE.md §14–§15](../ARCHITECTURE.md).

**Current status:** a hackathon build on a scaffold (see [CLAUDE.md §15](../CLAUDE.md)). Live today:
the Cognee seam (add/cognify/search/recall/forget, 1.2.2 signatures), per-ticker isolation, and the
**query/recall route** (single-LLM, Gemini). Stubbed: watchlist/price/admin routes, collectors, and
Celery tasks. Not present: auth (demo header instead), infrastructure, and CI.

## Development phases

| Phase | Scope | Complexity |
|---|---|---|
| **1 — Foundations** | Repo scaffolding, Postgres schema, auth, basic FastAPI + Next.js skeleton, Docker Compose | Low |
| **2 — Collection Layer** | Price collector, news/web collector, normalizer, dedup, Celery scheduling for a single test ticker | Medium |
| **3 — Cognee Integration** | `memory_service.py` wrapper, dataset-per-ticker, `add()`/`cognify()` wired in, `search()` smoke tests | Medium-High |
| **4 — Query + Answer Pipeline** | `/query` endpoint, `answer_formatter`, LLM prompt template, citation rendering | Medium |
| **5 — Frontend Buildout** | Dashboard, company detail page, watchlist CRUD | Medium |
| **6 — Scale-out** | Multi-ticker scheduling, DLQ, rate limiting, caching, admin/observability screen | High |
| **7 — Production Hardening** | Kubernetes, secrets, monitoring/alerting, security review, load testing | High |

Stubs across the repo are marked `# TODO(phase-N)` to indicate which phase implements them.

## Future enhancements

- **Multi-hop / agentic querying** — LLM issues follow-up `cognee.search()` calls mid-reasoning.
- **Multi-agent support** — dedicated agents per task sharing the same per-company Cognee dataset.
- **Personalization** — per-user memory layer blended with company datasets at query time.
- **Analytics** — sentiment trend lines from graph entity polarity over time.
- **Observability** — full OpenTelemetry tracing across collector → Cognee → LLM call.
- **Enterprise readiness** — SSO (SAML/OIDC), audit-log export, per-tenant data residency.
- **Mobile** — React Native app reusing the same backend API surface.

See also [system-design.md](./system-design.md) and [ARCHITECTURE.md](../ARCHITECTURE.md).
