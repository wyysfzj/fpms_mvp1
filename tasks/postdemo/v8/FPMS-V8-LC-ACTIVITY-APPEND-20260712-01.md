# FPMS-V8-LC-ACTIVITY-APPEND-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `9. Wave 2A — lifecycle foundation`
Catalog ordinal: `15`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `371`
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

`append_case_activity()` allocates sequence, enforces idempotency, rejects a missing/cross-case `source_activity_id`, enforces same-case evidence and increments revision in the caller transaction.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Implementation Freeze — 2026-07-13

This section is the complete implementation contract for High. It resolves the earlier
ambiguity without changing the accepted V8 business semantics or adding a customer gate.
The service is the single persistence seam for all three lanes. It does not decide an event
transition, calculate a legacy status, inspect a source-specific evidence table, expose HTTP,
or commit the caller transaction.

### Exact public callable

`backend/app/modules/cases/lifecycle_activity_service.py` exposes exactly this public
callable; helpers remain private:

```python
def append_case_activity(
    command: LifecycleEventCommand,
    transaction: Session,
    *,
    previous_projection: LifecycleProjection,
    current_projection: LifecycleProjection,
    legacy_case_status: str,
    conflict_codes: tuple[str, ...] = (),
) -> LifecycleTransitionResult:
    ...
```

- Parameter order, keyword-only boundary and default are exact.
- `command`, both projection values and the returned value are the frozen types from
  `lifecycle_contracts.py`; do not duplicate or replace them with dictionaries or Pydantic
  models.
- `transaction` is an existing SQLAlchemy `Session`. The function may `flush()` and refresh
  server-populated state, but must not call `commit()`, `rollback()` or close the session.
- The four keyword-only values are a persistence decision already calculated by the owning
  lifecycle rule/orchestrator. This seam validates and persists that decision; it does not
  import or call `LegacyCaseStatusProjection`.
- No new public exception, repository, protocol, registry, result type or generic HTTP seam
  is authorized.

There is deliberately no dependency on `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`.
`LC-LEGACY-PROJECTION` remains a pure calculation used by the later
`LC-APPLY-EVENT-SEAM`. For `DOCUMENT` and `FEE` callers, the required decision is the
unchanged current case projection and unchanged `Case.status`.

### Required validation order and fail-closed errors

The implementation performs validation in this order. On any failure it raises the existing
`app.core.errors.BusinessError`, writes no new activity/evidence row, does not increment the
revision and does not mutate a case projection/status.

1. **Command and persistence-decision shape — HTTP 400.** Require the exact frozen command
   and projection types; real enum members; non-empty strings within carrier lengths
   (`case_id/actor_id/reviewer_id/source_activity_id/supersedes_event_id <= 36`,
   `event_type <= 64`, `idempotency_key <= 128`, `legacy_case_status <= 32`); and a sorted,
   duplicate-free tuple of non-empty `conflict_codes`. Invalid general shape uses
   `LIFECYCLE_ACTIVITY_INVALID` with `details.field`.
2. **Timestamp and payload shape — HTTP 400.** `effective_at`, optional `occurred_at` and
   every `captured_at` must be timezone-naive `datetime` values because all W1 carriers are
   `DateTime(timezone=False)`. Serialize `command.payload` exactly with
   `json.dumps(..., ensure_ascii=False, sort_keys=True, separators=(",", ":"),
   allow_nan=False)`. Keys must be strings and the value must be a JSON object; non-JSON,
   NaN/infinity or a non-object uses `LIFECYCLE_PAYLOAD_INVALID`.
3. **Evidence-reference shape — HTTP 400.** Each reference requires non-empty values within
   W1 lengths (`case_id/object_id <= 36`, `evidence_kind <= 32`, `object_type <= 64`,
   `content_hash <= 128`) and a naive `captured_at`. Invalid shape uses
   `LIFECYCLE_EVIDENCE_INVALID`. The tuple must contain no repeated persisted identity
   `(case_id, evidence_kind, object_type, object_id)`; a repeat, including an exact duplicate,
   uses `LIFECYCLE_EVIDENCE_DUPLICATE`.
4. **Case lookup — HTTP 404.** Missing `Case(command.case_id)` uses `CASE_NOT_FOUND`.
5. **Existing idempotency key.** Query `(case_id, idempotency_key)` before any allocation or
   mutation and apply the replay rules below. A mismatch uses
   `LIFECYCLE_IDEMPOTENCY_CONFLICT`, HTTP 409.
6. **Current projection/revision consistency — HTTP 409.** For a new append,
   `previous_projection` must exactly equal the four current case columns after converting
   valid strings to the frozen enums. An unknown stored code, mismatch, negative revision,
   or disagreement between `coalesce(Case.lifecycle_revision, 0)` and the same-case maximum
   activity sequence uses `LIFECYCLE_PROJECTION_CONFLICT` or
   `LIFECYCLE_REVISION_CONFLICT`, as applicable.
7. **Lane/centre-change boundary — HTTP 409.** `DOCUMENT` and `FEE` require identical
   previous/current projections, unchanged `legacy_case_status == Case.status`, and empty
   `conflict_codes`. `LIFECYCLE` with `NEEDS_REVIEW` also cannot change the projection or
   legacy status. A changed central projection is accepted only for a `CONFIRMED`
   `LIFECYCLE` command, except the separately approved `LEGACY_IMPORT` with
   `LEGACY_UNVERIFIED`; that one-time import exception may initialize an unverified
   projection but may not overwrite an already non-null projection. Violations use
   `LIFECYCLE_CENTER_CHANGE_NOT_ALLOWED`.
8. **Source/correction references — HTTP 409.** Apply the exact rules below.
9. **Evidence same-case rule — HTTP 409.** Every `EvidenceReference.case_id` must equal
   `command.case_id`; otherwise use `LIFECYCLE_EVIDENCE_CASE_MISMATCH`.
10. **Compare-and-swap allocation and flush.** Apply the exact atomic-write sequence below.

Input validation is intentionally before case/idempotency access so malformed commands are
never treated as successful replays. Idempotency lookup precedes source and case-state
mutation so an exact replay is read-only.

### Exact idempotency identity and replay

Canonical command identity comprises all persisted command facts:

- case ID and idempotency key;
- event type, lane, effective/occurred time, actor/reviewer, confirmation status,
  source/supersede references;
- the exact canonical `payload_json` text; and
- the complete evidence-reference set, order-insensitive after sorting by
  `(case_id, evidence_kind, object_type, object_id, content_hash, captured_at)`.

The stored old/new three-axis columns must also equal the supplied old/new three axes. The
case-level verification values, `legacy_case_status` and non-blocking `conflict_codes` are
result/projection-decision context rather than command identity because the accepted W1
activity carrier has no columns for those historical values. Callers must repeat the same
decision context when retrying the same key; this task must not hide extra metadata inside
`payload_json` or alter the frozen payload wire.

- If all comparable values match, return the existing activity with `reused=True`, its
  existing `activity_id`, `sequence`, and `lifecycle_revision=sequence`; return the supplied
  structurally valid verification/status/conflict context and the stored old/new three axes.
  Do not add, update, flush, increment or rewrite any row.
- A same case/key mismatch in any canonical command fact, evidence member, or persisted
  old/new axis is `LIFECYCLE_IDEMPOTENCY_CONFLICT` (409), with no write.
- Evidence tuple order alone is never a conflict. Missing/extra evidence, or the same link
  identity with a different hash/capture time, is a conflict.
- Reuse remains valid even if a later activity exists. The replay returns the original
  activity sequence/revision and never rewinds the current case. The caller is responsible
  for retaining the original projection-decision context; this seam never substitutes the
  later current case state into an old result.

### Source activity and correction rules

- A non-null `source_activity_id` must identify an already persisted activity. Missing uses
  `LIFECYCLE_SOURCE_ACTIVITY_NOT_FOUND`; another case uses
  `LIFECYCLE_SOURCE_ACTIVITY_CASE_MISMATCH`. Both are HTTP 409.
- A non-null `supersedes_event_id` follows the same prior-row and same-case rule. Missing uses
  `LIFECYCLE_SUPERSEDED_ACTIVITY_NOT_FOUND`; another case uses
  `LIFECYCLE_SUPERSEDED_ACTIVITY_CASE_MISMATCH`. Both are HTTP 409.
- Both references necessarily point to a lower sequence because resolution occurs before
  allocating the new sequence. Neither is inferred from the other; they may legitimately
  identify the same prior activity.
- The function generates the new activity UUID, so neither reference can target the new row.
  It does not traverse ancestry, reject cycles beyond this prior-row rule, mutate a source,
  or mark a superseded event inactive. Append-only correction interpretation belongs to the
  overlay/event-rule tasks.

### Evidence validation and persisted rows

For each unique, valid reference, insert exactly one `CaseActivityEventEvidence` row with a
new application-generated UUID and fields copied without coercion. Sort before insertion so
tests and diagnostics are deterministic. All rows use the new activity ID and command case.

`EvidenceReference.object_type` is intentionally open in the frozen LC contract and W1-L3
has no foreign key or approved cross-module resolver to heterogeneous source tables.
Therefore this seam does **not** guess a model from `object_type` or query a generic registry.
The source-specific event/adapter must establish that the referenced document/task/payment
object exists before constructing the command. This task closes link completeness and
same-case enforcement only; introducing a polymorphic evidence registry would be a separate
schema/business slice and is prohibited here.

### Sequence, revision and single-transaction write

For a new append, the observable invariant is:

```text
coalesce(Case.lifecycle_revision, 0)
  == max(t_case_activity_event.sequence for the case, default 0)
new_sequence == new_lifecycle_revision == prior_revision + 1
```

Use the loaded revision as an optimistic compare-and-swap predicate on the `Case` row; do
not rely on `RETURNING`, process-local locks or `SELECT ... FOR UPDATE` for SQLite
correctness. A zero-row compare-and-swap uses `LIFECYCLE_CONCURRENCY_CONFLICT` (409). The
service then creates one `CaseActivityEvent`, creates its evidence rows, writes all four
current projection columns plus `Case.status=legacy_case_status`, and flushes once before
returning. UUIDs are generated in application code. The event old/new columns store only the
three central axes exactly as W1-L2 defines; `recorded_at/created_at/updated_at` use the
existing SQLite-safe server defaults.

The caller owns the surrounding transaction, so activity, evidence, projection, legacy
status and revision become visible together only when the caller commits. On any normal
validation conflict there is no write. SQLite tests are serialized. A raw database-lock or
driver failure is not swallowed or converted after a failed flush (which would require a
service rollback); the owning transaction boundary rolls back/retries it. Deterministic
compare-and-swap loss is the service-level 409 path.

### Exact returned result

For a new append return `LifecycleTransitionResult` with:

- identifiers and enum values copied from the command/new event;
- `sequence == lifecycle_revision ==` the allocated revision;
- the supplied validated projections, legacy status and sorted conflict tuple;
- `idempotency_key=command.idempotency_key`; and
- `reused=False`.

No event-rule conflict is invented here. Blocking conditions raise and return no result.

### Observable RED/GREEN dataset

The task test must cover each behavior through `append_case_activity()` and real SQLite
foreign-key-enabled sessions:

1. first append from nullable revision allocates sequence/revision `1`, persists one event
   and all evidence links, updates the four projection columns and `Case.status`, flushes but
   does not commit;
2. a second lane-only append allocates `2`, retains projection/status and proves global
   cross-lane monotonic ordering;
3. exact replay (including shuffled evidence order) returns the same ID/sequence with
   `reused=True` and no row/revision change, including after a later activity exists;
4. same key with changed payload, event fact, evidence set/hash/time or old/new axis raises
   `LIFECYCLE_IDEMPOTENCY_CONFLICT` 409 with no mutation;
5. missing and cross-case source activity, and missing/cross-case superseded activity, each
   raise their exact 409 code with no mutation;
6. wrong-case evidence, duplicate evidence identity, invalid/aware timestamps and
   non-canonical/non-JSON payload inputs fail with their exact status/code and no mutation;
7. `DOCUMENT`, `FEE` and `NEEDS_REVIEW` central-change attempts fail closed; confirmed
   lifecycle change succeeds; `LEGACY_IMPORT/LEGACY_UNVERIFIED` can initialize only a null
   projection;
8. stale previous projection, revision/sequence drift and compare-and-swap loss fail with the
   exact 409 code and no activity/evidence row;
9. caller rollback removes the event/evidence/projection/status/revision changes, proving
   there is no service commit.

The serialized inherited regression command is:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_lifecycle_contracts.py \
  tests/test_v8_w1_l1_case_lifecycle_projection.py \
  tests/test_v8_w1_l2_case_activity_event.py \
  tests/test_v8_w1_l3_case_activity_evidence.py
```

### Reaffirmed non-closure

Do not implement a transition matrix, legacy mapping, event whitelist beyond the structural
centre-change guard above, OA sequence policy, source-specific evidence lookup, correction
overlay, lifecycle HTTP endpoint, schema/migration change, generic event endpoint, UI, or
commit/retry loop. Event-specific evidence requirements and state reachability remain owned
by their exact rule tasks and `LC-APPLY-EVENT-SEAM`.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- `FPMS-V8-LC-CONTRACTS-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): contracts, L1–L3

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01.md`
- `backend/app/modules/cases/lifecycle_activity_service.py`
- `backend/tests/test_v8_lifecycle_activity_append.py`
- `artifacts/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_activity_append.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_activity_service.py tests/test_v8_lifecycle_activity_append.py && .venv/bin/ruff format app/modules/cases/lifecycle_activity_service.py tests/test_v8_lifecycle_activity_append.py && .venv/bin/ruff check app/modules/cases/lifecycle_activity_service.py tests/test_v8_lifecycle_activity_append.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_activity_service.py backend/tests/test_v8_lifecycle_activity_append.py tasks/postdemo/v8/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-ACTIVITY-APPEND-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-ACTIVITY-APPEND-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-ACTIVITY-APPEND-20260712-01` pass. Only then may this task be reported PASS.
