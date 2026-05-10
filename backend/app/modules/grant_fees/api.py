from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.grant_fees.schemas import (
    GrantFeeDraftGenerateOut,
    GrantFeeTaskBatchInstructionIn,
    GrantFeeTaskBatchInstructionOut,
    GrantFeeTaskBatchNoticeGenerateIn,
    GrantFeeTaskBatchNoticeGenerateOut,
    GrantFeeTaskListResponse,
    GrantFeeTaskModuleOut,
    GrantFeeTaskStateActionIn,
    GrantFeeTaskStateOut,
)
from app.modules.grant_fees.service import (
    apply_grant_fee_batch_instruction,
    apply_grant_fee_task_action,
    generate_grant_fee_draft,
    generate_grant_fee_notice_documents,
    get_grant_fee_module_contract,
    get_grant_fee_task_state,
    list_grant_fee_tasks,
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


@router.get("/grant-fee-tasks/list", summary="List grant fee tasks")
def list_grant_fee_tasks_endpoint(
    status: str | None = Query(default=None),
    client_instruction: str | None = Query(default=None),
    draft_generated: bool | None = Query(default=None),
    is_overdue: bool | None = Query(default=None),
    case_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("GrantFeeTask.Read")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskListResponse:
    return GrantFeeTaskListResponse.model_validate(
        list_grant_fee_tasks(
            db,
            filters={
                "status": status,
                "client_instruction": client_instruction,
                "draft_generated": draft_generated,
                "is_overdue": is_overdue,
                "case_id": case_id,
                "case_no": case_no,
                "date_from": date_from,
                "date_to": date_to,
            },
            page=page,
            page_size=page_size,
        )
    )


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


@router.post(
    "/grant-fee-tasks/batch-instruction", summary="Batch apply grant fee client instruction"
)
def post_grant_fee_task_batch_instruction_endpoint(
    payload: GrantFeeTaskBatchInstructionIn,
    _perm: None = Depends(require_perm("GrantFeeTask.Write")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskBatchInstructionOut:
    return GrantFeeTaskBatchInstructionOut.model_validate(
        apply_grant_fee_batch_instruction(db, task_ids=payload.task_ids, action=payload.action)
    )


@router.post(
    "/grant-fee-tasks/generate-notices", summary="Batch generate grant fee notice documents"
)
def post_grant_fee_task_batch_notice_generation_endpoint(
    payload: GrantFeeTaskBatchNoticeGenerateIn,
    _perm: None = Depends(require_perm("GrantFeeTask.Write")),
    db: Session = Depends(get_db),
) -> GrantFeeTaskBatchNoticeGenerateOut:
    return GrantFeeTaskBatchNoticeGenerateOut.model_validate(
        generate_grant_fee_notice_documents(db, task_ids=payload.task_ids)
    )


@router.post("/grant-fee-tasks/{task_id}/generate-draft", summary="Generate grant fee draft")
def post_grant_fee_task_generate_draft_endpoint(
    task_id: str,
    _perm: None = Depends(require_perm("GrantFeeTask.Write")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantFeeDraftGenerateOut:
    return GrantFeeDraftGenerateOut.model_validate(
        generate_grant_fee_draft(db, task_id=task_id, actor_id=current_user.id)
    )
