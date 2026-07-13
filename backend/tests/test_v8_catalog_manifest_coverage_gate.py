import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "v8_catalog_manifest_gate.py"
MATERIALIZATION = (
    ROOT / "artifacts" / "PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01" / "materialization"
)


@pytest.fixture(autouse=True)
def _reset_test_data() -> None:
    """Keep this stdlib CLI suite independent of the global SQLite fixture."""


def _make_sandbox(tmp_path: Path, task_validate_rc: int = 0) -> Path:
    sandbox = tmp_path / "repo"
    scripts = sandbox / "scripts"
    materialization = (
        sandbox
        / "artifacts"
        / "PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01"
        / "materialization"
    )
    scripts.mkdir(parents=True)
    materialization.mkdir(parents=True)
    shutil.copy2(SCRIPT, scripts / SCRIPT.name)
    for name in ("catalog.json", "gate_register.json", "foundation_manifest_index.json"):
        shutil.copy2(MATERIALIZATION / name, materialization / name)

    task_validate = scripts / "task_validate.sh"
    task_validate.write_text(
        f'#!/bin/sh\nprintf \'%s\\n\' "$1" >> "$TASK_VALIDATE_LOG"\nexit {task_validate_rc}\n',
        encoding="utf-8",
    )
    task_validate.chmod(0o755)
    return sandbox


def _write_manifest(sandbox: Path, task_ids: list[str]) -> Path:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))
    paths = {row["task_id"]: row["task_path"] for row in catalog["tasks"]}
    manifest = sandbox / "manifest.md"
    declarations = "\n".join(f"- Task file: `{paths[task_id]}`" for task_id in task_ids)
    manifest.write_text(
        f"# Test manifest\n\nTask count: {len(task_ids)}\n\n{declarations}\n",
        encoding="utf-8",
    )
    return manifest


def _write_gate_snapshot(sandbox: Path, statuses: dict[str, str]) -> Path:
    register = json.loads((MATERIALIZATION / "gate_register.json").read_text(encoding="utf-8"))
    for row in register["rows"]:
        if row["task_id"] in statuses:
            row["status"] = statuses[row["task_id"]]
    snapshot = sandbox / "gate_register.json"
    snapshot.write_text(json.dumps(register), encoding="utf-8")
    return snapshot


def _run_sandbox_gate(
    sandbox: Path,
    phase: str,
    task_ids: list[str],
    statuses: dict[str, str],
    self_pending: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    manifest = _write_manifest(sandbox, task_ids)
    snapshot = _write_gate_snapshot(sandbox, statuses)
    calls = sandbox / "task_validate_calls.txt"
    command = [
        sys.executable,
        str(sandbox / "scripts" / SCRIPT.name),
        "--phase",
        phase,
        "--manifest",
        str(manifest),
        "--gate-register",
        str(snapshot),
    ]
    if self_pending is not None:
        command.extend(("--self-pending", self_pending))
    result = subprocess.run(
        command,
        cwd=sandbox,
        env={**os.environ, "TASK_VALIDATE_LOG": str(calls)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    invoked = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
    return result, invoked


def test_foundation_accepts_real_ordered_197_row_manifest() -> None:
    index = json.loads(
        (MATERIALIZATION / "foundation_manifest_index.json").read_text(encoding="utf-8")
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--phase",
            "foundation",
            "--manifest",
            str(ROOT / index["manifest"]),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "foundation manifest coverage accepted: 197 tasks" in output


def test_lane_accepts_activation_then_children_and_checks_every_dependency(
    tmp_path: Path,
) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    activation_id = "FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01"
    activation = next(row for row in catalog if row["task_id"] == activation_id)
    children = [
        row["task_id"] for row in catalog if row["lane_activation_task_id"] == activation_id
    ]
    task_ids = [activation_id, *children]
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "lane",
        task_ids,
        {task_id: "confirmed-pending" for task_id in task_ids},
        self_pending=activation_id,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert f"lane manifest coverage accepted: {len(task_ids)} tasks" in output
    assert invoked == activation["depends_on"]


def test_full_accepts_all_283_rows_with_only_full_activation_pending(
    tmp_path: Path,
) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    register = json.loads((MATERIALIZATION / "gate_register.json").read_text(encoding="utf-8"))[
        "rows"
    ]
    task_ids = [row["task_id"] for row in catalog]
    activation_id = "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01"
    statuses = {row["task_id"]: "prior-PASS" for row in register}
    statuses[activation_id] = "confirmed-pending"
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "full",
        task_ids,
        statuses,
        self_pending=activation_id,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "full manifest coverage accepted: 283 tasks" in output
    assert invoked == []


def test_lane_rejects_unresolved_member_status(tmp_path: Path) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    activation_id = "FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01"
    children = [
        row["task_id"] for row in catalog if row["lane_activation_task_id"] == activation_id
    ]
    task_ids = [activation_id, *children]
    statuses = {task_id: "confirmed-pending" for task_id in task_ids}
    statuses[children[0]] = "unresolved"
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "lane",
        task_ids,
        statuses,
        self_pending=activation_id,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "lane member is not active" in output
    assert invoked == []


def test_lane_rejects_incomplete_membership(tmp_path: Path) -> None:
    activation_id = "FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01"
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "lane",
        [activation_id],
        {activation_id: "confirmed-pending"},
        self_pending=activation_id,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "lane manifest membership or order is incorrect" in output
    assert invoked == []


def test_lane_requires_self_pending_activation(tmp_path: Path) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    activation_id = "FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01"
    children = [
        row["task_id"] for row in catalog if row["lane_activation_task_id"] == activation_id
    ]
    task_ids = [activation_id, *children]
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "lane",
        task_ids,
        {task_id: "confirmed-pending" for task_id in task_ids},
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "lane SELF_PENDING is required" in output
    assert invoked == []


def test_lane_checks_every_prerequisite_before_rejecting_failure(
    tmp_path: Path,
) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    activation_id = "FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01"
    activation = next(row for row in catalog if row["task_id"] == activation_id)
    children = [
        row["task_id"] for row in catalog if row["lane_activation_task_id"] == activation_id
    ]
    task_ids = [activation_id, *children]
    sandbox = _make_sandbox(tmp_path, task_validate_rc=1)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "lane",
        task_ids,
        {task_id: "confirmed-pending" for task_id in task_ids},
        self_pending=activation_id,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "prerequisite task gate failed" in output
    assert invoked == activation["depends_on"]


def test_repeated_self_pending_is_an_input_error(tmp_path: Path) -> None:
    index = json.loads(
        (MATERIALIZATION / "foundation_manifest_index.json").read_text(encoding="utf-8")
    )
    sandbox = _make_sandbox(tmp_path)
    manifest = _write_manifest(sandbox, index["task_ids"])
    self_pending = "FPMS-V8-FOUNDATION-CLOSE-20260712-01"

    result = subprocess.run(
        [
            sys.executable,
            str(sandbox / "scripts" / SCRIPT.name),
            "--phase",
            "foundation",
            "--manifest",
            str(manifest),
            "--self-pending",
            self_pending,
            "--self-pending",
            self_pending,
        ],
        cwd=sandbox,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 2, output
    assert "--self-pending may be supplied only once" in output


def test_foundation_accepts_every_allowed_deferred_status(tmp_path: Path) -> None:
    index = json.loads(
        (MATERIALIZATION / "foundation_manifest_index.json").read_text(encoding="utf-8")
    )
    rows = json.loads((MATERIALIZATION / "gate_register.json").read_text(encoding="utf-8"))["rows"]
    allowed = ("unresolved", "confirmed-pending", "activated", "prior-PASS")
    statuses = {
        row["task_id"]: allowed[position] for position, row in enumerate(rows[: len(allowed)])
    }
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "foundation",
        index["task_ids"],
        statuses,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "foundation manifest coverage accepted: 197 tasks" in output
    assert invoked == []


def test_lane_rejects_gate_scope_mutation(tmp_path: Path) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    activation_id = "FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01"
    children = [
        row["task_id"] for row in catalog if row["lane_activation_task_id"] == activation_id
    ]
    task_ids = [activation_id, *children]
    sandbox = _make_sandbox(tmp_path)
    manifest = _write_manifest(sandbox, task_ids)
    snapshot = _write_gate_snapshot(
        sandbox,
        {task_id: "confirmed-pending" for task_id in task_ids},
    )
    register = json.loads(snapshot.read_text(encoding="utf-8"))
    activation = next(row for row in register["rows"] if row["task_id"] == activation_id)
    activation["gate_requirements"][0]["scope"] = "WRONG-SCOPE"
    snapshot.write_text(json.dumps(register), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(sandbox / "scripts" / SCRIPT.name),
            "--phase",
            "lane",
            "--manifest",
            str(manifest),
            "--gate-register",
            str(snapshot),
            "--self-pending",
            activation_id,
        ],
        cwd=sandbox,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "gate register changed an immutable row field" in output


@pytest.mark.parametrize("case", ("duplicate", "outside", "malformed", "count"))
def test_manifest_structure_input_errors_return_2(tmp_path: Path, case: str) -> None:
    index = json.loads(
        (MATERIALIZATION / "foundation_manifest_index.json").read_text(encoding="utf-8")
    )
    task_ids = index["task_ids"]
    sandbox = _make_sandbox(tmp_path)
    manifest = _write_manifest(
        sandbox,
        [task_ids[0], *task_ids] if case == "duplicate" else task_ids,
    )
    if case != "duplicate":
        text = manifest.read_text(encoding="utf-8")
        first_path = next(
            row["task_path"]
            for row in json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))[
                "tasks"
            ]
            if row["task_id"] == task_ids[0]
        )
        if case == "outside":
            text = text.replace(
                first_path,
                "tasks/postdemo/v8/FPMS-V8-NOT-IN-CATALOG-20260712-01.md",
                1,
            )
        elif case == "malformed":
            text = text.replace(f"`{first_path}`", first_path, 1)
        else:
            text = text.replace("Task count: 197", "Task count: 196", 1)
        manifest.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(sandbox / "scripts" / SCRIPT.name),
            "--phase",
            "foundation",
            "--manifest",
            str(manifest),
        ],
        cwd=sandbox,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 2, output
    assert "input error:" in output


def test_malformed_gate_register_is_an_input_error(tmp_path: Path) -> None:
    index = json.loads(
        (MATERIALIZATION / "foundation_manifest_index.json").read_text(encoding="utf-8")
    )
    sandbox = _make_sandbox(tmp_path)
    manifest = _write_manifest(sandbox, index["task_ids"])
    malformed = sandbox / "malformed_gate_register.json"
    malformed.write_text("{", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(sandbox / "scripts" / SCRIPT.name),
            "--phase",
            "foundation",
            "--manifest",
            str(manifest),
            "--gate-register",
            str(malformed),
        ],
        cwd=sandbox,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 2, output
    assert "cannot read gate register snapshot" in output


def test_full_rejects_confirmed_pending_non_self_deferred_row(
    tmp_path: Path,
) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    register = json.loads((MATERIALIZATION / "gate_register.json").read_text(encoding="utf-8"))[
        "rows"
    ]
    activation_id = "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01"
    statuses = {row["task_id"]: "prior-PASS" for row in register}
    statuses[activation_id] = "confirmed-pending"
    statuses[register[0]["task_id"]] = "confirmed-pending"
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "full",
        [row["task_id"] for row in catalog],
        statuses,
        self_pending=activation_id,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    assert "full deferred task is not complete" in output
    assert invoked == []


def test_full_allows_final_close_self_pending_marker(tmp_path: Path) -> None:
    catalog = json.loads((MATERIALIZATION / "catalog.json").read_text(encoding="utf-8"))["tasks"]
    register = json.loads((MATERIALIZATION / "gate_register.json").read_text(encoding="utf-8"))[
        "rows"
    ]
    final_close = "FPMS-V8-FINAL-CLOSE-20260712-01"
    sandbox = _make_sandbox(tmp_path)

    result, invoked = _run_sandbox_gate(
        sandbox,
        "full",
        [row["task_id"] for row in catalog],
        {row["task_id"]: "prior-PASS" for row in register},
        self_pending=final_close,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "full manifest coverage accepted: 283 tasks" in output
    assert invoked == []
