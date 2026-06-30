"""Company / watchlist + price-series schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

_TICKER_PATTERN = r"^[A-Z][A-Z0-9.\-]{0,9}$"


class TickerCreate(BaseModel):
    """Request body to add a ticker to the watchlist."""

    ticker: str = Field(pattern=_TICKER_PATTERN, description="Uppercase ticker symbol, e.g. AAPL.")

    @field_validator("ticker")
    @classmethod
    def _upper(cls, value: str) -> str:
        return value.upper()


class CompanyOut(BaseModel):
    """Company resource as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticker: str
    name: str | None = None
    status: str = Field(default="active", description="e.g. backfilling | active.")
    created_at: datetime


class PriceBar(BaseModel):
    """A single OHLCV price bar."""

    t: date = Field(description="Bar timestamp (date for EOD bars).")
    o: float = Field(description="Open.")
    h: float = Field(description="High.")
    l: float = Field(description="Low.")  # noqa: E741 - matches API contract field name
    c: float = Field(description="Close.")
    v: int = Field(description="Volume.")


class PriceSeriesOut(BaseModel):
    """Price series for a ticker over a requested range."""

    ticker: str
    bars: list[PriceBar] = Field(default_factory=list)
