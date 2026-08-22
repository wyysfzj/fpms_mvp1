# FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01

Status: PASS / INDEPENDENT REREVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `10. Wave 2B — one lifecycle event per task`
Catalog ordinal: `21`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `386`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Exact Closure Slice

Owned receipt moves to prosecution, submission confirmed/waiting acceptance and application pending.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): [DEFAULT LIFECYCLE SEAM]

### Shared ownership serialization

- `backend/app/modules/cases/lifecycle_rules.py` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md`
- `backend/tests/test_v8_lifecycle_filing_receipt_archived.py`
- `backend/app/modules/cases/lifecycle_rules.py`
- `artifacts/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Modify only lifecycle_rules.py plus the exact test, depend on apply_lifecycle_event(), preserve strict table order and implement exactly one event.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_receipt_archived.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_filing_receipt_archived.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_filing_receipt_archived.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_filing_receipt_archived.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_filing_receipt_archived.py app/modules/cases/lifecycle_rules.py`
- `git diff --check -- backend/tests/test_v8_lifecycle_filing_receipt_archived.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Authority and latest-wins boundary

- Authoritative Delta-4 contract:
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`.
- Supplemental batch authority: row `13 / M4-D / H4-0` of
  `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk is `HIGH`; this contract is frozen for High execution, and product implementation
  and task evidence remain `NOT STARTED` in this materialization lane.
- This section is the latest-wins authority only for the Delta-4 receipt evidence matrix,
  dependencies, runbook and serialization stated below. The pre-existing task body and
  rejected review/evidence remain immutable history and do not constitute acceptance.
- `chosen_runbook: P0-prereq-heavy-story` governs Delta-4 and High execution. The historical
  `P0-single-lane-story` classification above is preserved only as baseline history.

### Exact filing-receipt closure and evidence matrix

Close exactly one pure lifecycle rule, `FILING_RECEIPT_ARCHIVED`. It accepts only the exact
existing command boundary and exact prior projection:
`WAITING_EXTERNAL_RECEIPT` / `SUBMITTED_WAITING_RECEIPT` / `NOT_ESTABLISHED` / `CONFIRMED`.
The accepted catalog Task 21 registry and projection decision remain unchanged: the result
is `PROSECUTION_MANAGEMENT` / `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE` /
`APPLICATION_PENDING`, preserves `CONFIRMED`, and returns `oa_sequence=None`.

The command evidence tuple must contain exactly these two references and no other value:

| Cardinality | `evidence_kind` | `object_type` |
| --- | --- | --- |
| exactly 1 | `FINAL_SUBMISSION_VERSION` | `DocumentEvidenceVersion` |
| exactly 1 | `VALID_FILING_RECEIPT` | `OfficialWorkPackageReceipt` |

Every tuple member must have exact type `EvidenceReference`, the exact transitioning
`case_id`, a nonblank and non-duplicated object identity, a `content_hash` that full-matches
lowercase `sha256:[0-9a-f]{64}`, and a non-null naive `datetime` `captured_at`.

### Fail-closed, transaction and replay rules

- Missing evidence, an empty tuple, a non-tuple carrier, any cardinality other than two,
  zero or multiple values for either required kind/type pair, an extra or unknown value,
  a duplicate identity, a non-exact `EvidenceReference`, wrong kind/object type/case, blank
  identity, malformed/shortened/uppercase hash, or missing/non-datetime/timezone-aware
  capture time returns no decision through the accepted public lifecycle-rule surface.
- Tuple order is not authority. Reordering the exact valid pair preserves the decision;
  reordering cannot make an invalid set valid, and the rule never guesses, selects a
  fallback, or ignores an extra value.
- The rule does not query whether either referenced object exists. Source existence,
  current/review/status truth and canonical hash/linkage are adapter/resolver obligations
  before `apply_lifecycle_event()` is called.
- The rule remains pure and read-only: no SELECT, add, delete, write, flush, refresh,
  commit, rollback, nested transaction or other caller-owned transaction access; it
  creates no package, receipt, evidence, activity, projection or replay row.
- Repeated invocation with the same immutable command and prior projection returns the
  same decision or the same no-decision result. It does not reconstruct evidence from
  mutable source rows or perform durable replay lookup. Existing lifecycle-service
  idempotency and downstream adapter replay semantics remain unchanged.

### Dependencies and High serialization

- Shared lifecycle execution order is strict and each predecessor requires independently
  accepted PASS evidence:
  `D4-01 CASE_OPENED evidence guard` →
  `D4-03 filing-preparation evidence guard` →
  `D4-04 external-submission evidence guard` →
  this catalog Task 21 receipt-rule correction.
- The accepted Task 21 event/registry/prior-projection/target-projection semantics are
  inherited unchanged; this re-freeze corrects only its event-specific evidence
  acceptance. Existing canonical lifecycle-seam dependencies above remain required.
- High owns `backend/app/modules/cases/lifecycle_rules.py` only after D4-04 is independently
  accepted. No other agent may edit or verify that shared source concurrently, and later
  lifecycle-rule owners wait until this task is independently accepted and releases it.
- Any pytest or shared-file verification that activates SQLite reports
  `READY_FOR_SERIAL_TEST`, waits for the controller's explicit `GRANT`, and runs under
  `GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writer one.

### Explicit Delta-4 non-closure

- No second lifecycle event, projection decision, status vocabulary, actor, idempotency,
  payload, event-time, persistence or registry-order change.
- No filing-receipt adapter/resolver, work-package/receipt lookup, source validation,
  document evidence version creation, activity write or OA behavior; downstream catalog
  Task 66 owns the adapter behavior after this rule is accepted.
- No API/router/schema/model/migration/seed/frontend, permission, response envelope,
  status-code, fee, deadline, customer-decision or release-gate change.
- No new source/test/task/artifact path, no second receipt-correction task, no broad test or
  lint run, no adjacent refactor/cleanup, and no rewrite of the rejected evidence history.

### Unchanged implementation, TDD, evidence and gates

- The exact existing Allowed Files list remains the complete allowlist; no path is added or
  removed. The task-owned test remains
  `backend/tests/test_v8_lifecycle_filing_receipt_archived.py`.
- Under the latest-wins `P0-prereq-heavy-story` runbook, preserve task-scoped TDD: record a
  behavioral RED proving the tuple-only guard accepts a forbidden matrix case, then make
  the smallest rule/test change that proves the exact positive pair, order independence,
  every fail-closed class above, unchanged projection and zero transaction interaction.
- The existing targeted RED/GREEN, scoped Ruff/format/diff commands, evidence path,
  dirty-baseline and baseline-subtracted diff requirements, independent zero-finding
  approval, repository task gate, atomic evidence validation and Done Definition remain
  binding. Evidence 1.1 is the final High acceptance authority for this not-yet-PASS task.
- This Ultra materialization performs no product/test edit, evidence initialization,
  evidence rewrite, task gate, atomic evidence validation or release execution.
