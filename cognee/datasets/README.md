# Cognee datasets

This directory documents the **dataset-naming convention** and **isolation guarantees**. It contains
**no actual dataset data** — that is git-ignored and lives in `COGNEE_DATA_DIR` / the configured
managed backends.

## Naming convention

**One Cognee dataset per ticker:**

```text
dataset_name = f"company_{ticker}"     # e.g. company_AAPL, company_TSLA
```

This is centralized in `backend/src/memory/dataset_naming.py` and used by the single Cognee seam,
`backend/src/memory/cognee_client.py`. Every `add()`, `cognify()`, and `search()` call passes a
`dataset_name` of this exact form.

## What goes in a dataset

Both data streams for a company land in the **same** dataset, so the knowledge graph can correlate
price movements with narrative events:

- **Price summaries** (text derived from OHLCV bars).
- **News / web articles** (normalized, deduped).

See [`../../docs/memory-architecture.md`](../../docs/memory-architecture.md).

## Isolation guarantees

- **Per-ticker scoping.** Each dataset is independent; one company's entities/edges never bleed into
  another's.
- **No cross-dataset queries.** `search()` / `recall()` is always scoped to a single
  `company_{ticker}`. Cross-querying is forbidden ([CLAUDE.md §14](../../CLAUDE.md)).
- **Security boundary.** Per-company isolation prevents cross-tenant graph leakage
  ([ARCHITECTURE.md §11](../../ARCHITECTURE.md)).

Isolation is asserted by contract tests in
[`../../tests/memory/test_dataset_isolation.py`](../../tests/memory/test_dataset_isolation.py).

## Data is git-ignored

- No articles, embeddings, graphs, or price data are committed here.
- Only [`.gitkeep`](./.gitkeep) keeps the directory in version control.
- Purging a dataset is an admin action: `scripts/purge_dataset.py` or `DELETE /memory/delete`
  (see [`../../docs/api.md`](../../docs/api.md)).
