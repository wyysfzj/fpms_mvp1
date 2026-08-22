from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html import escape
from pathlib import Path

from app.common.doc_render.renderer import DocxRenderer
from app.modules.documents.letter_context import FormatLetterContextResult

_DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_STORAGE_ROOT = (Path(__file__).resolve().parents[3] / "storage").resolve()
_TEMPLATE_ROOT = (_STORAGE_ROOT / "templates").resolve()
_TEMPLATE_PATH_ERROR = "template_file_path must identify an existing file under storage/templates"


@dataclass(frozen=True, slots=True)
class RenderedFormatLetter:
    file_name: str
    media_type: str
    content: bytes
    content_hash: str


def _resolve_template_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(_TEMPLATE_PATH_ERROR)
    resolved = (_STORAGE_ROOT / path).resolve()
    if not resolved.is_relative_to(_TEMPLATE_ROOT) or not resolved.is_file():
        raise ValueError(_TEMPLATE_PATH_ERROR)
    return resolved


def render_format_letter(context_result: FormatLetterContextResult) -> RenderedFormatLetter:
    context = dict(context_result.context)
    render_context = {
        key: escape(value) if isinstance(value, str) else value for key, value in context.items()
    }
    content = DocxRenderer().render_docx_bytes(
        str(_resolve_template_path(context_result.template_file_path)),
        render_context,
    )
    return RenderedFormatLetter(
        file_name=f"{context['case_no']}-给{context['applicant_names_text']}的邮件.docx",
        media_type=_DOCX_MEDIA_TYPE,
        content=content,
        content_hash=f"sha256:{hashlib.sha256(content).hexdigest()}",
    )


__all__ = ("RenderedFormatLetter", "render_format_letter")
