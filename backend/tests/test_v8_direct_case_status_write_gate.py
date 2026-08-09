from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
_LIFECYCLE_PATH = "app/modules/cases/lifecycle_activity_service.py"
_SERVICE_PATH = "app/modules/cases/service.py"
_LIFECYCLE_VALUE_EXPRESSIONS = {
    "business_stage": "_enum_value(current_projection.business_stage)",
    "official_procedure_stage": "_enum_value(current_projection.official_procedure_stage)",
    "legal_status": "_enum_value(current_projection.legal_status)",
    "lifecycle_verification_status": "_enum_value(current_projection.lifecycle_verification_status)",
    "lifecycle_revision": "new_revision",
    "status": "legacy_case_status",
}
_LEGACY_CAS_PREDICATES = {
    "Case.id == case_id",
    "Case.status == original_status",
    "Case.business_stage.is_(None)",
    "Case.official_procedure_stage.is_(None)",
    "Case.legal_status.is_(None)",
    "Case.lifecycle_verification_status.is_(None)",
    "Case.lifecycle_revision.is_(None)",
}


@dataclass(frozen=True)
class _StatusWrite:
    path: str
    function: str
    kind: str
    conditions: tuple[str, ...]
    node: ast.AST

    @property
    def identity(self) -> tuple[str, str, str, tuple[str, ...]]:
        return (self.path, self.function, self.kind, self.conditions)


def _expression(node: ast.AST) -> str:
    return ast.unparse(node)


def _is_case_status(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "status"
        and isinstance(node.value, ast.Name)
        and node.value.id == "Case"
    )


def _is_update_case(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "update"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "Case"
    )


def _is_update_case_chain(node: ast.AST) -> bool:
    while isinstance(node, ast.Call):
        if _is_update_case(node):
            return True
        if not isinstance(node.func, ast.Attribute):
            return False
        node = node.func.value
    return False


def _contains_case_annotation(node: ast.AST | None) -> bool:
    return node is not None and any(
        isinstance(part, ast.Name) and part.id == "Case" for part in ast.walk(node)
    )


def _case_instance_names(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names = {
        argument.arg
        for argument in (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs)
        if _contains_case_annotation(argument.annotation)
    }
    for node in ast.walk(function):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if _contains_case_annotation(node.annotation):
                names.add(node.target.id)
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) for target in node.targets
        ):
            if isinstance(node.value, ast.Call) and any(
                isinstance(part, ast.Name) and part.id == "Case" for part in ast.walk(node.value)
            ):
                names.update(target.id for target in node.targets if isinstance(target, ast.Name))
    return names


class _StatusWriteVisitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.writes: list[_StatusWrite] = []
        self._functions: list[str] = []
        self._conditions: list[str] = []
        self._case_names: list[set[str]] = []

    def _function(self) -> str:
        return ".".join(self._functions)

    def _record(self, kind: str, node: ast.AST) -> None:
        self.writes.append(
            _StatusWrite(
                path=self.path,
                function=self._function(),
                kind=kind,
                conditions=tuple(self._conditions),
                node=node,
            )
        )

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._functions.append(node.name)
        self._case_names.append(_case_instance_names(node))
        self.generic_visit(node)
        self._case_names.pop()
        self._functions.pop()

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    def visit_If(self, node: ast.If) -> None:
        self._conditions.append(_expression(node.test))
        self.generic_visit(node)
        self._conditions.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "values"
            and _is_update_case_chain(node.func.value)
        ):
            if any(keyword.arg == "status" for keyword in node.keywords):
                self._record("orm_update", node)
            if any(
                isinstance(argument, ast.Dict)
                and any(_is_case_status(key) for key in argument.keys if key is not None)
                for argument in node.args
            ):
                self._record("bulk_mapping", node)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        if any(_is_case_status(key) for key in node.keys if key is not None):
            self._record("bulk_mapping", node)
        self.generic_visit(node)

    def _visit_assignment(self, node: ast.AST, targets: list[ast.AST]) -> None:
        if self._case_names and any(
            isinstance(target, ast.Attribute)
            and target.attr == "status"
            and (
                _is_case_status(target)
                or (isinstance(target.value, ast.Name) and target.value.id in self._case_names[-1])
            )
            for target in targets
        ):
            self._record("attribute_assignment", node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._visit_assignment(node, node.targets)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._visit_assignment(node, [node.target])

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._visit_assignment(node, [node.target])


def _status_writes() -> list[_StatusWrite]:
    writes: list[_StatusWrite] = []
    for path in sorted(_APP_ROOT.rglob("*.py")):
        visitor = _StatusWriteVisitor(path.relative_to(_APP_ROOT.parent).as_posix())
        visitor.visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
        writes.extend(visitor.writes)
    return writes


def _keyword_values(node: ast.Call) -> dict[str, str]:
    return {keyword.arg: _expression(keyword.value) for keyword in node.keywords if keyword.arg}


def _where_predicates(node: ast.Call) -> set[str]:
    statement = node.func.value
    while isinstance(statement, ast.Call):
        if isinstance(statement.func, ast.Attribute) and statement.func.attr == "where":
            return {_expression(argument) for argument in statement.args}
        if not isinstance(statement.func, ast.Attribute):
            break
        statement = statement.func.value
    raise AssertionError("approved status update has no where clause")


def test_direct_case_status_writes_match_only_the_two_frozen_structures() -> None:
    writes = _status_writes()

    assert [write.identity for write in writes] == [
        (_LIFECYCLE_PATH, "append_case_activity", "orm_update", ()),
        (_SERVICE_PATH, "update_case_full", "orm_update", ("status_change_requested",)),
    ]

    lifecycle_write, legacy_write = writes
    assert isinstance(lifecycle_write.node, ast.Call)
    assert _keyword_values(lifecycle_write.node) == _LIFECYCLE_VALUE_EXPRESSIONS

    assert isinstance(legacy_write.node, ast.Call)
    assert _keyword_values(legacy_write.node) == {"status": "requested_status"}
    assert _where_predicates(legacy_write.node) == _LEGACY_CAS_PREDICATES
