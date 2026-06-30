# Cognee backend configuration

Cognee's intelligence runs on two pluggable storage backends — a **vector store** and a **graph
store** — plus an **embedding model** and an **LLM provider**. All of these are **configuration, not
our code**: the app abstracts them away behind the single Cognee seam
(`backend/src/memory/cognee_client.py`). See
[`../../docs/memory-architecture.md`](../../docs/memory-architecture.md).

## Env-driven configuration

Configuration is driven by environment variables (documented in
[`../../docs/environment.md`](../../docs/environment.md)); [`cognee.config.example.yaml`](./cognee.config.example.yaml)
shows the shape with placeholder values.

| Variable | Purpose | Options (pluggable) |
|---|---|---|
| `COGNEE_VECTOR_DB_PROVIDER` | Vector store backend | `lancedb` \| `weaviate` \| `qdrant` |
| `COGNEE_GRAPH_DB_PROVIDER` | Graph store backend | `kuzu` \| `neo4j` |
| `COGNEE_DATA_DIR` | On-disk data directory (git-ignored) | e.g. `/data/cognee` |
| `COGNEE_LLM_PROVIDER` | LLM provider used by Cognee | `anthropic` |

The embedding model and LLM credentials come from the LLM section of the environment
(`ANTHROPIC_API_KEY`, `LLM_MODEL`).

## Vector store

Holds embeddings of every ingested chunk (price-summary text + article text), namespaced per
dataset (`company_{ticker}`).

- **LanceDB** — embedded, file-based; good default for local/dev and small deployments.
- **Weaviate / Qdrant** — managed/standalone services for larger, production deployments.

Switching providers is a config change only — no application code changes (single-seam rule).

## Graph store

Holds entities (`Company`, `Person`, `Product`, `Event`, `PriceMove`) and relationships
(`MENTIONS`, `CAUSED_BY`, `COMPETES_WITH`, `REPORTED_BY`), namespaced per dataset.

- **Kuzu** — embedded graph DB; good default for local/dev.
- **Neo4j** — managed/standalone for production graph workloads.

## Production notes

- In production the backends are provisioned by Terraform and reachable only from the backend's
  private network (see [`../../docs/deployment.md`](../../docs/deployment.md)).
- Credentials come from the secrets manager — **never committed**.
- Backend latency/saturation is a key signal in the
  [cognify-backlog](../../docs/runbooks/cognify-backlog.md) and
  [high-query-latency](../../docs/runbooks/high-query-latency.md) runbooks.
