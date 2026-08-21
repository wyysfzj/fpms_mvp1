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


def test_runner_accepts_only_the_frozen_public_lifecycle_api_allowlist():
    module = _module()
    source = SPEC.read_text(encoding="utf-8")
    module.validate_spec_source(source)
    assert module.PUBLIC_LIFECYCLE_API_ALLOWLIST == {
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
        "GRANT_REPLACEMENT": (
            "POST",
            "/grant-fee-tasks/{task_id}/replacement-notice",
        ),
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
        "RECORD_OA_NOTICE": (
            "POST",
            "/documents/{document_id}/lifecycle/oa-notice",
        ),
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


@pytest.mark.parametrize(
    "shortcut",
    [
        'page.request.post("/documents/x/attachments", { data: payload })',
        "request.fetch('/documents/x/attachments', { method: 'POST' })",
        'fetch("/documents/evidence-versions/x/review", { method: "POST" })',
        'axios.post("/documents/evidence-versions/x/review", payload)',
        "const transport = page.request; transport.post(endpoint, payload)",
        "const endpoint = '/attach' + 'ments'; fetch(endpoint, payload)",
        "const transport = page['request']; transport.post(endpoint, payload)",
        "const transport = page['req'+'uest']; const endpoint = '/attach'+'ments'; transport['po'+'st'](endpoint, payload)",
        "page.addInitScript(() => globalThis['fet'+'ch']('/documents/x/attachments'))",
        "apiRequest['fet'+'ch']('/documents/x/attachments')",
        "Reflect.get(page, 'req'+'uest')['post']('/documents/x/attachments')",
        "globalThis.fetch('/documents/x/attachments')",
        "const hiddenFetch = apiRequest['fe' + 'tch'].bind(apiRequest); hiddenFetch('/documents/x/attachments', { method: 'POST' })",
        "const hiddenRequest = Reflect.get(page, ['req', 'uest'].join('')); const hiddenPost = Reflect.get(hiddenRequest, 'post'); Reflect.apply(hiddenPost, hiddenRequest, ['/documents/x/attachments'])",
        "const { fetch: hiddenFetch } = apiRequest; hiddenFetch('/documents/x/attachments', { method: 'POST' })",
        "const transport = apiRequest; const method = ['fe', 'tch'].join(''); transport[method]('/documents/x/attachments', { method: 'POST' })",
        "const transportAlias = request; const { fetch: hiddenSend } = transportAlias; await hiddenSend('/documents/fake/attachments', { method: 'POST' })",
        "const leak = ({ fetch: hiddenSend }: APIRequestContext) => hiddenSend('/documents/fake/attachments', { method: 'POST' }); await leak(request)",
        "const descriptor = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(request), 'fetch')!; const hiddenSend = descriptor.value.bind(request); await hiddenSend('/documents/fake/attachments', { method: 'POST' })",
    ],
)
def test_runner_rejects_direct_evidence_shortcut_spellings(shortcut: str):
    module = _module()
    source = SPEC.read_text(encoding="utf-8") + "\n" + shortcut
    with pytest.raises(RuntimeError, match="visible UI"):
        module.validate_spec_source(source)


def test_runner_rejects_imported_local_helper_evasion():
    module = _module()
    source = SPEC.read_text(encoding="utf-8") + '\n  import { uploadAttachment } from "./helper"'
    with pytest.raises(RuntimeError, match="imports are not allowlisted"):
        module.validate_spec_source(source)


@pytest.mark.parametrize(
    "shortcut",
    [
        'import("./helper").then((m) => m.uploadAttachment())',
        'import "./side-effect-helper"',
    ],
)
def test_runner_rejects_dynamic_or_side_effect_import(shortcut: str):
    module = _module()
    source = SPEC.read_text(encoding="utf-8") + "\n" + shortcut
    with pytest.raises(RuntimeError):
        module.validate_spec_source(source)


def test_runner_rejects_public_api_allowlist_drift_to_evidence_write():
    module = _module()
    source = SPEC.read_text(encoding="utf-8").replace(
        "/documents/{document_id}/lifecycle/acceptance-notice",
        "/documents/{document_id}/attachments",
        1,
    )
    with pytest.raises(RuntimeError, match="public lifecycle API allowlist"):
        module.validate_spec_source(source)
