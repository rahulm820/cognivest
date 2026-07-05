# API Reference

REST/JSON, versioned under `/api/v1`. The **live OpenAPI spec at `http://localhost:8000/docs`
(and `/openapi.json`) is the source of truth** — this page is a hand-maintained companion.

## What's actually live

Most routes are typed stubs that raise `NotImplementedError` (FastAPI returns a `500`). Only two paths
are wired end-to-end today:

| Endpoint | Method | Status |
|---|---|---|
| `/health`, `/api/v1/health` | GET | ✅ **live** |
| `/companies/{ticker}/query` | POST | ✅ **live** (single-LLM recall) |
| `/auth/login`, `/auth/refresh` | POST | 🎯 stub |
| `/companies` (list/add) | GET / POST | 🎯 stub |
| `/companies/{ticker}` (remove) | DELETE | 🎯 stub |
| `/companies/{ticker}/price` | GET | 🎯 stub |
| `/memory/store` · `/memory/search` · `/memory/context` · `/memory/reflection` · `/memory/delete` | POST/DELETE | 🎯 stub |
| `/admin/jobs` | GET | 🎯 stub |

## Conventions

- **Base path:** `/api/v1`.
- **Auth:** a demo **`X-User-Id`** header (default `demo-user`, role `admin`) — **not** JWT. No tokens
  are verified. See [authentication.md](./authentication.md).
- **Error envelope** (🎯 target contract; stub routes currently surface a plain `500`):

  ```json
  { "error": { "code": "string", "message": "string", "detail": "string | object | null" } }
  ```

---

## Health ✅

### `GET /health` (and `GET /api/v1/health`)

```json
// Response 200
{ "status": "ok", "service": "cognivest", "version": "…", "env": "development" }
```

---

## Query ✅ — the live path

### `POST /companies/{ticker}/query`

Header: `X-User-Id: <id>` (optional; defaults to `demo-user`). Natural-language question scoped to the
company. Internally: `MemoryService.answer` →
`cognee.search(query_text=question, query_type=GRAPH_COMPLETION, datasets=[f"company_{ticker}"])`.
This is **single-LLM** (Cognee's `GRAPH_COMPLETION` on Gemini) — there is no separate answer-formatter.

```json
// Request
{
  "question": "Why did the stock drop on March 3?",
  "date_range": { "from": "2026-02-25", "to": "2026-03-05" }
}
```

`date_range` is accepted and forwarded as intent, but cognee 1.2.2's `search()` has **no** native date
filter (spike CONTRADICTION #1), so it does not slice results today.

```json
// Response 200 — with ingested data
{
  "answer": "The stock fell ~8% on March 3 after the company cut guidance …",
  "citations": [],
  "graph_snippet": { "nodes": [], "edges": [] }
}
```

```json
// Response 200 — empty dataset (honest, not fabricated)
{
  "answer": "No data has been ingested yet for AAPL, so there is nothing to answer from. …",
  "citations": [],
  "graph_snippet": { "nodes": [], "edges": [] }
}
```

Citations are derived **only** from real retrieval metadata; when none is available the list is empty
rather than fabricated. Rate-limited per user (`QUERY_RATE_LIMIT_PER_MINUTE`).

---

## Stubbed routes (🎯 designed, not implemented)

The endpoints below validate their schemas but raise `NotImplementedError`. Their intended shapes:

### Auth — `POST /auth/login`, `POST /auth/refresh`
Target: issue / rotate an RS256 JWT pair. Not enforced today (demo header auth).

### Companies — `GET /companies`, `POST /companies`, `DELETE /companies/{ticker}`, `GET /companies/{ticker}/price`
Target: watchlist CRUD + OHLCV price series backed by Postgres + a market-data vendor.

### Memory (internal) — `/memory/*`
The intended backend wrapper over the Cognee seam. **Routes are stubs; the seam methods they will call
are implemented** ([memory-architecture.md](./memory-architecture.md)):

| Endpoint | Maps to |
|---|---|
| `POST /memory/store` | `cognee.add(dataset_name=…)` then `cognee.cognify(datasets=[…])` |
| `POST /memory/search` | `cognee.search(query_text=…, query_type=GRAPH_COMPLETION, datasets=[…])` |
| `POST /memory/context` | assembled context block for the query path |
| `POST /memory/reflection` | a consolidation / cognify pass |
| `DELETE /memory/delete` | `cognee.forget(dataset="company_{ticker}")` |

Note: `search` in 1.2.2 takes `datasets=` (plural) and has **no** `dataset_name=`/`filters=` params.
The `/memory/*` service-token guard is a no-op in the demo ([authentication.md](./authentication.md)).

### Admin — `GET /admin/jobs`
Target: ingestion health per company, backed by the `INGESTION_JOBS` table.
