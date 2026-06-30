"""Shared schema building blocks: error envelope and date range."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ErrorDetail(BaseModel):
    """Machine-readable error body."""

    code: str = Field(description="Stable, machine-readable error code, e.g. 'not_found'.")
    message: str = Field(description="Human-readable error message.")
    detail: str | None = Field(default=None, description="Optional additional context.")


class ErrorEnvelope(BaseModel):
    """Consistent error response envelope: ``{ "error": { code, message, detail } }``."""

    error: ErrorDetail


class DateRange(BaseModel):
    """Inclusive date range used to scope queries and memory slices."""

    model_config = ConfigDict(populate_by_name=True)

    from_: date = Field(alias="from", description="Start date (inclusive).")
    to: date = Field(description="End date (inclusive).")

    @model_validator(mode="after")
    def _check_order(self) -> DateRange:
        """Ensure ``from`` is not after ``to``."""
        if self.from_ > self.to:
            raise ValueError("date_range.from must be on or before date_range.to")
        return self
