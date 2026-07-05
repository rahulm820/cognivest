# Cognivest

> Per-company financial intelligence powered by [Cognee](https://www.cognee.ai/) — correlating **price action** with **news/web narrative** in a per-ticker knowledge graph.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)

---

## What is Cognivest

Cognivest ingests two data streams per publicly traded company — **structured price data** and
**unstructured web/news content** — into **Cognee**, which builds a per-company knowledge graph and
answers natural-language questions (*"Why did $AAPL drop on March 3?"*) with grounded answers. The
application layer is a **thin orchestration + presentation shell** around Cognee: dataset scoping,
citation formatting, and UI — Cognee owns the hard parts (entity extraction, embedding, graph build,
retrieval).

**It runs entirely on free tiers.** One Gemini API key (free tier) drives graph construction and
answer generation; embeddings are computed locally with [fastembed](https://github.com/qdrant/fastembed)
(no API key, no cost); the vector store (LanceDB) and graph store (Kuzu) are embedded libraries. **One
API key, zero infrastructure cost, fully reproducible** — verified end-to-end in
[docs/spike-cognee-1.2.2.md](./docs/spike-cognee-1.2.2.md).

---

## The Cognee memory lifecycle

Cognivest's whole story is a memory loop over one dataset per ticker (`company_{ticker}`). Every stage
maps to a real Cognee 1.2.2 call behind our single seam
([`backend/src/memory/cognee_client.py`](./backend/src/memory/cognee_client.py)):

| Stage | What it does | Real Cognee call | Status |
|---|---|---|---|
| 🧠 **Remember** | Ingest a price summary or article, then build/update the graph | `cognee.add(dataset_name=…)` → `cognee.cognify(datasets=[…])` | Wired in the seam |
| 🔎 **Recall** | Answer a scoped question from the graph | `cognee.search(query_text=…, datasets=[…])` / `cognee.recall(…)` | Wired in the seam + the live `/query` route |
| 📈 **Improve** | Fold answer feedback back into the graph's weights | `cognee.improve(…)` / `FeedbackEntry` | Cognee SDK supports it ([spike §2](./docs/spike-cognee-1.2.2.md)); **not yet wired in our seam** |
| 🗑️ **Forget** | Purge a ticker's whole dataset | `cognee.forget(dataset=…)` | Wired in the seam |

> **Why one dataset per ticker?** Price summaries and news for a company land in the **same** dataset,
> so the graph can correlate a price move with the same-day narrative that explains it. We never
> cross-query datasets. See [docs/memory-architecture.md](./docs/memory-architecture.md).

---

## Quick start

<!-- FINAL-VERIFY July 5 -->

Runs the full stack in Docker. You need **Docker + Docker Compose** and **one Gemini API key**
([Google AI Studio](https://aistudio.google.com/), free tier).

```bash
git clone https://github.com/your-org/cognivest.git
cd cognivest
cp .env.example .env
# Open .env and set ONE value:  LLM_API_KEY=<your Gemini key>
#   (LLM_PROVIDER=gemini and EMBEDDING_PROVIDER=fastembed are already set correctly)

make up        # build + start postgres, redis, backend, worker, beat, frontend
make migrate   # apply Alembic migrations
make seed      # seed demo companies (AAPL, MSFT, TSLA) + a demo user
```

Then:

- Frontend: http://localhost:3000
- Backend API + live OpenAPI docs: http://localhost:8000/docs

> **Upgrading an older checkout?** Re-copy the template — `cp .env.example .env` — before booting.
> Stale `.env` files from earlier revisions carry a dead LLM config (an Anthropic/`claude-opus`
> setup that no longer exists) and will not work.

Only `LLM_API_KEY` is required to boot. Vendor keys (market data, news, web search) are for
collectors that are still in progress — see **Limitations** below.

---

## Architecture at a glance

```text
Next.js 14 frontend
   → FastAPI backend (/api/v1)
      → MemoryService  (the only caller of the Cognee seam)
         → cognee_client.py  (the ONLY module that imports the Cognee SDK)
            → Cognee 1.2.2 → Gemini (LLM) + fastembed (embeddings) + LanceDB + Kuzu
   → PostgreSQL (operational data)   ·   Redis (Celery broker, for the collector roadmap)
```

- **Single Cognee seam.** `backend/src/memory/cognee_client.py` is the *only* module allowed to import
  the Cognee SDK; everything funnels through `memory_service.py`. This keeps Cognee mockable and its
  config swappable without touching callers.
- **Per-ticker isolation.** The dataset name is always `company_{ticker}`
  ([`dataset_naming.py`](./backend/src/memory/dataset_naming.py)).
- **Single-LLM answers.** The query path returns Cognee's `GRAPH_COMPLETION` output directly — there is
  no second answer-formatter LLM call.

See [docs/](./docs/README.md) for the full documentation set and [ARCHITECTURE.md](./ARCHITECTURE.md)
for the design vision (built-vs-planned is marked throughout).

---

## Limitations & hackathon scope

<!-- FINAL-VERIFY July 5 -->

This is a hackathon build. It is honest about what is real:

- **One live end-to-end route.** `POST /api/v1/companies/{ticker}/query` runs the real recall path and
  returns a grounded answer (or an honest "no data ingested yet" when the dataset is empty). Most other
  routes — watchlist CRUD, price series, `/admin/jobs`, `/auth/*`, `/memory/*` — are typed stubs that
  raise `NotImplementedError`.
- **Auth is a demo header, not authentication.** Identity is asserted with an `X-User-Id` header
  (default `demo-user`, role `admin`). The JWT/OAuth design is roadmap — see
  [docs/authentication.md](./docs/authentication.md).
- **The demo path is synchronous.** Celery `worker` and `beat` containers boot, but the collector and
  cognify tasks are stubs; nothing is scheduled yet. Ingestion through the API is not wired.
- **Collectors are WIP.** Price/news/web-search collectors are interface stubs; the demonstrable
  Cognee round-trip lives in [`scripts/cognee_roundtrip.py`](./scripts/cognee_roundtrip.py) (the spike),
  not yet in the app's ingestion path.
- **No infrastructure.** There is no Kubernetes, Terraform, or CI. Local Docker Compose is the only
  supported target; cloud deployment is on the roadmap ([docs/roadmap.md](./docs/roadmap.md)).

What's solid: the Cognee seam (correct 1.2.2 signatures, verified against the spike), per-ticker dataset
isolation, the clean controller → service → repository layering, and a reproducible free-tier stack.

---

## LLM & embedding configuration

Cognee reads its LLM and embedding settings from these environment variables (its own pydantic field
names — see [`.env.example`](./.env.example)). **A single provider (Gemini) powers both graph
construction and answer generation.**

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | LLM provider Cognee uses for `cognify()` extraction + answer generation — `gemini`. |
| `LLM_MODEL` | litellm-format model string — `gemini/gemini-2.5-flash`. |
| `LLM_API_KEY` | API key for the LLM provider (a Google AI / Gemini key). |
| `EMBEDDING_PROVIDER` | Embedding backend — `fastembed` (local ONNX, no API key, no cost). |
| `EMBEDDING_MODEL` | Embedding model — `sentence-transformers/all-MiniLM-L6-v2`. |
| `EMBEDDING_DIMENSIONS` | Vector width; **must** match the model — `384`. Do not omit. |

**Manual fallback if the Gemini key is quota-exhausted.** Swap `LLM_API_KEY` for a second key from a
**different Google Cloud project** (quotas are per-project, so a key in the same project shares the
exhausted quota) and restart. To fall back to a **different provider** (e.g. Groq), swap
`LLM_PROVIDER`, `LLM_MODEL`, and `LLM_API_KEY` together. Embeddings stay local via fastembed, so your
existing vectors are unaffected by any LLM swap — no re-cognify needed. (Changing `EMBEDDING_*`, by
contrast, requires a prune + re-cognify.)

---

## Contributing

Read [CONTRIBUTING.md](./CONTRIBUTING.md) and the [Code of Conduct](./CODE_OF_CONDUCT.md) before opening
a PR. Security issues: see [SECURITY.md](./SECURITY.md).

## License

[MIT](./LICENSE) © Cognivest contributors.
