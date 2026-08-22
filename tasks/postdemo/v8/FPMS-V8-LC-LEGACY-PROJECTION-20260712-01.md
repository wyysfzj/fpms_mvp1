# FPMS-V8-LC-LEGACY-PROJECTION-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `9. Wave 2A — lifecycle foundation`
Catalog ordinal: `16`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `372`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Implement the approved one-way `LegacyCaseStatusProjection` precedence, including unverified/conflict retention.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

This section is the complete implementation contract for High. The implementation is a
pure, deterministic, one-way compatibility adapter. It consumes the already-frozen
`LifecycleProjection` plus the latest confirmed lifecycle-event facts and returns an
instruction; it does not read or mutate an ORM object, persist a conflict, open a
transaction, infer a central state from `Case.status`, or import SQLAlchemy/FastAPI.

### Exact public interface

`backend/app/modules/cases/lifecycle_projection.py` exports exactly these names in this
order:

```python
__all__ = (
    "LegacyCaseStatusProjection",
    "LegacyProjectionConflictCode",
    "LegacyProjectionDisposition",
    "project_legacy_case_status",
)
```

It imports `BusinessStage`, `ConfirmationStatus`, `LegalStatus`,
`LifecycleProjection`, and `OfficialProcedureStage` from
`app.modules.cases.lifecycle_contracts`. No duplicate lifecycle enum or ORM-facing
adapter is allowed.

```python
from dataclasses import dataclass
from enum import StrEnum


class LegacyProjectionConflictCode(StrEnum):
    AXIS_CONFLICT = "LEGACY_PROJECTION_AXIS_CONFLICT"
    INCOMPLETE_AXES = "LEGACY_PROJECTION_INCOMPLETE_AXES"
    MISSING_OA_SEQUENCE = "LEGACY_PROJECTION_MISSING_OA_SEQUENCE"
    NO_MAPPING = "LEGACY_PROJECTION_NO_MAPPING"
    UNKNOWN_LEGAL_STATUS = "LEGACY_PROJECTION_UNKNOWN_LEGAL_STATUS"
    UNVERIFIED = "LEGACY_PROJECTION_UNVERIFIED"


class LegacyProjectionDisposition(StrEnum):
    UNCHANGED = "UNCHANGED"
    UPDATE_REQUIRED = "UPDATE_REQUIRED"
    RETAINED_CONFLICT = "RETAINED_CONFLICT"


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyCaseStatusProjection:
    legacy_case_status: str
    derived_case_status: str | None
    disposition: LegacyProjectionDisposition
    conflict_codes: tuple[LegacyProjectionConflictCode, ...] = ()


def project_legacy_case_status(
    *,
    existing_status: str,
    projection: LifecycleProjection,
    latest_confirmed_lifecycle_event_type: str | None,
    oa_sequence: int | None,
) -> LegacyCaseStatusProjection: ...
```

`existing_status` is the exact current non-null `t_case.status` value. It is never
normalized or used to infer any axis. `latest_confirmed_lifecycle_event_type` means the
latest confirmed activity in lane `LIFECYCLE`, not the latest document/fee activity.
`oa_sequence` is the positive OA sequence attached to the applicable confirmed lifecycle
fact; it is not a legal status.

### Exact validation errors

Validation occurs before projection and has no side effect. The following failures and
messages are exact:

| Condition | Exception and exact message |
| --- | --- |
| `existing_status` is not `str` | `TypeError("existing_status must be str")` |
| `existing_status.strip()` is empty | `ValueError("existing_status must be non-empty")` |
| `projection` is not `LifecycleProjection` | `TypeError("projection must be LifecycleProjection")` |
| A non-null `business_stage` is not `BusinessStage` | `TypeError("projection.business_stage must be BusinessStage or None")` |
| A non-null `official_procedure_stage` is not `OfficialProcedureStage` | `TypeError("projection.official_procedure_stage must be OfficialProcedureStage or None")` |
| A non-null `legal_status` is not `LegalStatus` | `TypeError("projection.legal_status must be LegalStatus or None")` |
| A non-null verification value is not `ConfirmationStatus` | `TypeError("projection.lifecycle_verification_status must be ConfirmationStatus or None")` |
| Latest event is neither `None` nor `str` | `TypeError("latest_confirmed_lifecycle_event_type must be str or None")` |
| Latest event is a blank string | `ValueError("latest_confirmed_lifecycle_event_type must be non-empty when provided")` |
| OA sequence is a `bool` or a non-`int` value | `TypeError("oa_sequence must be int or None")` |
| OA sequence is less than one | `ValueError("oa_sequence must be positive when provided")` |

An open event-type string is intentional: each later event-rule task owns one whitelist
addition. An `existing_status` outside the current `CaseStatus` enum is still retained
byte-for-byte on a conflict and can be replaced by a verified deterministic projection;
this adapter does not create a reverse legacy-status authority.

### Complete consistency matrix

After input validation, conflict facts are accumulated rather than short-circuited. Axis
nullability and verification are classified as follows:

| Fact | Conflict added |
| --- | --- |
| `lifecycle_verification_status` is `None`, `NEEDS_REVIEW`, or `LEGACY_UNVERIFIED` | `UNVERIFIED` |
| Any of business, official, or legal axis is `None` | one `INCOMPLETE_AXES` |
| Legal axis is `UNKNOWN` | `UNKNOWN_LEGAL_STATUS` |

When business and official axes are both non-null, they are consistent only for the pairs
below. Any other pair adds one `AXIS_CONFLICT`:

| Official stage | Allowed business stage(s) |
| --- | --- |
| `NOT_SUBMITTED` | `NEW_CASE`, `FILING_PREPARATION` |
| `SUBMITTED_WAITING_RECEIPT` | `WAITING_EXTERNAL_RECEIPT` |
| `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE` | `PROSECUTION_MANAGEMENT` |
| `ACCEPTED` | `PROSECUTION_MANAGEMENT` |
| `PRELIMINARY_EXAMINATION` | `PROSECUTION_MANAGEMENT` |
| `RECTIFICATION_RESPONSE` | `OA_REPLY_IN_PROGRESS` |
| `PUBLISHED` | `PROSECUTION_MANAGEMENT` |
| `SUBSTANTIVE_EXAMINATION` | `PROSECUTION_MANAGEMENT` |
| `OFFICE_ACTION_RESPONSE` | `OA_REPLY_IN_PROGRESS` |
| `REEXAMINATION` | `PROSECUTION_MANAGEMENT` |
| `GRANT_REGISTRATION` | `GRANT_REGISTRATION_IN_PROGRESS` |
| `GRANT_ANNOUNCED` | `POST_GRANT_MAINTENANCE` |
| `PROCEDURE_CLOSED` | `CLOSED` |

When legal and official axes are both non-null and legal is not `UNKNOWN`, they are
consistent only for the pairs below. Any other pair adds the same deduplicated
`AXIS_CONFLICT`:

| Legal status | Allowed official stage(s) |
| --- | --- |
| `NOT_ESTABLISHED` | `NOT_SUBMITTED`, `SUBMITTED_WAITING_RECEIPT` |
| `APPLICATION_PENDING` | `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE`, `ACCEPTED`, `PRELIMINARY_EXAMINATION`, `RECTIFICATION_RESPONSE`, `PUBLISHED`, `SUBSTANTIVE_EXAMINATION`, `OFFICE_ACTION_RESPONSE`, `REEXAMINATION`, `GRANT_REGISTRATION` |
| `APPLICATION_REJECTED`, `APPLICATION_WITHDRAWN`, `APPLICATION_ABANDONED` | `PROCEDURE_CLOSED` |
| `PATENT_IN_FORCE` | `GRANT_ANNOUNCED` |
| `PATENT_TERMINATED`, `PATENT_EXPIRED`, `PATENT_INVALIDATED` | `PROCEDURE_CLOSED` |

If the official stage is `OFFICE_ACTION_RESPONSE` and `oa_sequence is None`, add
`MISSING_OA_SEQUENCE`. A supplied positive OA sequence is ignored outside that official
stage; this permits a caller to pass the last known OA sequence without making it a new
state authority. `PRELIMINARY_EXAMINATION_PASSED` only selects the special legacy value
while the official stage remains `PRELIMINARY_EXAMINATION`; every other event string or
`None` selects the ordinary preliminary-examination row and creates no event conflict.

Conflict codes are a set during evaluation and are returned once each, sorted
lexicographically by their string value. Thus an unverified projection with a null axis
and `UNKNOWN` legal status returns exactly the applicable sorted three-code tuple; it does
not hide later conflict facts behind the first gate.

### Exact precedence and result semantics

Only a complete, `CONFIRMED`, matrix-consistent projection with no missing OA sequence is
eligible for derivation. It applies the approved mapping from top to bottom and stops at
the first match:

| Order | Confirmed condition | Derived `Case.status` |
| ---: | --- | --- |
| 1 | legal=`PATENT_INVALIDATED` | `INVALIDATED` |
| 2 | legal=`PATENT_TERMINATED` | `TERMINATED` |
| 3 | legal=`PATENT_EXPIRED` | `EXPIRED` |
| 4 | legal=`PATENT_IN_FORCE` | `GRANTED` |
| 5 | legal=`APPLICATION_REJECTED` | `REJECTED` |
| 6 | legal=`APPLICATION_WITHDRAWN` | `WITHDRAWN` |
| 7 | legal=`APPLICATION_ABANDONED` | `ABANDONED` |
| 8 | official=`GRANT_REGISTRATION` | `GRANT_PENDING` |
| 9 | official=`REEXAMINATION` | `REEXAM` |
| 10 | official=`OFFICE_ACTION_RESPONSE` and `oa_sequence == 1` | `OA1` |
| 11 | official=`OFFICE_ACTION_RESPONSE` and `oa_sequence >= 2` | `OA2` |
| 12 | official=`RECTIFICATION_RESPONSE` | `AMENDMENT` |
| 13 | official=`SUBSTANTIVE_EXAMINATION` | `SUB_EXAM` |
| 14 | official=`PUBLISHED` | `PUBLISHED` |
| 15 | latest event=`PRELIMINARY_EXAMINATION_PASSED` and official=`PRELIMINARY_EXAMINATION` | `PRELIM_PASS` |
| 16 | official=`PRELIMINARY_EXAMINATION` | `PRELIM_EXAM` |
| 17 | official=`ACCEPTED` | `ACCEPTED` |
| 18 | official=`SUBMITTED_WAITING_RECEIPT` or `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE` | `WAITING_RECEIPT` |
| 19 | legal=`APPLICATION_PENDING` with no earlier match | `PENDING` |
| 20 | official=`NOT_SUBMITTED` | `NOT_FILED` |

`PENDING` is retained in the approved ordered table even though every currently defined,
complete, consistent `APPLICATION_PENDING`/official pair has a more-specific earlier row.
This adapter must not weaken null/conflict retention merely to force that fallback to be
reachable. If a complete, confirmed, consistent future enum combination reaches the end
of the table, add `NO_MAPPING` and treat it as a conflict; do not guess a status.

The result is exact:

| Situation | `legacy_case_status` | `derived_case_status` | `disposition` | `conflict_codes` |
| --- | --- | --- | --- | --- |
| One or more conflicts | exact input `existing_status` | `None` | `RETAINED_CONFLICT` | sorted unique applicable codes |
| No conflict and derived value equals `existing_status` exactly | derived value | derived value | `UNCHANGED` | `()` |
| No conflict and derived value differs | derived value | derived value | `UPDATE_REQUIRED` | `()` |

`RETAINED_CONFLICT` is authoritative fail-closed retention even when the retained legacy
string happens to equal the value the incomplete/unverified axes might otherwise suggest.
Only `UPDATE_REQUIRED` authorizes the later orchestration seam to assign `Case.status`;
`UNCHANGED` authorizes no assignment. This adapter itself never writes either status or
`legacy_conflicts`. A later write action that requires an accurate state must translate
`RETAINED_CONFLICT` into its already-approved 409/no-write boundary.

### Frozen RED / GREEN tests

The exact test module must cover all of the following through the public interface:

1. Exact four-name `__all__`; exact conflict/disposition `StrEnum` members and values; the
   result is frozen, slotted, keyword-only, with the exact field order/default.
2. Table-driven coverage of every currently reachable row in the 20-row precedence table,
   including OA1/OA2 boundary values and `PRELIM_PASS` versus ordinary `PRELIM_EXAM`.
3. All three non-confirmed verification inputs, every nullable axis position, `UNKNOWN`,
   and a combined case proving sorted duplicate-free conflict accumulation.
4. Every official/business allowed row plus a representative disallowed business for each
   official row; every legal/official allowed row plus representative disallowed pairs for
   each legal category.
5. OA sequence `None`, `1`, `2`, and a value greater than `2`; positive OA sequence ignored
   outside OA; invalid `bool`, non-integer, zero, and negative validation.
6. `UNCHANGED`, `UPDATE_REQUIRED`, and `RETAINED_CONFLICT`, including a retained legacy
   string equal to a plausible derived value and an unknown legacy string retained exactly.
7. Every validation error type and exact message above.
8. Purity: input objects remain unchanged; repeated equal calls return equal results; AST
   imports contain no SQLAlchemy/FastAPI/model/session module; public callable performs no
   repository or transaction operation.

RED fails because `lifecycle_projection.py` is absent. GREEN is the minimum pure module
that satisfies these tests. No SQLite test, service-level commit, repository fixture,
endpoint assertion, direct `Case.status` assignment, event-rule implementation, overlay
projection, legacy import, or conflict persistence belongs to this task.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-CONTRACTS-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): contracts

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01.md`
- `backend/app/modules/cases/lifecycle_projection.py`
- `backend/tests/test_v8_lifecycle_legacy_projection.py`
- `artifacts/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_legacy_projection.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_legacy_projection.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_projection.py tests/test_v8_lifecycle_legacy_projection.py && .venv/bin/ruff format app/modules/cases/lifecycle_projection.py tests/test_v8_lifecycle_legacy_projection.py && .venv/bin/ruff check app/modules/cases/lifecycle_projection.py tests/test_v8_lifecycle_legacy_projection.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_projection.py backend/tests/test_v8_lifecycle_legacy_projection.py tasks/postdemo/v8/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-LEGACY-PROJECTION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-LEGACY-PROJECTION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-LEGACY-PROJECTION-20260712-01` pass. Only then may this task be reported PASS.
