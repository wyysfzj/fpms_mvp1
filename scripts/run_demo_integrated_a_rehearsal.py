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
import zipfile
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
REHEARSAL_SCENARIO = {
    "customer_name": "澄岳智造技术（苏州）有限公司",
    "customer_code_prefix": "CYZN",
    "contact_name": "周岚",
    "contact_title": "知识产权经理",
    "contact_email": "zhou.lan@chengyue-ip.example",
    "case_no_prefix": "CYIP-CN-INV",
    "case_title": "一种柔性制造产线中视觉检测工位的自适应标定方法",
    "service_item_name": "授权登记阶段代理服务费",
    "bill_no_prefix": "AR-CYZN",
    "payment_no_prefix": "RCPT-CYZN",
    "bank_ref_prefix": "BTR-CYZN",
}
CUSTOMER_STAGE_ORDER = tuple(f"{index:02d}" for index in range(1, 10))


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


def integrated_evidence_descriptors(bundle: Path) -> list[dict[str, Any]]:
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest.get("evidence")
    if not isinstance(rows, list) or len(rows) != 12:
        raise RuntimeError("integrated evidence manifest must contain exactly twelve rows")
    descriptors: list[dict[str, Any]] = []
    bundle_root = bundle.resolve()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("integrated evidence row is invalid")
        source_path = (bundle_root / str(row.get("path", ""))).resolve()
        if bundle_root not in source_path.parents or not source_path.is_file():
            raise RuntimeError("integrated evidence path escapes or is unavailable")
        descriptors.append(
            {
                "role": row.get("role"),
                "path": str(source_path),
                "sha256": row.get("sha256"),
                "metadata": row.get("metadata"),
            }
        )
    return descriptors


def integrated_evidence_json(bundle: Path) -> str:
    return json.dumps(
        integrated_evidence_descriptors(bundle),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def materialize_oa_reply_outputs(output_root: Path) -> list[dict[str, Any]]:
    if output_root.exists() or output_root.is_symlink():
        raise RuntimeError(f"OA reply output root already exists: {output_root}")
    output_root.mkdir(parents=True)
    helpers = runpy.run_path(str(BACKEND / "tests" / "test_demo_abc_runtime_bundle.py"))
    write_docx = helpers.get("_write_docx")
    write_pdf = helpers.get("_write_pdf")
    if write_docx is None or write_pdf is None:
        raise RuntimeError("synthetic output writers are unavailable")

    definitions = (
        ("OA_STATEMENT_WORD", "审查意见答复意见陈述书（Word）", ".docx"),
        ("OA_STATEMENT_PDF", "审查意见答复意见陈述书（PDF）", ".pdf"),
        ("OA_MODIFIED_CLAIMS", "审查意见答复修改后权利要求书", ".docx"),
    )
    descriptors: list[dict[str, Any]] = []
    for oa_sequence in (1, 2):
        for role, label, suffix in definitions:
            sequence_label = "第一" if oa_sequence == 1 else "第二"
            title = f"{sequence_label}次{label}"
            output_path = output_root / f"oa{oa_sequence}-{role.lower()}{suffix}"
            if suffix == ".docx":
                write_docx(output_path)
                with zipfile.ZipFile(output_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr("customXml/fpms-demo-output-label.txt", title)
                media_type = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                write_pdf(output_path, unique_text=title)
                media_type = "application/pdf"
            descriptors.append(
                {
                    "oa_sequence": oa_sequence,
                    "official_file_role": role,
                    "title_zh_cn": title,
                    "classification": "SYNTHETIC_TEST_OUTPUT",
                    "path": str(output_path.resolve()),
                    "media_type": media_type,
                    "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
                }
            )
    if len({row["path"] for row in descriptors}) != 6 or len(
        {row["sha256"] for row in descriptors}
    ) != 6:
        raise RuntimeError("OA reply output identities must be unique")
    _write_json(output_root / "descriptors.json", descriptors)
    return descriptors


def oa_reply_outputs_json(descriptors: list[dict[str, Any]]) -> str:
    return json.dumps(descriptors, ensure_ascii=False, separators=(",", ":"))


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


def _checkpoint_map(run_artifact: Path) -> dict[str, dict[str, Any]]:
    ledger = json.loads((run_artifact / "task9-checkpoints.json").read_text(encoding="utf-8"))
    checkpoints = ledger.get("checkpoints")
    expected = [f"IA-{index:02d}" for index in range(19)]
    if not isinstance(checkpoints, list) or [row.get("checkpoint") for row in checkpoints] != expected:
        raise RuntimeError("integrated checkpoint ledger must contain IA-00 through IA-18 exactly once")
    bindings = ledger.get("evidence_bindings")
    if not isinstance(bindings, list) or len(bindings) != 12:
        raise RuntimeError("integrated checkpoint ledger must contain twelve evidence bindings")
    return {row["checkpoint"]: row["result"] for row in checkpoints}


def build_diagnostic_summary(artifact: Path, runs: int) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    identity_sets: list[set[str]] = []
    run_ids: list[str] = []
    for ordinal in range(1, runs + 1):
        run_artifact = artifact / f"run{ordinal}"
        checkpoints = _checkpoint_map(run_artifact)
        final = checkpoints["IA-18"]
        expected_final = {
            "lifecycle_status": "GRANT_REGISTRATION_IN_PROGRESS",
            "lifecycle_stage": "GRANT_REGISTRATION",
            "application_status": "APPLICATION_PENDING",
            "source_state": "CONFIRMED",
            "legacy_display": "GRANT_PENDING",
            "bill_status": "SETTLED",
            "payment_status": "FULLY_ALLOCATED",
            "bill_balance": "0.00",
            "payment_unapplied": "0.00",
            "currency": "CNY",
            "checkpoints_passed": 19,
        }
        if any(final.get(key) != value for key, value in expected_final.items()):
            raise RuntimeError(f"run {ordinal} final state does not match the frozen contract")
        cleanup = json.loads((run_artifact / "cleanup.json").read_text(encoding="utf-8"))
        if cleanup.get("run_root_removed") is not True:
            raise RuntimeError(f"run {ordinal} cleanup is incomplete")
        run_ids.append(str(cleanup.get("run_id", "")))
        command = json.loads((run_artifact / "command.json").read_text(encoding="utf-8"))
        if command.get("redacted") is not True or "environment_keys" not in command:
            raise RuntimeError(f"run {ordinal} command metadata is not redacted")
        if (run_artifact / "integrated-final.png").stat().st_size == 0:
            raise RuntimeError(f"run {ordinal} final screenshot is empty")
        role_map = json.loads((run_artifact / "evidence-role-map.json").read_text(encoding="utf-8"))
        if not isinstance(role_map, list) or len(role_map) != 12:
            raise RuntimeError(f"run {ordinal} evidence role map is incomplete")
        identities = {
            checkpoints["IA-01"]["client_id"],
            checkpoints["IA-01"]["contact_id"],
            checkpoints["IA-02"]["case_id"],
            checkpoints["IA-04"]["package_id"],
            checkpoints["IA-13"]["draft_id"],
            checkpoints["IA-14"]["bill_id"],
            checkpoints["IA-15"]["payment_id"],
            checkpoints["IA-15"]["payment_line_id"],
            checkpoints["IA-16"]["offset_id"],
        }
        if len(identities) != 9 or any(not value for value in identities):
            raise RuntimeError(f"run {ordinal} business identity set is incomplete")
        identity_sets.append(identities)
        summaries.append(expected_final)
    if len(set(run_ids)) != runs or any(identity_sets[left] & identity_sets[right] for left in range(runs) for right in range(left + 1, runs)):
        raise RuntimeError("integrated runs must use distinct run and business identities")
    return {
        "status": "DIAGNOSTIC_PASS",
        "runs": runs,
        "checkpoint_counts": [19] * runs,
        "evidence_binding_counts": [12] * runs,
        "run_ids": run_ids,
        "business_identity_sets_disjoint": True,
        "final_states": summaries,
    }


def write_checksums(artifact: Path) -> None:
    rows = []
    for path in sorted(item for item in artifact.rglob("*") if item.is_file() and item.name != "checksums.sha256"):
        rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(artifact)}")
    (artifact / "checksums.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")


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
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    template = manifest["templates"][0]
    rate = manifest["rates"][0]
    if rate.get("name_zh_cn") != REHEARSAL_SCENARIO["service_item_name"]:
        raise RuntimeError("integrated service item does not match the approved scenario")
    admin_password = secrets.token_urlsafe(24)
    reviewer_password = secrets.token_urlsafe(24)
    oa_reply_outputs = materialize_oa_reply_outputs(run_artifact / "oa-reply-outputs")
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
            FPMS_DEMO_EXPECTED_BUNDLE_ID=manifest["bundle_id"],
            FPMS_DEMO_EXPECTED_BUNDLE_VERSION=manifest["bundle_version"],
            FPMS_DEMO_EXPECTED_TEMPLATE_CODE=template["template_code"],
            FPMS_DEMO_EXPECTED_TEMPLATE_SHA256=template["sha256"],
            FPMS_DEMO_EXPECTED_RATE_ITEM_CODE=rate["item_code"],
            FPMS_DEMO_EXPECTED_RATE_SOURCE_REF=rate["source_ref"],
            FPMS_DEMO_EXPECTED_RATE_SOURCE_VERSION=rate["source_version"],
            FPMS_DEMO_EXPECTED_RATE_SOURCE_SHA256=rate["source_sha256"],
            FPMS_DEMO_EXPECTED_DISCLAIMER_ZH_CN=rate["disclaimer_zh_cn"],
            FPMS_DEMO_INTEGRATED_EVIDENCE_JSON=integrated_evidence_json(bundle),
            FPMS_DEMO_INTEGRATED_OA_REPLY_OUTPUT_JSON=oa_reply_outputs_json(oa_reply_outputs),
            FPMS_DEMO_CUSTOMER_NAME=REHEARSAL_SCENARIO["customer_name"],
            FPMS_DEMO_CUSTOMER_CODE_PREFIX=REHEARSAL_SCENARIO["customer_code_prefix"],
            FPMS_DEMO_CONTACT_NAME=REHEARSAL_SCENARIO["contact_name"],
            FPMS_DEMO_CONTACT_TITLE=REHEARSAL_SCENARIO["contact_title"],
            FPMS_DEMO_CONTACT_EMAIL=REHEARSAL_SCENARIO["contact_email"],
            FPMS_DEMO_CASE_NO_PREFIX=REHEARSAL_SCENARIO["case_no_prefix"],
            FPMS_DEMO_CASE_TITLE=REHEARSAL_SCENARIO["case_title"],
            FPMS_DEMO_SERVICE_ITEM_NAME=REHEARSAL_SCENARIO["service_item_name"],
            FPMS_DEMO_BILL_NO_PREFIX=REHEARSAL_SCENARIO["bill_no_prefix"],
            FPMS_DEMO_PAYMENT_NO_PREFIX=REHEARSAL_SCENARIO["payment_no_prefix"],
            FPMS_DEMO_BANK_REF_PREFIX=REHEARSAL_SCENARIO["bank_ref_prefix"],
            FPMS_DEMO_CUSTOMER_STAGE_ORDER=",".join(CUSTOMER_STAGE_ORDER),
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
        _write_json(
            run_artifact / "command.json",
            {
                "redacted": True,
                "command": command,
                "environment_keys": sorted(key for key in browser_env if key.startswith("FPMS_")),
            },
        )
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
            abc.remove_run_root(run_root, run_id)
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
    _write_json(artifact / "summary.json", build_diagnostic_summary(artifact, args.runs))
    write_checksums(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
