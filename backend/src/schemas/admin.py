"""Admin / observability schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class JobRun(BaseModel):
    """A single ingestion job run, for the admin health view."""

    ticker: str
    type: str = Field(description="Job type: 'price' | 'news' | 'cognify'.")
    last_run: datetime | None = None
    items_ingested: int = 0
    status: str = Field(description="e.g. success | running | failed.")
    error: str | None = None


class JobRunsOut(BaseModel):
    """Collection wrapper for ingestion job runs."""

    jobs: list[JobRun] = Field(default_factory=list)
