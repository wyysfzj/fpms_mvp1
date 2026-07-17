# FPMS-V8-OVERLAY-HTTP-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `265`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `796`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-API`

- RED expectation: Exact API test fails on the route, four-permission contract, direct
  response, 29-entry serialization or unchanged status matrix.
- GREEN expectation: Exact API test passes the direct 200 response and exact
  401/403/404/409/422 semantics without a new response envelope.

## Exact Closure Slice

Bodyless GET `/cases/{case_id}/lifecycle-overlay`; permissions as four function parameters; no router edit.

## Ultra Contract Freeze — 2026-07-14

This section is authoritative for High implementation. It materializes the delta-2 HTTP
serialization contract without changing this task's one-endpoint closure, duplicating
overlay business rules or reopening the accepted keyset service.

### Frozen route, permissions and direct response

- Keep the bodyless `GET /cases/{case_id}/lifecycle-overlay` route exactly as frozen.
  Path and query parameters are not a request body, and no body schema is introduced.
- Inject `Case.Read`, `Doc.Read`, `Task.Read` and `Fee.Read` as four separate handler
  function parameters using `Depends(require_perm(...))`; do not place them in decorator
  `dependencies`. Missing any one permission returns 403 rather than a partial snapshot.
- Use the already-wired cases router. Do not edit router wiring, add a second endpoint or
  create a partial-visibility variant.
- A successful request returns 200 and serializes the accepted `LifecycleOverlay`
  result directly. Do not wrap it in a new success envelope, rename fields, reconstruct
  the result, invoke a second resolver path or duplicate service rules in the adapter.

### Frozen 29-entry decision-gate serialization

- `decision_gates` contains exactly 29 ordered entries unchanged from the keyset result:
  the seven non-legacy codes in accepted enum order, each with
  `requested_scope_key=case:{case_id}`, followed by 22
  `DG-LEGACY-FORM-CLASS` entries requested as ascending `form-001..form-022`.
- Those 29 entries cover eight distinct gate codes. The legacy gate code intentionally
  repeats 22 times, and entry identity remains exactly
  `(gate_code, requested_scope_key)`. The HTTP adapter must not key, merge, replace or
  deduplicate entries by `gate_code` alone.
- Every cursor page returns the same complete ordered gate snapshot. Milestone paging
  must not truncate the tuple, omit it after the first page or otherwise apply
  `after_sequence`, `limit`, `has_more` or `next_cursor` to decision gates.
- No returned entry may have `requested_scope_key=ALL-22`, and the HTTP adapter must not
  issue such a request. A legacy fallback is preserved unchanged as
  `requested_scope_key=form-NNN` with `resolved_scope_key=ALL-22`, including its exact
  extracted value and source provenance.
- `generated_at`, `lifecycle_revision`, `next_cursor` and `has_more` are serialized
  unchanged from the keyset result. Timestamp capture, frozen revision, milestone cursor
  calculation and the complete-per-page gate snapshot remain inherited from
  `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`; the HTTP layer reads no new clock and
  calculates no cursor.

### Frozen unchanged HTTP status matrix

| Status | Exact API behavior |
| --- | --- |
| 200 | Return the direct complete `LifecycleOverlay`, including all 29 ordered decision-gate entries. |
| 401 | Existing authentication rejects an unauthenticated request. |
| 403 | Any missing `Case.Read`, `Doc.Read`, `Task.Read` or `Fee.Read` permission rejects the whole request. |
| 404 | Preserve the existing case-not-found behavior. |
| 409 | Preserve unreconstructable revision/configuration conflict behavior; representable conflicts stay in warnings and never truncate the snapshot. |
| 422 | Preserve query/path validation behavior. |

No status, error code, detail shape or module response convention is remapped or newly
enveloped by this adapter.

### Frozen RED / GREEN API test contract

`backend/tests/test_v8_lifecycle_overlay_api.py` MUST prove:

1. the sole bodyless GET route, four parameter-injected permissions, no partial response
   and no router-wiring or second-route requirement;
2. a direct 200 response contains exactly 29 ordered gate entries, exactly eight distinct
   gate codes and all 22 repeated legacy-code entries;
3. all 29 `(gate_code, requested_scope_key)` identities are distinct and preserve the
   seven `case:{case_id}` plus 22 ascending form scopes without code-only deduplication;
4. no entry requests `ALL-22`, while a fixture fallback preserves requested `form-NNN`
   separately from resolved `ALL-22` and keeps the remaining value/source fields
   unchanged;
5. every tested cursor page includes the complete same gate snapshot, while
   `generated_at`, `lifecycle_revision`, `next_cursor` and `has_more` remain exact
   keyset-service values; and
6. 401/403/404/409/422 behavior remains unchanged and success has no invented response
   envelope.

The RED is missing HTTP serialization or any route/permission/status mismatch. GREEN
does not authorize changes to keyset logic, decision-gate resolution, schemas, router
wiring, frontend behavior or any second endpoint.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): keyset

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OVERLAY-HTTP-20260712-01.md`
- `backend/app/modules/cases/api.py`
- `backend/tests/test_v8_lifecycle_overlay_api.py`
- `artifacts/FPMS-V8-OVERLAY-HTTP-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/api.py tests/test_v8_lifecycle_overlay_api.py && .venv/bin/ruff format app/modules/cases/api.py tests/test_v8_lifecycle_overlay_api.py && .venv/bin/ruff check app/modules/cases/api.py tests/test_v8_lifecycle_overlay_api.py`
- `git diff --check -- backend/app/modules/cases/api.py backend/tests/test_v8_lifecycle_overlay_api.py tasks/postdemo/v8/FPMS-V8-OVERLAY-HTTP-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OVERLAY-HTTP-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OVERLAY-HTTP-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OVERLAY-HTTP-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-HTTP-20260712-01` pass. Only then may this task be reported PASS.
