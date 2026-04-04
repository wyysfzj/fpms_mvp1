from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.modules.documents.models import DocTemplate
from app.modules.documents.service import resolve_document_template_render_source
from app.modules.templates.models import Template


def _unique_code(prefix: str = "DOCWIZ_STEP5") -> str:
    return f"{prefix}_{uuid4().hex[:8].upper()}"


def _create_doc_template(db, *, code: str) -> DocTemplate:
    template = DocTemplate(
        id=str(uuid4()),
        code=code,
        name=f"DocTemplate {code}",
        direction="IN",
        enabled=True,
    )
    db.add(template)
    db.flush()
    return template


def _create_template(db, *, name: str, file_path: str, enabled: bool = True) -> Template:
    template = Template(
        id=str(uuid4()),
        name=name,
        group="DOC_TEMPLATE",
        language="zh-CN",
        file_path=file_path,
        enabled=enabled,
    )
    db.add(template)
    db.flush()
    return template


def test_resolve_document_template_render_source_success(
    session_factory: sessionmaker, tmp_path: Path
) -> None:
    template_file = tmp_path / "oa_notice.docx"
    template_file.write_bytes(b"docx-bytes")

    with session_factory() as db:
        doc_code = _unique_code()
        doc_template = _create_doc_template(db, code=doc_code)
        source_template = _create_template(
            db,
            name=doc_code,
            file_path=str(template_file),
        )
        db.commit()

        resolved_template, resolved_path = resolve_document_template_render_source(
            db, doc_template=doc_template
        )

        assert resolved_template.id == source_template.id
        assert resolved_path == str(template_file)


def test_resolve_document_template_render_source_not_found(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        doc_template = _create_doc_template(db, code=_unique_code())
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            resolve_document_template_render_source(db, doc_template=doc_template)

        assert exc_info.value.code == "DOCUMENT_TEMPLATE_SOURCE_NOT_FOUND"
        assert exc_info.value.status_code == 409


def test_resolve_document_template_render_source_conflict(
    session_factory: sessionmaker, tmp_path: Path
) -> None:
    template_file_one = tmp_path / "one.docx"
    template_file_two = tmp_path / "two.docx"
    template_file_one.write_bytes(b"one")
    template_file_two.write_bytes(b"two")

    with session_factory() as db:
        doc_code = _unique_code()
        doc_template = _create_doc_template(db, code=doc_code)
        _create_template(db, name=doc_code, file_path=str(template_file_one))
        _create_template(db, name=doc_code, file_path=str(template_file_two))
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            resolve_document_template_render_source(db, doc_template=doc_template)

        assert exc_info.value.code == "DOCUMENT_TEMPLATE_SOURCE_CONFLICT"
        assert exc_info.value.status_code == 409


def test_resolve_document_template_render_source_file_missing(
    session_factory: sessionmaker, tmp_path: Path
) -> None:
    missing_path = tmp_path / "missing.docx"

    with session_factory() as db:
        doc_code = _unique_code()
        doc_template = _create_doc_template(db, code=doc_code)
        _create_template(db, name=doc_code, file_path=str(missing_path))
        db.commit()

        with pytest.raises(BusinessError) as exc_info:
            resolve_document_template_render_source(db, doc_template=doc_template)

        assert exc_info.value.code == "DOCUMENT_TEMPLATE_FILE_NOT_FOUND"
        assert exc_info.value.status_code == 409
