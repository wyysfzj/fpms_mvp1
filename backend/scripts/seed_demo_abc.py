from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.rbac.service import seed_default_roles_perms


@dataclass(frozen=True)
class DemoIdentity:
    username: str
    password: str
    display_name: str


def seed_demo_identities(
    db: Session,
    *,
    operator: DemoIdentity,
    reviewer: DemoIdentity,
) -> None:
    if operator.username == reviewer.username:
        raise RuntimeError("demo operator and reviewer usernames must differ")
    if operator.password == reviewer.password:
        raise RuntimeError("demo operator and reviewer passwords must differ")

    seed_default_roles_perms(db)
    admin_role = db.query(T_Role).filter(T_Role.code == "Admin").one_or_none()
    if admin_role is None:
        raise RuntimeError("Admin role is unavailable after role seed")

    for identity in (operator, reviewer):
        if db.query(T_User).filter(T_User.username == identity.username).first() is not None:
            raise RuntimeError(f"demo identity already exists: {identity.username}")
        user = T_User(
            id=str(uuid4()),
            username=identity.username,
            display_name=identity.display_name,
            password_hash=get_password_hash(identity.password),
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(T_UserRole(user_id=user.id, role_id=admin_role.id))
    db.commit()
