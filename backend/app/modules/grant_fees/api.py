from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.grant_fees.schemas import GrantFeeTaskModuleOut
from app.modules.grant_fees.service import get_grant_fee_module_contract

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
