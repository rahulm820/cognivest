# Contributing to Cognivest

Thanks for your interest in contributing! This guide covers how to set up your environment, our
conventions, and the PR process. Please also read [CLAUDE.md](./CLAUDE.md) — it captures the
non-negotiable architectural invariants.

## Getting Started

```bash
git clone https://github.com/your-org/cognivest.git
cd cognivest
cp .env.example .env          # fill in vendor + LLM keys
make install                  # backend + frontend deps
make hooks                    # install pre-commit hooks
make up && make migrate       # start the stack
```

See [docs/setup.md](./docs/setup.md) and [docs/development-workflow.md](./docs/development-workflow.md)
for details.

## Branching & Commits

- Branch from `main`: `feat/...`, `fix/...`, `chore/...`, `docs/...`, `refactor/...`.
- **Conventional Commits**: `type(scope): summary`
  - e.g. `feat(collectors): add GDELT news source`, `fix(memory): scope dataset by ticker`.
- Keep commits atomic and messages in the imperative mood.

## Code Standards

| Area | Tooling | Rule |
|---|---|---|
| Python | black, ruff, mypy (strict) | full type hints; no SQL outside `repositories/`; Cognee only in `memory/cognee_client.py` |
| TypeScript | prettier, eslint, tsc strict | API access only via `services/api/*`; server state via TanStack Query |

Run `make lint` and `make test` before pushing. Pre-commit enforces formatting on staged files —
**do not** bypass with `--no-verify`.

## The Cognee Rule

The single most important invariant: **the Cognee SDK is imported in exactly one place**
(`backend/src/memory/cognee_client.py`). Do not reimplement retrieval, embedding, reranking, or
summarization — Cognee owns those. See [CLAUDE.md §14](./CLAUDE.md).

## Tests

- New features ship with tests; bug fixes ship with a regression test.
- Backend: `pytest`. Mock the Cognee seam via `memory_service`.
- Frontend: `vitest` + RTL; e2e in `tests/e2e` (Playwright).
- Target ≥80% coverage on `services/` and `collectors/`.

## Pull Requests

1. Ensure CI is green (lint + type + test).
2. Fill in the PR template (what / why / testing / screenshots).
3. Update docs + `CHANGELOG.md` for user-facing changes.
4. Request review; keep PRs focused and reasonably small.

## Reporting Bugs / Requesting Features

Use the issue templates under `.github/ISSUE_TEMPLATE/`. For security issues, **do not** open a public
issue — follow [SECURITY.md](./SECURITY.md).

By contributing you agree your work is licensed under the project's [MIT License](./LICENSE) and that you
abide by our [Code of Conduct](./CODE_OF_CONDUCT.md).
