# FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `15. Migration and compatibility cutover`
Catalog ordinal: `252`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `774`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Read-only report classifies legacy state/evidence conflicts without changing data.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## High Contract Freeze — 2026-08-09

This section is the complete implementation contract for this read-only preflight. It
combines only three already-approved authorities: the one-way
`project_legacy_case_status()` classifier from V8 design §7.3, the legacy-data safety
rules from §11.4, and the accepted row-254 document-evidence dry-run classifications.
It does not create a reverse lifecycle mapping, authorize a backfill, or infer evidence.

### Exact public interface

`backend/scripts/audit_v8_legacy_state.py` exports exactly these names in this order:

```python
__all__ = (
    "LegacyStatePreflightCaseRow",
    "LegacyStatePreflightAttachmentRow",
    "LegacyStatePreflightReport",
    "audit_v8_legacy_state",
)
```

The three public result types use `@dataclass(frozen=True, slots=True, kw_only=True)` with
the exact fields and order below:

```python
class LegacyStatePreflightCaseRow:
    case_id: str
    legacy_status: str
    classification: str
    derived_status: str | None
    conflict_codes: tuple[str, ...]
    legacy_granted_unresolved: bool


class LegacyStatePreflightAttachmentRow:
    attachment_id: str
    classification: str


class LegacyStatePreflightReport:
    case_scanned: int
    case_unchanged: int
    case_update_required: int
    case_conflicts: int
    case_invalid: int
    legacy_granted_unresolved: int
    attachment_scanned: int
    attachment_importable: int
    attachment_unchanged: int
    attachment_invalid: int
    attachment_role_conflicts: int
    attachment_current_conflicts: int
    report_sha256: str
    cases: tuple[LegacyStatePreflightCaseRow, ...]
    attachments: tuple[LegacyStatePreflightAttachmentRow, ...]
```

The sole public callable is synchronous and keyword-only:

```python
def audit_v8_legacy_state(
    *,
    transaction: Session,
    actor_id: str,
) -> LegacyStatePreflightReport:
    ...
```

`actor_id` exists only because the accepted row-254 public dry-run seam requires it. It
must be an exact nonempty stripped `str`, contain no NUL, have length at most 36, and
identify an existing `T_User`. The row-254 errors
`LEGACY_DOCUMENT_EVIDENCE_ACTOR_INVALID` and
`LEGACY_DOCUMENT_EVIDENCE_ACTOR_MISSING` propagate unchanged with status 409. The actor is
not a fact in this report and is excluded from its rows, counts, and hash.

### Exact case-state read and classification

Read every current `Case` in `Case.id` ascending order. For each case, read at most one
latest activity satisfying exact `lane="LIFECYCLE"` and
`confirmation_status="CONFIRMED"`, ordered by `(sequence DESC, id DESC)`. The audit never
uses a DOCUMENT or FEE activity to derive state.

For non-null stored axis values, construct the accepted enums only by exact value:

- `Case.business_stage` -> `BusinessStage`;
- `Case.official_procedure_stage` -> `OfficialProcedureStage`;
- `Case.legal_status` -> `LegalStatus`; and
- `Case.lifecycle_verification_status` -> `ConfirmationStatus`.

Then construct the accepted `LifecycleProjection` and call the sole state classifier:

```python
project_legacy_case_status(
    existing_status=case.status,
    projection=projection,
    latest_confirmed_lifecycle_event_type=latest_activity.activity_type
        if latest_activity is not None else None,
    oa_sequence=oa_sequence,
)
```

The latest activity payload, when present, must decode as one JSON object. An absent
`oa_sequence` maps to `None`; a present value must be an exact positive `int`, not `bool`.
No older activity, document metadata, task, attachment, filename, or legacy status may
supply a replacement sequence.

Copy the accepted classifier result without reinterpretation:

| Classifier disposition | Row `classification` | Other copied fields |
| --- | --- | --- |
| `UNCHANGED` | `UNCHANGED` | exact derived status and conflict-code values |
| `UPDATE_REQUIRED` | `UPDATE_REQUIRED` | exact derived status and conflict-code values |
| `RETAINED_CONFLICT` | `RETAINED_CONFLICT` | exact derived status and conflict-code values |

An unknown but nonblank legacy status remains valid input because the §7.3 classifier
explicitly retains or replaces it. This audit does not create a reverse mapping from any
legacy status to lifecycle axes or an event type.

Malformed stored carrier data fails closed on that row. It does not abort later rows and
never reaches `project_legacy_case_status()`. Such a row has
`classification="INVALID_CARRIER"`, `derived_status=None`, and the sorted, unique
applicable codes from this exact set:

```text
LEGACY_STATE_CASE_ID_INVALID
LEGACY_STATE_STATUS_INVALID
LEGACY_STATE_BUSINESS_STAGE_INVALID
LEGACY_STATE_OFFICIAL_STAGE_INVALID
LEGACY_STATE_LEGAL_STATUS_INVALID
LEGACY_STATE_VERIFICATION_STATUS_INVALID
LEGACY_STATE_REVISION_INVALID
LEGACY_STATE_ACTIVITY_TYPE_INVALID
LEGACY_STATE_ACTIVITY_PAYLOAD_INVALID
LEGACY_STATE_OA_SEQUENCE_INVALID
```

The exact carrier validations are:

- case ID and status are nonempty stripped `str` values without NUL;
- every non-null axis value is an exact accepted enum wire value;
- `lifecycle_revision` is `None` or an exact non-`bool` `int >= 0`;
- a selected latest activity has a nonempty stripped activity type without NUL; and
- its payload and optional OA sequence satisfy the JSON/object/value rules above.

### Legacy `GRANTED` fail-closed rule

Old `GRANTED` is never authority for `PATENT_IN_FORCE`. Set
`legacy_granted_unresolved=True` exactly when the stored legacy status is `GRANTED` and
the row is not an already-managed, fully confirmed, conflict-free `UNCHANGED` projection
whose `derived_status` is also exact `GRANTED`.

For such a row, add exact code `LEGACY_GRANTED_UNRESOLVED` to the sorted, unique conflict
tuple and force `classification="RETAINED_CONFLICT"`. An `INVALID_CARRIER` row remains
`INVALID_CARRIER`, but carries the same flag and added code. This narrow exception permits
a current confirmed `PATENT_IN_FORCE` projection to report `UNCHANGED`; it never promotes
an old shortcut status.

### Exact document-evidence classification

Within the same read-only, no-autoflush section, call the accepted row-254 public seam
exactly in dry-run mode:

```python
import_legacy_document_evidence(
    transaction=transaction,
    actor_id=actor_id,
    dry_run=True,
)
```

Do not reproduce, widen, collapse, or rename its classification semantics. Project each
returned row to `LegacyStatePreflightAttachmentRow` with its exact `attachment_id` and one
of these exact values:

```text
IMPORT
UNCHANGED
INVALID
ROLE_CONFLICT
CURRENT_CONFLICT
```

`IMPORT` means only that row 254 could import the unambiguous attachment after its own
separate contract and acceptance; this preflight performs no import. `ROLE_CONFLICT` and
`CURRENT_CONFLICT` remain unresolved. Sort the projected rows by attachment ID ascending.

### Counts, ordering, and canonical report hash

Case rows are ordered by case ID ascending. Attachment rows are ordered by attachment ID
ascending. Conflict codes are sorted lexicographically and contain no duplicate.

All counts are derived only from the final returned tuples:

- `case_scanned` is the number of case rows;
- `case_unchanged`, `case_update_required`, `case_conflicts`, and `case_invalid` count
  `UNCHANGED`, `UPDATE_REQUIRED`, `RETAINED_CONFLICT`, and `INVALID_CARRIER` respectively;
- `legacy_granted_unresolved` counts the independent true flag;
- `attachment_scanned` is the number of attachment rows;
- `attachment_importable`, `attachment_unchanged`, `attachment_invalid`,
  `attachment_role_conflicts`, and `attachment_current_conflicts` count the five exact
  row-254 classifications in the order listed above.

`report_sha256` is the lowercase SHA-256 hex digest of canonical UTF-8 JSON produced with
`ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`, and `allow_nan=False`.
The hashed object contains exact schema `FPMS_V8_LEGACY_STATE_PREFLIGHT_V1`, all twelve
counts before `report_sha256`, and both complete ordered row lists. It excludes
`report_sha256` itself and excludes `actor_id`. Equal stored facts therefore produce the
same report and hash for every valid auditor.

### Read-only and focused RED/GREEN assertions

The entire operation runs under `transaction.no_autoflush`. It never calls `add`,
`add_all`, `delete`, `flush`, `commit`, `rollback`, or `close`, never mutates a loaded ORM
object, and never opens another session or engine. The test monkeypatches those write and
transaction methods to fail, snapshots `transaction.new`, `transaction.dirty`, and
`transaction.deleted`, and compares the relevant stored rows before and after both a
single call and an equal repeated call.

The exact focused test covers:

1. public `__all__`, keyword-only synchronous signature, and exact frozen/slotted DTO
   field order;
2. `UNCHANGED`, `UPDATE_REQUIRED`, accumulated `RETAINED_CONFLICT`, and every invalid
   carrier code through real stored case rows;
3. latest confirmed LIFECYCLE selection, JSON/OA handling, and exclusion of DOCUMENT/FEE
   activities;
4. unresolved old `GRANTED` versus an already-managed confirmed `GRANTED` projection;
5. all five exact row-254 attachment classifications without writes;
6. stable row order, counts, canonical hash, equal repeated results, actor exclusion, and
   unchanged propagation of both row-254 actor errors; and
7. zero ORM/session writes, autoflush, transaction control, engine creation, reverse
   mapping, event append, import, or conflict persistence.

No CLI, endpoint, UI, schema, migration, backfill, activity append, projection update,
`Case.status` assignment, evidence-version write, actor audit record, conflict table, or
second report family belongs to this task.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
- `FPMS-V8-LC-CASE-OPENED-20260712-01`
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
- `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
- `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
- `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
- `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
- `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
- `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
- `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
- `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
- `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): lifecycle rules/adapters

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01.md`
- `backend/scripts/audit_v8_legacy_state.py`
- `backend/tests/test_v8_legacy_state_preflight.py`
- `artifacts/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_state_preflight.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_legacy_state_preflight.py`
- `cd backend && .venv/bin/ruff check --fix scripts/audit_v8_legacy_state.py tests/test_v8_legacy_state_preflight.py && .venv/bin/ruff format scripts/audit_v8_legacy_state.py tests/test_v8_legacy_state_preflight.py && .venv/bin/ruff check scripts/audit_v8_legacy_state.py tests/test_v8_legacy_state_preflight.py`
- `git diff --check -- backend/scripts/audit_v8_legacy_state.py backend/tests/test_v8_legacy_state_preflight.py tasks/postdemo/v8/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01` pass. Only then may this task be reported PASS.
