from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _build_gate_fixture(tmp_path: Path) -> Path:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    shutil.copy2(REPO_ROOT / "scripts/release_gate.sh", scripts_dir / "release_gate.sh")
    (scripts_dir / "task_validate.sh").write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$1" >> validation.log
test ! -f "artifacts/$1/fail"
""",
        encoding="utf-8",
    )
    (scripts_dir / "release_gate.sh").chmod(0o755)
    (scripts_dir / "task_validate.sh").chmod(0o755)
    return tmp_path


def _write_v8_manifest(root: Path, task_ids: list[str]) -> Path:
    manifest = root / "foundation.md"
    manifest.write_text(
        "# V8 foundation manifest\n\n"
        + "\n".join(f"- Task file: `tasks/postdemo/v8/{task_id}.md`" for task_id in task_ids)
        + "\n",
        encoding="utf-8",
    )
    return manifest


def test_v8_manifest_gate_parses_exact_v8_task_declaration(tmp_path: Path) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_v8_manifest(root, ["FPMS-V8-TASK-A"])

    result = subprocess.run(
        ["./scripts/release_gate.sh", "--manifest", manifest.name],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (root / "validation.log").read_text(encoding="utf-8").splitlines() == ["FPMS-V8-TASK-A"]
    assert "Release Gate: 1 passed, 0 failed" in result.stdout


def test_v8_manifest_gate_excludes_only_the_exact_task_id(tmp_path: Path) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_v8_manifest(
        root,
        ["FPMS-V8-SELF", "FPMS-V8-SELF-OTHER"],
    )

    result = subprocess.run(
        [
            "./scripts/release_gate.sh",
            "--manifest",
            manifest.name,
            "--exclude-task",
            "FPMS-V8-SELF",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (root / "validation.log").read_text(encoding="utf-8").splitlines() == [
        "FPMS-V8-SELF-OTHER"
    ]
    assert "Release Gate: 1 passed, 0 failed" in result.stdout


def test_v8_manifest_gate_rejects_duplicate_ids_before_validation(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = root / "foundation.md"
    manifest.write_text(
        "# Mixed manifest\n\n"
        "- Task file: `tasks/additional_gaps/FPMS-DUPLICATE.md`\n"
        "- Task file: `tasks/postdemo/v8/FPMS-DUPLICATE.md`\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["./scripts/release_gate.sh", "--manifest", manifest.name],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Duplicate task ID in manifest: FPMS-DUPLICATE" in result.stdout
    assert not (root / "validation.log").exists()


def test_v8_manifest_gate_rejects_malformed_declaration_before_validation(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_v8_manifest(root, ["FPMS-V8-TASK-A"])
    with manifest.open("a", encoding="utf-8") as stream:
        stream.write("- Task file: `tasks/postdemo/v8/nested/FPMS-V8-TASK-B.md`\n")

    result = subprocess.run(
        ["./scripts/release_gate.sh", "--manifest", manifest.name],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Manifest contains an invalid task-file declaration" in result.stdout
    assert not (root / "validation.log").exists()


def test_v8_manifest_gate_rejects_unknown_exclusion_before_validation(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_v8_manifest(root, ["FPMS-V8-TASK-A"])

    result = subprocess.run(
        [
            "./scripts/release_gate.sh",
            "--manifest",
            manifest.name,
            "--exclude-task",
            "FPMS-V8-NOT-LISTED",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Excluded task is not listed in manifest: FPMS-V8-NOT-LISTED" in result.stdout
    assert not (root / "validation.log").exists()


def test_v8_manifest_gate_propagates_selected_task_failure(tmp_path: Path) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_v8_manifest(
        root,
        ["FPMS-V8-TASK-PASS", "FPMS-V8-TASK-FAIL"],
    )
    failing_artifact = root / "artifacts/FPMS-V8-TASK-FAIL"
    failing_artifact.mkdir(parents=True)
    (failing_artifact / "fail").touch()

    result = subprocess.run(
        ["./scripts/release_gate.sh", "--manifest", manifest.name],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert (root / "validation.log").read_text(encoding="utf-8").splitlines() == [
        "FPMS-V8-TASK-PASS",
        "FPMS-V8-TASK-FAIL",
    ]
    assert "Release Gate: 1 passed, 1 failed" in result.stdout


def test_foundation_manifest_parses_all_197_tasks_with_exact_self_exclusion(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = root / "foundation.md"
    shutil.copy2(
        REPO_ROOT / "tasks/batches/FPMS-POSTDEMO-V8-FOUNDATION-20260712-01.md",
        manifest,
    )
    excluded = "FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01"

    result = subprocess.run(
        [
            "./scripts/release_gate.sh",
            "--manifest",
            manifest.name,
            "--exclude-task",
            excluded,
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    validated = (root / "validation.log").read_text(encoding="utf-8").splitlines()
    assert len(validated) == 196
    assert validated[0] == "FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01"
    assert validated[-1] == "FPMS-V8-FOUNDATION-CLOSE-20260712-01"
    assert excluded not in validated
    assert "Release Gate: 196 passed, 0 failed" in result.stdout
