from __future__ import annotations

from pathlib import Path

from app.common.doc_render.renderer import DocxRenderer


class TemplateRenderer:
    def render_template_docx_bytes(self, *, template_path: str, context: dict) -> bytes:
        path = Path(template_path)
        if path.suffix != ".docx":
            raise ValueError("template_path must end with .docx")
        if not path.exists():
            raise FileNotFoundError(str(path))

        renderer = DocxRenderer()
        return renderer.render_docx_bytes(str(path), context)
