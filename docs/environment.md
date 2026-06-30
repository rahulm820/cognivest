# Environment Variables

Every variable in [`.env.example`](../.env.example). Copy that file to `.env` (git-ignored) and fill
it in — see [setup.md](./setup.md). **Never commit `.env` or any secret** ([CLAUDE.md §14](../CLAUDE.md)).
When you add a new variable, update **both** `.env.example` and this table.

> "Required?" = required for the app to function in a real run. Many vendor keys are not needed for
> the Phase-0 scaffold but are required once the corresponding feature is implemented.

## App

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `APP_ENV` | Runtime environment | `development` | Yes |
| `APP_NAME` | Application name | `cognivest` | Yes |
| `LOG_LEVEL` | Log verbosity | `INFO` | Yes |
| `API_V1_PREFIX` | API base path | `/api/v1` | Yes |
| `BACKEND_CORS_ORIGINS` | Allowed frontend origins (CORS) | `http://localhost:3000` | Yes |

## Backend / FastAPI

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `BACKEND_HOST` | Bind host | `0.0.0.0` | Yes |
| `BACKEND_PORT` | Bind port | `8000` | Yes |

## Postgres

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `POSTGRES_HOST` | DB host (`postgres` in Docker, `localhost` native) | `postgres` | Yes |
| `POSTGRES_PORT` | DB port | `5432` | Yes |
| `POSTGRES_USER` | DB user | `cognivest` | Yes |
| `POSTGRES_PASSWORD` | DB password (change from default) | `change_me` | Yes |
| `POSTGRES_DB` | DB name | `cognivest` | Yes |
| `DATABASE_URL` | Async SQLAlchemy URL | `postgresql+asyncpg://cognivest:change_me@postgres:5432/cognivest` | Yes |

See [database.md](./database.md).

## Redis (cache + Celery broker/backend)

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `REDIS_URL` | Cache connection | `redis://redis:6379/0` | Yes |
| `CELERY_BROKER_URL` | Celery broker | `redis://redis:6379/1` | Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/2` | Yes |

## Auth / JWT (RS256)

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `JWT_ALGORITHM` | Signing algorithm | `RS256` | Yes |
| `JWT_PRIVATE_KEY_PATH` | RS256 private key path | `./secrets/jwt_private.pem` | Yes |
| `JWT_PUBLIC_KEY_PATH` | RS256 public key path | `./secrets/jwt_public.pem` | Yes |
| `JWT_ACCESS_TOKEN_TTL_MINUTES` | Access token lifetime | `15` | Yes |
| `JWT_REFRESH_TOKEN_TTL_DAYS` | Refresh token lifetime | `7` | Yes |
| `SERVICE_TOKEN` | Internal token for `/memory/*` calls | `change_me_internal_service_token` | Yes |

Generate the keypair with `scripts/generate_jwt_keys.sh`. See [authentication.md](./authentication.md).

## OAuth (Google)

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID | `…apps.googleusercontent.com` | If Google login enabled |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret | `…` | If Google login enabled |

## Cognee

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `COGNEE_VECTOR_DB_PROVIDER` | Vector backend | `lancedb` (`lancedb` \| `weaviate` \| `qdrant`) | Yes |
| `COGNEE_GRAPH_DB_PROVIDER` | Graph backend | `kuzu` (`kuzu` \| `neo4j`) | Yes |
| `COGNEE_DATA_DIR` | Cognee data directory | `/data/cognee` | Yes |
| `COGNEE_LLM_PROVIDER` | Cognee's LLM provider | `anthropic` | Yes |

See [`cognee/config/README.md`](../cognee/config/README.md) and [memory-architecture.md](./memory-architecture.md).

## LLM (Anthropic Claude)

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API key (answer generation) | `sk-ant-…` | Yes (query path) |
| `LLM_MODEL` | Model id | `claude-opus-4-8` | Yes |
| `LLM_MAX_TOKENS` | Max answer tokens | `2048` | Yes |

See [prompting.md](./prompting.md).

## External data vendors (all pluggable)

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `MARKET_DATA_PROVIDER` | Price vendor | `polygon` (`polygon` \| `iex` \| `alphavantage`) | Yes (price collection) |
| `MARKET_DATA_API_KEY` | Price vendor key | `…` | Yes (price collection) |
| `NEWS_API_PROVIDER` | News vendor | `newsapi` (`newsapi` \| `gdelt`) | Yes (news collection) |
| `NEWS_API_KEY` | News vendor key | `…` | Yes (news collection) |
| `WEB_SEARCH_PROVIDER` | Web search vendor | `tavily` (`tavily` \| `serper`) | Yes (web collection) |
| `WEB_SEARCH_API_KEY` | Web search vendor key | `…` | Yes (web collection) |

## Scheduling

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `PRICE_COLLECT_CRON` | Price collection schedule (cron) | `0 22 * * 1-5` (EOD weekdays) | Yes |
| `NEWS_COLLECT_INTERVAL_HOURS` | News collection interval (hours) | `2` | Yes |
| `INGEST_DEDUP_ENABLED` | Toggle dedup hash check | `true` | Yes |

## Rate limiting

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `QUERY_RATE_LIMIT_PER_MINUTE` | Per-user query rate cap (LLM cost control) | `20` | Yes |

## Frontend (Next.js)

| Name | Purpose | Example | Required? |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base URL (browser-exposed) | `http://localhost:8000/api/v1` | Yes |
