from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.models.system_param import SystemParam

router = APIRouter()


@router.get("/system/params")
def get_system_params(
    _perm: None = Depends(require_perm("SystemParam.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    params = db.query(SystemParam).order_by(SystemParam.param_key).all()
    items = [
        {
            "param_key": param.param_key,
            "param_value": "***" if param.is_secret else param.param_value,
            "value_type": param.value_type,
            "is_secret": param.is_secret,
            "updated_at": param.updated_at,
        }
        for param in params
    ]
    return {"items": items}


@router.put("/system/params/{param_key}")
def upsert_system_param(
    param_key: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    param_value = payload.get("param_value")
    if param_value is None:
        raise HTTPException(status_code=400, detail="param_value is required")

    value_type = payload.get("value_type") or "string"
    is_secret = bool(payload.get("is_secret")) if payload.get("is_secret") is not None else False
    description = payload.get("description")

    param = db.query(SystemParam).filter(SystemParam.param_key == param_key).first()
    if not param:
        param = SystemParam(
            param_key=param_key,
            param_value=str(param_value),
            value_type=value_type,
            is_secret=is_secret,
            description=description,
        )
        db.add(param)
    else:
        param.param_value = str(param_value)
        param.value_type = value_type
        param.is_secret = is_secret
        param.description = description

    db.commit()
    db.refresh(param)

    return {
        "param_key": param.param_key,
        "param_value": param.param_value,
        "value_type": param.value_type,
        "is_secret": param.is_secret,
    }
