"""Common dependencies (auth, permissions, pagination).

This file is a placeholder for BE-00-02 task.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Header, HTTPException, status


def require_perm(code: str) -> Callable:
    """Return a FastAPI dependency that enforces a permission code.

    TODO (BE-00-02): implement with JWT auth + RBAC lookup.
    """

    async def _dep(authorization: str | None = Header(default=None)) -> None:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        # Placeholder: actual permission check to be implemented in BE-00-02.
        # The dependency stays in place to ensure the route remains protected.
        return None

    return _dep
