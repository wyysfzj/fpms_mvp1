# FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01

Status: PASS — HIGH IMPLEMENTATION + INDEPENDENT REVIEW 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `9. Wave 2A — lifecycle foundation`
Catalog ordinal: `17`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `373`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Implement generic `apply_lifecycle_event()` orchestration without adding a generic HTTP endpoint or absorbing any event rule.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for the generic lifecycle
orchestrator. It does not change the exact closure slice: event-specific decisions and the
registry implementation remain outside this task.

### Public seam and exact rule boundary

- `lifecycle_service.py` exposes
  `apply_lifecycle_event(command, transaction) -> LifecycleTransitionResult`.
- The same module defines the frozen, slots, keyword-only decision type
  `LifecycleRuleDecision(current_projection, oa_sequence=None)`. The exact rule callable is
  `(command, previous_projection, transaction) -> LifecycleRuleDecision`.
- Resolve the event-specific rule by lazily loading
  `lifecycle_rules.get_lifecycle_rule(command.event_type)`. This task neither implements nor
  eagerly imports the registry and does not absorb a concrete event rule.
- The public seam accepts only `lane=LIFECYCLE` with
  `confirmation_status=CONFIRMED`. `LEGACY_IMPORT/LEGACY_UNVERIFIED` remains exclusively on
  its independent import task and the append seam; it is not accepted by this orchestrator.
- A resolved rule remains event-specific and read-only. It returns the exact frozen
  `LifecycleRuleDecision`; it does not append an activity or mutate, flush, commit or roll
  back the caller-owned transaction.

### Projection, compatibility and stable replay

- For a new event, first read the same-case current projection and compatibility status,
  then invoke the read-only rule. Derive compatibility only in the forward direction with
  `project_legacy_case_status()` from the rule's `current_projection`, the event type and the
  rule's `oa_sequence`; never reverse-infer lifecycle axes from `Case.status`.
- OA sequence comes only from the rule decision. For an OA event, the canonical activity
  payload passed to `append_case_activity()` must persist that same `oa_sequence`, so replay
  can reproduce the original projection decision.
- A `RETAINED_CONFLICT` result raises HTTP 409
  `LIFECYCLE_LEGACY_PROJECTION_CONFLICT` before append. The complete call is write-free; it
  must not guess a replacement status, retain the old status and continue a central
  projection change, or increment lifecycle revision.
- A same-case, same-idempotency-key replay first reads the stored activity, reconstructs its
  stored previous and current projections, and derives the original compatibility status
  from the stored event and canonical payload. It then delegates to
  `append_case_activity()` for the complete fact/evidence comparison. Later advancement of
  the Case must not make that original request unreplayable.

### Fail-closed errors and transaction boundary

- Invalid command shape, lane or confirmation status returns HTTP 400. An unregistered event
  returns HTTP 409 `LIFECYCLE_RULE_NOT_REGISTERED`; rule resolution failure or a return value
  other than the exact `LifecycleRuleDecision` type also returns HTTP 409.
- Preserve the append seam's HTTP 404, HTTP 409, CAS, idempotency and caller-owned transaction
  semantics unchanged. This service may use the supplied transaction but must not commit,
  roll back or close it.
- Do not add a generic lifecycle-write HTTP endpoint.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
- `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): append, projection

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- `FPMS-V8-LC-CASE-OPENED-20260712-01` — first `lifecycle_rules.py` registry and event rule owner

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md`
- `backend/app/modules/cases/lifecycle_service.py`
- `backend/tests/test_v8_lifecycle_apply_event.py`
- `artifacts/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_apply_event.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_apply_event.py tests/test_v8_lifecycle_activity_append.py tests/test_v8_lifecycle_legacy_projection.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_service.py tests/test_v8_lifecycle_apply_event.py && .venv/bin/ruff format app/modules/cases/lifecycle_service.py tests/test_v8_lifecycle_apply_event.py && .venv/bin/ruff check app/modules/cases/lifecycle_service.py tests/test_v8_lifecycle_apply_event.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_service.py backend/tests/test_v8_lifecycle_apply_event.py tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01` pass. Only then may this task be reported PASS.
