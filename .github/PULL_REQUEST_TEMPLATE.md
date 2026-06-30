<!--
  Thanks for contributing to Cognivest!
  Keep PRs focused and small (CLAUDE.md §11). Use a Conventional Commit title:
  e.g. feat(collectors): add GDELT news source
-->

## What
<!-- A concise description of the change. -->

## Why
<!-- The motivation / problem this solves. Link issues: Closes #123 -->

## How
<!-- Notable implementation decisions, trade-offs, or follow-ups. -->

## Testing
<!-- How was this verified? Commands run, new tests added, manual steps. -->
- [ ] Unit tests added/updated
- [ ] `make test` passes locally
- [ ] `make lint` passes locally

## Screenshots / recordings
<!-- For UI changes. Delete if N/A. -->

## Checklist
- [ ] Conventional Commit title (`type(scope): summary`)
- [ ] Tests added for new behavior / regression test for bug fixes
- [ ] Docs updated (`README` / `docs/` / `ARCHITECTURE.md` / `CLAUDE.md` as needed)
- [ ] `.env.example` updated for any new env var
- [ ] OpenAPI + `docs/api.md` updated for any new/changed endpoint
- [ ] CHANGELOG updated for user-facing changes
- [ ] No secrets committed; no Cognee imports outside `memory/cognee_client.py`
- [ ] CI is green (lint + type + test)
