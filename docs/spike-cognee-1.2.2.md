# Spike: Cognee 1.2.2 Verification (GitHub issue #2)

> **Status: COMPLETE — round-trip verified end-to-end.**
> Purpose: pin down what the installed Cognee 1.2.2 SDK *actually* exposes (signatures, config,
> deletion, feedback) before we build Phase 3/4 on assumptions. Every claim below is backed by
> either an **SDK `file:line`** (paths relative to
> `.venv/lib/python3.12/site-packages/cognee/`) or **verbatim run output** from
> [`spike/roundtrip.py`](../spike/roundtrip.py) (scratch dir, gitignored).
>
> Scope guardrails honored: nothing under `backend/src` was touched; the repo-root `.env` was **not**
> modified (that reconciliation is issue #3).

---

## 1. Environment

| Item | Value |
|---|---|
| cognee | **1.2.2** (`pip show cognee`) |
| Python | 3.12.3 (`.venv`) |
| Install time | base ~2m14s; `cognee[fastembed]` extra +23s |
| Resolver conflicts | **none** — `pip check` → "No broken requirements found" (both installs) |
| LLM provider (verified) | **Gemini** via litellm — `gemini/gemini-2.5-flash` |
| Embeddings (verified) | **fastembed** (local ONNX) — `sentence-transformers/all-MiniLM-L6-v2`, 384-dim |

Base install bundles the AI stack: `litellm 1.90.3`, `openai 2.44.0`, `instructor 1.15.1`,
`lancedb 0.34.0` (default vector store), `networkx 3.6.1`. **fastembed is NOT in the base install** —
it is an optional extra (see §4).

---

## 2. Verified public API signatures (with SDK file:line)

Top-level exports are wired in [`cognee/__init__.py`](../.venv/lib/python3.12/site-packages/cognee/__init__.py) —
note it exposes **both** the V1 (`add`/`cognify`/`search`) and V2 (`remember`/`recall`/`forget`/`improve`) APIs
(`__init__.py:21-68`).

### `add` — `api/v1/add/add.py:25`
```python
async def add(data, dataset_name: str = "main_dataset", user=None, node_set=None,
              vector_db_config=None, graph_db_config=None, dataset_id: Optional[UUID]=None,
              preferred_loaders=None, incremental_loading=True, data_per_batch=20,
              importance_weight=0.5, run_in_background=False,
              llm_config=None, embedding_config=None, **kwargs)
```
Dataset targeted by **`dataset_name`** (singular str). ✅ matches our assumption.

### `cognify` — `api/v1/cognify/cognify.py:43`
```python
async def cognify(datasets: Union[str, list[str], list[UUID]] = None, user=None,
                  graph_model=KnowledgeGraph, chunker=TextChunker, chunk_size=None,
                  config=None, vector_db_config=None, graph_db_config=None,
                  run_in_background=False, incremental_loading=True, custom_prompt=None,
                  temporal_cognify=False, llm_config=None, embedding_config=None, **kwargs)
```
Dataset targeted by **`datasets`** (str or list) — **not** `dataset_name`.

### `search` — `api/v1/search/search.py:31`
```python
async def search(query_text: str,
                 query_type: SearchType = SearchType.GRAPH_COMPLETION,
                 user=None, datasets=None, dataset_ids=None,
                 system_prompt_path="answer_simple_question.txt", system_prompt=None,
                 top_k=15, node_type=NodeSet, node_name=None, only_context=False,
                 session_id=None, include_references=False,
                 llm_config=None, embedding_config=None) -> List[SearchResult]
```
First positional = **`query_text`**; mode = **`query_type`**; dataset = **`datasets`** / **`dataset_ids`**.
**No `dataset_name` and no `filters` parameter.** (See CONTRADICTION #1.)

**`SearchResult` runtime shape** (from the round-trip, §5) — a list of dicts:
```python
[{'dataset_id': UUID(...), 'dataset_name': 'company_TEST',
  'dataset_tenant_id': None, 'search_result': ['<answer text>', ...]}]
```
The generated answer lives in `result[i]["search_result"]` (a `list[str]`).

### `SearchType` enum — `modules/search/types/SearchType.py:4` (21 modes)
`SUMMARIES, CHUNKS, RAG_COMPLETION, HYBRID_COMPLETION, TRIPLET_COMPLETION,`
`GRAPH_COMPLETION` (default)`, GRAPH_COMPLETION_DECOMPOSITION, GRAPH_SUMMARY_COMPLETION, CYPHER,`
`NATURAL_LANGUAGE, GRAPH_COMPLETION_COT, GRAPH_COMPLETION_CONTEXT_EXTENSION, FEELING_LUCKY,`
`TEMPORAL, CODING_RULES, CHUNKS_LEXICAL, AGENTIC_COMPLETION`.

### `recall` (V2) — **EXISTS** — `api/v1/recall/recall.py:361`
```python
async def recall(query_text: str, query_type: SearchType|None = None, *,
                 datasets=None, dataset_ids=None, top_k=15, auto_route=True,
                 scope=None, session_id=None, context_profile="qa", ...) -> list[RecallResponse]
```
Higher-level wrapper over search: `auto_route=True` picks a `SearchType` for you and it is
session-cache aware. **Confirms** the `search()/recall()` assumption in
[memory-architecture.md](./memory-architecture.md); the "recall() might not exist" hypothesis in the
issue is **false** — it exists.

### Deletion API
- **`cognee.delete(...)` — DEPRECATED (since 0.3.9).** `api/v1/delete/__init__.py:10-13`:
  `async def delete(data_id, dataset_id, mode="soft", user=None)` — just forwards to
  `datasets.delete_data`. Deprecation message: *"Use `datasets.delete_data` instead."*
- **`cognee.datasets.delete_data(...)` — preferred item-level.** `api/v1/datasets/datasets.py:143`:
  `async def delete_data(dataset_id: UUID, data_id: UUID, user=None, mode="soft", delete_dataset_if_empty=False)`.
  Code comment (line 147): `mode="hard"` is **dangerous**, don't use.
- **`cognee.forget(...)` — V2 unified deletion.** `api/v1/forget/forget.py:16`:
  `async def forget(*, data_id=None, dataset=None, dataset_id=None, everything=False, memory_only=False, user=None)`.
  Docstring: *"replaces the separate prune/delete/empty_dataset APIs with a single mental model."*
  Supports item / whole-dataset (`dataset="company_TICKER"`) / `everything=True`.
- **`cognee.prune`** — `api/v1/prune/prune.py:4`: `prune.prune_data()` and
  `prune.prune_system(graph=True, vector=True, metadata=False, cache=True)` (full dev reset).

### Feedback / enrichment — **EXISTS**
- **`memify`** — `modules/memify/memify.py:25`:
  `async def memify(extraction_tasks=None, enrichment_tasks=None, data=None, dataset="main_dataset", user=None, node_type=NodeSet, node_name=None, ..., run_in_background=False)`.
  Graph-enrichment pipeline; runs over the existing graph when `data` is None.
- **`improve`** — `api/v1/improve/improve.py:36`:
  `async def improve(dataset="main_dataset", *, run_in_background=False, node_name=None, session_ids=None, build_global_context_index=False, build_truth_subspace=False, **kwargs)`.
  Docstring stage 1: applies **feedback weights** from session entries onto the graph nodes/edges that
  produced those answers.
- **`FeedbackEntry`** exported at `__init__.py:69`; `search()`/`recall()` accept a `feedback_influence`
  parameter — so the answer→feedback→improve loop is real in 1.2.2.

---

## 3. LLM + embedding configuration (with SDK file:line)

Both configs are pydantic `BaseSettings`, so **field name = env var** (case-insensitive), with
`SettingsConfigDict(env_file=".env")`.

### LLM — `infrastructure/llm/config.py:15`
Defaults (lines 44-47): `llm_provider="openai"`, `llm_model="openai/gpt-5-mini"`, `llm_api_key=None`.
Env vars: **`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `LLM_ENDPOINT`, `LLM_API_VERSION`**.
Gemini is a first-class provider — enum `get_llm_client.py:88` (`GEMINI = "gemini"`), dispatched at
`get_llm_client.py:294` → `GeminiAdapter`, which passes the model string verbatim to
`litellm.acompletion(model=self.model, api_key=self.api_key, ...)`
(`generic_llm_api/adapter.py:125-134`). So the **model string is litellm-format**: `gemini/<model>`.

### Embeddings — `infrastructure/databases/vector/embeddings/config.py:62`
Defaults (lines 71-72): `embedding_provider="openai"`, `embedding_model="openai/text-embedding-3-large"`.
Env vars: **`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_ENDPOINT`,
`EMBEDDING_API_KEY`, `EMBEDDING_API_VERSION`**.

Provider dispatch — `get_embedding_engine.py:82-128`:
```
fastembed            -> FastembedEmbeddingEngine   (line 82; local ONNX, no API)
ollama               -> OllamaEmbeddingEngine       (line 92)
openai_compatible    -> OpenAICompatibleEmbeddingEngine (line 104)
<anything else>      -> LiteLLMEmbeddingEngine      (line 116; openai/gemini/mistral/... via litellm)
```
⚠️ `embedding_dimensions` auto-derives when unset (`config.py:86-102`) and **falls back to 3072**
with only a warning if it can't resolve — which silently breaks the first vector write on a 384-dim
model. **Always set `EMBEDDING_DIMENSIONS` explicitly.**

### fastembed is an optional extra
`FastembedEmbeddingEngine.py:8-14` hard-raises `ImportError("... pip install 'cognee[fastembed]'")`
if missing. Package METADATA: `Provides-Extra: fastembed` → `fastembed<=0.8.0` + `onnxruntime`.
Activation is pure config: `EMBEDDING_PROVIDER=fastembed`.

### Working env var set (verified)
```dotenv
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-2.5-flash        # NOT 2.0-flash — see CONTRADICTION #3
LLM_API_KEY=<gemini key>                  # kept in gitignored spike/spike.env; never committed
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS=384
```

### ⚠️ Env-loading gotcha (critical for how we wire this into the app — issue #3)
`cognee/__init__.py:11` runs `dotenv.load_dotenv(override=True)` **at import time**, which loads the
**repo-root `.env`** into `os.environ` and **overrides** anything already set. Consequence:
setting `os.environ` *before* `import cognee` does **not** win — the import clobbers it. The spike
isolates by loading `spike/spike.env` with `override=True` **after** `import cognee` and clearing the
`@lru_cache`d config singletons. The isolation was proven at runtime (see §5, "ISOLATION PROOF").
Also note: cognee runs a live **LLM connection test during `add()`**
(`setup_and_check_environment.py:54` → `test_llm_connection`); bypass with
`COGNEE_SKIP_CONNECTION_TEST=true`.

---

## 4. Round-trip: `spike/roundtrip.py`

`add` (2 short docs → dataset `company_TEST`) → `cognify` → `search` (default `GRAPH_COMPLETION`).
Question: *"Why did Acme Corp stock fall on March 3 2025?"* (answerable only from doc 1).

### Isolation proof (printed before any API spend)
```
ISOLATION PROOF (resolved cognee config)
  llm_provider       = gemini
  llm_model          = gemini/gemini-2.5-flash
  embedding_provider = fastembed
  embedding_model    = sentence-transformers/all-MiniLM-L6-v2
  embedding_dims     = 384
  -> isolation OK (gemini LLM + fastembed embeddings)
```

### Model probe (single-shot, no backoff)
```
[gemini/gemini-2.5-flash] -> OK: answered ''    # cleared on first attempt; no fallback needed
```

### Timings + result (verbatim)
```
[prune]     3.97s
[add]       7.72s   (2 docs)
[cognify]  64.30s   (first run: incl. fastembed ONNX model download ~27s + 30 alembic migrations)
[search]   10.03s
Graph projection completed: 24 nodes, 32 edges

SEARCH RESULTS (verbatim repr):
[{'dataset_id': UUID('12190eec-021e-5947-9faa-c7d4cf3c6cc1'),
  'dataset_name': 'company_TEST', 'dataset_tenant_id': None,
  'search_result': ['Acme Corp stock fell on March 3, 2025, after the company cut its '
                    'full-year revenue guidance, citing weak enterprise demand.']}]

WINNING MODEL (use as LLM_MODEL downstream): gemini/gemini-2.5-flash
```
The answer is **correct and grounded** in doc 1 → the full `add → cognify → search` path works on
Gemini + fastembed. Benign noise observed (non-fatal): onnxruntime GPU-discovery warning (CPU box),
HF "unauthenticated requests" warning, and an aiohttp "Unclosed client session" at exit.

**🏆 WINNING MODEL: `gemini/gemini-2.5-flash`** — this is the value that should become `LLM_MODEL`
everywhere downstream.

---

## 5. CONTRADICTIONS (flagged prominently)

1. **`search()` has no `dataset_name` and no `filters` param.** Both
   [CLAUDE.md §7](../CLAUDE.md) and [memory-architecture.md:19](./memory-architecture.md) document
   `cognee.search(query, dataset_name=dataset, filters=date_range)`. In 1.2.2 the real signature is
   `search(query_text, query_type=..., datasets=[...], dataset_ids=[...])`
   (`api/v1/search/search.py:31`). **Code written against `dataset_name=`/`filters=` on search will
   `TypeError`.** Date-range filtering is not a top-level arg — it must go through query semantics /
   `TEMPORAL` search / `retriever_specific_config`. `add()` *does* still use `dataset_name=`, so the
   two calls are asymmetric. **Affects the Phase-4 query pipeline most.**
2. **`cognee.delete()` is DEPRECATED** (since 0.3.9; `api/v1/delete/__init__.py:10`).
   [memory-architecture.md:158](./memory-architecture.md) references a generic "Cognee delete API".
   Use **`forget(dataset="company_TICKER")`** (whole-ticker purge) or `datasets.delete_data(...)`
   (item-level) instead.
3. **`gemini/gemini-2.0-flash` is unusable** — Google deprecated it (Mar 2026); its free tier is
   `limit: 0` for all projects (observed as a hard 429 `RESOURCE_EXHAUSTED` in the first run). Use
   **`gemini/gemini-2.5-flash`**.
4. **Import-time `load_dotenv(override=True)`** (`cognee/__init__.py:11`) means the repo-root `.env`
   overrides pre-set `os.environ`. Any wiring in `backend/src` must account for this (issue #3).
5. **Root `.env` sets `COGNEE_LLM_PROVIDER`, which cognee ignores** — `LLMConfig` reads `LLM_PROVIDER`
   (`infrastructure/llm/config.py:44`). The root file's provider intent is currently inert for cognee
   (flag for issue #3).

---

## 6. VERDICT — what we CAN build on vs what does NOT exist in 1.2.2

> ⚠️ The issue bodies for **#4/#9/#10/#11 were not accessible in this environment** (private repo, no
> `gh` CLI). The mapping below is by **feature area**; confirm the exact issue↔capability pairing
> against the tracker. The **capability verdicts themselves are fully evidence-backed** (§2–§5).

### ✅ CAN build on (verified to exist and, where marked, run end-to-end)

| Capability | Evidence | Likely issue |
|---|---|---|
| `add → cognify → search` round-trip on **Gemini + fastembed** | §4 run output (correct grounded answer) | #4 (Query/Answer, Phase 4) |
| Per-ticker dataset scoping via `datasets=["company_TICKER"]` | `search.py:31`, `cognify.py:43`; run used `company_TEST` | #4 |
| `SearchType.GRAPH_COMPLETION` (+ 20 other modes incl. `TEMPORAL`, `RAG_COMPLETION`, `CYPHER`) | `SearchType.py:4` | #4 |
| Answer text extraction from `result["search_result"]` (`list[str]`) | §2 runtime shape + §4 output | #4 |
| `recall()` auto-routing wrapper (session-cache aware) | `recall.py:361` | #4 (optional simpler entry point) |
| **Deletion / per-ticker purge**: `forget(dataset=...)`, `datasets.delete_data(...)`, `prune` | `forget.py:16`, `datasets.py:143`, `prune.py:4` | #9 (purge memory) |
| **Feedback / self-improvement loop**: `improve()` applies feedback weights; `FeedbackEntry`; `feedback_influence` on search | `improve.py:36`, `__init__.py:69`, `search.py` sig | #10 (feedback) |
| **Graph enrichment**: `memify()` over existing graph | `memify.py:25` | #11 (enrichment/memify) |
| **Local, no-cost embeddings** (fastembed 384-dim) — no embedding API key needed | §3 + §4 (ran clean) | all |

### ❌ Does NOT exist / must NOT be assumed

| Assumption | Reality | Action |
|---|---|---|
| `search(dataset_name=..., filters=date_range)` | **No such params** — `datasets=` / `dataset_ids=`; no `filters` | Rewrite the memory seam + docs (CONTRADICTION #1) |
| `cognee.delete(...)` as the deletion API | **Deprecated** wrapper | Use `forget` / `datasets.delete_data` |
| `gemini/gemini-2.0-flash` | Deprecated by Google, `limit: 0` | Use `gemini/gemini-2.5-flash` |
| Set `os.environ` before `import cognee` "just works" | Clobbered by import-time `load_dotenv(override=True)` | Load config after import / manage env explicitly (issue #3) |
| `COGNEE_LLM_PROVIDER` selects cognee's provider | cognee reads `LLM_PROVIDER` only | Fix in `.env` reconciliation (issue #3) |
| We build our own reranker/summarizer/embedding pipeline | Cognee owns all of it (as designed) — **confirmed** | none (assumption holds) |

### Net
Cognee 1.2.2 **supports everything the roadmap's Phase 3/4 and the feature issues need** — query/answer,
per-ticker isolation, deletion/purge, a feedback→improve loop, and graph enrichment — and the core
path is **proven working** on our target stack (Gemini `2.5-flash` + local fastembed). The blockers are
**not capability gaps** but **API-shape drift**: the `search()` signature (`datasets=`, no `filters`),
the deprecated `delete()`, the stale Gemini model string, and the env-loading override. All four should
be corrected in the memory seam and `.env` reconciliation (issues #1/#3) before Phase 3 wiring.

---

*Reproduce:* `.venv/bin/python spike/roundtrip.py` (needs `spike/spike.env` with a valid Gemini key).
Raw run log: `spike/roundtrip-output.log`.
