from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile


def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def safe_join(base_dir: str, *parts: str) -> str:
    """
    Safely join path parts preventing directory traversal.
    Raises ValueError if result escapes base_dir.
    """
    base = Path(base_dir).resolve()
    target = (base / Path(*parts)).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"Path traversal detected: {parts}") from exc

    return str(target)


def save_upload_file(upload_file: UploadFile, dest_path: str) -> tuple[str, int]:
    """
    Save FastAPI UploadFile to dest_path.
    Returns (mime_type, size_bytes).
    """
    ensure_dir(str(Path(dest_path).parent))

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    size = Path(dest_path).stat().st_size
    mime_type = upload_file.content_type or "application/octet-stream"

    return (mime_type, size)
