from __future__ import annotations

import importlib.util
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_demo_integrated_a_rehearsal.py"
LEGACY_SPEC = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "playwright_ts"
    / "src"
    / "tests"
    / "demo-integrated-a.live-backend.spec.ts"
)
SPEC = LEGACY_SPEC.with_name("demo-integrated-v6.live-backend.spec.ts")
V6_SPEC = SPEC
V6_STATIC_CONTRACT = LEGACY_SPEC.with_name("demo-integrated-v6-static-contract.mjs")
V6_LIFECYCLE = ROOT / "docs/postdemo/demo-lifecycle-customer-v6.html"
V6_RUNBOOK = ROOT / "docs/postdemo/demo-lifecycle-customer-v6-runbook.md"


def _module():
    assert RUNNER.is_file(), "integrated rehearsal runner is not implemented"
    spec = importlib.util.spec_from_file_location("run_demo_integrated_a_rehearsal", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v6_contract_uses_exact_eleven_customer_stages_and_new_tail():
    module = _module()
    expected = (
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

    assert module.V6_CUSTOMER_STAGES == expected
    assert module.CUSTOMER_STAGE_ORDER == tuple(stage for stage, _label in expected)
    assert module.SPEC == V6_SPEC
    assert V6_SPEC.is_file()
    assert V6_STATIC_CONTRACT.is_file()
    assert V6_LIFECYCLE.is_file()
    assert V6_RUNBOOK.is_file()


def test_v6_contract_artifacts_share_the_same_stage_order_and_fact_boundaries():
    spec = V6_SPEC.read_text(encoding="utf-8")
    static_contract = V6_STATIC_CONTRACT.read_text(encoding="utf-8")
    lifecycle = V6_LIFECYCLE.read_text(encoding="utf-8")
    runbook = V6_RUNBOOK.read_text(encoding="utf-8")

    for stage in range(1, 12):
        ordinal = f"{stage:02d}"
        assert f'data-stage="{ordinal}"' in lifecycle
        assert f"## 阶段 {ordinal}" in runbook
    for token in (
        "候选预览，尚未形成缴费义务",
        "GOV",
        "SERVICE",
        "调整数量",
        "已登记，待官方凭证核验",
        "PARTIALLY_SETTLED",
        "SETTLED",
        "同案双轨费用概览",
    ):
        assert token in spec + lifecycle + runbook
    assert "demo-integrated-a.live-backend.spec" in spec
    assert "test_v6_customer_acceptance_receipts" in Path(__file__).read_text(encoding="utf-8")
    assert "FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR" in RUNNER.read_text(encoding="utf-8")
    assert "Acorn" in static_contract


def test_runner_selects_only_the_integrated_spec_and_supports_one_or_two_runs():
    module = _module()
    assert module.SPEC == SPEC
    assert module.parse_args(
        [
            "--profile",
            "TECHNICAL_REHEARSAL",
            "--artifact",
            "/tmp/integrated-a",
            "--runs",
            "1",
            "--headless",
        ]
    ).runs == 1
    assert module.parse_args(
        [
            "--profile",
            "TECHNICAL_REHEARSAL",
            "--artifact",
            "/tmp/integrated-a",
            "--runs",
            "2",
        ]
    ).runs == 2
    with pytest.raises(SystemExit):
        module.parse_args(
            [
                "--profile",
                "TECHNICAL_REHEARSAL",
                "--artifact",
                "/tmp/integrated-a",
                "--runs",
                "3",
            ]
        )
    with pytest.raises(SystemExit):
        module.parse_args(["--artifact", "/tmp/integrated-a"])


def test_runner_builds_the_integrated_bundle_successor(tmp_path: Path):
    module = _module()
    bundle, manifest_sha, authority_sha = module.build_integrated_bundle(tmp_path)

    assert bundle.is_dir()
    assert len(manifest_sha) == 64
    assert len(authority_sha) == 64
    manifest = (bundle / "manifest.json").read_text(encoding="utf-8")
    assert '"schema_version":"fpms.demo-input-bundle/integrated-a-v2"' in manifest
    assert manifest.count('"classification":"FICTIONAL_DEMO_EVIDENCE"') == 12


def test_customer_profile_requires_exact_external_bundle_contract(tmp_path: Path):
    module = _module()
    args = module.parse_args(
        [
            "--profile",
            "CUSTOMER_DEMO",
            "--artifact",
            str(tmp_path / "artifact"),
        ]
    )

    with pytest.raises(RuntimeError, match="customer bundle arguments"):
        module.resolve_runtime_bundle(args, tmp_path / "synthetic")

    relative = module.parse_args(
        [
            "--profile",
            "CUSTOMER_DEMO",
            "--artifact",
            str(tmp_path / "artifact"),
            "--bundle",
            "relative-bundle",
            "--expected-manifest-sha256",
            "a" * 64,
            "--expected-authority-sha256",
            "b" * 64,
        ]
    )
    with pytest.raises(RuntimeError, match="absolute"):
        module.resolve_runtime_bundle(relative, tmp_path / "synthetic")


def test_customer_profile_rejects_a_complete_synthetic_bundle_with_relabelled_authority(
    tmp_path: Path,
):
    module = _module()
    helpers = runpy.run_path(str(ROOT / "backend/tests/test_demo_abc_runtime_bundle.py"))
    bundle, manifest, _digest = helpers["_valid_v6_bundle"](tmp_path / "input")
    manifest["authority_classification"] = "CUSTOMER_AUTHORIZED"
    manifest_sha = helpers["_write_manifest"](bundle, manifest)
    authority_sha = helpers["_authority_digest"](bundle)
    args = module.parse_args(
        [
            "--profile",
            "CUSTOMER_DEMO",
            "--artifact",
            str(tmp_path / "artifact"),
            "--bundle",
            str(bundle.resolve()),
            "--expected-manifest-sha256",
            manifest_sha,
            "--expected-authority-sha256",
            authority_sha,
        ]
    )

    with pytest.raises(RuntimeError, match="customer authorization"):
        module.resolve_runtime_bundle(args, tmp_path / "synthetic")


def test_invalid_bundle_preflight_does_not_create_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = _module()
    artifact = tmp_path / "artifact"
    monkeypatch.setattr(module.abc, "candidate_identity", lambda: {"commit": "candidate"})
    monkeypatch.setattr(module, "validate_spec_source", lambda _source: None)

    with pytest.raises(RuntimeError, match="customer bundle arguments"):
        module.main(
            [
                "--profile",
                "CUSTOMER_DEMO",
                "--artifact",
                str(artifact),
                "--runs",
                "1",
                "--headless",
            ]
        )

    assert not artifact.exists()


@pytest.mark.parametrize("existing_name", ["root", "database", "wal", "shm"])
def test_fresh_run_preflight_rejects_every_existing_run_identity(
    tmp_path: Path, existing_name: str
):
    module = _module()
    run_root = tmp_path / "fresh-run"
    targets = {
        "root": run_root,
        "database": Path(f"{run_root}.db"),
        "wal": Path(f"{run_root}.db-wal"),
        "shm": Path(f"{run_root}.db-shm"),
    }
    target = targets[existing_name]
    if existing_name == "root":
        target.mkdir()
    else:
        target.write_text("occupied", encoding="utf-8")

    with pytest.raises(RuntimeError, match="already exists"):
        module.assert_fresh_run_paths(run_root, Path(f"{run_root}.db"))


def test_run_record_contains_only_recovery_binding_fields(tmp_path: Path):
    module = _module()
    database = (tmp_path / "run" / "fpms-demo.db").resolve()

    record = module.build_run_record(
        run_id="integrated-r1-abcdef",
        database_path=database,
        manifest_sha256="a" * 64,
        created_at="2026-08-23T20:00:00+08:00",
    )

    assert record == {
        "run_id": "integrated-r1-abcdef",
        "database_path": str(database),
        "bundle_manifest_sha256": "a" * 64,
        "created_at": "2026-08-23T20:00:00+08:00",
    }


def test_runner_uses_permission_safe_run_root_cleanup():
    source = RUNNER.read_text(encoding="utf-8")

    assert "abc.remove_run_root(run_root, run_id)" in source
    assert "shutil.rmtree(run_root)" not in source


def test_integrated_spec_login_uses_current_visible_form_labels():
    source = LEGACY_SPEC.read_text(encoding="utf-8")

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


def test_runner_binds_the_approved_realistic_customer_scenario():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8")

    assert module.REHEARSAL_SCENARIO == {
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
    for key in (
        "FPMS_DEMO_CUSTOMER_NAME",
        "FPMS_DEMO_CUSTOMER_CODE_PREFIX",
        "FPMS_DEMO_CONTACT_NAME",
        "FPMS_DEMO_CONTACT_TITLE",
        "FPMS_DEMO_CONTACT_EMAIL",
        "FPMS_DEMO_CASE_NO_PREFIX",
        "FPMS_DEMO_CASE_TITLE",
        "FPMS_DEMO_SERVICE_ITEM_NAME",
        "FPMS_DEMO_BILL_NO_PREFIX",
        "FPMS_DEMO_PAYMENT_NO_PREFIX",
        "FPMS_DEMO_BANK_REF_PREFIX",
    ):
        assert key in RUNNER.read_text(encoding="utf-8")
        assert key in source


def test_runner_binds_the_customer_stage_order():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8")

    assert module.LEGACY_CUSTOMER_STAGE_ORDER == tuple(f"{index:02d}" for index in range(1, 10))
    assert module.CUSTOMER_STAGE_ORDER == tuple(f"{index:02d}" for index in range(1, 12))
    assert "FPMS_DEMO_CUSTOMER_STAGE_ORDER" in RUNNER.read_text(encoding="utf-8")
    assert "FPMS_DEMO_CUSTOMER_STAGE_ORDER" in source


def test_runner_materializes_natural_oa_reply_output_titles(tmp_path: Path):
    module = _module()

    rows = module.materialize_oa_reply_outputs(tmp_path / "oa-outputs")

    assert [row["title_zh_cn"] for row in rows] == [
        "第一次审查意见答复意见陈述书（Word）",
        "第一次审查意见答复意见陈述书（PDF）",
        "第一次审查意见答复修改后权利要求书",
        "第二次审查意见答复意见陈述书（Word）",
        "第二次审查意见答复意见陈述书（PDF）",
        "第二次审查意见答复修改后权利要求书",
    ]
    assert [Path(row["path"]).name for row in rows] == [
        "第一次审查意见答复_意见陈述书.docx",
        "第一次审查意见答复_意见陈述书.pdf",
        "第一次审查意见答复_修改后权利要求书.docx",
        "第二次审查意见答复_意见陈述书.docx",
        "第二次审查意见答复_意见陈述书.pdf",
        "第二次审查意见答复_修改后权利要求书.docx",
    ]


def test_runner_accepts_only_the_frozen_public_lifecycle_api_allowlist():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8")
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
    source = LEGACY_SPEC.read_text(encoding="utf-8") + "\n" + shortcut
    with pytest.raises(RuntimeError, match="visible UI"):
        module.validate_spec_source(source)


def test_runner_rejects_imported_local_helper_evasion():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8") + '\n  import { uploadAttachment } from "./helper"'
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
    source = LEGACY_SPEC.read_text(encoding="utf-8") + "\n" + shortcut
    with pytest.raises(RuntimeError):
        module.validate_spec_source(source)


def test_runner_rejects_public_api_allowlist_drift_to_evidence_write():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8").replace(
        "/documents/{document_id}/lifecycle/acceptance-notice",
        "/documents/{document_id}/attachments",
        1,
    )
    with pytest.raises(RuntimeError, match="public lifecycle API allowlist"):
        module.validate_spec_source(source)


def test_runner_accepts_the_frozen_driver_lifecycle_wrapper_shape():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8").replace(
        "  async preflight(): Promise<Json>",
        "  async expectedWrapper(): Promise<Json> { return this.publicLifecycleApi('RESOLVE_FILING', { case_id: 'dynamic' }) }\n"
        "  async preflight(): Promise<Json>",
        1,
    )
    module.validate_spec_source(source)


def test_runner_rejects_lifecycle_wrapper_calls_on_an_alternate_receiver():
    module = _module()
    source = LEGACY_SPEC.read_text(encoding="utf-8").replace(
        "  async preflight(): Promise<Json>",
        "  async invalidWrapper(): Promise<Json> { return journey.publicLifecycleApi('RESOLVE_FILING', { case_id: 'dynamic' }) }\n"
        "  async preflight(): Promise<Json>",
        1,
    )
    with pytest.raises(RuntimeError, match="visible UI"):
        module.validate_spec_source(source)


def test_integrated_spec_closes_ia18_with_authoritative_summary_artifacts():
    source = LEGACY_SPEC.read_text(encoding="utf-8")

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
    v6_stages = [
        {"stage": f"{index:02d}", "label": f"stage-{index}"}
        for index in range(1, 12)
    ]
    v6_stages[-1].update({"bill_status": "SETTLED", "bill_balance": "0.00"})
    (run / "v6-stages.json").write_text(
        json.dumps(
            {"stages": v6_stages, "network_errors": [], "console_errors": []}
        ),
        encoding="utf-8",
    )
    (run / "run.json").write_text(
        json.dumps(
            {
                "run_id": f"integrated-r{ordinal}-unique",
                "database_path": f"/tmp/fpms-demo-{ordinal}.db",
                "bundle_manifest_sha256": "a" * 64,
                "created_at": "2026-08-25T00:00:00+08:00",
            }
        ),
        encoding="utf-8",
    )
    (run / "pass-receipt.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "profile": "CUSTOMER_DEMO",
                "stage_count": 11,
            }
        ),
        encoding="utf-8",
    )
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

    assert summary["status"] == "TECHNICAL_REHEARSAL_PASS"
    assert summary["runs"] == 2
    assert summary["checkpoint_counts"] == [19, 19]
    assert summary["v6_stage_counts"] == [11, 11]
    assert summary["evidence_binding_counts"] == [12, 12]
    assert summary["business_identity_sets_disjoint"] is True


def test_v6_customer_acceptance_receipts(tmp_path: Path, monkeypatch):
    module = _module()
    monkeypatch.delenv("FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR", raising=False)
    with pytest.raises(RuntimeError, match="FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR"):
        module.validate_v6_customer_acceptance_receipts()

    _write_fake_run(tmp_path, 1)
    _write_fake_run(tmp_path, 2)
    monkeypatch.setenv("FPMS_DEMO_V6_CUSTOMER_EVIDENCE_DIR", str(tmp_path))
    result = module.validate_v6_customer_acceptance_receipts()

    assert result["status"] == "CUSTOMER_DEMO_PASS"
    assert result["runs"] == 2
    assert len(set(result["run_ids"])) == 2
    assert len(set(result["database_paths"])) == 2
    assert result["bundle_manifest_sha256"] == "a" * 64
