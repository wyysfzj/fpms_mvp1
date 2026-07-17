# FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `94`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `517`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Record/reuse one confirmed CASE or canonical APPLICANT_SET approval with source/snapshot evidence, ratio, fee/year scope and interval; reject mixed scope and hash/snapshot conflicts.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for the one approval-record
service closure. It freezes creation and exact historical reuse only; it does not add a
current-approval model, overlap reader, endpoint, schema change or customer eligibility
policy.

### Frozen public interface

`fee_reduction_approval_service.py` imports the existing
`FeeReductionApprovalScopeType` and defines exactly the following task-owned public enum,
DTOs and synchronous callable. The enum inherits from `str, Enum`; member names and values
are identical. Both DTOs use `@dataclass(frozen=True, slots=True, kw_only=True)`, and field
order is exact.

```python
class FeeReductionApprovalRecordDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


class RecordFeeReductionApprovalCommand:
    case_id: str
    scope_type: FeeReductionApprovalScopeType
    applicant_ids: tuple[str, ...]
    eligibility_attributes_version: str
    eligibility_attributes_json: str
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    expected_source_content_hash: str
    confirmed_at: datetime
    confirmed_by: str


class RecordFeeReductionApprovalResult:
    approval_id: str
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_scope_snapshot: str
    fee_scope_hash: str
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmation_status: str
    confirmed_at: datetime
    confirmed_by: str
    eligibility_snapshot: str
    eligibility_snapshot_hash: str
    approval_identity_key: str
    disposition: FeeReductionApprovalRecordDisposition


def record_fee_reduction_approval(
    command: RecordFeeReductionApprovalCommand,
    transaction: Session,
) -> RecordFeeReductionApprovalResult:
    ...
```

The command deliberately contains no `applicant_set_key`, snapshot, digest,
`approval_identity_key`, confirmation status, generated ID or database timestamp. The
service rejects non-exact command/scope types and never accepts a raw mapping, caller-built
identity or caller-built snapshot in place of this interface.

### Exact input and approval rules

- Required strings are non-empty, equal to their own `strip()` value, contain no NUL and
  fit their existing carrier limit. No identifier, fee code, version or actor is trimmed,
  case-folded or inferred.
- `reduction_ratio` must be an exact `Decimal`, must be finite and must compare equal to
  exactly `Decimal("0.7")` or `Decimal("0.85")`; persist it normalized to four decimal
  places. Raw strings, integers, floats, booleans, `NaN`, infinities and every other value
  are invalid. `Decimal("0")` means no approval record is required and fails before any
  query or write with 400 `FEE_REDUCTION_APPROVAL_NOT_REQUIRED`.
- `applicant_ids` is an exact tuple of canonical IDs. Duplicate IDs are invalid rather
  than silently deduplicated. Ratio `0.85` requires exactly one applicant; ratio `0.7`
  requires at least two distinct applicants.
- `scope_type` is the exact existing enum. For `CASE`, the persisted identity is
  `case_id=command.case_id` and `applicant_set_key=None`. For `APPLICANT_SET`, the command's
  case remains the evidence-validation context, while the persisted identity is
  `case_id=None` and the service-computed `applicant_set_key`. Mixed or missing persisted
  scope identity is prohibited.
- `fee_codes` is a non-empty exact tuple of canonical codes. Duplicate codes are invalid;
  the service sorts them for the persisted set snapshot. Fee scope is always explicit and
  is never inferred from evidence, ratio, case category, rate book or fee name.
- Fee-year scope is either `(None, None)` for an explicitly non-annual scope or two exact,
  positive, non-boolean integers with `fee_year_from <= fee_year_to`. A half-open pair,
  zero, negative value or reversed pair is invalid. Both bounds are inclusive.
- `effective_from` is an exact `date`, not a `datetime`; `effective_to` is an exact `date`
  or `None`, and a non-null end must be on or after the start. Both bounds are inclusive.
  The service does not read a clock or infer dates.
- `confirmed_at` is a timezone-naive `datetime`; `confirmed_by` is an explicit canonical
  actor snapshot. New rows always store `confirmation_status="CONFIRMED"` and use that
  actor for `created_by` and `updated_by`. This task does not add an actor FK or invent a
  reviewer/qualifier role policy.

Invalid command shape or scope uses 400 `FEE_REDUCTION_APPROVAL_INVALID` with
`details.field`. Missing case or evidence uses 404 `CASE_NOT_FOUND` or
`EVIDENCE_VERSION_NOT_FOUND`. Persisted evidence/state corruption, snapshot conflict,
identity conflict or write race uses 409 `FEE_REDUCTION_APPROVAL_CONFLICT`; every error
path is write-free.

### Strict eligibility input and service-owned canonical facts

`eligibility_attributes_json` is input data, not a caller-built persisted snapshot. Parse
it as strict JSON: reject duplicate object keys at every depth, `NaN`/`Infinity`, non-JSON
types and a root other than an object. Its root keys must be exactly the distinct
`applicant_ids`; missing or extra applicant keys are invalid. Each value must be an object,
but its inner vocabulary remains opaque and is not interpreted as qualification.

All canonical JSON uses UTF-8 with
`json.dumps(..., ensure_ascii=False, sort_keys=True, separators=(",", ":"),
allow_nan=False)`. All SHA-256 values are the bare lowercase 64-character hex digest of
the canonical UTF-8 bytes. The service creates exactly these facts:

1. `fee_scope_snapshot` is canonical JSON of
   `{"fee_codes": <sorted unique codes>, "schema":
   "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}`; `fee_scope_hash` hashes that text.
2. `eligibility_snapshot` is canonical JSON of
   `{"applicants": [{"applicant_id": <id>, "attributes": <opaque object>}, ...],
   "attributes_version": <explicit version>, "schema":
   "FPMS_FEE_REDUCTION_ELIGIBILITY_V1"}` with applicants sorted by exact ID;
   `eligibility_snapshot_hash` hashes that text.
3. For `APPLICANT_SET` only, `applicant_set_key` hashes canonical JSON of
   `{"applicant_ids": <sorted IDs>, "eligibility_snapshot_hash": <hash>, "schema":
   "FPMS_FEE_REDUCTION_APPLICANT_SET_V1"}`. CASE never stores that key.
4. `approval_identity_key` hashes canonical JSON of exactly
   `source_evidence_version_id`, `scope_type`, `scope_id` (CASE ID or applicant-set key),
   four-place ratio text, `fee_scope_hash`, nullable year bounds, ISO effective bounds and
   schema `FPMS_FEE_REDUCTION_APPROVAL_IDENTITY_V1`. Generated IDs, actor/time and database
   timestamps are not identity members.

The exact record snapshot used for reuse is the complete persisted business projection:
scope identity, four-place ratio, both canonical snapshots and hashes, both explicit
intervals, source evidence ID, `CONFIRMED`, confirmer and confirmation time. Generated row
ID and database timestamps are excluded. Same identity with any different projected fact
is a conflict, never an overwrite or partial reuse.

### Evidence-at-record-time gate and immutable history

- Resolve the exact Case and `DocumentEvidenceVersion`. The version must belong to
  `command.case_id`, have exact state `FINAL`, exact review state `APPROVED`, and be the
  current version at initial record time. Its persisted `content_hash` must equal
  `expected_source_content_hash` byte-for-byte. Case mismatch, non-final, non-approved,
  non-current, malformed state or hash mismatch fails before insert.
- These checks depend on the completed evidence review/current-version contracts; the
  service must not approximate approval from attachment/document fields or an activity
  label.
- Once a row has been created, later evidence supersession/currentness changes do not
  update, revoke or invalidate that historical row. An exact replay may return that row
  after its evidence version is no longer current; it still requires the same immutable
  source ID/content hash and exact record snapshot, but does not reapply the creation-only
  currentness gate.

### Deterministic reuse, overlap and savepoint race

- Query the deterministic `approval_identity_key` before creating. Exactly one row with
  the exact record snapshot returns it with `REUSED` and performs no mutation. A different
  snapshot or multiplicity is a 409 conflict.
- If no row exists, insert one application-generated UUID row inside
  `transaction.begin_nested()` and `flush()`. The service never calls outer `commit()`,
  outer `rollback()` or `close()` and does not use `RETURNING`, database locks, process
  locks or retry loops.
- Catch `IntegrityError` only around that SAVEPOINT. After its rollback, re-read the
  deterministic identity once: an exact winner returns `REUSED`; a different winner,
  multiplicity or absent winner returns 409. Never retry the mutation or roll back the
  caller's transaction.
- The F5 carrier has no current, supersede or CAS field. The service therefore does not
  mark an approval current, retire an older row, rewrite intervals or manufacture an
  expected-current contract.
- Distinct identities with overlapping fee-code/year/effective scope are retained as
  separate history. This writer neither chooses nor replaces one. A later reader must
  return 409 when more than one approval applies; that reader is explicit non-closure.
- `eligibility_attributes_version` and the opaque attributes are audit data only. This
  service does not decide whether an applicant qualifies and does not infer that a new
  approval replaces an older approval.

### Frozen RED / GREEN and race contract

The exact RED is the missing public DTO/signature and record-service behavior through the
public seam; it is not a deliberately invalid fixture. GREEN must prove:

1. exact frozen/slots/keyword-only DTO fields, enum values and function signature;
2. valid CASE and APPLICANT_SET creation with exact canonical JSON, hashes, four-place
   ratio, exclusive persisted identity and caller-owned transaction semantics;
3. all ratio/type/applicant-count/duplicate/non-finite/extra-field, fee-set, year and date
   failures are write-free, including the explicit ratio-zero no-record branch;
4. same-case FINAL+APPROVED+current evidence and exact expected hash are mandatory for
   creation, and every missing/mismatch/state/current/hash failure leaves row counts and
   caller transaction unchanged;
5. exact replay returns the same row as `REUSED` with no update, including after the source
   evidence later becomes non-current; same identity with a changed snapshot returns 409;
6. overlapping distinct approvals remain present and no current/supersede/CAS behavior is
   written or claimed;
7. simulated unique-identity races prove exact winner reuse and conflicting/absent-winner
   409 branches through one SAVEPOINT without outer commit/rollback or mutation retry;
8. the F5 carrier, evidence review and fee-reduction validator inherited regressions remain
   green.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): F5, evidence versions

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
- `backend/app/modules/fees/fee_reduction_approval_service.py`
- `backend/tests/test_v8_fee_reduction_approval_record.py`
- `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_record.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_record.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_w1_f5_fee_reduction_approval.py tests/test_v8_document_evidence_review_service.py tests/test_v8_fee_reduction_validator.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/fee_reduction_approval_service.py tests/test_v8_fee_reduction_approval_record.py && .venv/bin/ruff format app/modules/fees/fee_reduction_approval_service.py tests/test_v8_fee_reduction_approval_record.py && .venv/bin/ruff check app/modules/fees/fee_reduction_approval_service.py tests/test_v8_fee_reduction_approval_record.py`
- `git diff --check -- backend/app/modules/fees/fee_reduction_approval_service.py backend/tests/test_v8_fee_reduction_approval_record.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01` pass. Only then may this task be reported PASS.
