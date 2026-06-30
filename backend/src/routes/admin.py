"""Admin routes: ingestion health (admin only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.middleware.auth_middleware import CurrentUser, require_admin
from src.schemas.admin import JobRunsOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/jobs", response_model=JobRunsOut)
async def list_jobs(admin: CurrentUser = Depends(require_admin)) -> JobRunsOut:
    """List recent ingestion job runs across companies (admin only).

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-6): admin service -> ingestion job health -> JobRunsOut
    raise NotImplementedError("TODO(phase-6): implement admin.list_jobs")
