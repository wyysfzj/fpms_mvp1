from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

PACK_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACK_ROOT.parent


def build_audit() -> dict[str, Any]:
    cases = _load_cases()
    case_ids = {case["id"] for case in cases}
    backend_routes = _extract_backend_routes()
    frontend_routes = _extract_frontend_routes()
    pytest_handlers = _extract_pytest_handlers()
    playwright_handlers = _extract_playwright_handlers()
    pytest_real = {
        case_id
        for case_id, handler in pytest_handlers.items()
        if not handler["skeleton"]
    }
    playwright_real = {
        case_id
        for case_id, handler in playwright_handlers.items()
        if not handler["skeleton"]
    }
    handler_ids = set(pytest_handlers) | set(playwright_handlers)
    real_handler_ids = pytest_real | playwright_real
    rough_backend_uncovered = _rough_uncovered_backend_routes(backend_routes)
    rough_frontend_uncovered = _rough_uncovered_frontend_routes(frontend_routes)

    return {
        "summary": {
            "canonical_case_count": len(cases),
            "backend_route_count": len(backend_routes),
            "frontend_route_count": len(frontend_routes),
            "pytest_handler_count": len(pytest_handlers),
            "pytest_real_handler_count": len(pytest_real),
            "playwright_handler_count": len(playwright_handlers),
            "playwright_real_handler_count": len(playwright_real),
            "cases_without_any_handler_count": len(case_ids - handler_ids),
            "cases_without_real_handler_count": len(case_ids - real_handler_ids),
            "rough_backend_uncovered_route_count": len(rough_backend_uncovered),
            "rough_frontend_uncovered_route_count": len(rough_frontend_uncovered),
        },
        "case_counts_by_wave": dict(
            sorted(Counter(case["wave"] for case in cases).items())
        ),
        "case_counts_by_priority": dict(
            sorted(Counter(case["priority"] for case in cases).items())
        ),
        "pytest_real_counts_by_wave": _count_handlers_by_wave(cases, pytest_real),
        "playwright_real_counts_by_wave": _count_handlers_by_wave(
            cases, playwright_real
        ),
        "cases_without_any_handler": sorted(case_ids - handler_ids),
        "cases_without_real_handler": sorted(case_ids - real_handler_ids),
        "rough_backend_uncovered_routes": rough_backend_uncovered,
        "rough_frontend_uncovered_routes": rough_frontend_uncovered,
    }


def validate_audit(audit: dict[str, Any]) -> list[str]:
    summary = audit["summary"]
    errors: list[str] = []
    if summary["canonical_case_count"] <= 0:
        errors.append("No canonical testcases found")
    if summary["backend_route_count"] <= 0:
        errors.append("No backend routes found")
    if summary["frontend_route_count"] <= 0:
        errors.append("No frontend routes found")
    if summary["cases_without_any_handler_count"] != 0:
        missing = ", ".join(audit["cases_without_any_handler"])
        errors.append(
            f"Canonical cases without pytest or Playwright handler: {missing}"
        )
    return errors


def _load_cases() -> list[dict[str, Any]]:
    with (PACK_ROOT / "data" / "testcases" / "all_testcases.yaml").open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)["testcases"]


def _extract_backend_routes() -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for path in sorted(
        (PROJECT_ROOT / "backend" / "app" / "modules").glob("**/api.py")
    ):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for decorator in node.decorator_list:
                route = _extract_route_decorator(path, node.name, decorator)
                if route is not None:
                    routes.append(route)
    return routes


def _extract_route_decorator(
    path: Path,
    function_name: str,
    decorator: ast.expr,
) -> dict[str, Any] | None:
    if not isinstance(decorator, ast.Call):
        return None
    if not isinstance(decorator.func, ast.Attribute):
        return None
    if not isinstance(decorator.func.value, ast.Name):
        return None
    if decorator.func.value.id != "router":
        return None
    if decorator.func.attr not in {"get", "post", "put", "delete", "patch"}:
        return None

    route_path = None
    if decorator.args and isinstance(decorator.args[0], ast.Constant):
        route_path = decorator.args[0].value

    summary = None
    for keyword in decorator.keywords:
        if keyword.arg == "summary" and isinstance(keyword.value, ast.Constant):
            summary = keyword.value.value

    return {
        "method": decorator.func.attr.upper(),
        "path": route_path,
        "summary": summary,
        "module": _backend_module_name(path),
        "file": str(path.relative_to(PROJECT_ROOT)),
        "function": function_name,
    }


def _backend_module_name(path: Path) -> str:
    parts = path.relative_to(PROJECT_ROOT).parts
    if len(parts) >= 5 and parts[2] == "modules" and parts[3] == "masterdata":
        return f"masterdata/{parts[4]}"
    if len(parts) >= 4 and parts[2] == "modules":
        return parts[3]
    return str(path.relative_to(PROJECT_ROOT))


def _extract_frontend_routes() -> list[dict[str, Any]]:
    router_path = PROJECT_ROOT / "frontend" / "src" / "router" / "index.ts"
    text = router_path.read_text(encoding="utf-8")
    routes = [
        {
            "path": match.group(1),
            "name": match.group(2),
            "component": match.group(3),
        }
        for match in re.finditer(
            r"\{\s*path:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'\s*,\s*"
            r"component:\s*\(\)\s*=>\s*import\('([^']+)'\)",
            text,
        )
    ]
    if "{ path: '/login'" in text:
        routes.append(
            {
                "path": "/login",
                "name": "login",
                "component": "../modules/auth/pages/Login.vue",
            }
        )
    return routes


def _extract_pytest_handlers() -> dict[str, dict[str, Any]]:
    handlers: dict[str, dict[str, Any]] = {}
    for path in sorted((PACK_ROOT / "pytest_python" / "handlers").glob("wave_*.py")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(
            r'"(TC-[A-Z0-9-]+)"\s*:\s*(handle_tc_[a-z0-9_]+)', text
        ):
            case_id = match.group(1)
            function_name = match.group(2)
            function_match = re.search(
                r"(?s)(@skeleton_case\s*)?def " + re.escape(function_name) + r"\(",
                text,
            )
            handlers[case_id] = {
                "file": str(path.relative_to(PROJECT_ROOT)),
                "skeleton": bool(function_match and function_match.group(1)),
            }
    return handlers


def _extract_playwright_handlers() -> dict[str, dict[str, Any]]:
    handlers: dict[str, dict[str, Any]] = {}
    handlers_dir = PACK_ROOT / "playwright_ts" / "src" / "handlers"
    for path in sorted(handlers_dir.glob("wave*.ts")):
        text = path.read_text(encoding="utf-8")
        skeleton_consts = set(
            re.findall(r"const\s+(TC_[A-Z0-9_]+)\s*=\s*markSkeleton", text)
        )
        for match in re.finditer(r'"(TC-[A-Z0-9-]+)"\s*:\s*(TC_[A-Z0-9_]+)', text):
            case_id = match.group(1)
            const_name = match.group(2)
            handlers[case_id] = {
                "file": str(path.relative_to(PROJECT_ROOT)),
                "skeleton": const_name in skeleton_consts,
            }
    return handlers


def _count_handlers_by_wave(
    cases: list[dict[str, Any]],
    handler_case_ids: set[str],
) -> dict[str, int]:
    waves = {case["id"]: case["wave"] for case in cases}
    return dict(
        sorted(
            Counter(
                waves[case_id] for case_id in handler_case_ids if case_id in waves
            ).items()
        )
    )


def _rough_uncovered_backend_routes(
    routes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    skeleton_text = _read_skeleton_source_text()
    uncovered: list[dict[str, Any]] = []
    for route in routes:
        route_path = route["path"] or ""
        candidates = {
            route_path,
            re.sub(r"\{[^}]+\}", "", route_path).rstrip("/"),
            re.sub(r"\{[^}]+\}", "", route_path),
        }
        candidates.update(
            chunk
            for chunk in re.split(r"\{[^}]+\}", route_path)
            if chunk and chunk != "/"
        )
        if not any(
            candidate and candidate in skeleton_text for candidate in candidates
        ):
            uncovered.append(route)
    return uncovered


def _rough_uncovered_frontend_routes(
    routes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    playwright_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (PACK_ROOT / "playwright_ts" / "src").glob("**/*.ts")
    )
    static_route_smoke_exists = (
        PACK_ROOT
        / "playwright_ts"
        / "src"
        / "tests"
        / "current-static-route-smoke.spec.ts"
    ).exists()
    uncovered: list[dict[str, Any]] = []
    for route in routes:
        route_path = route["path"]
        normalized = route_path if route_path.startswith("/") else f"/{route_path}"
        literal = re.sub(r":[^/]+", "", normalized).rstrip("/") or "/"
        component_name = route["component"].split("/")[-1].replace(".vue", "")
        if (
            static_route_smoke_exists
            and ":" not in route_path
            and normalized != "/login"
        ):
            continue
        if not (
            normalized in playwright_text
            or literal in playwright_text
            or component_name in playwright_text
        ):
            uncovered.append(route)
    return uncovered


def _read_skeleton_source_text() -> str:
    files = list((PACK_ROOT / "pytest_python").glob("**/*.py"))
    files.extend((PACK_ROOT / "playwright_ts" / "src").glob("**/*.ts"))
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in files
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json", action="store_true", help="Print the full audit as JSON"
    )
    parser.add_argument(
        "--fail-on-gaps",
        action="store_true",
        help="Fail when known real-handler or rough route/page gaps remain",
    )
    args = parser.parse_args()

    audit = build_audit()
    errors = validate_audit(audit)
    if args.fail_on_gaps:
        summary = audit["summary"]
        if summary["cases_without_real_handler_count"]:
            errors.append(
                "Canonical cases without real pytest or Playwright handler remain"
            )
        if summary["rough_backend_uncovered_route_count"]:
            errors.append("Rough backend route coverage gaps remain")
        if summary["rough_frontend_uncovered_route_count"]:
            errors.append("Rough frontend route coverage gaps remain")

    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        print("Current implementation coverage audit")
        for key, value in audit["summary"].items():
            print(f"{key}: {value}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
