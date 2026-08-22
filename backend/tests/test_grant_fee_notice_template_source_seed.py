from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents import service as document_service
from app.modules.documents.models import DocTemplate
from app.modules.documents.service import resolve_document_template_render_source
from app.modules.templates.models import Template
from app.modules.templates.render import TemplateRenderer
from scripts import seed_dev


def test_seed_doc_templates_configures_renderable_grant_fee_notice_source(
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    storage_dir = tmp_path / "storage"
    monkeypatch.setattr(seed_dev, "BASE_DIR", tmp_path)
    monkeypatch.setattr(document_service, "_backend_storage_dir", lambda: storage_dir)

    with session_factory() as db:
        for source in db.execute(
            select(Template).where(
                Template.group == "DOC_TEMPLATE",
                Template.name == "GRANT_FEE_NOTICE",
            )
        ).scalars():
            db.delete(source)
        existing_doc_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "GRANT_FEE_NOTICE")
        ).scalar_one_or_none()
        if existing_doc_template is not None:
            db.delete(existing_doc_template)
        db.commit()

        assert seed_dev.seed_grant_fee_notice_template_source(db) is True
        db.flush()
        assert seed_dev.seed_grant_fee_notice_template_source(db) is False
        db.flush()

        doc_template = db.execute(
            select(DocTemplate).where(DocTemplate.code == "GRANT_FEE_NOTICE")
        ).scalar_one()
        sources = (
            db.execute(
                select(Template).where(
                    Template.group == "DOC_TEMPLATE",
                    Template.name == "GRANT_FEE_NOTICE",
                    Template.enabled.is_(True),
                )
            )
            .scalars()
            .all()
        )

        assert doc_template.name == "授权费通知函"
        assert doc_template.direction == "OUT"
        assert doc_template.enabled is True
        assert len(sources) == 1
        assert sources[0].file_path == "templates/grant_fee_notice.docx"

        resolved_source, resolved_path = resolve_document_template_render_source(
            db,
            doc_template=doc_template,
        )

    assert resolved_source.name == "GRANT_FEE_NOTICE"
    assert Path(resolved_path).is_file()

    rendered = TemplateRenderer().render_template_docx_bytes(
        template_path=resolved_path,
        context={
            "case_no": "RUI202605100035",
            "grant_fee_task": {
                "due_date": "2026-07-09",
                "gov_fee_amt": "0.00",
                "service_fee_amt": "0.00",
                "currency": "CNY",
            },
        },
    )

    assert rendered.startswith(b"PK")
