import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tasks" / "batches" / "FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md"
ACTIVATION_ID = "FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01"
TASK_IDS = [
    ACTIVATION_ID,
    "FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01",
]
TASK_PATHS = [f"tasks/postdemo/v8/{task_id}.md" for task_id in TASK_IDS]


def _manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def _task_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## \d{3}\. (FPMS-V8-[A-Z0-9-]+)$", text, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[match.start() : end]
    return sections


def test_manifest_has_exact_activation_and_four_candidate_tasks_in_catalog_order() -> None:
    text = _manifest_text()
    declared_count = re.findall(r"^Task count: (\d+)$", text, re.MULTILINE)
    declared_paths = re.findall(
        r"^- Task file: `(tasks/postdemo/v8/[^`]+\.md)`$", text, re.MULTILINE
    )

    assert declared_count == ["5"]
    assert declared_paths == TASK_PATHS
    assert list(_task_sections(text)) == TASK_IDS
    assert len(declared_paths) == len(set(declared_paths))


def test_manifest_binds_approved_policy_without_inventing_runtime_source() -> None:
    text = _manifest_text()

    required_contract = (
        "DG-GRANT-EVIDENCE-SOURCE:GLOBAL",
        "APPROVED_POLICY / CONFIG_REQUIRED",
        "e5a41c8d07f11d1b0dec68891ef7bef53312f883",
        "72877386974cd57c720b7c622e6b00ca49c03d7d",
        "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1",
        "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace",
        "Product development: ELIGIBLE",
        "Runtime source configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST",
        "missing, stale or unreviewed",
        "409 / NO WRITE / NO LEGAL-STATE CHANGE",
        "Archive every candidate as unverified",
        "No concrete CNIPA source is selected, defaulted or seeded by this manifest",
    )
    for contract in required_contract:
        assert contract in text

    assert "www.cnipa.gov.cn" not in text
    assert "cnipa.gov.cn/attach" not in text


def test_manifest_preserves_per_task_closure_dependencies_and_serialization() -> None:
    text = _manifest_text()
    sections = _task_sections(text)
    expected = {
        ACTIVATION_ID: (
            "Create only this five-row grant-source lane manifest",
            "No product code, schema, catalog or coverage-ledger change",
            "FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01",
            "backend/tests/test_v8_grant_source_gate_manifest_contract.py",
        ),
        "FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01": (
            "archive it unverified and never change legal state",
            "No endpoint/UI/schema",
            "FPMS-V8-DE-REGISTER-VERSION-20260712-01",
            "tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md",
            "backend/app/modules/documents/grant_evidence_ingestion_service.py",
            "artifacts/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01/**",
        ),
        "FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01": (
            "return 201 candidate, 409 unresolved gate/source conflict and no legal-state change",
            "No second endpoint, router rewiring, business-rule duplication or frontend work",
            "FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01",
            "tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md",
            "backend/app/modules/documents/api.py",
            "artifacts/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01/**",
        ),
        "FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01": (
            "no legal-state inference or write",
            "No endpoint/UI/schema",
            "FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01",
            "tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md",
            "backend/tests/test_v8_grant_evidence_candidate_read_service.py",
            "artifacts/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01/**",
        ),
        "FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01": (
            "One bodyless GET `/documents/{document_id}/grant-evidence-candidates`",
            "No second endpoint, router rewiring, business-rule duplication or frontend work",
            "FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01",
            "tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md",
            "backend/app/modules/documents/grant_evidence_schemas.py",
            "artifacts/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01/**",
        ),
    }

    assert set(sections) == set(expected)
    for task_id, contracts in expected.items():
        for contract in contracts:
            assert contract in sections[task_id]

    assert (
        "grant_evidence_ingestion_service.py`: ingestion service before candidate read service"
        in text
    )
    assert (
        "documents/api.py` and `grant_evidence_schemas.py`: ingestion API before candidate list API"
        in text
    )
    assert "All SQLite-writing verification remains serialized" in text
    assert "Independent review is required per protected task" in text
