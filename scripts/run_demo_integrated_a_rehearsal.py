from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import runpy
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from contextlib import contextmanager
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator, NamedTuple
from urllib.parse import parse_qs, urlencode, urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_demo_abc_rehearsal as abc  # noqa: E402

BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.demo_bundle import load_demo_bundle  # noqa: E402

PLAYWRIGHT = ROOT / "FPMS_Automation_Skeleton_Pack" / "playwright_ts"
LEGACY_SPEC = PLAYWRIGHT / "src" / "tests" / "demo-integrated-a.live-backend.spec.ts"
SPEC = PLAYWRIGHT / "src" / "tests" / "demo-integrated-v6.live-backend.spec.ts"
STATIC_CONTRACT = PLAYWRIGHT / "src" / "tests" / "demo-integrated-a-static-contract.mjs"
V6_STATIC_CONTRACT = PLAYWRIGHT / "src" / "tests" / "demo-integrated-v6-static-contract.mjs"
DEFAULT_ARTIFACT = ROOT / "artifacts" / "FPMS-DEMO-INTEGRATED-A-DIAGNOSTIC"
UI_SESSION_CONTRACT_VERSION = json.loads(
    (
        ROOT
        / "FPMS_Automation_Skeleton_Pack"
        / "data"
        / "testcases"
        / "demo_v6_ui_parity_v1.json"
    ).read_text(encoding="utf-8")
)["schema_id"]
UI_SESSION_TIMEOUT_SECONDS = 12 * 60 * 60
UI_SESSION_MAX_BODY_BYTES = 2_000_000
UI_SESSION_OBSERVER_FILES = frozenset(
    {"observer-ui-ledger.json"}
    | {f"observer-stage-{stage:02d}.png" for stage in range(1, 12)}
)
_UI_SESSION_TUPLE_KEYS = (
    "contract_version",
    "run_id",
    "candidate_commit",
    "candidate_tree",
    "authority_sha256",
    "actor",
)
_UI_SESSION_INTERNAL_OBSERVER_FILES = frozenset({"finalize-binding.json"})
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_PNG_END = b"IEND\xaeB`\x82"
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
V6_CUSTOMER_STAGES = (
    ("01", "客户与案件"),
    ("02", "文件与递交准备"),
    ("03", "受理与审查"),
    ("04", "第一轮 OA"),
    ("05", "第二轮 OA"),
    ("06", "授权登记准备"),
    ("07", "生效官费预览"),
    ("08", "双草单与服务费调整"),
    ("09", "官费清单与待凭证登记"),
    ("10", "两次客户回款与核销"),
    ("11", "同案双轨汇总"),
)
CUSTOMER_STAGE_ORDER = tuple(stage for stage, _label in V6_CUSTOMER_STAGES)
LEGACY_CUSTOMER_STAGE_ORDER = tuple(f"{index:02d}" for index in range(1, 10))
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FPMS Integrated Scheme A rehearsal")
    parser.add_argument(
        "--profile",
        choices=("TECHNICAL_REHEARSAL", "CUSTOMER_DEMO"),
    )
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--expected-authority-sha256")
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--runs", type=int, choices=(1, 2))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--ui-session", action="store_true")
    parser.add_argument("--actor", choices=("HUMAN", "CODEX"))
    args = parser.parse_args(argv)
    if args.ui_session:
        forbidden = (
            args.profile,
            args.bundle,
            args.expected_manifest_sha256,
            args.expected_authority_sha256,
            args.runs,
            args.headless,
        )
        if args.actor is None or args.artifact is None:
            parser.error("--ui-session requires --actor and --artifact")
        if not args.artifact.is_absolute():
            parser.error("--ui-session artifact must be absolute")
        if any(value not in (None, False) for value in forbidden):
            parser.error("--ui-session accepts only --actor and --artifact")
        args.profile = "TECHNICAL_REHEARSAL"
        args.runs = 1
        return args
    if args.actor is not None:
        parser.error("--actor requires --ui-session")
    if args.profile is None:
        parser.error("--profile is required")
    if args.artifact is None:
        args.artifact = DEFAULT_ARTIFACT
    if args.runs is None:
        args.runs = 2
    return args


def build_integrated_bundle(parent: Path) -> tuple[Path, str, str]:
    helpers = runpy.run_path(str(BACKEND / "tests" / "test_demo_abc_runtime_bundle.py"))
    builder = helpers.get("_valid_v6_bundle")
    if builder is None:
        raise RuntimeError("integrated-a-v2 bundle builder is unavailable")
    bundle, _manifest, manifest_sha = builder(parent)
    authority_sha = hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest()
    return bundle, manifest_sha, authority_sha


def resolve_runtime_bundle(
    args: argparse.Namespace, synthetic_parent: Path
) -> tuple[Path, str, str]:
    supplied = (
        args.bundle,
        args.expected_manifest_sha256,
        args.expected_authority_sha256,
    )
    if args.profile == "TECHNICAL_REHEARSAL" and all(value is None for value in supplied):
        return build_integrated_bundle(synthetic_parent)
    if any(value is None for value in supplied):
        raise RuntimeError("customer bundle arguments must be supplied together")
    bundle = args.bundle
    assert bundle is not None
    if not bundle.is_absolute():
        raise RuntimeError("runtime bundle path must be absolute")
    manifest_sha = str(args.expected_manifest_sha256)
    authority_sha = str(args.expected_authority_sha256)
    if _SHA256_RE.fullmatch(manifest_sha) is None or _SHA256_RE.fullmatch(authority_sha) is None:
        raise RuntimeError("runtime bundle digests must be exact lowercase SHA-256 values")
    expected_classification = (
        "CUSTOMER_AUTHORIZED"
        if args.profile == "CUSTOMER_DEMO"
        else "SYNTHETIC_TEST_ONLY"
    )
    snapshot = load_demo_bundle(
        bundle,
        expected_manifest_sha256=manifest_sha,
        expected_authority_sha256=authority_sha,
        expected_authority_classification=expected_classification,
        repo_root=ROOT,
    )
    if snapshot.schema_version != "fpms.demo-input-bundle/integrated-a-v2":
        raise RuntimeError("runtime bundle must use the integrated-a-v2 contract")
    return snapshot.bundle_root, manifest_sha, authority_sha


def assert_fresh_run_paths(run_root: Path, database_path: Path) -> None:
    candidates = (
        run_root,
        database_path,
        Path(f"{database_path}-wal"),
        Path(f"{database_path}-shm"),
    )
    existing = [path for path in candidates if path.exists() or path.is_symlink()]
    if existing:
        raise RuntimeError(f"demo run path already exists: {existing[0]}")


def build_run_record(
    *,
    run_id: str,
    database_path: Path,
    manifest_sha256: str,
    created_at: str,
) -> dict[str, str]:
    if not database_path.is_absolute():
        raise RuntimeError("run database path must be absolute")
    if _SHA256_RE.fullmatch(manifest_sha256) is None:
        raise RuntimeError("run bundle digest must be an exact lowercase SHA-256 value")
    return {
        "run_id": run_id,
        "database_path": str(database_path),
        "bundle_manifest_sha256": manifest_sha256,
        "created_at": created_at,
    }


def integrated_evidence_descriptors(bundle: Path) -> list[dict[str, Any]]:
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest.get("evidence")
    if not isinstance(rows, list) or len(rows) != 12:
        raise RuntimeError("integrated evidence manifest must contain exactly twelve rows")
    descriptors: list[dict[str, Any]] = []
    bundle_root = bundle.resolve()
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError("integrated evidence row is invalid")
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
        ("OA_STATEMENT_WORD", "审查意见答复意见陈述书（Word）", "意见陈述书", ".docx"),
        ("OA_STATEMENT_PDF", "审查意见答复意见陈述书（PDF）", "意见陈述书", ".pdf"),
        ("OA_MODIFIED_CLAIMS", "审查意见答复修改后权利要求书", "修改后权利要求书", ".docx"),
    )
    descriptors: list[dict[str, Any]] = []
    for oa_sequence in (1, 2):
        for role, label, file_label, suffix in definitions:
            sequence_label = "第一" if oa_sequence == 1 else "第二"
            title = f"{sequence_label}次{label}"
            output_path = output_root / (
                f"{sequence_label}次审查意见答复_{file_label}{suffix}"
            )
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


class DemoRunContext(NamedTuple):
    run_id: str
    run_root: Path
    database_path: Path
    bundle: Path
    manifest_sha: str
    authority_sha: str
    candidate_commit: str
    candidate_tree: str
    admin_password: str
    reviewer_password: str
    env: dict[str, str]


class ObserverBinding(NamedTuple):
    activation_url: str
    finalized: threading.Event
    failed: threading.Event
    errors: list[str]


def _new_run_context(
    *,
    run_id: str,
    bundle: Path,
    manifest_sha: str,
    authority_sha: str,
    candidate: dict[str, Any],
    profile: str,
    ui_session: bool,
) -> DemoRunContext:
    run_root = (
        Path(tempfile.gettempdir()).resolve() / f"fpms-demo-abc-{run_id}"
    )
    database_path = run_root / "fpms-demo.db"
    assert_fresh_run_paths(run_root, database_path)
    admin_password = secrets.token_urlsafe(24)
    reviewer_password = secrets.token_urlsafe(24)
    env = os.environ.copy()
    env.pop("FPMS_DEMO_UI_SESSION", None)
    env.pop("FPMS_DEMO_CONTRACT_VERSION", None)
    env.update(
        FPMS_ENV="demo",
        FPMS_DEMO_SCOPE="LOCAL_ABC_E2E",
        FPMS_DEMO_RUN_PROFILE=profile,
        FPMS_DEMO_RUN_ID=run_id,
        FPMS_DEMO_BUNDLE_PATH=str(bundle),
        FPMS_DEMO_EXPECTED_MANIFEST_SHA256=manifest_sha,
        FPMS_DEMO_EXPECTED_AUTHORITY_SHA256=authority_sha,
        FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION=(
            "CUSTOMER_AUTHORIZED" if profile == "CUSTOMER_DEMO" else "SYNTHETIC_TEST_ONLY"
        ),
        FPMS_DEMO_CANDIDATE_COMMIT=str(candidate["commit"]),
        FPMS_DEMO_CANDIDATE_TREE=str(candidate["tree"]),
        FPMS_DEMO_ADMIN_USERNAME="admin",
        FPMS_DEMO_ADMIN_PASSWORD=admin_password,
        FPMS_DEMO_REVIEWER_USERNAME="demo_evidence_reviewer",
        FPMS_DEMO_REVIEWER_PASSWORD=reviewer_password,
        JWT_SECRET=secrets.token_urlsafe(48),
        NO_PROXY="127.0.0.1,localhost",
        no_proxy="127.0.0.1,localhost",
    )
    if ui_session:
        env.update(
            FPMS_DEMO_UI_SESSION="1",
            FPMS_DEMO_CONTRACT_VERSION=UI_SESSION_CONTRACT_VERSION,
        )
    return DemoRunContext(
        run_id=run_id,
        run_root=run_root,
        database_path=database_path,
        bundle=bundle,
        manifest_sha=manifest_sha,
        authority_sha=authority_sha,
        candidate_commit=str(candidate["commit"]),
        candidate_tree=str(candidate["tree"]),
        admin_password=admin_password,
        reviewer_password=reviewer_password,
        env=env,
    )


def _start_services(context: DemoRunContext, runner_log: Path) -> subprocess.Popen[bytes]:
    with runner_log.open("wb") as output:
        return subprocess.Popen(
            [sys.executable, "-m", "scripts.run_local_demo_abc"],
            cwd=BACKEND,
            env=context.env,
            stdout=output,
            stderr=subprocess.STDOUT,
        )


def _stop_process(process: subprocess.Popen[bytes] | None, *, interrupt: bool) -> None:
    if process is None or process.poll() is not None:
        return
    if interrupt:
        process.send_signal(signal.SIGINT)
    else:
        process.terminate()
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _remove_run_root(context: DemoRunContext) -> None:
    run_root = context.run_root
    run_id = context.run_id
    abc.remove_run_root(run_root, run_id)


def _remove_finalized_ui_run(artifact: Path, context: DemoRunContext) -> None:
    session = json.loads((artifact / "session.json").read_text(encoding="utf-8"))
    expected_root = (
        Path(tempfile.gettempdir()).resolve() / f"fpms-demo-abc-{context.run_id}"
    )
    if (
        context.run_root.is_symlink()
        or context.run_root != expected_root
        or session.get("run_id") != context.run_id
        or session.get("run_root") != str(context.run_root)
        or session.get("artifact") != str(artifact)
        or not context.database_path.is_file()
    ):
        raise RuntimeError(f"refusing invalid UI-session cleanup root: {context.run_root}")
    _remove_run_root(context)


@contextmanager
def _observer_binding(
    observer_root: Path,
    session_tuple: dict[str, str],
) -> Iterator[ObserverBinding]:
    observer_root = observer_root.resolve()
    observer_root.mkdir(parents=True, exist_ok=True)
    if set(session_tuple) != set(_UI_SESSION_TUPLE_KEYS):
        raise RuntimeError("invalid UI-session observer tuple")
    expected_tuple = {key: session_tuple[key] for key in _UI_SESSION_TUPLE_KEYS}
    capability = secrets.token_urlsafe(32)
    finalized = threading.Event()
    failed = threading.Event()
    errors: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def _response(self, status: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(body)

        def _reject(self, status: int, error: str, *, terminal: bool = True) -> None:
            if terminal:
                errors.append(error)
                failed.set()
            self._response(status, {"error": error})

        def _payload(self) -> dict[str, object] | None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._reject(400, "MALFORMED_REQUEST")
                return None
            if not 0 < length <= UI_SESSION_MAX_BODY_BYTES:
                self._reject(400, "MALFORMED_REQUEST")
                return None
            try:
                payload = json.loads(self.rfile.read(length))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._reject(400, "MALFORMED_REQUEST")
                return None
            if not isinstance(payload, dict):
                self._reject(400, "MALFORMED_REQUEST")
                return None
            return payload

        def _valid_tuple(self, payload: dict[str, object]) -> bool:
            if any(payload.get(key) != value for key, value in expected_tuple.items()):
                self._reject(409, "SESSION_TUPLE_CONFLICT")
                return False
            return True

        def _validate_ledger(self, content: object) -> bool:
            if not isinstance(content, dict):
                return False
            return (
                content.get("schema_id") == expected_tuple["contract_version"]
                and content.get("session") == expected_tuple
                and isinstance(content.get("events"), list)
            )

        def _exclusive_write(self, target: Path, content: bytes) -> bool:
            try:
                descriptor = os.open(
                    target,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
            except FileExistsError:
                self._reject(409, "OBSERVER_EVIDENCE_CONFLICT")
                return False
            try:
                with os.fdopen(descriptor, "wb") as output:
                    output.write(content)
            except Exception:
                target.unlink(missing_ok=True)
                raise
            return True

        def _write_observer_artifact(self, payload: dict[str, object]) -> None:
            expected_keys = set(_UI_SESSION_TUPLE_KEYS) | {
                "filename",
                "encoding",
                "content",
            }
            if set(payload) != expected_keys:
                self._reject(400, "MALFORMED_OBSERVER_ARTIFACT")
                return
            filename = payload.get("filename")
            if not isinstance(filename, str) or filename not in UI_SESSION_OBSERVER_FILES:
                self._reject(400, "MALFORMED_OBSERVER_ARTIFACT")
                return
            target = observer_root / filename
            if target.parent.resolve() != observer_root or target.exists() or target.is_symlink():
                self._reject(409, "OBSERVER_EVIDENCE_CONFLICT")
                return
            if filename.endswith(".json"):
                if payload.get("encoding") != "json" or not self._validate_ledger(
                    payload.get("content")
                ):
                    self._reject(400, "MALFORMED_OBSERVER_ARTIFACT")
                    return
                content = (
                    json.dumps(
                        payload["content"], ensure_ascii=False, indent=2
                    )
                    + "\n"
                ).encode()
            else:
                encoded = payload.get("content")
                if payload.get("encoding") != "base64" or not isinstance(encoded, str):
                    self._reject(400, "MALFORMED_OBSERVER_ARTIFACT")
                    return
                try:
                    content = base64.b64decode(encoded, validate=True)
                except (ValueError, binascii.Error):
                    self._reject(400, "MALFORMED_OBSERVER_ARTIFACT")
                    return
                if not content.startswith(_PNG_SIGNATURE) or not content.endswith(_PNG_END):
                    self._reject(400, "MALFORMED_OBSERVER_ARTIFACT")
                    return
            if self._exclusive_write(target, content):
                self._response(201, {"filename": filename})

        def _evidence_complete(self) -> bool:
            entries = {path.name for path in observer_root.iterdir()}
            allowed = UI_SESSION_OBSERVER_FILES | _UI_SESSION_INTERNAL_OBSERVER_FILES
            if entries - allowed or not UI_SESSION_OBSERVER_FILES <= entries:
                return False
            for filename in UI_SESSION_OBSERVER_FILES:
                target = observer_root / filename
                if target.is_symlink() or not target.is_file():
                    return False
            try:
                ledger = json.loads(
                    (observer_root / "observer-ui-ledger.json").read_text(
                        encoding="utf-8"
                    )
                )
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                return False
            if not self._validate_ledger(ledger):
                return False
            return all(
                (observer_root / filename).read_bytes().startswith(_PNG_SIGNATURE)
                and (observer_root / filename).read_bytes().endswith(_PNG_END)
                for filename in UI_SESSION_OBSERVER_FILES
                if filename.endswith(".png")
            )

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlsplit(self.path)
            if parse_qs(parsed.query, keep_blank_values=True).get("capability") != [
                capability
            ]:
                self._reject(401, "CAPABILITY_REQUIRED", terminal=False)
                return
            if parsed.path not in {"/revalidate", "/observer-artifact", "/finalize"}:
                self._reject(404, "NOT_FOUND")
                return
            payload = self._payload()
            if payload is None or not self._valid_tuple(payload):
                return
            if parsed.path == "/revalidate":
                if set(payload) != set(_UI_SESSION_TUPLE_KEYS):
                    self._reject(400, "MALFORMED_REQUEST")
                    return
                self._response(200, {"status": "VALID"})
                return
            if parsed.path == "/observer-artifact":
                self._write_observer_artifact(payload)
                return
            if set(payload) != set(_UI_SESSION_TUPLE_KEYS):
                self._reject(400, "MALFORMED_REQUEST")
                return
            if not self._evidence_complete():
                self._reject(409, "OBSERVER_EVIDENCE_INCOMPLETE")
                return
            finalized.set()
            self._response(200, {"status": "FINALIZED"})

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        activation_url = f"http://{host}:{port}/observer-artifact?" + urlencode(
            {
                "capability": capability,
                "actor": expected_tuple["actor"],
            }
        )
        yield ObserverBinding(
            activation_url=activation_url,
            finalized=finalized,
            failed=failed,
            errors=errors,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _start_headed_browser(
    command: list[str], env: dict[str, str]
) -> subprocess.Popen[bytes]:
    return subprocess.Popen(command, cwd=PLAYWRIGHT, env=env)


def _wait_for_browser_finalization(
    binding: ObserverBinding,
    browser_process: subprocess.Popen[bytes],
) -> str:
    deadline = time.monotonic() + UI_SESSION_TIMEOUT_SECONDS
    while True:
        if binding.failed.is_set():
            error = binding.errors[-1] if binding.errors else "UNKNOWN_HOST_ERROR"
            raise RuntimeError(f"observer host rejected browser state: {error}")
        if binding.finalized.is_set():
            return "FINALIZED"
        if browser_process.poll() is not None:
            return "STOPPED"
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "STOPPED"
        binding.finalized.wait(min(0.1, remaining))


def _run_ui_browser_session(
    args: argparse.Namespace,
    context: DemoRunContext,
    artifact: Path,
) -> str:
    artifact.mkdir(parents=True, exist_ok=True)
    if not context.database_path.is_file():
        raise RuntimeError("UI session database was not created")
    session_tuple = {
        "contract_version": UI_SESSION_CONTRACT_VERSION,
        "run_id": context.run_id,
        "candidate_commit": context.candidate_commit,
        "candidate_tree": context.candidate_tree,
        "authority_sha256": context.authority_sha,
        "actor": str(args.actor),
    }
    _write_json(
        artifact / "session.json",
        {
            **session_tuple,
            "run_root": str(context.run_root),
            "database_path": str(context.database_path),
            "artifact": str(artifact),
        },
    )
    observer_root = (artifact / "observer").resolve()
    browser_process: subprocess.Popen[bytes] | None = None
    try:
        with _observer_binding(observer_root, session_tuple) as binding:
            page_url = "http://127.0.0.1:5173/?" + urlencode(
                {"fpmsObserverBinding": binding.activation_url}
            )
            redacted_page_url = "http://127.0.0.1:5173/?" + urlencode(
                {"fpmsObserverBinding": "<redacted>"}
            )
            browser_command = [
                "node",
                "./node_modules/.bin/playwright",
                "open",
                "--browser=chromium",
                page_url,
            ]
            _write_json(
                observer_root / "finalize-binding.json",
                {
                    **session_tuple,
                    "observer_artifact_root": str(observer_root),
                    "observer_binding_origin": (
                        f"{urlsplit(binding.activation_url).scheme}://"
                        f"{urlsplit(binding.activation_url).netloc}"
                    ),
                    "capability": "<redacted>",
                    "operations": [
                        "/revalidate",
                        "/observer-artifact",
                        "/finalize",
                    ],
                    "required_observer_files": sorted(UI_SESSION_OBSERVER_FILES),
                    "browser_command": [*browser_command[:-1], redacted_page_url],
                },
            )
            browser_process = _start_headed_browser(browser_command, context.env)
            print(
                json.dumps(
                    {
                        "run_id": context.run_id,
                        "url": redacted_page_url,
                        "credentials": [
                            {"username": "admin", "password": "<redacted>"},
                            {
                                "username": "demo_evidence_reviewer",
                                "password": "<redacted>",
                            },
                        ],
                    },
                    ensure_ascii=False,
                )
            )
            return _wait_for_browser_finalization(binding, browser_process)
    except Exception:
        _write_json(
            observer_root / "session-status.json",
            {"status": "FAILED", "run_id": context.run_id, "run_root_removed": False},
        )
        raise
    finally:
        _stop_process(browser_process, interrupt=False)


def _complete_ui_session(
    context: DemoRunContext,
    artifact: Path,
    status: str,
) -> None:
    if status == "FINALIZED":
        _remove_finalized_ui_run(artifact, context)
    _write_json(
        artifact / "observer" / "session-status.json",
        {
            "status": status,
            "run_id": context.run_id,
            "run_root_removed": not context.run_root.exists(),
        },
    )


def _run_ui_session(
    args: argparse.Namespace,
    bundle: Path,
    manifest_sha: str,
    authority_sha: str,
    candidate: dict[str, Any],
) -> None:
    artifact = args.artifact
    assert artifact is not None and artifact.is_absolute()
    artifact = artifact.resolve()
    if artifact.exists() or artifact.is_symlink():
        raise RuntimeError(f"evidence path already exists: {artifact}")
    context = _new_run_context(
        run_id=f"ui-{str(args.actor).lower()}-{secrets.token_hex(6)}",
        bundle=bundle,
        manifest_sha=manifest_sha,
        authority_sha=authority_sha,
        candidate=candidate,
        profile="TECHNICAL_REHEARSAL",
        ui_session=True,
    )
    artifact.mkdir(parents=True)
    service_process = _start_services(context, artifact / "runner.log")
    try:
        abc.wait_url("http://127.0.0.1:8000/healthz", service_process)
        abc.wait_url("http://127.0.0.1:5173", service_process)
        status = _run_ui_browser_session(args, context, artifact)
    except Exception:
        _write_json(
            artifact / "observer" / "session-status.json",
            {"status": "FAILED", "run_id": context.run_id, "run_root_removed": False},
        )
        raise
    finally:
        _stop_process(service_process, interrupt=True)
    _complete_ui_session(context, artifact, status)


def _checkpoint_map(run_artifact: Path) -> dict[str, dict[str, Any]]:
    ledger = json.loads((run_artifact / "task9-checkpoints.json").read_text(encoding="utf-8"))
    checkpoints = ledger.get("checkpoints")
    expected = [f"IA-{index:02d}" for index in range(13)]
    if not isinstance(checkpoints, list) or [row.get("checkpoint") for row in checkpoints] != expected:
        raise RuntimeError("V6 lifecycle prefix must contain IA-00 through IA-12 exactly once")
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
        cleanup = json.loads((run_artifact / "cleanup.json").read_text(encoding="utf-8"))
        if cleanup.get("run_root_removed") is not True:
            raise RuntimeError(f"run {ordinal} cleanup is incomplete")
        run_ids.append(str(cleanup.get("run_id", "")))
        command = json.loads((run_artifact / "command.json").read_text(encoding="utf-8"))
        if command.get("redacted") is not True or "environment_keys" not in command:
            raise RuntimeError(f"run {ordinal} command metadata is not redacted")
        if (run_artifact / "v6-final.png").stat().st_size == 0:
            raise RuntimeError(f"run {ordinal} final screenshot is empty")
        v6_ledger = json.loads((run_artifact / "v6-stages.json").read_text(encoding="utf-8"))
        v6_stages = v6_ledger.get("stages")
        if not isinstance(v6_stages, list) or [row.get("stage") for row in v6_stages] != list(CUSTOMER_STAGE_ORDER):
            raise RuntimeError(f"run {ordinal} V6 stage ledger is incomplete")
        if v6_ledger.get("network_errors") != [] or v6_ledger.get("console_errors") != []:
            raise RuntimeError(f"run {ordinal} contains browser errors")
        stage_map = {row["stage"]: row for row in v6_stages}
        finance = stage_map["10"]
        v6_final = v6_stages[-1]
        expected_final = {
            "partial_status": "PARTIALLY_SETTLED",
            "partial_balance": "600.00",
            "final_status": "SETTLED",
            "final_balance": "0.00",
            "amount_equation": "1200.00 + 600.00 = 1800.00",
            "bill_status": "SETTLED",
            "bill_balance": "0.00",
        }
        actual_final = {
            "partial_status": finance.get("partial_status"),
            "partial_balance": finance.get("partial_balance"),
            "final_status": finance.get("final_status"),
            "final_balance": finance.get("final_balance"),
            "amount_equation": finance.get("amount_equation"),
            "bill_status": v6_final.get("bill_status"),
            "bill_balance": v6_final.get("bill_balance"),
        }
        if actual_final != expected_final:
            raise RuntimeError(f"run {ordinal} V6 final finance state is incomplete")
        role_map = json.loads((run_artifact / "evidence-role-map.json").read_text(encoding="utf-8"))
        if not isinstance(role_map, list) or len(role_map) != 12:
            raise RuntimeError(f"run {ordinal} evidence role map is incomplete")
        identities = {
            checkpoints["IA-01"]["client_id"],
            checkpoints["IA-01"]["contact_id"],
            checkpoints["IA-02"]["case_id"],
            checkpoints["IA-04"]["package_id"],
            checkpoints["IA-11"]["replacement_task_id"],
            stage_map["07"]["gov_draft_id"],
            stage_map["08"]["service_draft_id"],
            finance["bill_id"],
            finance["first_payment_id"],
            finance["second_payment_id"],
            finance["first_offset_id"],
            finance["second_offset_id"],
        }
        if len(identities) != 12 or any(not value for value in identities):
            raise RuntimeError(f"run {ordinal} business identity set is incomplete")
        identity_sets.append(identities)
        summaries.append(actual_final)
    if len(set(run_ids)) != runs or any(identity_sets[left] & identity_sets[right] for left in range(runs) for right in range(left + 1, runs)):
        raise RuntimeError("integrated runs must use distinct run and business identities")
    return {
        "status": "TECHNICAL_REHEARSAL_PASS",
        "runs": runs,
        "checkpoint_counts": [13] * runs,
        "v6_stage_counts": [11] * runs,
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


def validate_v6_customer_acceptance_receipts(evidence_dir: Path | None = None) -> dict[str, Any]:
    configured = os.environ.get("FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR")
    root = evidence_dir or (Path(configured) if configured else None)
    if root is None:
        raise RuntimeError("FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR is required")
    root = root.resolve()
    run_ids: list[str] = []
    database_paths: list[str] = []
    manifest_digests: list[str] = []
    for ordinal in (1, 2):
        run = root / f"run{ordinal}"
        run_record = json.loads((run / "run.json").read_text(encoding="utf-8"))
        receipt = json.loads((run / "pass-receipt.json").read_text(encoding="utf-8"))
        stages = json.loads((run / "v6-stages.json").read_text(encoding="utf-8"))
        if receipt.get("status") != "PASS" or receipt.get("profile") != "CUSTOMER_DEMO":
            raise RuntimeError(f"run {ordinal} customer PASS receipt is invalid")
        if receipt.get("stage_count") != 11:
            raise RuntimeError(f"run {ordinal} stage receipt is incomplete")
        if stages.get("network_errors") != [] or stages.get("console_errors") != []:
            raise RuntimeError(f"run {ordinal} browser evidence contains errors")
        stage_rows = stages.get("stages")
        if not isinstance(stage_rows, list) or [row.get("stage") for row in stage_rows] != list(CUSTOMER_STAGE_ORDER):
            raise RuntimeError(f"run {ordinal} stage order is invalid")
        run_ids.append(str(run_record.get("run_id", "")))
        database_paths.append(str(run_record.get("database_path", "")))
        manifest_digests.append(str(run_record.get("bundle_manifest_sha256", "")))
    if len(set(run_ids)) != 2 or len(set(database_paths)) != 2:
        raise RuntimeError("customer acceptance requires two distinct runs and databases")
    if len(set(manifest_digests)) != 1 or _SHA256_RE.fullmatch(manifest_digests[0]) is None:
        raise RuntimeError("customer acceptance input digests do not match")
    return {
        "status": "CUSTOMER_DEMO_PASS",
        "runs": 2,
        "run_ids": run_ids,
        "database_paths": database_paths,
        "bundle_manifest_sha256": manifest_digests[0],
    }


def _run_one(
    ordinal: int,
    artifact: Path,
    bundle: Path,
    manifest_sha: str,
    authority_sha: str,
    candidate: dict[str, Any],
    headless: bool,
    profile: str,
) -> None:
    run_id = f"integrated-r{ordinal}-{secrets.token_hex(6)}"
    context = _new_run_context(
        run_id=run_id,
        bundle=bundle,
        manifest_sha=manifest_sha,
        authority_sha=authority_sha,
        candidate=candidate,
        profile=profile,
        ui_session=False,
    )
    run_root = context.run_root
    database_path = context.database_path
    admin_password = context.admin_password
    reviewer_password = context.reviewer_password
    env = context.env
    run_artifact = artifact / f"run{ordinal}"
    run_artifact.mkdir()
    _write_json(
        run_artifact / "run.json",
        build_run_record(
            run_id=run_id,
            database_path=database_path,
            manifest_sha256=manifest_sha,
            created_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        ),
    )
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    template = manifest["templates"][0]
    rate = manifest["rates"][0]
    if rate.get("name_zh_cn") != REHEARSAL_SCENARIO["service_item_name"]:
        raise RuntimeError("integrated service item does not match the approved scenario")
    oa_reply_outputs = materialize_oa_reply_outputs(run_artifact / "oa-reply-outputs")
    runner_log = run_artifact / "runner.log"
    runner = _start_services(context, runner_log)
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
            FPMS_DEMO_CUSTOMER_STAGE_ORDER=",".join(LEGACY_CUSTOMER_STAGE_ORDER),
            FPMS_DEMO_V6_STAGE_ORDER=",".join(CUSTOMER_STAGE_ORDER),
            FPMS_DEMO_V6_TAIL="1",
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
                check=False,
            )
        if completed.returncode != 0:
            raise RuntimeError(f"integrated Playwright failed: rc={completed.returncode}")
        v6_ledger = json.loads((run_artifact / "v6-stages.json").read_text(encoding="utf-8"))
        _write_json(
            run_artifact / "pass-receipt.json",
            {
                "status": "PASS",
                "profile": profile,
                "run_id": run_id,
                "bundle_manifest_sha256": manifest_sha,
                "stage_count": len(v6_ledger.get("stages", [])),
                "network_errors": v6_ledger.get("network_errors"),
                "console_errors": v6_ledger.get("console_errors"),
            },
        )
    finally:
        _stop_process(runner, interrupt=True)
        if run_root.exists():
            if run_root.parent != Path(tempfile.gettempdir()).resolve() or not run_root.name.startswith("fpms-demo-abc-integrated-r"):
                raise RuntimeError(f"refusing unexpected cleanup root: {run_root}")
            _remove_run_root(context)
        _write_json(run_artifact / "cleanup.json", {"run_id": run_id, "run_root_removed": not run_root.exists()})


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.ui_session:
        candidate = abc.candidate_identity()
        bundle_parent = Path(tempfile.mkdtemp(prefix="fpms-integrated-a-bundle-"))
        try:
            bundle, manifest_sha, authority_sha = build_integrated_bundle(bundle_parent)
            _run_ui_session(args, bundle, manifest_sha, authority_sha, candidate)
        finally:
            if bundle_parent.exists():
                shutil.rmtree(bundle_parent)
        return 0
    artifact = args.artifact.resolve()
    if artifact.exists():
        raise RuntimeError(f"evidence path already exists: {artifact}")
    candidate = abc.candidate_identity()
    source = LEGACY_SPEC.read_text(encoding="utf-8")
    validate_spec_source(source)
    static_check = subprocess.run(
        ["node", str(V6_STATIC_CONTRACT)],
        cwd=PLAYWRIGHT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if static_check.returncode != 0:
        raise RuntimeError(static_check.stdout.strip())
    bundle_parent = Path(tempfile.mkdtemp(prefix="fpms-integrated-a-bundle-"))
    try:
        bundle, manifest_sha, authority_sha = resolve_runtime_bundle(args, bundle_parent)
        artifact.mkdir(parents=True)
        _write_json(artifact / "candidate.json", candidate)
        for ordinal in range(1, args.runs + 1):
            _run_one(
                ordinal,
                artifact,
                bundle,
                manifest_sha,
                authority_sha,
                candidate,
                args.headless,
                args.profile,
            )
    finally:
        if bundle_parent.exists():
            shutil.rmtree(bundle_parent)
    _write_json(artifact / "summary.json", build_diagnostic_summary(artifact, args.runs))
    write_checksums(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
