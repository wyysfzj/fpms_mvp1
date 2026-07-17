# FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Materialization batch: `FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01`
Materialization row: `07 / D4-07`
Materialization wave: `M4-B`
High execution wave: `H4-1`
Risk tier: `HIGH`
Scope: `Foundation`
Contract state: `CONTRACT FROZEN`
Materialization owner role: Document architect
Executor role: High implementation agent / Backend Developer

## Authoritative Contract

- `AGENTS.md`
- Delta-4 specification:
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- Frozen Delta-4 specification SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`
- Supplemental batch manifest row `07`:
  `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`
- Direct Delta-4 predecessor:
  `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md`
- Accepted Delta-3 registration guard:
  `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01.md`

The hash-locked Delta-4 specification controls if this task text is read ambiguously. A
specification hash mismatch, dependency regression, non-Status predecessor drift or
shared-file ownership conflict fails closed and returns only this affected lane to Ultra
contract review. Do not reopen broad V8 source analysis.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: after D4-06 supplies the two production `EvidenceRole` members, the
  public registration service still rejects each newly allowed pair as an unlisted role
  before database access.
- GREEN expectation: the service admits exactly the three newly allowed combinations,
  rejects `GENERATED_ATTACHMENT` / `FINAL`, and preserves the accepted original-nine,
  RAW-only-DRAFT and future-unlisted-role behavior.

## Exact Closure Slice

After D4-06 is independently accepted, add exactly the following two explicit role/state
rows to the fail-closed registration matrix used by
`register_evidence_version()` in
`backend/app/modules/documents/evidence_service.py`:

| `EvidenceRole` | `DRAFT` | `FINAL` |
| --- | --- | --- |
| `GENERATED_ATTACHMENT` | allow | deny |
| `OA_STRUCTURED_ATTACHMENT` | allow | allow |

This is an additive correction to the accepted Delta-3 matrix, not a replacement or an
enum-derived policy. The accepted matrix remains exact:

- each of the original nine formal role values remains allowed for both `DRAFT` and
  `FINAL`;
- `RAW_ATTACHMENT` remains allowed only for `DRAFT` and denied for `FINAL`;
- `GENERATED_ATTACHMENT` is allowed only for `DRAFT` and denied for `FINAL`;
- `OA_STRUCTURED_ATTACHMENT` is allowed for `DRAFT` and `FINAL`; and
- every unknown or future role value not explicitly listed remains denied for both states.

The implementation must remain an explicit positive role/state matrix. It must not use
enum iteration, enum membership alone, a catch-all branch, `else: allow`, or any rule that
automatically grants registration authority to a newly added `EvidenceRole`.

Preserve the accepted validation order: validate the exact command and field shapes, exact
current `EvidenceRole`, exact `EvidenceVersionState` and lowercase SHA-256 content hash;
then enforce the role/state matrix before the first use of `transaction` or
`append_case_activity()`.

`GENERATED_ATTACHMENT` / `FINAL` must fail before database or activity access through the
existing registration error surface:

- `BusinessError`;
- status `400`;
- code `EVIDENCE_VERSION_INVALID`;
- `details={"field":"state"}`.

Any unknown or future role under either otherwise valid state continues to fail before
database or activity access through:

- `BusinessError`;
- status `400`;
- code `EVIDENCE_VERSION_INVALID`;
- `details={"field":"role"}`.

No new message string is part of this Delta-4 contract. Preserve the existing service
surface and assert the status, code and field details above.

For an allowed new pair, control proceeds into the already accepted registration service
without another behavioral change. The returned and persisted role/state must equal the
command, the new version begins in the accepted `PENDING` review state, and the existing
immutable-version, current-identity, version-allocation, activity, evidence-reference and
caller-owned transaction semantics remain unchanged.

Neither new role becomes externally submittable. D4-06's accepted preservation regression
continues to keep both values outside the exact Delta-3 nine-role external-submission
positive allowlist. OA manifest labels remain manifest roles and are not registration
roles.

## Explicit Non-Closure

- No `EvidenceRole` enum addition, deletion, rename, reorder or alias. D4-06 exclusively
  owns the two enum members and inherited exact-iteration expectation.
- No RAW-to-OA promotion, derivation, manifest link or activity. D4-08 exclusively owns
  formal OA structured-attachment promotion.
- No generated-attachment adapter, actor propagation, template identity, lineage, review,
  hash, persistence or API behavior. Existing V8 Task 50 owns that closure.
- No external-submission positive allowlist change, automatic eligibility, finalization or
  readiness behavior; both new roles remain denied there.
- No change to command/result contracts, evidence review, derivation, current-version,
  lifecycle, legal status, fee, deadline, permission or customer-decision behavior.
- No API, router, schema, model, migration, seed, frontend, export or shared registry change.
- No edit to an inherited Delta-3 test/task/evidence, D4-06, D4-08, Task 50, batch manifest,
  Delta-4 specification or any other task.
- No refactor, adjacent cleanup, repo-wide verification, release gate, commit, push, reset,
  clean, stash or discard; no second closure slice.

## Dependencies and Ownership

### Direct dependencies

1. `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` must be independently accepted
   `PASS` at the frozen Delta-4 hash. Its exact twelve-member `EvidenceRole` contract must
   expose `GENERATED_ATTACHMENT` followed by `OA_STRUCTURED_ATTACHMENT`, while preserving
   the first ten members and the unchanged external-submission exclusion.
2. `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` must remain accepted `PASS`.
   Its pre-database guard, original-nine positive matrix, RAW-only-DRAFT row and
   future-unlisted-role denial are inherited unchanged.

Customer decision gate: `None`.

### Shared ownership and serialization

- The H4-1 document chain is strictly D4-06 → D4-07 → D4-08. Product/test execution for
  this task must not start before D4-06 is independently accepted, and D4-08 must not start
  before this task is independently accepted.
- Row 14, `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`, also waits for
  D4-06 and this task to be independently accepted.
- This task is the sole owner of
  `backend/app/modules/documents/evidence_service.py` and
  `backend/tests/test_v8_delta4_registration_matrix.py` during its execution. No other
  `evidence_service.py` owner or shared-file verification may run concurrently.
- Every task-owned or inherited registration test writes or may write SQLite. Before each
  pytest command, the worker must report `READY_FOR_SERIAL_TEST`, wait for an explicit
  controller `GRANT`, acquire `GLOBAL_SQLITE_SERIAL_QUEUE`, run with maximum writers `1`,
  and release the repository lock afterward.
- Read-only lint and review may run only when no other owner is editing the shared source.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01`
- `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`

## Allowed Files

- `backend/app/modules/documents/evidence_service.py`
- `backend/tests/test_v8_delta4_registration_matrix.py`
- `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01.md`
- `artifacts/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01/**`

No other source, test, task, manifest, specification, script, evidence family or shared-
ownership path is authorized. Inherited registration and external-submission tests are
read-only verification inputs. Preserve the dirty worktree and use the Evidence 1.1
captured baseline to subtract every pre-existing allowlist change and enumerate exact
outside-dirty paths.

## Runtime and Error Contracts

Keep the accepted public callable and command/result types unchanged:

```python
def register_evidence_version(
    command: RegisterEvidenceVersionCommand,
    transaction: Session,
) -> EvidenceVersionResult:
    ...
```

- The service remains caller-transaction-owned and must not commit, rollback, close,
  retry a lock or rely on `RETURNING`.
- Denied role/state combinations perform zero transaction lookup, scalar query, add,
  execute, flush, refresh or mutation and append no activity/evidence reference.
- Allowed combinations preserve the accepted registration persistence and activity path;
  this task does not add a new endpoint or response envelope.
- Expected observable service status for the denied classes in this task is `400`.
  Expected endpoint status codes: `None`.

## Exact TDD Contract

High must test one behavior at a time through the public
`register_evidence_version()` seam in
`backend/tests/test_v8_delta4_registration_matrix.py`.

1. Use the real post-D4-06 production `EvidenceRole` members for all original, RAW,
   `GENERATED_ATTACHMENT` and `OA_STRUCTURED_ATTACHMENT` cases. Do not monkeypatch a new
   role that D4-06 owns.
2. First prove RED for the three intended positive combinations:
   `GENERATED_ATTACHMENT` / `DRAFT`, `OA_STRUCTURED_ATTACHMENT` / `DRAFT`, and
   `OA_STRUCTURED_ATTACHMENT` / `FINAL`. With D4-06 present and D4-07 absent, each reaches
   the existing unlisted-role 400 instead of accepted registration. Collection failure,
   a missing D4-06 member, invalid fixture/command/hash or unrelated failure is not a valid
   RED.
3. GREEN those same three combinations through serialized real SQLite registration. Assert
   the returned and stored exact role/state, accepted `PENDING` review state and one
   accepted registration activity/evidence-link path; the service must not commit.
4. Prove `GENERATED_ATTACHMENT` / `FINAL` returns the exact state-field 400 surface before
   any transaction or activity access and creates no pending ORM write.
5. Prove both states of one clearly named future-unlisted role retain the exact role-field
   400 surface before any transaction or activity access. Only these future-role cases may
   use a test-local forward enum with a case-scoped monkeypatch matching the accepted
   Delta-3 guard technique.
6. Run the accepted Delta-3 RAW guard and inherited register-version suite unchanged to
   prove all original-nine pairs, RAW-only-DRAFT, future-role denial and the accepted
   registration service remain intact.
7. Run the inherited external-submission role-allowlist regression unchanged to prove that
   neither newly registerable role gained external-submission authority.

A private constant assertion alone is not acceptance. The task-owned test must exercise
the public service, and inherited tests remain read-only.

## Verification Commands

Use only the following task-scoped implementation verification contract.

### Preflight and Evidence 1.1 initialization

Before product/test edits, verify the frozen authority and both dependencies:

```bash
test "$(shasum -a 256 docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md | awk '{print $1}')" = "7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8"
./scripts/task_validate.sh FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01
./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01
./scripts/evidence_init.sh FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01.md \
  --allowlist backend/app/modules/documents/evidence_service.py \
  --allowlist backend/tests/test_v8_delta4_registration_matrix.py
```

Do not call the installed helper's `init` entry point directly. Initialize once through
the repository wrapper after dependency PASS and before product/test edits.

### RED

After controller `GRANT` and serialization-lock acquisition, create only the task-owned
test and run:

```bash
cd backend && .venv/bin/pytest -q tests/test_v8_delta4_registration_matrix.py
```

Record the expected nonzero RED caused only by the three missing positive matrix entries.

### GREEN and targeted regressions

Implement the smallest explicit matrix correction and, under a fresh controller `GRANT`
and serialization-lock acquisition, run:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_delta4_registration_matrix.py \
  tests/test_v8_raw_attachment_registration_guard.py \
  tests/test_v8_document_evidence_register_version.py \
  tests/test_v8_external_submission_role_allowlist.py
```

### Targeted lint and format

```bash
cd backend && .venv/bin/ruff check --fix \
  app/modules/documents/evidence_service.py \
  tests/test_v8_delta4_registration_matrix.py
cd backend && .venv/bin/ruff format \
  app/modules/documents/evidence_service.py \
  tests/test_v8_delta4_registration_matrix.py
cd backend && .venv/bin/ruff check \
  app/modules/documents/evidence_service.py \
  tests/test_v8_delta4_registration_matrix.py
```

Do not run repo-wide Ruff/pytest, frontend build, Playwright or the release gate.

### Scoped diff, independent review and evidence finalization

```bash
git diff --check -- \
  backend/app/modules/documents/evidence_service.py \
  backend/tests/test_v8_delta4_registration_matrix.py \
  tasks/postdemo/v8/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01.md
./scripts/evidence_finalize.sh FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01
```

Record RED, GREEN/regressions, lint, independent review and scope through the shared
Evidence 1.1 producer; do not hand-author `results.jsonl`. PASS requires task-local
`results.jsonl`, `summary.md`, baseline-subtracted `git/diff.patch`, dirty-baseline
artifacts when applicable, latest required zero-result/log validation and no outside-
allowlist path.

One independent document-evidence domain reviewer must issue an evidence-backed
`APPROVED` verdict with `P0=P1=P2=0`. The implementer cannot approve this task. Review must
confirm the exact two additive rows, pre-database denied cases, future-role fail closure,
unchanged RAW/original matrix and unchanged external-submission exclusion.

### Task and atomic evidence gates

After the summary and task status are truthfully set to PASS, run:

```bash
./scripts/task_validate.sh FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01
python3 scripts/atomic_evidence_validate.py \
  FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01 \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope
```

## Evidence Path

- `artifacts/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when the task starts from a
  dirty worktree.
- Required latest steps: `lint`, `test`, `independent_review`, and `scope`.

## Done Definition

This implementation task is PASS only when all of the following are true:

- the hash-locked Delta-4 authority, independently accepted D4-06 role extension and
  accepted Delta-3 registration guard remain valid;
- one expected public-service RED proves only the missing positive entries for the two new
  role rows;
- `GENERATED_ATTACHMENT` allows only `DRAFT`, and `OA_STRUCTURED_ATTACHMENT` allows exactly
  `DRAFT` and `FINAL`;
- `GENERATED_ATTACHMENT` / `FINAL` and both states of a future-unlisted role fail with the
  exact 400/code/details surfaces before database or activity access;
- all original-nine role/state pairs and RAW-only-DRAFT behavior remain unchanged, and
  neither new role gains external-submission authority;
- the task-owned public-service test, inherited targeted regressions, scoped Ruff/format,
  scoped diff and baseline-subtracted scope validation pass under required serialization;
- task-local Evidence 1.1 artifacts contain the latest required results/logs and no scope
  drift; an independent document-evidence reviewer approves with zero findings; and
- the repository task gate and atomic evidence validation pass.

Only then may the task status become `PASS`. D4-08 OA promotion, Task 50 generated-
attachment adaptation and every other non-closure remain separately owned and
unimplemented by this task.
