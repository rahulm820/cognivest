# Runbook: High query latency (p95 > 3s)

Query responses are exceeding the **< 3s p95** SLO
([ARCHITECTURE.md §1.7](../../ARCHITECTURE.md)). The query path is
`POST /companies/{ticker}/query` → cache check → `cognee.search()` → `answer_formatter` (LLM).

> Template runbook (scaffold phase). Replace `<…>` placeholders with real dashboards/contacts.

## The query path (where time goes)

```text
request → auth/rate-limit → cache lookup (Redis)
  └─(miss)→ cognee.search/recall (vector + graph + rerank)
          → answer_formatter → Claude (LLM) → cited answer → cache store
```

See [memory-architecture.md](../memory-architecture.md) §retrieval and [prompting.md](../prompting.md).

## Severity

- **SEV-3** — p95 mildly over 3s, no error spike.
- **SEV-2** — p95 well over SLO and/or timeouts/5xx rising; users impacted.

## Symptoms

- Alert: query `p95 > 3s` (`<latency_dashboard_url>`).
- Frontend "answer" spinner long / timeouts on the company page.
- Elevated 5xx or upstream-timeout errors on `/companies/{ticker}/query`.

## Dashboards / signals

- Endpoint latency histogram (p50/p95/p99) for `/companies/{ticker}/query`.
- **Stage breakdown**: cache hit rate, Cognee `search()` latency, LLM call latency.
- Redis cache health and hit rate.
- Cognee vector/graph backend latency: `<cognee_store_dashboard>`.
- Anthropic API latency/error rate; `<llm_provider_status>`.

## Diagnosis — isolate the slow stage

1. **Cache hit rate dropped?** Low hit rate → every query pays full cost. Check Redis health and
   whether a deploy changed the cache key. Caching is the cheapest win.
2. **Cognee `search()` slow?** Vector/graph backend saturated (CPU, disk, connections) or `top_k` too
   large. Check the store dashboard and recent config changes
   ([`cognee/config/README.md`](../../cognee/config/README.md)).
3. **LLM call slow?** Anthropic API latency up, or `LLM_MAX_TOKENS` too high, or oversized context.
   Check provider status and the answer-token budget (see [environment.md](../environment.md)).
4. **Big date ranges / huge context?** Very wide `date_range` filters pull more passages → larger
   prompt → slower LLM. See [api.md](../api.md).
5. **Resource contention?** API pods CPU-throttled, or a `cognify` backlog stealing backend
   resources (see [cognify-backlog runbook](./cognify-backlog.md)).

## Mitigation

- **Cache**: restore Redis health; warm/repair the cache; confirm identical-query caching is working.
- **Cognee backend**: scale the vector/graph tier; reduce default `top_k` if over-fetching.
- **LLM**: lower `LLM_MAX_TOKENS` / trim context size; if the provider is degraded, surface a
  graceful "try again" and back off.
- **API**: scale API pods (HPA); ensure `cognify` workers aren't co-located and starving the API.
- **Rate limiting**: confirm `QUERY_RATE_LIMIT_PER_MINUTE` is protecting against a query flood
  (also a cost control).

> Do not work around Cognee by adding a second retrieval path — keep the single seam
> ([CLAUDE.md §14](../../CLAUDE.md)). Tune via config and scaling.

## Verify recovery

- p95 back under 3s on `<latency_dashboard_url>`.
- Cache hit rate and per-stage latencies back to baseline.
- 5xx/timeout rate back to baseline.

## Escalation

1. On-call → 2. Backend owner (query path, caching, memory seam) → 3. Platform/infra (Cognee backend
tier, pod scaling) → 4. Anthropic support (LLM provider outage). See the [runbooks index](./README.md).
