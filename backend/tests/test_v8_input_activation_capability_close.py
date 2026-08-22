from __future__ import annotations

import ast
import json
import re
from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import FeeObligation, FeeObligationLine
from app.modules.fees.obligation_service import (
    CreateServiceReceivableObligationCommand,
    create_service_receivable_obligation,
)

ROOT = __file__.rsplit("/backend/tests/", 1)[0]
RECEIPT_PATH = "docs/product/v8/reviews/V8-INPUT-ACTIVATION-CAPABILITY-CURRENT-ADOPTION.md"
TASK_PATH = "tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md"
NOW = datetime(2026, 8, 13, 19, 0)

DECISIVE_PROOFS = (
    (
        "backend/tests/test_v8_payment_workbook_input_service.py",
        "test_test_only_isolated_resolution_never_activates_or_becomes_current",
    ),
    (
        "backend/tests/test_v8_payment_workbook_input_service.py",
        "test_test_resolution_rejects_ambiguity_and_production_rejects_test_only",
    ),
    (
        "backend/tests/test_v8_official_payment_workbook_generation_service.py",
        "test_missing_or_test_only_production_input_fails_409_without_side_effects",
    ),
    (
        "backend/tests/test_v8_official_payment_workbook_generation_service.py",
        "test_missing_or_mismatched_production_gate_fails_without_write",
    ),
    (
        "backend/tests/test_v8_service_price_book_import.py",
        "test_test_only_requires_explicit_test_profile_and_retains_classification",
    ),
    (
        "backend/tests/test_v8_service_price_book_activation.py",
        "test_malformed_or_test_only_candidate_is_409_without_mutation",
    ),
    (
        "backend/tests/test_v8_service_price_book_activation.py",
        "test_missing_or_mismatched_gate_is_409",
    ),
    (
        "backend/tests/test_v8_service_price_book_activation.py",
        "test_test_runtime_and_same_creator_are_409",
    ),
    (
        "backend/tests/test_v8_service_receivable_obligation.py",
        "test_active_item_creates_service_obligation_and_caller_owns_transaction",
    ),
    (
        "backend/tests/test_v8_service_receivable_obligation.py",
        "test_noncanonical_book_hash_is_409_without_receivable_write",
    ),
)


def _read(path: str) -> str:
    with open(f"{ROOT}/{path}", encoding="utf-8") as stream:
        return stream.read()


def _capability_state(receipt: str) -> dict[str, object]:
    match = re.search(r"## Capability receipt\n\n```json\n(.*?)\n```", receipt, re.DOTALL)
    assert match is not None
    return json.loads(match.group(1))


def test_receipt_records_capability_ready_without_production_activation() -> None:
    receipt = _read(RECEIPT_PATH)
    assert _capability_state(receipt) == {
        "capability": "CAPABILITY_READY",
        "payment_workbook": "CONFIG_REQUIRED",
        "service_rate": "CONFIG_REQUIRED",
        "production_activation_claimed": False,
    }
    assert "DG-PAYMENT-WORKBOOK:GLOBAL" in receipt
    assert "DG-SERVICE-RATE-VERSION:GLOBAL" in receipt
    assert "409 / NO WRITE" in receipt
    registry = _read("docs/product/v8/source-decision-registry.md")
    assert "| `DG-PAYMENT-WORKBOOK` | `PENDING` |" in registry
    assert "| `DG-SERVICE-RATE-VERSION` | `PENDING` |" in registry


def test_receipt_binds_each_decisive_negative_and_isolation_proof() -> None:
    receipt = _read(RECEIPT_PATH)
    for path, test_name in DECISIVE_PROOFS:
        source = _read(path)
        functions = {
            node.name for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)
        }
        assert test_name in functions
        assert f"{path}::{test_name}" in receipt
    assert "6a17a18" in receipt
    assert "97771c2" in receipt
    assert "Independent row 278 review: APPROVED" in receipt
    assert "P0/P1/P2: 0/0/0" in receipt


def test_missing_service_price_configuration_is_409_without_product_write(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = "case-capability-config-required"
    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).order_by(T_User.id))
        assert actor_id is not None
        transaction.add(
            Case(
                id=case_id,
                case_no="CASE-CAPABILITY-CLOSE",
                client_id=None,
                status="NOT_FILED",
            )
        )
        transaction.commit()
        before = (
            transaction.scalar(select(func.count()).select_from(FeeObligation)),
            transaction.scalar(select(func.count()).select_from(FeeObligationLine)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
        )

        with pytest.raises(BusinessError) as caught:
            create_service_receivable_obligation(
                CreateServiceReceivableObligationCommand(
                    price_book_version_id="11111111-1111-4111-8111-111111111999",
                    item_code="CONFIG-REQUIRED",
                    case_id=case_id,
                    actor_id=actor_id,
                    idempotency_key="capability-close-config-required",
                    recognized_at=NOW,
                ),
                transaction,
            )

        assert caught.value.code == "SERVICE_RECEIVABLE_CONFLICT"
        assert caught.value.status_code == 409
        assert (
            transaction.scalar(select(func.count()).select_from(FeeObligation)),
            transaction.scalar(select(func.count()).select_from(FeeObligationLine)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
        ) == before
        transaction.rollback()


def test_task_close_remains_qa_only_and_requires_independent_review() -> None:
    task = _read(TASK_PATH)
    assert "Status: REVIEW REQUIRED / CAPABILITY EVIDENCE GREEN" in task
    assert "QA-only" in task
    assert "CAPABILITY_READY + CONFIG_REQUIRED" in task
    assert "never claims production activation" in task
    assert "Independent High review" in task
    assert "No product fix" in task
