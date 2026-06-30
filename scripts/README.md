# `scripts/` — Operational CLIs

Admin / ops scripts. Run from the repo root (or inside the backend container via the
[Makefile](../Makefile) targets noted below).

> **Scaffold phase.** The Python scripts have valid CLIs (argparse) but stub bodies marked
> `# TODO(phase-N)`. `generate_jwt_keys.sh` is real and working.

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| [`backfill_ticker.py`](./backfill_ticker.py) | Enqueue a historical backfill for a ticker. | `python scripts/backfill_ticker.py --ticker AAPL` (or `make backfill t=AAPL`) |
| [`purge_dataset.py`](./purge_dataset.py) | Purge a Cognee dataset (admin). | `python scripts/purge_dataset.py --ticker AAPL --scope all` (or `make purge t=AAPL`) |
| [`seed.py`](./seed.py) | Seed a demo ticker into Postgres. | `python scripts/seed.py` (or `make seed`) |
| [`generate_jwt_keys.sh`](./generate_jwt_keys.sh) | Generate an RS256 JWT keypair into `./secrets/`. | `bash scripts/generate_jwt_keys.sh` |

## Notes

- **`backfill_ticker.py`** enqueues collector jobs onto the Celery queues (`price`, `news`) for a
  date range, then cognify follows on its own queue. Backfills can spike the `cognify` queue — see
  the [cognify-backlog runbook](../docs/runbooks/cognify-backlog.md).
- **`purge_dataset.py`** is the deletion lever for memory. It goes through the single Cognee seam
  (`memory_service` → `cognee_client`), scoped to `company_{ticker}`. `--scope` selects all vs. a
  date-bounded slice. This is the CLI equivalent of `DELETE /memory/delete`
  ([api.md](../docs/api.md)). **Admin only.**
- **`seed.py`** inserts a demo company into Postgres (see [database.md](../docs/database.md)) so the
  dashboard isn't empty on first run.
- **`generate_jwt_keys.sh`** writes `secrets/jwt_private.pem` + `secrets/jwt_public.pem` matching
  `JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH` ([authentication.md](../docs/authentication.md)).
  `./secrets/` is git-ignored — **never commit keys**.

## Invariants

- Scripts that touch memory use the Cognee seam; they never import the Cognee SDK directly and never
  cross datasets ([CLAUDE.md §14](../CLAUDE.md)).
- Scripts that touch Postgres go through repositories — no inline SQL.
