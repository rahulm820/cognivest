# Offline Evaluation

Offline evaluation of the answer-generation step: how good and how grounded are the cited answers
the system produces? This guards against prompt regressions (see
[`../prompts/README.md`](../prompts/README.md)).

> **Scaffold phase.** [`run_eval.py`](./run_eval.py) is a stub with a valid CLI and a `TODO` body.

## What we measure

| Metric | Definition |
|---|---|
| **Citation accuracy** | Of the `[index]` citations in the answer, what fraction point to a passage that actually supports the cited claim (and is a valid index)? |
| **Groundedness** | What fraction of factual claims in the answer are supported by the retrieved context (vs. hallucinated / outside knowledge)? |
| **Context faithfulness** | Does the answer correctly say "not in the sources" when the fixture's gold answer is "insufficient context"? (tests the only-use-context rule) |
| **Injection resistance** | For fixtures with adversarial instructions embedded in passages, did the model ignore them? (tests the prompt-injection guard) |
| **Latency** | End-to-end query latency; tracked against the **< 3s p95** SLO ([ARCHITECTURE.md §1.7](../../ARCHITECTURE.md)). |

## Methodology

1. **Fixtures** — a curated set of `(ticker, question, date_range)` cases with gold expectations
   live under [`datasets/`](./datasets/) (payloads git-ignored; only `.gitkeep` is committed).
2. **Run** — for each fixture, call the query API (`POST /companies/{ticker}/query`, see
   [`../../docs/api.md`](../../docs/api.md)) and capture the answer + citations + latency.
3. **Score** — compute the metrics above. Citation/groundedness scoring may use exact-index checks
   plus an LLM-as-judge pass for claim support (kept separate from the system-under-test model).
4. **Report** — aggregate scores; compare against the previous baseline to catch regressions.

## Usage

```bash
python ai/eval/run_eval.py --dataset ai/eval/datasets/smoke.jsonl --api-base http://localhost:8000/api/v1
```

Run it after any change to the prompts ([`../prompts/`](../prompts/README.md)) or the
`answer_formatter`. See [`../../docs/prompting.md`](../../docs/prompting.md).
