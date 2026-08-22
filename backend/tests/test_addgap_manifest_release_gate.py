from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="superseded by the C3.1 Git-native release gate; old taskctl manifests are retired"
)

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


def _write_manifest(root: Path, task_ids: list[str]) -> Path:
    manifest = root / "batch.md"
    manifest.write_text(
        "# Test manifest\n\n"
        + "\n".join(
            f"### {index:02d} — `{task_id}`\n\n- Task file: `tasks/additional_gaps/{task_id}.md`"
            for index, task_id in enumerate(task_ids, 1)
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def test_manifest_gate_validates_only_listed_tasks_and_honors_exclusion(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_manifest(root, ["TASK-A", "TASK-B", "TASK-C"])

    result = subprocess.run(
        [
            "./scripts/release_gate.sh",
            "--manifest",
            manifest.name,
            "--exclude-task",
            "TASK-B",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (root / "validation.log").read_text(encoding="utf-8").splitlines() == [
        "TASK-A",
        "TASK-C",
    ]
    assert "Release Gate: 2 passed, 0 failed" in result.stdout


def test_no_argument_gate_keeps_enh_artifact_discovery_and_failure_semantics(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    (root / "artifacts/ENH-A").mkdir(parents=True)
    failing_artifact = root / "artifacts/ENH-B"
    failing_artifact.mkdir()
    (failing_artifact / "fail").touch()

    result = subprocess.run(
        ["./scripts/release_gate.sh"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert (root / "validation.log").read_text(encoding="utf-8").splitlines() == [
        "ENH-A",
        "ENH-B",
    ]
    assert "Release Gate: 1 passed, 1 failed" in result.stdout


@pytest.mark.parametrize(
    ("task_ids", "excluded_task"),
    [
        ([], None),
        (["TASK-A", "TASK-A"], None),
        (["TASK-A"], "TASK-NOT-LISTED"),
    ],
)
def test_manifest_gate_rejects_empty_duplicate_or_unknown_exclusion(
    tmp_path: Path,
    task_ids: list[str],
    excluded_task: str | None,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_manifest(root, task_ids)
    command = ["./scripts/release_gate.sh", "--manifest", manifest.name]
    if excluded_task is not None:
        command.extend(["--exclude-task", excluded_task])

    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0


def test_manifest_gate_propagates_selected_task_failure(tmp_path: Path) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_manifest(root, ["TASK-PASS", "TASK-FAIL"])
    failing_artifact = root / "artifacts/TASK-FAIL"
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
    assert "Release Gate: 1 passed, 1 failed" in result.stdout


def test_program_manifest_extracts_all_tasks_except_the_requested_exclusion(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = root / "program.md"
    shutil.copy2(
        REPO_ROOT / "tasks/batches/FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01.md",
        manifest,
    )
    excluded = "FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01"

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
    assert len(validated) == 46
    assert validated[0] == "FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01"
    assert validated[-1] == "FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01"
    assert excluded not in validated


def test_manifest_gate_rejects_a_mixed_valid_and_malformed_task_declaration(
    tmp_path: Path,
) -> None:
    root = _build_gate_fixture(tmp_path)
    manifest = _write_manifest(root, ["TASK-A"])
    with manifest.open("a", encoding="utf-8") as stream:
        stream.write("- Task file: `tasks/not-allowed/TASK-B.md`\n")

    result = subprocess.run(
        ["./scripts/release_gate.sh", "--manifest", manifest.name],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert not (root / "validation.log").exists()
