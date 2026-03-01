from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.modules.auth.models import T_User


def authenticate_user(db: Session, username: str, password: str) -> T_User | None:
    """
    Authenticate user with username and password.

    Returns:
        T_User if authenticated, None otherwise
    """
    user = db.query(T_User).filter(T_User.username == username).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
