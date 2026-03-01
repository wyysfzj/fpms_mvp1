from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_param import SystemParam
from app.modules.system.schemas import SystemParamUpsertIn


def list_system_params(db: Session) -> list[SystemParam]:
    stmt = select(SystemParam).order_by(SystemParam.param_key.asc())
    return db.execute(stmt).scalars().all()


def get_system_param(db: Session, key: str) -> SystemParam | None:
    return db.execute(select(SystemParam).where(SystemParam.param_key == key)).scalar_one_or_none()


def upsert_system_param(
    db: Session,
    *,
    param_key: str,
    data: SystemParamUpsertIn,
    actor_id: str | None,
) -> SystemParam:
    param = db.execute(
        select(SystemParam).where(SystemParam.param_key == param_key)
    ).scalar_one_or_none()
    if not param:
        param = SystemParam(
            param_key=param_key,
            param_value=str(data.param_value),
            value_type=data.value_type or "string",
            description=data.description,
            is_secret=bool(data.is_secret) if data.is_secret is not None else False,
        )
        db.add(param)
    else:
        param.param_value = str(data.param_value)
        if data.value_type is not None:
            param.value_type = data.value_type
        if data.description is not None:
            param.description = data.description
        if data.is_secret is not None:
            param.is_secret = data.is_secret

    db.commit()
    db.refresh(param)
    return param


def mask_secret_param_value(param: SystemParam) -> str:
    if param.is_secret:
        return "******"
    return param.param_value
