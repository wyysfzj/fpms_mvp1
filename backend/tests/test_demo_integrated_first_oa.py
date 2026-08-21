from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document, DocumentEvidenceVersion

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_demo_integrated_a_rehearsal.py"
LOCAL_RUNNER = ROOT / "backend" / "scripts" / "run_local_demo_abc.py"
SPEC = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "playwright_ts"
    / "src"
    / "tests"
    / "demo-integrated-a.live-backend.spec.ts"
)


def _runner_module():
    spec = importlib.util.spec_from_file_location("run_demo_integrated_a_task05", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_bridge_exposes_exact_manifest_evidence_descriptors(tmp_path: Path) -> None:
    module = _runner_module()
    bundle, _manifest_sha, _authority_sha = module.build_integrated_bundle(tmp_path)

    descriptors = module.integrated_evidence_descriptors(bundle)

    assert [row["role"] for row in descriptors] == [
        "FILING_FINAL_SUBMISSION",
        "FILING_RECEIPT",
        "ACCEPTANCE_NOTICE",
        "PRELIMINARY_EXAMINATION_SOURCE",
        "PUBLICATION_NOTICE",
        "SUBSTANTIVE_EXAMINATION_SOURCE",
        "OA_NOTICE_1",
        "OA_RECEIPT_1",
        "OA_NOTICE_2",
        "OA_RECEIPT_2",
        "GRANT_NOTICE_ORIGINAL",
        "GRANT_NOTICE_REPLACEMENT",
    ]
    assert len({row["sha256"] for row in descriptors}) == 12
    assert all(Path(row["path"]).is_file() for row in descriptors)
    assert all(set(row) == {"role", "path", "sha256", "metadata"} for row in descriptors)
    assert json.loads(module.integrated_evidence_json(bundle)) == descriptors


def test_canonical_driver_replaces_only_ia01_through_ia06_red_methods() -> None:
    source = SPEC.read_text(encoding="utf-8")

    for checkpoint in range(1, 7):
        assert f"this.red('IA-{checkpoint:02d}')" not in source
    assert "this.red('IA-07')" in source
    assert "FPMS_DEMO_INTEGRATED_EVIDENCE_JSON" in source
    assert "uploadRole(" in source
    assert "publicLifecycleApi(" in source
    assert "page.request" not in source
    assert "route.fulfill" not in source
    assert "client_count: 1" not in source
    assert "business_counts: { package: 0" not in source
    assert "return deadline" not in source
    assert "replayed_task_id: targetTask.task_id" not in source
    assert "link_count: linked.body.reply_document.id ===" not in source
    assert "task5-checkpoints.json" in source
    assert "visibleCaseSnapshot(" in source
    assert "visibleOaTasks(" in source
    assert "tasks.map((item) => item.id)" in source
    assert "matches.map((item) => item.id)" in source
    assert "observedOverlayPackages(" in source
    assert "item.package_kind, item.status" in source
    assert "typeof x.task_id).toBe('string')" in source
    assert "item.client_code === code && item.name_cn === this.clientName" in source
    assert "item.contact_name === '虚构主联系人'" in source
    assert source.count(".then((response) => response.json() as Promise<Json>)") == 3
    assert "tasks.map((item) => item.task_id)" not in source
    assert ".map((item) => item.package_id).filter" not in source


def test_local_runner_materializes_the_approved_60_row_reference_catalog() -> None:
    source = LOCAL_RUNNER.read_text(encoding="utf-8")

    assert "seed_fee_reduction_approval_official_notice_catalog" in source
    assert "seed_demo_task_templates" in source
    assert "seed_demo_oa_out_template" in source
    assert "catalog_count != 60" in source


def test_filing_receipt_hash_uses_the_configured_storage_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.official_workflows import service

    storage = tmp_path / "isolated-storage"
    receipt = storage / "documents" / "fictional-receipt.pdf"
    receipt.parent.mkdir(parents=True)
    receipt.write_bytes(b"%PDF-1.4\n% synthetic filing receipt\n")
    content_hash = f"sha256:{hashlib.sha256(receipt.read_bytes()).hexdigest()}"
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(storage_dir=str(storage)),
    )

    assert service._filing_receipt_attachment_hash(
        SimpleNamespace(
            file_path="documents/fictional-receipt.pdf",
            content_hash=content_hash,
        )
    ) == content_hash


def test_filing_receipt_accepts_later_non_lifecycle_evidence_activity() -> None:
    from app.modules.official_workflows import service

    case = SimpleNamespace(
        status="WAITING_RECEIPT",
        business_stage="WAITING_EXTERNAL_RECEIPT",
        official_procedure_stage="SUBMITTED_WAITING_RECEIPT",
        legal_status="NOT_ESTABLISHED",
        lifecycle_verification_status="CONFIRMED",
        lifecycle_revision=9,
    )

    assert service._filing_receipt_projection_matches(
        case,
        receipt_replay=False,
        latest_lifecycle_key="filing-external-lifecycle:package:2026-08-02T09:00:00",
        submission_lifecycle_key="filing-external-lifecycle:package:2026-08-02T09:00:00",
        replay_receipt_lifecycle_key=None,
    )


def test_linked_oa_reply_enters_waiting_receipt_without_closing_task() -> None:
    from app.modules.official_workflows import service

    package = SimpleNamespace(status="NEEDS_MAINTENANCE")
    task = SimpleNamespace(status="OPEN")

    service._mark_linked_oa_reply_waiting_receipt(package)

    assert package.status == "WAITING_RECEIPT"
    assert task.status == "OPEN"


def test_oa_reply_link_replays_same_identity_and_rejects_replacement() -> None:
    from app.modules.official_workflows import service

    package = SimpleNamespace(
        id="package-1",
        source_document_id="source-1",
        reply_document_id=None,
    )
    first = SimpleNamespace(id="reply-1", reply_to_id=None)
    replacement = SimpleNamespace(id="reply-2", reply_to_id=None)

    service._bind_oa_reply_identity(package, first)
    service._bind_oa_reply_identity(package, first)

    assert package.reply_document_id == "reply-1"
    assert first.reply_to_id == "source-1"
    with pytest.raises(BusinessError) as exc_info:
        service._bind_oa_reply_identity(package, replacement)
    assert exc_info.value.code == "OA_REPLY_IDENTITY_CONFLICT"
    assert exc_info.value.status_code == 409
    assert package.reply_document_id == "reply-1"
    assert replacement.reply_to_id is None


def test_confirmed_deadline_change_is_rejected_without_document_mutation() -> None:
    from app.modules.documents import service

    original = json.dumps(
        {
            "OfficialDueDate": "2026-12-08",
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
            "description": "原说明",
        },
        ensure_ascii=False,
    )
    document = SimpleNamespace(extra_data=original)

    with pytest.raises(BusinessError) as exc_info:
        service._merge_document_update_extra_data(
            document,
            {
                "official_due_date": date(2026, 12, 9),
                "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                "official_due_date_status": "CONFIRMED",
            },
        )

    assert exc_info.value.code == "DOCUMENT_DEADLINE_OVERRIDE_REQUIRED"
    assert exc_info.value.status_code == 409
    assert document.extra_data == original


def test_confirmed_deadline_change_api_rejects_without_persisted_mutation(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = str(uuid4())
    document_id = str(uuid4())
    original = json.dumps(
        {
            "OfficialDueDate": "2026-12-08",
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
            "description": "原说明",
        },
        ensure_ascii=False,
    )
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=case_id,
                case_no=f"IA-DEADLINE-LOCK-{uuid4().hex[:8]}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                status="OA1",
                fee_reduction="0",
                business_stage="OA_REPLY_IN_PROGRESS",
                official_procedure_stage="OFFICE_ACTION_RESPONSE",
                legal_status="APPLICATION_PENDING",
                lifecycle_verification_status="CONFIRMED",
                lifecycle_revision=1,
            )
        )
        transaction.add(
            Document(
                id=document_id,
                case_id=case_id,
                direction="IN",
                title="虚构已确认期限官文",
                extra_data=original,
            )
        )
        transaction.commit()

    response = client.put(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers,
        json={
            "official_due_date": "2026-12-09",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
            "description": "不应持久化",
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "DOCUMENT_DEADLINE_OVERRIDE_REQUIRED"
    with session_factory() as transaction:
        stored = transaction.get(Document, document_id)
        assert stored is not None
        assert stored.extra_data == original


def test_executable_oa_create_requires_confirmed_deadline_without_writing(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = str(uuid4())
    template_id = str(uuid4())
    title = "虚构缺失期限审查意见"
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=case_id,
                case_no=f"IA-DEADLINE-{uuid4().hex[:8]}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                status="SUB_EXAM",
                fee_reduction="0",
                business_stage="PROSECUTION_MANAGEMENT",
                official_procedure_stage="SUBSTANTIVE_EXAMINATION",
                legal_status="APPLICATION_PENDING",
                lifecycle_verification_status="CONFIRMED",
                lifecycle_revision=0,
            )
        )
        transaction.add(
            DocTemplate(
                id=template_id,
                code=f"OFFICIAL_NOTICE_{uuid4().hex[:8].upper()}",
                name="虚构可执行OA模板",
                direction="IN",
                enabled=True,
                status_effect="OA1",
                deadline_template_code="OA_REPLY",
                need_reply=True,
                input_fields=json.dumps(
                    {
                        "catalog_kind": "OFFICIAL_NOTICE",
                        "catalog_status": "EXECUTABLE",
                        "canonical_template_code": "OA_IN",
                        "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                        "archive_status_restore": "SUB_EXAM",
                        "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                        "execution_behavior": "OA_REPLY",
                        "task_template_code": "OA_REPLY",
                    }
                ),
            )
        )
        transaction.commit()

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-08-08",
            "title": title,
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_OFFICIAL_DUE_DATE_REQUIRED"
    with session_factory() as transaction:
        assert transaction.scalars(select(Document).where(Document.title == title)).all() == []


@pytest.mark.parametrize("official_file_role", ("FILING_MERGED_PDF", "OFFICIAL_NOTICE_PDF"))
def test_visible_official_pdf_upload_creates_reviewable_final_evidence(
    official_file_role: str,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.documents import api as documents_api

    monkeypatch.setattr(
        documents_api,
        "get_settings",
        lambda: SimpleNamespace(storage_dir=str(tmp_path / "storage")),
    )
    case_id = str(uuid4())
    document_id = str(uuid4())
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=case_id,
                case_no=f"IA-UPLOAD-{uuid4().hex[:8]}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                status="NOT_FILED",
                fee_reduction="0",
                business_stage="NEW_CASE",
                official_procedure_stage="NOT_SUBMITTED",
                legal_status="NOT_ESTABLISHED",
                lifecycle_verification_status="CONFIRMED",
                lifecycle_revision=0,
            )
        )
        transaction.flush()
        transaction.add(
            Document(
                id=document_id,
                case_id=case_id,
                direction="IN",
                title="虚构官方PDF上传契约",
            )
        )
        transaction.commit()

    response = client.post(
        f"/api/v1/documents/{document_id}/attachments",
        headers=auth_headers,
        data={"official_file_role": official_file_role},
        files={"file": ("fictional.pdf", b"%PDF-1.4\n% synthetic\n", "application/pdf")},
    )

    assert response.status_code == 201, response.text
    with session_factory() as transaction:
        versions = transaction.scalars(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.document_id == document_id
            )
        ).all()
        assert len(versions) == 1
        version = versions[0]
        assert version.role == "OFFICIAL_FINAL_PDF"
        assert version.state == "FINAL"
        assert version.review_state == "PENDING"
