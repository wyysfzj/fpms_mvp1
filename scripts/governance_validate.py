#!/usr/bin/env python3
"""Validate a staged FPMS governance kernel, manifest, modules, and rule ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


RULE_ID_PATTERN = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+"
RULE_DECLARATION = re.compile(rf"^### Rule ({RULE_ID_PATTERN}) — .+$")
RULE_REFERENCE = re.compile(rf"^Rule-Ref: ({RULE_ID_PATTERN})$")
HEADING = re.compile(r"^(#{1,4})\s+(.+)$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TAG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TABLE_LINE = re.compile(r"^\s*\|.*\|\s*$")
THEMATIC_RULE = re.compile(r"^\s*(?:-{3,}|—{3,})\s*$")
INVENTORY_ALGORITHM = "markdown-logical-units-v1"

REQUIRED_FAMILIES = {
    "GOV-API-UI",
    "GOV-AUTH",
    "GOV-BEHAVIOR",
    "GOV-CUSTOMER",
    "GOV-DATA",
    "GOV-EVIDENCE",
    "GOV-FEE",
    "GOV-LEGACY",
    "GOV-LIFECYCLE",
    "GOV-LINEAGE",
    "GOV-LINT",
    "GOV-LIVENESS",
    "GOV-MULTIAGENT",
    "GOV-RELEASE",
    "GOV-REPORT",
    "GOV-RISK-RUNTIME",
    "GOV-RUNBOOK",
    "GOV-SCOPE",
    "GOV-SKILLS",
    "GOV-SOURCE",
    "GOV-SQLITE",
}
SELECTOR_FIELDS = {"risk_any", "task_path_any", "closure_tag_any"}
MANIFEST_FIELDS = {
    "schema_version",
    "active_version",
    "adapter_version",
    "activation_task",
    "required_closure_tags",
    "rule_owners",
    "modules",
}
MODULE_FIELDS = {"path", "always", "selectors"}


class GovernanceError(ValueError):
    """Raised when staged governance fails closed."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GovernanceError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise GovernanceError(f"invalid {label}: top level must be an object")
    return value


def _safe_posix_path(value: object, *, label: str, allow_glob: bool = False) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise GovernanceError(f"unsafe {label}: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise GovernanceError(f"unsafe {label}: {value!r}")
    if not allow_glob and any(character in value for character in "*?[]{}"):
        raise GovernanceError(f"unsafe {label}: {value!r}")
    if allow_glob:
        if any(character in value for character in "?[]{}") or "***" in value:
            raise GovernanceError(f"unsupported glob: {value}")
    return value


def _ensure_not_symlink(repo_root: Path, relative_path: str) -> Path:
    current = repo_root
    for part in PurePosixPath(relative_path).parts:
        current = current / part
        if current.is_symlink():
            raise GovernanceError(f"symlink module path: {relative_path}")
    return current


def _sorted_unique_strings(value: object, *, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) for item in value)
    ):
        raise GovernanceError(f"{label} must be a non-empty string array")
    if value != sorted(set(value)):
        raise GovernanceError(f"{label} must be sorted and unique")
    return value


def _validate_selector(selector: object) -> dict[str, list[str]]:
    if not isinstance(selector, dict) or not selector:
        raise GovernanceError("selector must be a non-empty object")
    unknown = set(selector) - SELECTOR_FIELDS
    if unknown:
        raise GovernanceError(f"unknown selector field: {sorted(unknown)[0]}")
    validated: dict[str, list[str]] = {}
    for field, raw_values in selector.items():
        values = _sorted_unique_strings(raw_values, label=field)
        if field == "risk_any":
            if any(value not in {"LOW", "MEDIUM", "HIGH"} for value in values):
                raise GovernanceError("selector risk_any contains an invalid risk")
        elif field == "closure_tag_any":
            if any(not TAG.fullmatch(value) for value in values):
                raise GovernanceError(
                    "selector closure_tag_any contains an invalid tag"
                )
        else:
            for value in values:
                _safe_posix_path(value, label="task path glob", allow_glob=True)
        validated[field] = values
    return validated


def _validate_manifest(
    manifest: dict[str, Any], repo_root: Path
) -> list[dict[str, Any]]:
    if set(manifest) != MANIFEST_FIELDS:
        missing = sorted(MANIFEST_FIELDS - set(manifest))
        extra = sorted(set(manifest) - MANIFEST_FIELDS)
        raise GovernanceError(
            f"invalid manifest fields: missing={missing}, extra={extra}"
        )
    if manifest["schema_version"] != 2:
        raise GovernanceError("manifest schema_version must be 2")
    if manifest["active_version"] != manifest["adapter_version"]:
        raise GovernanceError("version mismatch between active governance and adapter")
    if (
        not isinstance(manifest["activation_task"], str)
        or not manifest["activation_task"]
    ):
        raise GovernanceError("manifest activation_task is required")

    required_tags = _sorted_unique_strings(
        manifest["required_closure_tags"], label="required_closure_tags"
    )
    if any(not TAG.fullmatch(tag) for tag in required_tags):
        raise GovernanceError("required_closure_tags contains an invalid tag")
    if not isinstance(manifest["rule_owners"], dict) or not manifest["rule_owners"]:
        raise GovernanceError("manifest rule_owners must be a non-empty object")

    modules = manifest["modules"]
    if not isinstance(modules, list) or not modules:
        raise GovernanceError("manifest modules must be a non-empty array")
    seen_paths: set[str] = set()
    routed_tags: set[str] = set()
    validated_modules: list[dict[str, Any]] = []
    for module in modules:
        if not isinstance(module, dict) or set(module) != MODULE_FIELDS:
            raise GovernanceError(
                "module must contain only path, always, and selectors"
            )
        path = _safe_posix_path(module["path"], label="module path")
        if path in seen_paths:
            raise GovernanceError(f"duplicate module path: {path}")
        seen_paths.add(path)
        module_path = _ensure_not_symlink(repo_root, path)
        if not module_path.is_file():
            raise GovernanceError(f"missing module: {path}")
        if not isinstance(module["always"], bool) or not isinstance(
            module["selectors"], list
        ):
            raise GovernanceError(f"invalid selector configuration for {path}")
        if module["always"] and module["selectors"]:
            raise GovernanceError("always module must have empty selectors")
        if not module["always"] and not module["selectors"]:
            raise GovernanceError("conditional module requires selectors")
        selectors = [_validate_selector(selector) for selector in module["selectors"]]
        for selector in selectors:
            routed_tags.update(selector.get("closure_tag_any", []))
        validated_modules.append(
            {"path": path, "always": module["always"], "selectors": selectors}
        )

    for tag in required_tags:
        if tag not in routed_tags:
            raise GovernanceError(f"required closure tag has no module: {tag}")

    module_dir = repo_root / "docs/agents"
    actual_modules = {
        path.relative_to(repo_root).as_posix()
        for path in module_dir.glob("*.md")
        if path.is_file() or path.is_symlink()
    }
    undeclared = sorted(actual_modules - seen_paths)
    if undeclared:
        raise GovernanceError(f"undeclared normative module: {undeclared[0]}")
    return validated_modules


def _fence_marker(line: str) -> str | None:
    stripped = line.lstrip()
    if stripped.startswith("```"):
        return "```"
    if stripped.startswith("~~~"):
        return "~~~"
    return None


def inventory_markdown_units(
    text: str, path: str = "AGENTS.md"
) -> list[dict[str, Any]]:
    """Return deterministic, non-overlapping authoritative Markdown units."""
    lines = text.splitlines()
    units: list[dict[str, Any]] = []

    def add(kind: str, start_index: int, end_index: int) -> None:
        unit_text = "\n".join(lines[start_index:end_index])
        start_line = start_index + 1
        end_line = end_index
        units.append(
            {
                "current_location": f"{path}:{start_line}-{end_line}:{kind}",
                "unit_kind": kind,
                "start_line": start_line,
                "end_line": end_line,
                "text_sha256": _sha256(unit_text.encode("utf-8")),
                "text": unit_text,
            }
        )

    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        marker = _fence_marker(line)
        if marker is not None:
            start = index
            index += 1
            while index < len(lines) and not lines[index].lstrip().startswith(marker):
                index += 1
            if index == len(lines):
                raise GovernanceError(f"unclosed Markdown fence: {path}")
            index += 1
            add("code_fence", start, index)
            continue

        if HEADING.fullmatch(line):
            add("heading", index, index + 1)
            index += 1
            continue
        if THEMATIC_RULE.fullmatch(line):
            add("thematic_rule", index, index + 1)
            index += 1
            continue
        if TABLE_LINE.fullmatch(line):
            start = index
            index += 1
            while index < len(lines) and TABLE_LINE.fullmatch(lines[index]):
                index += 1
            add("table", start, index)
            continue

        kind = "list" if LIST_ITEM.match(line) else "prose"
        start = index
        index += 1
        while index < len(lines) and lines[index].strip():
            next_line = lines[index]
            if (
                _fence_marker(next_line) is not None
                or HEADING.fullmatch(next_line)
                or THEMATIC_RULE.fullmatch(next_line)
                or TABLE_LINE.fullmatch(next_line)
                or (kind == "prose" and LIST_ITEM.match(next_line))
            ):
                break
            index += 1
        add(kind, start, index)
    return units


def _validate_links(
    path: str,
    text: str,
    repo_root: Path,
    manifest_candidate: Path,
) -> None:
    for match in MARKDOWN_LINK.finditer(text):
        target = match.group(1).split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        target_path = _safe_posix_path(target, label="internal link")
        resolved = (
            manifest_candidate
            if target_path == "docs/agents/manifest.json"
            else repo_root / target_path
        )
        if not resolved.is_file():
            raise GovernanceError(f"broken internal link in {path}: {target}")


def _collect_rules(
    documents: dict[str, str],
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    declarations: dict[str, str] = {}
    references: list[tuple[str, str]] = []
    for path, text in documents.items():
        declared_here: set[str] = set()
        referenced_here: list[str] = []
        for unit in inventory_markdown_units(text, path):
            if unit["unit_kind"] == "code_fence":
                continue
            for line in unit["text"].splitlines():
                if line.startswith("### Rule "):
                    match = RULE_DECLARATION.fullmatch(line)
                    if match is None:
                        raise GovernanceError(
                            f"invalid Rule declaration in {path}: {line}"
                        )
                    rule_id = match.group(1)
                    if rule_id in declarations:
                        raise GovernanceError(f"rule {rule_id} declared more than once")
                    declarations[rule_id] = path
                    declared_here.add(rule_id)
                elif line.startswith("Rule-Ref:"):
                    match = RULE_REFERENCE.fullmatch(line)
                    if match is None:
                        raise GovernanceError(f"invalid Rule-Ref in {path}: {line}")
                    referenced_here.append(match.group(1))
                    references.append((path, match.group(1)))
        self_references = declared_here.intersection(referenced_here)
        if self_references:
            raise GovernanceError(
                f"module {path} references its own rule: {sorted(self_references)[0]}"
            )
    for path, rule_id in references:
        if rule_id not in declarations:
            raise GovernanceError(f"undefined Rule-Ref in {path}: {rule_id}")
    return declarations, references


def _validate_owners(manifest: dict[str, Any], declarations: dict[str, str]) -> None:
    owners = manifest["rule_owners"]
    if set(owners) != set(declarations):
        missing = sorted(set(declarations) - set(owners))
        extra = sorted(set(owners) - set(declarations))
        raise GovernanceError(
            f"rule owner inventory mismatch: missing={missing}, extra={extra}"
        )
    for rule_id, declared_path in declarations.items():
        if owners[rule_id] != declared_path:
            raise GovernanceError(
                f"owner mismatch for {rule_id}: {owners[rule_id]} != {declared_path}"
            )


def _glob_pattern_covers(broad: str, narrow: str) -> bool:
    if broad == narrow or broad == "**":
        return True
    if broad.endswith("/**"):
        prefix = broad[:-3].rstrip("/")
        return narrow == prefix or narrow.startswith(prefix + "/")
    return False


def _selector_covers(
    module_selector: dict[str, list[str]], ledger_selector: dict[str, list[str]]
) -> bool:
    if not set(module_selector).issubset(ledger_selector):
        return False
    for field, module_values in module_selector.items():
        ledger_values = ledger_selector[field]
        if field == "task_path_any":
            if not all(
                any(_glob_pattern_covers(broad, narrow) for broad in module_values)
                for narrow in ledger_values
            ):
                return False
        elif not set(module_values).issuperset(ledger_values):
            return False
    return True


def _validate_ledger_selector(
    raw_selector: object,
    owner_path: str,
    modules: list[dict[str, Any]],
    label: str,
) -> None:
    is_always = (
        isinstance(raw_selector, dict)
        and set(raw_selector) == {"always"}
        and raw_selector["always"] is True
    )
    if is_always:
        selector: dict[str, list[str]] | None = None
    else:
        if not isinstance(raw_selector, dict) or "always" in raw_selector:
            raise GovernanceError(f"invalid ledger selector for {label}")
        try:
            selector = _validate_selector(raw_selector)
        except GovernanceError as exc:
            raise GovernanceError(
                f"invalid ledger selector for {label}: {exc}"
            ) from exc

    if owner_path == "AGENTS.md":
        if not is_always:
            raise GovernanceError(
                f"ledger selector does not route to owner AGENTS.md for {label}"
            )
        return

    owner_module = next(
        (module for module in modules if module["path"] == owner_path), None
    )
    if owner_module is None:
        raise GovernanceError(f"ledger selector owner module is missing for {label}")
    if owner_module["always"]:
        return
    if selector is None or not any(
        _selector_covers(module_selector, selector)
        for module_selector in owner_module["selectors"]
    ):
        raise GovernanceError(
            f"ledger selector does not route to owner {owner_path} for {label}"
        )


def _validate_ledger(
    ledger: dict[str, Any],
    repo_root: Path,
    declarations: dict[str, str],
    manifest: dict[str, Any],
    modules: list[dict[str, Any]],
) -> None:
    if ledger.get("schema_version") != 1:
        raise GovernanceError("disposition ledger schema_version must be 1")
    source = ledger.get("source")
    if not isinstance(source, dict) or source.get("path") != "AGENTS.md":
        raise GovernanceError("disposition ledger source must be AGENTS.md")
    current_bytes = (repo_root / "AGENTS.md").read_bytes()
    current_text = current_bytes.decode("utf-8")
    if source.get("sha256") != _sha256(current_bytes):
        raise GovernanceError("disposition ledger source hash mismatch")
    if source.get("line_count") != len(current_text.splitlines()):
        raise GovernanceError("disposition ledger source line count mismatch")
    logical_units = inventory_markdown_units(current_text)
    if source.get("inventory_algorithm") != INVENTORY_ALGORITHM:
        raise GovernanceError("disposition ledger inventory algorithm mismatch")
    if source.get("logical_unit_count") != len(logical_units):
        raise GovernanceError("disposition ledger logical unit count mismatch")

    families = ledger.get("families")
    if not isinstance(families, list):
        raise GovernanceError("disposition ledger families must be an array")
    family_by_name: dict[str, dict[str, Any]] = {}
    for item in families:
        if not isinstance(item, dict) or not isinstance(item.get("family"), str):
            raise GovernanceError("invalid preservation family entry")
        family = item["family"]
        if family in family_by_name:
            raise GovernanceError(f"duplicate preservation family: {family}")
        family_by_name[family] = item
    missing_families = REQUIRED_FAMILIES - set(family_by_name)
    if missing_families:
        raise GovernanceError(
            f"missing preservation family: {sorted(missing_families)[0]}"
        )
    extra_families = set(family_by_name) - REQUIRED_FAMILIES
    if extra_families:
        raise GovernanceError(
            f"unknown preservation family: {sorted(extra_families)[0]}"
        )

    for family, item in family_by_name.items():
        owner_rule = item.get("owner_rule")
        owner_path = item.get("owner_path")
        if owner_rule not in declarations:
            raise GovernanceError(f"family owner rule is not declared: {family}")
        if manifest["rule_owners"].get(owner_rule) != owner_path:
            raise GovernanceError(f"family owner mismatch: {family}")
        if (
            not isinstance(item.get("activation_check"), str)
            or not item["activation_check"].strip()
        ):
            raise GovernanceError(f"incomplete preservation family: {family}")
        _validate_ledger_selector(
            item.get("selector"), owner_path, modules, f"family {family}"
        )

    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise GovernanceError("disposition ledger entries must be an array")
    expected_units = {unit["current_location"]: unit for unit in logical_units}
    seen_locations: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise GovernanceError("invalid disposition entry")
        location = entry.get("current_location")
        if not isinstance(location, str) or location in seen_locations:
            raise GovernanceError(f"invalid or duplicate current location: {location}")
        seen_locations.add(location)
        family = entry.get("family")
        if family not in family_by_name:
            raise GovernanceError(f"unknown disposition family: {family}")
        owner_rule = entry.get("owner_rule")
        if owner_rule not in declarations:
            raise GovernanceError(f"ledger owner rule is not declared: {owner_rule}")
        if owner_rule != family_by_name[family]["owner_rule"]:
            raise GovernanceError(
                f"ledger owner does not match family owner: {location}"
            )
        expected_unit = expected_units.get(location)
        if expected_unit is None:
            raise GovernanceError(
                f"unknown current logical unit disposition: {location}"
            )
        for field in ("unit_kind", "start_line", "end_line"):
            if entry.get(field) != expected_unit[field]:
                raise GovernanceError(f"logical unit {field} mismatch at {location}")
        if entry.get("text_sha256") != expected_unit["text_sha256"]:
            raise GovernanceError(f"logical unit text hash mismatch at {location}")
        disposition = entry.get("disposition")
        if disposition not in {"PRESERVE", "MOVE", "SUPERSEDE", "REMOVE"}:
            raise GovernanceError(f"invalid disposition: {location}")
        if disposition in {"SUPERSEDE", "REMOVE"} and not entry.get("design_approval"):
            raise GovernanceError(f"{disposition} requires design approval: {location}")
        _validate_ledger_selector(
            entry.get("selector"),
            family_by_name[family]["owner_path"],
            modules,
            f"entry {location}",
        )
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            raise GovernanceError(f"missing disposition reason: {location}")
        check = entry.get("observable_activation_check")
        if not isinstance(check, str) or not check.strip():
            raise GovernanceError(f"missing observable activation check: {location}")

    missing_units = set(expected_units) - seen_locations
    if missing_units:
        raise GovernanceError(
            f"missing current logical unit disposition: {sorted(missing_units)[0]}"
        )
    extra_locations = seen_locations - set(expected_units)
    if extra_locations:
        raise GovernanceError(
            f"unknown current logical unit disposition: {sorted(extra_locations)[0]}"
        )


def _glob_matches(path: str, pattern: str) -> bool:
    sentinel = "\0DOUBLESTAR\0"
    expression = re.escape(pattern).replace(r"\*\*", sentinel).replace(r"\*", "[^/]*")
    expression = expression.replace(sentinel, ".*")
    return re.fullmatch(expression, path) is not None


def select_modules(
    manifest: dict[str, Any], metadata: dict[str, Any]
) -> tuple[list[str], list[dict[str, Any]]]:
    """Select modules using field-AND, value-OR, selector-object-OR semantics."""
    selected: list[str] = []
    trace: list[dict[str, Any]] = []
    for module in manifest["modules"]:
        module_matches = bool(module["always"])
        selector_traces = []
        for index, selector in enumerate(module["selectors"]):
            field_matches: dict[str, bool] = {}
            if "risk_any" in selector:
                field_matches["risk_any"] = (
                    metadata["risk_tier"] in selector["risk_any"]
                )
            if "closure_tag_any" in selector:
                field_matches["closure_tag_any"] = bool(
                    set(metadata["closure_tags"]).intersection(
                        selector["closure_tag_any"]
                    )
                )
            if "task_path_any" in selector:
                field_matches["task_path_any"] = any(
                    _glob_matches(metadata["task_path"], pattern)
                    for pattern in selector["task_path_any"]
                )
            matched = bool(field_matches) and all(field_matches.values())
            module_matches = module_matches or matched
            selector_traces.append(
                {"selector_index": index, "fields": field_matches, "matched": matched}
            )
        trace.append(
            {
                "path": module["path"],
                "always": module["always"],
                "selectors": selector_traces,
                "matched": module_matches,
            }
        )
        if module_matches:
            selected.append(module["path"])
    return sorted(set(selected)), trace


def parse_task_metadata(text: str, expected_path: str) -> dict[str, Any]:
    """Parse the required fields from a task's first metadata block."""
    metadata_block = text.split("\n## ", 1)[0]
    fields: dict[str, list[str]] = {
        "Risk-Tier": [],
        "Closure-Tags": [],
        "Task-Path": [],
    }
    for line in metadata_block.splitlines():
        for name in fields:
            prefix = f"{name}:"
            if line.startswith(prefix):
                fields[name].append(line[len(prefix) :].strip())
    for name, values in fields.items():
        if len(values) != 1:
            raise ValueError(
                f"{name} must appear exactly once in the first metadata block"
            )

    risk = fields["Risk-Tier"][0]
    if risk not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError("Risk-Tier must be unadorned LOW, MEDIUM, or HIGH")
    raw_tags = fields["Closure-Tags"][0]
    try:
        closure_tags = json.loads(raw_tags)
    except json.JSONDecodeError as exc:
        raise ValueError("Closure-Tags must be RFC 8259 JSON") from exc
    if not isinstance(closure_tags, list) or not all(
        isinstance(tag, str) for tag in closure_tags
    ):
        raise ValueError("Closure-Tags must be a string array")
    if closure_tags != sorted(set(closure_tags)) or any(
        not TAG.fullmatch(tag) for tag in closure_tags
    ):
        raise ValueError("Closure-Tags must be sorted, unique, lowercase tags")
    task_path = fields["Task-Path"][0]
    _safe_posix_path(task_path, label="task path")
    if task_path != expected_path:
        raise ValueError(
            "Task-Path does not match the current repository-relative path"
        )
    return {"risk_tier": risk, "closure_tags": closure_tags, "task_path": task_path}


def _write_digest(
    root_candidate: Path,
    manifest_candidate: Path,
    manifest: dict[str, Any],
    repo_root: Path,
) -> str:
    inputs: dict[str, str] = {"AGENTS.md": _sha256(root_candidate.read_bytes())}
    manifest_bytes = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    inputs["docs/agents/manifest.json"] = _sha256(manifest_bytes)
    for module in sorted(manifest["modules"], key=lambda item: item["path"]):
        inputs[module["path"]] = _sha256((repo_root / module["path"]).read_bytes())
    digest = _sha256(
        json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    output = {
        "schema_version": 1,
        "algorithm": "sha256",
        "digest": digest,
        "inputs": inputs,
    }
    digest_path = manifest_candidate.parent / "governance_digest.json"
    digest_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return digest


def validate(
    root_candidate: Path,
    manifest_candidate: Path,
    disposition_ledger: Path,
    repo_root: Path,
) -> str:
    root_text = root_candidate.read_text(encoding="utf-8")
    if len(root_text.splitlines()) > 300:
        raise GovernanceError("root candidate exceeds 300 lines")
    manifest = _load_json(manifest_candidate, "manifest candidate")
    modules = _validate_manifest(manifest, repo_root)

    documents = {"AGENTS.md": root_text}
    for module in modules:
        documents[module["path"]] = (repo_root / module["path"]).read_text(
            encoding="utf-8"
        )
    for path, text in documents.items():
        _validate_links(path, text, repo_root, manifest_candidate)
    declarations, _references = _collect_rules(documents)
    _validate_owners(manifest, declarations)
    ledger = _load_json(disposition_ledger, "disposition ledger")
    _validate_ledger(ledger, repo_root, declarations, manifest, modules)
    return _write_digest(root_candidate, manifest_candidate, manifest, repo_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root-candidate", type=Path, required=True)
    parser.add_argument("--manifest-candidate", type=Path, required=True)
    parser.add_argument("--disposition-ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        digest = validate(
            args.root_candidate,
            args.manifest_candidate,
            args.disposition_ledger,
            Path.cwd(),
        )
    except (GovernanceError, OSError, UnicodeError) as exc:
        print(f"Governance validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Governance validation PASS: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
