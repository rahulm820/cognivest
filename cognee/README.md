# `cognee/` — Cognee configuration & conventions

This directory holds **Cognee backend configuration and dataset-naming conventions only**.

> **No raw data is ever committed here.** Cognee's actual vector/graph data lives in
> `COGNEE_DATA_DIR` (and the configured managed backends), which is git-ignored.

## What is — and isn't — here

| Here | Not here |
|---|---|
| Vector + graph backend configuration (env-driven) | The Cognee **SDK usage** — that lives in the backend |
| The `company_{ticker}` dataset-naming convention | Any ingested articles, price data, embeddings, or graphs |
| Example config files (placeholder values) | Any secrets / API keys |

## The SDK lives in the backend

The Cognee SDK is imported in **exactly one place** in the whole repository:

```text
backend/src/memory/cognee_client.py   ← the ONLY Cognee importer
```

All memory operations funnel through `backend/src/memory/memory_service.py`, which wraps that
client. This is the **single-seam rule** — see
[`../docs/memory-architecture.md`](../docs/memory-architecture.md) and
[CLAUDE.md §14](../CLAUDE.md). This `cognee/` directory only configures the backends that client
talks to.

## Contents

| Path | Purpose |
|---|---|
| [`config/`](./config/README.md) | How Cognee's vector + graph backends are configured (env-driven, pluggable). |
| [`config/cognee.config.example.yaml`](./config/cognee.config.example.yaml) | Example config with placeholder values. |
| [`datasets/`](./datasets/README.md) | The `company_{ticker}` naming convention + isolation guarantees (data git-ignored). |

## Key conventions

- **One dataset per ticker**: `company_{ticker}` (e.g. `company_AAPL`). Centralized in
  `backend/src/memory/dataset_naming.py`.
- **Price + news share the dataset** so the graph can correlate them.
- **Never cross-query** datasets — memory is strictly per-ticker.

See [`../docs/memory-architecture.md`](../docs/memory-architecture.md) for the full design.
