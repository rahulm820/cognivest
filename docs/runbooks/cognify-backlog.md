# Runbook: Cognify backlog growing

The `cognify` queue depth is growing: items are ingested (`cognee.add()`) but
`cognee.cognify()` is falling behind, so new content is slow to become searchable.

> Template runbook (scaffold phase). Replace `<…>` placeholders with real dashboards/contacts.

## Why this queue exists

`cognify()` is **decoupled onto its own queue** so a slow cognify never blocks fetching (see
[backend.md](../backend.md) and [memory-architecture.md](../memory-architecture.md)). A growing
backlog means cognify throughput < ingestion rate — fetches still succeed, but the graph/vector
stores lag, so recent items won't appear in `search()` until they're cognified.

## Severity

- **SEV-3** — backlog growing slowly, freshness lag minutes.
- **SEV-2** — large/accelerating backlog, freshness lag hours, queries visibly missing recent news.

## Symptoms

- `cognify` queue depth trending up: `<queue_dashboard_url>`.
- "Time to searchable" (add → available in `search()`) rising.
- Users report recent articles missing from answers for a ticker.

## Dashboards / signals

- Queue depth + age of oldest task for `cognify`.
- `cognify` worker throughput + error rate: `<logs_url>`.
- Cognee store health (vector + graph backend latency/CPU): `<cognee_store_dashboard>`.
- LLM/embedding provider latency (cognify uses the configured embedding model).

## Diagnosis

1. **Throughput vs arrival.** Is arrival spiking (e.g. a backfill — see
   [backfill](../../scripts/README.md)) or is throughput dropping?
2. **Worker capacity.** Are `cognify` workers healthy and at expected replica count? Are they
   crash-looping or OOMing? Check `<logs_url>`.
3. **Downstream slowness.** Is the **Cognee vector/graph backend** slow or saturated (CPU, disk,
   connection limits)? See [`cognee/config/README.md`](../../cognee/config/README.md).
4. **Embedding/LLM latency.** `cognify()` calls the embedding model; provider slowness throttles the
   whole queue.
5. **Poison task.** A single oversized/malformed item repeatedly failing and retrying can stall a
   worker — look for one task with many retries.

## Mitigation

- **Scale out `cognify` workers** (HPA / replica bump) — it is the independent lever here and won't
  affect `price`/`news` queues.
- **Throttle arrival** temporarily: pause/slow backfills (`scripts/backfill_ticker.py`), reduce
  `NEWS_COLLECT_INTERVAL_HOURS` frequency until caught up.
- **Backend slowness**: scale the Cognee vector/graph backend tier (managed service), or check its
  connection pool limits.
- **Provider latency**: confirm the embedding/LLM provider isn't degraded; back off if rate-limited.
- **Poison task**: isolate it to the DLQ so the rest of the queue drains; file a bug.

> Keep all mitigations within the single Cognee seam — never bypass `memory_service` /
> `cognee_client` to "manually" cognify. See [CLAUDE.md §14](../../CLAUDE.md).

## Verify recovery

- `cognify` queue depth and oldest-task age return to baseline.
- "Time to searchable" back within target.
- A scoped query surfaces the most recent articles for an affected ticker.

## Escalation

1. On-call → 2. Backend owner (worker scaling, memory seam) → 3. Platform/infra (Cognee backend
tier, provider quotas). See the [runbooks index](./README.md).
