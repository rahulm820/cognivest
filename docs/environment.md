# Environment Variables

Every variable in [`.env.example`](../.env.example). Copy that file to `.env` (git-ignored) and fill
it in — see [setup.md](./setup.md). **Never commit `.env` or any secret** ([CLAUDE.md §14](../CLAUDE.md)).
When you add a new variable, update **both** `.env.example` and this table.

> **To boot the stack you only need one real value: `LLM_API_KEY`** (a Gemini key). The compose
> template already targets the service hostnames, so Postgres/Redis need no edits. Vendor keys and the
> JWT/OAuth block are for features that are stubs today — see the "Status" notes.

> **Upgrading an older checkout?** Re-copy `cp .env.example .env`. Stale `.env` files carry a dead
> Anthropic/`claude-opus` LLM config that no longer works.

## App

| Name | Purpose | Example |
|---|---|---|
| `APP_ENV` | Runtime environment | `development` |
| `APP_NAME` | Application name | `cognivest` |
| `LOG_LEVEL` | Log verbosity | `INFO` |
| `API_V1_PREFIX` | API base path | `/api/v1` |
| `BACKEND_CORS_ORIGINS` | Allowed frontend origins (CORS) | `http://localhost:3000` |

## Backend / FastAPI

| Name | Purpose | Example |
|---|---|---|
| `BACKEND_HOST` | Bind host | `0.0.0.0` |
| `BACKEND_PORT` | Bind port | `8000` |

## Postgres

| Name | Purpose | Example |
|---|---|---|
| `POSTGRES_HOST` | DB host (`postgres` in Docker, `localhost` native) | `postgres` |
| `POSTGRES_PORT` | DB port | `5432` |
| `POSTGRES_USER` | DB user | `cognivest` |
| `POSTGRES_PASSWORD` | DB password (change from default) | `change_me` |
| `POSTGRES_DB` | DB name | `cognivest` |
| `DATABASE_URL` | Async SQLAlchemy URL | `postgresql+asyncpg://cognivest:change_me@postgres:5432/cognivest` |

See [database.md](./database.md).

## Redis (cache + Celery broker/backend)

| Name | Purpose | Example |
|---|---|---|
| `REDIS_URL` | Cache connection | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker | `redis://redis:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/2` |

## Cognee: LLM + embeddings

**This is the block that matters.** These are Cognee's own pydantic field names (not ours) — do not
rename or prefix them. A single provider (**Gemini**, via litellm) powers both `cognify()` extraction
and answer generation; embeddings run **locally** via fastembed (no API key, no cost). Verified in
[spike-cognee-1.2.2.md](./spike-cognee-1.2.2.md) §3.

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `LLM_PROVIDER` | Cognee LLM provider | `gemini` | Yes |
| `LLM_MODEL` | litellm-format model string | `gemini/gemini-2.5-flash` | Yes |
| `LLM_API_KEY` | Gemini / Google AI key | `AIza…` | **Yes** (query path) |
| `EMBEDDING_PROVIDER` | Embedding backend | `fastembed` | Yes |
| `EMBEDDING_MODEL` | Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Yes |
| `EMBEDDING_DIMENSIONS` | Vector width — **must** match the model | `384` | Yes (do not omit) |

> `gemini/gemini-2.0-flash` is deprecated by Google (free tier `limit: 0`) — use `2.5-flash`. Omitting
> `EMBEDDING_DIMENSIONS` silently falls back to 3072 and breaks the first vector write (spike §3).

### Alternative LLM: Groq (if you hit Gemini's free-tier limit)

Gemini's free tier is small (5 req/min, **20 req/day** on `2.5-flash`), and one `cognify` fires
several calls — enough to exhaust a day's quota during heavy testing. Groq's free tier is looser and
works as a drop-in for the LLM (embeddings stay on local fastembed — unchanged). **Verified working**
end-to-end (cognify + cited query). Cognee has no `groq` provider enum, so route it through the
OpenAI adapter + litellm's native `groq/` model prefix:

```bash
LLM_PROVIDER=openai                      # Cognee enum has no 'groq'; the openai adapter + litellm route it
LLM_MODEL=groq/llama-3.3-70b-versatile   # litellm sends this to Groq using LLM_API_KEY
LLM_API_KEY=gsk_…                        # a Groq key (https://console.groq.com)
```

This is a **local-dev override only** — the committed default stays Gemini. Setting `LLM_PROVIDER=groq`
directly fails with `ValueError: 'groq' is not a valid LLMProvider`.

## Cognee: vector / graph / data dir (unverified — left commented)

Present in `.env.example` but **commented out**. The spike did not confirm Cognee reads these
`COGNEE_`-prefixed names (the analogous `COGNEE_LLM_PROVIDER` is ignored — Cognee reads `LLM_PROVIDER`).
LanceDB + Kuzu are Cognee's defaults, so no wiring is needed today.

| Name (commented) | Intended purpose | Default |
|---|---|---|
| `COGNEE_VECTOR_DB_PROVIDER` | Vector backend | `lancedb` |
| `COGNEE_GRAPH_DB_PROVIDER` | Graph backend | `kuzu` |
| `COGNEE_DATA_DIR` | Cognee data directory | `/data/cognee` |

## Auth / JWT / OAuth (present but inert today)

These exist in `.env.example` for the roadmap JWT/OAuth design. **They are not enforced** — auth is a
demo `X-User-Id` header ([authentication.md](./authentication.md)). Safe to leave at defaults for the demo.

| Name | Purpose | Status |
|---|---|---|
| `JWT_ALGORITHM`, `JWT_PRIVATE_KEY_PATH`, `JWT_PUBLIC_KEY_PATH`, `JWT_ACCESS_TOKEN_TTL_MINUTES`, `JWT_REFRESH_TOKEN_TTL_DAYS` | RS256 JWT config | 🎯 not enforced |
| `SERVICE_TOKEN` | Internal token for `/memory/*` | 🎯 guard is a no-op |
| `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth | 🎯 not wired |

## External data vendors (pluggable — collectors are stubs)

Needed once the collector path is built; not required for the demo.

| Name | Purpose | Example |
|---|---|---|
| `MARKET_DATA_PROVIDER` / `MARKET_DATA_API_KEY` | Price vendor + key | `polygon` |
| `NEWS_API_PROVIDER` / `NEWS_API_KEY` | News vendor + key | `newsapi` |
| `WEB_SEARCH_PROVIDER` / `WEB_SEARCH_API_KEY` | Web search vendor + key | `tavily` |

## Scheduling (collectors are stubs)

| Name | Purpose | Example |
|---|---|---|
| `PRICE_COLLECT_CRON` | Price collection schedule (cron) | `0 22 * * 1-5` |
| `NEWS_COLLECT_INTERVAL_HOURS` | News collection interval (hours) | `2` |
| `INGEST_DEDUP_ENABLED` | Toggle dedup hash check | `true` |

## Rate limiting

| Name | Purpose | Example |
|---|---|---|
| `QUERY_RATE_LIMIT_PER_MINUTE` | Per-user query rate cap | `20` |

## Frontend (Next.js)

| Name | Purpose | Example |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base URL (browser-exposed) | `http://localhost:8000/api/v1` |
