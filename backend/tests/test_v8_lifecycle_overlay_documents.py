from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_overlay_service import read_lifecycle_overlay
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)
from app.modules.tasks.models import Task


def _id() -> str:
    return str(uuid4())


def _document(transaction: Session, case_id: str, *, title: str) -> Document:
    document = Document(id=_id(), case_id=case_id, direction="OUT", title=title)
    transaction.add(document)
    transaction.flush()
    return document


def _evidence_version(
    transaction: Session,
    *,
    case_id: str,
    document: Document,
    lineage_key: str,
    state: str = "FINAL",
) -> DocumentEvidenceVersion:
    attachment = DocAttachment(
        id=_id(),
        document_id=document.id,
        file_name=f"{lineage_key}.pdf",
        file_path=f"attachments/{lineage_key}.pdf",
        content_hash=f"sha256:{lineage_key}",
    )
    version = DocumentEvidenceVersion(
        id=_id(),
        case_id=case_id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=lineage_key,
        role="RAW_ATTACHMENT",
        version_number=1,
        state=state,
        creator_id="creator",
        review_state="APPROVED",
        reviewer_id="reviewer",
        reviewed_at=datetime(2026, 8, 1, 9, 0),
        final_submitted_at=datetime(2026, 8, 1, 10, 0),
        content_hash=attachment.content_hash,
        current_identity_key=f"{case_id}|{lineage_key}",
    )
    transaction.add_all((attachment, version))
    transaction.flush()
    return version


def _activity(transaction: Session, case: Case) -> CaseActivityEvent:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    activity = CaseActivityEvent(
        id=_id(),
        case_id=case.id,
        sequence=1,
        lane=ActivityLane.LIFECYCLE.value,
        activity_type="CASE_OPENED",
        occurred_at=datetime(2026, 8, 1, 8, 0),
        effective_at=datetime(2026, 8, 1, 8, 0),
        recorded_at=datetime(2026, 8, 1, 8, 0),
        confirmation_status=ConfirmationStatus.CONFIRMED.value,
        new_business_stage=BusinessStage.NEW_CASE.value,
        new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
        new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
        actor_id=actor_id,
        idempotency_key=f"overlay-document-{case.id}",
        payload_json="{}",
        conflict_lineage_version="V1",
        conflict_code_count=0,
        conflict_codes_sha256="4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    )
    transaction.add(activity)
    transaction.flush()
    return activity


def _case(transaction: Session, *, prefix: str) -> Case:
    case = Case(
        id=_id(),
        case_no=f"{prefix}-{uuid4().hex}",
        status="NOT_FILED",
        business_stage=BusinessStage.NEW_CASE.value,
        official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
        legal_status=LegalStatus.NOT_ESTABLISHED.value,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
        lifecycle_revision=1,
    )
    transaction.add(case)
    transaction.flush()
    return case


def test_overlay_projects_only_exact_document_evidence_graph_without_writing(
    session_factory: sessionmaker,
) -> None:
    case_id = _id()
    with session_factory() as transaction:
        case = Case(
            id=case_id,
            case_no=f"OVERLAY-DOCUMENT-{uuid4().hex}",
            status="NOT_FILED",
            business_stage=BusinessStage.NEW_CASE.value,
            official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
            legal_status=LegalStatus.NOT_ESTABLISHED.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=1,
        )
        transaction.add(case)
        transaction.flush()
        activity = _activity(transaction, case)
        version_document = _document(transaction, case.id, title="证据版本")
        child_document = _document(transaction, case.id, title="派生证据")
        package_document = _document(transaction, case.id, title="工作包来源")
        version = _evidence_version(
            transaction,
            case_id=case.id,
            document=version_document,
            lineage_key="version",
        )
        child = _evidence_version(
            transaction,
            case_id=case.id,
            document=child_document,
            lineage_key="child",
            state="DRAFT",
        )
        transaction.add(
            DocumentEvidenceDerivation(
                id=_id(),
                case_id=case.id,
                parent_evidence_version_id=version.id,
                child_evidence_version_id=child.id,
                derivation_type="REVISION",
                actor_id="deriver",
                derived_at=datetime(2026, 8, 1, 11, 0),
                source_snapshot="{}",
            )
        )
        direct_package = OfficialWorkPackage(
            id=_id(),
            case_id=case.id,
            package_kind="OA_REPLY",
            status="ARCHIVED",
            source_document_id=package_document.id,
        )
        manifest_package = OfficialWorkPackage(
            id=_id(),
            case_id=case.id,
            package_kind="OA_REPLY",
            status="PREPARING",
            reply_document_id=package_document.id,
        )
        transaction.add_all((direct_package, manifest_package))
        transaction.flush()
        receipt = OfficialWorkPackageReceipt(
            id=_id(),
            package_id=direct_package.id,
            receipt_kind="RECEIPT_PDF",
            receipt_attachment_id=version.attachment_id,
            receiving_case_no="CN-1",
            submitter="提交人",
            received_at=datetime(2026, 8, 1, 12, 0),
            archive_status="ARCHIVED",
        )
        transaction.add_all(
            (
                receipt,
                OfficialWorkPackageManifest(
                    id=_id(),
                    package_id=manifest_package.id,
                    evidence_version_id=version.id,
                    present=True,
                    sort_order=1,
                ),
                Task(
                    id=_id(),
                    case_id=case.id,
                    document_id=version_document.id,
                    title="版本任务",
                    due_date=date(2026, 8, 3),
                    status="OPEN",
                ),
                Task(
                    id=_id(),
                    case_id=case.id,
                    document_id=package_document.id,
                    title="工作包任务",
                    due_date=date(2026, 8, 2),
                    status="DONE",
                    done_at=datetime(2026, 8, 2, 9, 0),
                ),
            )
        )
        for object_type, object_id in (
            ("DocumentEvidenceVersion", version.id),
            ("OfficialWorkPackage", direct_package.id),
            ("OfficialWorkPackageReceipt", receipt.id),
            ("UnrecognizedEvidence", _id()),
        ):
            transaction.add(
                CaseActivityEventEvidence(
                    id=_id(),
                    case_id=case.id,
                    activity_id=activity.id,
                    evidence_kind=f"DOCUMENT_FACT:{object_type}",
                    object_type=object_type,
                    object_id=object_id,
                    content_hash=f"sha256:{object_id}",
                    captured_at=datetime(2026, 8, 1, 13, 0),
                )
            )
        transaction.commit()

        statements: list[str] = []

        def capture_sql(_conn, _cursor, statement, _params, _context, _many) -> None:
            statements.append(statement.lstrip().split(None, 1)[0].upper())

        event.listen(transaction.get_bind(), "before_cursor_execute", capture_sql)
        try:
            result = read_lifecycle_overlay(
                case_id=case.id,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )
        finally:
            event.remove(transaction.get_bind(), "before_cursor_execute", capture_sql)

        milestone = result.milestones[0]
        assert [item.version.evidence_version_id for item in milestone.document_evidence] == [
            version.id
        ]
        assert milestone.document_evidence[0].version.is_current is True
        assert milestone.document_evidence[0].version.is_final is True
        assert [
            item.evidence_derivation_id for item in milestone.document_evidence[0].derivations
        ] == [
            transaction.scalar(
                select(DocumentEvidenceDerivation.id).where(
                    DocumentEvidenceDerivation.parent_evidence_version_id == version.id
                )
            )
        ]
        assert [item.package_id for item in milestone.work_packages] == sorted(
            (direct_package.id, manifest_package.id)
        )
        by_package = {item.package_id: item for item in milestone.work_packages}
        assert by_package[direct_package.id].receipts[0].receipt_id == receipt.id
        assert by_package[manifest_package.id].manifest_evidence_version_ids == (version.id,)
        assert by_package[direct_package.id].missing_gate_codes == ()
        assert by_package[manifest_package.id].missing_gate_codes == ("RECEIPT_MISSING",)
        assert [item.title for item in milestone.tasks] == ["工作包任务", "版本任务"]
        assert milestone.evidence_summary[-1].object_type == "UnrecognizedEvidence"
        assert statements and set(statements) == {"SELECT"}
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_overlay_rejects_missing_selected_document_evidence_without_writing(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = Case(
            id=_id(),
            case_no=f"OVERLAY-DOCUMENT-CONFLICT-{uuid4().hex}",
            status="NOT_FILED",
            business_stage=BusinessStage.NEW_CASE.value,
            official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
            legal_status=LegalStatus.NOT_ESTABLISHED.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=1,
        )
        transaction.add(case)
        transaction.flush()
        activity = _activity(transaction, case)
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(),
                case_id=case.id,
                activity_id=activity.id,
                evidence_kind="DOCUMENT_FACT:missing",
                object_type="DocumentEvidenceVersion",
                object_id=_id(),
                content_hash="sha256:missing",
                captured_at=datetime(2026, 8, 1, 13, 0),
            )
        )
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            read_lifecycle_overlay(
                case_id=case.id,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )

        assert caught.value.code == "LIFECYCLE_OVERLAY_DOCUMENT_CONFLICT"
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


@pytest.mark.parametrize(
    "scenario",
    (
        "cross_case_version",
        "cross_case_package",
        "cross_case_receipt_package",
        "cross_case_manifest_package",
        "cross_case_derivation_endpoint",
        "corrupt_evidence_role",
    ),
)
def test_overlay_rejects_cross_case_document_graph_and_corrupt_enum_without_writing(
    session_factory: sessionmaker,
    scenario: str,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction, prefix="OVERLAY-DOCUMENT-GUARD")
        activity = _activity(transaction, case)
        object_type = "DocumentEvidenceVersion"
        object_id: str
        if scenario == "cross_case_version":
            other_case = _case(transaction, prefix="OTHER")
            other_document = _document(transaction, other_case.id, title="外部案件证据")
            object_id = _evidence_version(
                transaction,
                case_id=other_case.id,
                document=other_document,
                lineage_key="other-version",
            ).id
        elif scenario == "cross_case_package":
            other_case = _case(transaction, prefix="OTHER")
            package = OfficialWorkPackage(
                id=_id(),
                case_id=other_case.id,
                package_kind="OA_REPLY",
                status="PREPARING",
            )
            transaction.add(package)
            object_type, object_id = "OfficialWorkPackage", package.id
        elif scenario == "cross_case_receipt_package":
            other_case = _case(transaction, prefix="OTHER")
            package = OfficialWorkPackage(
                id=_id(),
                case_id=other_case.id,
                package_kind="OA_REPLY",
                status="PREPARING",
            )
            receipt = OfficialWorkPackageReceipt(
                id=_id(),
                package_id=package.id,
                receipt_kind="RECEIPT_PDF",
            )
            transaction.add_all((package, receipt))
            object_type, object_id = "OfficialWorkPackageReceipt", receipt.id
        else:
            document = _document(transaction, case.id, title="本案证据")
            version = _evidence_version(
                transaction,
                case_id=case.id,
                document=document,
                lineage_key=scenario,
            )
            object_id = version.id
            if scenario == "cross_case_manifest_package":
                other_case = _case(transaction, prefix="OTHER")
                package = OfficialWorkPackage(
                    id=_id(),
                    case_id=other_case.id,
                    package_kind="OA_REPLY",
                    status="PREPARING",
                )
                transaction.add_all(
                    (
                        package,
                        OfficialWorkPackageManifest(
                            id=_id(),
                            package_id=package.id,
                            evidence_version_id=version.id,
                        ),
                    )
                )
            elif scenario == "cross_case_derivation_endpoint":
                other_case = _case(transaction, prefix="OTHER")
                other_document = _document(transaction, other_case.id, title="外部派生证据")
                child = _evidence_version(
                    transaction,
                    case_id=other_case.id,
                    document=other_document,
                    lineage_key="other-child",
                )
                transaction.add(
                    DocumentEvidenceDerivation(
                        id=_id(),
                        case_id=case.id,
                        parent_evidence_version_id=version.id,
                        child_evidence_version_id=child.id,
                        derivation_type="REVISION",
                        actor_id="deriver",
                        derived_at=datetime(2026, 8, 1, 11, 0),
                        source_snapshot="{}",
                    )
                )
            else:
                assert scenario == "corrupt_evidence_role"
                version.role = "CORRUPT"
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(),
                case_id=case.id,
                activity_id=activity.id,
                evidence_kind=f"DOCUMENT_FACT:{scenario}",
                object_type=object_type,
                object_id=object_id,
                content_hash=f"sha256:{object_id}",
                captured_at=datetime(2026, 8, 1, 13, 0),
            )
        )
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            read_lifecycle_overlay(
                case_id=case.id,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )

        assert caught.value.code == "LIFECYCLE_OVERLAY_DOCUMENT_CONFLICT"
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted
