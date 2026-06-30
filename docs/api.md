# API Reference

REST/JSON, resource-oriented, versioned under `/api/v1`. This document reproduces the API summary
from [ARCHITECTURE.md §7](../ARCHITECTURE.md) and gives request/response examples for the main
endpoints.

> **The live OpenAPI spec at `http://localhost:8000/docs` (and `/openapi.json`) is the source of
> truth.** Frontend TypeScript types are generated from it. This page is a hand-maintained
> companion — when they disagree, OpenAPI wins.

## Conventions

- **Base path**: `/api/v1`.
- **Auth**: `Authorization: Bearer <access_token>` (JWT RS256). See [authentication.md](./authentication.md).
- **Internal endpoints** (`/memory/*`): network-isolated and additionally require a service token.
- **Error envelope** (consistent across all endpoints):

  ```json
  { "error": { "code": "string", "message": "string", "detail": "string | object | null" } }
  ```

## Endpoint summary

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/auth/login` | POST | none | issue JWT |
| `/auth/refresh` | POST | refresh token | rotate JWT |
| `/companies` | GET / POST | user | list / add watchlist tickers |
| `/companies/{ticker}` | DELETE | user | remove from watchlist |
| `/companies/{ticker}/price` | GET | user | price series |
| `/companies/{ticker}/query` | POST | user | natural-language Q&A (wraps `/memory/search`) |
| `/memory/store` | POST | internal | collector → Cognee ingestion |
| `/memory/search` | POST | internal | Cognee retrieval |
| `/memory/context` | POST | internal | pre-LLM context assembly |
| `/memory/reflection` | POST | admin | trigger consolidation |
| `/memory/delete` | DELETE | admin | purge memory |
| `/admin/jobs` | GET | admin | ingestion health |

---

## Auth

### `POST /auth/login`

Auth: none. Issues an access + refresh token pair.

```json
// Request
{ "email": "user@example.com", "password": "..." }
// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### `POST /auth/refresh`

Auth: a valid (un-revoked) refresh token. Rotates the refresh token and issues a new access token.

```json
// Request
{ "refresh_token": "eyJ..." }
// Response 200
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer", "expires_in": 900 }
```

See [authentication.md](./authentication.md) for rotation and revocation.

---

## Companies

### `GET /companies`

Auth: user. Lists the caller's watchlist.

```json
// Response 200
{ "companies": [ { "id": "uuid", "ticker": "AAPL", "name": "Apple Inc.", "status": "active" } ] }
```

### `POST /companies`

Auth: user. Adds a ticker to the watchlist → triggers collector registration + initial backfill.

```json
// Request
{ "ticker": "AAPL" }
// Response 201
{ "id": "uuid", "ticker": "AAPL", "status": "backfilling" }
```

Validation: ticker format whitelist; unique per user.

### `DELETE /companies/{ticker}`

Auth: user. Removes the watchlist entry. **Does not** purge Cognee memory — that is a separate
admin action (`DELETE /memory/delete`). See [memory-architecture.md](./memory-architecture.md) §lifecycle.

```json
// Response 204 (no content)
```

### `GET /companies/{ticker}/price?range=30d`

Auth: user. Returns OHLCV price bars.

```json
// Response 200
{
  "ticker": "AAPL",
  "bars": [
    { "t": "2026-06-01", "o": 1, "h": 2, "l": 0.9, "c": 1.5, "v": 12345 }
  ]
}
```

### `POST /companies/{ticker}/query`

Auth: user. Natural-language question scoped to the company. Internally calls
`cognee.search()` / `recall(dataset_name=f"company_{ticker}", query=question, filters=date_range)`,
then formats a cited answer via the LLM (see [prompting.md](./prompting.md)).

```json
// Request
{
  "question": "Why did the stock drop on March 3?",
  "date_range": { "from": "2026-02-25", "to": "2026-03-05" }
}
// Response 200
{
  "answer": "The stock fell ~8% on March 3 after [1] reported a supply-chain warning ...",
  "citations": [
    { "title": "Apple warns on supply chain", "url": "https://...", "published_at": "2026-03-03T10:00:00Z" }
  ],
  "graph_snippet": { "nodes": [], "edges": [] }
}
```

Rate-limited per user (`QUERY_RATE_LIMIT_PER_MINUTE`) for LLM cost control.

---

## Memory (internal)

These endpoints are the backend wrapper surface over Cognee. They are **internal-only**:
network-isolated and require a service token in addition to (where noted) an admin role. They are
documented here for completeness; application code reaches them through `memory_service.py`, never
the frontend. See [memory-architecture.md](./memory-architecture.md) and
[ARCHITECTURE.md §5.7](../ARCHITECTURE.md).

| Endpoint | Maps to |
|---|---|
| `POST /memory/store` | `cognee.add(content, dataset_name=f"company_{ticker}")` then `cognee.cognify()` |
| `POST /memory/search` | `cognee.search()` / `recall(dataset_name=…, query=…, filters=…)` |
| `POST /memory/context` | returns the assembled context block (chunks + graph snippet) for prompt injection |
| `POST /memory/reflection` | triggers a consolidation / cognify pass (admin) |
| `DELETE /memory/delete` | removes a dataset or a date-bounded slice (admin) |

```json
// POST /memory/search — Request
{ "ticker": "AAPL", "query": "supply chain", "filters": { "from": "2026-02-25", "to": "2026-03-05" }, "top_k": 8 }
// Response 200
{ "results": [ { "text": "...", "score": 0.82, "source_url": "https://...", "published_at": "..." } ] }
```

---

## Admin

### `GET /admin/jobs`

Auth: admin. Ingestion health per company.

```json
// Response 200
{
  "jobs": [
    { "ticker": "AAPL", "type": "news", "last_run": "2026-06-30T08:00:00Z", "items_ingested": 12, "status": "success" }
  ]
}
```

See the [ingestion-failure runbook](./runbooks/ingestion-failure.md) for interpreting failures.
