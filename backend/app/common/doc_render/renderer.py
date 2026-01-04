from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docxtpl import DocxTemplate


class DocxRenderer:
    def render_docx_bytes(self, template_path: str, context: dict) -> bytes:
        path = Path(template_path)
        if path.suffix != ".docx":
            raise ValueError("template_path must end with .docx")
        if not path.exists():
            raise FileNotFoundError(str(path))

        template = DocxTemplate(str(path))
        template.render(context)
        buffer = BytesIO()
        template.save(buffer)
        return buffer.getvalue()
