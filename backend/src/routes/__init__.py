"""API route aggregation.

Builds the single :data:`api_router` that ``main.py`` mounts under ``/api/v1``. Each
sub-router is thin: validate via schema, call a service, return a schema.
"""

from fastapi import APIRouter

from src.routes import admin, auth, companies, memory

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(admin.router)
api_router.include_router(memory.router)

__all__ = ["api_router"]
