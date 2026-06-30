# Runbook: Ingestion failure for a ticker

A collector job (`price` or `news`) is repeatedly failing for one or more tickers.

> Template runbook (scaffold phase). Replace `<…>` placeholders with real dashboard URLs, alert
> names, and contacts once observability is wired up.

## Severity

- **SEV-3** — one ticker failing, others healthy (isolation holding).
- **SEV-2** — many tickers failing or a vendor-wide outage; data is going stale platform-wide.
- **SEV-1** — failures are blocking *other* tickers' ingestion (isolation broken — itself a bug).

## Symptoms

- `GET /admin/jobs` shows `status: "failed"` / `error` for a ticker (see [api.md](../api.md)).
- Admin "Ingestion Health" screen shows red badges / stale `last_run`.
- Alert: `<ingestion_failure_rate>` above threshold.
- DLQ depth increasing (tasks exhausted retries).

## Dashboards / signals

- Ingestion health: `GET /admin/jobs` and the `/admin` screen.
- Worker logs (Celery `price` / `news` queues): `<logs_url>` (filter by `ticker`).
- Queue + DLQ depth: `<queue_dashboard_url>`.
- Vendor status pages: market-data / news / search providers.

## Diagnosis

1. **Scope it.** One ticker or many? Many → suspect a vendor outage or a credential/quota problem.
   One → suspect bad ticker, a single bad payload, or a per-ticker config issue.
2. **Read the error** from `INGESTION_JOBS.error` (see [database.md](../database.md)) / worker logs.
   Common classes:
   - **Vendor auth/quota** — 401/403/429 from a vendor. Check `MARKET_DATA_API_KEY` /
     `NEWS_API_KEY` / `WEB_SEARCH_API_KEY` and rate limits (see [environment.md](../environment.md)).
   - **Bad ticker** — vendor 404 / empty payload for an invalid or delisted symbol.
   - **Normalizer error** — a malformed payload broke `normalizer.py`.
   - **Downstream** — failure at `memory_service` → Cognee `add()` (if so, also check the
     [cognify-backlog runbook](./cognify-backlog.md)).
3. **Confirm isolation** — verify other tickers' jobs are still succeeding. If not, escalate as SEV-1.

## Mitigation

- **Transient / vendor blip**: re-drive failed tasks from the **DLQ** once the vendor recovers; they
  are idempotent (dedup before `add()`), so retries are safe.
- **Quota / rate limit (429)**: back off the schedule (`NEWS_COLLECT_INTERVAL_HOURS`,
  `PRICE_COLLECT_CRON`) or raise the vendor plan; confirm per-vendor rate limits in collectors.
- **Bad credentials**: rotate the key in the secrets manager and restart workers (see
  [deployment.md](../deployment.md)). Never commit keys.
- **Bad ticker**: mark/quarantine the ticker so it stops scheduling; notify the requester.
- **Bad payload / normalizer bug**: capture the offending payload, drop that one task, file a bug;
  patch `normalizer.py` with a regression test.

```bash
# manual re-drive for one ticker (ops shell)
python scripts/backfill_ticker.py --ticker <TICKER>   # see scripts/README.md
```

## Verify recovery

- `GET /admin/jobs` shows `success` and a fresh `last_run` for the ticker.
- DLQ depth returns to baseline.
- A scoped query (`POST /companies/{ticker}/query`) returns recent, cited results.

## Escalation

1. On-call → 2. Backend owner (normalizer / collector / memory seam) → 3. Platform/infra (secrets,
network) → 4. Vendor support (upstream outage). See the [runbooks index](./README.md).
