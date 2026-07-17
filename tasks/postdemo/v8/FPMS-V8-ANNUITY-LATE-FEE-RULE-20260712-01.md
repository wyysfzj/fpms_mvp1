# FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `134`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/postdemo/文件样例及模版/常见官文样例/年费缴费通知书.PDF`
- `artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/专利收费场景-20260626.txt`
- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/analysis/source_ledger.md`
- `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`
- `https://www.cnipa.gov.cn/jact/front/mailpubdetail.do?sysid=6&transactId=486612`
- Source catalog line: `576`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Exact Closure Slice

Implement one pure rule that calculates an annuity late fee from the unreduced full annual fee for one statutory due date and one actual payment date. The fallback statutory bands are exactly 0%, 5%, 10%, 15%, 20% and 25%; the six-calendar-month endpoint is inclusive and any later date fails closed. When reviewed official-notice bands are supplied, their inclusive date bands and stated amounts take precedence for matching dates under the frozen validation and gap rules below.

## Frozen Public Contract (FIXED)

Create `backend/app/modules/fees/late_fee.py`. Its complete public export surface MUST be exactly:

```python
__all__ = (
    "AnnuityLateFeeCalculationSource",
    "AnnuityLateFeeErrorCode",
    "AnnuityLateFeeNotificationBand",
    "CalculateAnnuityLateFeeCommand",
    "AnnuityLateFeeResult",
    "AnnuityLateFeeRuleError",
    "calculate_annuity_late_fee",
)
```

The public callable MUST have this exact positional-only signature and MUST perform no I/O, ORM access, mutation, clock read or persistence:

```python
def calculate_annuity_late_fee(
    command: CalculateAnnuityLateFeeCommand, /
) -> AnnuityLateFeeResult:
    ...
```

The enums and immutable input/result contracts MUST be exactly:

```python
class AnnuityLateFeeCalculationSource(str, Enum):
    STATUTORY = "STATUTORY"
    NOTIFICATION = "NOTIFICATION"


class AnnuityLateFeeErrorCode(str, Enum):
    INVALID_FULL_ANNUAL_FEE = "INVALID_FULL_ANNUAL_FEE"
    PAYMENT_BEFORE_DUE_DATE = "PAYMENT_BEFORE_DUE_DATE"
    PAYMENT_AFTER_LATE_WINDOW = "PAYMENT_AFTER_LATE_WINDOW"
    INVALID_NOTIFICATION_BAND = "INVALID_NOTIFICATION_BAND"
    NOTIFICATION_BAND_OVERLAP = "NOTIFICATION_BAND_OVERLAP"
    NOTIFICATION_BAND_GAP = "NOTIFICATION_BAND_GAP"


@dataclass(frozen=True, slots=True)
class AnnuityLateFeeNotificationBand:
    start_date: date
    end_date: date
    rate: Decimal
    amount: Decimal
    source_document_id: str


@dataclass(frozen=True, slots=True)
class CalculateAnnuityLateFeeCommand:
    full_annual_fee: Decimal
    statutory_due_date: date
    payment_date: date
    notification_bands: tuple[AnnuityLateFeeNotificationBand, ...] = ()


@dataclass(frozen=True, slots=True)
class AnnuityLateFeeResult:
    full_annual_fee: Decimal
    statutory_due_date: date
    payment_date: date
    rate: Decimal
    late_fee_amount: Decimal
    band_start_date: date
    band_end_date: date
    calculation_source: AnnuityLateFeeCalculationSource
    source_document_id: str | None
```

`AnnuityLateFeeRuleError` MUST subclass `ValueError`, expose the selected `AnnuityLateFeeErrorCode` as a read-only `code` attribute, and use `code.value` as its exact exception message. No other public exception or result type is permitted.

## Frozen Statutory Calendar-Month Algorithm (FIXED)

Define the internal calendar-month anniversary `M(n)` as `statutory_due_date` plus `n` calendar months. Preserve the original day when that day exists in the target month; otherwise clamp to the target month's final day. Do not use a fixed day count. Examples: `2025-01-31 + 1 month = 2025-02-28`, `2024-08-31 + 6 months = 2025-02-28`, and `2023-08-31 + 6 months = 2024-02-29`.

The payment-date bands are inclusive at both ends as stated below:

| Payment date | Rate | Result band |
| --- | ---: | --- |
| `statutory_due_date` through `M(1) - 1 day` | `Decimal("0")` | those two dates |
| `M(1)` through `M(2) - 1 day` | `Decimal("0.05")` | those two dates |
| `M(2)` through `M(3) - 1 day` | `Decimal("0.10")` | those two dates |
| `M(3)` through `M(4) - 1 day` | `Decimal("0.15")` | those two dates |
| `M(4)` through `M(5) - 1 day` | `Decimal("0.20")` | those two dates |
| `M(5)` through `M(6)` | `Decimal("0.25")` | those two dates |

- `payment_date == statutory_due_date` is valid and returns the 0% band.
- `payment_date < statutory_due_date` raises `PAYMENT_BEFORE_DUE_DATE`.
- `payment_date > M(6)` raises `PAYMENT_AFTER_LATE_WINDOW`; do not continue returning a capped 25% amount after the legal late-payment window.
- The rule uses `full_annual_fee`, never a reduced/payable annuity amount. `full_annual_fee` MUST be finite and strictly greater than zero; otherwise raise `INVALID_FULL_ANNUAL_FEE`.
- For a statutory result, calculate `full_annual_fee * rate` and quantize only the final amount to `Decimal("0.01")` with `ROUND_HALF_UP`. Preserve `full_annual_fee` unchanged in the result. This explicitly makes `Decimal("100.10") * Decimal("0.05")` return `Decimal("5.01")`.

## Frozen Official-Notification Precedence (FIXED)

`notification_bands` represent already reviewed and confirmed lines extracted from one or more official notices. The pure rule does not review, parse or persist those notices.

1. Band endpoints are inclusive. Input tuple order is not significant; validate after sorting by `(start_date, end_date, source_document_id)`.
2. Every band MUST have `start_date <= end_date`, lie wholly between `statutory_due_date` and `M(6)`, use one of the six frozen rates `0/0.05/0.10/0.15/0.20/0.25`, contain a finite non-negative `amount`, and contain a non-blank `source_document_id`. Any violation raises `INVALID_NOTIFICATION_BAND`.
3. Adjacent sorted bands MUST NOT overlap. `next.start_date <= previous.end_date` raises `NOTIFICATION_BAND_OVERLAP`.
4. Adjacent sorted bands MUST be contiguous. `next.start_date != previous.end_date + 1 day` raises `NOTIFICATION_BAND_GAP`.
5. If exactly one valid notice band contains `payment_date`, return that band's `rate`, inclusive boundaries, `source_document_id` and stated `amount`. Quantize the stated amount to `Decimal("0.01")` with `ROUND_HALF_UP`; do not recompute it from the annual fee. Set `calculation_source=NOTIFICATION`.
6. A notice may legitimately omit the leading 0% period. If no notice band contains `payment_date`, statutory fallback is allowed only when the statutory rate for that date is 0%. Set `calculation_source=STATUTORY` and `source_document_id=None` in that case.
7. If valid notice bands exist but no band contains a payment date whose statutory rate is non-zero, raise `NOTIFICATION_BAND_GAP`. Do not silently replace an incomplete official-notice schedule with a statutory estimate.
8. All statutory input/date validations run before notice-band selection. A notice band cannot extend or reopen the six-month late-payment window.

The customer sample demonstrates the required precedence shape: for a statutory due date of `2025-10-13`, its first stated 5% band begins `2025-11-13`, subsequent bands are calendar-contiguous, and its final 25% band ends on the inclusive six-month endpoint `2026-04-13`.

## Exact Error Ordering (FIXED)

When more than one condition is invalid, raise the first applicable code in this order:

1. `INVALID_FULL_ANNUAL_FEE`
2. `PAYMENT_BEFORE_DUE_DATE`
3. `PAYMENT_AFTER_LATE_WINDOW`
4. `INVALID_NOTIFICATION_BAND`
5. `NOTIFICATION_BAND_OVERLAP`
6. `NOTIFICATION_BAND_GAP`

## Explicit Non-Closure

No annuity due-date derivation, first-ten-year reduction, annual-fee rate lookup/activation, notice parsing/review, obligation creation, payment sufficiency or restoration calculation. No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup. In particular, a restoration-procedure 25% amount after termination is not this rule and MUST NOT be added.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-CONTRACTS-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): contracts

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01.md`
- `backend/app/modules/fees/late_fee.py`
- `backend/tests/test_v8_annuity_late_fee.py`
- `artifacts/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Exact TDD Acceptance Matrix

`backend/tests/test_v8_annuity_late_fee.py` MUST test the public callable only and MUST include all of these named cases:

1. Public `__all__`, exact callable signature, enum values, dataclass field order and frozen/slots behavior.
2. Due date and the day before `M(1)` return 0%; `M(1)` returns 5%; each later anniversary switches exactly to 10%, 15%, 20% and 25%; `M(6)` remains 25%; `M(6) + 1 day` raises `PAYMENT_AFTER_LATE_WINDOW`.
3. Month-end clamping for `2025-01-31`, the non-leap six-month endpoint from `2024-08-31`, and the leap six-month endpoint from `2023-08-31`.
4. Full annual fee `Decimal("1200")` with reduced payable context deliberately absent: statutory 5% returns `Decimal("60.00")`; final-amount `ROUND_HALF_UP` returns `Decimal("5.01")` for `Decimal("100.10")` at 5%.
5. A matching reviewed notice band with amount `Decimal("61")` at 5% overrides the statutory `Decimal("60.00")`, returns its exact inclusive dates/source document, and reports `NOTIFICATION`.
6. The real-sample shape `2025-11-13..2025-12-12`, `2025-12-13..2026-01-12`, `2026-01-13..2026-02-12`, `2026-02-13..2026-03-12`, `2026-03-13..2026-04-13` is accepted for due date `2025-10-13`; a payment before the first band in the statutory 0% period falls back to `STATUTORY`.
7. Each invalid full-fee form (zero, negative, NaN and infinity), payment before due date, and payment after six months raises the exact ordered code/message.
8. Invalid notice range/source/rate/amount/outside-window inputs raise `INVALID_NOTIFICATION_BAND`; overlapping bands raise `NOTIFICATION_BAND_OVERLAP`; an internal gap or an uncovered non-zero payment date raises `NOTIFICATION_BAND_GAP`.

Tests MUST NOT instantiate ORM models, write SQLite, read the clock/network/filesystem, activate rates, or test restoration, persistence, API or UI behavior.

## Policy and Provenance Gates

- No customer decision gate blocks this pure statutory rule.
- Upstream code MAY pass `notification_bands` only after the source official notice is reviewed/confirmed and its source document ID is retained. That provenance review is a caller precondition and is not implemented or inferred here.
- The caller owns the canonical statutory due date. This task MUST NOT recalculate or overwrite `AnnuityTask.due_date`.
- Official-rate-book approval and activation remain separate tasks. This rule accepts the caller-supplied unreduced full annual fee and does not select a rate version.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_late_fee.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_late_fee.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/late_fee.py tests/test_v8_annuity_late_fee.py && .venv/bin/ruff format app/modules/fees/late_fee.py tests/test_v8_annuity_late_fee.py && .venv/bin/ruff check app/modules/fees/late_fee.py tests/test_v8_annuity_late_fee.py`
- `git diff --check -- backend/app/modules/fees/late_fee.py backend/tests/test_v8_annuity_late_fee.py tasks/postdemo/v8/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01` pass. Only then may this task be reported PASS.
