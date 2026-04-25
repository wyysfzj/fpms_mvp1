from __future__ import annotations

from framework.data_loader import load_all_cases, load_boundary_cases


def test_asset_integrity_counts() -> None:
    all_cases = load_all_cases()
    boundary_cases = load_boundary_cases()
    assert len(all_cases) == 155
    assert len(boundary_cases) == 20
    assert len({case.id for case in all_cases}) == 155
