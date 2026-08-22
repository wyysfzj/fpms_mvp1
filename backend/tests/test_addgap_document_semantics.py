from __future__ import annotations

import importlib
import json
from dataclasses import FrozenInstanceError, asdict
from types import SimpleNamespace

import pytest

from app.core.errors import BusinessError


def _template(**overrides) -> SimpleNamespace:
    values = {
        "code": "CLIENT_IN",
        "name": "客户来函",
        "direction": "IN",
        "status_effect": None,
        "status_restore": None,
        "deadline_template_code": None,
        "fee_draft_type": None,
        "need_reply": False,
        "reply_to_template_code": None,
        "input_fields": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _resolve(template: SimpleNamespace):
    module = importlib.import_module("app.modules.documents.semantics")
    return module.resolve_document_semantics(template)


def _metadata(**overrides) -> str:
    values = {
        "catalog_kind": "OFFICIAL_NOTICE",
        "catalog_status": "EXECUTABLE",
        "execution_behavior": "OA_REPLY",
        "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
        "archive_status_restore": "SUB_EXAM",
        "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
        "canonical_template_code": "OA_IN",
        "source": "customer-source",
    }
    values.update(overrides)
    return json.dumps(values, ensure_ascii=False)


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        (
            _template(
                code="OA_IN",
                name="任意显示名称",
                need_reply=True,
                status_effect="OA1",
                deadline_template_code="OA_REPLY",
                input_fields='[{"name":"official_due_date","type":"date"}]',
            ),
            {
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "OA_REPLY",
                "case_status_effect": "OA1",
                "task_template_code": "OA_REPLY",
                "requires_reply": True,
                "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                "archive_status_restore": "SUB_EXAM",
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "fee_trigger": None,
            },
        ),
        (
            _template(
                code="GRANT_NOTICE",
                status_effect="GRANT_PENDING",
                fee_draft_type="GRANT_FEE",
            ),
            {
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "GRANT_NOTICE",
                "case_status_effect": "GRANT_PENDING",
                "task_template_code": None,
                "requires_reply": False,
                "completion_event": None,
                "archive_status_restore": None,
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "fee_trigger": "GRANT_FEE",
            },
        ),
        (
            _template(code="ACCEPTANCE_NOTICE", status_effect="ACCEPTED"),
            {
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "ACCEPTANCE_NOTICE",
                "case_status_effect": "ACCEPTED",
                "task_template_code": None,
                "requires_reply": False,
                "completion_event": None,
                "archive_status_restore": None,
                "deadline_source_policy": None,
                "fee_trigger": None,
            },
        ),
    ],
)
def test_exact_technical_codes_use_narrow_backward_compatible_fallbacks(
    template: SimpleNamespace,
    expected: dict[str, object],
) -> None:
    assert asdict(_resolve(template)) == expected


def test_display_name_and_direct_fields_never_infer_executable_semantics() -> None:
    result = _resolve(
        _template(
            code="CUSTOM_NOTICE",
            name="授权通知书",
            status_effect="GRANT_PENDING",
            fee_draft_type="GRANT_FEE",
        )
    )

    assert asdict(result) == {
        "catalog_status": "REFERENCE_ONLY",
        "execution_behavior": None,
        "case_status_effect": None,
        "task_template_code": None,
        "requires_reply": False,
        "completion_event": None,
        "archive_status_restore": None,
        "deadline_source_policy": None,
        "fee_trigger": None,
    }


def test_existing_official_catalog_metadata_without_status_is_reference_only() -> None:
    result = _resolve(
        _template(
            code="OFFICIAL_NOTICE_003",
            name="第一次审查意见通知书",
            input_fields=json.dumps(
                {
                    "catalog_kind": "OFFICIAL_NOTICE",
                    "official_notice_name": "第一次审查意见通知书",
                    "official_doc_codes": ["210401", "210402"],
                    "source": "相关流程操作-20260526.docx",
                },
                ensure_ascii=False,
            ),
        )
    )

    assert result.catalog_status == "REFERENCE_ONLY"
    assert result.execution_behavior is None
    assert result.case_status_effect is None


@pytest.mark.parametrize(
    ("status_effect", "task_template_code"),
    [("OA1", "OA_REPLY"), ("OA2", "OA_REPLY_SUBSEQUENT")],
)
def test_declared_oa_alias_resolves_from_system_metadata_and_direct_fields(
    status_effect: str,
    task_template_code: str,
) -> None:
    result = _resolve(
        _template(
            code="OFFICIAL_NOTICE_ALIAS",
            name="不参与解析的显示名称",
            status_effect=status_effect,
            deadline_template_code=task_template_code,
            need_reply=True,
            input_fields=_metadata(),
        )
    )

    assert result.catalog_status == "EXECUTABLE"
    assert result.execution_behavior == "OA_REPLY"
    assert result.case_status_effect == status_effect
    assert result.task_template_code == task_template_code
    assert result.requires_reply is True


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        (
            _template(
                code="OFFICIAL_NOTICE_GRANT_ALIAS",
                status_effect="GRANT_PENDING",
                fee_draft_type="GRANT_FEE",
                input_fields=_metadata(
                    execution_behavior="GRANT_NOTICE",
                    completion_event=None,
                    archive_status_restore=None,
                    canonical_template_code="GRANT_NOTICE",
                ),
            ),
            {
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "GRANT_NOTICE",
                "case_status_effect": "GRANT_PENDING",
                "task_template_code": None,
                "requires_reply": False,
                "completion_event": None,
                "archive_status_restore": None,
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "fee_trigger": "GRANT_FEE",
            },
        ),
        (
            _template(
                code="OFFICIAL_NOTICE_ACCEPTANCE_ALIAS",
                status_effect="ACCEPTED",
                input_fields=_metadata(
                    execution_behavior="ACCEPTANCE_NOTICE",
                    completion_event=None,
                    archive_status_restore=None,
                    deadline_source_policy=None,
                    canonical_template_code="ACCEPTANCE_NOTICE",
                ),
            ),
            {
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "ACCEPTANCE_NOTICE",
                "case_status_effect": "ACCEPTED",
                "task_template_code": None,
                "requires_reply": False,
                "completion_event": None,
                "archive_status_restore": None,
                "deadline_source_policy": None,
                "fee_trigger": None,
            },
        ),
    ],
)
def test_declared_grant_and_acceptance_aliases_resolve_complete_contracts(
    template: SimpleNamespace,
    expected: dict[str, object],
) -> None:
    assert asdict(_resolve(template)) == expected


@pytest.mark.parametrize(
    "template",
    [
        _template(code="OA_IN", input_fields="{"),
        _template(
            code="OFFICIAL_NOTICE_001",
            input_fields=_metadata(catalog_status="ACTIVE"),
        ),
        _template(
            code="OFFICIAL_NOTICE_001",
            input_fields=_metadata(catalog_status=None),
        ),
        _template(
            code="OFFICIAL_NOTICE_001",
            input_fields=_metadata(execution_behavior=None),
        ),
        _template(
            code="OFFICIAL_NOTICE_001",
            input_fields=_metadata(execution_behavior="UNCONFIRMED_BEHAVIOR"),
        ),
    ],
)
def test_malformed_incomplete_or_unknown_metadata_is_non_executable(
    template: SimpleNamespace,
) -> None:
    result = _resolve(template)

    assert result.catalog_status == "REFERENCE_ONLY"
    assert result.execution_behavior is None
    assert result.case_status_effect is None


@pytest.mark.parametrize(
    "template",
    [
        _template(
            code="OFFICIAL_NOTICE_003",
            status_effect="GRANT_PENDING",
            deadline_template_code="OA_REPLY",
            need_reply=True,
            input_fields=_metadata(),
        ),
        _template(
            code="OFFICIAL_NOTICE_003",
            status_effect="OA1",
            deadline_template_code="GRANT_FEE",
            need_reply=True,
            input_fields=_metadata(),
        ),
        _template(
            code="OFFICIAL_NOTICE_003",
            status_effect="OA1",
            deadline_template_code="OA_REPLY",
            need_reply=True,
            input_fields=_metadata(canonical_template_code="GRANT_NOTICE"),
        ),
        _template(
            code="OFFICIAL_NOTICE_003",
            status_effect="OA1",
            status_restore="WRONG_STATUS",
            deadline_template_code="OA_REPLY",
            need_reply=True,
            input_fields=_metadata(),
        ),
        _template(
            code="OFFICIAL_NOTICE_003",
            status_effect="OA1",
            deadline_template_code="OA_REPLY",
            need_reply=True,
            reply_to_template_code="OA_IN",
            input_fields=_metadata(),
        ),
        _template(
            code="OFFICIAL_NOTICE_003",
            status_effect="OA1",
            input_fields=_metadata(
                catalog_status="REFERENCE_ONLY",
                execution_behavior=None,
                completion_event=None,
                archive_status_restore=None,
                deadline_source_policy=None,
                canonical_template_code=None,
            ),
        ),
    ],
)
def test_conflicting_direct_and_system_metadata_returns_configuration_error(
    template: SimpleNamespace,
) -> None:
    with pytest.raises(BusinessError) as exc_info:
        _resolve(template)

    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "DOCUMENT_SEMANTICS_CONFLICT"


def test_resolved_semantics_value_is_immutable() -> None:
    result = _resolve(_template(code="ACCEPTANCE_NOTICE", status_effect="ACCEPTED"))

    with pytest.raises(FrozenInstanceError):
        result.case_status_effect = "OA1"
