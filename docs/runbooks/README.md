# Runbooks

On-call operational runbooks for Cognivest. Each follows a template: **symptoms → dashboards /
signals → diagnosis → mitigation → escalation**. They assume the production topology in
[deployment.md](../deployment.md).

## Index

| Runbook | When to use |
|---|---|
| [Ingestion failure](./ingestion-failure.md) | A collector job is failing for one or more tickers (`GET /admin/jobs` shows `error`/`failed`). |
| [Cognify backlog](./cognify-backlog.md) | The `cognify` queue depth is growing; new memory is slow to become searchable. |
| [High query latency](./high-query-latency.md) | Query p95 exceeds the 3s SLO. |

## Conventions

- **SLOs**: query responses target **< 3s p95** for typical scoped queries
  ([ARCHITECTURE.md §1.7](../../ARCHITECTURE.md)).
- **Isolation**: one ticker's collector failure must **not** block others. If it does, that itself is
  an incident.
- **Queues**: `price`, `news`, `cognify` are independent (Celery + Redis). A backlog in one must not
  starve the others (see [backend.md](../backend.md)).
- **Datasets**: memory is per-ticker (`company_{ticker}`). Mitigations that touch memory must stay
  scoped to the affected ticker — never cross datasets.
- **Secrets**: never paste secrets/keys into tickets or logs.

## Escalation ladder (generic)

1. **On-call engineer** — triage with the runbook.
2. **Backend owner** — for service/queue/Cognee-config issues.
3. **Platform / infra** — for managed-service (RDS/ElastiCache/Cognee store) or cluster issues.
4. **Vendor support** — for upstream data-vendor or Anthropic API outages.

> These runbooks are templates for the scaffold phase. Fill in real dashboard URLs, alert names, and
> escalation contacts when observability is wired up (roadmap phases 6–7, see [roadmap.md](../roadmap.md)).
