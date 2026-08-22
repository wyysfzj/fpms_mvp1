from __future__ import annotations

import importlib
import json
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
)


def _create_case(db: Session, *, status: str = "OA1") -> Case:
    case = Case(
        id=str(uuid4()),
        case_no=f"ADDGAP-OA-{uuid4().hex[:8].upper()}",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="OA ensure service 测试案件",
        status=status,
    )
    db.add(case)
    db.commit()
    return case


def _oa_alias_template(db: Session, *, status_effect: str) -> DocTemplate:
    task_template_code = "OA_REPLY" if status_effect == "OA1" else "OA_REPLY_SUBSEQUENT"
    template = DocTemplate(
        id=str(uuid4()),
        code=f"OA_ALIAS_{status_effect}_{uuid4().hex[:8].upper()}",
        name="不参与解析的 OA 别名",
        direction="IN",
        status_effect=status_effect,
        deadline_template_code=task_template_code,
        need_reply=True,
        input_fields=json.dumps(
            {
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "OA_REPLY",
                "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                "archive_status_restore": "SUB_EXAM",
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "canonical_template_code": "OA_IN",
            },
            ensure_ascii=False,
        ),
    )
    db.add(template)
    db.commit()
    return template


def _create_source(
    db: Session,
    *,
    case: Case,
    template: DocTemplate | None = None,
    template_code: str = "OA_IN",
    direction: str = "IN",
) -> Document:
    if template is None:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.code == template_code)
        ).scalar_one()
    document = Document(
        id=str(uuid4()),
        case_id=case.id,
        doc_template_id=template.id,
        doc_type="OFFICIAL_NOTICE",
        direction=direction,
        title="审查意见通知书",
        need_reply=True,
    )
    db.add(document)
    db.commit()
    return document


def _ensure(db: Session, *, source_document_id: str):
    service = importlib.import_module("app.modules.official_workflows.service")
    return service.ensure_oa_reply_package(db, source_document_id=source_document_id)


def _oa_packages(db: Session, *, source_document_id: str) -> list[OfficialWorkPackage]:
    return (
        db.execute(
            select(OfficialWorkPackage).where(
                OfficialWorkPackage.source_document_id == source_document_id,
                OfficialWorkPackage.package_kind == "OA_REPLY",
            )
        )
        .scalars()
        .all()
    )


def test_oa1_source_creates_one_initialized_package(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)

        result = _ensure(db, source_document_id=source.id)

        packages = _oa_packages(db, source_document_id=source.id)
        assert len(packages) == 1
        assert result.package.id == packages[0].id
        assert result.source_document is not None
        assert result.source_document.id == source.id
        assert packages[0].case_id == case.id
        assert packages[0].resolve_key == f"OA_REPLY:{source.id}"
        assert packages[0].status == "NEEDS_MAINTENANCE"

        manifests = (
            db.execute(
                select(OfficialWorkPackageManifest).where(
                    OfficialWorkPackageManifest.package_id == packages[0].id
                )
            )
            .scalars()
            .all()
        )
        assert {manifest.official_file_role for manifest in manifests} == {
            "OA_STATEMENT_WORD",
            "OA_STATEMENT_PDF",
            "OA_MODIFIED_CLAIMS",
            "OA_AMENDMENT_COMPARISON",
            "OA_OTHER_PROOF",
            "OA_ADDITIONAL_FILE",
        }

        checklists = (
            db.execute(
                select(OfficialWorkPackageChecklist).where(
                    OfficialWorkPackageChecklist.package_id == packages[0].id
                )
            )
            .scalars()
            .all()
        )
        assert {checklist.item_code for checklist in checklists} == {
            "STATEMENT_TEXT_CONFIRMED",
            "PDF_FIDELITY_CONFIRMED",
            "MODIFIED_CLAIMS_CONFIRMED",
            "EXPERIMENT_DATA_FLAG_CONFIRMED",
            "PREVIEW_CONFIRMED",
            "SIGNATURE_CONFIRMED",
        }


def test_oa2_semantic_alias_creates_package_only_in_oa2_state(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db, status="OA2")
        template = _oa_alias_template(db, status_effect="OA2")
        source = _create_source(db, case=case, template=template)

        result = _ensure(db, source_document_id=source.id)

        assert result.package.source_document_id == source.id
        assert result.package.case_id == case.id
        assert result.package.status == "NEEDS_MAINTENANCE"
        assert _oa_packages(db, source_document_id=source.id)[0].resolve_key == (
            f"OA_REPLY:{source.id}"
        )


def test_existing_archived_package_is_returned_before_case_state_gate(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)
        created = _ensure(db, source_document_id=source.id)
        package = db.get(OfficialWorkPackage, created.package.id)
        package.status = "ARCHIVED"
        case.status = "SUB_EXAM"
        db.commit()

        checklist_count = len(
            db.execute(
                select(OfficialWorkPackageChecklist).where(
                    OfficialWorkPackageChecklist.package_id == package.id
                )
            )
            .scalars()
            .all()
        )
        manifest_count = len(
            db.execute(
                select(OfficialWorkPackageManifest).where(
                    OfficialWorkPackageManifest.package_id == package.id
                )
            )
            .scalars()
            .all()
        )

        resolved = _ensure(db, source_document_id=source.id)

        assert resolved.package.id == package.id
        assert resolved.package.status == "ARCHIVED"
        assert (
            len(
                db.execute(
                    select(OfficialWorkPackageChecklist).where(
                        OfficialWorkPackageChecklist.package_id == package.id
                    )
                )
                .scalars()
                .all()
            )
            == checklist_count
        )
        assert (
            len(
                db.execute(
                    select(OfficialWorkPackageManifest).where(
                        OfficialWorkPackageManifest.package_id == package.id
                    )
                )
                .scalars()
                .all()
            )
            == manifest_count
        )


def test_existing_package_still_rejects_source_direction_change(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)
        created = _ensure(db, source_document_id=source.id)
        package = db.get(OfficialWorkPackage, created.package.id)
        package.status = "ARCHIVED"
        source.direction = "OUT"
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 400
        assert exc_info.value.code == "OA_REPLY_SOURCE_DIRECTION_INVALID"


def test_existing_package_still_rejects_reference_only_template_change(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)
        created = _ensure(db, source_document_id=source.id)
        package = db.get(OfficialWorkPackage, created.package.id)
        reference_only = db.execute(
            select(DocTemplate).where(DocTemplate.code == "CLIENT_IN")
        ).scalar_one()
        package.status = "ARCHIVED"
        source.doc_template_id = reference_only.id
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "OA_REPLY_SOURCE_SEMANTICS_INVALID"


def test_wrong_case_state_fails_without_creating(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        case = _create_case(db, status="SUB_EXAM")
        source = _create_source(db, case=case)

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "OA_REPLY_CASE_STATE_INVALID"
        assert _oa_packages(db, source_document_id=source.id) == []


def test_missing_document_returns_not_found(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=str(uuid4()))

        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "DOCUMENT_NOT_FOUND"


def test_outgoing_source_fails_without_creating(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case, direction="OUT")

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 400
        assert exc_info.value.code == "OA_REPLY_SOURCE_DIRECTION_INVALID"
        assert _oa_packages(db, source_document_id=source.id) == []


def test_reference_only_source_fails_without_creating(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case, template_code="CLIENT_IN")

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "OA_REPLY_SOURCE_SEMANTICS_INVALID"
        assert _oa_packages(db, source_document_id=source.id) == []


@pytest.mark.parametrize("existing_count", [1, 2])
def test_corrupt_oa_identity_returns_conflict_without_creating(
    session_factory: sessionmaker,
    existing_count: int,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)
        db.add_all(
            [
                OfficialWorkPackage(
                    id=str(uuid4()),
                    case_id=case.id,
                    package_kind="OA_REPLY",
                    status="PREPARING",
                    source_document_id=source.id,
                    resolve_key=None,
                )
                for _ in range(existing_count)
            ]
        )
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "OA_REPLY_IDENTITY_CONFLICT"
        assert len(_oa_packages(db, source_document_id=source.id)) == existing_count


def test_unique_race_rereads_committed_winner(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)
        original_flush = db.flush
        winner_id: list[str] = []

        def racing_flush(*args, **kwargs) -> None:
            monkeypatch.setattr(db, "flush", original_flush)
            db.rollback()
            with session_factory() as rival_db:
                winner = _ensure(rival_db, source_document_id=source.id)
                winner_id.append(winner.package.id)
            raise IntegrityError("simulated unique-key race", {}, Exception())

        monkeypatch.setattr(db, "flush", racing_flush)

        resolved = _ensure(db, source_document_id=source.id)

        assert resolved.package.id == winner_id[0]
        assert [package.id for package in _oa_packages(db, source_document_id=source.id)] == (
            winner_id
        )


def test_unique_collision_without_exact_winner_returns_identity_conflict(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        source = _create_source(db, case=case)
        db.add(
            OfficialWorkPackage(
                id=str(uuid4()),
                case_id=case.id,
                package_kind="OTHER_KIND",
                status="PREPARING",
                resolve_key=f"OA_REPLY:{source.id}",
            )
        )
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, source_document_id=source.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "OA_REPLY_IDENTITY_CONFLICT"
        assert _oa_packages(db, source_document_id=source.id) == []
