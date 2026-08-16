from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import secrets
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
PLAYWRIGHT = ROOT / "FPMS_Automation_Skeleton_Pack" / "playwright_ts"
SPEC = PLAYWRIGHT / "src" / "tests" / "demo-abc.live-backend.spec.ts"
DEFAULT_ARTIFACT = ROOT / "artifacts" / "FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-02"
FORBIDDEN_SPEC_TOKENS = (
    "page.route(",
    "route.fulfill(",
    "sqlite3",
    "SessionLocal",
    "pdP1LiveSeed",
    "v6-enrich",
    "test.skip",
    "markSkeleton",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def candidate_identity() -> dict[str, Any]:
    status = git("status", "--porcelain=v1", "-uall").splitlines()
    if status:
        raise RuntimeError(f"technical rehearsal requires a clean candidate: {status}")
    return {
        "commit": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "branch": git("branch", "--show-current"),
        "status": "CLEAN",
        "captured_at": now(),
    }


def build_synthetic_bundle(parent: Path) -> tuple[Path, str, str]:
    helpers = runpy.run_path(str(BACKEND / "tests" / "test_demo_abc_runtime_bundle.py"))
    bundle, _manifest, manifest_sha = helpers["_valid_bundle"](parent)
    authority_sha = hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest()
    return bundle, manifest_sha, authority_sha


def wait_url(url: str, process: subprocess.Popen[bytes], timeout: float = 120) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"local runner exited before readiness: rc={process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"timed out waiting for {url}")


def child_processes(parent_pid: int) -> list[dict[str, Any]]:
    output = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,command="],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3 and int(parts[1]) == parent_pid:
            rows.append({"pid": int(parts[0]), "ppid": int(parts[1]), "command": parts[2]})
    return rows


def listeners() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for port in (8000, 5173):
        result = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        rows.append({"port": port, "rc": result.returncode, "output": result.stdout.splitlines()})
    return rows


def export_postconditions(database: Path, candidate: dict[str, Any], run_id: str) -> dict[str, Any]:
    uri = f"file:{database}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        def scalar(sql: str) -> int:
            return int(db.execute(sql).fetchone()[0])

        bill = db.execute(
            "SELECT status, printf('%.2f', amount), printf('%.2f', balance) FROM t_bill"
        ).fetchone()
        line = db.execute(
            "SELECT printf('%.2f', raw_amount), printf('%.2f', allocated_amt), "
            "printf('%.2f', balance_amt) FROM t_payment_line"
        ).fetchone()
        offset = db.execute("SELECT printf('%.2f', offset_amt) FROM t_offset").fetchone()
        receipt = db.execute(
            "SELECT printf('%.2f', receivable_amt), printf('%.2f', received_amt), receipt_key "
            "FROM t_case_receipt"
        ).fetchone()
        case = db.execute("SELECT id, case_no FROM t_case").fetchone()
        command_states = db.execute(
            "SELECT operation, state FROM t_demo_finance_command ORDER BY operation"
        ).fetchall()
        result = {
            "run_id": run_id,
            "candidate_commit": candidate["commit"],
            "candidate_tree": candidate["tree"],
            "case_id": case[0],
            "case_no": case[1],
            "client_count": scalar("SELECT COUNT(*) FROM t_client"),
            "case_count": scalar("SELECT COUNT(*) FROM t_case"),
            "applicant_count": scalar("SELECT COUNT(*) FROM t_case_applicant"),
            "draft_source_count": scalar("SELECT COUNT(*) FROM t_bill_draft_source"),
            "bill_count": scalar("SELECT COUNT(*) FROM t_bill"),
            "bill_item_count": scalar("SELECT COUNT(*) FROM t_bill_item"),
            "payment_count": scalar("SELECT COUNT(*) FROM t_payment"),
            "payment_line_count": scalar("SELECT COUNT(*) FROM t_payment_line"),
            "payment_command_count": scalar("SELECT COUNT(*) FROM t_demo_payment_command"),
            "active_offset_count": scalar(
                "SELECT COUNT(*) FROM t_offset WHERE is_reversed = 0"
            ),
            "offset_command_count": scalar("SELECT COUNT(*) FROM t_demo_offset_command"),
            "receipt_count": scalar("SELECT COUNT(*) FROM t_case_receipt"),
            "finance_command_count": scalar("SELECT COUNT(*) FROM t_demo_finance_command"),
            "finance_command_states": [list(row) for row in command_states],
            "bill_status": bill[0],
            "bill_amount": bill[1],
            "bill_balance": bill[2],
            "payment_raw": line[0],
            "payment_allocated": line[1],
            "payment_balance": line[2],
            "offset_amount": offset[0],
            "receipt_receivable": receipt[0],
            "receipt_received": receipt[1],
            "receipt_key": receipt[2],
        }
    expected_counts = (
        "client_count",
        "case_count",
        "applicant_count",
        "draft_source_count",
        "bill_count",
        "bill_item_count",
        "payment_count",
        "payment_line_count",
        "payment_command_count",
        "active_offset_count",
        "offset_command_count",
        "receipt_count",
    )
    if any(result[key] != 1 for key in expected_counts):
        raise RuntimeError(f"unexpected ABC carrier counts: {result}")
    if (
        result["finance_command_count"] != 3
        or command_states != [("BILL", "COMPLETED"), ("OFFSET", "COMPLETED"), ("PAYMENT", "COMPLETED")]
        or result["bill_status"] != "SETTLED"
        or result["bill_amount"] != "1200.00"
        or result["bill_balance"] != "0.00"
        or result["payment_raw"] != "1200.00"
        or result["payment_allocated"] != "1200.00"
        or result["payment_balance"] != "0.00"
        or result["offset_amount"] != "1200.00"
        or result["receipt_receivable"] != "1200.00"
        or result["receipt_received"] != "1200.00"
        or result["receipt_key"]
        != f"{result['case_id']}|DEMO_SERVICE_1|SERVICE|-|CNY"
    ):
        raise RuntimeError(f"unexpected ABC financial postconditions: {result}")
    return result


def remove_run_root(run_root: Path, run_id: str) -> None:
    expected = f"fpms-demo-abc-{run_id}"
    if run_root.name != expected or run_root.parent != Path(tempfile.gettempdir()).resolve():
        raise RuntimeError(f"refusing unexpected cleanup target: {run_root}")
    for path in sorted(run_root.rglob("*"), reverse=True):
        path.chmod(0o700 if path.is_dir() else 0o600)
    run_root.chmod(0o700)
    shutil.rmtree(run_root)


def run_one(
    *,
    ordinal: int,
    artifact: Path,
    bundle: Path,
    manifest_sha: str,
    authority_sha: str,
    candidate: dict[str, Any],
    headed: bool,
) -> dict[str, Any]:
    run_id = f"tech-r{ordinal}-{int(time.time())}-{secrets.token_hex(3)}"
    run_artifact = artifact / f"run{ordinal}"
    run_artifact.mkdir()
    run_root = (Path(tempfile.gettempdir()) / f"fpms-demo-abc-{run_id}").resolve()
    admin_password = secrets.token_urlsafe(24)
    reviewer_password = secrets.token_urlsafe(24)
    env = os.environ.copy()
    env.update(
        FPMS_ENV="demo",
        FPMS_DEMO_SCOPE="LOCAL_ABC_E2E",
        FPMS_DEMO_RUN_PROFILE="TECHNICAL_REHEARSAL",
        FPMS_DEMO_RUN_ID=run_id,
        FPMS_DEMO_BUNDLE_PATH=str(bundle),
        FPMS_DEMO_EXPECTED_MANIFEST_SHA256=manifest_sha,
        FPMS_DEMO_EXPECTED_AUTHORITY_SHA256=authority_sha,
        FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION="SYNTHETIC_TEST_ONLY",
        FPMS_DEMO_ADMIN_USERNAME="admin",
        FPMS_DEMO_ADMIN_PASSWORD=admin_password,
        FPMS_DEMO_REVIEWER_USERNAME="demo_evidence_reviewer",
        FPMS_DEMO_REVIEWER_PASSWORD=reviewer_password,
        JWT_SECRET=secrets.token_urlsafe(48),
    )
    commands = artifact / "commands.jsonl"
    results = artifact / "results.jsonl"
    runner_argv = [
        sys.executable,
        "-m",
        "scripts.run_local_demo_abc",
    ]
    append_jsonl(
        commands,
        {
            "step": f"run{ordinal}-launch",
            "cwd": str(BACKEND),
            "argv": runner_argv,
            "environment_keys": sorted(key for key in env if key.startswith("FPMS_DEMO_") or key == "JWT_SECRET"),
            "credentials": "EPHEMERAL_REDACTED",
            "ts": now(),
        },
    )
    runner_log = run_artifact / "runner.log"
    started = time.monotonic()
    with runner_log.open("wb") as log:
        runner = subprocess.Popen(runner_argv, cwd=BACKEND, env=env, stdout=log, stderr=subprocess.STDOUT)
    playwright_rc = -1
    runner_rc: int | None = None
    initial_children: list[dict[str, Any]] = []
    try:
        wait_url("http://127.0.0.1:8000/healthz", runner)
        wait_url("http://127.0.0.1:5173", runner)
        initial_children = child_processes(runner.pid)
        write_json(
            run_artifact / "process-start.json",
            {
                "runner_pid": runner.pid,
                "children": initial_children,
                "listeners": listeners(),
                "captured_at": now(),
            },
        )
        metadata_path = run_root / "run-metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if (
            metadata["candidate_commit"] != candidate["commit"]
            or metadata["candidate_tree"] != candidate["tree"]
            or metadata["authority_classification"] != "SYNTHETIC_TEST_ONLY"
            or metadata["customer_activation_eligible"] is not False
        ):
            raise RuntimeError(f"runner metadata is not bound to candidate/synthetic class: {metadata}")
        write_json(run_artifact / "run-metadata.json", metadata)

        playwright_env = env.copy()
        playwright_env.update(
            FPMS_BASE_URL="http://127.0.0.1:5173",
            FPMS_API_URL="http://127.0.0.1:8000/api/v1",
            FPMS_ADMIN_USERNAME="admin",
            FPMS_ADMIN_PASSWORD=admin_password,
            FPMS_DEMO_EVIDENCE_DIR=str(run_artifact),
        )
        playwright_argv = [
            "node",
            "./node_modules/.bin/playwright",
            "test",
            "src/tests/demo-abc.live-backend.spec.ts",
            "--project=chromium",
            "--workers=1",
            "--reporter=list",
        ]
        if headed:
            playwright_argv.append("--headed")
        append_jsonl(
            commands,
            {
                "step": f"run{ordinal}-browser",
                "cwd": str(PLAYWRIGHT),
                "argv": playwright_argv,
                "environment_keys": [
                    "FPMS_BASE_URL",
                    "FPMS_API_URL",
                    "FPMS_ADMIN_USERNAME",
                    "FPMS_ADMIN_PASSWORD",
                    "FPMS_DEMO_EVIDENCE_DIR",
                ],
                "credentials": "EPHEMERAL_REDACTED",
                "ts": now(),
            },
        )
        with (run_artifact / "playwright.log").open("wb") as output:
            browser = subprocess.run(
                playwright_argv,
                cwd=PLAYWRIGHT,
                env=playwright_env,
                stdout=output,
                stderr=subprocess.STDOUT,
                timeout=180,
            )
        playwright_rc = browser.returncode
        append_jsonl(
            results,
            {
                "step": f"run{ordinal}-browser",
                "rc": playwright_rc,
                "log": f"run{ordinal}/playwright.log",
                "log_sha256": sha256(run_artifact / "playwright.log"),
                "ts": now(),
            },
        )
        if playwright_rc != 0:
            raise RuntimeError(f"headed Playwright rehearsal failed: rc={playwright_rc}")
        append_jsonl(
            commands,
            {
                "step": f"run{ordinal}-db-export",
                "operation": "read-only sqlite mode=ro postcondition export",
                "database": "EPHEMERAL_RUN_ROOT_REDACTED",
                "ts": now(),
            },
        )
        postconditions = export_postconditions(run_root / "fpms-demo.db", candidate, run_id)
        write_json(run_artifact / "db-postconditions.json", postconditions)
    finally:
        append_jsonl(
            commands,
            {
                "step": f"run{ordinal}-shutdown",
                "operation": "SIGINT exact recorded runner PID, verify children/listeners, remove exact run root",
                "runner_pid": runner.pid,
                "ts": now(),
            },
        )
        if runner.poll() is None:
            runner.send_signal(signal.SIGINT)
        try:
            runner_rc = runner.wait(timeout=20)
        except subprocess.TimeoutExpired:
            runner.kill()
            runner_rc = runner.wait(timeout=10)
        stopped_children = child_processes(runner.pid)
        surviving_initial_pids: list[int] = []
        for child in initial_children:
            try:
                os.kill(int(child["pid"]), 0)
            except ProcessLookupError:
                continue
            else:
                surviving_initial_pids.append(int(child["pid"]))
        remaining_listeners = listeners()
        run_removed = not run_root.exists()
        if run_root.exists():
            remove_run_root(run_root, run_id)
            run_removed = not run_root.exists()
        cleanup = {
            "runner_pid": runner.pid,
            "runner_rc_after_sigint": runner_rc,
            "initial_child_pids": [row["pid"] for row in initial_children],
            "surviving_initial_child_pids": surviving_initial_pids,
            "remaining_children": stopped_children,
            "remaining_listeners": remaining_listeners,
            "run_root": str(run_root),
            "run_root_removed": run_removed,
            "captured_at": now(),
        }
        write_json(run_artifact / "cleanup.json", cleanup)
        if (
            stopped_children
            or surviving_initial_pids
            or any(row["output"] for row in remaining_listeners)
            or not run_removed
        ):
            raise RuntimeError(f"local rehearsal cleanup failed: {cleanup}")
        append_jsonl(
            results,
            {
                "step": f"run{ordinal}-cleanup",
                "rc": 0,
                "runner_rc_after_sigint": runner_rc,
                "duration_seconds": round(time.monotonic() - started, 3),
                "ts": now(),
            },
        )
    return json.loads((run_artifact / "db-postconditions.json").read_text(encoding="utf-8"))


def write_checksums(artifact: Path) -> None:
    files = sorted(
        path for path in artifact.rglob("*") if path.is_file() and path.name != "checksums.sha256"
    )
    lines = [f"{sha256(path)}  {path.relative_to(artifact).as_posix()}" for path in files]
    (artifact / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        expected, relative = line.split("  ", 1)
        if sha256(artifact / relative) != expected:
            raise RuntimeError(f"checksum verification failed: {relative}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run two exact FPMS ABC technical rehearsals")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args(argv)
    artifact = args.artifact.resolve()
    if artifact.exists():
        raise RuntimeError(f"evidence path already exists: {artifact}")
    artifact.mkdir(parents=True)
    candidate = candidate_identity()
    write_json(artifact / "candidate.json", candidate)
    append_jsonl(
        artifact / "commands.jsonl",
        {
            "step": "candidate-identity",
            "operation": "git rev-parse HEAD and HEAD^{tree}; git status --porcelain=v1 -uall",
            "cwd": str(ROOT),
            "ts": now(),
        },
    )
    append_jsonl(
        artifact / "results.jsonl",
        {"step": "candidate-identity", "rc": 0, "candidate": candidate, "ts": now()},
    )
    spec_text = SPEC.read_text(encoding="utf-8")
    forbidden = [token for token in FORBIDDEN_SPEC_TOKENS if token in spec_text]
    if forbidden:
        raise RuntimeError(f"focused spec contains forbidden constructs: {forbidden}")
    bundle_parent = Path(tempfile.mkdtemp(prefix="fpms-demo-synthetic-bundle-"))
    bundle: Path | None = None
    try:
        bundle, manifest_sha, authority_sha = build_synthetic_bundle(bundle_parent)
        write_json(
            artifact / "bundle.json",
            {
                "classification": "SYNTHETIC_TEST_ONLY",
                "customer_activation_eligible": False,
                "builder": "backend/tests/test_demo_abc_runtime_bundle.py::_valid_bundle",
                "builder_sha256": sha256(BACKEND / "tests" / "test_demo_abc_runtime_bundle.py"),
                "manifest_sha256": manifest_sha,
                "authority_sha256": authority_sha,
                "bundle_path": "EPHEMERAL_REDACTED",
            },
        )
        runs = [
            run_one(
                ordinal=ordinal,
                artifact=artifact,
                bundle=bundle,
                manifest_sha=manifest_sha,
                authority_sha=authority_sha,
                candidate=candidate,
                headed=not args.headless,
            )
            for ordinal in (1, 2)
        ]
    finally:
        if bundle_parent.exists():
            shutil.rmtree(bundle_parent)
    if runs[0]["run_id"] == runs[1]["run_id"] or runs[0]["case_no"] == runs[1]["case_no"]:
        raise RuntimeError("two rehearsal runs are not independent")
    write_json(
        artifact / "two-run-summary.json",
        {
            "status": "TECHNICAL_REHEARSAL_PASS",
            "candidate": candidate,
            "authority_classification": "SYNTHETIC_TEST_ONLY",
            "customer_activation_eligible": False,
            "headed": not args.headless,
            "runs": runs,
        },
    )
    write_json(
        artifact / "bundle-cleanup.json",
        {"ephemeral_bundle_root": "REDACTED", "removed": not bundle_parent.exists(), "ts": now()},
    )
    (artifact / "summary.md").write_text(
        "\n".join(
            [
                "# FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-02 Summary",
                "",
                "- Status: TECHNICAL_REHEARSAL_PASS",
                f"- Candidate: `{candidate['commit']}` / tree `{candidate['tree']}`",
                "- Authority: `SYNTHETIC_TEST_ONLY`; customer activation eligible: `false`",
                f"- Run 1: `{runs[0]['run_id']}` / `{runs[0]['case_no']}` / SETTLED",
                f"- Run 2: `{runs[1]['run_id']}` / `{runs[1]['case_no']}` / SETTLED",
                f"- Browser mode: {'headless' if args.headless else 'headed'} Chromium",
                "- Customer input activation: BLOCKED pending exact customer-authorized bundle",
                "- Production/security/PostgreSQL/release: not evaluated",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_checksums(artifact)
    print(json.dumps({"status": "PASS", "artifact": str(artifact)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
