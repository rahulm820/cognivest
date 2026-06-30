# Prompts — mapping to the backend

The Markdown files in this directory are the **canonical source of truth** for the answer-generation
prompts. The backend mirrors them at runtime.

## Files

| File | Role |
|---|---|
| [`system_prompt.md`](./system_prompt.md) | The financial-news-analyst **system prompt** (rules: only-use-context, cite-by-index, prompt-injection guard). |
| [`answer_generation.md`](./answer_generation.md) | The **user/template prompt** with `{{question}}`, `{{ticker}}`, date range, and `{{context_block}}` placeholders. |

## Mapping into the backend

```text
ai/prompts/system_prompt.md       ─┐
ai/prompts/answer_generation.md   ─┴─►  backend/src/ai/prompt_templates.py
                                              │
                                              ▼
                                  backend/src/ai/answer_formatter.py
                                   (fills placeholders from Cognee
                                    search() results, calls Claude)
```

- `backend/src/ai/prompt_templates.py` holds the prompt text/templates used at runtime — kept **in
  sync with these files**. Treat the Markdown here as the reviewed, versioned source; sync the
  Python module when it changes.
- `backend/src/ai/answer_formatter.py` builds the numbered `{{context_block}}` from the ranked
  passages returned by the Cognee seam (`memory_service` → `cognee_client.search()`), fills the
  template, and calls Claude (`LLM_MODEL`, `LLM_MAX_TOKENS`). It then parses the model output into the
  `answer` + `citations` response shape.

## Workflow when changing a prompt

1. Edit the relevant file here.
2. Sync `backend/src/ai/prompt_templates.py`.
3. Re-run the offline evaluation ([`../eval/README.md`](../eval/README.md)) to check citation
   accuracy / groundedness / latency haven't regressed.
4. Commit both together (`docs`/`feat` scope `ai` or `prompts`).

See [`../../docs/prompting.md`](../../docs/prompting.md) for the full design and output contract.
