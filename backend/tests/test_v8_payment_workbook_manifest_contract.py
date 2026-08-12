from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tasks/batches/FPMS-POSTDEMO-V8-PAYMENT-WORKBOOK-GATE-20260712-01.md"
MEMBER_PREFIX = "- Task file: `"
EXPECTED_MEMBERS = (
    "tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01.md",
)
EXTERNAL_SUCCESSORS = (
    "FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01",
    "FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01",
    "FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01",
)


def test_payment_workbook_lane_manifest_exists() -> None:
    assert MANIFEST.is_file(), f"missing payment-workbook manifest: {MANIFEST}"


def test_payment_workbook_lane_has_exact_original_members() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    members = tuple(
        line.removeprefix(MEMBER_PREFIX).removesuffix("`")
        for line in text.splitlines()
        if line.startswith(MEMBER_PREFIX)
    )

    assert members == EXPECTED_MEMBERS
    assert "Task count: 11" in text
    assert all(successor in text for successor in EXTERNAL_SUCCESSORS)
    assert all(
        not member.endswith(f"{successor}.md")
        for member in members
        for successor in EXTERNAL_SUCCESSORS
    )


def test_payment_workbook_lane_preserves_fail_closed_production_boundary() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for required in (
        "DG-PAYMENT-WORKBOOK:GLOBAL",
        "CAPABILITY_READY",
        "PRODUCTION_INPUT_ACTIVE",
        "CONFIG_REQUIRED",
        "409 / NO WRITE",
        "does not block development",
        "external successor prerequisites only",
    ):
        assert required in normalized
