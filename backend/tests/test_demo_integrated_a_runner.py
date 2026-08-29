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
V6_COLLEAGUE_GUIDE = ROOT / "docs/postdemo/demo-v6-colleague-clone-start-guide.md"
V6_HANDOFF = ROOT / "docs/postdemo/demo-v6-clone-deploy-handoff.md"
V6_SEED_GUIDE = ROOT / "docs/postdemo/demo-lifecycle-customer-v6-seed-data.md"
V6_UI_CONTRACT = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json"
)
V6_DOCUMENT_CHECKER = ROOT / "scripts/check_customer_demo_lifecycle_v6.py"


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


def test_v6_colleague_docs_and_checker_freeze_current_customer_projection_contract():
    document_paths = (
        V6_COLLEAGUE_GUIDE,
        V6_HANDOFF,
        V6_RUNBOOK,
        V6_SEED_GUIDE,
        V6_LIFECYCLE,
    )
    for path in (*document_paths, V6_UI_CONTRACT, V6_DOCUMENT_CHECKER):
        assert path.is_file(), f"missing V6 document contract artifact: {path}"

    documents = {path.name: path.read_text(encoding="utf-8") for path in document_paths}
    combined = "\n".join(documents.values())
    guide = documents[V6_COLLEAGUE_GUIDE.name]
    handoff = documents[V6_HANDOFF.name]
    runbook = documents[V6_RUNBOOK.name]
    seed_guide = documents[V6_SEED_GUIDE.name]
    lifecycle = documents[V6_LIFECYCLE.name]
    checker = V6_DOCUMENT_CHECKER.read_text(encoding="utf-8")
    contract = json.loads(V6_UI_CONTRACT.read_text(encoding="utf-8"))

    tag = "demo-v6-customer-20260829-r2"
    assert tag in guide
    assert tag in handoff
    for document in (guide, handoff):
        assert "十二份上传文件的附件角色" in document
        assert "先选择文件" in document
        assert "再选择附件角色" in document
        assert "最后确认上传" in document
    upload_role_rows = {
        "FILING_FINAL_SUBMISSION": "合并PDF",
        "FILING_RECEIPT": "电子申请回执",
        "ACCEPTANCE_NOTICE": "官方通知书PDF",
        "PRELIMINARY_EXAMINATION_SOURCE": "官方通知书PDF",
        "PUBLICATION_NOTICE": "官方通知书PDF",
        "SUBSTANTIVE_EXAMINATION_SOURCE": "官方通知书PDF",
        "OA_NOTICE_1": "官方通知书PDF",
        "OA_RECEIPT_1": "电子申请回执",
        "OA_NOTICE_2": "官方通知书PDF",
        "OA_RECEIPT_2": "电子申请回执",
        "GRANT_NOTICE_ORIGINAL": "官方通知书PDF",
        "GRANT_NOTICE_REPLACEMENT": "官方通知书PDF",
    }
    for evidence_key, attachment_role in upload_role_rows.items():
        assert f"`{evidence_key}`" in runbook
        assert any(
            f"`{evidence_key}`" in line and f"| {attachment_role} |" in line
            for line in runbook.splitlines()
        )
    for stale in (
        "demo-v6-customer-20260829-r1",
        "90d9c560cd2d8687fddb038dcd8c3f51cd8af72b",
        "codex/demo-v6-ui-parity-candidate-20260826",
    ):
        assert stale not in combined
        assert stale in checker

    for required_path in (
        "demo-v6-colleague-clone-start-guide.md",
        "demo-v6-clone-deploy-handoff.md",
        "demo-lifecycle-customer-v6-runbook.md",
        "demo-lifecycle-customer-v6-seed-data.md",
        "demo-lifecycle-customer-v6.html",
        "demo_v6_ui_parity_v1.json",
    ):
        assert required_path in checker

    for token in (
        "客户名称面包屑",
        "第5阶段/5 · 授权登记",
        "结构化文书字段",
        "历史首次申请递交材料核验",
        "预览官费",
        "确认官费",
        "现在是什么状态",
        "最近发生了什么",
        "下一步是什么",
        "查看完整历史",
        "审计信息",
    ):
        assert token in runbook
    assert "技术标识、摘要和原始状态默认隐藏" in lifecycle
    assert "upload-manifest.json" in guide + handoff + seed_guide
    assert "2026-09-30" in seed_guide
    for token in ("--strict-ui", "--runs 1", "--headless"):
        assert token in handoff
    for token in ("HUMAN：待完成", "CODEX：待完成", "Comparator：待完成"):
        assert token in handoff

    assert len(contract["stages"]) == 11
    assert sum(len(stage["inputs"]) for stage in contract["stages"]) == 103
    assert sum(len(stage["outputs"]) for stage in contract["stages"]) == 30


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


def test_ui_upload_manifest_materializes_frozen_evidence_inside_artifact(
    tmp_path: Path,
):
    module = _module()
    helpers = runpy.run_path(str(ROOT / "backend/tests/test_demo_abc_runtime_bundle.py"))
    bundle, manifest, _manifest_sha = helpers["_valid_v6_bundle"](tmp_path / "bundle")
    artifact = (tmp_path / "external-artifact").resolve()
    artifact.mkdir()

    module.materialize_ui_upload_manifest(bundle, artifact)

    upload_root = artifact / "upload-files"
    upload_manifest = json.loads(
        (artifact / "upload-manifest.json").read_text(encoding="utf-8")
    )
    assert set(upload_manifest) == {"schema_id", "files"}
    assert upload_manifest["schema_id"] == "fpms.demo-v6-upload-manifest/v1"
    assert len(upload_manifest["files"]) == 12
    for ordinal, (source, copied) in enumerate(
        zip(manifest["evidence"], upload_manifest["files"], strict=True),
        start=1,
    ):
        copied_path = Path(copied["path"])
        assert copied == {
            "evidence_key": source["role"],
            "title_zh_cn": source["title_zh_cn"],
            "classification": source["classification"],
            "media_type": source["media_type"],
            "metadata": source["metadata"],
            "file_name": copied_path.name,
            "path": str(copied_path),
            "size_bytes": source["size_bytes"],
            "sha256": source["sha256"],
        }
        assert copied_path == upload_root / f"{ordinal:02d}-{Path(source['path']).name}"
        assert copied_path.is_file()
        assert copied_path.stat().st_size == source["size_bytes"]
        assert module.hashlib.sha256(copied_path.read_bytes()).hexdigest() == source["sha256"]
    serialized = json.dumps(upload_manifest, ensure_ascii=False).casefold()
    for sensitive in (
        "authorization",
        "capability",
        "cookie",
        "credential",
        "password",
        "secret",
        "token",
    ):
        assert sensitive not in serialized


def test_ui_upload_materialization_cleans_partial_copy_and_allows_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = _module()
    helpers = runpy.run_path(str(ROOT / "backend/tests/test_demo_abc_runtime_bundle.py"))
    bundle, _manifest, _manifest_sha = helpers["_valid_v6_bundle"](
        tmp_path / "bundle"
    )
    artifact = (tmp_path / "external-artifact").resolve()
    artifact.mkdir()
    real_copyfile = module.shutil.copyfile
    copy_count = 0

    def fail_second_copy(source: Path, target: Path):
        nonlocal copy_count
        copy_count += 1
        if copy_count == 2:
            raise OSError("second copy failed")
        return real_copyfile(source, target)

    monkeypatch.setattr(module.shutil, "copyfile", fail_second_copy)
    with pytest.raises(OSError, match="second copy failed"):
        module.materialize_ui_upload_manifest(bundle, artifact)

    assert not (artifact / "upload-files").exists()
    assert not (artifact / "upload-manifest.json").exists()
    monkeypatch.setattr(module.shutil, "copyfile", real_copyfile)
    module.materialize_ui_upload_manifest(bundle, artifact)
    assert len(list((artifact / "upload-files").iterdir())) == 12
    assert (artifact / "upload-manifest.json").is_file()


def test_ui_upload_manifest_rejects_missing_required_field_before_writing(
    tmp_path: Path,
):
    module = _module()
    helpers = runpy.run_path(str(ROOT / "backend/tests/test_demo_abc_runtime_bundle.py"))
    bundle, manifest, _manifest_sha = helpers["_valid_v6_bundle"](
        tmp_path / "bundle"
    )
    manifest["evidence"][0].pop("role")
    helpers["_write_manifest"](bundle, manifest)
    artifact = (tmp_path / "external-artifact").resolve()
    artifact.mkdir()

    with pytest.raises(RuntimeError, match="required fields"):
        module.materialize_ui_upload_manifest(bundle, artifact)

    assert not (artifact / "upload-files").exists()
    assert not (artifact / "upload-manifest.json").exists()


def test_ui_upload_manifest_rejects_unknown_metadata_key_before_writing(
    tmp_path: Path,
):
    module = _module()
    helpers = runpy.run_path(str(ROOT / "backend/tests/test_demo_abc_runtime_bundle.py"))
    bundle, manifest, _manifest_sha = helpers["_valid_v6_bundle"](
        tmp_path / "bundle"
    )
    manifest["evidence"][0]["metadata"]["api_key"] = "must-not-be-exported"
    helpers["_write_manifest"](bundle, manifest)
    artifact = (tmp_path / "external-artifact").resolve()
    artifact.mkdir()

    with pytest.raises(RuntimeError, match="required fields"):
        module.materialize_ui_upload_manifest(bundle, artifact)

    assert not (artifact / "upload-files").exists()
    assert not (artifact / "upload-manifest.json").exists()


def test_ui_session_removes_new_empty_artifact_when_upload_materialization_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = _module()
    artifact = (tmp_path / "external-artifact").resolve()
    args = module.argparse.Namespace(actor="CODEX", artifact=artifact)
    monkeypatch.setattr(module, "_new_run_context", lambda **_kwargs: object())

    def fail_materialization(*_args):
        raise RuntimeError("materialize failed")

    monkeypatch.setattr(
        module,
        "materialize_ui_upload_manifest",
        fail_materialization,
    )

    with pytest.raises(RuntimeError, match="materialize failed"):
        module._run_ui_session(args, tmp_path / "bundle", "a" * 64, "b" * 64, {})

    assert not artifact.exists()


def test_ui_session_materializes_upload_files_before_starting_services(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = _module()
    artifact = (tmp_path / "external-artifact").resolve()
    args = module.argparse.Namespace(actor="HUMAN", artifact=artifact)
    context = object()
    service_process = object()
    events: list[object] = []
    monkeypatch.setattr(module, "_new_run_context", lambda **_kwargs: context)
    monkeypatch.setattr(
        module,
        "materialize_ui_upload_manifest",
        lambda bundle, target: events.append(("uploads", bundle, target)),
    )
    monkeypatch.setattr(
        module,
        "_start_services",
        lambda actual_context, _log: (
            events.append(("services", actual_context)),
            service_process,
        )[1],
    )
    monkeypatch.setattr(module.abc, "wait_url", lambda *_args: None)
    monkeypatch.setattr(module, "_run_ui_browser_session", lambda *_args: "STOPPED")
    monkeypatch.setattr(module, "_stop_process", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(module, "_complete_ui_session", lambda *_args: None)

    module._run_ui_session(args, tmp_path / "bundle", "a" * 64, "b" * 64, {})

    assert events == [
        ("uploads", tmp_path / "bundle", artifact),
        ("services", context),
    ]


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


def test_legacy_journey_reads_v6_service_provenance_from_the_first_item():
    source = LEGACY_SPEC.read_text(encoding="utf-8")

    assert "const primaryItem = (item.items as Json[])[0]" in source
    assert "const primaryCreatedItem = (created.items as Json[])[0]" in source
    assert "this.bundleAmount = created.total_amount" in source
    assert "rate_item_code: primaryItem.item_code" in source
    assert "rate_source_ref: primaryItem.source_ref" in source
    assert "rate_source_version: primaryItem.source_version" in source
    assert "rate_source_sha256: primaryItem.source_sha256" in source
    assert "rate_item_code: primaryCreatedItem.item_code" in source
    assert "rate_source_ref: primaryCreatedItem.source_ref" in source
    assert "rate_source_version: primaryCreatedItem.source_version" in source
    assert "rate_source_sha256: primaryCreatedItem.source_sha256" in source
    assert "disclaimer: primaryCreatedItem.disclaimer_zh_cn" in source
    assert "bundle_amount: created.total_amount" in source


def test_v6_runner_reuses_only_the_legacy_lifecycle_prefix():
    runner = RUNNER.read_text(encoding="utf-8")
    source = LEGACY_SPEC.read_text(encoding="utf-8")

    assert 'FPMS_DEMO_V6_TAIL="1"' in runner
    assert "const v6Tail = process.env.FPMS_DEMO_V6_TAIL === '1'" in source
    assert "`${baseUrl}/demo/inputs`" in source
    assert "getByTestId('demo-inputs-preflight')" in source
    assert "if (!v6Tail) {" in source
    assert "if (v6Tail) {" in source
    assert "checkpoint: 'IA-12'" in source
    assert "'task9-checkpoints.json'" in source
    assert "await reviewerContext.close()\n    return" in source


def test_replacement_grant_notice_is_typed_as_an_official_incoming_document():
    source = LEGACY_SPEC.read_text(encoding="utf-8")

    assert "doc_type: 'OFFICIAL_IN'" in source


def test_demo_inputs_parser_accepts_the_v6_multi_item_preflight_shape():
    source = (
        ROOT / "frontend/src/modules/demo/demo.contract.ts"
    ).read_text(encoding="utf-8")

    assert "Array.isArray(raw.items)" in source
    assert "const primary = record(raw.items[0], 'service_item.items[0]')" in source
    assert "amount: raw.total_amount" in source
    assert "return row as unknown as DemoServiceItem" in source
    assert "const normalized = parseDemoServiceItem(value)" in source


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
        for index in range(13)
    ]
    identities = {
        "client_id": f"client-{ordinal}",
        "contact_id": f"contact-{ordinal}",
        "case_id": f"case-{ordinal}",
        "package_id": f"package-{ordinal}",
        "grant_task_id": f"grant-task-{ordinal}",
        "gov_draft_id": f"gov-draft-{ordinal}",
        "service_draft_id": f"service-draft-{ordinal}",
        "bill_id": f"bill-{ordinal}",
        "first_payment_id": f"payment-{ordinal}-1",
        "second_payment_id": f"payment-{ordinal}-2",
        "first_offset_id": f"offset-{ordinal}-1",
        "second_offset_id": f"offset-{ordinal}-2",
    }
    checkpoints[1]["result"] = {
        "client_id": identities["client_id"],
        "contact_id": identities["contact_id"],
    }
    checkpoints[2]["result"] = {"case_id": identities["case_id"]}
    checkpoints[4]["result"] = {"package_id": identities["package_id"]}
    checkpoints[11]["result"] = {"replacement_task_id": identities["grant_task_id"]}
    (run / "task9-checkpoints.json").write_text(
        json.dumps({"checkpoints": checkpoints, "evidence_bindings": [{}] * 12}),
        encoding="utf-8",
    )
    (run / "evidence-role-map.json").write_text(json.dumps([{}] * 12), encoding="utf-8")
    (run / "v6-final.png").write_bytes(b"png")
    v6_stages = [
        {"stage": f"{index:02d}", "label": f"stage-{index}"}
        for index in range(1, 12)
    ]
    v6_stages[6].update({"gov_draft_id": identities["gov_draft_id"]})
    v6_stages[7].update({"service_draft_id": identities["service_draft_id"]})
    v6_stages[9].update(
        {
            "bill_id": identities["bill_id"],
            "first_payment_id": identities["first_payment_id"],
            "second_payment_id": identities["second_payment_id"],
            "first_offset_id": identities["first_offset_id"],
            "second_offset_id": identities["second_offset_id"],
            "partial_status": "PARTIALLY_SETTLED",
            "partial_balance": "600.00",
            "final_status": "SETTLED",
            "final_balance": "0.00",
            "amount_equation": "1200.00 + 600.00 = 1800.00",
        }
    )
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
    assert summary["checkpoint_counts"] == [13, 13]
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
