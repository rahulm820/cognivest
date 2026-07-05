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

**Stack:** [Cognee 1.2.2](https://www.cognee.ai/) (OSS, self-hosted) · Gemini free tier (LLM) · local
fastembed embeddings · LanceDB (vector) · Kuzu (graph) · FastAPI · Next.js 14. No managed services, no
paid vector DB, no cloud bill — the whole thing boots from `docker compose`.

---

## The Cognee memory lifecycle

Cognivest's whole story is a memory loop over one dataset per ticker (`company_{ticker}`). Every stage
is **live** behind our single seam
([`backend/src/memory/cognee_client.py`](./backend/src/memory/cognee_client.py)):

| Stage | What it does | How it's built | Status |
|---|---|---|---|
| 🧠 **Remember** | Ingest a price summary or article, then build/update the graph | `cognee.add(dataset_name=…)` → `cognee.cognify(datasets=[…])` | ✅ Live |
| 🔎 **Recall** | Answer a scoped question, with citations parsed from provenance | `cognee.search(query_text=…, datasets=[…], GRAPH_COMPLETION)` → provenance-header parsing → `Citation`s | ✅ Live (`POST /companies/{ticker}/query`) |
| 📈 **Improve** | Fold a user's feedback into *their* future answers | Feedback stored as a `USER FEEDBACK` note in `user_{id}`; the personalization read path folds it into that user's later queries | ✅ Live (`POST /memory/reflection`) |
| 🗑️ **Forget** | Purge a ticker's whole dataset and rebuild | `cognee.forget(dataset=…)` (whole-dataset; Cognee 1.2.2 has no sliced delete) | ✅ Live |

> **"Improve" is our design, not Cognee's `improve()`.** We deliberately do **not** call Cognee's native
> `improve()`/`FeedbackEntry` API. Instead, feedback (and explicit `remember: …` preferences) are stored
> as first-party **user memory** in a separate `user_{id}` dataset, then folded into that user's
> subsequent company queries as a `USER PROFILE` data block — so the same question can lead with what a
> returning user cares about, over the same real corpus. User memory only *steers emphasis*; it is never
> itself a citation. See
> [`memory_service.remember_feedback`](./backend/src/services/memory_service.py) and the
> session-memory demo in [docs/demo-questions.md](./docs/demo-questions.md).

> **Why one dataset per ticker?** Price summaries and news for a company land in the **same** dataset,
> so the graph can correlate a price move with the same-day narrative that explains it. We never
> cross-query datasets. See [docs/memory-architecture.md](./docs/memory-architecture.md).

---

## Quick start

Runs the full stack in Docker and loads the AAPL demo. You need **Docker + Docker Compose** and **one
Gemini API key** ([Google AI Studio](https://aistudio.google.com/), free — no credit card).

```bash
# 1. Clone and configure
git clone https://github.com/your-org/cognivest.git
cd cognivest
cp .env.example .env
# Open .env and set ONE value:  LLM_API_KEY=<your Gemini key>
#   (LLM_PROVIDER=gemini, LLM_MODEL=gemini/gemini-2.5-flash, and
#    EMBEDDING_PROVIDER=fastembed are already correct in the template)

# 2. Build + start the stack (postgres, redis, backend, worker, beat, frontend)
docker compose up -d --build

# 3. Apply DB migrations
docker compose exec backend alembic upgrade head

# 4. Seed demo companies (AAPL, MSFT, TSLA) + a demo user
docker compose exec backend python -m scripts.seed

# 5. Backfill AAPL price action (yfinance, keyless) into Cognee
docker compose exec backend python -m scripts.backfill_ticker --ticker AAPL

# 6. Ingest the curated AAPL news corpus (3 source-verified events) into Cognee
docker compose exec backend python -m scripts.ingest_demo_corpus --ticker AAPL

# 7. Open the app
open http://localhost:3000     # or just visit it in a browser
```

Then ask an AAPL question on the company page (e.g. *"How did Apple do in its fiscal Q2 2026?"*).
Backend API + live OpenAPI docs are at http://localhost:8000/docs.

> The same steps are available as `make` targets (`make up`, `make migrate`, `make seed`,
> `make backfill t=AAPL`) — they wrap the exact `docker compose exec` commands above. The
> `docker compose` form is the canonical, copy-pasteable path.

**Gotchas (honest):**

- **A query says "no data ingested yet"?** The graph is empty for that ticker — re-run step 6
  (`ingest_demo_corpus`), and step 5 for price. Cognee's `cognify` runs at the end of ingest and takes
  ~30–60s; give it a moment before asking.
- **`429` / `503` from Gemini?** The free tier is **~20 requests/day per model**. Swap `LLM_MODEL` in
  `.env` between `gemini/gemini-2.5-flash` and `gemini/gemini-2.5-flash-lite` (separate quotas), or drop
  in a fresh key from a **different** Google Cloud project, then `docker compose up -d` to restart. Your
  ingested vectors are unaffected — embeddings are local (fastembed), so no re-ingest is needed.
- **Upgrading an older checkout?** Re-copy the template (`cp .env.example .env`) before booting. Stale
  `.env` files from earlier revisions carry a dead LLM config (an Anthropic/`claude-opus` setup that no
  longer exists) and will not work.

Only `LLM_API_KEY` is required. Vendor keys (market data, news, web search) are optional — see
**Limitations** below.

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

This is a hackathon build. It is honest about what is real:

- **Gemini free-tier quota.** The demo runs on Gemini's free tier (~20 requests/day per model). A busy
  demo can exhaust it and get `429`/`503`; the Quick start's gotcha note covers the model/key swap.
- **Demo corpus is AAPL-only.** The curated news corpus is **3 source-verified real AAPL events**
  ([`data/demo_corpus.json`](./data/demo_corpus.json)). MSFT/TSLA are intentionally absent — no verified
  URLs were available, and an honest 1-ticker corpus beats a 3-ticker corpus with invented sources. Ask
  an MSFT/TSLA question and the system truthfully answers "no data ingested yet."
- **News uses a curated corpus, not live fetch.** The GDELT news collector is real
  ([`news_collector.py`](./backend/src/collectors/news_collector.py)), but GDELT's public API
  rate-limits (`429`), so the demo's news ground truth comes from the curated corpus via
  [`scripts/ingest_demo_corpus.py`](./scripts/ingest_demo_corpus.py). Price data is live and keyless
  (yfinance) via [`scripts/backfill_ticker.py`](./scripts/backfill_ticker.py).
- **The demo path is synchronous.** The Celery `worker`/`beat` containers boot, but the demo ingests via
  the backfill/corpus scripts inline — there is no scheduled background collection yet.
- **Auth is a demo header, not authentication.** Identity is asserted with an `X-User-Id` header
  (default `demo-user`, role `admin`). Real JWT/OAuth is designed but not enforced — see
  [docs/authentication.md](./docs/authentication.md).

Beyond the memory lifecycle, the live API surface is the query route
(`POST /api/v1/companies/{ticker}/query`) and the feedback route (`POST /api/v1/memory/reflection`).
Other routes — watchlist CRUD, price series, `/admin/jobs`, `/auth/*`, the remaining `/memory/*` — are
typed stubs that raise `NotImplementedError`.

What's solid: the full Remember → Recall → Improve → Forget loop, per-user session memory, per-ticker
dataset isolation, the clean controller → service → repository layering, and a reproducible free-tier
stack.

### Roadmap / not built

Honest scope for what comes next — not a wishlist:

- **Multi-ticker corpus** — extend the verified news corpus beyond AAPL as more source-checked events land.
- **Live news ingestion** — a keyed news vendor behind the collector interface, replacing the curated corpus once rate limits are solved.
- **Real auth** — enforce the designed JWT/OAuth flow in place of the demo `X-User-Id` header.
- **Background scheduling** — move collection + `cognify` onto the Celery queues so ingestion runs on a schedule instead of via scripts.

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

## Team & credits

Built by **Team TopK_Devs** — Mohit Jeswani, Rahul Madhawani, Yash Sainani, Sahil Ahuja — for the
**WeMakeDevs × Cognee "Hangover Part AI" hackathon**.

## Contributing

Read [CONTRIBUTING.md](./CONTRIBUTING.md) and the [Code of Conduct](./CODE_OF_CONDUCT.md) before opening
a PR. Security issues: see [SECURITY.md](./SECURITY.md).

## License

[MIT](./LICENSE) © Cognivest contributors.
