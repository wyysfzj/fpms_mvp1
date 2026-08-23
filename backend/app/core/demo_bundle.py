from __future__ import annotations

import hashlib
import json
import math
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree
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
    unit_price: str
    initial_quantity: int
    final_quantity: int
    adjustable: bool
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str

    @property
    def amount(self) -> str:
        return self.unit_price


@dataclass(frozen=True)
class DemoOfficialFeeSelector:
    source_authority: str
    rate_book_version: str
    rate_book_sha256: str
    fee_codes: tuple[str, ...]
    fee_row_sha256s: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class DemoTemplate:
    template_code: str
    path: Path
    sha256: str
    required_variables: tuple[str, ...]


@dataclass(frozen=True)
class DemoEvidenceMetadata:
    effective_at: str | None
    received_at: str | None
    receipt_kind: str | None
    official_due_date: str | None
    official_due_date_source: str | None
    official_due_date_status: str | None
    oa_sequence: int | None
    source_template_code: str | None
    supersedes_role: str | None


@dataclass(frozen=True)
class DemoEvidence:
    role: str
    title_zh_cn: str
    path: Path
    sha256: str
    metadata: DemoEvidenceMetadata


@dataclass(frozen=True)
class DemoBundleSnapshot:
    bundle_root: Path
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    authority_sha256: str
    authority_classification: str
    customer_activation_eligible: bool
    approved_by: str
    approved_at: str
    local_date: date
    template: DemoTemplate
    service_rates: tuple[DemoServiceRate, ...]
    official_fee_selector: DemoOfficialFeeSelector | None
    first_receipt_amount: Decimal | None
    readiness: str
    schema_version: str
    evidence_roles: tuple[str, ...]
    evidence: tuple[DemoEvidence, ...]

    @property
    def service_rate(self) -> DemoServiceRate:
        return self.service_rates[0]


_CONTRACT_REF = "docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md"
_INTEGRATED_CONTRACT_REF = (
    "docs/superpowers/specs/2026-08-21-fpms-integrated-demo-a-design.md"
)
_V6_CONTRACT_REF = (
    "docs/superpowers/specs/"
    "2026-08-23-fpms-demo-v6-dual-track-fee-enrichment-design.md"
)
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
_INTEGRATED_EVIDENCE_ROLES = [
    "FILING_FINAL_SUBMISSION",
    "FILING_RECEIPT",
    "ACCEPTANCE_NOTICE",
    "PRELIMINARY_EXAMINATION_SOURCE",
    "PUBLICATION_NOTICE",
    "SUBSTANTIVE_EXAMINATION_SOURCE",
    "OA_NOTICE_1",
    "OA_RECEIPT_1",
    "OA_NOTICE_2",
    "OA_RECEIPT_2",
    "GRANT_NOTICE_ORIGINAL",
    "GRANT_NOTICE_REPLACEMENT",
]
_TOP_KEYS = {
    "schema_version",
    "bundle_id",
    "bundle_version",
    "classification",
    "authority_classification",
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
_V6_TOP_KEYS = _TOP_KEYS | {"official_fee_selector", "first_receipt_amount"}
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
_INTEGRATED_METADATA_KEYS = _METADATA_KEYS | {"supersedes_role"}
_HASH_RE = re.compile(r"[0-9a-f]{64}")
_BUNDLE_ID_RE = re.compile(r"[a-z0-9._-]{1,64}")
_VERSION_RE = re.compile(r"[A-Za-z0-9._-]{1,64}")
_CODE_RE = re.compile(r"[A-Z0-9_]{1,64}")
_FEE_CODE_RE = re.compile(r"[A-Z0-9_-]{1,64}")
_VARIABLE_RE = re.compile(r"[a-z][a-z0-9_]{0,63}")
_AMOUNT_RE = re.compile(r"(?:0|[1-9][0-9]*)\.[0-9]{2}")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_AUTHORITY_CLASSIFICATIONS = {"SYNTHETIC_TEST_ONLY", "CUSTOMER_AUTHORIZED"}
_PDF_MARKER = "FICTIONAL_DEMO_EVIDENCE / 仅用于本地虚构演示"
_DOCX_MARKER = "DEMO_ONLY / 仅用于本地虚构演示"
_WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


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
    if type(value) is not type(expected) or value != expected:
        raise _error(f"{label} must be {expected!r}")


def _visible_word_text(document_xml: str, styles_xml: str | None) -> str:
    try:
        root = ElementTree.fromstring(document_xml)
    except ElementTree.ParseError as exc:
        raise _error("DOCX document.xml is invalid") from exc
    word = f"{{{_WORD_NAMESPACE}}}"
    visible: list[str] = []

    def is_enabled(element: ElementTree.Element | None) -> bool:
        if element is None:
            return False
        value = element.get(f"{word}val")
        return value is None or value.lower() not in {"0", "false", "off", "no"}

    def properties_hidden(properties: ElementTree.Element | None) -> bool:
        return properties is not None and any(
            is_enabled(properties.find(f"{word}{name}"))
            for name in ("vanish", "webHidden")
        )

    style_hidden: dict[str, bool] = {}
    if styles_xml is not None:
        try:
            styles_root = ElementTree.fromstring(styles_xml)
        except ElementTree.ParseError as exc:
            raise _error("DOCX styles.xml is invalid") from exc
        style_rows: dict[str, tuple[str | None, bool]] = {}
        default_style_ids: dict[str, str] = {}
        for style in styles_root.findall(f"{word}style"):
            style_id = style.get(f"{word}styleId")
            if not style_id:
                continue
            style_type = style.get(f"{word}type")
            if (
                style_type in {"paragraph", "character"}
                and style.get(f"{word}default", "0").lower() in {"1", "true", "on", "yes"}
            ):
                default_style_ids[style_type] = style_id
            based_on = style.find(f"{word}basedOn")
            based_on_id = based_on.get(f"{word}val") if based_on is not None else None
            style_rows[style_id] = (based_on_id, properties_hidden(style.find(f"{word}rPr")))

        resolving: set[str] = set()

        def resolve_style(style_id: str) -> bool:
            if style_id in style_hidden:
                return style_hidden[style_id]
            if style_id in resolving:
                raise _error("DOCX style inheritance cycle is invalid")
            row = style_rows.get(style_id)
            if row is None:
                return True
            resolving.add(style_id)
            based_on_id, directly_hidden = row
            hidden = directly_hidden or (
                based_on_id is not None and resolve_style(based_on_id)
            )
            resolving.remove(style_id)
            style_hidden[style_id] = hidden
            return hidden

        for style_id in style_rows:
            resolve_style(style_id)
        default_properties = styles_root.find(
            f"{word}docDefaults/{word}rPrDefault/{word}rPr"
        )
        default_hidden = properties_hidden(default_properties)
    else:
        default_hidden = False
        default_style_ids = {}

    def referenced_style_hidden(
        properties: ElementTree.Element | None,
        style_tag: str,
        default_style_type: str,
    ) -> bool:
        reference = properties.find(f"{word}{style_tag}") if properties is not None else None
        if reference is None:
            default_style_id = default_style_ids.get(default_style_type)
            return default_style_id is not None and style_hidden.get(default_style_id, True)
        style_id = reference.get(f"{word}val")
        return style_id is None or style_hidden.get(style_id, True)

    def collect(
        node: ElementTree.Element,
        hidden: bool = False,
        paragraph_style_is_hidden: bool = False,
    ) -> None:
        if node.tag in {f"{word}del", f"{word}moveFrom"}:
            return
        if node.tag == f"{word}p":
            paragraph_properties = node.find(f"{word}pPr")
            paragraph_style_is_hidden = referenced_style_hidden(
                paragraph_properties, "pStyle", "paragraph"
            ) or properties_hidden(
                paragraph_properties.find(f"{word}rPr")
                if paragraph_properties is not None
                else None
            )
        if node.tag == f"{word}r":
            properties = node.find(f"{word}rPr")
            hidden = (
                hidden
                or default_hidden
                or paragraph_style_is_hidden
                or properties_hidden(properties)
                or referenced_style_hidden(properties, "rStyle", "character")
            )
        if not hidden and node.tag == f"{word}t" and node.text:
            visible.append(node.text)
        for child in node:
            collect(child, hidden, paragraph_style_is_hidden)

    collect(root)
    return "".join(visible)


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


def _aware_timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise _error(f"{label} must be an aware ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise _error(f"{label} must be an aware ISO timestamp") from exc
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.microsecond != 0
        or parsed.isoformat() != value
    ):
        raise _error(f"{label} must be a second-precision aware ISO timestamp")
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
            try:
                styles_xml = archive.read("word/styles.xml").decode("utf-8")
            except KeyError:
                styles_xml = None
            except UnicodeDecodeError as exc:
                raise _error("DOCX styles.xml is invalid") from exc
            if _DOCX_MARKER not in _visible_word_text(document_xml, styles_xml):
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
        first_page = reader.pages[0]
        box = first_page.cropbox
        state = {
            "render_mode": 0,
            "clipped": False,
            "horizontal_scale": 100.0,
            "font_size": None,
            "unsafe_text_show": False,
        }
        stack: list[tuple[int, bool, float, float | None]] = []
        visible_fragments: list[str] = []

        def text_show_is_visible(cm, tm) -> bool:
            font_size = state["font_size"]
            if font_size is None:
                return False
            size = float(font_size)
            horizontal_scale = float(state["horizontal_scale"])
            values = [*(float(value) for value in cm), *(float(value) for value in tm)]
            determinant = (
                (float(cm[0]) * float(cm[3]) - float(cm[1]) * float(cm[2]))
                * (float(tm[0]) * float(tm[3]) - float(tm[1]) * float(tm[2]))
                * horizontal_scale
                / 100.0
            )
            x = float(tm[4]) * float(cm[0]) + float(tm[5]) * float(cm[2]) + float(cm[4])
            y = float(tm[4]) * float(cm[1]) + float(tm[5]) * float(cm[3]) + float(cm[5])
            return (
                state["render_mode"] == 0
                and not state["clipped"]
                and math.isfinite(size)
                and size > 0
                and math.isfinite(horizontal_scale)
                and abs(horizontal_scale) > 1e-12
                and all(math.isfinite(value) for value in values)
                and math.isfinite(determinant)
                and abs(determinant) > 1e-12
                and float(box.left) <= x <= float(box.right)
                and float(box.bottom) <= y <= float(box.top)
            )

        def before_operand(operator, operands, _cm, _tm) -> None:
            if operator == b"q":
                stack.append(
                    (
                        state["render_mode"],
                        state["clipped"],
                        state["horizontal_scale"],
                        state["font_size"],
                    )
                )
            elif operator == b"Q":
                if stack:
                    (
                        state["render_mode"],
                        state["clipped"],
                        state["horizontal_scale"],
                        state["font_size"],
                    ) = stack.pop()
            elif operator == b"Tr" and operands:
                state["render_mode"] = int(operands[0])
            elif operator == b"Tz" and operands:
                state["horizontal_scale"] = float(operands[0])
            elif operator == b"Tf" and len(operands) >= 2:
                state["font_size"] = float(operands[1])
            elif operator in {b"W", b"W*"}:
                state["clipped"] = True
            elif operator in {b"TJ", b"'", b'"'}:
                state["unsafe_text_show"] = True
            elif operator == b"Tj":
                if not text_show_is_visible(_cm, _tm):
                    state["unsafe_text_show"] = True

        def visit_text(text, _cm, _tm, _font, _font_size) -> None:
            if text:
                visible_fragments.append(text)

        first_page.extract_text(
            visitor_operand_before=before_operand,
            visitor_text=visit_text,
        )
    except DemoBundleError:
        raise
    except Exception as exc:
        raise _error("PDF is not structurally readable") from exc
    if state["unsafe_text_show"] or _PDF_MARKER not in "".join(visible_fragments):
        raise _error("PDF first-page visible bilingual fictional demo marker is missing")


def demo_bundle_forbidden_roots(
    bundle_path: Path,
    *,
    run_id: str,
    configured_storage: str | None,
) -> tuple[Path, ...]:
    resolved_bundle = Path(bundle_path).resolve()
    if not run_id:
        raise _error("demo run ID is missing")
    if any(part.startswith("fpms-demo-abc-") for part in resolved_bundle.parts):
        raise _error("demo bundle must not come from an existing run directory")
    if configured_storage:
        return (Path(configured_storage),)
    return ()


def _validate_authority(
    manifest: dict[str, Any], repo_root: Path, *, contract_ref: str
) -> None:
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
    _exact(contract["ref"], contract_ref, "contract.ref")
    contract_digest = _matches(contract["sha256"], _HASH_RE, "contract.sha256")
    contract_path = (repo_root / contract_ref).resolve()
    if repo_root.resolve() not in contract_path.parents or not contract_path.is_file():
        raise _error("adopted contract is unavailable")
    if _sha256_file(contract_path) != contract_digest:
        raise _error("adopted contract digest mismatch")


def _validate_authority_record(
    root: Path,
    *,
    expected_authority_sha256: str,
    manifest: dict[str, Any],
    manifest_sha256: str,
    repo_root: Path,
    expected_file_digests: list[dict[str, str]],
    expected_authority_classification: str,
) -> tuple[str, str, str]:
    authority_path = root / "authority.json"
    if authority_path.is_symlink() or not authority_path.is_file():
        raise _error("authority.json is missing")
    if _sha256_file(authority_path) != expected_authority_sha256:
        raise _error("authority digest mismatch")
    raw = authority_path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n"):
        raise _error("authority encoding or line endings are invalid")
    try:
        authority = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_object_without_duplicates
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _error("authority JSON is invalid") from exc
    authority = _expect_keys(
        authority,
        {
            "schema_version",
            "status",
            "authority_classification",
            "approved_by",
            "approved_at",
            "decision_ref",
            "decision_version",
            "decision_sha256",
            "bundle_id",
            "bundle_version",
            "manifest_sha256",
            "source_digests",
            "file_digests",
        },
        "authority record",
    )
    _exact(
        authority["schema_version"],
        "fpms.demo-bundle-authority/v1",
        "authority.schema_version",
    )
    _exact(authority["status"], "APPROVED", "authority.status")
    authority_classification = _string(
        authority["authority_classification"],
        "authority.authority_classification",
        maximum=64,
    )
    if authority_classification not in _AUTHORITY_CLASSIFICATIONS:
        raise _error("authority classification is invalid")
    _exact(
        authority_classification,
        expected_authority_classification,
        "authority classification",
    )
    _exact(
        authority_classification,
        manifest["authority_classification"],
        "authority classification",
    )
    approved_by = _string(authority["approved_by"], "authority.approved_by", maximum=120)
    approved_at = _aware_timestamp(authority["approved_at"], "authority.approved_at")

    manifest_authority = manifest["authority"]
    decision_ref = _safe_relative_path(
        authority["decision_ref"], "authority.decision_ref", "docs/", ".txt"
    )
    _exact(decision_ref, manifest_authority["decision_ref"], "authority.decision_ref")
    _exact(
        authority["decision_version"],
        manifest_authority["decision_version"],
        "authority.decision_version",
    )
    decision_digest = _matches(
        authority["decision_sha256"], _HASH_RE, "authority.decision_sha256"
    )
    decision_path = (repo_root / decision_ref).resolve()
    if repo_root not in decision_path.parents or not decision_path.is_file():
        raise _error("authority decision_ref is unavailable")
    if _sha256_file(decision_path) != decision_digest:
        raise _error("authority decision digest mismatch")

    _exact(authority["bundle_id"], manifest["bundle_id"], "authority.bundle_id")
    _exact(
        authority["bundle_version"],
        manifest["bundle_version"],
        "authority.bundle_version",
    )
    _exact(
        authority["manifest_sha256"],
        manifest_sha256,
        "authority.manifest_sha256",
    )
    expected_sources = [
        {
            "kind": "PROVENANCE",
            "ref": manifest["provenance"]["source_ref"],
            "version": manifest["provenance"]["source_version"],
            "sha256": manifest["provenance"]["source_sha256"],
        },
        *(
            {
                "kind": "SERVICE_RATE",
                "ref": row["source_ref"],
                "version": row["source_version"],
                "sha256": row["source_sha256"],
            }
            for row in manifest["rates"]
        ),
    ]
    if manifest["schema_version"] == "fpms.demo-input-bundle/integrated-a-v2":
        selector = manifest["official_fee_selector"]
        expected_sources.append(
            {
                "kind": "OFFICIAL_RATE_BOOK",
                "ref": selector["source_authority"],
                "version": selector["rate_book_version"],
                "sha256": selector["rate_book_sha256"],
            }
        )
        expected_sources.extend(
            {
                "kind": "OFFICIAL_FEE_RATE",
                "ref": fee_code,
                "version": selector["rate_book_version"],
                "sha256": selector["fee_row_sha256s"][fee_code],
            }
            for fee_code in selector["fee_codes"]
        )
    if authority["source_digests"] != expected_sources:
        raise _error("authority source digests do not match the manifest")
    if authority["file_digests"] != expected_file_digests:
        raise _error("authority file digests do not match the manifest")
    if authority_classification == "CUSTOMER_AUTHORIZED":
        try:
            decision_text = decision_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise _error("customer authorization decision must be UTF-8") from exc
        required_bindings = (
            "CUSTOMER_AUTHORIZED",
            manifest_sha256,
            manifest["bundle_id"],
            manifest["bundle_version"],
            manifest["authority"]["decision_version"],
            approved_by,
            approved_at,
            manifest["provenance"]["source_sha256"],
            *(row["source_sha256"] for row in manifest["rates"]),
        )
        if manifest["schema_version"] == "fpms.demo-input-bundle/integrated-a-v2":
            required_bindings += (
                manifest["official_fee_selector"]["rate_book_sha256"],
                *(
                    manifest["official_fee_selector"]["fee_row_sha256s"][
                        fee_code
                    ]
                    for fee_code in manifest["official_fee_selector"]["fee_codes"]
                ),
            )
        if (
            not decision_ref.startswith("docs/product/v8/customer-decisions/")
            or "synthetic" in approved_by.casefold()
            or any(binding not in decision_text for binding in required_bindings)
        ):
            raise _error(
                "customer authorization decision does not bind the exact bundle sources"
            )
    return authority_classification, approved_by, approved_at


def _validate_metadata(
    role: str, metadata_value: Any, *, integrated: bool
) -> DemoEvidenceMetadata:
    expected_keys = _INTEGRATED_METADATA_KEYS if integrated else _METADATA_KEYS
    metadata = _expect_keys(
        metadata_value, expected_keys, f"evidence[{role}].metadata"
    )
    receipt_roles = (
        {"FILING_RECEIPT", "OA_RECEIPT_1", "OA_RECEIPT_2"}
        if integrated
        else {"FILING_RECEIPT", "OA_RECEIPT"}
    )
    oa_roles = {"OA_NOTICE_1", "OA_NOTICE_2"} if integrated else {"OA_NOTICE"}
    grant_roles = (
        {"GRANT_NOTICE_ORIGINAL", "GRANT_NOTICE_REPLACEMENT"}
        if integrated
        else set()
    )
    receipt_role = role in receipt_roles
    oa_notice = role in oa_roles
    grant_notice = role in grant_roles

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
        sequence = 2 if role == "OA_NOTICE_2" else 1
        _exact(
            metadata["oa_sequence"],
            sequence,
            f"evidence[{role}].metadata.oa_sequence",
        )
        _naive_timestamp(metadata["effective_at"], f"evidence[{role}].effective_at")
        _iso_date(metadata["official_due_date"], f"evidence[{role}].official_due_date")
        if metadata["official_due_date_source"] not in {
            "MANUAL_OFFICIAL_NOTICE",
            "IMPORTED_OFFICIAL_NOTICE",
        }:
            raise _error("OA semantic due-date source is invalid")
        _exact(metadata["official_due_date_status"], "CONFIRMED", "OA semantic due-date status")
        _exact(
            metadata["source_template_code"],
            f"DEMO_OA_NOTICE_{sequence}",
            "OA semantic template",
        )
        null_keys = {"received_at", "receipt_kind"}
    elif grant_notice:
        _naive_timestamp(metadata["effective_at"], f"evidence[{role}].effective_at")
        _iso_date(metadata["official_due_date"], f"evidence[{role}].official_due_date")
        _exact(
            metadata["official_due_date_source"],
            "IMPORTED_OFFICIAL_NOTICE",
            f"evidence[{role}].official_due_date_source",
        )
        _exact(
            metadata["official_due_date_status"],
            "CONFIRMED",
            f"evidence[{role}].official_due_date_status",
        )
        replacement = role == "GRANT_NOTICE_REPLACEMENT"
        _exact(
            metadata["source_template_code"],
            "DEMO_GRANT_NOTICE_2" if replacement else "DEMO_GRANT_NOTICE_1",
            f"evidence[{role}].source_template_code",
        )
        _exact(
            metadata["supersedes_role"],
            "GRANT_NOTICE_ORIGINAL" if replacement else None,
            f"evidence[{role}].metadata.supersedes_role",
        )
        null_keys = {"received_at", "receipt_kind", "oa_sequence"}
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
    if integrated and not grant_notice:
        null_keys.add("supersedes_role")
    for key in null_keys:
        if metadata[key] is not None:
            raise _error(f"evidence[{role}].metadata.{key} must be null")
    return DemoEvidenceMetadata(
        effective_at=metadata["effective_at"],
        received_at=metadata["received_at"],
        receipt_kind=metadata["receipt_kind"],
        official_due_date=metadata["official_due_date"],
        official_due_date_source=metadata["official_due_date_source"],
        official_due_date_status=metadata["official_due_date_status"],
        oa_sequence=metadata["oa_sequence"],
        source_template_code=metadata["source_template_code"],
        supersedes_role=metadata.get("supersedes_role"),
    )


def load_demo_bundle(
    bundle_root: Path,
    *,
    expected_manifest_sha256: str,
    expected_authority_sha256: str,
    expected_authority_classification: str,
    repo_root: Path,
    forbidden_roots: tuple[Path, ...] = (),
) -> DemoBundleSnapshot:
    unresolved_root = Path(bundle_root)
    if unresolved_root.is_symlink():
        raise _error("bundle root must not be a symlink")
    root = unresolved_root.resolve()
    repo = Path(repo_root).resolve()
    expected_digest = _matches(
        expected_manifest_sha256, _HASH_RE, "expected manifest digest"
    )
    expected_authority_digest = _matches(
        expected_authority_sha256, _HASH_RE, "expected authority digest"
    )
    if expected_authority_classification not in _AUTHORITY_CLASSIFICATIONS:
        raise _error("expected authority classification is invalid")
    if not root.is_dir():
        raise _error("bundle root must be a real directory")
    if root == repo or repo in root.parents:
        raise _error("bundle root must be outside the repository")
    for forbidden_root in forbidden_roots:
        forbidden = Path(forbidden_root).resolve()
        if root == forbidden or forbidden in root.parents:
            raise _error("bundle root must be outside product and run storage")
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
    supported_schemas = {
        "fpms.demo-input-bundle/v1",
        "fpms.demo-input-bundle/integrated-a-v1",
        "fpms.demo-input-bundle/integrated-a-v2",
    }
    if not isinstance(manifest, dict) or manifest.get("schema_version") not in supported_schemas:
        raise _error("schema_version is unsupported")
    expected_top_keys = (
        _V6_TOP_KEYS
        if isinstance(manifest, dict)
        and manifest.get("schema_version") == "fpms.demo-input-bundle/integrated-a-v2"
        else _TOP_KEYS
    )
    manifest = _expect_keys(manifest, expected_top_keys, "manifest")

    schema_version = manifest["schema_version"]
    if schema_version == "fpms.demo-input-bundle/v1":
        integrated = False
        purpose = "LOCAL_ABC_E2E"
        contract_ref = _CONTRACT_REF
        evidence_roles = _EVIDENCE_ROLES
    elif schema_version == "fpms.demo-input-bundle/integrated-a-v1":
        integrated = True
        purpose = "LOCAL_INTEGRATED_A_E2E"
        contract_ref = _INTEGRATED_CONTRACT_REF
        evidence_roles = _INTEGRATED_EVIDENCE_ROLES
    elif schema_version == "fpms.demo-input-bundle/integrated-a-v2":
        integrated = True
        purpose = "LOCAL_INTEGRATED_A_E2E"
        contract_ref = _V6_CONTRACT_REF
        evidence_roles = _INTEGRATED_EVIDENCE_ROLES
    else:
        raise _error("schema_version is unsupported")
    bundle_id = _matches(manifest["bundle_id"], _BUNDLE_ID_RE, "bundle_id")
    bundle_version = _matches(manifest["bundle_version"], _VERSION_RE, "bundle_version")
    _exact(manifest["classification"], "DEMO_ONLY", "classification")
    authority_classification = _string(
        manifest["authority_classification"],
        "authority_classification",
        maximum=64,
    )
    _exact(
        authority_classification,
        expected_authority_classification,
        "authority classification",
    )
    _exact(manifest["purpose"], purpose, "purpose")
    valid_from = _iso_date(manifest["valid_from"], "valid_from")
    valid_until = _iso_date(manifest["valid_until"], "valid_until")
    local_date = _current_demo_date()
    if valid_until < valid_from or not valid_from <= local_date <= valid_until:
        raise _error(
            "bundle validity does not include the current Asia/Shanghai local date"
        )
    _validate_authority(manifest, repo, contract_ref=contract_ref)
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
    if not isinstance(evidence_rows, list) or [
        row.get("role") for row in evidence_rows if isinstance(row, dict)
    ] != evidence_roles:
        raise _error("evidence roles or order are invalid")
    expected_files = {"manifest.json", "authority.json", template_relative}
    evidence_metadata: list[DemoEvidenceMetadata] = []
    for index, row_value in enumerate(evidence_rows):
        role = evidence_roles[index]
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
        evidence_metadata.append(
            _validate_metadata(role, row["metadata"], integrated=integrated)
        )

    if integrated:
        titles = [row["title_zh_cn"] for row in evidence_rows]
        if any(_CJK_RE.search(title) is None for title in titles):
            raise _error("integrated evidence title_zh_cn must contain Chinese text")
        if len(set(titles)) != len(titles):
            raise _error("integrated evidence titles must be unique")
        critical_rows = evidence_rows[6:12]
        if len({row["sha256"] for row in critical_rows}) != len(critical_rows):
            raise _error("critical evidence hashes must be distinct")
        if len({row["sha256"] for row in evidence_rows}) != len(evidence_rows):
            raise _error("integrated evidence hashes must be unique")
        oa1, receipt1, oa2, receipt2, original_grant, replacement_grant = critical_rows
        if any(oa1[key] == oa2[key] for key in ("path", "sha256")) or any(
            oa1["metadata"][key] == oa2["metadata"][key]
            for key in ("effective_at", "official_due_date", "source_template_code")
        ):
            raise _error("OA2 semantic metadata must be distinct from OA1")
        if any(receipt1[key] == receipt2[key] for key in ("path", "sha256")) or (
            receipt1["metadata"]["received_at"]
            == receipt2["metadata"]["received_at"]
        ):
            raise _error("OA2 receipt semantic metadata must be distinct from OA1")
        if any(
            original_grant[key] == replacement_grant[key]
            for key in ("path", "sha256")
        ) or any(
            original_grant["metadata"][key] == replacement_grant["metadata"][key]
            for key in ("effective_at", "official_due_date", "source_template_code")
        ):
            raise _error("grant replacement semantic metadata must be distinct")

    rates = manifest["rates"]
    service_rates: list[DemoServiceRate] = []
    official_fee_selector: DemoOfficialFeeSelector | None = None
    first_receipt_amount: Decimal | None = None
    if schema_version == "fpms.demo-input-bundle/integrated-a-v2":
        if not isinstance(rates, list) or len(rates) < 2:
            raise _error("rates must contain at least two service rows")
        item_codes: set[str] = set()
        changed_rows = 0
        for index, value in enumerate(rates):
            label = f"rates[{index}]"
            rate = _expect_keys(
                value,
                {
                    "domain",
                    "item_code",
                    "name_zh_cn",
                    "currency",
                    "unit_price",
                    "initial_quantity",
                    "final_quantity",
                    "adjustable",
                    "source_ref",
                    "source_version",
                    "source_sha256",
                    "disclaimer_zh_cn",
                },
                label,
            )
            _exact(rate["domain"], "SERVICE_DEMO_PRICE", f"{label}.domain")
            item_code = _matches(rate["item_code"], _CODE_RE, f"{label}.item_code")
            if item_code in item_codes:
                raise _error("rates item_code values must be unique")
            item_codes.add(item_code)
            initial_quantity = rate["initial_quantity"]
            final_quantity = rate["final_quantity"]
            if type(initial_quantity) is not int or initial_quantity <= 0:
                raise _error(f"{label}.initial_quantity must be positive")
            if type(final_quantity) is not int or final_quantity <= 0:
                raise _error(f"{label}.final_quantity must be positive")
            adjustable = rate["adjustable"]
            if type(adjustable) is not bool:
                raise _error(f"{label}.adjustable must be boolean")
            if not adjustable and final_quantity != initial_quantity:
                raise _error("fixed service rate final_quantity must equal initial_quantity")
            if final_quantity != initial_quantity:
                changed_rows += 1
                if not adjustable:
                    raise _error("changed service rate must be adjustable")
            _exact(rate["currency"], "CNY", f"{label}.currency")
            unit_price = _matches(rate["unit_price"], _AMOUNT_RE, f"{label}.unit_price")
            if unit_price == "0.00":
                raise _error(f"{label}.unit_price must be positive")
            service_rates.append(
                DemoServiceRate(
                    item_code=item_code,
                    name_zh_cn=_string(
                        rate["name_zh_cn"], f"{label}.name_zh_cn", maximum=120
                    ),
                    currency="CNY",
                    unit_price=unit_price,
                    initial_quantity=initial_quantity,
                    final_quantity=final_quantity,
                    adjustable=adjustable,
                    source_ref=_string(
                        rate["source_ref"], f"{label}.source_ref", maximum=240
                    ),
                    source_version=_string(
                        rate["source_version"], f"{label}.source_version", maximum=120
                    ),
                    source_sha256=_matches(
                        rate["source_sha256"], _HASH_RE, f"{label}.source_sha256"
                    ),
                    disclaimer_zh_cn=_string(
                        rate["disclaimer_zh_cn"],
                        f"{label}.disclaimer_zh_cn",
                        maximum=200,
                    ),
                )
            )
        if not any(row.adjustable for row in service_rates):
            raise _error("rates must contain an adjustable service row")
        if not any(not row.adjustable for row in service_rates):
            raise _error("rates must contain a fixed service row")
        if changed_rows != 1:
            raise _error("exactly one adjustable service row must change final_quantity")

        selector = _expect_keys(
            manifest["official_fee_selector"],
            {
                "source_authority",
                "rate_book_version",
                "rate_book_sha256",
                "fee_codes",
                "fee_row_sha256s",
            },
            "official_fee_selector",
        )
        _exact(selector["source_authority"], "CNIPA", "official_fee_selector.source_authority")
        fee_codes = selector["fee_codes"]
        if (
            not isinstance(fee_codes, list)
            or len(fee_codes) < 2
            or len(set(fee_codes)) != len(fee_codes)
            or any(
                not isinstance(code, str) or _FEE_CODE_RE.fullmatch(code) is None
                for code in fee_codes
            )
        ):
            raise _error("official_fee_selector.fee_codes must contain at least two unique codes")
        fee_row_sha256s = selector["fee_row_sha256s"]
        if (
            not isinstance(fee_row_sha256s, dict)
            or set(fee_row_sha256s) != set(fee_codes)
            or any(
                not isinstance(value, str) or _HASH_RE.fullmatch(value) is None
                for value in fee_row_sha256s.values()
            )
        ):
            raise _error(
                "official_fee_selector.fee_row_sha256s must exactly bind fee_codes"
            )
        official_fee_selector = DemoOfficialFeeSelector(
            source_authority="CNIPA",
            rate_book_version=_string(
                selector["rate_book_version"],
                "official_fee_selector.rate_book_version",
                maximum=120,
            ),
            rate_book_sha256=_matches(
                selector["rate_book_sha256"],
                _HASH_RE,
                "official_fee_selector.rate_book_sha256",
            ),
            fee_codes=tuple(fee_codes),
            fee_row_sha256s=tuple(
                (fee_code, fee_row_sha256s[fee_code]) for fee_code in fee_codes
            ),
        )
        receipt_text = _matches(
            manifest["first_receipt_amount"], _AMOUNT_RE, "first_receipt_amount"
        )
        first_receipt_amount = Decimal(receipt_text)
        final_total = sum(
            Decimal(row.unit_price) * row.final_quantity for row in service_rates
        )
        if first_receipt_amount <= 0 or first_receipt_amount >= final_total:
            raise _error("first_receipt_amount must be positive and less than final service total")
    else:
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
        _exact(rate["currency"], "CNY", "rates[0].currency")
        _exact(rate["calc_mode"], "FIXED", "rates[0].calc_mode")
        amount = _matches(rate["amount"], _AMOUNT_RE, "rates[0].amount")
        if amount == "0.00":
            raise _error("rates[0].amount must be positive")
        service_rates.append(
            DemoServiceRate(
                item_code=_matches(rate["item_code"], _CODE_RE, "rates[0].item_code"),
                name_zh_cn=_string(rate["name_zh_cn"], "rates[0].name_zh_cn", maximum=120),
                currency="CNY",
                unit_price=amount,
                initial_quantity=1,
                final_quantity=1,
                adjustable=False,
                source_ref=_string(rate["source_ref"], "rates[0].source_ref", maximum=240),
                source_version=_string(
                    rate["source_version"], "rates[0].source_version", maximum=120
                ),
                source_sha256=_matches(
                    rate["source_sha256"], _HASH_RE, "rates[0].source_sha256"
                ),
                disclaimer_zh_cn=_string(
                    rate["disclaimer_zh_cn"], "rates[0].disclaimer_zh_cn", maximum=200
                ),
            )
        )

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

    expected_file_digests = sorted(
        [
            {"path": template_relative, "sha256": template_row["sha256"]},
            *(
                {"path": row["path"], "sha256": row["sha256"]}
                for row in evidence_rows
            ),
        ],
        key=lambda row: row["path"],
    )
    authority_classification, approved_by, approved_at = _validate_authority_record(
        root,
        expected_authority_sha256=expected_authority_digest,
        manifest=manifest,
        manifest_sha256=expected_digest,
        repo_root=repo,
        expected_file_digests=expected_file_digests,
        expected_authority_classification=expected_authority_classification,
    )

    return DemoBundleSnapshot(
        bundle_root=root,
        bundle_id=bundle_id,
        bundle_version=bundle_version,
        manifest_sha256=expected_digest,
        authority_sha256=expected_authority_digest,
        authority_classification=authority_classification,
        customer_activation_eligible=authority_classification == "CUSTOMER_AUTHORIZED",
        approved_by=approved_by,
        approved_at=approved_at,
        local_date=local_date,
        template=DemoTemplate(
            template_code=template_code,
            path=template_path,
            sha256=template_row["sha256"],
            required_variables=tuple(variables),
        ),
        service_rates=tuple(service_rates),
        official_fee_selector=official_fee_selector,
        first_receipt_amount=first_receipt_amount,
        readiness=(
            "TECHNICAL_REHEARSAL_INPUT_READY"
            if authority_classification == "SYNTHETIC_TEST_ONLY"
            else "CUSTOMER_INPUT_VALIDATED"
        ),
        schema_version=schema_version,
        evidence_roles=tuple(evidence_roles),
        evidence=tuple(
            DemoEvidence(
                role=row["role"],
                title_zh_cn=row["title_zh_cn"],
                path=root / row["path"],
                sha256=row["sha256"],
                metadata=evidence_metadata[index],
            )
            for index, row in enumerate(evidence_rows)
        ),
    )
