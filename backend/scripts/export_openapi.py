from __future__ import annotations

import json
from pathlib import Path

from app.main import app

OUT = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    schema = app.openapi()
    OUT.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OpenAPI exported to: {OUT}")


if __name__ == "__main__":
    main()
