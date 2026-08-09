from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from app.core.errors import BusinessError

CatalogStatus = Literal["EXECUTABLE", "REFERENCE_ONLY"]
ExecutionBehavior = Literal[
    "ACCEPTANCE_NOTICE",
    "APPLICATION_FEE_NOTICE",
    "FEE_REDUCTION_APPROVAL_NOTICE",
    "OA_REPLY",
    "GRANT_NOTICE",
]

_CATALOG_KIND = "OFFICIAL_NOTICE"
_EXECUTABLE = "EXECUTABLE"
_REFERENCE_ONLY = "REFERENCE_ONLY"
_TECHNICAL_CODES = frozenset({"OA_IN", "GRANT_NOTICE", "ACCEPTANCE_NOTICE"})
_SYSTEM_KEYS = frozenset(
    {
        "catalog_status",
        "execution_behavior",
        "completion_event",
        "archive_status_restore",
        "deadline_source_policy",
        "canonical_template_code",
    }
)
_EXECUTION_KEYS = _SYSTEM_KEYS - {"catalog_status"}


@dataclass(frozen=True, slots=True)
class ResolvedDocumentSemantics:
    catalog_status: CatalogStatus
    execution_behavior: ExecutionBehavior | None
    case_status_effect: str | None
    task_template_code: str | None
    requires_reply: bool
    completion_event: str | None
    archive_status_restore: str | None
    deadline_source_policy: str | None
    fee_trigger: str | None

    @property
    def lifecycle_event_type(self) -> str | None:
        return {
            "ACCEPTANCE_NOTICE": "ACCEPTANCE_NOTICE_RECORDED",
            "OA_REPLY": "OA_NOTICE_RECORDED",
            "GRANT_NOTICE": "GRANT_REGISTRATION_NOTICE_RECORDED",
        }.get(self.execution_behavior)


@dataclass(frozen=True, slots=True)
class _ExecutionContract:
    behavior: ExecutionBehavior
    canonical_code: str
    status_effect: str | None
    task_template_code: str | None
    requires_reply: bool
    completion_event: str | None = None
    archive_status_restore: str | None = None
    deadline_source_policy: str | None = None
    fee_trigger: str | None = None


_ACCEPTANCE = _ExecutionContract(
    behavior="ACCEPTANCE_NOTICE",
    canonical_code="ACCEPTANCE_NOTICE",
    status_effect="ACCEPTED",
    task_template_code=None,
    requires_reply=False,
)
_GRANT = _ExecutionContract(
    behavior="GRANT_NOTICE",
    canonical_code="GRANT_NOTICE",
    status_effect="GRANT_PENDING",
    task_template_code=None,
    requires_reply=False,
    deadline_source_policy="EXPLICIT_OFFICIAL_DUE_REQUIRED",
    fee_trigger="GRANT_FEE",
)
_APPLICATION_FEE_NOTICE = _ExecutionContract(
    behavior="APPLICATION_FEE_NOTICE",
    canonical_code="APPLICATION_FEE_NOTICE",
    status_effect=None,
    task_template_code=None,
    requires_reply=False,
    deadline_source_policy="EXPLICIT_OFFICIAL_DUE_REQUIRED",
    fee_trigger="APPLICATION_FEE",
)
_FEE_REDUCTION_APPROVAL_NOTICE = _ExecutionContract(
    behavior="FEE_REDUCTION_APPROVAL_NOTICE",
    canonical_code="FEE_REDUCTION_APPROVAL_NOTICE",
    status_effect=None,
    task_template_code=None,
    requires_reply=False,
)
_OA_BY_STATUS = {
    status: _ExecutionContract(
        behavior="OA_REPLY",
        canonical_code="OA_IN",
        status_effect=status,
        task_template_code=task_code,
        requires_reply=True,
        completion_event="OFFICIAL_RECEIPT_ARCHIVED",
        archive_status_restore="SUB_EXAM",
        deadline_source_policy="EXPLICIT_OFFICIAL_DUE_REQUIRED",
    )
    for status, task_code in {"OA1": "OA_REPLY", "OA2": "OA_REPLY_SUBSEQUENT"}.items()
}
_TECHNICAL_CONTRACTS = {
    "ACCEPTANCE_NOTICE": _ACCEPTANCE,
    "GRANT_NOTICE": _GRANT,
    "OA_IN": _OA_BY_STATUS["OA1"],
}


def _reference_only() -> ResolvedDocumentSemantics:
    return ResolvedDocumentSemantics(
        catalog_status=_REFERENCE_ONLY,
        execution_behavior=None,
        case_status_effect=None,
        task_template_code=None,
        requires_reply=False,
        completion_event=None,
        archive_status_restore=None,
        deadline_source_policy=None,
        fee_trigger=None,
    )


def _normalized_code(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized.upper() if normalized else None


def _template_code(template: object) -> str:
    return _normalized_code(getattr(template, "code", None)) or "<UNKNOWN>"


def _raise_configuration_error(
    code: str,
    template_code: str,
    *,
    field: str,
    reason: str,
    expected: object = None,
    actual: object = None,
) -> None:
    details = {
        "template_code": template_code,
        "field": field,
        "reason": reason,
        "actual": actual,
    }
    if code == "DOCUMENT_SEMANTICS_CONFLICT":
        details["expected"] = expected
    raise BusinessError(
        code=code,
        message=(
            "Document execution metadata conflicts with template configuration"
            if code == "DOCUMENT_SEMANTICS_CONFLICT"
            else "Document execution metadata is invalid"
        ),
        details=details,
        status_code=409,
    )


def _invalid(
    template_code: str,
    *,
    field: str,
    reason: str,
    actual: object = None,
) -> None:
    _raise_configuration_error(
        "DOCUMENT_SEMANTICS_METADATA_INVALID",
        template_code,
        field=field,
        reason=reason,
        actual=actual,
    )


def _conflict(
    template_code: str,
    *,
    field: str,
    expected: object,
    actual: object,
) -> None:
    _raise_configuration_error(
        "DOCUMENT_SEMANTICS_CONFLICT",
        template_code,
        field=field,
        reason="metadata and direct template configuration disagree",
        expected=expected,
        actual=actual,
    )


def _load_system_metadata(template: object, template_code: str) -> dict[str, Any] | None:
    raw = getattr(template, "input_fields", None)
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    if not isinstance(raw, str):
        if template_code in _TECHNICAL_CODES:
            _invalid(
                template_code,
                field="input_fields",
                reason="input_fields must be JSON text",
                actual=type(raw).__name__,
            )
        return None

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        is_system_owned = (
            template_code in _TECHNICAL_CODES
            or template_code.startswith("OFFICIAL_NOTICE_")
            or any(key in raw for key in _SYSTEM_KEYS)
        )
        if is_system_owned:
            _invalid(
                template_code,
                field="input_fields",
                reason="system metadata must be valid JSON",
                actual=raw,
            )
        return None

    if not isinstance(payload, dict):
        return None
    catalog_kind = _normalized_code(payload.get("catalog_kind"))
    if catalog_kind != _CATALOG_KIND and not any(key in payload for key in _SYSTEM_KEYS):
        return None
    return payload


def _metadata_code(
    metadata: dict[str, Any],
    template_code: str,
    field: str,
) -> str | None:
    value = metadata.get(field)
    if value is None:
        return None
    normalized = _normalized_code(value)
    if normalized is None:
        _invalid(
            template_code,
            field=field,
            reason="metadata value must be a non-empty string or null",
            actual=value,
        )
    return normalized


def _validate_metadata_contract(
    metadata: dict[str, Any],
    template_code: str,
    contract: _ExecutionContract,
) -> None:
    expected_values = {
        "canonical_template_code": contract.canonical_code,
        "completion_event": contract.completion_event,
        "archive_status_restore": contract.archive_status_restore,
        "deadline_source_policy": contract.deadline_source_policy,
    }
    for field, expected in expected_values.items():
        actual = _metadata_code(metadata, template_code, field)
        if expected is not None and actual is None:
            _invalid(
                template_code,
                field=field,
                reason="required execution metadata is missing",
            )
        if actual != expected:
            _conflict(template_code, field=field, expected=expected, actual=actual)


def _direct_code(template: object, template_code: str, field: str) -> str | None:
    raw = getattr(template, field, None)
    if raw is None:
        return None
    normalized = _normalized_code(raw)
    if normalized is None:
        _invalid(
            template_code,
            field=field,
            reason="direct template value must be a non-empty string or null",
            actual=raw,
        )
    return normalized


def _validate_direct_code(
    template: object,
    template_code: str,
    *,
    field: str,
    expected: str | None,
    required: bool,
) -> str | None:
    actual = _direct_code(template, template_code, field)
    if actual is None and required and expected is not None:
        _invalid(
            template_code,
            field=field,
            reason="required direct template field is missing",
        )
    if actual is not None and actual != expected:
        _conflict(template_code, field=field, expected=expected, actual=actual)
    return expected if actual is None else actual


def _validate_direct_bool(
    template: object,
    template_code: str,
    *,
    expected: bool,
    required: bool,
) -> bool:
    actual = getattr(template, "need_reply", None)
    if actual is None:
        if required:
            _invalid(
                template_code,
                field="need_reply",
                reason="required direct template field is missing",
            )
        return expected
    if not isinstance(actual, bool) or actual is not expected:
        _conflict(template_code, field="need_reply", expected=expected, actual=actual)
    return actual


def _validate_reference_only_direct_fields(template: object, template_code: str) -> None:
    for field in (
        "status_effect",
        "status_restore",
        "deadline_template_code",
        "fee_draft_type",
        "reply_to_template_code",
    ):
        actual = _direct_code(template, template_code, field)
        if actual is not None:
            _conflict(template_code, field=field, expected=None, actual=actual)
    if getattr(template, "need_reply", None) is True:
        _conflict(template_code, field="need_reply", expected=False, actual=True)


def _resolve_contract(
    template: object,
    template_code: str,
    contract: _ExecutionContract,
    *,
    direct_fields_required: bool,
) -> ResolvedDocumentSemantics:
    direction = _direct_code(template, template_code, "direction")
    if direction != "IN":
        _conflict(template_code, field="direction", expected="IN", actual=direction)

    status_effect = _validate_direct_code(
        template,
        template_code,
        field="status_effect",
        expected=contract.status_effect,
        required=direct_fields_required,
    )
    task_template_code = _validate_direct_code(
        template,
        template_code,
        field="deadline_template_code",
        expected=contract.task_template_code,
        required=direct_fields_required,
    )
    fee_trigger = _validate_direct_code(
        template,
        template_code,
        field="fee_draft_type",
        expected=contract.fee_trigger,
        required=direct_fields_required,
    )
    _validate_direct_code(
        template,
        template_code,
        field="status_restore",
        expected=contract.archive_status_restore,
        required=False,
    )
    _validate_direct_code(
        template,
        template_code,
        field="reply_to_template_code",
        expected=None,
        required=False,
    )
    requires_reply = _validate_direct_bool(
        template,
        template_code,
        expected=contract.requires_reply,
        required=direct_fields_required,
    )
    return ResolvedDocumentSemantics(
        catalog_status=_EXECUTABLE,
        execution_behavior=contract.behavior,
        case_status_effect=status_effect,
        task_template_code=task_template_code,
        requires_reply=requires_reply,
        completion_event=contract.completion_event,
        archive_status_restore=contract.archive_status_restore,
        deadline_source_policy=contract.deadline_source_policy,
        fee_trigger=fee_trigger,
    )


def _resolve_declared_metadata(
    template: object,
    template_code: str,
    metadata: dict[str, Any],
) -> ResolvedDocumentSemantics:
    if _normalized_code(metadata.get("catalog_kind")) != _CATALOG_KIND:
        return _reference_only()

    catalog_status = _metadata_code(metadata, template_code, "catalog_status")
    has_execution_metadata = any(metadata.get(key) is not None for key in _EXECUTION_KEYS)
    if catalog_status is None:
        if has_execution_metadata:
            _invalid(
                template_code,
                field="catalog_status",
                reason="execution metadata requires catalog_status",
            )
        return _reference_only()
    if catalog_status not in {_EXECUTABLE, _REFERENCE_ONLY}:
        _invalid(
            template_code,
            field="catalog_status",
            reason="unsupported catalog status",
            actual=catalog_status,
        )

    if catalog_status == _REFERENCE_ONLY:
        if has_execution_metadata:
            _conflict(
                template_code,
                field="catalog_status",
                expected="REFERENCE_ONLY without execution metadata",
                actual=metadata,
            )
        _validate_reference_only_direct_fields(template, template_code)
        return _reference_only()

    behavior = _metadata_code(metadata, template_code, "execution_behavior")
    if behavior == "OA_REPLY":
        status_effect = _direct_code(template, template_code, "status_effect")
        if status_effect is None:
            _invalid(
                template_code,
                field="status_effect",
                reason="OA execution requires OA1 or OA2 status_effect",
            )
        if status_effect not in _OA_BY_STATUS:
            _conflict(
                template_code,
                field="status_effect",
                expected="OA1|OA2",
                actual=status_effect,
            )
        contract = _OA_BY_STATUS[status_effect]
    elif behavior == "GRANT_NOTICE":
        contract = _GRANT
    elif behavior == "APPLICATION_FEE_NOTICE":
        contract = _APPLICATION_FEE_NOTICE
    elif behavior == "FEE_REDUCTION_APPROVAL_NOTICE":
        contract = _FEE_REDUCTION_APPROVAL_NOTICE
    elif behavior == "ACCEPTANCE_NOTICE":
        contract = _ACCEPTANCE
    else:
        _invalid(
            template_code,
            field="execution_behavior",
            reason="unsupported or missing execution behavior",
            actual=behavior,
        )

    _validate_metadata_contract(metadata, template_code, contract)
    return _resolve_contract(
        template,
        template_code,
        contract,
        direct_fields_required=True,
    )


def resolve_document_semantics(template: object | None) -> ResolvedDocumentSemantics:
    if template is None:
        return _reference_only()

    template_code = _template_code(template)
    try:
        metadata = _load_system_metadata(template, template_code)
        if metadata is not None:
            return _resolve_declared_metadata(template, template_code, metadata)

        contract = _TECHNICAL_CONTRACTS.get(template_code)
        if contract is None:
            return _reference_only()
        return _resolve_contract(
            template,
            template_code,
            contract,
            direct_fields_required=False,
        )
    except BusinessError as exc:
        if exc.code != "DOCUMENT_SEMANTICS_METADATA_INVALID":
            raise
        return _reference_only()


__all__ = ["ResolvedDocumentSemantics", "resolve_document_semantics"]
