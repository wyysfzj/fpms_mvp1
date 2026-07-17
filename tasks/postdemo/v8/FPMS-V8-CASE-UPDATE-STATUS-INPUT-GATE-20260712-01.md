# FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `56`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `442`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Full case update cannot directly change legacy status once lifecycle is active; conflict is 409 with no partial update.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for the existing full case-update
entrypoint. It does not change the exact closure slice, explicit non-closure or canonical
dependency. Only `update_case_full()` may gain this status-input gate; case creation, limited
updates, batch actions and lifecycle write entrypoints remain unchanged.

### Lifecycle protection predicate and status no-ops

- A persisted Case is lifecycle inactive if and only if all five carrier columns are SQL
  `NULL`: `business_stage`, `official_procedure_stage`, `legal_status`,
  `lifecycle_verification_status` and `lifecycle_revision`.
- Any non-`NULL` value in any one carrier makes the Case lifecycle protected. This is an
  SQL-nullity test, not a truthiness or enum-validity test: empty/corrupt strings, incomplete
  carrier combinations, and `lifecycle_revision` values `0` or below all protect the Case.
- A request with `status` omitted, explicitly `null`, or explicitly equal to the Case status
  read from the database is a status no-op. It performs no status write and requires no status
  CAS; every other provided field continues through the existing full-update behavior.
- Only an explicit non-null `status` different from the status read from the database is a
  direct status-change request.

### Gate ordering and exact protected-case conflict

- Read the Case first and preserve the existing 404 behavior. Immediately after that read,
  classify the status input and evaluate the five persisted carrier values. This gate runs
  before every other service validation, relationship delete/add, scalar assignment, flush,
  commit or other ORM mutation.
- A direct status-change request against a lifecycle-protected Case raises exactly HTTP 409
  with code `CASE_STATUS_MANAGED_BY_LIFECYCLE`, message
  `案件状态已由生命周期管理，不能直接修改`, and details containing exactly:

  ```python
  {
      "case_id": case.id,
      "current_status": current_status,
      "requested_status": requested_status,
      "lifecycle_revision": lifecycle_revision,
  }
  ```

  Here `current_status` and `lifecycle_revision` are the raw persisted values observed for the
  Case at rejection; `requested_status` is the explicit non-null requested value. No extra
  details keys are allowed.

- The rejection leaves every scalar field and child collection unchanged. The gate does not
  normalize, repair or reinterpret a corrupt or partially populated lifecycle carrier.

### Legacy transition preservation and status CAS

- When all five carriers were SQL `NULL` at the initial read, an explicit different status
  continues through the existing `validate_case_status_transition()` and status-required-field
  rules without weakening, replacing or reordering those rules relative to each other.
- After all existing validations pass and before any requested ORM mutation, write the legacy
  status with one conditional CAS whose predicate requires the Case id, the originally read
  status, and all five lifecycle carriers still SQL `NULL`. Exactly one matched row is success.
- A zero-row CAS is the same exact 409 conflict defined above. No requested scalar or child
  update may be applied, flushed or committed before a successful CAS, so concurrent lifecycle
  activation or a concurrent status change cannot produce a TOCTOU overwrite or partial update.
- Status omission, explicit `null` and explicit same-value requests remain no-ops and do not
  enter this CAS path.

### Exact RED/GREEN test matrix

`backend/tests/test_v8_case_update_status_gate.py` must prove all of the following through the
public `update_case_full()` service behavior:

1. On a protected Case, each of omitted `status`, explicit `null` and explicit same status is a
   no-op while another valid field update succeeds and the status remains unchanged.
2. Parameterize the five carriers so each independently protects an otherwise all-`NULL` Case;
   include corrupt/incomplete string-carrier values and both `0` and a negative
   `lifecycle_revision`. Every explicit different status receives the exact 409 code, Chinese
   message and four-key details contract above.
3. Submit a protected different-status request that also contains data that would fail a later
   existing validation and requests scalar/child changes. The lifecycle 409 wins, and a fresh
   database read proves no scalar or child mutation occurred.
4. For an all-`NULL` legacy Case, prove one valid status transition with its required fields still
   succeeds, one forbidden transition still raises `CASE_STATUS_TRANSITION_INVALID`, and one
   transition missing required fields still raises `CASE_STATUS_REQUIRES_APPLICATION_FIELDS`.
5. Force a race after the initial all-`NULL` read but before the CAS: parameterize concurrent
   population of each lifecycle carrier, then separately change the original status. Every CAS
   miss raises the same exact lifecycle-managed 409 and a fresh database read proves the
   request made no partial scalar or child update.
6. Run `backend/tests/test_case_missing_fields_crud.py` unchanged as the inherited full-update
   regression; it remains read-only and must pass with the exact task test.

This task does not repair dirty lifecycle data, add or alter a schema/model carrier, change
another case-update entrypoint, or introduce a lifecycle transition rule.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `backend/tests/test_case_missing_fields_crud.py`: Exact read-only pre-V8 regression required by the approved dependency alias.

- Approved source dependency cell (verbatim): projection; existing case-update tests

### Shared ownership serialization

- `backend/app/modules/cases/service.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_v8_case_update_status_gate.py`
- `artifacts/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_case_update_status_gate.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_case_update_status_gate.py tests/test_case_missing_fields_crud.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/service.py tests/test_v8_case_update_status_gate.py && .venv/bin/ruff format app/modules/cases/service.py tests/test_v8_case_update_status_gate.py && .venv/bin/ruff check app/modules/cases/service.py tests/test_v8_case_update_status_gate.py`
- `git diff --check -- backend/app/modules/cases/service.py backend/tests/test_v8_case_update_status_gate.py tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01` pass. Only then may this task be reported PASS.
