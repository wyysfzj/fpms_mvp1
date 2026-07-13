from __future__ import annotations

import importlib
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
)


def _create_case(db: Session, *, status: str = "NOT_FILED") -> Case:
    case = Case(
        id=str(uuid4()),
        case_no=f"ADDGAP-FILING-{uuid4().hex[:8].upper()}",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="Filing ensure service 测试案件",
        status=status,
    )
    db.add(case)
    db.commit()
    return case


def _ensure(db: Session, *, case_id: str):
    service = importlib.import_module("app.modules.official_workflows.service")
    return service.ensure_filing_preparation_package(db, case_id=case_id)


def test_not_filed_case_creates_one_initialized_filing_package(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)

        result = _ensure(db, case_id=case.id)

        packages = (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.case_id == case.id,
                    OfficialWorkPackage.package_kind == "FILING_PREP",
                )
            )
            .scalars()
            .all()
        )
        assert len(packages) == 1
        assert result.package.id == packages[0].id
        assert packages[0].resolve_key == f"FILING_PREP:{case.id}"
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
            "TECHNICAL_DISCLOSURE",
            "COMMISSION_INSTRUCTION",
            "FILING_XML_ZIP",
            "FILING_MERGED_PDF",
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
            "PREVIEW_CONFIRMED",
            "SIGNATURE_CONFIRMED",
        }


def test_existing_archived_package_is_returned_before_case_state_gate(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        created = _ensure(db, case_id=case.id)
        package = db.get(OfficialWorkPackage, created.package.id)
        package.status = "ARCHIVED"
        case.status = "GRANTED"
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

        resolved = _ensure(db, case_id=case.id)

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


def test_non_not_filed_case_without_package_fails_without_creating(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db, status="ACCEPTED")

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, case_id=case.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "FILING_PREPARATION_CASE_STATE_INVALID"
        assert (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.case_id == case.id,
                    OfficialWorkPackage.package_kind == "FILING_PREP",
                )
            )
            .scalars()
            .all()
            == []
        )


@pytest.mark.parametrize("existing_count", [1, 2])
def test_corrupt_filing_identity_returns_conflict_without_creating(
    session_factory: sessionmaker,
    existing_count: int,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        db.add_all(
            [
                OfficialWorkPackage(
                    id=str(uuid4()),
                    case_id=case.id,
                    package_kind="FILING_PREP",
                    status="PREPARING",
                    resolve_key=None,
                )
                for _ in range(existing_count)
            ]
        )
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, case_id=case.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "FILING_PREPARATION_IDENTITY_CONFLICT"
        assert (
            len(
                db.execute(
                    select(OfficialWorkPackage).where(
                        OfficialWorkPackage.case_id == case.id,
                        OfficialWorkPackage.package_kind == "FILING_PREP",
                    )
                )
                .scalars()
                .all()
            )
            == existing_count
        )


def test_missing_case_returns_not_found(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, case_id=str(uuid4()))

        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "CASE_NOT_FOUND"


def test_unique_race_rereads_committed_winner(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        original_flush = db.flush
        winner_id: list[str] = []

        def racing_flush(*args, **kwargs) -> None:
            monkeypatch.setattr(db, "flush", original_flush)
            db.rollback()
            with session_factory() as rival_db:
                winner = _ensure(rival_db, case_id=case.id)
                winner_id.append(winner.package.id)
            raise IntegrityError("simulated unique-key race", {}, Exception())

        monkeypatch.setattr(db, "flush", racing_flush)

        resolved = _ensure(db, case_id=case.id)

        assert resolved.package.id == winner_id[0]
        packages = (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.case_id == case.id,
                    OfficialWorkPackage.package_kind == "FILING_PREP",
                )
            )
            .scalars()
            .all()
        )
        assert [package.id for package in packages] == winner_id


def test_unique_collision_without_exact_winner_returns_identity_conflict(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        case = _create_case(db)
        db.add(
            OfficialWorkPackage(
                id=str(uuid4()),
                case_id=case.id,
                package_kind="OTHER_KIND",
                status="PREPARING",
                resolve_key=f"FILING_PREP:{case.id}",
            )
        )
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            _ensure(db, case_id=case.id)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "FILING_PREPARATION_IDENTITY_CONFLICT"
        assert (
            db.execute(
                select(OfficialWorkPackage).where(
                    OfficialWorkPackage.case_id == case.id,
                    OfficialWorkPackage.package_kind == "FILING_PREP",
                )
            )
            .scalars()
            .all()
            == []
        )
