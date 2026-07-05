# Authentication & Authorization

> **Reality check.** For this hackathon build, auth is a **demo identity mechanism, not
> authentication.** Identity is asserted with a single header; no tokens are verified. The JWT/OAuth
> design is documented at the end as **roadmap**. Restore real auth before anything ships.

## What's built today: the `X-User-Id` header

Identity is asserted by the caller via an `X-User-Id` request header. There is no token, no signature,
no verification. Source of truth: [`backend/src/middleware/auth_middleware.py`](../backend/src/middleware/auth_middleware.py).

| Dependency | Behavior today |
|---|---|
| `get_current_user` | Reads `X-User-Id` (default `demo-user`). Returns a `CurrentUser` with role **`admin`** — so the single demo user can reach every screen, including `/admin`. |
| `require_admin` | Kept for API shape. Passes, because the demo user is always `admin`. |
| `require_service_token` | Guards `/memory/*` in the design. **No-op today** — internal endpoints are not actually gated. |

```bash
# every route is callable with no credentials; the header just names the principal
curl -s http://localhost:8000/api/v1/companies/AAPL/query \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: demo-user' \
  -d '{"question": "Why did the stock move?"}'
```

Missing header → `demo-user`. That's it. This is enough for the one thing per-user memory needs — a
**stable user id** to thread into session-scoped recall — without the ceremony of a real auth stack.

### What this means

- **RBAC is effectively off.** The demo principal is always `admin`; `require_admin` never blocks.
- **`/memory/*` is not network-isolated or token-gated** in the demo — the service-token check is a
  no-op. Treat the running stack as trusted/local only.
- The JWT/OAuth code paths and the login page exist in the tree but are **bypassed** at runtime.

## Roadmap: real auth (designed, not built) 🎯

The intended production design, none of which is enforced today:

- **JWT (RS256):** short-lived access token (15 min) + rotating refresh token (7 days), signed with a
  private key and verified with a public key. Config placeholders (`JWT_*`) exist in `.env.example`.
- **OAuth (Google):** sign-in mapped to the same `users` table by email
  (`GOOGLE_OAUTH_CLIENT_ID` / `_SECRET`).
- **Refresh rotation + revocation:** refresh tokens stored hashed in Postgres.
- **RBAC:** `user` vs `admin` enforced in middleware.
- **Internal service token:** `/memory/*` gated by `SERVICE_TOKEN` in addition to network isolation.
- **Key generation helper:** [`scripts/generate_jwt_keys.sh`](../scripts/generate_jwt_keys.sh)
  writes an RS256 keypair to the git-ignored `./secrets/` (for when JWT is wired up).

See [ARCHITECTURE.md §9](../ARCHITECTURE.md) for the full target design.

## Related controls (real today)

- **CORS** locked to configured origins (`BACKEND_CORS_ORIGINS`) — enforced in
  [`backend/src/main.py`](../backend/src/main.py).
- **Prompt-injection stance:** retrieved web/news content is treated as data, not instructions (a
  design rule — see [prompting.md](./prompting.md)).
