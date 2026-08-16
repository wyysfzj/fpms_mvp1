from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from zoneinfo import ZoneInfo

from docxtpl import DocxTemplate
from pypdf import PdfReader


class DemoBundleError(RuntimeError):
    pass


@dataclass(frozen=True)
class DemoServiceRate:
    item_code: str
    name_zh_cn: str
    currency: str
    amount: str
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str


@dataclass(frozen=True)
class DemoTemplate:
    template_code: str
    path: Path
    sha256: str
    required_variables: tuple[str, ...]


@dataclass(frozen=True)
class DemoBundleSnapshot:
    bundle_root: Path
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    local_date: date
    template: DemoTemplate
    service_rate: DemoServiceRate
    evidence_roles: tuple[str, ...]


_CONTRACT_REF = "docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md"
_CAPABILITIES = [
    "FICTIONAL_LIFECYCLE_EVIDENCE",
    "INTERNAL_TEMPLATE_PREVIEW",
    "SERVICE_PRICE_TO_OBLIGATION",
]
_EVIDENCE_ROLES = [
    "FILING_FINAL_SUBMISSION",
    "FILING_RECEIPT",
    "ACCEPTANCE_NOTICE",
    "PRELIMINARY_EXAMINATION_SOURCE",
    "PUBLICATION_NOTICE",
    "SUBSTANTIVE_EXAMINATION_SOURCE",
    "OA_NOTICE",
    "OA_RECEIPT",
]
_TOP_KEYS = {
    "schema_version",
    "bundle_id",
    "bundle_version",
    "classification",
    "purpose",
    "valid_from",
    "valid_until",
    "authority",
    "provenance",
    "contract",
    "capabilities",
    "templates",
    "evidence",
    "rates",
}
_METADATA_KEYS = {
    "effective_at",
    "received_at",
    "receipt_kind",
    "official_due_date",
    "official_due_date_source",
    "official_due_date_status",
    "oa_sequence",
    "source_template_code",
}
_HASH_RE = re.compile(r"[0-9a-f]{64}")
_BUNDLE_ID_RE = re.compile(r"[a-z0-9._-]{1,64}")
_VERSION_RE = re.compile(r"[A-Za-z0-9._-]{1,64}")
_CODE_RE = re.compile(r"[A-Z0-9_]{1,64}")
_VARIABLE_RE = re.compile(r"[a-z][a-z0-9_]{0,63}")
_AMOUNT_RE = re.compile(r"(?:0|[1-9][0-9]*)\.[0-9]{2}")
_PDF_MARKER = "FICTIONAL_DEMO_EVIDENCE"
_DOCX_MARKER = "DEMO_ONLY / 仅用于本地虚构演示"


def _current_demo_date() -> date:
    return datetime.now(ZoneInfo("Asia/Shanghai")).date()


def _error(message: str) -> DemoBundleError:
    return DemoBundleError(f"DEMO_INPUT_INVALID: {message}")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _error(f"duplicate key: {key}")
        result[key] = value
    return result


def _expect_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise _error(
            f"{label} unknown keys or missing keys: "
            f"extra={sorted(actual - expected)}, missing={sorted(expected - actual)}"
        )
    return value


def _string(value: Any, label: str, *, minimum: int = 1, maximum: int) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise _error(f"{label} must be a {minimum}..{maximum} character string")
    return value


def _matches(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise _error(f"{label} has invalid format")
    return value


def _exact(value: Any, expected: Any, label: str) -> None:
    if value != expected:
        raise _error(f"{label} must be {expected!r}")


def _iso_date(value: Any, label: str) -> date:
    if not isinstance(value, str):
        raise _error(f"{label} must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise _error(f"{label} must be an ISO date") from exc
    if parsed.isoformat() != value:
        raise _error(f"{label} must be an ISO date")
    return parsed


def _naive_timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise _error(f"{label} must be a naive ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise _error(f"{label} must be a naive ISO timestamp") from exc
    if parsed.tzinfo is not None or parsed.microsecond != 0 or parsed.isoformat() != value:
        raise _error(f"{label} must be a second-precision naive ISO timestamp")
    return value


def _safe_relative_path(value: Any, label: str, prefix: str, suffix: str) -> str:
    text = _string(value, label, maximum=240)
    pure = PurePosixPath(text)
    if pure.is_absolute() or pure.as_posix() != text or any(part in {"", ".", ".."} for part in pure.parts):
        raise _error(f"{label} is not a normalized relative path")
    if not text.startswith(prefix) or not text.endswith(suffix):
        raise _error(f"{label} must match {prefix}*{suffix}")
    return text


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_file(path: Path, row: dict[str, Any], label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise _error(f"{label} must be a regular file")
    size = row["size_bytes"]
    if not isinstance(size, int) or isinstance(size, bool) or not 1 <= size <= 10_485_760:
        raise _error(f"{label} size_bytes is invalid")
    digest = _matches(row["sha256"], _HASH_RE, f"{label}.sha256")
    if path.stat().st_size != size or _sha256_file(path) != digest:
        raise _error(f"{label} size or hash mismatch")


def _validate_docx(path: Path, required_variables: tuple[str, ...]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if not entries or len(entries) > 200:
                raise _error("DOCX ZIP entry limit exceeded")
            total = 0
            for entry in entries:
                pure = PurePosixPath(entry.filename)
                if pure.is_absolute() or ".." in pure.parts:
                    raise _error("DOCX contains an unsafe ZIP path")
                total += entry.file_size
                if total > 20 * 1024 * 1024:
                    raise _error("DOCX uncompressed size limit exceeded")
                if entry.file_size and (
                    entry.compress_size == 0 or entry.file_size / entry.compress_size > 100
                ):
                    raise _error("DOCX compression ratio limit exceeded")
                if entry.filename.lower().endswith(("vbaProject.bin".lower(), ".exe", ".js")):
                    raise _error("DOCX contains a disallowed executable entry")
                if entry.filename.endswith(".rels"):
                    rels = archive.read(entry).decode("utf-8", errors="strict")
                    if re.search(r'TargetMode\s*=\s*["\']External["\']', rels, re.IGNORECASE):
                        raise _error("DOCX external relationship is forbidden")
            try:
                document_xml = archive.read("word/document.xml").decode("utf-8")
            except (KeyError, UnicodeDecodeError) as exc:
                raise _error("DOCX document.xml is missing or invalid") from exc
            if _DOCX_MARKER not in document_xml:
                raise _error("DOCX visible demo marker is missing")
    except zipfile.BadZipFile as exc:
        raise _error("DOCX is not a valid ZIP package") from exc
    try:
        actual_variables = tuple(sorted(DocxTemplate(str(path)).get_undeclared_template_variables()))
    except Exception as exc:
        raise _error("DOCX template variables cannot be extracted") from exc
    if actual_variables != required_variables:
        raise _error(
            "DOCX placeholder mismatch: "
            f"actual={list(actual_variables)}, declared={list(required_variables)}"
        )


def _validate_pdf(path: Path) -> None:
    try:
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted or not reader.pages:
            raise _error("PDF must contain a readable first page")
        first_page_text = reader.pages[0].extract_text() or ""
    except DemoBundleError:
        raise
    except Exception as exc:
        raise _error("PDF is not structurally readable") from exc
    if _PDF_MARKER not in first_page_text:
        raise _error("PDF first-page visible fictional demo marker is missing")


def _validate_authority(manifest: dict[str, Any], repo_root: Path) -> None:
    authority = _expect_keys(manifest["authority"], {"decision_ref", "decision_version"}, "authority")
    decision_ref = _safe_relative_path(
        authority["decision_ref"], "authority.decision_ref", "docs/", ".txt"
    )
    _string(authority["decision_version"], "authority.decision_version", maximum=120)
    decision_path = (repo_root / decision_ref).resolve()
    if repo_root.resolve() not in decision_path.parents or not decision_path.is_file():
        raise _error("authority decision_ref is unavailable")

    provenance = _expect_keys(
        manifest["provenance"],
        {"label_zh_cn", "source_ref", "source_version", "source_sha256"},
        "provenance",
    )
    _string(provenance["label_zh_cn"], "provenance.label_zh_cn", maximum=120)
    _string(provenance["source_ref"], "provenance.source_ref", maximum=240)
    _string(provenance["source_version"], "provenance.source_version", maximum=120)
    _matches(provenance["source_sha256"], _HASH_RE, "provenance.source_sha256")

    contract = _expect_keys(manifest["contract"], {"ref", "sha256"}, "contract")
    _exact(contract["ref"], _CONTRACT_REF, "contract.ref")
    contract_digest = _matches(contract["sha256"], _HASH_RE, "contract.sha256")
    contract_path = (repo_root / _CONTRACT_REF).resolve()
    if repo_root.resolve() not in contract_path.parents or not contract_path.is_file():
        raise _error("adopted contract is unavailable")
    if _sha256_file(contract_path) != contract_digest:
        raise _error("adopted contract digest mismatch")


def _validate_metadata(role: str, metadata_value: Any) -> None:
    metadata = _expect_keys(metadata_value, _METADATA_KEYS, f"evidence[{role}].metadata")
    receipt_role = role in {"FILING_RECEIPT", "OA_RECEIPT"}
    oa_notice = role == "OA_NOTICE"

    if receipt_role:
        _naive_timestamp(metadata["received_at"], f"evidence[{role}].received_at")
        if metadata["receipt_kind"] not in {
            "RECEIPT_PDF",
            "MERGED_PDF",
            "ELECTRONIC_APPLICATION_RECEIPT",
        }:
            raise _error(f"evidence[{role}] receipt_kind is invalid")
        null_keys = {
            "effective_at",
            "official_due_date",
            "official_due_date_source",
            "official_due_date_status",
            "source_template_code",
        }
    elif oa_notice:
        _exact(metadata["oa_sequence"], 1, "evidence[OA_NOTICE].metadata.oa_sequence")
        _naive_timestamp(metadata["effective_at"], "evidence[OA_NOTICE].effective_at")
        _iso_date(metadata["official_due_date"], "evidence[OA_NOTICE].official_due_date")
        if metadata["official_due_date_source"] not in {
            "MANUAL_OFFICIAL_NOTICE",
            "IMPORTED_OFFICIAL_NOTICE",
        }:
            raise _error("OA semantic due-date source is invalid")
        _exact(metadata["official_due_date_status"], "CONFIRMED", "OA semantic due-date status")
        _exact(metadata["source_template_code"], "DEMO_OA_NOTICE_1", "OA semantic template")
        null_keys = {"received_at", "receipt_kind"}
    else:
        _naive_timestamp(metadata["effective_at"], f"evidence[{role}].effective_at")
        null_keys = {
            "received_at",
            "receipt_kind",
            "official_due_date",
            "official_due_date_source",
            "official_due_date_status",
            "source_template_code",
        }
    if not oa_notice:
        null_keys.add("oa_sequence")
    for key in null_keys:
        if metadata[key] is not None:
            raise _error(f"evidence[{role}].metadata.{key} must be null")


def load_demo_bundle(
    bundle_root: Path,
    *,
    expected_manifest_sha256: str,
    repo_root: Path,
) -> DemoBundleSnapshot:
    unresolved_root = Path(bundle_root)
    if unresolved_root.is_symlink():
        raise _error("bundle root must not be a symlink")
    root = unresolved_root.resolve()
    repo = Path(repo_root).resolve()
    expected_digest = _matches(
        expected_manifest_sha256, _HASH_RE, "expected manifest digest"
    )
    if not root.is_dir():
        raise _error("bundle root must be a real directory")
    if root == repo or repo in root.parents:
        raise _error("bundle root must be outside the repository")
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise _error("manifest.json is missing")
    raw_manifest = manifest_path.read_bytes()
    if _sha256_file(manifest_path) != expected_digest:
        raise _error("manifest digest mismatch")
    if raw_manifest.startswith(b"\xef\xbb\xbf") or b"\r" in raw_manifest or not raw_manifest.endswith(b"\n"):
        raise _error("manifest encoding or line endings are invalid")
    try:
        text = raw_manifest.decode("utf-8")
        manifest = json.loads(text, object_pairs_hook=_object_without_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _error("manifest JSON is invalid") from exc
    manifest = _expect_keys(manifest, _TOP_KEYS, "manifest")

    _exact(manifest["schema_version"], "fpms.demo-input-bundle/v1", "schema_version")
    bundle_id = _matches(manifest["bundle_id"], _BUNDLE_ID_RE, "bundle_id")
    bundle_version = _matches(manifest["bundle_version"], _VERSION_RE, "bundle_version")
    _exact(manifest["classification"], "DEMO_ONLY", "classification")
    _exact(manifest["purpose"], "LOCAL_ABC_E2E", "purpose")
    valid_from = _iso_date(manifest["valid_from"], "valid_from")
    valid_until = _iso_date(manifest["valid_until"], "valid_until")
    local_date = _current_demo_date()
    if valid_until < valid_from or not valid_from <= local_date <= valid_until:
        raise _error(
            "bundle validity does not include the current Asia/Shanghai local date"
        )
    _validate_authority(manifest, repo)
    _exact(manifest["capabilities"], _CAPABILITIES, "capabilities")

    templates = manifest["templates"]
    if not isinstance(templates, list) or len(templates) != 1:
        raise _error("templates must contain exactly one row")
    template_row = _expect_keys(
        templates[0],
        {
            "consumer",
            "template_code",
            "group",
            "language",
            "path",
            "media_type",
            "size_bytes",
            "sha256",
            "required_variables",
        },
        "templates[0]",
    )
    _exact(template_row["consumer"], "DOCUMENT_RENDER", "templates[0].consumer")
    template_code = _matches(template_row["template_code"], _CODE_RE, "template_code")
    _exact(template_row["group"], "INTERNAL_DEMO", "templates[0].group")
    _exact(template_row["language"], "zh-CN", "templates[0].language")
    _exact(
        template_row["media_type"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "templates[0].media_type",
    )
    template_relative = _safe_relative_path(
        template_row["path"], "templates[0].path", "templates/", ".docx"
    )
    variables = template_row["required_variables"]
    if (
        not isinstance(variables, list)
        or not variables
        or variables != sorted(set(variables))
        or any(not isinstance(value, str) or _VARIABLE_RE.fullmatch(value) is None for value in variables)
    ):
        raise _error("required_variables must be a non-empty sorted unique allowlist")

    evidence_rows = manifest["evidence"]
    if not isinstance(evidence_rows, list) or [row.get("role") for row in evidence_rows if isinstance(row, dict)] != _EVIDENCE_ROLES:
        raise _error("evidence roles or order are invalid")
    expected_files = {"manifest.json", template_relative}
    for index, row_value in enumerate(evidence_rows):
        role = _EVIDENCE_ROLES[index]
        row = _expect_keys(
            row_value,
            {
                "role",
                "title_zh_cn",
                "classification",
                "path",
                "media_type",
                "size_bytes",
                "sha256",
                "metadata",
            },
            f"evidence[{index}]",
        )
        _exact(row["role"], role, f"evidence[{index}].role")
        _string(row["title_zh_cn"], f"evidence[{role}].title_zh_cn", maximum=120)
        _exact(row["classification"], "FICTIONAL_DEMO_EVIDENCE", f"evidence[{role}].classification")
        _exact(row["media_type"], "application/pdf", f"evidence[{role}].media_type")
        relative = _safe_relative_path(row["path"], f"evidence[{role}].path", "evidence/", ".pdf")
        if relative in expected_files:
            raise _error("duplicate bundle file identity")
        expected_files.add(relative)
        _validate_metadata(role, row["metadata"])

    rates = manifest["rates"]
    if not isinstance(rates, list) or len(rates) != 1:
        raise _error("rates must contain exactly one row")
    rate = _expect_keys(
        rates[0],
        {
            "domain",
            "item_code",
            "name_zh_cn",
            "currency",
            "calc_mode",
            "amount",
            "source_ref",
            "source_version",
            "source_sha256",
            "disclaimer_zh_cn",
        },
        "rates[0]",
    )
    _exact(rate["domain"], "SERVICE_DEMO_PRICE", "rates[0].domain")
    item_code = _matches(rate["item_code"], _CODE_RE, "rates[0].item_code")
    name_zh_cn = _string(rate["name_zh_cn"], "rates[0].name_zh_cn", maximum=120)
    _exact(rate["currency"], "CNY", "rates[0].currency")
    _exact(rate["calc_mode"], "FIXED", "rates[0].calc_mode")
    amount = _matches(rate["amount"], _AMOUNT_RE, "rates[0].amount")
    if amount == "0.00":
        raise _error("rates[0].amount must be positive")
    source_ref = _string(rate["source_ref"], "rates[0].source_ref", maximum=240)
    source_version = _string(rate["source_version"], "rates[0].source_version", maximum=120)
    source_sha = _matches(rate["source_sha256"], _HASH_RE, "rates[0].source_sha256")
    disclaimer = _string(rate["disclaimer_zh_cn"], "rates[0].disclaimer_zh_cn", maximum=200)

    actual_files: set[str] = set()
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise _error("bundle contains a symlink")
        if candidate.is_file():
            actual_files.add(candidate.relative_to(root).as_posix())
    if actual_files != expected_files:
        raise _error(
            f"bundle file set mismatch: extra={sorted(actual_files - expected_files)}, "
            f"missing={sorted(expected_files - actual_files)}"
        )

    template_path = root / template_relative
    _validate_file(template_path, template_row, "templates[0]")
    _validate_docx(template_path, tuple(variables))
    for index, row in enumerate(evidence_rows):
        evidence_path = root / row["path"]
        _validate_file(evidence_path, row, f"evidence[{index}]")
        _validate_pdf(evidence_path)

    return DemoBundleSnapshot(
        bundle_root=root,
        bundle_id=bundle_id,
        bundle_version=bundle_version,
        manifest_sha256=expected_digest,
        local_date=local_date,
        template=DemoTemplate(
            template_code=template_code,
            path=template_path,
            sha256=template_row["sha256"],
            required_variables=tuple(variables),
        ),
        service_rate=DemoServiceRate(
            item_code=item_code,
            name_zh_cn=name_zh_cn,
            currency="CNY",
            amount=amount,
            source_ref=source_ref,
            source_version=source_version,
            source_sha256=source_sha,
            disclaimer_zh_cn=disclaimer,
        ),
        evidence_roles=tuple(_EVIDENCE_ROLES),
    )
