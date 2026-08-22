from __future__ import annotations

import importlib.util
import json
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


def test_runner_builds_the_integrated_bundle_successor(tmp_path: Path):
    module = _module()
    bundle, manifest_sha, authority_sha = module.build_integrated_bundle(tmp_path)

    assert bundle.is_dir()
    assert len(manifest_sha) == 64
    assert len(authority_sha) == 64
    manifest = (bundle / "manifest.json").read_text(encoding="utf-8")
    assert '"schema_version":"fpms.demo-input-bundle/integrated-a-v1"' in manifest
    assert manifest.count('"classification":"FICTIONAL_DEMO_EVIDENCE"') == 12


def test_runner_uses_permission_safe_run_root_cleanup():
    source = RUNNER.read_text(encoding="utf-8")

    assert "abc.remove_run_root(run_root, run_id)" in source
    assert "shutil.rmtree(run_root)" not in source


def test_integrated_spec_login_uses_current_visible_form_labels():
    source = SPEC.read_text(encoding="utf-8")

    assert "getByPlaceholder('用户名')" not in source
    assert "getByPlaceholder('密码')" not in source
    assert 'page.locator(\'.el-form-item:has-text("用户名") input\').fill(username)' in source
    assert 'page.locator(\'.el-form-item:has-text("密码") input\').fill(password)' in source
    assert "page.getByRole('button', { name: '登 录' }).click()" in source


def test_runner_binds_ia00_expectations_to_the_integrated_manifest():
    source = RUNNER.read_text(encoding="utf-8")

    for key in (
        "FPMS_DEMO_EXPECTED_BUNDLE_ID",
        "FPMS_DEMO_EXPECTED_BUNDLE_VERSION",
        "FPMS_DEMO_EXPECTED_TEMPLATE_CODE",
        "FPMS_DEMO_EXPECTED_TEMPLATE_SHA256",
        "FPMS_DEMO_EXPECTED_RATE_ITEM_CODE",
        "FPMS_DEMO_EXPECTED_RATE_SOURCE_REF",
        "FPMS_DEMO_EXPECTED_RATE_SOURCE_VERSION",
        "FPMS_DEMO_EXPECTED_RATE_SOURCE_SHA256",
        "FPMS_DEMO_EXPECTED_DISCLAIMER_ZH_CN",
    ):
        assert key in source
    assert '(bundle / "manifest.json").read_text' in source


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
        "const uiAlias = page as any; const hiddenTransport = uiAlias[['req', 'uest'].join('')]; const hiddenSend = hiddenTransport[['po', 'st'].join('')]; await hiddenSend('/documents/fake/attachments', {})",
        "const hiddenTransport = (journey as any)[['api', 'Request'].join('')]; const hiddenSend = hiddenTransport[['fe', 'tch'].join('')]; await hiddenSend('/documents/fake/attachments', { method: 'POST' })",
        'await page.addScriptTag({ content: "void globalThis[\'fe\' + \'tch\'](\'/api/v1/documents/fake/attachments\',{method:\'POST\'})" })',
        'await page.setContent("<script>void globalThis[\'fe\' + \'tch\'](\'/api/v1/documents/fake/attachments\',{method:\'POST\'})</script>")',
        "await page.goto('javascript:void globalThis.fetch(\'/api/v1/documents/fake/attachments\')')",
        "await page.goto('data:text/html,<script>fetch(\'/api/v1/documents/fake/attachments\')</script>')",
        "await writeFile('../../frontend/direct-api.html', `<script>void globalThis['fe' + 'tch']('${apiBase}/documents/fake/attachments',{method:'POST',headers:{Authorization:'Bearer ${operatorToken}'}})</script>`); await page.goto(`${baseUrl}/direct-api.html`)",
        "await page.waitForResponse(async (response) => { await writeFile('../../frontend/direct-api.html', '<script>malicious()</script>'); return response.status() === 200 })",
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


def test_runner_accepts_the_frozen_driver_lifecycle_wrapper_shape():
    module = _module()
    source = SPEC.read_text(encoding="utf-8").replace(
        "  async preflight(): Promise<Json>",
        "  async expectedWrapper(): Promise<Json> { return this.publicLifecycleApi('RESOLVE_FILING', { case_id: 'dynamic' }) }\n"
        "  async preflight(): Promise<Json>",
        1,
    )
    module.validate_spec_source(source)


def test_runner_rejects_lifecycle_wrapper_calls_on_an_alternate_receiver():
    module = _module()
    source = SPEC.read_text(encoding="utf-8").replace(
        "  async preflight(): Promise<Json>",
        "  async invalidWrapper(): Promise<Json> { return journey.publicLifecycleApi('RESOLVE_FILING', { case_id: 'dynamic' }) }\n"
        "  async preflight(): Promise<Json>",
        1,
    )
    with pytest.raises(RuntimeError, match="visible UI"):
        module.validate_spec_source(source)


def test_integrated_spec_closes_ia18_with_authoritative_summary_artifacts():
    source = SPEC.read_text(encoding="utf-8")

    assert "if (this.summaryReads > 1) return this.red('IA-18')" not in source
    assert "checkpoints_passed: checkpointContract.length" in source
    assert "task0Checkpoints.push({ checkpoint: 'IA-00', result: snapshot })" in source
    assert "checkpoints: [...task0Checkpoints, ...task5Checkpoints" in source
    assert "'task9-checkpoints.json'" in source
    assert "'integrated-final.png'" in source


def _write_fake_run(root: Path, ordinal: int) -> None:
    run = root / f"run{ordinal}"
    run.mkdir(parents=True)
    checkpoints = [
        {"checkpoint": f"IA-{index:02d}", "result": {}}
        for index in range(19)
    ]
    identities = {
        "client_id": f"client-{ordinal}",
        "contact_id": f"contact-{ordinal}",
        "case_id": f"case-{ordinal}",
        "package_id": f"package-{ordinal}",
        "draft_id": f"draft-{ordinal}",
        "bill_id": f"bill-{ordinal}",
        "payment_id": f"payment-{ordinal}",
        "payment_line_id": f"line-{ordinal}",
        "offset_id": f"offset-{ordinal}",
    }
    checkpoints[1]["result"] = {
        "client_id": identities["client_id"],
        "contact_id": identities["contact_id"],
    }
    checkpoints[2]["result"] = {"case_id": identities["case_id"]}
    checkpoints[4]["result"] = {"package_id": identities["package_id"]}
    checkpoints[13]["result"] = {"draft_id": identities["draft_id"]}
    checkpoints[14]["result"] = {"bill_id": identities["bill_id"]}
    checkpoints[15]["result"] = {
        "payment_id": identities["payment_id"],
        "payment_line_id": identities["payment_line_id"],
    }
    checkpoints[16]["result"] = {"offset_id": identities["offset_id"]}
    checkpoints[18]["result"] = {
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
    (run / "task9-checkpoints.json").write_text(
        json.dumps({"checkpoints": checkpoints, "evidence_bindings": [{}] * 12}),
        encoding="utf-8",
    )
    (run / "evidence-role-map.json").write_text(json.dumps([{}] * 12), encoding="utf-8")
    (run / "integrated-final.png").write_bytes(b"png")
    (run / "cleanup.json").write_text(
        json.dumps({"run_id": f"integrated-r{ordinal}-unique", "run_root_removed": True}),
        encoding="utf-8",
    )
    (run / "command.json").write_text(
        json.dumps({"redacted": True, "environment_keys": ["FPMS_DEMO_RUN_ID"]}),
        encoding="utf-8",
    )


def test_runner_accepts_only_two_clean_runs_with_disjoint_business_identities(tmp_path: Path):
    module = _module()
    _write_fake_run(tmp_path, 1)
    _write_fake_run(tmp_path, 2)

    summary = module.build_diagnostic_summary(tmp_path, 2)

    assert summary["status"] == "DIAGNOSTIC_PASS"
    assert summary["runs"] == 2
    assert summary["checkpoint_counts"] == [19, 19]
    assert summary["evidence_binding_counts"] == [12, 12]
    assert summary["business_identity_sets_disjoint"] is True
