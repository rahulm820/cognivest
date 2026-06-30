"""Request middleware + FastAPI security dependencies.

Houses JWT verification + RBAC dependencies (``auth_middleware``) and the per-user
rate-limit dependency (``rate_limit``).
"""
