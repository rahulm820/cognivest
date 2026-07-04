"""Integration round-trip for the Cognee seam (issues #2 / #4 acceptance).

Adds two documents to ``company_AAPL`` → ``cognify`` → ``search`` and prints the
results, proving the seam wires cognee 1.2.2 (Gemini + fastembed) end to end.

Uses ONLY the memory seam (``get_cognee_client``) and never imports the cognee SDK
directly, so a repo-wide search for the SDK import stays at exactly one hit (the seam).

Run (needs ``LLM_API_KEY`` set for cognify's Gemini LLM — see .env / issue #3):

    docker compose exec backend python -m scripts.cognee_roundtrip
"""

from __future__ import annotations

import asyncio

from src.memory.cognee_client import get_cognee_client

TICKER = "AAPL"

DOCS: list[tuple[str, dict[str, str]]] = [
    (
        "Apple reported record fiscal Q3 revenue driven by strong iPhone sales and "
        "double-digit Services growth. The company beat analyst expectations on both "
        "revenue and EPS, sending shares up about 6% in after-hours trading.",
        {
            "source_url": "https://example.com/apple-q3-earnings",
            "published_at": "2026-05-02T20:00:00Z",
            "title": "Apple beats Q3 estimates on iPhone and Services strength",
        },
    ),
    (
        "Apple's board authorized a $110 billion share buyback — the largest in the "
        "company's history — and raised its quarterly dividend. Investors welcomed the "
        "expanded capital-return program, adding to the post-earnings rally.",
        {
            "source_url": "https://example.com/apple-buyback",
            "published_at": "2026-05-02T20:05:00Z",
            "title": "Apple announces record $110B buyback and dividend hike",
        },
    ),
]

QUERY = "Why did Apple stock rise after earnings?"


async def main() -> None:
    """Run add → cognify → search against company_AAPL and print the results."""
    client = get_cognee_client()

    for content, metadata in DOCS:
        await client.add(TICKER, content, metadata=metadata)
    print(f"[add] ingested {len(DOCS)} documents into company_{TICKER}")

    await client.cognify(TICKER)
    print("[cognify] knowledge graph built")

    results = await client.search(TICKER, QUERY, top_k=5)
    print(f"[search] query={QUERY!r} -> {len(results)} result(s)")
    for i, result in enumerate(results, start=1):
        print(f"  {i}. {result}")

    assert results, "expected at least one search result"
    print("[ok] round-trip succeeded")


if __name__ == "__main__":
    asyncio.run(main())
