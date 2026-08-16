from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path

import pytest

try:
    from app.core import demo_bundle
    from app.core.demo_bundle import DemoBundleError, load_demo_bundle
except ImportError:
    demo_bundle = None

    class DemoBundleError(RuntimeError):
        pass

    def load_demo_bundle(*_args, **_kwargs):
        pytest.fail("demo bundle preflight is not implemented")


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_REF = "docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md"
EVIDENCE_ROLES = [
    "FILING_FINAL_SUBMISSION",
    "FILING_RECEIPT",
    "ACCEPTANCE_NOTICE",
    "PRELIMINARY_EXAMINATION_SOURCE",
    "PUBLICATION_NOTICE",
    "SUBSTANTIVE_EXAMINATION_SOURCE",
    "OA_NOTICE",
    "OA_RECEIPT",
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_docx(path: Path, *, marker: bool = True, external: bool = False) -> None:
    marker_text = "DEMO_ONLY / 仅用于本地虚构演示" if marker else "普通模板"
    relationship = (
        '<Relationship Id="rId1" Target="https://example.invalid" TargetMode="External" />'
        if external
        else ""
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "word/document.xml",
            f'<w:document xmlns:w="urn:test"><w:body><w:t>{marker_text}</w:t></w:body></w:document>',
        )
        archive.writestr(
            "word/_rels/document.xml.rels",
            f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f"{relationship}</Relationships>",
        )


def _metadata_for(role: str) -> dict[str, object]:
    metadata: dict[str, object] = {
        "effective_at": None,
        "received_at": None,
        "receipt_kind": None,
        "official_due_date": None,
        "official_due_date_source": None,
        "official_due_date_status": None,
        "oa_sequence": 1,
        "source_template_code": None,
    }
    if role in {"FILING_RECEIPT", "OA_RECEIPT"}:
        metadata["received_at"] = "2026-08-16T10:00:00"
        metadata["receipt_kind"] = "RECEIPT_PDF"
    else:
        metadata["effective_at"] = "2026-08-16T09:00:00"
    if role == "OA_NOTICE":
        metadata.update(
            official_due_date="2026-09-16",
            official_due_date_source="MANUAL_OFFICIAL_NOTICE",
            official_due_date_status="CONFIRMED",
            source_template_code="DEMO_OA_NOTICE_1",
        )
    return metadata


def _write_manifest(bundle_root: Path, manifest: dict[str, object]) -> str:
    raw = (json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    (bundle_root / "manifest.json").write_bytes(raw)
    return _sha256(raw)


def _valid_bundle(tmp_path: Path) -> tuple[Path, dict[str, object], str]:
    bundle_root = tmp_path / "bundle"
    templates = bundle_root / "templates"
    evidence = bundle_root / "evidence"
    templates.mkdir(parents=True)
    evidence.mkdir()

    template_path = templates / "demo-letter.docx"
    _write_docx(template_path)
    evidence_rows: list[dict[str, object]] = []
    for role in EVIDENCE_ROLES:
        evidence_path = evidence / f"{role.lower()}.pdf"
        evidence_bytes = (
            b"%PDF-1.4\n% FICTIONAL_DEMO_EVIDENCE / "
            + "仅用于本地虚构演示".encode()
            + b"\n%%EOF\n"
        )
        evidence_path.write_bytes(evidence_bytes)
        evidence_rows.append(
            {
                "role": role,
                "title_zh_cn": f"虚构演示证据-{role}",
                "classification": "FICTIONAL_DEMO_EVIDENCE",
                "path": f"evidence/{evidence_path.name}",
                "media_type": "application/pdf",
                "size_bytes": len(evidence_bytes),
                "sha256": _sha256(evidence_bytes),
                "metadata": _metadata_for(role),
            }
        )

    contract_bytes = (REPO_ROOT / CONTRACT_REF).read_bytes()
    manifest: dict[str, object] = {
        "schema_version": "fpms.demo-input-bundle/v1",
        "bundle_id": "fpms-local-abc",
        "bundle_version": "2026.08.16",
        "classification": "DEMO_ONLY",
        "purpose": "LOCAL_ABC_E2E",
        "valid_from": "2026-08-16",
        "valid_until": "2026-08-16",
        "authority": {
            "decision_ref": "docs/product/v8/customer-decisions/2026-08-15-local-demo-abc.txt",
            "decision_version": "DEC-LOCAL-DEMO-ABC-20260815",
        },
        "provenance": {
            "label_zh_cn": "本地虚构演示输入",
            "source_ref": "customer-demo-input",
            "source_version": "2026.08.16",
            "source_sha256": "a" * 64,
        },
        "contract": {"ref": CONTRACT_REF, "sha256": _sha256(contract_bytes)},
        "capabilities": [
            "FICTIONAL_LIFECYCLE_EVIDENCE",
            "INTERNAL_TEMPLATE_PREVIEW",
            "SERVICE_PRICE_TO_OBLIGATION",
        ],
        "templates": [
            {
                "consumer": "DOCUMENT_RENDER",
                "template_code": "DEMO_INTERNAL_LETTER_1",
                "group": "INTERNAL_DEMO",
                "language": "zh-CN",
                "path": "templates/demo-letter.docx",
                "media_type": (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ),
                "size_bytes": template_path.stat().st_size,
                "sha256": _sha256(template_path.read_bytes()),
                "required_variables": ["case_no", "client_name"],
            }
        ],
        "evidence": evidence_rows,
        "rates": [
            {
                "domain": "SERVICE_DEMO_PRICE",
                "item_code": "DEMO_SERVICE_1",
                "name_zh_cn": "演示服务费",
                "currency": "CNY",
                "calc_mode": "FIXED",
                "amount": "1200.00",
                "source_ref": "customer-demo-rate",
                "source_version": "2026.08.16",
                "source_sha256": "b" * 64,
                "disclaimer_zh_cn": "仅用于本地虚构演示，不是正式报价或官方费用。",
            }
        ],
    }
    return bundle_root, manifest, _write_manifest(bundle_root, manifest)


def test_valid_bundle_returns_immutable_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root, _manifest, digest = _valid_bundle(tmp_path)
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: date(2026, 8, 16))

    snapshot = load_demo_bundle(root, expected_manifest_sha256=digest, repo_root=REPO_ROOT)

    assert snapshot.bundle_id == "fpms-local-abc"
    assert snapshot.manifest_sha256 == digest
    assert snapshot.service_rate.amount == "1200.00"
    assert snapshot.evidence_roles == tuple(EVIDENCE_ROLES)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda manifest: manifest.update(extra=True), "unknown keys"),
        (
            lambda manifest: manifest["evidence"][6]["metadata"].update(
                source_template_code="OTHER_OA"
            ),
            "OA semantic",
        ),
        (lambda manifest: manifest.update(valid_until="2026-08-15"), "validity"),
    ],
)
def test_manifest_contract_mismatch_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation,
    message: str,
):
    root, manifest, _digest = _valid_bundle(tmp_path)
    mutation(manifest)
    digest = _write_manifest(root, manifest)
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: date(2026, 8, 16))

    with pytest.raises(DemoBundleError, match=message):
        load_demo_bundle(root, expected_manifest_sha256=digest, repo_root=REPO_ROOT)


def test_external_manifest_digest_is_checked_before_parsing(tmp_path: Path):
    root, _manifest, _digest = _valid_bundle(tmp_path)

    with pytest.raises(DemoBundleError, match="manifest digest"):
        load_demo_bundle(root, expected_manifest_sha256="0" * 64, repo_root=REPO_ROOT)


def test_file_hash_extra_file_and_marker_fail_closed(tmp_path: Path, monkeypatch):
    root, manifest, digest = _valid_bundle(tmp_path)
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: date(2026, 8, 16))
    evidence_path = root / manifest["evidence"][0]["path"]
    evidence_path.write_bytes(b"tampered")

    with pytest.raises(DemoBundleError, match="size or hash"):
        load_demo_bundle(root, expected_manifest_sha256=digest, repo_root=REPO_ROOT)

    root, _manifest, digest = _valid_bundle(tmp_path / "extra")
    (root / "unexpected.txt").write_text("unexpected")
    with pytest.raises(DemoBundleError, match="file set"):
        load_demo_bundle(root, expected_manifest_sha256=digest, repo_root=REPO_ROOT)

    root, manifest, _digest = _valid_bundle(tmp_path / "marker")
    template_path = root / manifest["templates"][0]["path"]
    _write_docx(template_path, marker=False)
    manifest["templates"][0]["size_bytes"] = template_path.stat().st_size
    manifest["templates"][0]["sha256"] = _sha256(template_path.read_bytes())
    digest = _write_manifest(root, manifest)
    with pytest.raises(DemoBundleError, match="demo marker"):
        load_demo_bundle(root, expected_manifest_sha256=digest, repo_root=REPO_ROOT)


def test_docx_external_relationship_fails_closed(tmp_path: Path, monkeypatch):
    root, manifest, _digest = _valid_bundle(tmp_path)
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: date(2026, 8, 16))
    template_path = root / manifest["templates"][0]["path"]
    _write_docx(template_path, external=True)
    manifest["templates"][0]["size_bytes"] = template_path.stat().st_size
    manifest["templates"][0]["sha256"] = _sha256(template_path.read_bytes())
    digest = _write_manifest(root, manifest)

    with pytest.raises(DemoBundleError, match="external relationship"):
        load_demo_bundle(root, expected_manifest_sha256=digest, repo_root=REPO_ROOT)
