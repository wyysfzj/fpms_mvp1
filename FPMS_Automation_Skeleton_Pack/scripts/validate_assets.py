from __future__ import annotations

from pathlib import Path

import yaml

from audit_current_coverage import build_audit, validate_audit

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    all_cases = load_yaml(ROOT / "data" / "testcases" / "all_testcases.yaml")[
        "testcases"
    ]
    boundary_cases = load_yaml(ROOT / "data" / "boundary" / "boundary_matrix.yaml")[
        "boundary_cases"
    ]
    wave_manifest = load_yaml(ROOT / "data" / "manifests" / "wave_manifest.yaml")[
        "waves"
    ]

    assert len(all_cases) == 170, f"Expected 170 cases, got {len(all_cases)}"
    assert len(boundary_cases) == 20, (
        f"Expected 20 boundary cases, got {len(boundary_cases)}"
    )

    ids = [case["id"] for case in all_cases]
    assert len(ids) == len(set(ids)), "Duplicate testcase IDs found"

    by_wave: dict[str, int] = {}
    for case in all_cases:
        by_wave[case["wave"]] = by_wave.get(case["wave"], 0) + 1

    for wave in wave_manifest:
        expected = wave["case_count"]
        actual = by_wave.get(wave["wave"], 0)
        assert actual == expected, (
            f"Wave {wave['wave']} expected {expected}, got {actual}"
        )

    coverage_audit = build_audit()
    coverage_errors = validate_audit(coverage_audit)
    assert not coverage_errors, "; ".join(coverage_errors)
    coverage_summary = coverage_audit["summary"]

    print("Asset validation passed.")
    print(
        f"Cases: {len(all_cases)} | Boundary: {len(boundary_cases)} | Waves: {len(wave_manifest)}"
    )
    print(
        "Current coverage: "
        f"backend_routes={coverage_summary['backend_route_count']} | "
        f"frontend_routes={coverage_summary['frontend_route_count']} | "
        f"pytest_real={coverage_summary['pytest_real_handler_count']} | "
        f"playwright_real={coverage_summary['playwright_real_handler_count']} | "
        f"cases_without_real={coverage_summary['cases_without_real_handler_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
