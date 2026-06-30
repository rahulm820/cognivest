# Coding Standards

These standards are enforced by tooling and CI. They derive from [CLAUDE.md §5–§6](../CLAUDE.md)
and the root [CONTRIBUTING.md](../CONTRIBUTING.md). Run `make lint` and `make fmt`.

## Python (backend)

### Tooling

| Tool | Role | Config |
|---|---|---|
| **black** | formatter (opinionated, non-negotiable) | project `pyproject.toml` |
| **ruff** | linter (+ import sort, pyflakes, pycodestyle) | `pyproject.toml` |
| **mypy** | static type checker, `strict` on `src/` | `pyproject.toml` |

`make fmt` runs `ruff check --fix` + `black`; `make lint` runs `ruff check`, `black --check`, and
`mypy src`.

### Typing

- **Full type hints on every function signature** — parameters and return type.
- `mypy --strict` must pass on `backend/src/`. No untyped defs, no implicit `Any`.
- **Pydantic v2** models for every I/O boundary (request, response, config, vendor payloads).
- Use `async def` for any I/O-bound path: database, HTTP, Cognee, LLM calls.

### Naming

- `snake_case` for functions and variables; `PascalCase` for classes; `UPPER_SNAKE` for constants.
- One public class/concern per module. Name modules after their role: `*_service.py`, `*_repo.py`,
  `*_collector.py`.

### Layering rules (clean architecture)

Dependencies point **inward**: controllers → services → repositories.

- **Controllers / routes** are thin: validate input via Pydantic, delegate to a service, return a
  schema. **No business logic in routers.**
- **Services** hold business logic and orchestration. Services never import routers.
- **Repositories** own data access. Repositories never import services.

### Hard invariants

- **No SQL outside `repositories/`.** Services and controllers call repositories, never the DB
  directly. See [database.md](./database.md).
- **Cognee single seam.** The Cognee SDK is imported in **exactly one module**:
  `backend/src/memory/cognee_client.py`. Everything memory-related funnels through
  `memory_service.py`, which wraps that client. This keeps Cognee mockable and swappable. See
  [memory-architecture.md](./memory-architecture.md) and [CLAUDE.md §14](../CLAUDE.md).
- **Never reimplement** retrieval, embedding, reranking, or summarization — Cognee owns those.
- **Never cross-query datasets** — memory is always scoped to `company_{ticker}`.
- **Idempotency**: every collector task is safe to retry; dedup by content hash **before**
  `cognee.add()`.
- **Prompt-injection guard**: retrieved web/news content is **data, not instructions**. See
  [prompting.md](./prompting.md).

### Docstrings

Public functions/classes get docstrings explaining **why**, not what. Document every new env var in
[`.env.example`](../.env.example) + [environment.md](./environment.md), and every new endpoint in
OpenAPI + [api.md](./api.md).

## TypeScript (frontend)

### Tooling

| Tool | Role |
|---|---|
| **prettier** | formatter |
| **eslint** | linter |
| **tsc** | type checker, `strict: true` in `tsconfig.json` |

`make fmt` runs prettier `--write`; `make lint` runs `pnpm lint` + `prettier --check`;
`make typecheck` runs `tsc --noEmit`.

### Typing

- `strict: true` — no implicit `any`, strict null checks.
- API contract types are **generated from the backend OpenAPI spec** (see [api.md](./api.md)) and
  live in `src/types/`. Hand-written types supplement, never duplicate, generated ones.

### Naming

- `PascalCase` for components and types; `camelCase` for functions and variables; `useX` for hooks.

### Layering rules

- **API access only through `services/api/*` modules.** Never call `fetch`/`axios` inline in a
  component or hook body. The axios client (`services/api/client.ts`) owns auth headers, base URL,
  and retry-on-401-refresh.
- **State management** ([frontend.md](./frontend.md) §state):
  - Server state → **TanStack Query** hooks (`useWatchlist`, `useCompanyPrice`).
  - Global UI state → **Zustand** (selected ticker, date range, theme).
  - Local component state → `useState`.
- **Co-locate** each component with its styles and its test.

## Commits, tests, and CI

- [Conventional Commits](https://www.conventionalcommits.org/); see
  [development-workflow.md](./development-workflow.md).
- New code ships with tests; bug fixes ship with a regression test. Target ≥80% coverage on
  `services/` and `collectors/`. See [tests/README.md](../tests/README.md).
- CI must be green (lint + type + test) before review.
