from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_demo_abc_rehearsal as abc  # noqa: E402


BACKEND = ROOT / "backend"
PLAYWRIGHT = ROOT / "FPMS_Automation_Skeleton_Pack" / "playwright_ts"
SPEC = PLAYWRIGHT / "src" / "tests" / "demo-integrated-a.live-backend.spec.ts"
DEFAULT_ARTIFACT = ROOT / "artifacts" / "FPMS-DEMO-INTEGRATED-A-DIAGNOSTIC"
FORBIDDEN_SPEC_TOKENS = (
    "page.route(",
    "route.fulfill(",
    "SessionLocal",
    "sqlite3",
    "pdP1LiveSeed",
    "v6-enrich",
    "test.skip",
    "markSkeleton",
    "contractRed",
    ".toBeTruthy()",
    "expect({",
)
FORBIDDEN_NETWORK_PATTERNS = (
    re.compile(r"\brequest\b"),
    re.compile(r"\bfetch\b"),
    re.compile(r"\baxios\b"),
    re.compile(r"\bXMLHttpRequest\b"),
    re.compile(r"\bWebSocket\b"),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bFunction\s*\("),
    re.compile(r"\bimport\s*\("),
    re.compile(r"\.evaluate\s*\("),
    re.compile(r"\[['\"]request['\"]\]"),
)
ALLOWED_SPEC_IMPORT_LINES = [
    "import { test, expect, type BrowserContext, type Page } from '@playwright/test'",
    "import { mkdir, writeFile } from 'node:fs/promises'",
    "import path from 'node:path'",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FPMS Integrated Scheme A rehearsal")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--runs", type=int, choices=(1, 2), default=2)
    parser.add_argument("--headless", action="store_true")
    return parser.parse_args(argv)


def build_integrated_bundle(parent: Path) -> tuple[Path, str, str]:
    helpers = runpy.run_path(str(BACKEND / "tests" / "test_demo_abc_runtime_bundle.py"))
    builder = helpers.get("_valid_integrated_bundle")
    if builder is None:
        raise RuntimeError("integrated-a-v1 bundle builder is unavailable")
    bundle, _manifest, manifest_sha = builder(parent)
    authority_sha = hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest()
    return bundle, manifest_sha, authority_sha


def validate_spec_source(source: str) -> None:
    forbidden = [token for token in FORBIDDEN_SPEC_TOKENS if token in source]
    if forbidden:
        raise RuntimeError(f"focused spec contains forbidden constructs: {forbidden}")
    if any(pattern.search(source) for pattern in FORBIDDEN_NETWORK_PATTERNS):
        raise RuntimeError("canonical spec business writes must use visible UI")
    imports = [line for line in source.splitlines() if line.startswith("import ")]
    if imports != ALLOWED_SPEC_IMPORT_LINES:
        raise RuntimeError(f"focused spec imports are not allowlisted: {imports}")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _run_one(
    ordinal: int,
    artifact: Path,
    bundle: Path,
    manifest_sha: str,
    authority_sha: str,
    candidate: dict[str, Any],
    headless: bool,
) -> None:
    run_id = f"integrated-r{ordinal}-{secrets.token_hex(6)}"
    run_root = (Path(tempfile.gettempdir()) / f"fpms-demo-abc-{run_id}").resolve()
    run_artifact = artifact / f"run{ordinal}"
    run_artifact.mkdir()
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
        NO_PROXY="127.0.0.1,localhost",
        no_proxy="127.0.0.1,localhost",
    )
    runner_log = run_artifact / "runner.log"
    with runner_log.open("wb") as output:
        runner = subprocess.Popen(
            [sys.executable, "-m", "scripts.run_local_demo_abc"],
            cwd=BACKEND,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
    try:
        abc.wait_url("http://127.0.0.1:8000/healthz", runner)
        abc.wait_url("http://127.0.0.1:5173", runner)
        browser_env = env.copy()
        browser_env.update(
            FPMS_BASE_URL="http://127.0.0.1:5173",
            FPMS_API_URL="http://127.0.0.1:8000/api/v1",
            FPMS_ADMIN_USERNAME="admin",
            FPMS_ADMIN_PASSWORD=admin_password,
            FPMS_REVIEWER_USERNAME="demo_evidence_reviewer",
            FPMS_REVIEWER_PASSWORD=reviewer_password,
            FPMS_DEMO_EVIDENCE_DIR=str(run_artifact),
        )
        command = [
            "node",
            "./node_modules/.bin/playwright",
            "test",
            str(SPEC.relative_to(PLAYWRIGHT)),
            "--project=chromium",
            "--workers=1",
            "--reporter=list",
        ]
        if not headless:
            command.append("--headed")
        with (run_artifact / "playwright.log").open("wb") as output:
            completed = subprocess.run(
                command,
                cwd=PLAYWRIGHT,
                env=browser_env,
                stdout=output,
                stderr=subprocess.STDOUT,
                timeout=300,
            )
        if completed.returncode != 0:
            raise RuntimeError(f"integrated Playwright failed: rc={completed.returncode}")
    finally:
        if runner.poll() is None:
            runner.send_signal(signal.SIGINT)
        try:
            runner.wait(timeout=20)
        except subprocess.TimeoutExpired:
            runner.kill()
            runner.wait(timeout=10)
        if run_root.exists():
            if run_root.parent != Path(tempfile.gettempdir()).resolve() or not run_root.name.startswith("fpms-demo-abc-integrated-r"):
                raise RuntimeError(f"refusing unexpected cleanup root: {run_root}")
            shutil.rmtree(run_root)
        _write_json(run_artifact / "cleanup.json", {"run_id": run_id, "run_root_removed": not run_root.exists()})


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact.resolve()
    if artifact.exists():
        raise RuntimeError(f"evidence path already exists: {artifact}")
    candidate = abc.candidate_identity()
    source = SPEC.read_text(encoding="utf-8")
    validate_spec_source(source)
    artifact.mkdir(parents=True)
    _write_json(artifact / "candidate.json", candidate)
    bundle_parent = Path(tempfile.mkdtemp(prefix="fpms-integrated-a-bundle-"))
    try:
        bundle, manifest_sha, authority_sha = build_integrated_bundle(bundle_parent)
        for ordinal in range(1, args.runs + 1):
            _run_one(ordinal, artifact, bundle, manifest_sha, authority_sha, candidate, args.headless)
    finally:
        if bundle_parent.exists():
            shutil.rmtree(bundle_parent)
    _write_json(artifact / "summary.json", {"status": "DIAGNOSTIC_PASS", "runs": args.runs})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
