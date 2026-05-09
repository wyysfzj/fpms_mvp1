from __future__ import annotations

import sys
from pathlib import Path

from framework.data_loader import load_all_cases, load_boundary_cases

PACK_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACK_ROOT / "scripts"))

from audit_current_coverage import build_audit, validate_audit  # noqa: E402


def test_asset_integrity_counts() -> None:
    all_cases = load_all_cases()
    boundary_cases = load_boundary_cases()
    assert len(all_cases) == 170
    assert len(boundary_cases) == 20
    assert len({case.id for case in all_cases}) == 170


def test_current_implementation_coverage_audit_contract() -> None:
    audit = build_audit()
    assert validate_audit(audit) == []

    summary = audit["summary"]
    assert summary["canonical_case_count"] == 170
    assert summary["backend_route_count"] >= 160
    assert summary["frontend_route_count"] >= 63
    assert summary["cases_without_any_handler_count"] == 0
    assert summary["pytest_real_handler_count"] >= 54
    assert summary["playwright_real_handler_count"] >= 1
    assert summary["cases_without_real_handler_count"] > 0
