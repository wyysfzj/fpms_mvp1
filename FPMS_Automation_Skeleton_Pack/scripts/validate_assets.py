from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main() -> int:
    all_cases = load_yaml(ROOT / "data" / "testcases" / "all_testcases.yaml")["testcases"]
    boundary_cases = load_yaml(ROOT / "data" / "boundary" / "boundary_matrix.yaml")["boundary_cases"]
    wave_manifest = load_yaml(ROOT / "data" / "manifests" / "wave_manifest.yaml")["waves"]

    assert len(all_cases) == 170, f"Expected 170 cases, got {len(all_cases)}"
    assert len(boundary_cases) == 20, f"Expected 20 boundary cases, got {len(boundary_cases)}"

    ids = [case["id"] for case in all_cases]
    assert len(ids) == len(set(ids)), "Duplicate testcase IDs found"

    by_wave: dict[str, int] = {}
    for case in all_cases:
        by_wave[case["wave"]] = by_wave.get(case["wave"], 0) + 1

    for wave in wave_manifest:
        expected = wave["case_count"]
        actual = by_wave.get(wave["wave"], 0)
        assert actual == expected, f"Wave {wave['wave']} expected {expected}, got {actual}"

    print("Asset validation passed.")
    print(f"Cases: {len(all_cases)} | Boundary: {len(boundary_cases)} | Waves: {len(wave_manifest)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
