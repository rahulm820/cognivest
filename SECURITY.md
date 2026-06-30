# Security Policy

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email **security@cognivest.ai** (or the maintainers' private contact) with:

- A description of the issue and its impact.
- Steps to reproduce (proof-of-concept if available).
- Affected components/versions.

We aim to acknowledge within **48 hours** and provide a remediation timeline within **7 days**.
Please give us a reasonable window to fix the issue before any public disclosure.

## Supported Versions

| Version | Supported |
|---|---|
| `main` (latest) | ✅ |
| pre-1.0 tags | ⚠️ best-effort |

## Security Model (summary)

See [ARCHITECTURE.md §11](./ARCHITECTURE.md) for the full model. Key controls:

- **Secrets** live only in env / a secrets manager — never in code, logs, or Cognee datasets.
- **JWT (RS256)** + RBAC (`user` / `admin`); internal `/memory/*` endpoints are network-isolated and
  require a service token.
- **Prompt-injection guard**: ingested web/news content is treated strictly as *data*. The LLM system
  prompt instructs the model to ignore any instructions embedded in retrieved context.
- **Per-company dataset isolation** (`company_{ticker}`) prevents cross-tenant graph leakage.
- **Rate limiting** on query endpoints (LLM cost control) and per-vendor limits in collectors.
- **TLS in transit**, encryption at rest for Postgres and Cognee stores.

## Responsible Use

This project ingests third-party content via licensed APIs/search — **not** unrestricted scraping.
Contributors must respect each data source's Terms of Service.
