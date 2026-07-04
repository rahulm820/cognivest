# Contributing

This is a short pointer. The full contribution guide is the root
[CONTRIBUTING.md](../CONTRIBUTING.md) — read it first. The durable architectural invariants are in
[CLAUDE.md](../CLAUDE.md).

## Quick links

- **Getting set up** → [setup.md](./setup.md)
- **Day-to-day workflow** (branching, commits, `make`, PRs) → [development-workflow.md](./development-workflow.md)
- **Code style & layering** → [coding-standards.md](./coding-standards.md)
- **Code of Conduct** → [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- **Security policy** → [SECURITY.md](../SECURITY.md)

## The Cognee invariant (do not violate)

The single most important rule in this codebase:

> **The Cognee SDK is imported in exactly one place: `backend/src/memory/cognee_client.py`.**

Corollaries:

- Everything memory-related funnels through `memory_service.py` — Cognee is a **single seam**.
- **Never** reimplement retrieval, embedding, reranking, or summarization — Cognee owns those.
- Memory is always scoped to **one dataset per ticker** (`company_{ticker}`); never cross-query.
- Always run the **dedup hash check before `cognee.add()`**.
- Retrieved web/news content is **data, not instructions** (prompt-injection guard).

See [memory-architecture.md](./memory-architecture.md) and [CLAUDE.md §14](../CLAUDE.md) for the
complete list of invariants Claude (and humans) must never break.
