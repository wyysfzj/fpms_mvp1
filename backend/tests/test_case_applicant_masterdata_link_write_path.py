from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.errors import BusinessError
from app.modules.cases.models import T_CaseApplicant
from app.modules.cases.schemas import CaseCreate, CaseUpdateFull
from app.modules.cases.service import create_case, update_case_full
from app.modules.masterdata.applicants.models import Applicant


def _seed_applicant(session_factory, *, code: str, name_cn: str) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=code,
                name_cn=name_cn,
                name_en=None,
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def test_create_case_persists_case_applicant_applicant_id(session_factory) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        code=f"APP-{uuid4().hex[:8].upper()}",
        name_cn=f"测试申请人甲-{uuid4().hex[:4]}",
    )

    with session_factory() as db:
        case = create_case(
            db,
            CaseCreate(
                case_no=f"CASE-{uuid4().hex[:8].upper()}",
                fee_reduction="0",
                applicants=[
                    {
                        "seq": 1,
                        "is_first": True,
                        "name_cn": "测试申请人甲",
                        "applicant_id": applicant_id,
                    }
                ],
            ),
            user_id="test-user",
        )

        case_applicant = db.execute(
            select(T_CaseApplicant).where(T_CaseApplicant.case_id == case.id)
        ).scalar_one()

    assert case_applicant.applicant_id == applicant_id


def test_update_case_full_persists_case_applicant_applicant_id(session_factory) -> None:
    initial_applicant_id = _seed_applicant(
        session_factory,
        code=f"APP-{uuid4().hex[:8].upper()}",
        name_cn=f"测试申请人甲-{uuid4().hex[:4]}",
    )
    updated_applicant_id = _seed_applicant(
        session_factory,
        code=f"APP-{uuid4().hex[:8].upper()}",
        name_cn=f"测试申请人乙-{uuid4().hex[:4]}",
    )

    with session_factory() as db:
        case = create_case(
            db,
            CaseCreate(
                case_no=f"CASE-{uuid4().hex[:8].upper()}",
                fee_reduction="0",
                applicants=[
                    {
                        "seq": 1,
                        "is_first": True,
                        "name_cn": "测试申请人甲",
                        "applicant_id": initial_applicant_id,
                    }
                ],
            ),
            user_id="test-user",
        )

        update_case_full(
            db,
            case.id,
            CaseUpdateFull(
                applicants=[
                    {
                        "seq": 1,
                        "is_first": True,
                        "name_cn": "测试申请人乙",
                        "applicant_id": updated_applicant_id,
                    }
                ],
            ),
            user_id="test-user",
        )

        case_applicant = db.execute(
            select(T_CaseApplicant).where(T_CaseApplicant.case_id == case.id)
        ).scalar_one()

    assert case_applicant.applicant_id == updated_applicant_id


def test_create_case_rejects_unknown_applicant_id(session_factory) -> None:
    with session_factory() as db:
        with pytest.raises(BusinessError) as exc_info:
            create_case(
                db,
                CaseCreate(
                    case_no=f"CASE-{uuid4().hex[:8].upper()}",
                    fee_reduction="0",
                    applicants=[
                        {
                            "seq": 1,
                            "is_first": True,
                            "name_cn": "测试申请人甲",
                            "applicant_id": str(uuid4()),
                        }
                    ],
                ),
                user_id="test-user",
            )

    assert exc_info.value.code == "APPLICANT_NOT_FOUND"
    assert exc_info.value.status_code == 404


def test_update_case_full_rejects_unknown_applicant_id(session_factory) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        code=f"APP-{uuid4().hex[:8].upper()}",
        name_cn=f"测试申请人甲-{uuid4().hex[:4]}",
    )

    with session_factory() as db:
        case = create_case(
            db,
            CaseCreate(
                case_no=f"CASE-{uuid4().hex[:8].upper()}",
                fee_reduction="0",
                applicants=[
                    {
                        "seq": 1,
                        "is_first": True,
                        "name_cn": "测试申请人甲",
                        "applicant_id": applicant_id,
                    }
                ],
            ),
            user_id="test-user",
        )

        with pytest.raises(BusinessError) as exc_info:
            update_case_full(
                db,
                case.id,
                CaseUpdateFull(
                    applicants=[
                        {
                            "seq": 1,
                            "is_first": True,
                            "name_cn": "测试申请人乙",
                            "applicant_id": str(uuid4()),
                        }
                    ],
                ),
                user_id="test-user",
            )

    assert exc_info.value.code == "APPLICANT_NOT_FOUND"
    assert exc_info.value.status_code == 404


def test_blank_applicant_id_normalizes_to_none_on_create_and_update(session_factory) -> None:
    with session_factory() as db:
        case = create_case(
            db,
            CaseCreate(
                case_no=f"CASE-{uuid4().hex[:8].upper()}",
                fee_reduction="0",
                applicants=[
                    {
                        "seq": 1,
                        "is_first": True,
                        "name_cn": "测试申请人甲",
                        "applicant_id": "   ",
                    }
                ],
            ),
            user_id="test-user",
        )

        case_applicant = db.execute(
            select(T_CaseApplicant).where(T_CaseApplicant.case_id == case.id)
        ).scalar_one()
        assert case_applicant.applicant_id is None

        update_case_full(
            db,
            case.id,
            CaseUpdateFull(
                applicants=[
                    {
                        "seq": 1,
                        "is_first": True,
                        "name_cn": "测试申请人乙",
                        "applicant_id": "\t",
                    }
                ],
            ),
            user_id="test-user",
        )

        updated_case_applicant = db.execute(
            select(T_CaseApplicant).where(T_CaseApplicant.case_id == case.id)
        ).scalar_one()

    assert updated_case_applicant.applicant_id is None
