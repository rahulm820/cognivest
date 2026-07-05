"""FastAPI application factory.

Builds the ASGI app: structured logging, CORS from settings, the aggregated API
router mounted under the configured ``/api/v1`` prefix, and liveness health endpoints.
Import-time side effects are avoided — everything happens inside :func:`create_app`.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import __version__
from src.config.logging import configure_logging, get_logger
from src.config.settings import Settings, get_settings
from src.routes import api_router


def _health_payload(settings: Settings) -> dict[str, Any]:
    """Build the health-check response body."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": __version__,
        "env": settings.app_env,
    }


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override (useful in tests); defaults to the
            cached singleton.

    Returns:
        The configured :class:`FastAPI` instance.
    """
    settings = settings or get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)

    app = FastAPI(
        title="Cognivest — Backend",
        version=__version__,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # CORS locked to known frontend origins (ARCHITECTURE.md §11).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Liveness (unversioned) — always functional, used by tests + orchestrators.
    @app.get("/health", tags=["health"])
    async def health() -> dict[str, Any]:
        """Liveness probe."""
        return _health_payload(settings)

    # Versioned health under the API prefix.
    @app.get(f"{settings.api_v1_prefix}/health", tags=["health"])
    async def health_v1() -> dict[str, Any]:
        """Versioned health probe."""
        return _health_payload(settings)

    # Scaffold-honest error contract: routes/services that are still typed stubs raise
    # NotImplementedError. Map that to a 501 envelope so unimplemented endpoints return an
    # honest "not built yet" instead of a raw 500. This only fires when NotImplementedError
    # *escapes* a handler — the live query path catches its own in-path NotImplementedError
    # (see routes/companies.py and services/memory_service.py) and stays a 200, so the
    # no-data query flow is unaffected.
    @app.exception_handler(NotImplementedError)
    async def _not_implemented_handler(
        _request: Request, _exc: NotImplementedError
    ) -> JSONResponse:
        """Return a 501 for endpoints still stubbed out in the hackathon scaffold."""
        return JSONResponse(
            status_code=501,
            content={"detail": "Not implemented — hackathon scope. See README limitations."},
        )

    # Mount all v1 routers.
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    logger.info("app.created", env=settings.app_env, prefix=settings.api_v1_prefix)
    return app


# ASGI entrypoint used by uvicorn (`uvicorn src.main:app`).
app = create_app()
