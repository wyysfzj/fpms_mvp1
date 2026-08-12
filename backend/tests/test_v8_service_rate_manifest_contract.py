from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / ("tasks/batches/FPMS-POSTDEMO-V8-SERVICE-RATE-GATE-20260712-01.md")
MEMBER_PREFIX = "- Task file: `"
EXPECTED_MEMBERS = (
    "tasks/postdemo/v8/FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01.md",
)


def test_service_rate_lane_manifest_exists() -> None:
    assert MANIFEST.is_file(), "service-rate lane manifest is missing"


def test_service_rate_lane_has_exact_original_members() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    members = tuple(
        line.removeprefix(MEMBER_PREFIX).removesuffix("`")
        for line in text.splitlines()
        if line.startswith(MEMBER_PREFIX)
    )

    assert members == EXPECTED_MEMBERS
    assert "Task count: 8" in text
    assert "No external successor is a lane member" in text


def test_service_rate_lane_preserves_fail_closed_production_boundary() -> None:
    normalized = " ".join(MANIFEST.read_text(encoding="utf-8").split())

    for required in (
        "DG-SERVICE-RATE-VERSION:GLOBAL",
        "CAPABILITY_READY",
        "PRODUCTION_INPUT_ACTIVE",
        "production activation",
        "CONFIG_REQUIRED",
        "409 / NO WRITE",
        "does not block development",
        "PayList export-artifact carrier",
        "decision-gate read service",
        "global Alembic predecessor",
        "catalog-manifest coverage gate",
    ):
        assert required in normalized
