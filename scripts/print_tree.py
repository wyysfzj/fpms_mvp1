from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def walk(path: Path, prefix: str = ""):
    items = sorted(
        [p for p in path.iterdir() if p.name not in {".git", "node_modules", ".venv"}],
        key=lambda p: (p.is_file(), p.name.lower()),
    )
    for i, p in enumerate(items):
        last = i == len(items) - 1
        branch = "└── " if last else "├── "
        print(prefix + branch + p.name)
        if p.is_dir():
            walk(p, prefix + ("    " if last else "│   "))


if __name__ == "__main__":
    print(ROOT.name)
    walk(ROOT)
