# config/

Shared, **static** configuration consumed at runtime by the backend and workers.
These are non-secret, version-controlled defaults — secrets always come from env /
the secrets manager (CLAUDE.md §14, ARCHITECTURE.md §11).

| File | Consumed by | Purpose |
|---|---|---|
| `logging.yaml` | backend + workers | Structured (JSON) logging config — `structlog`/stdlib `logging.config.dictConfig`. |
| `ratelimits.yaml` | collectors + API middleware | Per-vendor (downstream quota) and per-user (LLM cost) rate limits. |
| `scheduling.example.yaml` | Celery beat | Per-ticker price/news collection cron defaults. Copy to `scheduling.yaml` (or load from DB). |

## Conventions

- **No secrets here.** API keys/passwords are env-only.
- Values mirror the defaults in `.env.example`; env vars override file values where both exist.
- `scheduling.example.yaml` is an example — real per-company schedules live in Postgres
  (overridable per company) and seed from these defaults.

## Loading (intended wiring — backend stubs)

```python
# backend/src/core/config.py (TODO)
import logging.config, yaml
with open("config/logging.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))
```

> Phase 0 scaffold: these files define the *shape*; the backend loaders are stubs.
