from __future__ import annotations

import re
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.modules.rbac.service import ROLE_PERMISSIONS  # noqa: E402

_PERM_PATTERN = re.compile(r"require_perm\(\s*['\"]([^'\"]+)['\"]\s*\)")


def _scan_permission_codes(base_dir: Path) -> set[str]:
    codes: set[str] = set()
    for path in base_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        codes.update(_PERM_PATTERN.findall(text))
    return codes


def _print_section(title: str, lines: list[str]) -> None:
    print(title)
    for line in lines:
        print(line)


def main() -> None:
    app_dir = _BACKEND_DIR / "app"
    all_codes = sorted(_scan_permission_codes(app_dir))

    admin_codes = set(ROLE_PERMISSIONS.get("Admin", []))
    admin_missing = sorted(set(all_codes) - admin_codes)

    _print_section("ALL_CODES", all_codes)
    _print_section("ADMIN_MISSING", admin_missing)

    print("ROLE_MISSING")
    for role in sorted(role for role in ROLE_PERMISSIONS if role != "Admin"):
        role_missing = sorted(set(all_codes) - set(ROLE_PERMISSIONS[role]))
        print(f"[{role}]")
        for code in role_missing:
            print(code)


if __name__ == "__main__":
    main()
