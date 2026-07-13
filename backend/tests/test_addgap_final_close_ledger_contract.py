from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tasks/batches/FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01.md"
LEDGER = ROOT / "docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md"

EXPECTED_GAPS = {
    "ADD-GAP-WIZARD-01",
    "ADD-GAP-WORKPKG-01",
    "ADD-GAP-OA-01",
    "ADD-GAP-RECEIPT-01",
    "ADD-GAP-CATALOG-01",
    "ADD-GAP-DEADLINE-01",
    "ADD-GAP-GRANT-01",
}

SUPPLEMENTAL_TASKS = {
    48: "FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    49: "FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    50: "FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    51: "FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    52: "FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01",
    53: "FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    54: "FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    55: "FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    56: "FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    57: "FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01",
    58: "FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01",
    59: "FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01",
    60: "FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01",
    61: "FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01",
    62: "FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01",
    63: "FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01",
    64: "FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02",
    65: "FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02",
    66: "FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02",
    67: "FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02",
    68: "FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02",
    69: "FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02",
    70: "FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01",
}


def _task_status(task_id: str) -> str:
    task_file = ROOT / f"tasks/additional_gaps/{task_id}.md"
    match = re.search(r"^Status: (\S+)$", task_file.read_text(), flags=re.MULTILINE)
    assert match, f"missing task status: {task_id}"
    return match.group(1)


def _assert_task_gate_evidence(task_id: str) -> None:
    artifact = ROOT / "artifacts" / task_id
    for relative_path in ("summary.md", "results.jsonl", "git/diff.patch", "task.json"):
        assert (artifact / relative_path).is_file(), f"{task_id}: missing {relative_path}"

    results = [
        json.loads(line)
        for line in (artifact / "results.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert any(row.get("step") == "lint" and row.get("rc") == 0 for row in results), (
        f"{task_id}: missing successful task-gate lint evidence"
    )
    assert any(row.get("step") == "test" and row.get("rc") == 0 for row in results), (
        f"{task_id}: missing successful task-gate test evidence"
    )

    task_meta = json.loads((artifact / "task.json").read_text())
    if task_meta.get("baseline_dirty"):
        assert (artifact / "baseline_allowlist.diff").is_file()
        assert (artifact / "baseline_external_files.txt").is_file()


def _manifest_task_ids() -> list[str]:
    return re.findall(
        r"^- Task file: `tasks/additional_gaps/([^/`]+)\.md`$",
        MANIFEST.read_text(),
        flags=re.MULTILINE,
    )


def _markdown_rows(text: str, prefix: str) -> list[list[str]]:
    return [
        [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if line.startswith(prefix)
    ]


def test_final_close_ledger_contract() -> None:
    original_ids = _manifest_task_ids()
    assert len(original_ids) == len(set(original_ids)) == 47
    assert original_ids[-1] == "FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01"
    assert not set(SUPPLEMENTAL_TASKS.values()).intersection(original_ids)

    for task_id in original_ids[:-1]:
        assert _task_status(task_id) == "PASS", task_id
        _assert_task_gate_evidence(task_id)

    for task_id in SUPPLEMENTAL_TASKS.values():
        assert _task_status(task_id) == "PASS", task_id
        _assert_task_gate_evidence(task_id)

    assert LEDGER.is_file(), "final close ledger must be created after RED"
    ledger = LEDGER.read_text()

    gap_rows = _markdown_rows(ledger, "| `ADD-GAP-")
    assert len(gap_rows) == 7
    assert {row[0] for row in gap_rows} == EXPECTED_GAPS
    for row in gap_rows:
        assert len(row) == 7
        assert row[4].startswith("artifacts/")
        assert row[5] == "None"
        assert row[6] == "covered"

    task_rows = _markdown_rows(ledger, "| `Task")
    acceptance_rows = [row for row in task_rows if row[0] in {"Task45", "Task46", "Task47"}]
    assert [row[0] for row in acceptance_rows] == ["Task45", "Task46", "Task47"]

    supplemental_rows = [
        row for row in task_rows if row[0] in {f"Task{number}" for number in SUPPLEMENTAL_TASKS}
    ]
    assert len(supplemental_rows) == 23
    assert {row[0] for row in supplemental_rows} == {
        f"Task{number}" for number in SUPPLEMENTAL_TASKS
    }
    for row in supplemental_rows:
        number = int(row[0].removeprefix("Task"))
        assert len(row) == 8
        assert row[1] == SUPPLEMENTAL_TASKS[number]
        assert row[4].startswith(f"artifacts/{SUPPLEMENTAL_TASKS[number]}/")
        assert row[5] == "APPROVE / PASS"
        assert row[6] == "None"
        assert row[7] == "covered"

    required_sections = {
        "## Permission and status-code audit",
        "## Response-envelope and SQLite audit",
        "## Simplified Chinese UI audit",
        "## Verification evidence",
        "## Supplemental Tasks48–70 appendix",
    }
    assert all(section in ledger for section in required_sections)
