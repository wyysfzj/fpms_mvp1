import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tasks" / "batches" / "FPMS-POSTDEMO-V8-APPLICATION-DRAFT-GATE-20260712-01.md"

ACTIVATION_TASK = "tasks/postdemo/v8/FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01.md"
SUCCESSOR_TASK = (
    "tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md"
)
SUPERSEDED_TASK = "tasks/postdemo/v8/FPMS-V8-APPLICATION-AUTO-DRAFT-POLICY-20260712-01.md"
SUCCESSOR_SHARED_FILES = [
    "fee_linking_service.py",
    "obligation_contracts.py",
    "obligation_service.py",
    "annuity/service.py",
    "cases/lifecycle_overlay_service.py",
]

GATE_SOURCE_COMMIT = "e5a41c8d07f11d1b0dec68891ef7bef53312f883"
GATE_ADOPTION_COMMIT = "72877386974cd57c720b7c622e6b00ca49c03d7d"
GATE_DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
GATE_SOURCE_SHA256 = "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace"


def _manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def _metadata(text: str, label: str) -> str:
    matches = re.findall(rf"^- {re.escape(label)}: `([^`]+)`$", text, re.MULTILINE)
    assert len(matches) == 1, f"expected one exact {label} declaration"
    return matches[0]


def test_manifest_contains_only_activation_then_internal_draft_successor() -> None:
    text = _manifest_text()
    task_files = re.findall(r"^- Task file: `([^`]+)`$", text, re.MULTILINE)
    controller_tasks = re.findall(r"^Controller task: `([^`]+)`$", text, re.MULTILINE)

    assert _metadata(text, "Manifest phase") == "lane"
    assert _metadata(text, "Task count") == "2"
    assert controller_tasks == [ACTIVATION_TASK.removesuffix(".md").split("/")[-1]]
    assert task_files == [ACTIVATION_TASK, SUCCESSOR_TASK]
    assert len(task_files) == len(set(task_files))
    assert task_files.count(SUCCESSOR_TASK) == 1
    assert task_files.count(SUPERSEDED_TASK) == 0
    assert _metadata(text, "SELF_PENDING") == ACTIVATION_TASK.removesuffix(".md").split("/")[-1]


def test_manifest_binds_the_accepted_application_draft_policy() -> None:
    text = _manifest_text()

    assert _metadata(text, "Gate identity") == "DG-FEE-APPLICATION-DRAFT:GLOBAL"
    assert _metadata(text, "Gate status") == "APPROVED_POLICY"
    assert _metadata(text, "Decision version") == GATE_DECISION_VERSION
    assert _metadata(text, "Decision source SHA-256") == GATE_SOURCE_SHA256
    assert _metadata(text, "Decision source commit") == GATE_SOURCE_COMMIT
    assert _metadata(text, "Decision adoption commit") == GATE_ADOPTION_COMMIT
    assert _metadata(text, "Draft trigger") == "reviewed-real-application-fee-notice"
    assert _metadata(text, "Draft result") == "one-internal-pending-review-draft"
    assert _metadata(text, "Payment boundary") == "client-instruction-required"


def test_manifest_binds_current_prerequisites_and_serial_activation_order() -> None:
    text = _manifest_text()
    execution_order = re.search(
        r"^## Execution order\n\n(?P<body>.*?)(?=^## )",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert execution_order is not None
    shared_files = re.findall(r"`([^`]+\.py)`", execution_order.group("body"))
    prerequisite_rows = re.findall(
        r"^\| `([^`]+)` \| `([^`]+)` \| `CURRENT_VERIFIED` \|$",
        text,
        re.MULTILINE,
    )

    assert prerequisite_rows == [
        (
            "FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01",
            "C3-LEAN-LEDGER-INTEGRATION-REF-CORRECTION",
        ),
        (
            "FPMS-V8-FO-PREPARE-DRAFT-20260712-01",
            "V8-FEE-OBLIGATION-READ-DRAFT-CURRENT-ADOPTION",
        ),
        (
            "FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01",
            "V8-APPLICATION-FEE-NOTICE-OBLIGATION-CURRENT-ADOPTION",
        ),
    ]
    assert shared_files == SUCCESSOR_SHARED_FILES
    assert _metadata(text, "Activation review") == "independent-high-zero-finding-required"
    assert _metadata(text, "Product start") == "after-activation-pass-only"
    assert _metadata(text, "SQLite verification") == "globally-serialized"
