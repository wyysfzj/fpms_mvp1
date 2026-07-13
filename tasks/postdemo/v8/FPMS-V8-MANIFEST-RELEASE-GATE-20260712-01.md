# FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `7. Wave 0 — materialization and planning gates`
Catalog ordinal: `1`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `341`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Extend manifest parsing to accept exact `tasks/postdemo/v8/*.md` declarations while preserving the accepted Additional-GAP path, duplicate detection and self-exclusion. It does not run the V8 release gate.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- None

### External, gate and inherited prerequisites

- `external` — `PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01`: Wave 0 materialization PASS and foundation catalog artifacts exist.
- `inherited` — `backend/tests/test_addgap_manifest_release_gate.py`: Accepted Additional-GAP manifest parser regression; read-only for this V8 task.

- Approved source dependency cell (verbatim): Wave 0 manifest exists

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01.md`
- `scripts/release_gate.sh`
- `backend/tests/test_v8_manifest_release_gate.py`
- `artifacts/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_manifest_release_gate.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_manifest_release_gate.py tests/test_addgap_manifest_release_gate.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_manifest_release_gate.py && .venv/bin/ruff format tests/test_v8_manifest_release_gate.py && .venv/bin/ruff check tests/test_v8_manifest_release_gate.py`
- `git diff --check -- scripts/release_gate.sh backend/tests/test_v8_manifest_release_gate.py tasks/postdemo/v8/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01` pass. Only then may this task be reported PASS.
