from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.grant_fees.schemas import (
    GrantFeeTaskModuleOut,
    GrantFeeTaskStateActionIn,
    GrantFeeTaskStateOut,
)
from app.modules.grant_fees.service import (
    apply_grant_fee_task_action,
    get_grant_fee_module_contract,
    get_grant_fee_task_state,
)

router = APIRouter()


@router.get("/grant-fee-tasks", summary="Grant fee module contract")
def get_grant_fee_tasks(
    _perm: None = Depends(require_perm("GrantFeeTask.Read")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskModuleOut:
    _ = db
    return GrantFeeTaskModuleOut.model_validate(get_grant_fee_module_contract())


@router.post("/grant-fee-tasks", summary="Grant fee module write contract")
def post_grant_fee_tasks(
    _perm: None = Depends(require_perm("GrantFeeTask.Write")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskModuleOut:
    _ = db
    return GrantFeeTaskModuleOut.model_validate(get_grant_fee_module_contract())


@router.get("/grant-fee-tasks/{task_id}/state", summary="Get grant fee task state")
def get_grant_fee_task_state_endpoint(
    task_id: str,
    _perm: None = Depends(require_perm("GrantFeeTask.Read")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskStateOut:
    return GrantFeeTaskStateOut.model_validate(get_grant_fee_task_state(db, task_id=task_id))


@router.put("/grant-fee-tasks/{task_id}/state", summary="Advance grant fee task state")
def put_grant_fee_task_state_endpoint(
    task_id: str,
    payload: GrantFeeTaskStateActionIn,
    _perm: None = Depends(require_perm("GrantFeeTask.Write")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskStateOut:
    return GrantFeeTaskStateOut.model_validate(
        apply_grant_fee_task_action(db, task_id=task_id, action=payload.action)
    )
