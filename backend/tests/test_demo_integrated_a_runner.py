from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_demo_integrated_a_rehearsal.py"
SPEC = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "playwright_ts"
    / "src"
    / "tests"
    / "demo-integrated-a.live-backend.spec.ts"
)


def _module():
    assert RUNNER.is_file(), "integrated rehearsal runner is not implemented"
    spec = importlib.util.spec_from_file_location("run_demo_integrated_a_rehearsal", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_selects_only_the_integrated_spec_and_supports_one_or_two_runs():
    module = _module()
    assert module.SPEC == SPEC
    assert module.parse_args(["--artifact", "/tmp/integrated-a", "--runs", "1", "--headless"]).runs == 1
    assert module.parse_args(["--artifact", "/tmp/integrated-a", "--runs", "2"]).runs == 2
    with pytest.raises(SystemExit):
        module.parse_args(["--artifact", "/tmp/integrated-a", "--runs", "3"])


def test_runner_fails_at_the_missing_integrated_bundle_builder(tmp_path: Path):
    module = _module()
    with pytest.raises(RuntimeError, match="integrated-a-v1 bundle builder is unavailable"):
        module.build_integrated_bundle(tmp_path)


def test_runner_forbids_mock_db_enrichment_and_direct_evidence_shortcuts():
    module = _module()
    source = SPEC.read_text(encoding="utf-8")
    module.validate_spec_source(source)


@pytest.mark.parametrize(
    "shortcut",
    [
        'page.request.post("/documents/x/attachments", { data: payload })',
        "request.fetch('/documents/x/attachments', { method: 'POST' })",
        'fetch("/documents/evidence-versions/x/review", { method: "POST" })',
        'axios.post("/documents/evidence-versions/x/review", payload)',
    ],
)
def test_runner_rejects_direct_evidence_shortcut_spellings(shortcut: str):
    module = _module()
    source = SPEC.read_text(encoding="utf-8") + "\n" + shortcut
    with pytest.raises(RuntimeError, match="direct evidence write shortcut"):
        module.validate_spec_source(source)


def test_runner_rejects_imported_local_helper_evasion():
    module = _module()
    source = SPEC.read_text(encoding="utf-8") + '\nimport { uploadAttachment } from "./helper"'
    with pytest.raises(RuntimeError, match="imports are not allowlisted"):
        module.validate_spec_source(source)
