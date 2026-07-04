#!/usr/bin/env python3
"""Seed demo data into Postgres.

Inserts a small, idempotent demo dataset so the dashboard isn't empty on first
run: three companies (AAPL, MSFT, TSLA), one demo user, and a watchlist linking
that user to all three. Safe to re-run — rows already present (matched on their
unique keys) are left untouched.

Run (Docker):  docker compose exec backend python -m scripts.seed
Access goes through the ORM session; there is no raw SQL. See scripts/README.md
and docs/database.md.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_sessionmaker
from src.models import Company, User, WatchlistItem

# (ticker, display name) for the demo watchlist.
DEMO_COMPANIES: list[tuple[str, str]] = [
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corporation"),
    ("TSLA", "Tesla, Inc."),
]

DEMO_EMAIL = "demo@cognivest.local"
DEMO_PASSWORD = "demo1234"  # local demo credential only — never a real secret
# 'admin' so the demo account can view every screen, including /admin. This is a
# local convenience seed; do not run it against a real environment.
DEMO_ROLE = "admin"


def _hash_password(password: str) -> str:
    """Bcrypt-hash a plaintext password.

    TODO(phase-1): delegate to ``src.utils.security.hash_password`` once that is
    implemented (security-primitives issue). It is kept inline here so the seed
    does not depend on unmerged work — the bcrypt output is format-compatible.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def _seed(session: AsyncSession) -> dict[str, int]:
    """Upsert the demo dataset within an open session; return created-row counts."""
    counts = {"companies": 0, "users": 0, "watchlist": 0}

    # Companies — idempotent on the unique COMPANIES(ticker) index.
    companies: dict[str, Company] = {}
    for ticker, name in DEMO_COMPANIES:
        company = (
            await session.execute(select(Company).where(Company.ticker == ticker))
        ).scalar_one_or_none()
        if company is None:
            company = Company(ticker=ticker, name=name)
            session.add(company)
            await session.flush()  # populate the client-side UUID PK for FKs below
            counts["companies"] += 1
        companies[ticker] = company

    # Demo user — idempotent on the unique USERS(email) index.
    user = (
        await session.execute(select(User).where(User.email == DEMO_EMAIL))
    ).scalar_one_or_none()
    if user is None:
        user = User(
            email=DEMO_EMAIL,
            password_hash=_hash_password(DEMO_PASSWORD),
            role=DEMO_ROLE,
        )
        session.add(user)
        await session.flush()
        counts["users"] += 1

    # Watchlist links — idempotent on the unique (user_id, company_id) constraint.
    for company in companies.values():
        link = (
            await session.execute(
                select(WatchlistItem).where(
                    WatchlistItem.user_id == user.id,
                    WatchlistItem.company_id == company.id,
                )
            )
        ).scalar_one_or_none()
        if link is None:
            session.add(WatchlistItem(user_id=user.id, company_id=company.id))
            counts["watchlist"] += 1

    await session.commit()
    return counts


async def seed() -> dict[str, int]:
    """Open a session and seed the demo dataset."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        return await _seed(session)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments (currently none — the demo set is fixed)."""
    parser = argparse.ArgumentParser(
        description="Seed demo companies (AAPL, MSFT, TSLA) + a demo user into Postgres."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: seed the demo dataset and report what was created."""
    parse_args(argv)
    tickers = ", ".join(ticker for ticker, _ in DEMO_COMPANIES)
    print(f"Seeding demo companies ({tickers}) + demo user {DEMO_EMAIL}...")
    counts = asyncio.run(seed())
    print(
        f"Done: {counts['companies']} company(ies), {counts['users']} user(s), "
        f"{counts['watchlist']} watchlist link(s) created "
        "(existing rows left untouched)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
