# FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `93`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `516`
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

- RED expectation: importing the exact frozen public contract below fails because `backend/app/modules/fees/fee_reduction.py` does not exist.
- GREEN expectation: the exact pure-rule test passes the frozen explicit-zero, approved-ratio, boundary and fail-closed matrix below without persistence, FastAPI or unrelated fee-policy behavior.

## Exact Closure Slice

Pure rule accepts explicit `0`; requires confirmed scoped approval for `0.7/0.85`; rejects missing/illegal/ambiguous values.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

The prior High readiness audit correctly stopped before RED because the approved V8 design froze the business rule but not its callable, typed boundary, result or stable error surface. This section resolves only that implementation ambiguity; it does not approve fee reduction for any customer, applicant set, case, fee or year.

### Source reconciliation and precedence

- The customer answer confirms that `0.85` and `0.7` are **reduction ratios**, producing payable ratios `0.15` and `0.30`; it also describes an unselected legacy/default value as `0`.
- Canonical V8 deliberately tightens that legacy behavior: only a current explicit entry or a confirmed migration may mean `0`; missing, unverified legacy and ambiguous values must not be coerced to `0`.
- The customer fee scenario and approval-notice evidence confirm that approval applicability is per fee scope, fee year and effective period. The validator therefore consumes an already parsed, source-backed approval snapshot and never manufactures a default approval scope.
- F5 is the persisted carrier. The later approval-record/read services own ORM queries, canonical JSON/hashes, applicant-set key generation, duplicate/current-row resolution and transaction behavior. This task owns only deterministic validation and reduction-to-payable conversion.

### Exact public module contract

`backend/app/modules/fees/fee_reduction.py` must export exactly these task-owned public names through `__all__`, in this order:

```python
__all__ = (
    "FeeReductionInputProvenance",
    "FeeReductionApprovalScopeType",
    "FeeReductionErrorCode",
    "FeeReductionInput",
    "FeeReductionEvaluationContext",
    "FeeReductionApprovalContext",
    "FeeReductionValidationResult",
    "FeeReductionValidationError",
    "validate_fee_reduction",
)
```

Enums are `class X(str, Enum)` with exactly these members and wire values:

```python
class FeeReductionInputProvenance(str, Enum):
    EXPLICIT_ENTRY = "EXPLICIT_ENTRY"
    CONFIRMED_MIGRATION = "CONFIRMED_MIGRATION"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"
    UNKNOWN = "UNKNOWN"

class FeeReductionApprovalScopeType(str, Enum):
    CASE = "CASE"
    APPLICANT_SET = "APPLICANT_SET"

class FeeReductionErrorCode(str, Enum):
    MISSING_REDUCTION_VALUE = "FEE_REDUCTION_MISSING_VALUE"
    AMBIGUOUS_REDUCTION_PROVENANCE = "FEE_REDUCTION_AMBIGUOUS_PROVENANCE"
    ILLEGAL_REDUCTION_VALUE = "FEE_REDUCTION_ILLEGAL_VALUE"
    INVALID_EVALUATION_CONTEXT = "FEE_REDUCTION_INVALID_CONTEXT"
    APPROVAL_REQUIRED = "FEE_REDUCTION_APPROVAL_REQUIRED"
    APPROVAL_INVALID = "FEE_REDUCTION_APPROVAL_INVALID"
    APPROVAL_NOT_CONFIRMED = "FEE_REDUCTION_APPROVAL_NOT_CONFIRMED"
    APPROVAL_NOT_CURRENT = "FEE_REDUCTION_APPROVAL_NOT_CURRENT"
    APPROVAL_SOURCE_MISSING = "FEE_REDUCTION_APPROVAL_SOURCE_MISSING"
    APPROVAL_RATIO_MISMATCH = "FEE_REDUCTION_APPROVAL_RATIO_MISMATCH"
    APPROVAL_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_SCOPE_MISMATCH"
    APPROVAL_FEE_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_FEE_SCOPE_MISMATCH"
    APPROVAL_YEAR_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_YEAR_SCOPE_MISMATCH"
    APPROVAL_EFFECTIVE_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_EFFECTIVE_SCOPE_MISMATCH"
```

The four DTOs are `@dataclass(frozen=True, slots=True)` with exactly these fields and order:

```python
class FeeReductionInput:
    reduction_ratio: Decimal | None
    provenance: FeeReductionInputProvenance

class FeeReductionEvaluationContext:
    case_id: str
    applicant_set_key: str | None
    fee_code: str
    fee_year_key: int
    as_of_date: date

class FeeReductionApprovalContext:
    approval_id: str
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_codes: frozenset[str]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmation_status: str
    is_current: bool

class FeeReductionValidationResult:
    reduction_ratio: Decimal
    payable_ratio: Decimal
    provenance: FeeReductionInputProvenance
    approval_id: str | None
    source_evidence_version_id: str | None
    scope_type: FeeReductionApprovalScopeType | None
```

The exact callable is pure and keyword-only:

```python
def validate_fee_reduction(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
) -> FeeReductionValidationResult:
```

It performs no ORM query, I/O, mutation, logging, clock read or rounding of money. The caller supplies `as_of_date`; all date and year interval bounds are inclusive.

### Canonical input and result semantics

- `reduction_ratio` accepts only a finite `Decimal` or `None` at this pure-rule boundary. Strings, floats, booleans, integers and non-finite `Decimal` values are illegal; request-schema parsing belongs to an adapter and malformed request representation remains HTTP 422 before this rule.
- The only legal normalized reduction ratios are exactly `Decimal("0.0000")`, `Decimal("0.7000")` and `Decimal("0.8500")`. A finite input must first compare numerically equal to `Decimal("0")`, `Decimal("0.7")` or `Decimal("0.85")`; only then is the matching four-decimal constant returned. Numerically equal values such as `Decimal("0.70")` and `Decimal("0.850")` therefore normalize, while a nearby value must not become legal through quantization. No clamping or nearest-value rounding is allowed.
- `EXPLICIT_ENTRY` means the current action explicitly selected the value. `CONFIRMED_MIGRATION` means a separately audited migration confirmed the same meaning. Those are the only usable provenances.
- `LEGACY_UNVERIFIED` and `UNKNOWN` always fail as ambiguous, including when their numeric value is zero. `None` always fails as missing. This is the explicit zero-versus-missing/legacy boundary.
- Valid zero returns reduction `0.0000`, payable `1.0000` and all three approval fields as `None`. An available approval may be passed but is not applied, inspected or returned for a zero selection.
- Valid approved `0.7000` returns payable `0.3000`; valid approved `0.8500` returns payable `0.1500`. The result returns the matched approval id, source evidence id and scope type.
- The rule validates approval applicability only; it does not calculate a money amount. Amount quantization belongs to the fee-line calculation task.

### Approval and evaluation applicability

Evaluation context is structurally valid only when `case_id` and `fee_code` are nonempty strings equal to their own `.strip()` value, `fee_year_key` is an exact non-boolean `int >= 0`, and `as_of_date` is an exact `date` rather than `datetime`. No identifier is implicitly trimmed. `fee_year_key == 0` is the canonical non-annual sentinel; positive values are annual fee years. `applicant_set_key` may be null unless an APPLICANT_SET approval is evaluated.

For `0.7000/0.8500`, exactly one supplied approval snapshot must meet every condition:

1. `approval_id` is a nonempty stripped string; its ratio is a finite legal `Decimal`; `fee_codes` is a nonempty `frozenset` of nonempty stripped exact fee-code strings; its effective values are exact `date` values rather than `datetime` and are ordered; and its year bounds are either both null or both exact non-boolean positive integers with `from <= to`.
2. Scope is physically exclusive: CASE has nonblank `case_id` and null `applicant_set_key`; APPLICANT_SET has null `case_id` and nonblank `applicant_set_key`.
3. `confirmation_status` is exactly `CONFIRMED` and `is_current is True`.
4. `source_evidence_version_id` is nonblank.
5. Approval ratio equals the requested normalized ratio.
6. CASE scope matches `context.case_id`; APPLICANT_SET scope matches non-null `context.applicant_set_key` exactly.
7. `context.fee_code` is an exact member of `approval.fee_codes`. No hard-coded statutory fee list or wildcard is introduced here.
8. For `fee_year_key == 0`, both approval year bounds must be null. For `fee_year_key > 0`, both bounds must be non-null and contain that year inclusively.
9. `effective_from <= context.as_of_date <= effective_to` when an end date exists; a null end is open-ended.

`is_current` is a read-adapter fact, not a new F5 database column. A future read service must fail before constructing this DTO if persistence yields missing or multiple current approval records; this validator still rejects an explicitly non-current snapshot.

### Stable fail-closed exception and HTTP boundary

`FeeReductionValidationError` is the only expected business exception from the callable. It subclasses `ValueError` and has exact constructor `__init__(self, code: FeeReductionErrorCode, details: dict[str, str | int | bool | None]) -> None`. It exposes `code` and a defensive copy of `details`, and initializes its base message to `code.value`. Detail values must be JSON-safe primitives; tests compare the exact code and required detail keys, not localized prose. A runtime provenance value that is not one of the four enum members is treated as ambiguous and reported through `AMBIGUOUS_REDUCTION_PROVENANCE`.

Validation stops at the first failure in this exact order:

1. missing reduction value;
2. illegal runtime type/non-finite value;
3. ambiguous provenance;
4. illegal ratio vocabulary;
5. invalid evaluation context;
6. missing approval;
7. malformed approval snapshot/exclusivity/intervals;
8. not confirmed;
9. not current;
10. missing source evidence;
11. ratio mismatch;
12. case/applicant-set scope mismatch;
13. fee-code scope mismatch;
14. year scope mismatch;
15. effective-date scope mismatch.

Within step 5, invalid evaluation fields are checked in `case_id`, `fee_code`, `fee_year_key`, `as_of_date` order. Within step 7, malformed approval fields are checked in `approval_id`, `reduction_ratio`, `fee_codes`, `effective_from`, `effective_to`, `fee_year_from`, `fee_year_to`, `scope_type`, `case_id/applicant_set_key`, `confirmation_status`, `is_current` order. A wrong runtime type for `confirmation_status` or `is_current` is `APPROVAL_INVALID`; a correctly typed but non-`CONFIRMED` status or false current flag proceeds to steps 8 or 9.

The exact required detail keys are:

| Error code member | Required `details` keys |
| --- | --- |
| `MISSING_REDUCTION_VALUE` | `field` |
| `ILLEGAL_REDUCTION_VALUE` | `field`, `value` |
| `AMBIGUOUS_REDUCTION_PROVENANCE` | `provenance` |
| `INVALID_EVALUATION_CONTEXT` | `field` |
| `APPROVAL_REQUIRED` | `reduction_ratio`, `case_id`, `fee_code`, `fee_year_key`, `as_of_date` |
| `APPROVAL_INVALID` | `approval_id`, `field` |
| `APPROVAL_NOT_CONFIRMED` | `approval_id`, `confirmation_status` |
| `APPROVAL_NOT_CURRENT` | `approval_id` |
| `APPROVAL_SOURCE_MISSING` | `approval_id`, `field` |
| `APPROVAL_RATIO_MISMATCH` | `approval_id`, `requested_ratio`, `approval_ratio` |
| `APPROVAL_SCOPE_MISMATCH` | `approval_id`, `scope_type` |
| `APPROVAL_FEE_SCOPE_MISMATCH` | `approval_id`, `fee_code` |
| `APPROVAL_YEAR_SCOPE_MISMATCH` | `approval_id`, `fee_year_key` |
| `APPROVAL_EFFECTIVE_SCOPE_MISMATCH` | `approval_id`, `as_of_date` |

Detail values are deterministic:

- `field` is the exact snake-case field name; physical scope exclusivity uses `case_id/applicant_set_key`.
- Legal requested/approval ratios in details use fixed four-decimal strings; an illegal input uses `str(value)` and a wrong runtime type therefore remains visible without coercion.
- Dates use ISO `YYYY-MM-DD`; `fee_year_key` remains an integer; booleans remain booleans.
- `approval_id`, `fee_code`, `confirmation_status` and scope identifiers preserve their exact input strings; `scope_type` and a recognized provenance use `.value`, while an unrecognized provenance uses `str(value)`.
- `APPROVAL_REQUIRED` therefore emits exactly `{"reduction_ratio": <four-place string>, "case_id": <exact string>, "fee_code": <exact string>, "fee_year_key": <int>, "as_of_date": <ISO date>}`. Other codes emit exactly the required-key set from the table, with no extra keys.

All `FeeReductionValidationError` codes map at an HTTP adapter boundary to business conflict `409`, preserving `code.value` and `details` inside the module's existing error-envelope convention. This pure module must not import FastAPI or construct an HTTP response. Request representation/type failures rejected before invocation remain 422; authentication, authorization and missing-resource mappings remain owned by their API/service tasks.

### Deterministic RED / GREEN matrix

The task-owned test must prove at least:

1. exact `__all__`, enum values, frozen/slotted DTO field names/order and keyword-only callable signature;
2. explicit current and confirmed-migration zero each return `0.0000/1.0000` without approval;
3. `None`, unverified legacy zero and unknown-provenance zero fail with the first exact code;
4. string, float, bool, integer, NaN, infinity, `0.15`, `0.30`, `1`, negative and greater-than-one inputs fail rather than clamp or reinterpret;
5. equivalent Decimal scales normalize to the exact four-place results;
6. confirmed/current/source-backed matching CASE approvals produce `0.7000/0.3000` and `0.8500/0.1500` results;
7. matching APPLICANT_SET approval succeeds only with the exact applicant-set key;
8. missing, malformed, unconfirmed, non-current or source-less approval snapshots fail with their exact ordered codes;
9. approval ratio, scope, fee code, non-annual/annual year and effective-date mismatches fail with their exact codes;
10. year start/end and effective start/end dates are accepted on both inclusive boundaries, while adjacent outside values fail;
11. the callable leaves every input DTO unchanged and imports no FastAPI or ORM model.

### Residual data gates and non-closure

- This task does not make any actual `0.7/0.85` selection executable by itself. A real, current, `CONFIRMED`, source-evidence-backed F5 approval record with exact fee/year/effective scope remains mandatory.
- Confirming a legacy zero is a separate migration/audit fact; this rule never self-confirms it.
- Building/parsing `fee_codes`, resolving current approval rows, calculating `applicant_set_key`, recording/reusing approvals and mapping API errors are later tasks.
- Statutory fee eligibility outside the recorded approval scope, PCT exemptions, open-license reduction, late fees, rate-book activation, obligation persistence, money rounding, endpoints, UI and migration/backfill are explicitly excluded.
- No unresolved customer decision gate is created or bypassed. The ratio meaning is already confirmed; per-case/per-applicant approval data remains source-dependent operational evidence.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F5

### Shared ownership serialization

- `backend/app/modules/fees/fee_reduction.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01.md`
- `backend/app/modules/fees/fee_reduction.py`
- `backend/tests/test_v8_fee_reduction_validator.py`
- `artifacts/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_validator.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_validator.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py && .venv/bin/ruff format app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py && .venv/bin/ruff check app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py`
- `git diff --check -- backend/app/modules/fees/fee_reduction.py backend/tests/test_v8_fee_reduction_validator.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01` pass. Only then may this task be reported PASS.
