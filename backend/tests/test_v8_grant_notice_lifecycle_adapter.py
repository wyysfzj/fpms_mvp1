from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventEvidence,
)
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.documents.service import _advance_grant_notice_case_after_attachment
from app.modules.fees.models import T_GrantFeeTask
from app.modules.grant_fees import service as grant_fee_service

_CONTENT_HASH = f"sha256:{'a' * 64}"
_REVIEWED_AT = datetime(2026, 7, 27, 9, 30)
_RECORDED_AT = datetime(2026, 7, 27, 10, 0)
_DEADLINE_CONFIRMED_AT = datetime(2026, 7, 26, 16, 0)
_IDEMPOTENCY_PREFIX = "grant-registration-notice:"


def _dispatch_public(**kwargs):
    assert hasattr(grant_fee_service, "dispatch_grant_registration_notice")
    return grant_fee_service.dispatch_grant_registration_notice(**kwargs)


def _grant_extra_data() -> str:
    return json.dumps(
        {
            "OfficialDueDate": "2026-09-27",
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
            "GrantFeeLines": [
                {
                    "fee_name": "授权当年年费",
                    "year": 1,
                    "amount": "900.00",
                    "reduction_ratio": "0.85",
                }
            ],
        },
        ensure_ascii=False,
    )


@pytest.mark.parametrize(
    ("helper_name", "expected_code", "expected_message"),
    (
        (
            "_grant_notice_invalid",
            "GRANT_NOTICE_LIFECYCLE_INVALID",
            "办理登记手续通知书生命周期输入无效",
        ),
        (
            "_grant_notice_source_conflict",
            "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT",
            "办理登记手续通知书生命周期来源不一致",
        ),
        (
            "_grant_notice_hash_conflict",
            "GRANT_NOTICE_EVIDENCE_HASH_CONFLICT",
            "办理登记手续通知书证据哈希不匹配",
        ),
        (
            "_grant_notice_fee_lines_conflict",
            "GRANT_NOTICE_FEE_LINES_CONFLICT",
            "办理登记手续通知书费用明细不一致",
        ),
        (
            "_grant_notice_replacement_conflict",
            "GRANT_NOTICE_REPLACEMENT_LINEAGE_CONFLICT",
            "办理登记手续通知书替换谱系不一致",
        ),
        (
            "_grant_notice_idempotency_conflict",
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            "生命周期幂等键与已存活动冲突",
        ),
    ),
)
def test_grant_notice_domain_errors_use_simplified_chinese(
    helper_name: str,
    expected_code: str,
    expected_message: str,
) -> None:
    with pytest.raises(BusinessError) as caught:
        getattr(grant_fee_service, helper_name)()

    assert caught.value.code == expected_code
    assert caught.value.message == expected_message


def _grant_template(db: Session) -> DocTemplate:
    return db.execute(select(DocTemplate).where(DocTemplate.code == "GRANT_NOTICE")).scalar_one()


def _grant_fixture(
    db: Session,
    *,
    label: str,
) -> tuple[Case, Document, T_GrantFeeTask, DocumentEvidenceVersion]:
    case = Case(
        id=str(uuid4()),
        case_no=f"V8-GRANT-ADAPTER-{label}-{uuid4().hex[:8].upper()}",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        status="SUB_EXAM",
        business_stage="PROSECUTION_MANAGEMENT",
        official_procedure_stage="SUBSTANTIVE_EXAMINATION",
        legal_status="APPLICATION_PENDING",
        lifecycle_verification_status="CONFIRMED",
        lifecycle_revision=0,
    )
    document = Document(
        id=str(uuid4()),
        case_id=case.id,
        doc_template_id=_grant_template(db).id,
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date=date(2026, 7, 27),
        title="办理登记手续通知书",
        extra_data=_grant_extra_data(),
    )
    task = T_GrantFeeTask(
        id=str(uuid4()),
        case_id=case.id,
        type="GRANT",
        due_date=date(2026, 9, 27),
        source_document_id=document.id,
        deadline_source="MANUAL_OFFICIAL_NOTICE",
        deadline_confirmed_at=_DEADLINE_CONFIRMED_AT,
        currency="CNY",
    )
    attachment = DocAttachment(
        id=str(uuid4()),
        document_id=document.id,
        file_name="grant-notice.pdf",
        file_path=f"attachments/{document.id}/grant-notice.pdf",
        mime_type="application/pdf",
        file_size=1024,
        content_hash=_CONTENT_HASH,
    )
    lineage_key = f"attachment:{attachment.id}"
    evidence = DocumentEvidenceVersion(
        id=str(uuid4()),
        case_id=case.id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=lineage_key,
        role="RAW_ATTACHMENT",
        version_number=1,
        state="FINAL",
        creator_id=str(uuid4()),
        review_state="APPROVED",
        reviewer_id=str(uuid4()),
        reviewed_at=_REVIEWED_AT,
        content_hash=_CONTENT_HASH,
        current_identity_key=f"{case.id}|{lineage_key}",
    )
    db.add(case)
    db.flush()
    db.add(document)
    db.flush()
    db.add(task)
    db.add(attachment)
    db.flush()
    db.add(evidence)
    db.flush()
    return case, document, task, evidence


def _dispatch(
    db: Session,
    *,
    task: T_GrantFeeTask,
    document: Document,
    evidence: DocumentEvidenceVersion,
    idempotency_key: str,
):
    return _dispatch_public(
        grant_fee_task_id=task.id,
        source_document_id=document.id,
        reviewed_evidence_version_id=evidence.id,
        expected_content_hash=evidence.content_hash,
        actor_id=str(uuid4()),
        recorded_at=_RECORDED_AT,
        idempotency_key=idempotency_key,
        transaction=db,
    )


def _dispatch_call(
    db: Session,
    *,
    task: T_GrantFeeTask,
    document: Document,
    evidence: DocumentEvidenceVersion,
    actor_id: str,
    recorded_at: datetime,
    idempotency_key: str,
) -> dict[str, object]:
    return {
        "grant_fee_task_id": task.id,
        "source_document_id": document.id,
        "reviewed_evidence_version_id": evidence.id,
        "expected_content_hash": evidence.content_hash,
        "actor_id": actor_id,
        "recorded_at": recorded_at,
        "idempotency_key": idempotency_key,
        "transaction": db,
    }


def _replacement_fixture(
    db: Session,
    *,
    case: Case,
    predecessor_task: T_GrantFeeTask,
    label: str,
) -> tuple[Document, T_GrantFeeTask, DocumentEvidenceVersion]:
    document = Document(
        id=str(uuid4()),
        case_id=case.id,
        doc_template_id=_grant_template(db).id,
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date=date(2026, 7, 28),
        title=f"更正办理登记手续通知书-{label}",
        extra_data=_grant_extra_data(),
    )
    task = T_GrantFeeTask(
        id=str(uuid4()),
        case_id=case.id,
        type="GRANT",
        due_date=date(2026, 10, 8),
        source_document_id=document.id,
        deadline_source="CORRECTED_OFFICIAL_NOTICE",
        deadline_confirmed_at=datetime(2026, 7, 28, 9, 0),
        currency="CNY",
    )
    attachment = DocAttachment(
        id=str(uuid4()),
        document_id=document.id,
        file_name=f"grant-notice-correction-{label}.pdf",
        file_path=f"attachments/{document.id}/grant-notice-correction.pdf",
        content_hash=_CONTENT_HASH,
    )
    lineage_key = f"attachment:{attachment.id}"
    evidence = DocumentEvidenceVersion(
        id=str(uuid4()),
        case_id=case.id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=lineage_key,
        role="RAW_ATTACHMENT",
        version_number=1,
        state="FINAL",
        creator_id=str(uuid4()),
        review_state="APPROVED",
        reviewer_id=str(uuid4()),
        reviewed_at=datetime(2026, 7, 28, 9, 30),
        content_hash=_CONTENT_HASH,
        current_identity_key=f"{case.id}|{lineage_key}",
    )
    db.add(document)
    db.flush()
    db.add(task)
    db.flush()
    predecessor_task.superseded_by_task_id = task.id
    db.add(attachment)
    db.flush()
    db.add(evidence)
    db.flush()
    return document, task, evidence


def _activity_count(db: Session, case_id: str) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        )
        or 0
    )


def test_valid_notice_is_the_only_dispatch_and_exact_replay_is_write_free(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label="INITIAL")
        actor_id = str(uuid4())
        call = {
            "grant_fee_task_id": task.id,
            "source_document_id": document.id,
            "reviewed_evidence_version_id": evidence.id,
            "expected_content_hash": evidence.content_hash,
            "actor_id": actor_id,
            "recorded_at": _RECORDED_AT,
            "idempotency_key": "initial-notice",
            "transaction": db,
        }
        case.app_no = "CN2026000001"
        case.filing_date = date(2026, 1, 2)
        case.pub_no = "CN123456789A"
        case.pub_date = date(2026, 6, 1)
        case.grant_no = "CN123456789B"
        case.grant_date = date(2026, 7, 1)
        case.first_annuity_year = 1
        case.valid_until = date(2046, 1, 2)
        db.flush()

        first = _dispatch_public(**call)
        db.flush()
        activity = db.get(CaseActivityEvent, first.activity_id)
        assert activity is not None
        payload = json.loads(activity.payload_json)
        evidence_rows = db.scalars(
            select(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == activity.id)
            .order_by(CaseActivityEventEvidence.evidence_kind)
        ).all()
        assert first.reused is False
        assert first.lifecycle_revision == 1
        assert _activity_count(db, case.id) == 1
        assert set(payload) == {
            "schema",
            "case_id",
            "grant_fee_task_id",
            "source_document_id",
            "reviewed_evidence_version_id",
            "reviewed_evidence_content_hash",
            "reviewed_at",
            "grant_fee_lines_schema",
            "grant_fee_lines_snapshot",
            "grant_fee_lines_snapshot_hash",
            "due_date",
            "deadline_source",
            "deadline_confirmed_at",
            "predecessor_grant_fee_task_id",
            "supersedes_activity_id",
        }
        assert payload["schema"] == "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V1"
        assert payload["grant_fee_task_id"] == task.id
        assert payload["source_document_id"] == document.id
        assert payload["reviewed_evidence_version_id"] == evidence.id
        assert payload["reviewed_evidence_content_hash"] == evidence.content_hash
        assert payload["reviewed_at"] == _REVIEWED_AT.isoformat()
        assert payload["grant_fee_lines_schema"] == "FPMS_GRANT_NOTICE_FEE_LINES_V1"
        snapshot = payload["grant_fee_lines_snapshot"]
        assert type(snapshot) is str
        assert (
            payload["grant_fee_lines_snapshot_hash"]
            == hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
        )
        assert payload["due_date"] == task.due_date.isoformat()
        assert payload["deadline_source"] == task.deadline_source
        assert payload["deadline_confirmed_at"] == _DEADLINE_CONFIRMED_AT.isoformat()
        assert payload["predecessor_grant_fee_task_id"] is None
        assert payload["supersedes_activity_id"] is None
        assert activity.source_activity_id is None
        assert activity.supersedes_event_id is None
        assert [row.evidence_kind for row in evidence_rows] == [
            "DOCUMENT_EVIDENCE_VERSION",
            "SOURCE_DOCUMENT",
        ]
        assert {row.content_hash for row in evidence_rows} == {evidence.content_hash}
        assert {row.captured_at for row in evidence_rows} == {_REVIEWED_AT}

        replay = _dispatch_public(**call)
        _advance_grant_notice_case_after_attachment(db, document=document)
        db.flush()
        assert replay.reused is True
        assert replay.activity_id == first.activity_id
        assert _activity_count(db, case.id) == 1
        assert db.get(Case, case.id).lifecycle_revision == 1


@pytest.mark.parametrize(
    ("target", "field", "replacement"),
    [
        ("payload", "grant_fee_lines_snapshot", "{}"),
        ("payload", "grant_fee_lines_snapshot_hash", "b" * 64),
        ("payload", "due_date", "2026-09-28"),
        ("payload", "deadline_source", "OTHER_SOURCE"),
        ("payload", "deadline_confirmed_at", "2026-07-26T16:01:00"),
        ("payload", "predecessor_grant_fee_task_id", "unexpected-predecessor"),
        ("payload", "supersedes_activity_id", "unexpected-activity"),
        ("activity", "source_activity_id", "SELF"),
        ("activity", "supersedes_event_id", "SELF"),
    ],
)
def test_replay_rejects_tampered_immutable_payload_or_lineage_column(
    session_factory: sessionmaker,
    target: str,
    field: str,
    replacement: str,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label=f"REPLAY-{field}")
        call = _dispatch_call(
            db,
            task=task,
            document=document,
            evidence=evidence,
            actor_id=str(uuid4()),
            recorded_at=_RECORDED_AT,
            idempotency_key=f"replay-{field}",
        )
        first = _dispatch_public(**call)
        activity = db.get(CaseActivityEvent, first.activity_id)
        assert activity is not None

        if target == "payload":
            payload = json.loads(activity.payload_json)
            payload[field] = replacement
            activity.payload_json = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        else:
            setattr(activity, field, activity.id if replacement == "SELF" else replacement)
        db.flush()

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(**call)

        assert caught.value.code == "LIFECYCLE_IDEMPOTENCY_CONFLICT"
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == 1
        assert db.get(Case, case.id).lifecycle_revision == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("grant_fee_task_id", ""),
        ("source_document_id", " source "),
        ("reviewed_evidence_version_id", "x" * 37),
        ("expected_content_hash", f"sha256:{'A' * 64}"),
        ("actor_id", " actor "),
        ("recorded_at", datetime(2026, 7, 27, 10, 0, tzinfo=timezone.utc)),
        ("idempotency_key", ""),
        ("idempotency_key", "x" * (129 - len(_IDEMPOTENCY_PREFIX))),
    ],
)
def test_malformed_dispatch_input_is_http_400_and_write_free(
    session_factory: sessionmaker,
    field: str,
    value: object,
) -> None:
    with session_factory() as db:
        before = int(db.scalar(select(func.count()).select_from(CaseActivityEvent)) or 0)
        call: dict[str, object] = {
            "grant_fee_task_id": str(uuid4()),
            "source_document_id": str(uuid4()),
            "reviewed_evidence_version_id": str(uuid4()),
            "expected_content_hash": _CONTENT_HASH,
            "actor_id": str(uuid4()),
            "recorded_at": _RECORDED_AT,
            "idempotency_key": "invalid-boundary",
            "transaction": db,
        }
        call[field] = value

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(**call)

        assert caught.value.code == "GRANT_NOTICE_LIFECYCLE_INVALID"
        assert caught.value.status_code == 400
        assert int(db.scalar(select(func.count()).select_from(CaseActivityEvent)) or 0) == before


@pytest.mark.parametrize(
    ("missing", "expected_code", "expected_message"),
    [
        ("task", "GRANT_FEE_TASK_NOT_FOUND", "未找到授权费用任务"),
        ("document", "DOCUMENT_NOT_FOUND", "未找到文书"),
        ("evidence", "EVIDENCE_VERSION_NOT_FOUND", "未找到证据版本"),
        ("case", "CASE_NOT_FOUND", "未找到案件"),
    ],
)
def test_missing_source_row_is_resource_specific_http_404_and_write_free(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    missing: str,
    expected_code: str,
    expected_message: str,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label=f"MISSING-{missing}")
        call = _dispatch_call(
            db,
            task=task,
            document=document,
            evidence=evidence,
            actor_id=str(uuid4()),
            recorded_at=_RECORDED_AT,
            idempotency_key=f"missing-{missing}",
        )
        if missing == "task":
            call["grant_fee_task_id"] = str(uuid4())
        elif missing == "document":
            call["source_document_id"] = str(uuid4())
        elif missing == "evidence":
            call["reviewed_evidence_version_id"] = str(uuid4())
        else:
            original_get = db.get

            def get_without_case(entity, ident, **kwargs):
                if entity is Case:
                    return None
                return original_get(entity, ident, **kwargs)

            monkeypatch.setattr(db, "get", get_without_case)

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(**call)

        assert caught.value.code == expected_code
        assert caught.value.message == expected_message
        assert caught.value.status_code == 404
        assert _activity_count(db, case.id) == 0
        assert case.lifecycle_revision == 0


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ({"state": "DRAFT"}, "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT"),
        ({"review_state": "PENDING"}, "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT"),
        ({"current_identity_key": None}, "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT"),
        ({"content_hash": f"sha256:{'b' * 64}"}, "GRANT_NOTICE_EVIDENCE_HASH_CONFLICT"),
    ],
)
def test_invalid_reviewed_source_fails_without_writes(
    session_factory: sessionmaker,
    mutation: dict[str, object],
    expected_code: str,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label="BAD-SOURCE")
        expected_hash = evidence.content_hash
        for field, value in mutation.items():
            setattr(evidence, field, value)
        db.flush()

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(
                grant_fee_task_id=task.id,
                source_document_id=document.id,
                reviewed_evidence_version_id=evidence.id,
                expected_content_hash=expected_hash,
                actor_id=str(uuid4()),
                recorded_at=_RECORDED_AT,
                idempotency_key="bad-source",
                transaction=db,
            )

        assert caught.value.code == expected_code
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == 0
        assert db.get(Case, case.id).lifecycle_revision == 0


@pytest.mark.parametrize("mismatch", ["document", "evidence"])
def test_wrong_case_source_is_one_source_conflict_without_writes(
    session_factory: sessionmaker,
    mismatch: str,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label=f"WRONG-CASE-{mismatch}")
        _, other_document, _, other_evidence = _grant_fixture(
            db,
            label=f"WRONG-CASE-OTHER-{mismatch}",
        )
        call = _dispatch_call(
            db,
            task=task,
            document=(other_document if mismatch == "document" else document),
            evidence=(other_evidence if mismatch in {"document", "evidence"} else evidence),
            actor_id=str(uuid4()),
            recorded_at=_RECORDED_AT,
            idempotency_key=f"wrong-case-{mismatch}",
        )

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(**call)

        assert caught.value.code == "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT"
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == 0
        assert db.get(Case, case.id).lifecycle_revision == 0


def test_semantics_resolver_business_error_maps_to_source_conflict(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label="SEMANTICS-ERROR")

        def resolver_failure(_template):
            raise BusinessError(
                code="DOCUMENT_SEMANTICS_METADATA_INVALID",
                message="invalid resolver source",
                status_code=409,
            )

        monkeypatch.setattr(
            grant_fee_service,
            "resolve_document_semantics",
            resolver_failure,
        )

        with pytest.raises(BusinessError) as caught:
            _dispatch(
                db,
                task=task,
                document=document,
                evidence=evidence,
                idempotency_key="semantics-error",
            )

        assert caught.value.code == "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT"
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == 0
        assert db.get(Case, case.id).lifecycle_revision == 0


@pytest.mark.parametrize(
    "extra_data",
    [
        json.dumps({"GrantFeeLines": []}),
        "{",
        json.dumps(
            {
                "GrantFeeLines": [
                    {
                        "fee_name": "授权当年年费",
                        "year": 1,
                        "amount": "not-a-decimal",
                        "reduction_ratio": "0.85",
                    }
                ]
            },
            ensure_ascii=False,
        ),
    ],
)
def test_malformed_fee_lines_fail_at_parser_boundary_without_writes(
    session_factory: sessionmaker,
    extra_data: str,
) -> None:
    with session_factory() as db:
        case, document, task, evidence = _grant_fixture(db, label="BAD-LINES")
        document.extra_data = extra_data
        db.flush()

        with pytest.raises(BusinessError) as caught:
            _dispatch(
                db,
                task=task,
                document=document,
                evidence=evidence,
                idempotency_key="bad-lines",
            )

        assert caught.value.code == "GRANT_NOTICE_FEE_LINES_CONFLICT"
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == 0
        assert db.get(Case, case.id).lifecycle_revision == 0


@pytest.mark.parametrize(
    ("target", "field", "replacement"),
    [
        ("payload", "schema", "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V2"),
        ("payload", "case_id", "wrong-case"),
        ("payload", "predecessor_grant_fee_task_id", "unexpected-predecessor"),
        ("payload", "supersedes_activity_id", "unexpected-activity"),
        ("activity", "lane", "FEE"),
        ("activity", "confirmation_status", "NEEDS_REVIEW"),
        ("activity", "source_activity_id", "SELF"),
        ("activity", "supersedes_event_id", "SELF"),
    ],
)
def test_replacement_rejects_non_v1_or_column_inconsistent_predecessor(
    session_factory: sessionmaker,
    target: str,
    field: str,
    replacement: str,
) -> None:
    with session_factory() as db:
        case, first_document, first_task, first_evidence = _grant_fixture(
            db,
            label=f"BAD-PREDECESSOR-{field}",
        )
        first = _dispatch(
            db,
            task=first_task,
            document=first_document,
            evidence=first_evidence,
            idempotency_key=f"predecessor-{field}",
        )
        predecessor = db.get(CaseActivityEvent, first.activity_id)
        assert predecessor is not None
        replacement_document, replacement_task, replacement_evidence = _replacement_fixture(
            db,
            case=case,
            predecessor_task=first_task,
            label=field,
        )

        if target == "payload":
            payload = json.loads(predecessor.payload_json)
            payload[field] = replacement
            predecessor.payload_json = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        else:
            setattr(
                predecessor,
                field,
                predecessor.id if replacement == "SELF" else replacement,
            )
        db.flush()

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(
                **_dispatch_call(
                    db,
                    task=replacement_task,
                    document=replacement_document,
                    evidence=replacement_evidence,
                    actor_id=str(uuid4()),
                    recorded_at=datetime(2026, 7, 28, 10, 0),
                    idempotency_key=f"replacement-{field}",
                )
            )

        assert caught.value.code == "GRANT_NOTICE_REPLACEMENT_LINEAGE_CONFLICT"
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == 1
        assert db.get(Case, case.id).lifecycle_revision == 1


@pytest.mark.parametrize("conflict", ["ambiguous-task", "ambiguous-activity", "reversed"])
def test_ambiguous_or_reversed_replacement_lineage_fails_without_writes(
    session_factory: sessionmaker,
    conflict: str,
) -> None:
    with session_factory() as db:
        case, first_document, first_task, first_evidence = _grant_fixture(
            db,
            label=f"LINEAGE-{conflict}",
        )
        first = _dispatch(
            db,
            task=first_task,
            document=first_document,
            evidence=first_evidence,
            idempotency_key=f"lineage-first-{conflict}",
        )
        predecessor = db.get(CaseActivityEvent, first.activity_id)
        assert predecessor is not None
        replacement_document, replacement_task, replacement_evidence = _replacement_fixture(
            db,
            case=case,
            predecessor_task=first_task,
            label=conflict,
        )

        if conflict == "ambiguous-task":
            db.add(
                T_GrantFeeTask(
                    id=str(uuid4()),
                    case_id=case.id,
                    type="GRANT",
                    due_date=date(2026, 10, 9),
                    source_document_id=None,
                    deadline_source="CORRECTED_OFFICIAL_NOTICE",
                    deadline_confirmed_at=datetime(2026, 7, 28, 9, 1),
                    superseded_by_task_id=replacement_task.id,
                    currency="CNY",
                )
            )
        elif conflict == "ambiguous-activity":
            db.add(
                CaseActivityEvent(
                    id=str(uuid4()),
                    case_id=case.id,
                    sequence=2,
                    lane=predecessor.lane,
                    activity_type=predecessor.activity_type,
                    source_activity_id=predecessor.source_activity_id,
                    occurred_at=predecessor.occurred_at,
                    effective_at=predecessor.effective_at,
                    confirmation_status=predecessor.confirmation_status,
                    old_business_stage=predecessor.old_business_stage,
                    new_business_stage=predecessor.new_business_stage,
                    old_official_procedure_stage=predecessor.old_official_procedure_stage,
                    new_official_procedure_stage=predecessor.new_official_procedure_stage,
                    old_legal_status=predecessor.old_legal_status,
                    new_legal_status=predecessor.new_legal_status,
                    actor_id=predecessor.actor_id,
                    reviewer_id=predecessor.reviewer_id,
                    idempotency_key=f"duplicate-{uuid4()}",
                    supersedes_event_id=predecessor.supersedes_event_id,
                    payload_json=predecessor.payload_json,
                )
            )
        else:
            replacement_task.superseded_by_task_id = first_task.id
        db.flush()

        with pytest.raises(BusinessError) as caught:
            _dispatch_public(
                **_dispatch_call(
                    db,
                    task=replacement_task,
                    document=replacement_document,
                    evidence=replacement_evidence,
                    actor_id=str(uuid4()),
                    recorded_at=datetime(2026, 7, 28, 10, 0),
                    idempotency_key=f"lineage-replacement-{conflict}",
                )
            )

        assert caught.value.code == "GRANT_NOTICE_REPLACEMENT_LINEAGE_CONFLICT"
        assert caught.value.status_code == 409
        assert _activity_count(db, case.id) == (2 if conflict == "ambiguous-activity" else 1)
        assert db.get(Case, case.id).lifecycle_revision == 1


def test_replacement_appends_one_linked_successor_and_preserves_predecessor(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case, first_document, first_task, first_evidence = _grant_fixture(
            db,
            label="REPLACEMENT",
        )
        first = _dispatch(
            db,
            task=first_task,
            document=first_document,
            evidence=first_evidence,
            idempotency_key="first",
        )
        predecessor = db.get(CaseActivityEvent, first.activity_id)
        assert predecessor is not None
        predecessor_bytes = (
            predecessor.payload_json,
            predecessor.updated_at,
            tuple(
                (
                    row.evidence_kind,
                    row.object_type,
                    row.object_id,
                    row.content_hash,
                    row.captured_at,
                )
                for row in db.scalars(
                    select(CaseActivityEventEvidence)
                    .where(CaseActivityEventEvidence.activity_id == predecessor.id)
                    .order_by(CaseActivityEventEvidence.evidence_kind)
                )
            ),
        )

        replacement_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=_grant_template(db).id,
            doc_type="OFFICIAL_IN",
            direction="IN",
            doc_date=date(2026, 7, 28),
            title="更正办理登记手续通知书",
            extra_data=_grant_extra_data(),
        )
        replacement_task = T_GrantFeeTask(
            id=str(uuid4()),
            case_id=case.id,
            type="GRANT",
            due_date=date(2026, 10, 8),
            source_document_id=replacement_document.id,
            deadline_source="CORRECTED_OFFICIAL_NOTICE",
            deadline_confirmed_at=datetime(2026, 7, 28, 9, 0),
            currency="CNY",
        )
        replacement_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=replacement_document.id,
            file_name="grant-notice-correction.pdf",
            file_path=f"attachments/{replacement_document.id}/grant-notice-correction.pdf",
            content_hash=_CONTENT_HASH,
        )
        replacement_lineage = f"attachment:{replacement_attachment.id}"
        replacement_evidence = DocumentEvidenceVersion(
            id=str(uuid4()),
            case_id=case.id,
            document_id=replacement_document.id,
            attachment_id=replacement_attachment.id,
            lineage_key=replacement_lineage,
            role="RAW_ATTACHMENT",
            version_number=1,
            state="FINAL",
            creator_id=str(uuid4()),
            review_state="APPROVED",
            reviewer_id=str(uuid4()),
            reviewed_at=datetime(2026, 7, 28, 9, 30),
            content_hash=_CONTENT_HASH,
            current_identity_key=f"{case.id}|{replacement_lineage}",
        )
        db.add(replacement_document)
        db.flush()
        db.add(replacement_task)
        db.flush()
        first_task.superseded_by_task_id = replacement_task.id
        db.add(replacement_attachment)
        db.flush()
        db.add(replacement_evidence)
        db.flush()

        second = _dispatch_public(
            grant_fee_task_id=replacement_task.id,
            source_document_id=replacement_document.id,
            reviewed_evidence_version_id=replacement_evidence.id,
            expected_content_hash=replacement_evidence.content_hash,
            actor_id=str(uuid4()),
            recorded_at=datetime(2026, 7, 28, 10, 0),
            idempotency_key="replacement",
            transaction=db,
        )

        successor = db.get(CaseActivityEvent, second.activity_id)
        assert successor is not None
        successor_payload = json.loads(successor.payload_json)
        assert successor.supersedes_event_id == predecessor.id
        assert successor_payload["predecessor_grant_fee_task_id"] == first_task.id
        assert successor_payload["supersedes_activity_id"] == predecessor.id
        assert second.lifecycle_revision == 2
        db.refresh(predecessor)
        assert (
            predecessor.payload_json,
            predecessor.updated_at,
            tuple(
                (
                    row.evidence_kind,
                    row.object_type,
                    row.object_id,
                    row.content_hash,
                    row.captured_at,
                )
                for row in db.scalars(
                    select(CaseActivityEventEvidence)
                    .where(CaseActivityEventEvidence.activity_id == predecessor.id)
                    .order_by(CaseActivityEventEvidence.evidence_kind)
                )
            ),
        ) == predecessor_bytes


def test_caller_rollback_removes_activity_evidence_and_projection(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as setup:
        case, document, task, evidence = _grant_fixture(setup, label="ROLLBACK")
        case_id = case.id
        document_id = document.id
        task_id = task.id
        evidence_id = evidence.id
        setup.commit()

    with session_factory() as db:
        case = db.get(Case, case_id)
        document = db.get(Document, document_id)
        task = db.get(T_GrantFeeTask, task_id)
        evidence = db.get(DocumentEvidenceVersion, evidence_id)
        assert case is not None
        assert document is not None
        assert task is not None
        assert evidence is not None
        _dispatch(
            db,
            task=task,
            document=document,
            evidence=evidence,
            idempotency_key="rollback",
        )
        assert _activity_count(db, case_id) == 1
        db.rollback()

    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        assert case.lifecycle_revision == 0
        assert db.get(Document, document_id) is not None
        assert db.get(T_GrantFeeTask, task_id) is not None
        assert db.get(DocumentEvidenceVersion, evidence_id) is not None
        assert _activity_count(db, case_id) == 0
        assert (
            int(
                db.scalar(
                    select(func.count())
                    .select_from(CaseActivityEventEvidence)
                    .where(CaseActivityEventEvidence.case_id == case_id)
                )
                or 0
            )
            == 0
        )
