# FPMS-V8-LC-CASE-OPENED-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `10. Wave 2B — one lifecycle event per task`
Catalog ordinal: `18`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `383`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Exact Closure Slice

Implement the first `lifecycle_rules.py` registry interface and only the `CASE_OPENED`
rule: an uninitialized projection becomes new case, not submitted, not established and
confirmed, with no OA sequence.

## Ultra Contract Freeze — 2026-07-13

This task is the first implementation owner of
`backend/app/modules/cases/lifecycle_rules.py`. It freezes the registry shape needed by
the already separate apply seam and adds exactly one event rule; it does not absorb the
generic orchestration or any later event.

### Frozen registry and callable interface

- `lifecycle_rules.py` exposes `get_lifecycle_rule(event_type)`. The
  `apply_lifecycle_event()` seam imports and calls this lookup lazily, so the apply-seam
  task does not own or eagerly import the rule table.
- For the exact string `CASE_OPENED`, `get_lifecycle_rule()` returns the one rule callable
  registered by this task. Every other value is unregistered and returns no rule; the
  caller seam alone maps that absence to 409 `LIFECYCLE_RULE_NOT_REGISTERED`.
- The returned rule has the exact callable signature
  `(command, previous_projection, transaction) -> LifecycleRuleDecision`. It consumes the
  frozen `LifecycleEventCommand` and `LifecycleProjection` contracts and returns the
  frozen `LifecycleRuleDecision` defined by `lifecycle_service.py`; this task must not
  redefine or widen any of those types.
- No public rule-engine class, decorator, plugin mechanism, mutable registration API,
  fallback rule, case-folding or event-type normalization is authorized. The concrete
  `CASE_OPENED` rule helper may remain private.

### Exact `CASE_OPENED` decision

The rule accepts only an uninitialized `previous_projection`, meaning an exact
`LifecycleProjection` whose `business_stage`, `official_procedure_stage`, `legal_status`
and `lifecycle_verification_status` are all `None`. For a frozen, valid `CASE_OPENED`
command, it returns exactly:

```python
LifecycleRuleDecision(
    current_projection=LifecycleProjection(
        business_stage=BusinessStage.NEW_CASE,
        official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
        legal_status=LegalStatus.NOT_ESTABLISHED,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
    ),
    oa_sequence=None,
)
```

The callable must fail closed and return no decision when invoked with a malformed
command/projection, a non-`CASE_OPENED` event, or a projection with any initialized axis
or verification value. It must not partially fill, preserve or overwrite an initialized
projection. An exact same-idempotency-key replay remains owned by the apply/append seams,
which reconstruct the originally stored transition; a new repeated `CASE_OPENED` against
an initialized current projection is rejected by this rule.

### Transaction, RED and GREEN boundary

- `transaction` is caller-owned and exists only to preserve the uniform rule signature.
  This rule performs no SELECT or write, invokes no append seam, and does not add, delete,
  flush, commit or roll back.
- RED proves that the registry/module or exact `CASE_OPENED` registration is missing and
  that no valid decision can yet be obtained.
- GREEN proves exact lookup for `CASE_OPENED`, no-rule results for unregistered events,
  the four exact projection values and `oa_sequence=None`, fail-closed malformed and
  initialized inputs, and zero transaction/persistence interaction.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, append/orchestration seam, endpoint,
seed or UI. Every later lifecycle event named under `Remaining Follow-Up Task IDs` is an
explicit non-closure and must remain separately implemented in shared-file order. Do not
absorb another V8 catalog row, a second closure slice, an unresolved customer policy or
unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): [DEFAULT LIFECYCLE SEAM]

### Shared ownership serialization

- `backend/app/modules/cases/lifecycle_rules.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
- `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
- `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
- `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
- `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
- `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
- `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
- `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
- `backend/tests/test_v8_lifecycle_case_opened.py`
- `backend/app/modules/cases/lifecycle_rules.py`
- `artifacts/FPMS-V8-LC-CASE-OPENED-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Modify only lifecycle_rules.py plus the exact test, depend on apply_lifecycle_event(), preserve strict table order and implement exactly one event.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_case_opened.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_case_opened.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_case_opened.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff format tests/test_v8_lifecycle_case_opened.py app/modules/cases/lifecycle_rules.py && .venv/bin/ruff check tests/test_v8_lifecycle_case_opened.py app/modules/cases/lifecycle_rules.py`
- `git diff --check -- backend/tests/test_v8_lifecycle_case_opened.py backend/app/modules/cases/lifecycle_rules.py tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-CASE-OPENED-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-CASE-OPENED-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-CASE-OPENED-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-CASE-OPENED-20260712-01` pass. Only then may this task be reported PASS.
