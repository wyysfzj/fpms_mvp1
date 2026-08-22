import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tasks" / "batches" / "FPMS-POSTDEMO-V8-LEGACY-FORM-010-GATE-20260712-01.md"

ACTIVATION_TASK = "tasks/postdemo/v8/FPMS-V8-LEGACY-FORM-010-MANIFEST-ACTIVATION-20260712-01.md"
OUT_010_TASK = "tasks/postdemo/v8/FPMS-V8-OUT-010-RIGHT-RESTORATION-20260712-01.md"
EXPECTED_DEPENDENCIES = (
    "FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01",
    "FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01",
    "FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01",
    "FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01",
    "FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01",
    "FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01",
)


@pytest.fixture(autouse=True)
def _reset_test_data() -> None:
    """Keep this filesystem contract suite out of the serialized SQLite queue."""


def _manifest_text() -> str:
    assert MANIFEST.is_file(), f"missing form-010 lane manifest: {MANIFEST}"
    return MANIFEST.read_text(encoding="utf-8")


def test_manifest_contains_only_activation_then_out_010() -> None:
    text = _manifest_text()
    declared_task_files = re.findall(r"^- Task file: `([^`]+)`$", text, re.MULTILINE)

    assert re.findall(r"^Task count: (\d+)$", text, re.MULTILINE) == ["2"]
    assert declared_task_files == [ACTIVATION_TASK, OUT_010_TASK]


def test_manifest_binds_internal_only_authority_and_prerequisites() -> None:
    text = _manifest_text()

    assert "DG-LEGACY-FORM-CLASS:form-010" in text
    assert "Classification: `INTERNAL_ONLY`" in text
    assert "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1" in text
    assert "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace" in text
    assert "e5a41c8d07f11d1b0dec68891ef7bef53312f883" in text
    assert "72877386974cd57c720b7c622e6b00ca49c03d7d" in text
    for task_id in EXPECTED_DEPENDENCIES:
        assert task_id in text


def test_manifest_preserves_reference_only_and_execution_boundaries() -> None:
    text = _manifest_text()

    assert "Reference/internal-only status preserved: yes" in text
    assert "Official submission activation: forbidden" in text
    assert "Other legacy-form lanes activated or blocked: none" in text
    assert "Product, schema, catalog and coverage-ledger changes: forbidden" in text
    assert "Child execution requires independently accepted activation: yes" in text
