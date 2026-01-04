from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.masterdata.clients.models import Client

router = APIRouter()


@router.get("/clients")
def get_clients(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Client.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    base_query = db.query(Client)
    if q:
        pattern = f"%{q}%"
        base_query = base_query.filter(
            or_(
                Client.client_code.ilike(pattern),
                Client.name_cn.ilike(pattern),
                Client.name_en.ilike(pattern),
            )
        )

    total = base_query.count()
    clients = (
        base_query.order_by(Client.client_code)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        {
            "id": client.id,
            "client_code": client.client_code,
            "name_cn": client.name_cn,
            "name_en": client.name_en,
        }
        for client in clients
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/clients", status_code=status.HTTP_201_CREATED)
def create_client(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Client.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    client = Client(
        id=str(uuid4()),
        client_code=payload.get("client_code"),
        name_cn=payload.get("name_cn") or "",
        name_en=payload.get("name_en"),
        client_type=payload.get("client_type") or "CLIENT",
        default_currency=payload.get("default_currency") or "CNY",
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {
        "id": client.id,
        "client_code": client.client_code,
        "name_cn": client.name_cn,
        "name_en": client.name_en,
        "client_type": client.client_type,
        "default_currency": client.default_currency,
    }


@router.put("/clients/{client_id}/deactivate")
def deactivate_client(
    client_id: str,
    _perm: None = Depends(require_perm("Client.Action")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    client.is_active = False
    db.commit()
    return {"status": "ok"}


@router.put("/clients/{client_id}")
def update_client(
    client_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Client.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    client.client_code = payload.get("client_code", client.client_code)
    client.name_cn = payload.get("name_cn", client.name_cn) or ""
    client.name_en = payload.get("name_en", client.name_en)
    client.client_type = payload.get("client_type", client.client_type)
    client.default_currency = payload.get("default_currency", client.default_currency)

    db.commit()
    db.refresh(client)
    return {
        "id": client.id,
        "client_code": client.client_code,
        "name_cn": client.name_cn,
        "name_en": client.name_en,
        "client_type": client.client_type,
        "default_currency": client.default_currency,
    }
