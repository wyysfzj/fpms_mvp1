# FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01

Status: PASS / INDEPENDENT REVIEW APPROVED / MAIN ACCEPTED 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `131`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- Source catalog line: `573`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Importing the exact wrapper contract fails because `backend/app/modules/fees/annuity_reduction.py` does not exist.
- GREEN expectation: The exact wrapper test passes every named zero, annual-fee-code, grant-relative-year, base-validator-delegation and fail-closed case.

## Exact Closure Slice

A confirmed approval applies only from grant year through the tenth annual-fee year and only within its effective scope.

## Ultra Contract Freeze — 2026-07-14

Create the isolated pure-rule module
`backend/app/modules/fees/annuity_reduction.py`. This module wraps the already accepted
`validate_fee_reduction()` contract; it MUST NOT change the exact public surface or
behavior of `backend/app/modules/fees/fee_reduction.py`.

The public callable MUST be keyword-only with this exact signature and return the base
validator result unchanged:

```python
def validate_annuity_fee_reduction(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
    grant_fee_year_key: int,
) -> FeeReductionValidationResult:
    ...
```

### Frozen annuity scope

- `context.fee_year_key` and `grant_fee_year_key` are positive, exact non-boolean
  integer patent-year ordinals in the same coordinate system. Neither is a calendar
  year or a pre-normalized grant-relative year.
- Derive `grant_relative_year` exactly as
  `context.fee_year_key - grant_fee_year_key + 1`.
- This wrapper accepts only `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM` and
  `CN_ANNUITY_FEE_DES` as `context.fee_code`.
- A legal explicit ratio numerically equal to zero delegates directly to
  `validate_fee_reduction()` and does not require the statutory reduction window.
- Exact legal non-zero ratios `Decimal("0.7")` and `Decimal("0.85")` may delegate to
  `validate_fee_reduction()` only when `grant_relative_year` is inclusively `1..10`.
  A relative year below `1` or above `10` fails closed before approval applicability
  is evaluated.
- After the wrapper boundary succeeds, `validate_fee_reduction()` remains the sole
  authority for normalized result values, provenance, confirmed/current/source-backed
  approval, fee-code membership, patent-year interval and effective-date scope.
  The wrapper MUST NOT copy or weaken those rules.

### Frozen wrapper error surface and precedence

`AnnuityReductionScopeError` MUST subclass `ValueError`, expose the exact string error
code as a read-only `.code`, expose a defensive read-only mapping as `.details`, and use
the code as its exception message. The only wrapper-owned codes are:

```text
ANNUITY_REDUCTION_INVALID_CONTEXT
ANNUITY_REDUCTION_FEE_CODE_UNSUPPORTED
ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE
```

The wrapper checks failures in this exact order:

1. Invalid `context.fee_year_key`, then invalid `grant_fee_year_key`, raises
   `ANNUITY_REDUCTION_INVALID_CONTEXT`; details contain only `field`, naming
   `context.fee_year_key` or `grant_fee_year_key` respectively.
2. A fee code outside the three exact annual-fee codes raises
   `ANNUITY_REDUCTION_FEE_CODE_UNSUPPORTED`; details are exactly
   `{"fee_code": context.fee_code}`.
3. Missing, illegal or ambiguous ratio values, and unusable or ambiguous provenance,
   delegate to `validate_fee_reduction()` immediately so its existing
   `FeeReductionValidationError` wins and is never disguised as a year error. Legal
   zero also delegates immediately without a window check.
4. Only an exact legal non-zero `0.7/0.85` input with base-usable provenance reaches
   the statutory window check. Outside relative years `1..10`, raise
   `ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE` with exactly `fee_year_key`,
   `grant_fee_year_key` and `grant_relative_year` in `.details`.
5. Inside the window, delegate to `validate_fee_reduction()` and return its result
   unchanged. All remaining approval and scope failures therefore retain the base
   validator error surface.

The wrapper is a pure function: no ORM/database access, I/O, clock read, mutation,
logging, money calculation or rounding.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): validator, approval service

### Shared ownership serialization

- `backend/app/modules/fees/annuity_reduction.py` is isolated task ownership. There is no shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01.md`
- `backend/app/modules/fees/annuity_reduction.py`
- `backend/tests/test_v8_annuity_first_ten_year_reduction_scope.py`
- `artifacts/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Exact TDD Acceptance Matrix

`backend/tests/test_v8_annuity_first_ten_year_reduction_scope.py` MUST test the public
wrapper only and MUST prove:

1. The exact keyword-only signature, base result return annotation, error inheritance,
   read-only code/details and pure-module boundary.
2. Both patent-year keys reject booleans, non-integers and values below `1` with the
   exact first wrapper code, field detail and precedence.
3. Each of the three exact annual-fee codes is accepted; any other code raises the
   exact unsupported-code error before ratio, window or base approval validation.
4. Grant year derives relative year `1`, the tenth year derives `10`, and both legal
   non-zero ratios delegate successfully on both inclusive boundaries.
5. The year before grant derives `0` and the eleventh year derives `11`; both raise
   the exact out-of-scope code/details for a legal non-zero ratio.
6. Legal explicit zero delegates without a statutory-window check, including outside
   relative years `1..10`, and returns the base result unchanged.
7. Missing, illegal and ambiguous ratios plus unusable/ambiguous provenance preserve
   the exact base `FeeReductionValidationError` even outside the statutory window.
8. Inside the window, unconfirmed/non-current/source-less approval and fee/year/date
   scope mismatches preserve the exact base validator errors; inputs are unchanged.

Tests MUST NOT access ORM/database, filesystem, network or clock behavior, and MUST NOT
calculate or round money.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_first_ten_year_reduction_scope.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_first_ten_year_reduction_scope.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/annuity_reduction.py tests/test_v8_annuity_first_ten_year_reduction_scope.py && .venv/bin/ruff format app/modules/fees/annuity_reduction.py tests/test_v8_annuity_first_ten_year_reduction_scope.py && .venv/bin/ruff check app/modules/fees/annuity_reduction.py tests/test_v8_annuity_first_ten_year_reduction_scope.py`
- `git diff --check -- backend/app/modules/fees/annuity_reduction.py backend/tests/test_v8_annuity_first_ten_year_reduction_scope.py tasks/postdemo/v8/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01` pass. Only then may this task be reported PASS.
