# FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `7. Wave 0 — materialization and planning gates`
Catalog ordinal: `2`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `342`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Replan Record — 2026-07-13

Two independent read-only contract audits found that the approved plan fixed the
Foundation and Full invocations but did not freeze how an independent gate lane
supplies its current gate status. Implementation therefore paused before RED.
The story classification was re-evaluated above; the existing
`P0-prereq-heavy-story` remains the correct runbook. The following technical
contract resolves only that input ambiguity and does not change the closure
slice, business semantics, customer gates, catalog membership or upstream
materialization artifacts.

## Frozen Coverage CLI and Input Contract

### Command line

The public command is:

```text
python3 scripts/v8_catalog_manifest_gate.py \
  --phase foundation|lane|full \
  --manifest <markdown-path> \
  [--gate-register <json-path>] \
  [--self-pending <canonical-task-id>]
```

- `--phase` and `--manifest` are required. Unknown/missing arguments or unreadable/malformed inputs return `2`.
- The catalog, immutable base gate register and Foundation index are read only from:
  - `artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/materialization/catalog.json`
  - `artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/materialization/gate_register.json`
  - `artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/materialization/foundation_manifest_index.json`
- `--gate-register` defaults to the immutable base register. A future lane/full activation task supplies a full same-schema snapshot from its own authorized artifact subtree. Only each row's `status` may differ from the immutable base; task identity, path, deferred kind, gate requirements, lane activation and full-only fields must match exactly.
- The only allowed statuses are the base register's exact `allowed_statuses`: `unresolved`, `confirmed-pending`, `activated`, `prior-PASS`.
- Well-formed coverage, gate-status, prerequisite-PASS or `SELF_PENDING` violations return `1`; success returns `0`.

### Manifest grammar and common validation

- A task declaration is exactly `- Task file: ` followed by one backtick-wrapped `tasks/postdemo/v8/<canonical-task-id>.md` path.
- The declared count must equal the parsed count. Duplicate task IDs, malformed declarations and IDs outside the 283-row catalog are input errors (`2`).
- Catalog order is authoritative: a valid Foundation or Full manifest has the exact expected ordered task-ID sequence, not only a count match.
- `--self-pending` is singular, must name a task declared in the manifest and is allowed only as specified for the selected phase below. The command does not infer another pending task from filesystem state.
- The command validates structure and task-gate evidence only. It never runs product tests, SQLite, `release_gate.sh`, customer-decision writes or product fixes.

### Foundation phase

- Manifest membership/order must equal the 197 IDs in `foundation_manifest_index.task_ids`.
- Omitted IDs must equal the 86 `excluded_task_ids`, and the supplied gate-register snapshot must contain exactly those 86 immutable rows with an allowed status. Any of the four statuses is valid because unrelated lanes may remain unresolved or progress independently.
- `--self-pending` is optional; when present it must be exactly `FPMS-V8-FOUNDATION-CLOSE-20260712-01`.
- Foundation coverage does not run all 197 task gates; Foundation Close performs that separately before its coverage invocation.

### Lane phase

- `--self-pending` is required and must identify exactly one catalog row whose `deferred_kind` is `gate_activation`.
- Exact lane membership/order is the activation row followed by every catalog row whose `lane_activation_task_id` equals that activation task, in catalog order. No unrelated deferred or Foundation row is allowed.
- Every lane member must have status `confirmed-pending`, `activated` or `prior-PASS` in the supplied snapshot and retain the catalog's exact gate code/scope requirements. `unresolved`, wrong-code, wrong-scope or cross-lane status is a coverage violation (`1`).
- Declared prerequisite PASS evidence is the activation row's canonical `depends_on` list. The command invokes `./scripts/task_validate.sh <task-id>` for every dependency; any nonzero result is a coverage violation (`1`). This includes the already-PASS catalog coverage gate and excludes no dependency by inference.

### Full phase

- Manifest membership/order must equal all 283 catalog task IDs.
- All deferred rows except the exact self-pending Full activation row, when applicable, must be `activated` or `prior-PASS`; the self-pending Full activation row may be `confirmed-pending`.
- `--self-pending` is optional and may be only `FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01` or `FPMS-V8-FINAL-CLOSE-20260712-01`.
- Complete deferred-row status coverage necessarily includes all eight gate codes and all 22 `form-NNN` scopes because the immutable 86-row register is validated exactly; no blanket or missing form classification is accepted.

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Phase-aware validation: foundation lists every non-gated row and may classify omitted gated rows as unresolved, confirmed-pending, activated or prior-PASS; a lane manifest validates only its exact activation/tasks, confirmed gate(s), declared prerequisite PASS evidence and catalog membership while unrelated rows may remain pending; full manifest lists every catalog row with zero omissions. Permit `SELF_PENDING` only for the exact manifest-activation or close task currently producing its own evidence; reject every other undeclared/duplicate/pending-self row. It does not run product tests or the release gate.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`

### External, gate and inherited prerequisites

- `external` — `PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01`: Machine-readable catalog and gate register exist.

- Approved source dependency cell (verbatim): machine-readable catalog, gate register, manifest parser

### Shared ownership serialization

- `FOUNDATION_SHARED_VERIFICATION` order key `1`; project this order only across owners present in the active manifest.
- `FULL_SHARED_VERIFICATION` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01.md`
- `scripts/v8_catalog_manifest_gate.py`
- `backend/tests/test_v8_catalog_manifest_coverage_gate.py`
- `artifacts/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_catalog_manifest_coverage_gate.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_catalog_manifest_coverage_gate.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_catalog_manifest_coverage_gate.py && .venv/bin/ruff format tests/test_v8_catalog_manifest_coverage_gate.py && .venv/bin/ruff check tests/test_v8_catalog_manifest_coverage_gate.py`
- `git diff --check -- scripts/v8_catalog_manifest_gate.py backend/tests/test_v8_catalog_manifest_coverage_gate.py tasks/postdemo/v8/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01` pass. Only then may this task be reported PASS.
