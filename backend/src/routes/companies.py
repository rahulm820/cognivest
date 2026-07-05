"""Company / watchlist + price + query routes.

All handlers are thin: validate via schema, delegate to a service, return a schema.
Auth (user) is required; the query path additionally applies the rate limiter.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.memory.dataset_naming import normalize_ticker
from src.middleware.auth_middleware import CurrentUser, get_current_user
from src.middleware.rate_limit import rate_limit
from src.repositories.company_repo import CompanyRepository
from src.schemas.company import CompanyOut, PriceSeriesOut, TickerCreate
from src.schemas.query import QueryRequest, QueryResponse
from src.services.memory_service import get_memory_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
async def list_companies(user: CurrentUser = Depends(get_current_user)) -> list[CompanyOut]:
    """List the authenticated user's watchlisted companies.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): watchlist_service.list_companies(user.id)
    raise NotImplementedError("TODO(phase-1): implement companies.list_companies")


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
async def add_company(
    payload: TickerCreate,
    user: CurrentUser = Depends(get_current_user),
) -> CompanyOut:
    """Add a ticker to the user's watchlist (triggers backfill).

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): watchlist_service.add_ticker(user.id, payload)
    raise NotImplementedError("TODO(phase-1): implement companies.add_company")


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_company(
    ticker: str,
    user: CurrentUser = Depends(get_current_user),
) -> None:
    """Remove a ticker from the user's watchlist (does not purge memory).

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-1): watchlist_service.remove_ticker(user.id, ticker)
    raise NotImplementedError("TODO(phase-1): implement companies.remove_company")


@router.get("/{ticker}/price", response_model=PriceSeriesOut)
async def get_price(
    ticker: str,
    range: str = Query(default="30d", description="Lookback window, e.g. '30d'."),
    user: CurrentUser = Depends(get_current_user),
) -> PriceSeriesOut:
    """Return the price series for a ticker over a lookback window.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-2): company/price service -> PriceSeriesOut
    raise NotImplementedError("TODO(phase-2): implement companies.get_price")


@router.post("/{ticker}/query", response_model=QueryResponse, dependencies=[Depends(rate_limit)])
async def query_company(
    ticker: str,
    payload: QueryRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> QueryResponse:
    """Answer a natural-language question scoped to a company.

    Single-LLM: the answer comes straight from Cognee's ``GRAPH_COMPLETION`` search via
    :class:`MemoryService` (no separate answer-formatter LLM). Rate-limited per user.

    Error contract:
      * 400 — ticker fails format validation (``normalize_ticker``).
      * 404 — company not on record. Wired to ``CompanyRepository.get_by_ticker``; that
        method is a phase-1 stub today, so the call is guarded (see below) and the route
        stays verifiable without 500-ing until issue #1 lands.
      * 200 — including the honest "no data ingested yet" answer when the dataset is
        empty (or the Cognee seam is still a scaffold stub — issue #4).
    """
    # 1. Validate ticker format (400 on bad input) before any I/O.
    try:
        normalized = normalize_ticker(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # 2. Existence guard (404). CompanyRepository.get_by_ticker is a phase-1 stub that
    #    raises NotImplementedError today; guard it so the route never 500s on the stub.
    #    TODO(#1): drop the NotImplementedError fallthrough once get_by_ticker is real.
    try:
        company = await CompanyRepository(db).get_by_ticker(normalized)
        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"company {normalized} is not on record",
            )
    except NotImplementedError:
        pass

    # 3. Session + user identity for per-user memory (#10/#11):
    #    - session_id keys Cognee's session cache; prefer X-User-Id, else a per-request id.
    #    - user_id enables cross-session memory (preferences + Q&A history) and is ONLY the
    #      caller-supplied X-User-Id — anonymous callers (no header) stay fully stateless.
    #    Raw header sanitization into a safe ``user_{id}`` dataset happens in the seam.
    session_id = x_user_id or uuid4().hex

    # 4. Single-LLM answer via the memory seam (personalized when X-User-Id is present).
    result = await get_memory_service().answer(
        normalized,
        payload.question,
        date_range=payload.date_range,
        session_id=session_id,
        user_id=x_user_id,
    )
    return QueryResponse(
        answer=result.answer,
        citations=result.citations,
        graph_snippet=result.graph_snippet,
    )
