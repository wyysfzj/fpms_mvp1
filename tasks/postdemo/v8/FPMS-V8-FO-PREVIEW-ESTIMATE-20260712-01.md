# FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `104`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `532`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Ultra Contract Freeze — 2026-07-13

The prior High readiness audit correctly stopped before RED because the V8 design and
foundation DTOs did not freeze the callable, rate-provider boundary, effective-date
source, fail-closed source errors or the exact mapping from a rate selection to a
`FeeEstimate`. This section resolves only that ambiguity. It does not activate a rate
book, approve a fee amount or add a new trigger/rate rule.

### Source reconciliation and precedence

- `PreviewFeeEstimateCommand`, `FeeEstimate`, `FeeEstimateCandidate`,
  `FeeObligationLineInput`, `FeeEstimateSource`, `FeeEstimateStatus`,
  `FeeSourceStatus` and `FeeDifferenceReviewState` from
  `backend/app/modules/fees/obligation_contracts.py` are the only public fee-obligation
  command/result shapes for this task. High must not return the legacy preview `dict`.
- The task-local provider seam below isolates the read-only estimator from SQLAlchemy and
  from the not-yet-activated official rate book. This allows deterministic High TDD with
  a fake provider without treating current seed values as legal authority.
- A production provider may select only an enabled GOV `FeeRate` linked through
  `FeeRate.official_rate_book_id` to the single approved, active, effective CNIPA
  `OfficialRateBook`. The carrier and source-activation tasks remain authoritative for
  that provenance. A legacy unlinked `FeeRate`, customer workbook value, Tianyue value,
  `source_status=None` or the legacy string `CONFIRMED` is not a verified V8 official
  source.
- The current `fees.service.preview_official_fee_candidates()` is not the provider and
  must not be called or wrapped by this service: it reads unlinked legacy rates, uses an
  implicit `date.today()`, normalizes/clamps reduction input and returns no
  `fee_year_key` or frozen V8 source/result contract. The later HTTP adapter may preserve
  its route but must use this V8 service/provider path without a legacy fallback.

### Exact task-owned public contract

`backend/app/modules/fees/obligation_service.py` must expose these task-owned names. The
file will later contain other serialized fee-obligation services, so this task does not
freeze a file-wide `__all__`:

```python
class FeeEstimatePreviewErrorCode(str, Enum):
    INVALID_COMMAND = "FEE_ESTIMATE_INVALID_COMMAND"
    TRIGGER_UNSUPPORTED = "FEE_ESTIMATE_TRIGGER_UNSUPPORTED"
    RATE_MISSING = "FEE_ESTIMATE_RATE_MISSING"
    RATE_SOURCE_UNAPPROVED = "FEE_ESTIMATE_RATE_SOURCE_UNAPPROVED"
    RATE_SOURCE_AMBIGUOUS = "FEE_ESTIMATE_RATE_SOURCE_AMBIGUOUS"
    RATE_SOURCE_INVALID = "FEE_ESTIMATE_RATE_SOURCE_INVALID"
    CANDIDATE_INVALID = "FEE_ESTIMATE_CANDIDATE_INVALID"

@dataclass(frozen=True, slots=True)
class OfficialFeeEstimateRateCandidate:
    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: Decimal
    source: FeeEstimateSource
    reduction_input: FeeReductionInput
    reduction_context: FeeReductionEvaluationContext
    reduction_approval: FeeReductionApprovalContext | None

class OfficialFeeEstimateRateProvider(Protocol):
    def select_rate_candidates(
        self,
        *,
        command: PreviewFeeEstimateCommand,
        rate_effective_on: date,
    ) -> tuple[OfficialFeeEstimateRateCandidate, ...]: ...

def preview_estimate(
    *,
    command: PreviewFeeEstimateCommand,
    rate_effective_on: date,
    rate_provider: OfficialFeeEstimateRateProvider,
) -> FeeEstimate:
```

`FeeEstimatePreviewError` is the only task-owned expected service exception other than
the deliberately propagated `FeeReductionValidationError`. It subclasses `ValueError`,
has exact constructor
`__init__(self, code: FeeEstimatePreviewErrorCode, details: dict[str, str | int | bool | None]) -> None`,
exposes `code` and a defensive copy of `details`, and initializes its base message to
`code.value`. The service does not import FastAPI or construct an HTTP response.

The protocol is structurally typed; no runtime `isinstance` check or abstract base class
is required. Provider implementations are read-only. They must not create an obligation,
draft, fee item, activity or any other row and must not call `commit`, `flush`, `add`,
`delete` or mutate a supplied object.

### Exact command and effective-date validation

Validation is deterministic and does not normalize identifiers:

1. `command` must be an exact `PreviewFeeEstimateCommand` instance.
2. `case_id`, `trigger_context.trigger` and `currency` are nonempty strings equal to
   their own `.strip()` value. `currency` is exactly three uppercase ASCII letters.
3. `trigger_context.source_document_id` is either `None` or a nonempty stripped string.
4. `rate_effective_on` is an exact `date`, not `datetime`. The service never reads the
   system clock.

The first invalid field raises `INVALID_COMMAND` with exactly `{"field": <field-name>}`
in this order: `command`, `case_id`, `trigger_context`, `trigger`,
`source_document_id`, `currency`, `rate_effective_on`. Trigger vocabulary remains open
in the foundation DTO, so the service does not hard-code only the two legacy triggers.
When a provider has no approved rule for a syntactically valid trigger, it raises
`TRIGGER_UNSUPPORTED` with exactly `{"trigger": command.trigger_context.trigger}`.

### Exact rate-provider selection contract

For one command/effective date, the provider must return a deterministic tuple in legal
display order. Each returned row is the already trigger-specific **full line amount**,
not a unit price: quantity/tier/formula application belongs to the provider's separately
approved trigger/rate rule. This service preserves provider order.

For a production provider, each selection must satisfy all of the following:

1. the case/trigger rule identifies the required official fee code and explicit
   `fee_year_key`; `0` means non-annual and a positive integer means that annual year;
2. `FeeRate.fee_type == "GOV"`, `enabled is True`, currency equals the command and both
   the rate interval and linked book interval contain `rate_effective_on` inclusively;
3. the linked book has `source_authority == "CNIPA"`, `approval_status == "APPROVED"`,
   `activation_status == "ACTIVE"` and the exact current identity key frozen by the
   carrier task;
4. there is exactly one selection per `(fee_code, fee_year_key)`; zero matching rows for
   a required code is missing, and more than one is ambiguous;
5. the returned `FeeEstimateSource` maps the selected rate/book exactly as follows:

| `FeeEstimateSource` field | Exact production-provider value |
| --- | --- |
| `rate_id` | `FeeRate.id` |
| `source_document_id` | `command.trigger_context.source_document_id` |
| `source_doc` | `OfficialRateBook.source_version` |
| `source_url` | `OfficialRateBook.source_reference` |
| `source_policy` | `OfficialRateBook.book_code` |
| `source_version` | `OfficialRateBook.version_code` |
| `status` | `FeeSourceStatus.VERIFIED` |

The provider uses the following exact fail-closed codes before returning a tuple:

- no approved rule for the trigger: `TRIGGER_UNSUPPORTED`;
- a required code has no effective linked verified rate: `RATE_MISSING`;
- a candidate/book exists but is not approved and active: `RATE_SOURCE_UNAPPROVED`;
- more than one effective selection exists for one `(fee_code, fee_year_key)`:
  `RATE_SOURCE_AMBIGUOUS`;
- the linked source tuple/provenance is malformed or inconsistent:
  `RATE_SOURCE_INVALID`.

Provider errors use these exact detail shapes:

| Code | Exact `details` keys |
| --- | --- |
| `TRIGGER_UNSUPPORTED` | `trigger` |
| `RATE_MISSING` | `fee_code`, `fee_year_key`, `rate_effective_on` |
| `RATE_SOURCE_UNAPPROVED` | `fee_code`, `fee_year_key`, `rate_id` |
| `RATE_SOURCE_AMBIGUOUS` | `fee_code`, `fee_year_key`, `rate_effective_on` |
| `RATE_SOURCE_INVALID` | `fee_code`, `fee_year_key`, `field` |

Dates in details are ISO strings. A provider that cannot identify a rate uses
`rate_id=None`; a trigger rule must still identify the required `fee_code` and
`fee_year_key`. The provider must raise rather than omit a required fee candidate.

### Candidate validation, fee-reduction boundary and amount mapping

After the provider returns, the service validates in tuple order:

1. the provider result must be an exact `tuple`; otherwise raise `CANDIDATE_INVALID`
   with field `rate_provider_result`;
2. an empty tuple raises `RATE_MISSING` with
   `{"fee_code": None, "fee_year_key": 0, "rate_effective_on": <ISO date>}`;
3. each item must be an exact `OfficialFeeEstimateRateCandidate`; otherwise raise
   `CANDIDATE_INVALID` with field `candidate`;
4. `fee_code` and `fee_name` must be nonempty stripped strings;
5. `fee_year_key` must be an exact non-boolean integer `>= 0`;
6. `official_full_amount` must be a finite, non-negative `Decimal` already equal to its
   two-decimal `ROUND_HALF_UP` quantization;
7. a repeated `(fee_code, fee_year_key)` raises `RATE_SOURCE_AMBIGUOUS`;
8. `source` must be an exact `FeeEstimateSource`; otherwise raise
   `RATE_SOURCE_INVALID` with field `source`;
9. `source.status` must be exactly `FeeSourceStatus.VERIFIED`; otherwise raise
   `RATE_SOURCE_UNAPPROVED`;
10. `rate_id`, `source_doc`, `source_url`, `source_policy` and `source_version` must each
   be a nonempty stripped string, and `source.source_document_id` must equal
   `command.trigger_context.source_document_id`; otherwise raise `RATE_SOURCE_INVALID`;
11. `reduction_input` and `reduction_context` must be exact frozen validator DTOs and
    `reduction_approval` must be `None` or an exact `FeeReductionApprovalContext`;
    otherwise raise `CANDIDATE_INVALID` using the first field in that order;
12. reduction context `case_id`, `fee_code`, `fee_year_key` and `as_of_date` must equal
   the command/candidate/effective date exactly; otherwise raise `CANDIDATE_INVALID`;
13. call `validate_fee_reduction(reduction_input=..., context=...,
   approval=...)` exactly once. `FeeReductionValidationError` propagates unchanged.

`CANDIDATE_INVALID` has exactly `{"fee_code": <value-or-None>, "fee_year_key":
<value-or-0>, "field": <field-name>}`. The service validates candidate fields in the
order written above and never coerces a wrong type. For deterministic error details,
`fee_code` is the exact value only when it is a string, otherwise `None`, and
`fee_year_key` is the exact value only when it is a non-boolean integer, otherwise `0`.
Provider/service errors map to HTTP
400 only for `INVALID_COMMAND` and `TRIGGER_UNSUPPORTED`; every other provider/service
error and every `FeeReductionValidationError` maps to 409 at the later adapter boundary.

For each valid selection the service constructs exactly:

```python
FeeEstimateCandidate(
    line=FeeObligationLineInput(
        fee_code=selection.fee_code,
        fee_name=selection.fee_name,
        fee_year_key=selection.fee_year_key,
        official_full_amount=selection.official_full_amount,
        reduction_ratio=reduction.reduction_ratio,
        payable_amount=(
            selection.official_full_amount * reduction.payable_ratio
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        source_amount=None,
        source_date=rate_effective_on,
        difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
    ),
    source=selection.source,
)
```

`FeeEstimate` echoes `case_id`, the exact `trigger_context` object and currency; sets
`estimate_status=FeeEstimateStatus.ESTIMATE`; stores the candidate tuple in provider
order; and sets `total_payable_amount` to the sum of the already rounded line payable
amounts, quantized to two decimals with `ROUND_HALF_UP`. The result contains no generated
identifier.

### Date and deadline boundary

- `rate_effective_on` is the explicit date used to choose the legally effective rate/book.
  It is copied to `FeeObligationLineInput.source_date` as the amount/rate applicability
  date required by F2. It is not a payment deadline.
- The frozen `FeeEstimate` shape has no `due_date` or deadline-source field. Therefore this
  service must not guess, calculate, parse or hide a due date. The legacy
  `deadline_rule` prose is not a structured date and is not mapped into
  `source_date`.
- A source-backed official due date belongs to recognized obligation input/result after
  an actual notice or reviewed source event. If a future estimate UI needs a distinct
  estimated due-date/source pair, that requires a separately approved contracts task;
  High must not add fields here.

### Frozen RED / GREEN test contract

`backend/tests/test_v8_fee_estimate_read_only.py` must prove at least:

1. the exact enum values, frozen/slotted candidate fields, Protocol method signature,
   keyword-only service signature and error code/details behavior;
2. invalid command fields fail in the frozen order without calling the provider;
3. a fake provider receives the exact command and explicit effective date once;
4. provider errors for unsupported, missing, unapproved, ambiguous and invalid source
   propagate with exact code/details;
5. empty, malformed, duplicate and non-VERIFIED selections fail closed;
6. non-annual `fee_year_key=0` and a positive annual key are preserved;
7. source fields map unchanged, `source_amount is None`, `source_date` equals the explicit
   rate effective date and difference state is `SOURCE_PENDING`;
8. explicit zero and approved `0.7/0.85` pass only through the frozen fee-reduction
   validator, with half-up line rounding and sum-of-rounded-lines totals;
9. provider tuple order is preserved and neither input objects nor provider results are
   mutated;
10. no obligation, draft, fee item or activity ID is present in the result, and the
    service performs no SQLAlchemy/model import, transaction call, clock read, UUID
    generation or persistence side effect.

The task-owned test uses a pure fake provider and performs no SQLite write. It must not
insert or assert a real legal fee amount; synthetic amounts are labeled test fixtures.

## Exact Closure Slice

Read-only estimate returns candidates and creates no obligation/draft/activity.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-CONTRACTS-20260712-01`
- `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): contracts
- Ultra freeze dependency delta: the exact service calls the frozen pure fee-reduction
  validator, so High must complete `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01` first.

### Shared ownership serialization

- `backend/app/modules/fees/obligation_service.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01.md`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_fee_estimate_read_only.py`
- `artifacts/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_estimate_read_only.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_estimate_read_only.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_estimate_read_only.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_estimate_read_only.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_estimate_read_only.py`
- `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_estimate_read_only.py tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01` pass. Only then may this task be reported PASS.
