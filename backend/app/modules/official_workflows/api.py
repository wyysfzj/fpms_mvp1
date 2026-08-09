from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.errors import BusinessError
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.official_workflows.schemas import (
    FilingPreparationChecklistResultOut,
    FilingPreparationChecklistUpdateIn,
    FilingPreparationExternalOperationIn,
    FilingPreparationPackageOut,
    FilingPreparationRefreshIn,
    FormatLetterArchiveIn,
    FormatLetterArchiveOut,
    LetterHandoffCreateIn,
    LetterHandoffPreviewOut,
    LetterHandoffResultOut,
    LetterHandoffStatusUpdateIn,
    OaReplyChecklistResultOut,
    OaReplyChecklistUpdateIn,
    OaReplyLinkDocumentIn,
    OaReplyPackageOut,
    OaReplyRefreshIn,
    OfficialFeeLinkageOut,
    OfficialWorkPackageArchiveIn,
    OfficialWorkPackageArchiveResultOut,
    OfficialWorkPackageChecklistOut,
    OfficialWorkPackageOut,
    OfficialWorkPackageReceiptCreateIn,
    OfficialWorkPackageReceiptOut,
)
from app.modules.official_workflows.service import (
    FormatLetterArchiveCommand,
    PendingFormatLetterArchiveOperation,
    _remove_format_letter_archive_file,
    archive_official_work_package,
    ensure_filing_preparation_package,
    ensure_oa_reply_package,
    evaluate_official_work_package,
    get_filing_preparation_package,
    get_letter_handoff_preview,
    get_oa_reply_package,
    get_official_fee_linkage,
    link_oa_reply_document,
    prepare_format_letter_archive,
    prepare_letter_handoff,
    record_filing_preparation_external_operation,
    record_letter_handoff_status,
    record_official_work_package_receipt,
    refresh_filing_preparation_package,
    refresh_oa_reply_package,
    update_filing_preparation_checklist,
    update_oa_reply_checklist,
)

router = APIRouter()


def format_letter_archive_out(
    db: Session,
    pending: PendingFormatLetterArchiveOperation,
    *,
    reused: bool,
) -> FormatLetterArchiveOut:
    del db
    result = pending.result
    return FormatLetterArchiveOut(
        handoff=result.handoff,
        evidence_version_id=result.evidence_version_id,
        version_number=result.version_number,
        content_hash=result.content_hash,
        generated_document_id=result.generated_document_id,
        attachment_id=result.attachment_id,
        file_name=result.file_name,
        role=result.role.value,
        state=result.state.value,
        review_state=result.review_state.value,
        is_current=result.is_current,
        reused=reused,
    )


@router.get(
    "/official-documents/{document_id}/letter-handoff/preview",
    response_model=LetterHandoffPreviewOut,
    summary="Preview format-letter handoff",
)
def preview_letter_handoff_endpoint(
    document_id: str,
    _perm: None = Depends(require_perm("OfficialWorkflow.Read")),
    db: Session = Depends(get_db),
) -> LetterHandoffPreviewOut:
    return get_letter_handoff_preview(db, source_document_id=document_id)


@router.post(
    "/official-documents/{document_id}/letter-handoff",
    status_code=status.HTTP_201_CREATED,
    response_model=LetterHandoffResultOut,
    summary="Create format-letter handoff",
)
def create_letter_handoff_endpoint(
    document_id: str,
    payload: LetterHandoffCreateIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> LetterHandoffResultOut:
    return prepare_letter_handoff(
        db,
        source_document_id=document_id,
        remark=payload.remark,
    )


@router.post(
    "/official-documents/{source_document_id}/format-letter-archive",
    status_code=status.HTTP_201_CREATED,
    response_model=FormatLetterArchiveOut,
    summary="Generate and archive format letter",
)
def archive_format_letter_endpoint(
    source_document_id: UUID,
    payload: FormatLetterArchiveIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FormatLetterArchiveOut:
    try:
        pending = prepare_format_letter_archive(
            FormatLetterArchiveCommand(
                source_document_id=str(source_document_id),
                operation_id=str(payload.operation_id),
                selected_contact_id=(
                    str(payload.selected_contact_id)
                    if payload.selected_contact_id is not None
                    else None
                ),
                remark=payload.remark,
                actor_id=current_user.id,
            ),
            db,
        )
    except Exception:
        db.rollback()
        raise

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        if (
            not pending.reused
            and pending.managed_file_path is not None
            and pending.managed_file_identity is not None
        ):
            _remove_format_letter_archive_file(
                pending.managed_file_path,
                expected_identity=pending.managed_file_identity,
                original_error=exc,
            )
        raise BusinessError(
            "FORMAT_LETTER_ARCHIVE_PERSIST_FAILED",
            "Format-letter archive could not be persisted",
            status_code=500,
        ) from exc

    return format_letter_archive_out(db, pending, reused=pending.reused)


@router.patch(
    "/official-documents/{document_id}/letter-handoff/{handoff_id}/status",
    response_model=LetterHandoffResultOut,
    summary="Record format-letter handoff status",
)
def record_letter_handoff_status_endpoint(
    document_id: str,
    handoff_id: str,
    payload: LetterHandoffStatusUpdateIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> LetterHandoffResultOut:
    return record_letter_handoff_status(
        db,
        source_document_id=document_id,
        handoff_id=handoff_id,
        longxia_handoff_status=payload.longxia_handoff_status,
        longxia_handoff_payload=payload.longxia_handoff_payload,
        handoff_at=payload.handoff_at,
    )


@router.post(
    "/official-documents/{document_id}/official-work-packages/oa-reply/resolve",
    status_code=status.HTTP_200_OK,
    response_model=OaReplyPackageOut,
    summary="Resolve OA reply package",
)
def resolve_oa_reply_package_endpoint(
    document_id: UUID,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> OaReplyPackageOut:
    return ensure_oa_reply_package(db, source_document_id=str(document_id))


@router.get(
    "/official-work-packages/{package_id}/oa-reply",
    response_model=OaReplyPackageOut,
    summary="Get OA reply package",
)
def get_oa_reply_package_endpoint(
    package_id: str,
    _perm: None = Depends(require_perm("OfficialWorkflow.Read")),
    db: Session = Depends(get_db),
) -> OaReplyPackageOut:
    return get_oa_reply_package(db, package_id=package_id)


@router.post(
    "/official-work-packages/{package_id}/oa-reply/refresh",
    response_model=OaReplyPackageOut,
    summary="Refresh OA reply package",
)
def refresh_oa_reply_package_endpoint(
    package_id: str,
    payload: OaReplyRefreshIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> OaReplyPackageOut:
    return refresh_oa_reply_package(
        db,
        package_id=package_id,
        experiment_data_submitted=payload.experiment_data_submitted,
    )


@router.post(
    "/official-work-packages/{package_id}/oa-reply/reply-document",
    response_model=OaReplyPackageOut,
    summary="Link OA reply document",
)
def link_oa_reply_document_endpoint(
    package_id: str,
    payload: OaReplyLinkDocumentIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> OaReplyPackageOut:
    return link_oa_reply_document(
        db,
        package_id=package_id,
        reply_document_id=payload.reply_document_id,
    )


@router.patch(
    "/official-work-packages/{package_id}/oa-reply/checklist/{item_code}",
    response_model=OaReplyChecklistResultOut,
    summary="Update OA reply checklist item",
)
def update_oa_reply_checklist_endpoint(
    package_id: str,
    item_code: str,
    payload: OaReplyChecklistUpdateIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> OaReplyChecklistResultOut:
    checklist = update_oa_reply_checklist(
        db,
        package_id=package_id,
        item_code=item_code,
        status=payload.status,
        evidence_note=payload.evidence_note,
    )
    return OaReplyChecklistResultOut(
        package_id=package_id,
        checklist_item=OfficialWorkPackageChecklistOut.model_validate(
            checklist,
            from_attributes=True,
        ),
    )


@router.post(
    "/cases/{case_id}/official-work-packages/filing-preparation/resolve",
    status_code=status.HTTP_200_OK,
    response_model=FilingPreparationPackageOut,
    summary="Resolve filing preparation package",
)
def resolve_filing_preparation_package_endpoint(
    case_id: UUID,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FilingPreparationPackageOut:
    result = ensure_filing_preparation_package(
        db,
        case_id=str(case_id),
        actor_id=current_user.id,
    )
    db.commit()
    return result


@router.get(
    "/official-work-packages/{package_id}/filing-preparation",
    response_model=FilingPreparationPackageOut,
    summary="Get filing preparation package",
)
def get_filing_preparation_package_endpoint(
    package_id: str,
    _perm: None = Depends(require_perm("OfficialWorkflow.Read")),
    db: Session = Depends(get_db),
) -> FilingPreparationPackageOut:
    return get_filing_preparation_package(db, package_id=package_id)


@router.post(
    "/official-work-packages/{package_id}/filing-preparation/refresh",
    response_model=FilingPreparationPackageOut,
    summary="Refresh filing preparation package",
)
def refresh_filing_preparation_package_endpoint(
    package_id: str,
    payload: FilingPreparationRefreshIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> FilingPreparationPackageOut:
    return refresh_filing_preparation_package(
        db,
        package_id=package_id,
        require_commission_instruction=payload.require_commission_instruction,
    )


@router.patch(
    "/official-work-packages/{package_id}/filing-preparation/checklist/{item_code}",
    response_model=FilingPreparationChecklistResultOut,
    summary="Update filing preparation checklist item",
)
def update_filing_preparation_checklist_endpoint(
    package_id: str,
    item_code: str,
    payload: FilingPreparationChecklistUpdateIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    db: Session = Depends(get_db),
) -> FilingPreparationChecklistResultOut:
    checklist = update_filing_preparation_checklist(
        db,
        package_id=package_id,
        item_code=item_code,
        status=payload.status,
        evidence_note=payload.evidence_note,
    )
    return FilingPreparationChecklistResultOut(
        package_id=package_id,
        checklist_item=OfficialWorkPackageChecklistOut.model_validate(
            checklist,
            from_attributes=True,
        ),
    )


@router.post(
    "/official-work-packages/{package_id}/filing-preparation/external-operations",
    response_model=FilingPreparationChecklistResultOut,
    summary="Record filing preparation external operation",
)
def record_filing_preparation_external_operation_endpoint(
    package_id: str,
    payload: FilingPreparationExternalOperationIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> FilingPreparationChecklistResultOut:
    checklist = record_filing_preparation_external_operation(
        db,
        package_id=package_id,
        operation_code=payload.operation_code,
        occurred_at=payload.occurred_at,
        note=payload.note,
        actor_id=current_user.id,
    )
    return FilingPreparationChecklistResultOut(
        package_id=package_id,
        checklist_item=OfficialWorkPackageChecklistOut.model_validate(
            checklist,
            from_attributes=True,
        ),
    )


@router.get(
    "/official-work-packages/{package_id}/fee-linkage",
    response_model=OfficialFeeLinkageOut,
    summary="Get official work-package fee linkage readiness",
)
def get_official_work_package_fee_linkage(
    package_id: str,
    _perm: None = Depends(require_perm("OfficialWorkflow.Read")),
    db: Session = Depends(get_db),
) -> OfficialFeeLinkageOut:
    return get_official_fee_linkage(db, package_id=package_id)


@router.post(
    "/official-work-packages/{package_id}/receipts",
    status_code=status.HTTP_201_CREATED,
    response_model=OfficialWorkPackageReceiptOut,
    summary="Record official work-package receipt evidence",
)
def create_official_work_package_receipt(
    package_id: str,
    payload: OfficialWorkPackageReceiptCreateIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OfficialWorkPackageReceiptOut:
    receipt = record_official_work_package_receipt(
        db,
        package_id=package_id,
        receipt_kind=payload.receipt_kind,
        receipt_attachment_id=payload.receipt_attachment_id,
        receiving_case_no=payload.receiving_case_no,
        submitter=payload.submitter,
        received_at=payload.received_at,
        received_file_list=payload.received_file_list,
        archive_status=payload.archive_status,
        note=payload.note,
        actor_id=current_user.id,
    )
    return OfficialWorkPackageReceiptOut.model_validate(receipt, from_attributes=True)


@router.post(
    "/official-work-packages/{package_id}/archive",
    response_model=OfficialWorkPackageArchiveResultOut,
    summary="Archive official work package",
)
def archive_official_work_package_endpoint(
    package_id: str,
    payload: OfficialWorkPackageArchiveIn,
    _perm: None = Depends(require_perm("OfficialWorkflow.Update")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OfficialWorkPackageArchiveResultOut:
    package = archive_official_work_package(
        db,
        package_id=package_id,
        actor_id=current_user.id,
        override_reason=payload.override_reason,
        follow_up_owner=payload.follow_up_owner,
        follow_up_due_date=payload.follow_up_due_date,
        follow_up_note=payload.follow_up_note,
    )
    return OfficialWorkPackageArchiveResultOut(
        package=OfficialWorkPackageOut.model_validate(package, from_attributes=True),
        evaluation=evaluate_official_work_package(db, package_id=package_id),
    )
