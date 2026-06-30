# Authentication & Authorization

Auth secures the **application layer** (users/admins) only. Cognee is treated as an internal,
network-isolated service. Derived from [ARCHITECTURE.md §9](../ARCHITECTURE.md) and
[§4.6](../ARCHITECTURE.md).

## JWT (RS256)

- **Algorithm**: RS256 (asymmetric). Tokens are signed with a **private key** and verified with a
  **public key** — the private key never leaves the auth issuer.
- **Access token**: short-lived (**15 min**, `JWT_ACCESS_TOKEN_TTL_MINUTES`). Sent on every request
  as `Authorization: Bearer <token>`.
- **Refresh token**: longer-lived (**7 days**, `JWT_REFRESH_TOKEN_TTL_DAYS`), **rotated** on each
  use.
- **Sessions are stateless** — the API verifies the JWT signature; no server-side session store for
  access tokens.

### Keys

Generate the RS256 keypair with the helper script (writes to the git-ignored `./secrets/`):

```bash
bash scripts/generate_jwt_keys.sh
```

Configured via `.env` (see [environment.md](./environment.md)):

```ini
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./secrets/jwt_public.pem
JWT_ACCESS_TOKEN_TTL_MINUTES=15
JWT_REFRESH_TOKEN_TTL_DAYS=7
```

In production, keys come from the secrets manager, never committed. See [deployment.md](./deployment.md).

## Refresh & rotation

- `POST /auth/login` issues an access + refresh pair (see [api.md](./api.md)).
- `POST /auth/refresh` validates the presented refresh token, **rotates** it (issues a new one and
  invalidates the old), and returns a fresh access token.
- **Refresh tokens are stored hashed in Postgres** so they can be **revoked** on logout or suspected
  compromise. Rotation means a stolen-and-replayed old refresh token fails after the legitimate
  client has refreshed.

## OAuth (Google)

Google sign-in is an additional login option, mapped to the **same `users` table** via email. A
Google login resolves to (or creates) the same user record a password login would, so RBAC and
watchlists are identical regardless of login method.

Configured via `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET`.

## RBAC

Two roles for v1, enforced in middleware (`backend/src/middleware/auth_middleware.py`):

| Role | Can |
|---|---|
| `user` | manage own watchlist, query own companies (`/companies/*`). |
| `admin` | everything `user` can, plus ingestion health (`/admin/jobs`), `/memory/reflection`, `/memory/delete`. |

The role is a claim in the access token and a column on `USERS` (see [database.md](./database.md)).

## Internal service token for `/memory/*`

The `/memory/*` endpoints are **internal-only**: they are network-isolated (private subnet) **and**
require a service-to-service token in addition to any role check:

```ini
SERVICE_TOKEN=change_me_internal_service_token
```

- Collectors and the query path reach Cognee through `memory_service.py`, which presents the
  service token on internal calls.
- `/memory/reflection` and `/memory/delete` additionally require the `admin` role.
- The frontend **never** calls `/memory/*` directly — only `/companies/{ticker}/query`, which wraps
  `/memory/search` server-side.

This layering keeps the Cognee single seam (see [memory-architecture.md](./memory-architecture.md))
both code-isolated and network-isolated.

## Related security controls

- CORS locked to known frontend origins (`BACKEND_CORS_ORIGINS`).
- Per-user rate limiting on `/companies/{ticker}/query` (`QUERY_RATE_LIMIT_PER_MINUTE`) for LLM cost
  control.
- Prompt-injection guard on retrieved content (see [prompting.md](./prompting.md)).

See [ARCHITECTURE.md §11](../ARCHITECTURE.md) for the full security model.
