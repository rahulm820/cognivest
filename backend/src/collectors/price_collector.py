"""Price collector — yfinance (keyless market-data vendor, issue #8).

Two roles:
  * :func:`fetch_price_bars` — raw OHLCV bars for the ``/price`` endpoint (served
    on-demand; there is no price table).
  * :class:`PriceCollector` — turns the same bars into a few high-signal text
    summaries (period overview + notable-move days) so price action lands in the
    SAME Cognee dataset as news and the graph can correlate the two.

yfinance is synchronous; all calls are pushed off the event loop with
``asyncio.to_thread`` so they never block the API.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import yfinance as yf

from src.collectors.base import Collector, NormalizedItem
from src.config.logging import get_logger
from src.schemas.company import PriceBar

logger = get_logger(__name__)

# A day whose absolute close-to-close move meets this gets its own memory item.
_NOTABLE_MOVE_PCT = 3.0


async def fetch_price_bars(ticker: str, *, days: int = 30) -> list[PriceBar]:
    """Fetch trailing EOD OHLCV bars for ``ticker`` (up to ``days`` back).

    Returns an empty list for unknown tickers / no data rather than raising.
    """
    return await asyncio.to_thread(_fetch_price_bars_sync, ticker.upper(), days)


def _fetch_price_bars_sync(ticker: str, days: int) -> list[PriceBar]:
    """Blocking yfinance fetch (runs in a worker thread)."""
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    try:
        history = yf.Ticker(ticker).history(
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=False,
        )
    except Exception as exc:  # yfinance raises a grab-bag of network/parse errors
        logger.warning("price.fetch_failed", ticker=ticker, error=str(exc))
        return []

    bars: list[PriceBar] = []
    for index, row in history.iterrows():
        try:
            bars.append(
                PriceBar(
                    t=index.date(),
                    o=round(float(row["Open"]), 4),
                    h=round(float(row["High"]), 4),
                    l=round(float(row["Low"]), 4),
                    c=round(float(row["Close"]), 4),
                    v=int(row["Volume"]),
                )
            )
        except (ValueError, KeyError):  # skip holiday/NaN rows
            continue
    return bars


class PriceCollector(Collector):
    """Collect price bars from yfinance and summarize them for memory."""

    name = "price"

    def __init__(self, *, days: int = 30) -> None:
        """Look back ``days`` trailing days when collecting."""
        self._days = days

    async def collect(self, ticker: str) -> list[NormalizedItem]:
        """Fetch bars and normalize to a few high-signal price-action summaries."""
        ticker = ticker.upper()
        bars = await fetch_price_bars(ticker, days=self._days)
        if not bars:
            return []

        items: list[NormalizedItem] = []
        first, last = bars[0], bars[-1]
        period_pct = _pct_change(first.c, last.c)
        high = max(b.h for b in bars)
        low = min(b.l for b in bars)
        overview_ts = _to_dt(last.t)
        items.append(
            NormalizedItem(
                ticker=ticker,
                title=f"{ticker} price action, {first.t} to {last.t} ({period_pct:+.1f}%)",
                body=(
                    f"Over {first.t} to {last.t}, {ticker} moved from a close of "
                    f"{first.c:.2f} to {last.c:.2f} ({period_pct:+.1f}%). The period high was "
                    f"{high:.2f} and the low was {low:.2f} across {len(bars)} trading days."
                ),
                source="yfinance",
                ts=overview_ts,
                extra={"kind": "price_overview", "days": self._days},
            )
        )

        # One item per notable close-to-close move, so "why did it move on <date>?"
        # queries have a price event to correlate with same-day news.
        prev_close = first.c
        for bar in bars[1:]:
            move = _pct_change(prev_close, bar.c)
            if abs(move) >= _NOTABLE_MOVE_PCT:
                direction = "rose" if move > 0 else "fell"
                items.append(
                    NormalizedItem(
                        ticker=ticker,
                        title=f"{ticker} {direction} {abs(move):.1f}% on {bar.t}",
                        body=(
                            f"On {bar.t}, {ticker} {direction} {abs(move):.1f}% to close at "
                            f"{bar.c:.2f} (open {bar.o:.2f}, high {bar.h:.2f}, low {bar.l:.2f}, "
                            f"volume {bar.v:,})."
                        ),
                        source="yfinance",
                        ts=_to_dt(bar.t),
                        extra={"kind": "price_move", "pct": round(move, 2)},
                    )
                )
            prev_close = bar.c
        return items


def _pct_change(start: float, end: float) -> float:
    """Percent change from ``start`` to ``end`` (0.0 if start is falsy)."""
    return ((end - start) / start * 100.0) if start else 0.0


def _to_dt(day: object) -> datetime:
    """Coerce a bar ``date`` to a UTC ``datetime`` for ``NormalizedItem.ts``."""
    return datetime.fromisoformat(f"{day}T00:00:00+00:00")
