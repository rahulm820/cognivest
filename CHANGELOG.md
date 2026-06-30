# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository scaffold (Phase 0): folder structure, documentation, configuration,
  and typed placeholder implementations across frontend, backend, Cognee, AI, infra, and CI/CD.
- `ARCHITECTURE.md` (full Software Architecture Document) and `CLAUDE.md` (AI context).
- Docker Compose local development stack (postgres, redis, backend, worker, beat, frontend).
- Root tooling: Makefile, pre-commit, lint/format/type configs, `.env.example`.

### Notes
- Business logic is intentionally **not** implemented in this phase. Placeholders raise
  `NotImplementedError` or return typed stubs marked `# TODO(phase-N)`.

[Unreleased]: https://github.com/your-org/cognivest/commits/main
