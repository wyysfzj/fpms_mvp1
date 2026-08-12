from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "docs" / "product" / "v8" / "coverage-ledger.json"
CHECKER_PATH = REPO_ROOT / "scripts" / "v8_lean_coverage_check.py"
REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "product"
    / "v8"
    / "reviews"
    / "V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION.md"
)
STORY_ID = "V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION"
CATALOG_IDS = {
    "FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01",
    "FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01",
    "FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01",
    "FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01",
    "FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01",
    "FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01",
    "FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01",
    "FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01",
    "FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01",
    "FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01",
    "FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01",
    "FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01",
    "FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01",
    "FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01",
    "FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01",
    "FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01",
    "FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01",
    "FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01",
    "FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01",
}
FINGERPRINT_PATHS = {
    "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-official-payment-workbook-ui.spec.ts",
    "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-official-workbook-acceptance-ui.spec.ts",
    "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-official-workbook-live.spec.ts",
    "backend/alembic/versions/v8_payment_workbook_input_version.py",
    "backend/alembic/versions/v8_w6_service_price_book.py",
    "backend/app/models/__init__.py",
    "backend/app/main.py",
    "backend/app/modules/annuity/api.py",
    "backend/app/modules/annuity/models.py",
    "backend/app/modules/annuity/official_payment_workbook_input_schemas.py",
    "backend/app/modules/annuity/official_payment_workbook_input_service.py",
    "backend/app/modules/annuity/schemas.py",
    "backend/app/modules/annuity/service.py",
    "backend/app/modules/annuity/verified_official_payment_workbook.py",
    "backend/app/modules/fees/api.py",
    "backend/app/modules/fees/models.py",
    "backend/app/modules/fees/obligation_schemas.py",
    "backend/app/modules/fees/obligation_service.py",
    "backend/app/modules/fees/service_price_book.py",
    "backend/app/modules/fees/service_price_book_schemas.py",
    "backend/tests/fixtures/v8_verified_official_payment_template.xlsm",
    "backend/tests/test_v8_input_activation_capability_close.py",
    "backend/tests/test_v8_official_payment_workbook_adapter.py",
    "backend/tests/test_v8_official_payment_workbook_api.py",
    "backend/tests/test_v8_official_payment_workbook_generation_service.py",
    "backend/tests/test_v8_official_workbook_acceptance_api.py",
    "backend/tests/test_v8_official_workbook_acceptance_service.py",
    "backend/tests/test_v8_official_workbook_cors_headers.py",
    "backend/tests/test_v8_payment_workbook_input_api.py",
    "backend/tests/test_v8_payment_workbook_input_service.py",
    "backend/tests/test_v8_payment_workbook_input_version.py",
    "backend/tests/test_v8_payment_workbook_manifest_contract.py",
    "backend/tests/test_v8_service_price_book_activation.py",
    "backend/tests/test_v8_service_price_book_activation_api.py",
    "backend/tests/test_v8_service_price_book_import.py",
    "backend/tests/test_v8_service_price_book_import_api.py",
    "backend/tests/test_v8_service_price_book_schema.py",
    "backend/tests/test_v8_service_rate_manifest_contract.py",
    "backend/tests/test_v8_service_receivable_obligation.py",
    "backend/tests/test_v8_service_receivable_obligation_api.py",
    "docs/product/v8/reviews/V8-INPUT-ACTIVATION-CAPABILITY-CURRENT-ADOPTION.md",
    "frontend/src/api/contracts/v8_official_payment_workbook.contract.ts",
    "frontend/src/api/contracts/v8_official_workbook_acceptance.contract.ts",
    "frontend/src/api/govPayments.ts",
    "frontend/src/api/govPayments.types.ts",
    "frontend/src/modules/annuity/pages/PayListDetail.vue",
    "tasks/batches/FPMS-POSTDEMO-V8-PAYMENT-WORKBOOK-GATE-20260712-01.md",
    "tasks/batches/FPMS-POSTDEMO-V8-SERVICE-RATE-GATE-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-CORS-EXPOSURE-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-GENERATED-STATUS-HEADER-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-IDEMPOTENCY-CARRIER-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md",
    "docs/product/v8/full-terminal-dependency-successor.json",
    "docs/product/v8/stories/V8-FULL-TERMINAL-DEPENDENCY-SUCCESSOR-CONTRACT.md",
    "docs/product/v8/stories/V8-INPUT-ACTIVATION-CAPABILITY-LEDGER-ADOPTION.md",
    "scripts/v8_lean_coverage_check.py",
    "scripts/tests/test_v8_lean_coverage_check.py",
    "scripts/tests/test_v8_input_activation_capability_ledger_adoption.py",
    "tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-LEDGER-ADOPTION-20260813-01.md",
}


def _load_checker():
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text())


def test_exact_nineteen_rows_resolve_to_one_current_capability_story() -> None:
    ledger = _ledger()
    rows = {
        row["catalog_id"]: row
        for row in ledger["rows"]
        if row["catalog_id"] in CATALOG_IDS
    }

    assert set(rows) == CATALOG_IDS
    assert len(rows) == 19
    for row in rows.values():
        assert row["disposition"] == "CURRENT_VERIFIED"
        assert row["story_id"] == STORY_ID
        assert row["successor_story_id"] is None
        assert row["blocker"] is None


def test_story_separates_ready_capability_from_unconfigured_production() -> None:
    ledger = _ledger()
    stories = {story["story_id"]: story for story in ledger["stories"]}
    story = stories[STORY_ID]

    assert story["status"] == "CURRENT_VERIFIED"
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == (
        "docs/product/v8/reviews/"
        "V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION.md"
    )
    assert story["verification_ref"] == story["review_ref"]
    assert story["capability_status"] == "CAPABILITY_READY"
    assert story["production_inputs"] == {
        "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
        "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED",
    }
    assert story["production_failure"] == "409 / NO WRITE"
    assert story["production_activation_claimed"] is False
    assert set(story["paths"]) == FINGERPRINT_PATHS
    assert len(story["paths"]) == 63


def test_protected_story_has_exact_independent_approval_record() -> None:
    ledger = _ledger()
    story = next(story for story in ledger["stories"] if story["story_id"] == STORY_ID)
    review = REVIEW_PATH.read_text()

    assert "Verdict: APPROVED" in review
    assert "P0: 0" in review
    assert "P1: 0" in review
    assert "P2: 0" in review
    assert story["commits"][-1] in review


def test_story_fingerprint_binds_candidate_and_current_product_bytes() -> None:
    checker = _load_checker()
    ledger = _ledger()
    story = next(story for story in ledger["stories"] if story["story_id"] == STORY_ID)
    candidate_sha = story["commits"][-1]
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert subprocess.run(
        ["git", "merge-base", "--is-ancestor", candidate_sha, head_sha],
        cwd=REPO_ROOT,
        check=False,
    ).returncode == 0
    assert story["tree_sha256"] == checker.compute_tree_fingerprint(
        REPO_ROOT,
        candidate_sha,
        story["paths"],
    )


def test_row199_and_terminal_rows_remain_outside_this_adoption() -> None:
    ledger = _ledger()
    rows = {row["catalog_id"]: row for row in ledger["rows"]}
    excluded = {
        "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01",
        "FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01",
        "FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01",
        "FPMS-V8-FINAL-CLOSE-20260712-01",
    }

    assert all(rows[catalog_id]["story_id"] != STORY_ID for catalog_id in excluded)
