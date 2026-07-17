# FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-16
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `H4-0 / D4-02`
Materialization row: `02 / D4-02`
Risk tier: `HIGH`
Scope: `Foundation`
Contract state: `CONTRACT FROZEN`
Executor role: High implementation agent / Backend Developer

## Authoritative Contract

- `AGENTS.md`
- Delta-4 specification:
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- Frozen Delta-4 specification SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`
- Supplemental batch manifest row: `02 / D4-02`
- Required D4 predecessor:
  `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01`
- Accepted catalog predecessor / Task 55:
  `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`

The hash-locked Delta-4 specification controls if this task text is read ambiguously. A
specification hash mismatch, a non-PASS direct dependency, an accepted-seam regression or
an allowlist conflict fails closed and returns only this affected lane to Ultra contract
review. Do not reopen broad V8 source or customer-document analysis.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: after D4-01 is accepted, the task-owned create-path regression expects
  the exact case-record evidence and immutable payload, while the accepted Task 55 adapter
  still sends `evidence_refs=()` and `payload={}` and therefore fails closed.
- GREEN expectation: the smallest `create_case()` correction supplies the exact evidence
  and payload through the accepted lifecycle seam; the task-owned test and the named
  read-only Task 55 regressions pass without any API/schema/rule change.

## Exact Closure Slice

Change only the existing `create_case()` adapter in
`backend/app/modules/cases/service.py` so its one `CASE_OPENED` command supplies the exact
single `CASE_RECORD` evidence reference accepted by D4-01 and persists the exact immutable
case-create source snapshot in the accepted lifecycle activity payload.

The source is the newly created `Case` object after its existing flush, while it is visible
inside the same transaction. Do not build source truth from an unflushed request DTO, a
later/latest lookup, a mutable post-create row or a fallback value.

### Exact source snapshot and hash

Construct one JSON object with exactly these keys and values:

1. `case_id`: exact `Case.id`;
2. `case_no`: exact `Case.case_no`;
3. `case_type`: exact persisted `Case.case_type` string; and
4. `client_id`: exact nullable `Case.client_id`.

The semantic and canonical key order is exactly `case_id`, `case_no`, `case_type`,
`client_id`. A null client remains an explicit JSON `null`; it must not be omitted, replaced
with an empty string or inferred later.

Serialize the snapshot as UTF-8 JSON with:

- sorted object keys;
- compact separators `(",", ":")`;
- `ensure_ascii=False`;
- no NaN/infinity and no trailing newline.

Compute:

```text
source_snapshot_hash = "sha256:" + sha256(exact_snapshot_utf8_bytes).hexdigest()
```

The result must full-match `sha256:[0-9a-f]{64}`. It is the hash of the four-key snapshot
object only, not the enclosing activity payload, request body, ORM representation or a
later Case state.

### Exact lifecycle payload

Pass a payload with exactly these three top-level keys and no others:

```json
{"evidence_schema":"FPMS_CASE_OPENED_EVIDENCE_V1","source_snapshot":{"case_id":"<Case.id>","case_no":"<Case.case_no>","case_type":"<Case.case_type>","client_id":null},"source_snapshot_hash":"sha256:<64-lower-hex>"}
```

For a non-null `Case.client_id`, its exact JSON string replaces `null` and no other contract
changes. `append_case_activity()` remains the only canonical payload persistence seam; its
persisted canonical payload bytes are the durable replay truth.

### Exact evidence reference and event facts

Pass exactly one `EvidenceReference` in a one-element tuple with:

```text
case_id       = Case.id
evidence_kind = "CASE_RECORD"
object_type   = "Case"
object_id     = Case.id
content_hash  = source_snapshot_hash
captured_at   = opened_at
```

The existing `opened_at` remains one server-owned naive datetime value and is used
byte-for-byte for `captured_at`, `effective_at` and `occurred_at`. Preserve all other
accepted command facts:

- `event_type="CASE_OPENED"`;
- `lane=ActivityLane.LIFECYCLE`;
- `actor_id=user_id` from the authenticated current user;
- `idempotency_key=f"case-opened:{Case.id}"`; and
- `confirmation_status=ConfirmationStatus.CONFIRMED`.

Do not add a second evidence item, a synthetic evidence object, a new evidence kind, a
reviewer, a source/supersede activity or an adapter-owned projection decision.

### Fail-closed and replay contract

- D4-01 remains the sole rule owner for exact `CASE_OPENED` evidence cardinality, kind,
  object type, same-case identity, hash shape and capture time. This adapter must supply
  that contract; it must not duplicate, weaken or bypass the rule.
- The accepted apply/append seams validate and persist the complete command. Missing,
  extra, malformed or cross-case evidence and invalid timestamps fail through their
  existing error surfaces before the owning commit. Do not catch and convert such failures
  into a successful Case response or a partial row.
- A same-case `case-opened:<case-id>` lifecycle replay compares the entire persisted
  three-key payload and the complete evidence reference, including hash and capture time.
  An exact replay reuses the original activity without mutation. Any payload/evidence/time/
  actor mismatch remains HTTP 409 `LIFECYCLE_IDEMPOTENCY_CONFLICT` with no write.
- Later mutation of `Case.case_no`, `Case.case_type`, `Case.client_id` or any other Case
  field must not reconstruct, replace or invalidate the original durable snapshot. Replay
  truth comes from the persisted activity payload and evidence row.
- The Case POST itself does not gain a new client idempotency contract. Existing duplicate
  case-create behavior remains unchanged; replay here means the accepted lifecycle
  activity seam under its existing same-case idempotency key.

### Transaction and observable HTTP contract

- Case insert, existing child inserts, lifecycle activity, the one evidence row and the
  lifecycle projection remain one atomic write set in the existing create transaction.
- `apply_lifecycle_event()` and `append_case_activity()` retain caller-owned transaction
  behavior and must not commit or roll back internally.
- The existing create entrypoint commits exactly once, only after the case, activity,
  evidence and projection have all succeeded. Once the write phase has begun, a failure
  before completion is rolled back once by the owning boundary and re-raised; it must leave
  no Case, child row, lifecycle activity, evidence row, revision or projection write.
- Do not assign the lifecycle axes directly. Preserve Task 55's accepted initial legacy
  compatibility status and let the accepted lifecycle seam own the projected state.
- Preserve `POST /api/v1/cases`, permission `Case.Create`, server-owned current user,
  strict input-status gate, response envelope and successful HTTP 201 response. A supplied
  legacy `status` remains HTTP 422. No new route, request field, response field, permission
  or status-code mapping is introduced.

## Explicit Non-Closure

- No change to the D4-01 `CASE_OPENED` evidence guard or any lifecycle rule/registry.
- No change to lifecycle contracts, apply/orchestration, activity append, legacy projection,
  activity/evidence models or persistence tables.
- No change to the Case POST route, API dependency, permission, response serialization,
  request/status schema, duplicate-case policy or other case-create validation.
- No case edit, batch filing, filing preparation/external submission/receipt, OA, document,
  fee, deadline, grant or other lifecycle adapter.
- No schema, migration, seed, router, frontend, customer decision or source activation.
- No new helper module, evidence registry, envelope, public interface or speculative
  abstraction.
- No edit to accepted predecessor tasks/evidence, inherited regression files, the batch
  manifest, cumulative overlay or Delta-4 specification.
- No refactor, adjacent cleanup, repo-wide verification, release gate, commit, push, reset,
  clean, stash or discard; no second closure slice.

## Dependencies and Ownership

### Exact direct dependencies

1. `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01` must be independently accepted
   `PASS` first. Its exact one-item `CASE_RECORD / Case` matrix is immutable here.
2. `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01` (accepted catalog Task 55) must
   remain `PASS`. Its input-status gate, create route, HTTP 201 behavior and existing
   case-create semantics are immutable here.

Customer decision gate: `None`.

### Accepted read-only seams and inherited regressions

- `backend/app/modules/cases/lifecycle_contracts.py::EvidenceReference`,
  `backend/app/modules/cases/lifecycle_service.py::apply_lifecycle_event`, and
  `backend/app/modules/cases/lifecycle_activity_service.py::append_case_activity` are
  accepted immutable seams, not allowlisted prerequisites to edit.
- `backend/tests/test_v8_case_create_status_gate.py` is the accepted Task 55 public adapter
  regression and remains read-only.
- `backend/tests/test_case_missing_fields_crud.py` is Task 55's accepted inherited
  case-create/read regression and remains read-only.
- `backend/app/modules/cases/api.py`, `schemas.py`, `models.py` and every lifecycle source or
  test not named in the allowlist remain read-only. The existing carriers already support
  the exact evidence row; no hidden schema/router/export prerequisite is authorized.

If any accepted seam or inherited regression requires a source edit outside this task's
allowlist, stop this lane and escalate the exact mismatch. Do not absorb that prerequisite.

### Shared ownership and serialization

- The case-service order is strictly accepted Task 55 → D4-02 → catalog Task 60
  (`FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`). Task 60 must not edit or verify
  `backend/app/modules/cases/service.py` concurrently and starts only after this task is
  independently accepted.
- No other agent may edit or verify the allowlisted source/test concurrently with this
  task.
- The task-owned and inherited tests write SQLite. The worker must report
  `READY_FOR_SERIAL_TEST`, wait for an explicit controller `GRANT`, acquire
  `GLOBAL_SQLITE_SERIAL_QUEUE`, run with maximum writers `1`, and release the lock.

## Remaining Follow-Up Task IDs

- `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_v8_case_create_opened_evidence_adapter.py`
- `artifacts/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01/**`

No other source, test, task, manifest, specification, script, evidence family or shared-
ownership path is authorized. Preserve the dirty worktree and use the Evidence 1.1 captured
baseline to subtract every pre-existing allowlist change and enumerate exact outside-dirty
paths.

## Verification Commands

Use task-scoped TDD through the public create/lifecycle seams. Do not run any command in
parallel with another SQLite writer.

### Preflight and Evidence 1.1 initialization

Before product/test edits, verify the frozen hash and the two exact dependencies:

```bash
test "$(shasum -a 256 docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md | awk '{print $1}')" = "7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8"
./scripts/task_validate.sh FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01
./scripts/task_validate.sh FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01
./scripts/evidence_init.sh FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01.md \
  --allowlist backend/app/modules/cases/service.py \
  --allowlist backend/tests/test_v8_case_create_opened_evidence_adapter.py
```

Do not call the installed helper's `init` entry point directly. Initialize once through the
repository Evidence 1.1 wrapper before implementation edits.

### RED

Create `backend/tests/test_v8_case_create_opened_evidence_adapter.py` first and add one
behavior at a time. Begin with a public Case POST assertion for the exact successful
persisted payload/evidence tuple, then run after controller `GRANT` and lock acquisition:

```bash
cd backend && .venv/bin/pytest -q tests/test_v8_case_create_opened_evidence_adapter.py
```

Record the expected nonzero RED against the accepted predecessor: D4-01 rejects the empty
evidence currently supplied by `create_case()`, or the persisted exact payload/evidence
assertion is missing. An import/collection failure, a dependency failure, an unrelated
create validation failure or a changed D4-01 rule is not a valid RED.

The task-owned test must cover, through public seams and persisted state:

1. null-client and non-null-client canonical snapshots;
2. byte-exact three-key payload and recomputed four-key snapshot hash;
3. exactly one same-case `CASE_RECORD / Case` evidence row with matching object ID/hash;
4. one identical naive `opened_at` across effective, occurred and captured times;
5. unchanged server-owned actor, idempotency key, HTTP 201 and Task 55 projection;
6. exact lifecycle replay reuse after later mutable Case-field changes, and changed replay
   HTTP 409 with no mutation;
7. exactly one owning commit on success; and
8. injected pre-commit lifecycle/persistence failure leaves no partial Case, child,
   activity, evidence, revision or projection state and performs the owning rollback.

### GREEN and targeted inherited regressions

Implement the smallest correction in `service.py`, then run after controller `GRANT` and
lock acquisition:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_case_create_opened_evidence_adapter.py \
  tests/test_v8_case_create_status_gate.py \
  tests/test_case_missing_fields_crud.py
```

The last two tests are read-only inherited regressions. Their inclusion does not authorize
editing them. Do not rerun broad lifecycle or case suites after their accepted dependency
gates pass unless a concrete regression is demonstrated.

### Scoped lint and format

```bash
cd backend && .venv/bin/ruff check --fix \
  app/modules/cases/service.py \
  tests/test_v8_case_create_opened_evidence_adapter.py
cd backend && .venv/bin/ruff format \
  app/modules/cases/service.py \
  tests/test_v8_case_create_opened_evidence_adapter.py
cd backend && .venv/bin/ruff check \
  app/modules/cases/service.py \
  tests/test_v8_case_create_opened_evidence_adapter.py
```

Do not run repo-wide Ruff/pytest, frontend build, Playwright or the release gate.

### Scoped diff, evidence and independent acceptance

```bash
git diff --check -- \
  backend/app/modules/cases/service.py \
  backend/tests/test_v8_case_create_opened_evidence_adapter.py \
  tasks/postdemo/v8/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01.md
./scripts/evidence_finalize.sh FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01
```

Record the required latest nonzero RED and zero GREEN, inherited regression, lint and scope
results with their logs through the shared Evidence 1.1 producer. Do not hand-author
`results.jsonl` or omit tracked/untracked task output.

One independent case/lifecycle domain reviewer must issue an evidence-backed `APPROVED`
verdict with `P0=P1=P2=0`, explicitly checking canonical bytes/hash, exact evidence tuple,
immutable replay, transaction atomicity, Task 55 preservation and allowlist scope. The
implementer cannot approve this task.

After the summary and task status are truthfully set to PASS, run:

```bash
./scripts/task_validate.sh FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01
python3 scripts/atomic_evidence_validate.py \
  FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01 \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope
```

## Evidence Path

- `artifacts/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when the task starts from a
  dirty worktree.
- Required latest steps: `lint`, `test`, `independent_review`, and `scope`, with the required
  RED and targeted inherited-regression logs preserved.

## Done Definition

This implementation task is PASS only when all of the following are true:

- the frozen Delta-4 hash and both exact direct dependencies remain accepted;
- `create_case()` builds the four-key snapshot from the just-flushed same-transaction Case,
  persists the exact three-key payload, and supplies exactly one matching
  `CASE_RECORD / Case` evidence reference to D4-01;
- canonical snapshot bytes/hash, explicit null/non-null client behavior, one shared naive
  time, server-owned actor and existing idempotency key are exact;
- exact replay reuses immutable persisted payload/evidence despite later Case mutation,
  while changed replay fails 409 without mutation;
- one owning success commit makes case/children/activity/evidence/projection visible
  together, and the required failure regression proves no partial durable state;
- the task-owned RED/GREEN and both read-only Task 55 regressions are recorded and GREEN;
- targeted Ruff/format, scoped diff and baseline-subtracted scope validation pass;
- task-local Evidence 1.1 artifacts contain the latest required results/logs and no scope
  drift; one independent case/lifecycle reviewer approves with zero findings; and
- the repository task gate and atomic evidence validation pass.

Only then may the task status become `PASS`. The batch-filing adapter, all other lifecycle
events and every explicit non-closure remain separately owned and unimplemented by this
task.
