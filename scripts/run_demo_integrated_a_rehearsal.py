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
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_demo_abc_rehearsal as abc  # noqa: E402


BACKEND = ROOT / "backend"
PLAYWRIGHT = ROOT / "FPMS_Automation_Skeleton_Pack" / "playwright_ts"
SPEC = PLAYWRIGHT / "src" / "tests" / "demo-integrated-a.live-backend.spec.ts"
STATIC_CONTRACT = PLAYWRIGHT / "src" / "tests" / "demo-integrated-a-static-contract.mjs"
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
PUBLIC_LIFECYCLE_API_ALLOWLIST = {
    "ARCHIVE_PACKAGE": ("POST", "/official-work-packages/{package_id}/archive"),
    "GET_FILING_PACKAGE": (
        "GET",
        "/official-work-packages/{package_id}/filing-preparation",
    ),
    "GET_GRANT_TASK": ("GET", "/grant-fee-tasks/{task_id}/state"),
    "GET_OA_PACKAGE": ("GET", "/official-work-packages/{package_id}/oa-reply"),
    "GRANT_BATCH_INSTRUCTION": ("POST", "/grant-fee-tasks/batch-instruction"),
    "GRANT_GENERATE_DRAFT": ("POST", "/grant-fee-tasks/{task_id}/generate-draft"),
    "GRANT_GENERATE_NOTICES": ("POST", "/grant-fee-tasks/generate-notices"),
    "GRANT_NOTICE": (
        "POST",
        "/grant-fee-tasks/{grant_fee_task_id}/lifecycle/grant-notice",
    ),
    "GRANT_REPLACEMENT": ("POST", "/grant-fee-tasks/{task_id}/replacement-notice"),
    "GRANT_TASK_STATE": ("PUT", "/grant-fee-tasks/{task_id}/state"),
    "LINK_OA_REPLY": (
        "POST",
        "/official-work-packages/{package_id}/oa-reply/reply-document",
    ),
    "RECORD_ACCEPTANCE": (
        "POST",
        "/documents/{document_id}/lifecycle/acceptance-notice",
    ),
    "RECORD_FILING_EXTERNAL": (
        "POST",
        "/official-work-packages/{package_id}/filing-preparation/external-operations",
    ),
    "RECORD_OA_NOTICE": ("POST", "/documents/{document_id}/lifecycle/oa-notice"),
    "RECORD_PACKAGE_RECEIPT": (
        "POST",
        "/official-work-packages/{package_id}/receipts",
    ),
    "RECORD_PRELIMINARY_PASS": (
        "POST",
        "/documents/{document_id}/lifecycle/preliminary-pass",
    ),
    "RECORD_PRELIMINARY_START": (
        "POST",
        "/documents/{document_id}/lifecycle/preliminary-start",
    ),
    "RECORD_PUBLICATION": (
        "POST",
        "/documents/{document_id}/lifecycle/publication-notice",
    ),
    "RECORD_SUBSTANTIVE_START": (
        "POST",
        "/documents/{document_id}/lifecycle/substantive-start",
    ),
    "RESOLVE_FILING": (
        "POST",
        "/cases/{case_id}/official-work-packages/filing-preparation/resolve",
    ),
    "RESOLVE_OA": (
        "POST",
        "/official-documents/{document_id}/official-work-packages/oa-reply/resolve",
    ),
}
PUBLIC_API_START = "// BEGIN EXACT PUBLIC LIFECYCLE API ALLOWLIST"
PUBLIC_API_END = "// END EXACT PUBLIC LIFECYCLE API ALLOWLIST"
PUBLIC_HELPER_START = "// BEGIN AUDITED PUBLIC API HELPER"
PUBLIC_HELPER_END = "// END AUDITED PUBLIC API HELPER"
ALLOWED_SPEC_IMPORT_LINES = [
    "import { test, expect, type APIRequestContext, type BrowserContext, type Page } from '@playwright/test'",
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
    imports = [line.strip() for line in source.splitlines() if line.lstrip().startswith("import ")]
    if imports != ALLOWED_SPEC_IMPORT_LINES:
        raise RuntimeError(f"focused spec imports are not allowlisted: {imports}")

    if source.count(PUBLIC_API_START) != 1 or source.count(PUBLIC_API_END) != 1:
        raise RuntimeError("public lifecycle API allowlist markers are invalid")
    allowlist_block = source.split(PUBLIC_API_START, 1)[1].split(PUBLIC_API_END, 1)[0]
    for operation, (method, path) in PUBLIC_LIFECYCLE_API_ALLOWLIST.items():
        exact = f"  {operation}: {{ method: '{method}', path: '{path}' }},"
        if allowlist_block.count(exact) != 1:
            raise RuntimeError("public lifecycle API allowlist does not match the approved boundary")
    operation_lines = [
        line
        for line in allowlist_block.splitlines()
        if line.startswith("  ") and ": { method:" in line
    ]
    if len(operation_lines) != len(PUBLIC_LIFECYCLE_API_ALLOWLIST):
        raise RuntimeError("public lifecycle API allowlist contains an extra operation")
    if any(token in allowlist_block for token in ("attachments", "evidence-versions", "/review")):
        raise RuntimeError("public lifecycle API allowlist includes a visible-UI-only evidence write")

    if source.count(PUBLIC_HELPER_START) != 1 or source.count(PUBLIC_HELPER_END) != 1:
        raise RuntimeError("audited public API helper markers are invalid")
    prefix, helper_and_suffix = source.split(PUBLIC_HELPER_START, 1)
    helper, suffix = helper_and_suffix.split(PUBLIC_HELPER_END, 1)
    if helper.count("apiRequest.fetch(") != 1:
        raise RuntimeError("audited public API helper must own the only request fetch")
    outside_helper = prefix + suffix
    direct_network_tokens = (
        "page.request",
        "page['request']",
        'page["request"]',
        "['req'+'uest']",
        '["req"+"uest"]',
        ".fetch(",
        "fetch(",
        "axios",
        "XMLHttpRequest",
        "WebSocket",
        "addInitScript",
        ".evaluate(",
        "eval(",
        "Function(",
        "import(",
        "['fet'+'ch']",
        '["fet"+"ch"]',
        "['po'+'st']",
        '["po"+"st"]',
    )
    if any(token in outside_helper for token in direct_network_tokens):
        raise RuntimeError("evidence writes must use visible UI; public calls must use the audited helper")
    ast_check = subprocess.run(
        ["node", str(STATIC_CONTRACT), "--stdin"],
        cwd=PLAYWRIGHT,
        input=source,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ast_check.returncode != 0:
        raise RuntimeError(ast_check.stdout.strip())


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
