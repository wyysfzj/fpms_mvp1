from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_demo_integrated_a_rehearsal.py"


def _module():
    spec = importlib.util.spec_from_file_location("run_demo_integrated_a_rehearsal", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_controller_materializes_six_hash_bound_outputs_outside_bundle(tmp_path: Path) -> None:
    module = _module()
    bundle_parent = tmp_path / "bundle-parent"
    bundle_parent.mkdir()
    bundle, _manifest_sha, _authority_sha = module.build_integrated_bundle(bundle_parent)
    bundle_before = {
        item.relative_to(bundle).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in sorted(bundle.rglob("*"))
        if item.is_file()
    }
    output_root = tmp_path / "run-evidence" / "oa-reply-outputs"

    descriptors = module.materialize_oa_reply_outputs(output_root)

    assert len(descriptors) == 6
    assert {(item["oa_sequence"], item["official_file_role"]) for item in descriptors} == {
        (1, "OA_STATEMENT_WORD"),
        (1, "OA_STATEMENT_PDF"),
        (1, "OA_MODIFIED_CLAIMS"),
        (2, "OA_STATEMENT_WORD"),
        (2, "OA_STATEMENT_PDF"),
        (2, "OA_MODIFIED_CLAIMS"),
    }
    assert {item["classification"] for item in descriptors} == {"SYNTHETIC_TEST_OUTPUT"}
    assert len({item["path"] for item in descriptors}) == 6
    assert len({item["sha256"] for item in descriptors}) == 6
    for item in descriptors:
        output_path = Path(item["path"])
        assert output_path.is_file()
        assert output_root.resolve() in output_path.resolve().parents
        assert bundle.resolve() not in output_path.resolve().parents
        assert hashlib.sha256(output_path.read_bytes()).hexdigest() == item["sha256"]
        assert item["title_zh_cn"].startswith("虚构")
        if output_path.suffix == ".docx":
            with ZipFile(output_path) as archive:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            assert "仅用于本地虚构演示" in document_xml
        else:
            assert output_path.suffix == ".pdf"
            assert output_path.read_bytes().startswith(b"%PDF")
    bundle_after = {
        item.relative_to(bundle).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in sorted(bundle.rglob("*"))
        if item.is_file()
    }
    assert bundle_after == bundle_before
    encoded = module.oa_reply_outputs_json(descriptors)
    assert json.loads(encoded) == descriptors


def test_controller_passes_only_output_descriptor_json_to_browser() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "FPMS_DEMO_INTEGRATED_OA_REPLY_OUTPUT_JSON" in source
    assert "materialize_oa_reply_outputs(run_artifact / \"oa-reply-outputs\")" in source
    assert "SYNTHETIC_TEST_OUTPUT" in source
    assert "FPMS_DEMO_INTEGRATED_EVIDENCE_JSON" in source
