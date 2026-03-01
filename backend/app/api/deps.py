from __future__ import annotations

from typing import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import raise_business_error
from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.rbac.service import get_user_permissions

security = HTTPBearer(auto_error=False)
credentials_dep = Depends(security)
db_dep = Depends(get_db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = credentials_dep,
    db: Session = db_dep,
) -> T_User:
    """Get current authenticated user from JWT token."""
    if credentials is None:
        raise_business_error("AUTH_REQUIRED", "Authentication required", status_code=401)

    token = credentials.credentials
    settings = get_settings()

    try:
        payload = decode_access_token(token, settings.jwt_secret)
        user_id = payload.get("sub")
        if not user_id:
            raise_business_error("AUTH_REQUIRED", "Invalid token", status_code=401)
    except Exception:
        raise_business_error("AUTH_REQUIRED", "Authentication required", status_code=401)

    user = db.query(T_User).filter(T_User.id == user_id).first()
    if not user or not user.is_active:
        raise_business_error("AUTH_REQUIRED", "User not found or inactive", status_code=401)

    return user


current_user_dep = Depends(get_current_user)


def require_perm(code: str) -> Callable:
    """Return dependency that enforces a permission code."""

    def _perm_checker(
        current_user: T_User = current_user_dep,
        db: Session = db_dep,
    ) -> None:
        perms = get_user_permissions(db, current_user.id)
        if code not in perms:
            raise_business_error(
                "FORBIDDEN",
                "Permission denied",
                details={"required_perm": code},
                status_code=403,
            )

    return _perm_checker
