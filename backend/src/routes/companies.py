"""Company / watchlist + price + query routes.

All handlers are thin: validate via schema, delegate to a service, return a schema.
Auth (user) is required; the query path additionally applies the rate limiter.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from src.middleware.auth_middleware import CurrentUser, get_current_user
from src.middleware.rate_limit import rate_limit
from src.schemas.company import CompanyOut, PriceSeriesOut, TickerCreate
from src.schemas.query import QueryRequest, QueryResponse

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
) -> QueryResponse:
    """Answer a natural-language question scoped to a company.

    Wraps ``memory_service.search`` + answer formatting (rate-limited per user).

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-4): query_service.answer(user_id=user.id, ticker=ticker, request=payload)
    raise NotImplementedError("TODO(phase-4): implement companies.query_company")
