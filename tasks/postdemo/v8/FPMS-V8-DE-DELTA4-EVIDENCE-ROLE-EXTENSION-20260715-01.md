# FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-16 / ULTRA CONTRACT FROZEN 2026-07-15
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Materialization batch: `FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01`
Materialization row: `06 / D4-06`
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
- Supplemental batch manifest row `06`:
  `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`
- Accepted direct predecessor:
  `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md`
- Accepted inherited external-submission guard:
  `tasks/postdemo/v8/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01.md`

The hash-locked Delta-4 specification controls if this task text is read ambiguously. A
specification hash mismatch, dependency regression, or allowlist conflict fails closed and
returns only this affected lane to Ultra contract review.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-INTERFACE`

- RED expectation: the two allowlisted contract tests expect the exact ordered twelve-member
  `EvidenceRole` interface, but production still exposes only the accepted first ten members;
  the mismatch is only the missing two-member suffix.
- GREEN expectation: appending the exact two new members after `RAW_ATTACHMENT` makes both
  contract tests pass while the first ten pairs, all other contracts, and the original-nine
  external-submission positive allowlist remain unchanged.

## Exact Closure Slice

Extend only `EvidenceRole` in
`backend/app/modules/documents/evidence_contracts.py` by appending exactly these two unique
members, in this exact order, immediately after `RAW_ATTACHMENT`:

```python
GENERATED_ATTACHMENT = "GENERATED_ATTACHMENT"
OA_STRUCTURED_ATTACHMENT = "OA_STRUCTURED_ATTACHMENT"
```

The complete accepted ordered `(name, value)` sequence becomes exactly:

```text
FILING_FULL_WORD
TRACKED_REVISED_WORD
FILING_COMPONENT
EXTERNAL_XML_PACKAGE
OFFICIAL_SUBMISSION_LIST
OFFICIAL_FINAL_PDF
SUBMITTED_XML
OFFICIAL_RECEIPT
CLIENT_LETTER_WORD
RAW_ATTACHMENT
GENERATED_ATTACHMENT
OA_STRUCTURED_ATTACHMENT
```

The existing first ten names, values and order must not change. Neither new member is an
alias. No existing member is renamed, reordered, removed or rewritten.

In `backend/tests/test_v8_document_evidence_contracts.py`, change only the inherited exact
`ENUM_MEMBERS[EvidenceRole]` expectation from ten pairs to twelve by appending:

```python
("GENERATED_ATTACHMENT", "GENERATED_ATTACHMENT"),
("OA_STRUCTURED_ATTACHMENT", "OA_STRUCTURED_ATTACHMENT"),
```

No other assertion, fixture, import, contract expectation or formatting-only region in the
inherited test changes. This ten-to-twelve expectation update is required GREEN coverage of
the same enum closure, not a second product closure.

Create `backend/tests/test_v8_delta4_evidence_role_extension.py` as the task-owned Delta-4
regression. It must prove all of the following without changing a service:

1. the exact first-ten ordered prefix remains unchanged;
2. the exact ordered suffix is `GENERATED_ATTACHMENT`, then
   `OA_STRUCTURED_ATTACHMENT`, with matching string values;
3. the complete enum iteration contains exactly twelve unique pairs and no aliases; and
4. the accepted `_EXTERNAL_SUBMISSION_ELIGIBLE_ROLES` value set remains exactly the
   original nine formal values and is disjoint from both new values.

The external-submission assertion is a read-only preservation regression. It does not
authorize an edit to `evidence_workflow_service.py` or its accepted test. Enum validity,
matching content, a manifest label or the presence of either new member grants no external-
submission authority.

`GENERATED_ATTACHMENT` records a generated output classification.
`OA_STRUCTURED_ATTACHMENT` records that formal OA attachment promotion occurred. OA
manifest labels remain manifest roles and must not be added to `EvidenceRole`.

## Explicit Non-Closure

- No registration-state matrix change. D4-07 exclusively owns whether either new role may
  register as `DRAFT` or `FINAL`.
- No RAW-to-OA promotion, derivation, link or activity behavior. D4-08 owns that closure.
- No generated-attachment adapter, actor, hash, lineage, review or persistence behavior.
- No external-submission positive-set change, role rewrite, alias inference, automatic
  eligibility or new error/status surface.
- No evidence service, workflow service, API, router, schema, model, migration, seed,
  frontend, permission or customer-gate change.
- No other enum, dataclass, import, export or `__all__` change.
- No edit to any accepted predecessor task/evidence, batch manifest, Delta-4 specification,
  other test, or follow-up task.
- No refactor, adjacent cleanup, repo-wide verification, release gate, commit, push, reset,
  clean, stash or discard; no second closure slice.

## Dependencies and Ownership

### Direct dependency

- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01` must remain accepted `PASS`, with
  `RAW_ATTACHMENT` as the exact tenth ordered member and its task/evidence gates valid.

### Inherited fail-closed boundary

- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` remains accepted `PASS` and
  read-only. Its explicit positive set contains exactly the original nine formal role
  values. Adding an enum member alone must never expand that set.
- Customer decision gate: `None`.

### Shared ownership and serialization

- The H4-1 document chain is strictly D4-06 → D4-07 → D4-08. D4-07 and D4-08 must
  not start product execution until this task is independently accepted.
- Row 14, `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`, waits for both
  D4-06 and D4-07.
- No other agent may edit or verify
  `backend/app/modules/documents/evidence_contracts.py`,
  `backend/tests/test_v8_document_evidence_contracts.py`, or
  `backend/tests/test_v8_delta4_evidence_role_extension.py` concurrently with this task.
- The two task-owned contract tests are read-only and do not write SQLite. The inherited
  external-submission public-service regression writes SQLite and therefore requires the
  worker to report `READY_FOR_SERIAL_TEST`, wait for an explicit controller `GRANT`, acquire
  the repository serialization lock, run it with maximum writers `1`, and release the lock.
- Shared-file verification is serialized even when the targeted command is read-only.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01`
- `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01`
- `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md`
- `backend/app/modules/documents/evidence_contracts.py`
- `backend/tests/test_v8_document_evidence_contracts.py`
- `backend/tests/test_v8_delta4_evidence_role_extension.py`
- `artifacts/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01/**`

No other source, test, task, manifest, specification, script, evidence family or shared-
ownership path is authorized. Preserve the dirty worktree and use the Evidence 1.1 captured
baseline to subtract every pre-existing allowlist change and enumerate exact outside-dirty
paths.

## Runtime Contracts

- `EvidenceRole` remains a `str, Enum`; the contract module remains stdlib-only and
  performs no database, filesystem, network, policy or gate operation.
- Preserve every other enum, frozen dataclass shape, function-free interface boundary and
  the exact existing `__all__` order.
- The original-nine external-submission positive allowlist remains exact. Fresh or replay
  finalization presented with either new role continues to fail before downstream behavior
  with the accepted service status `409` and code
  `EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT`; this task changes no service implementation.
- This task adds no endpoint. Expected HTTP status codes for this pure interface extension:
  `None`.
- The D4-07 registration matrix and D4-08 promotion semantics remain unavailable until
  their separately owned tasks pass.

## Verification Commands

Use the following task-scoped TDD and verification contract.

### Preflight and Evidence 1.1 initialization

Before edits, verify the hash-locked authority and direct dependency:

```bash
test "$(shasum -a 256 docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md | awk '{print $1}')" = "7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8"
./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01
./scripts/task_validate.sh FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01
./scripts/evidence_init.sh FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01 \
  --task-file tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md \
  --allowlist backend/app/modules/documents/evidence_contracts.py \
  --allowlist backend/tests/test_v8_document_evidence_contracts.py \
  --allowlist backend/tests/test_v8_delta4_evidence_role_extension.py
```

Do not call the installed helper's `init` entry point directly. Evidence must be initialized
once through the repository wrapper before product/test edits.

### RED

First create only the task-owned regression and append only the two inherited expected
pairs. Run:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_delta4_evidence_role_extension.py \
  tests/test_v8_document_evidence_contracts.py
```

Record the expected nonzero RED. The accepted failure is the exact missing two-member
suffix while the first ten remain identical. Import/collection failure, an altered first-ten
member, a changed external allowlist, or an unrelated failure is not a valid RED.

### GREEN and targeted regressions

Append the two enum members and run the same two contract tests to GREEN:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_delta4_evidence_role_extension.py \
  tests/test_v8_document_evidence_contracts.py
```

After controller `GRANT` and serialization-lock acquisition, run the inherited public-
service guard unchanged:

```bash
cd backend && .venv/bin/pytest -q tests/test_v8_external_submission_role_allowlist.py
```

### Targeted lint and format

```bash
cd backend && .venv/bin/ruff check --fix \
  app/modules/documents/evidence_contracts.py \
  tests/test_v8_document_evidence_contracts.py \
  tests/test_v8_delta4_evidence_role_extension.py
cd backend && .venv/bin/ruff format \
  app/modules/documents/evidence_contracts.py \
  tests/test_v8_document_evidence_contracts.py \
  tests/test_v8_delta4_evidence_role_extension.py
cd backend && .venv/bin/ruff check \
  app/modules/documents/evidence_contracts.py \
  tests/test_v8_document_evidence_contracts.py \
  tests/test_v8_delta4_evidence_role_extension.py
```

Do not run repo-wide Ruff/pytest, frontend build, Playwright or the release gate.

### Scoped diff and evidence finalization

```bash
git diff --check -- \
  backend/app/modules/documents/evidence_contracts.py \
  backend/tests/test_v8_document_evidence_contracts.py \
  backend/tests/test_v8_delta4_evidence_role_extension.py \
  tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md
./scripts/evidence_finalize.sh FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01
```

Record RED, GREEN, targeted regression, lint, independent review and scope through the
shared Evidence 1.1 producer; do not hand-author `results.jsonl`. PASS requires task-local
`results.jsonl`, `summary.md`, baseline-subtracted `git/diff.patch`, dirty-baseline artifacts
when applicable, latest required zero-result/log validation and no outside-allowlist path.

One independent document-domain reviewer must issue an evidence-backed `APPROVED` verdict
with `P0=P1=P2=0`. The implementer cannot approve this task.

### Task and atomic evidence gates

After the summary and task status are truthfully set to PASS, run:

```bash
./scripts/task_validate.sh FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01
python3 scripts/atomic_evidence_validate.py \
  FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01 \
  --required-step lint \
  --required-step test \
  --required-step independent_review \
  --required-step scope
```

## Evidence Path

- `artifacts/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when the task starts from a
  dirty worktree.
- Required latest steps: `lint`, `test`, `independent_review`, and `scope`.

## Done Definition

This implementation task is PASS only when all of the following are true:

- the hash-locked Delta-4 authority and accepted RAW-role dependency remain valid;
- a task-owned expected RED proves only the missing ordered two-member suffix;
- `GENERATED_ATTACHMENT` and `OA_STRUCTURED_ATTACHMENT` are appended after
  `RAW_ATTACHMENT` with exact matching values, while the first ten pairs remain unchanged;
- the inherited exact-iteration test changes only from ten to the same exact twelve pairs,
  and the new Delta-4 regression proves exact order, uniqueness and exclusion from the
  unchanged original-nine external-submission positive set;
- both contract tests and the serialized inherited external-submission guard are GREEN;
- targeted Ruff/format, scoped diff and baseline-subtracted scope validation pass;
- task-local Evidence 1.1 artifacts contain the latest required results/logs and no scope
  drift; an independent document-domain reviewer approves with zero findings; and
- the repository task gate and atomic evidence validation pass.

Only then may the task status become `PASS`. The D4-07 registration matrix, D4-08 OA
promotion, generated-attachment adapter and every other non-closure remain separately owned
and unimplemented by this task.
