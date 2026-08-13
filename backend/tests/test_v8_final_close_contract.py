from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"
REPORT_PATH = ROOT / "docs/product/v8/final-close-report.json"
STORY_PATH = ROOT / "docs/product/v8/stories/V8-FINAL-CLOSE.md"
RECEIPT_PATH = ROOT / "docs/product/v8/reviews/V8-FINAL-CLOSE-CURRENT-ADOPTION.md"
LOG_ROOT = Path("/tmp/fpms-v8-final-close-20260813")
ROW283_ID = "FPMS-V8-FINAL-CLOSE-20260712-01"
STORY_ID = "V8-FINAL-CLOSE-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-FINAL-CLOSE-CURRENT-ADOPTION.md"
CANDIDATE_PATHS = [
    "tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md",
    "backend/tests/test_v8_final_close_contract.py",
    "scripts/run_v8_paylist_boundary_live_isolated.py",
    "docs/product/v8/final-close-report.json",
    "docs/product/v8/stories/V8-FINAL-CLOSE.md",
]
MILESTONE_STORIES = {
    "foundation": {
        "story_id": "V8-FOUNDATION-CLOSE-CURRENT-ADOPTION",
        "story_path": "docs/product/v8/stories/V8-FOUNDATION-CLOSE-CURRENT-ADOPTION.md",
        "review_path": "docs/product/v8/reviews/V8-FOUNDATION-CLOSE-CURRENT-ADOPTION.md",
    },
    "full": {
        "story_id": "V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION",
        "story_path": "docs/product/v8/stories/V8-FULL-CAPABILITY-MANIFEST-CLOSE.md",
        "review_path": "docs/product/v8/reviews/V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION.md",
    },
}
LANE_COMMANDS = {
    "clean_sqlite_upgrade_seed": (
        "tmp=$(mktemp -d); trap 'rm -rf \"$tmp\"' EXIT; cd backend && "
        'FPMS_ENV=test DATABASE_URL="sqlite:///$tmp/final.db" '
        'STORAGE_DIR="$tmp/storage" .venv/bin/alembic upgrade head && '
        'FPMS_ENV=test DATABASE_URL="sqlite:///$tmp/final.db" '
        'STORAGE_DIR="$tmp/storage" .venv/bin/python scripts/seed_dev.py'
    ),
    "backend_ruff": "cd backend && .venv/bin/ruff check .",
    "backend_pytest": "cd backend && .venv/bin/pytest -q",
    "frontend_quality": "cd frontend && npm run lint && npm run typecheck && npm run build",
    "lifecycle_real_e2e": "python3 scripts/run_v8_lifecycle_overlay_live_isolated.py",
    "paylist_real_e2e": "python3 scripts/run_v8_paylist_boundary_live_isolated.py",
    "workbook_real_e2e": (
        "cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test "
        "src/tests/v8-official-workbook-live.spec.ts --workers=1"
    ),
}
SENSITIVE_RULES = {
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "live_credential": re.compile(
        r"(?i)(?:password|passwd|secret|api[_-]?key|access[_-]?token)"
        r"\s*[:=]\s*['\"]?(?!admin123\b|secret123\b|not-used\b|ChangeMe123!\b)"
        r"[^\s'\"]{8,}"
    ),
    "prc_identity": re.compile(r"(?<!\d)[1-9]\d{5}(?:19|20)\d{2}[01]\d[0-3]\d\d{3}[0-9Xx](?!\d)"),
    "prc_mobile": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
}


def _git_text(revision: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _git_json(revision: str, path: str) -> dict:
    return json.loads(_git_text(revision, path))


def _is_ancestor(commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def _load_checker():
    path = ROOT / "scripts/v8_lean_coverage_check.py"
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _story_map(ledger: dict) -> dict[str, dict]:
    return {story["story_id"]: story for story in ledger["stories"]}


def _scan(path: Path) -> dict[str, int]:
    text = path.read_text(errors="replace")
    findings = {name: len(pattern.findall(text)) for name, pattern in SENSITIVE_RULES.items()}
    return {name: count for name, count in findings.items() if count}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ledger_patch_sha256() -> str:
    patch = subprocess.run(
        ["git", "diff", "--binary", "--", "docs/product/v8/coverage-ledger.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert patch
    return hashlib.sha256(patch).hexdigest()


def _assert_current_story(story: dict) -> None:
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["paths"] == CANDIDATE_PATHS
    assert story["review_ref"] == story["verification_ref"] == REVIEW_REF
    assert story["commits"] and _is_ancestor(story["commits"][-1])
    assert re.fullmatch(r"[0-9a-f]{64}", story["tree_sha256"])
    assert (
        _load_checker().compute_tree_fingerprint(ROOT, story["commits"][-1], CANDIDATE_PATHS)
        == story["tree_sha256"]
    )


def test_report_records_the_exact_successful_final_matrix() -> None:
    report = json.loads(REPORT_PATH.read_text())
    assert report["schema_version"] == "v8-final-close-report-v1"
    assert report["expensive_matrix_runs"] == 1
    assert report["configuration_residual"] == {
        "inputs": {
            "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
            "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED",
        },
        "source_decisions": {
            "DG-PAYMENT-WORKBOOK:GLOBAL": "PENDING",
            "DG-SERVICE-RATE-VERSION:GLOBAL": "PENDING",
        },
        "production_failure": "409 / NO WRITE",
        "test_only_isolated": True,
        "production_activation_claimed": False,
    }
    assert set(report["lanes"]) == set(LANE_COMMANDS)
    for lane_id, command in LANE_COMMANDS.items():
        lane = report["lanes"][lane_id]
        assert lane["command"] == command
        assert lane["status"] == "PASS"
        assert lane["return_code"] == 0
        assert isinstance(lane["observed_summary"], str) and lane["observed_summary"]
        assert isinstance(lane["warnings"], list)
        assert re.fullmatch(r"[0-9a-f]{64}", lane["log_sha256"])
        log_path = LOG_ROOT / f"{lane_id}.log"
        if log_path.is_file():
            assert _sha256(log_path) == lane["log_sha256"]
            assert _scan(log_path) == {}, f"sensitive finding: {lane_id}"
        else:
            assert RECEIPT_PATH.is_file()

    scan_paths = [REPORT_PATH, STORY_PATH]
    if RECEIPT_PATH.exists():
        scan_paths.append(RECEIPT_PATH)
    for path in scan_paths:
        assert _scan(path) == {}, f"sensitive finding: {path.relative_to(ROOT)}"


def test_foundation_full_and_rows_1_to_282_are_current() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    stories = _story_map(ledger)
    assert all(
        row["disposition"] in {"CURRENT_VERIFIED", "SUPERSEDED_BY_STORY"}
        for row in ledger["rows"][:282]
    )
    for milestone in MILESTONE_STORIES.values():
        story = stories[milestone["story_id"]]
        assert story["status"] == "CURRENT_VERIFIED"
        assert story["commits"] and _is_ancestor(story["commits"][-1])
        assert milestone["story_path"] in story["paths"]
        assert story["review_ref"] == milestone["review_path"]
        assert story["verification_ref"] == milestone["review_path"]
        assert (ROOT / milestone["story_path"]).is_file()
        assert (ROOT / milestone["review_path"]).is_file()


def test_row283_state_matches_candidate_review_or_adoption() -> None:
    head_ledger = _git_json("HEAD", "docs/product/v8/coverage-ledger.json")
    worktree_ledger = json.loads(LEDGER_PATH.read_text())
    head_row = head_ledger["rows"][282]
    worktree_row = worktree_ledger["rows"][282]
    worktree_story = _story_map(worktree_ledger).get(STORY_ID)

    if head_row["disposition"] == "PENDING":
        assert worktree_row["disposition"] in {"PENDING", "CURRENT_VERIFIED"}
        if worktree_row["disposition"] == "PENDING":
            assert worktree_story is None
            assert not RECEIPT_PATH.exists()
        else:
            assert worktree_story is not None
            assert worktree_row["story_id"] == STORY_ID
            _assert_current_story(worktree_story)
            if RECEIPT_PATH.exists():
                receipt = RECEIPT_PATH.read_text()
                assert worktree_story["commits"][-1] in receipt
                assert worktree_story["tree_sha256"] in receipt
                assert _ledger_patch_sha256() in receipt
                assert "P0/P1/P2: `0/0/0`" in receipt
        return

    assert head_row == worktree_row
    assert head_row == {
        "catalog_id": ROW283_ID,
        "phase": "deferred",
        "disposition": "CURRENT_VERIFIED",
        "story_id": STORY_ID,
        "successor_story_id": None,
        "blocker": None,
    }
    assert worktree_story is not None
    _assert_current_story(worktree_story)
    assert RECEIPT_PATH.is_file()
    receipt = RECEIPT_PATH.read_text()
    candidate = worktree_story["commits"][-1]
    assert candidate in receipt
    assert worktree_story["tree_sha256"] in receipt
    assert re.search(r"Ledger patch SHA-256: `[0-9a-f]{64}`", receipt)
    assert "P0/P1/P2: `0/0/0`" in receipt
