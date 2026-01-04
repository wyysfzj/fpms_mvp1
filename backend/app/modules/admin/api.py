from __future__ import annotations

import hashlib
import logging
import os
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.auth.models import T_Role, T_User, T_UserRole

router = APIRouter()


@router.get("/admin/users")
def list_admin_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("AdminUser.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(T_User)
    total = query.count()
    users = (
        query.order_by(T_User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "roles": [ur.role.code for ur in user.user_roles if ur.role],
            "created_at": user.created_at,
        }
        for user in users
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/admin/users", status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("AdminUser.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    username = payload.get("username")
    password = payload.get("password")
    role_codes: list[str] = payload.get("roles") or []

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="username and password are required"
        )

    existing = db.query(T_User).filter(T_User.username == username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")

    roles = []
    if role_codes:
        roles = db.query(T_Role).filter(T_Role.code.in_(role_codes)).all()
        found_codes = {role.code for role in roles}
        missing = [code for code in role_codes if code not in found_codes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"roles not found: {', '.join(missing)}",
            )

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user = T_User(
        id=str(uuid4()),
        username=username,
        password_hash=password_hash,
        is_active=payload.get("is_active", True),
    )
    db.add(user)
    db.flush()

    for role in roles:
        db.add(T_UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "is_active": user.is_active,
        "roles": role_codes or [role.code for role in roles],
    }


@router.put("/admin/users/{user_id}")
def update_admin_user(
    user_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("AdminUser.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    user = db.query(T_User).filter(T_User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    roles_payload: list[str] | None = payload.get("roles")
    is_active = payload.get("is_active")

    role_codes: list[str] = []
    roles: list[T_Role] = []
    if roles_payload is not None:
        role_codes = roles_payload
        roles = db.query(T_Role).filter(T_Role.code.in_(role_codes)).all()
        found_codes = {role.code for role in roles}
        missing = [code for code in role_codes if code not in found_codes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"roles not found: {', '.join(missing)}",
            )

        db.query(T_UserRole).filter(T_UserRole.user_id == user.id).delete()
        for role in roles:
            db.add(T_UserRole(user_id=user.id, role_id=role.id))

    if is_active is not None:
        user.is_active = bool(is_active)

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "is_active": user.is_active,
        "roles": role_codes or [ur.role.code for ur in user.user_roles if ur.role],
    }


@router.post("/admin/seed/roles-permissions")
async def seed_roles_permissions(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    roles = [
        {"code": "Admin", "name": "Admin"},
        {"code": "Staff", "name": "Staff"},
    ]

    existing_users = db.query(T_User).count()
    admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
    bootstrap_allowed = existing_users == 0 or admin_role is None
    if not bootstrap_allowed:
        await require_perm("AdminUser.Edit")(authorization=authorization)

    existing_roles = {
        role.code: role
        for role in db.query(T_Role).filter(T_Role.code.in_([r["code"] for r in roles])).all()
    }

    for role_data in roles:
        if role_data["code"] not in existing_roles:
            role = T_Role(id=str(uuid4()), code=role_data["code"], name=role_data["name"])
            db.add(role)
            existing_roles[role.code] = role

    admin_user = db.query(T_User).filter(T_User.username == "admin").first()
    admin_password = os.getenv("FPMS_ADMIN_PASSWORD") or "ChangeMe123!"
    if os.getenv("FPMS_ADMIN_PASSWORD") is None:
        logging.warning("FPMS_ADMIN_PASSWORD not set; using default for bootstrap only")

    if not admin_user:
        admin_user = T_User(
            id=str(uuid4()),
            username="admin",
            password_hash=hashlib.sha256(admin_password.encode("utf-8")).hexdigest(),
            is_active=True,
        )
        db.add(admin_user)
        db.flush()

    admin_role = existing_roles.get("Admin")
    if admin_role:
        has_admin_role = (
            db.query(T_UserRole)
            .filter(T_UserRole.user_id == admin_user.id, T_UserRole.role_id == admin_role.id)
            .first()
        )
        if not has_admin_role:
            db.add(T_UserRole(user_id=admin_user.id, role_id=admin_role.id))

    db.commit()

    return {"status": "ok"}
