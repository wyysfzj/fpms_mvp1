from __future__ import annotations

from datetime import datetime
from typing import Callable, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.errors import BusinessError
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.system.decision_gate_schemas import (
    DecisionGateAuditOut,
    DecisionGateRecordIn,
    DecisionGateRecordOut,
)
from app.modules.system.decision_gate_service import (
    DecisionGateRecordDisposition,
    RecordDecisionGateCommand,
    record_decision_gate,
)
from app.modules.system.grant_evidence_source_schemas import (
    ActivateGrantEvidenceSourceIn,
    GrantEvidenceSourceConfigOut,
    GrantEvidenceSourceRecordOut,
    PublishGrantEvidenceSourceConfigIn,
    RegisterGrantEvidenceSourceIn,
    RetireGrantEvidenceSourceIn,
    ReviewGrantEvidenceSourceIn,
    RevokeGrantEvidenceSourceConfigIn,
)
from app.modules.system.grant_evidence_source_service import (
    ActivateGrantEvidenceSourceCommand,
    GrantEvidenceSourceDisposition,
    PublishGrantEvidenceSourceConfigCommand,
    RegisterGrantEvidenceSourceCommand,
    RetireGrantEvidenceSourceCommand,
    ReviewGrantEvidenceSourceCommand,
    RevokeGrantEvidenceSourceConfigCommand,
    activate_grant_evidence_source,
    publish_grant_evidence_source_config,
    register_grant_evidence_source,
    retire_grant_evidence_source,
    review_grant_evidence_source,
    revoke_grant_evidence_source_config,
)
from app.modules.system.grant_manual_review_role_schemas import (
    GrantManualReviewRoleConfigOut,
    PublishGrantManualReviewRoleConfigIn,
    RevokeGrantManualReviewRoleConfigIn,
)
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleDisposition,
    PublishGrantManualReviewRoleConfigCommand,
    RevokeGrantManualReviewRoleConfigCommand,
    publish_grant_manual_review_role_config,
    revoke_grant_manual_review_role_config,
)
from app.modules.system.models import CustomerDecisionGate
from app.modules.system.schemas import (
    ConfigReadinessOut,
    OkOut,
    SystemParamListItemOut,
    SystemParamUpsertIn,
)
from app.modules.system.service import (
    build_config_readiness,
    list_system_params,
    mask_secret_param_value,
)
from app.modules.system.service import (
    upsert_system_param as upsert_system_param_service,
)

router = APIRouter()
_SourceMutationResult = TypeVar("_SourceMutationResult")


def _utc_now() -> datetime:
    return datetime.utcnow()


def _commit_source_mutation(
    db: Session,
    operation: Callable[[], _SourceMutationResult],
) -> _SourceMutationResult:
    try:
        result = operation()
    except Exception:
        db.rollback()
        raise
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.get("/system/params", summary="List system parameters")
def get_system_params(
    _perm: None = Depends(require_perm("SystemParam.Read")),
    db: Session = Depends(get_db),
) -> list[SystemParamListItemOut]:
    """
    List system parameters (secrets are masked).

    **Auth**: Bearer JWT
    **Permission**: SystemParam.Read
    **Request example**:
    `GET /api/v1/system/params`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/system/params \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of system params
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    params = list_system_params(db)
    return [
        SystemParamListItemOut(
            param_key=param.param_key,
            param_value=mask_secret_param_value(param),
            value_type=param.value_type,
            description=param.description,
            is_secret=param.is_secret,
            updated_at=param.updated_at,
            created_at=param.created_at,
        )
        for param in params
    ]


@router.get(
    "/system/config-readiness",
    response_model=ConfigReadinessOut,
    summary="Audit system configuration readiness",
)
def get_config_readiness(
    _perm: None = Depends(require_perm("SystemParam.Read")),
    db: Session = Depends(get_db),
) -> ConfigReadinessOut:
    """
    Read-only audit for seed/config readiness.

    **Auth**: Bearer JWT
    **Permission**: SystemParam.Read
    **Request example**:
    `GET /api/v1/system/config-readiness`
    **Responses**:
    - 200: Current config readiness counts and missing hard blockers
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    """
    return ConfigReadinessOut.model_validate(build_config_readiness(db))


@router.put(
    "/system/params/{param_key}",
    response_model=OkOut,
    summary="Upsert a system parameter",
)
def upsert_system_param(
    param_key: str,
    payload: SystemParamUpsertIn,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> OkOut:
    """
    Create or update a system parameter by key.

    **Auth**: Bearer JWT
    **Permission**: SystemParam.Edit
    **Request example**:
    ```json
    {"param_value": "templates/bill.docx", "value_type": "string", "is_secret": false}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/system/params/bill_template_path \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"param_value":"templates/bill.docx","value_type":"string","is_secret":false}'
    ```
    **Responses**:
    - 200: Parameter upserted
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    upsert_system_param_service(
        db,
        param_key=param_key,
        data=payload,
        actor_id=current_user.id,
    )
    return OkOut()


@router.get(
    "/system/decision-gates",
    response_model=list[DecisionGateAuditOut],
    summary="List customer decision gate audit history",
)
def list_decision_gate_audit(
    _perm: None = Depends(require_perm("SystemParam.Read")),
    db: Session = Depends(get_db),
) -> list[DecisionGateAuditOut]:
    with db.no_autoflush:
        rows = (
            db.execute(
                select(
                    CustomerDecisionGate.id.label("gate_id"),
                    CustomerDecisionGate.gate_code,
                    CustomerDecisionGate.scope_key,
                    CustomerDecisionGate.decision_value,
                    CustomerDecisionGate.decision_status,
                    CustomerDecisionGate.source_reference,
                    CustomerDecisionGate.source_version,
                    CustomerDecisionGate.confirmed_by,
                    CustomerDecisionGate.effective_at,
                    CustomerDecisionGate.recorded_at,
                    CustomerDecisionGate.supersedes_gate_id,
                    CustomerDecisionGate.current_identity_key,
                ).order_by(
                    CustomerDecisionGate.recorded_at.asc(),
                    CustomerDecisionGate.id.asc(),
                )
            )
            .mappings()
            .all()
        )
    return [DecisionGateAuditOut.model_validate(row) for row in rows]


@router.post(
    "/system/decision-gates",
    response_model=DecisionGateRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a customer decision gate",
)
def create_decision_gate_record(
    payload: DecisionGateRecordIn,
    response: Response,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> DecisionGateRecordOut:
    command = RecordDecisionGateCommand(
        gate_code=payload.gate_code,
        scope_key=payload.scope_key,
        decision_value=payload.decision_value,
        decision_status=payload.decision_status,
        source_reference=payload.source_reference,
        source_version=payload.source_version,
        confirmed_by=current_user.id,
        effective_at=payload.effective_at,
        idempotency_key=payload.idempotency_key,
        expected_current_gate_id=payload.expected_current_gate_id,
    )
    try:
        result = record_decision_gate(command, db)
    except BusinessError:
        db.rollback()
        raise

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    response.status_code = (
        status.HTTP_201_CREATED
        if result.disposition is DecisionGateRecordDisposition.CREATED
        else status.HTTP_200_OK
    )
    return DecisionGateRecordOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-evidence-sources",
    response_model=GrantEvidenceSourceRecordOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grant_evidence_source(
    payload: RegisterGrantEvidenceSourceIn,
    response: Response,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantEvidenceSourceRecordOut:
    result = _commit_source_mutation(
        db,
        lambda: register_grant_evidence_source(
            RegisterGrantEvidenceSourceCommand(
                source_code=payload.source_code,
                source_version=payload.source_version,
                evidence_scope=payload.evidence_scope,
                source_reference_kind=payload.source_reference_kind,
                source_reference_value=payload.source_reference_value,
                acquisition_method=payload.acquisition_method,
                effective_from=payload.effective_from,
                effective_to=payload.effective_to,
                supersedes_source_id=payload.supersedes_source_id,
                actor_id=current_user.id,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        ),
    )
    response.status_code = (
        status.HTTP_201_CREATED
        if result.disposition is GrantEvidenceSourceDisposition.CREATED
        else status.HTTP_200_OK
    )
    return GrantEvidenceSourceRecordOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-evidence-sources/{source_record_id}/review",
    response_model=GrantEvidenceSourceRecordOut,
)
def review_grant_evidence_source_record(
    source_record_id: UUID,
    payload: ReviewGrantEvidenceSourceIn,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantEvidenceSourceRecordOut:
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: review_grant_evidence_source(
            ReviewGrantEvidenceSourceCommand(
                source_record_id=str(source_record_id),
                decision=payload.decision,
                reviewer_id=current_user.id,
                reviewed_at=now,
                reason=payload.reason,
            ),
            db,
        ),
    )
    return GrantEvidenceSourceRecordOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-evidence-sources/{source_record_id}/activate",
    response_model=GrantEvidenceSourceRecordOut,
)
def activate_grant_evidence_source_record(
    source_record_id: UUID,
    payload: ActivateGrantEvidenceSourceIn,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantEvidenceSourceRecordOut:
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: activate_grant_evidence_source(
            ActivateGrantEvidenceSourceCommand(
                source_record_id=str(source_record_id),
                actor_id=current_user.id,
                activated_at=now,
                expected_current_source_id=payload.expected_current_source_id,
            ),
            db,
        ),
    )
    return GrantEvidenceSourceRecordOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-evidence-sources/{source_record_id}/retire",
    response_model=GrantEvidenceSourceRecordOut,
)
def retire_grant_evidence_source_record(
    source_record_id: UUID,
    payload: RetireGrantEvidenceSourceIn,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantEvidenceSourceRecordOut:
    source_id = str(source_record_id)
    if payload.expected_current_source_id != source_id:
        raise BusinessError(
            code="VALIDATION_ERROR",
            message="Path and body source IDs differ",
            status_code=422,
        )
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: retire_grant_evidence_source(
            RetireGrantEvidenceSourceCommand(
                source_record_id=source_id,
                actor_id=current_user.id,
                retired_at=now,
                expected_current_source_id=payload.expected_current_source_id,
            ),
            db,
        ),
    )
    return GrantEvidenceSourceRecordOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-evidence-source-configurations",
    response_model=GrantEvidenceSourceConfigOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grant_evidence_source_configuration(
    payload: PublishGrantEvidenceSourceConfigIn,
    response: Response,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantEvidenceSourceConfigOut:
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: publish_grant_evidence_source_config(
            PublishGrantEvidenceSourceConfigCommand(
                evidence_scope=payload.evidence_scope,
                source_record_id=payload.source_record_id,
                config_version=payload.config_version,
                effective_from=payload.effective_from,
                effective_to=payload.effective_to,
                selected_by=current_user.id,
                published_at=now,
                selection_reason=payload.selection_reason,
                expected_current_config_id=payload.expected_current_config_id,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        ),
    )
    response.status_code = (
        status.HTTP_201_CREATED
        if result.disposition is GrantEvidenceSourceDisposition.CREATED
        else status.HTTP_200_OK
    )
    return GrantEvidenceSourceConfigOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-evidence-source-configurations/{config_id}/revoke",
    response_model=GrantEvidenceSourceConfigOut,
    status_code=status.HTTP_201_CREATED,
)
def revoke_grant_evidence_source_configuration(
    config_id: UUID,
    payload: RevokeGrantEvidenceSourceConfigIn,
    response: Response,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantEvidenceSourceConfigOut:
    if payload.expected_current_config_id != str(config_id):
        raise BusinessError(
            code="VALIDATION_ERROR",
            message="Path and body config IDs differ",
            status_code=422,
        )
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: revoke_grant_evidence_source_config(
            RevokeGrantEvidenceSourceConfigCommand(
                evidence_scope=payload.evidence_scope,
                config_version=payload.config_version,
                effective_from=payload.effective_from,
                selected_by=current_user.id,
                published_at=now,
                selection_reason=payload.selection_reason,
                expected_current_config_id=payload.expected_current_config_id,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        ),
    )
    response.status_code = (
        status.HTTP_201_CREATED
        if result.disposition is GrantEvidenceSourceDisposition.CREATED
        else status.HTTP_200_OK
    )
    return GrantEvidenceSourceConfigOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-manual-review-role-configurations",
    response_model=GrantManualReviewRoleConfigOut,
    status_code=status.HTTP_201_CREATED,
)
def create_grant_manual_review_role_configuration(
    payload: PublishGrantManualReviewRoleConfigIn,
    response: Response,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantManualReviewRoleConfigOut:
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: publish_grant_manual_review_role_config(
            PublishGrantManualReviewRoleConfigCommand(
                official_copy_acquirer_role_id=payload.official_copy_acquirer_role_id,
                first_verifier_role_id=payload.first_verifier_role_id,
                second_verifier_role_id=payload.second_verifier_role_id,
                manual_review_proposer_role_id=payload.manual_review_proposer_role_id,
                manual_review_second_reviewer_role_id=(
                    payload.manual_review_second_reviewer_role_id
                ),
                config_version=payload.config_version,
                effective_from=payload.effective_from,
                effective_to=payload.effective_to,
                confirmed_by=current_user.id,
                published_at=now,
                expected_current_config_id=payload.expected_current_config_id,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        ),
    )
    response.status_code = (
        status.HTTP_201_CREATED
        if result.disposition is GrantManualReviewRoleDisposition.CREATED
        else status.HTTP_200_OK
    )
    return GrantManualReviewRoleConfigOut.model_validate(result, from_attributes=True)


@router.post(
    "/system/grant-manual-review-role-configurations/{config_id}/revoke",
    response_model=GrantManualReviewRoleConfigOut,
    status_code=status.HTTP_201_CREATED,
)
def revoke_grant_manual_review_role_configuration(
    config_id: UUID,
    payload: RevokeGrantManualReviewRoleConfigIn,
    response: Response,
    _perm: None = Depends(require_perm("SystemParam.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> GrantManualReviewRoleConfigOut:
    if payload.expected_current_config_id != str(config_id):
        raise BusinessError(
            code="VALIDATION_ERROR",
            message="Path and body config IDs differ",
            status_code=422,
        )
    now = _utc_now()
    result = _commit_source_mutation(
        db,
        lambda: revoke_grant_manual_review_role_config(
            RevokeGrantManualReviewRoleConfigCommand(
                config_version=payload.config_version,
                effective_from=payload.effective_from,
                confirmed_by=current_user.id,
                published_at=now,
                expected_current_config_id=payload.expected_current_config_id,
                idempotency_key=payload.idempotency_key,
            ),
            db,
        ),
    )
    response.status_code = (
        status.HTTP_201_CREATED
        if result.disposition is GrantManualReviewRoleDisposition.CREATED
        else status.HTTP_200_OK
    )
    return GrantManualReviewRoleConfigOut.model_validate(result, from_attributes=True)
