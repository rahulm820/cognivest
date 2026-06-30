"""Controllers.

In this codebase the FastAPI routers under ``src/routes/`` ARE the controllers in the
Clean Architecture sense: thin HTTP adapters that validate input via Pydantic schemas
and delegate to services. We keep them under ``routes/`` (FastAPI's idiom) rather than
duplicating a ``controllers/`` tree, so this package intentionally contains no handlers
— it exists only to document the choice and to keep the layer name discoverable.

See ``src/routes/__init__.py`` for the aggregated API router.
"""
