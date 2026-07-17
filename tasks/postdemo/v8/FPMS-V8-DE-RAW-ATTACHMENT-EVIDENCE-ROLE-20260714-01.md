# FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01

Status: PASS / INDEPENDENT REREVIEW APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Wave: `M5 — Foundation external prerequisites (delta-2)`
Phase: `foundation_external_prerequisite` (delta-2; outside the immutable baseline)
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
- Materialization row: `04`
- Delta-3 successor materialization row: `03`
- Expected manifest phase: `foundation_external_prerequisite`
- Immutable baseline membership: `outside`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Blocked Review Outcome — 2026-07-14

Independent review rejected the frozen two-line closure because adding
`RAW_ATTACHMENT` to the generic `EvidenceRole` enum implicitly expands an existing
runtime whitelist: external-submission finalization accepts any value validated by
`EvidenceRole(version.role)` and does not independently restrict eligibility to formal
external-submission roles. The enum-only change therefore cannot prove this task's
fail-closed statement that raw evidence satisfies no external-submission or formal gate.

The attempted source and test additions have been safely reverted to their captured
pre-task hashes. This task remains blocked until Ultra updates the contract and dependency
graph with both:

- an independent fail-closed prerequisite that explicitly restricts formal/external-
  submission role eligibility and excludes raw evidence; and
- a targeted negative regression proving raw evidence cannot satisfy the affected formal
  gate before the enum extension is reconsidered.

The required prerequisite task ID has not been materialized and is intentionally not
guessed here. No workflow/service fix, policy change or new closure is authorized inside
this blocked task.

The frozen contract below is retained only as rejected history and MUST NOT be executed
again until the required Ultra contract/dependency update and independent re-review exist.

## Delta-3 Successor Re-freeze — 2026-07-14

The complete blocked review outcome above is preserved as rejected history. Its finding
remains authoritative for an unguarded dependency graph: adding the enum member alone
would still expand unsafe runtime behavior. Delta-3 resolves only that dependency defect,
not the finding itself, by making both independently owned guards direct prerequisites:

- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`

Both prerequisite tasks and their required evidence/task gates must be `PASS` before this
task starts in the H3-3 single lane. High then executes the original enum-only RED/GREEN
closure unchanged. After GREEN, High must rerun both guard suites read-only with the real
`EvidenceRole.RAW_ATTACHMENT` member, proving RAW remains DRAFT-only at registration and
cannot fresh or replay external submission. String stand-ins, mocks or a locally faked
enum value do not satisfy these regressions.

This successor section does not authorize either service fix, any test edit outside the
original exact contract-test delta, or deletion or reinterpretation of the rejected
history. The original closure, allowlist, non-closure and remaining adapter/overlay
follow-ups remain unchanged. Because H3-3 has no peer lane, atomic evidence validation
uses the repository wrapper without manifest or peer arguments.

## Task Contract Profile

Task Contract Profile: `TC-INTERFACE`

- RED expectation: After the exact contract test appends the tenth ordered
  `EvidenceRole` pair, targeted pytest fails because the accepted interface exposes only
  the original nine members.
- GREEN expectation: The same targeted test passes after `RAW_ATTACHMENT` is appended to
  `EvidenceRole`; the original nine members, all other contracts and the pure-interface
  boundary remain unchanged.

## Exact Closure Slice

Extend only the accepted document-evidence role interface by appending
`RAW_ATTACHMENT = "RAW_ATTACHMENT"` after the original nine `EvidenceRole` members in
`backend/app/modules/documents/evidence_contracts.py`, and update the exact ordered
`EvidenceRole` expectation in
`backend/tests/test_v8_document_evidence_contracts.py` with that tenth pair.

## Ultra Contract Freeze — 2026-07-14

This is one additive, fail-closed intake-role interface prerequisite. It does not reopen
or rewrite the accepted `FPMS-V8-DE-CONTRACTS-20260712-01` task.

### Exact enum extension

The first nine member names, values and order remain byte-for-semantic-order compatible.
Append exactly one member after `CLIENT_LETTER_WORD`:

```python
class EvidenceRole(str, Enum):
    FILING_FULL_WORD = "FILING_FULL_WORD"
    TRACKED_REVISED_WORD = "TRACKED_REVISED_WORD"
    FILING_COMPONENT = "FILING_COMPONENT"
    EXTERNAL_XML_PACKAGE = "EXTERNAL_XML_PACKAGE"
    OFFICIAL_SUBMISSION_LIST = "OFFICIAL_SUBMISSION_LIST"
    OFFICIAL_FINAL_PDF = "OFFICIAL_FINAL_PDF"
    SUBMITTED_XML = "SUBMITTED_XML"
    OFFICIAL_RECEIPT = "OFFICIAL_RECEIPT"
    CLIENT_LETTER_WORD = "CLIENT_LETTER_WORD"
    RAW_ATTACHMENT = "RAW_ATTACHMENT"
```

No alias, fallback member, enum reorder, other enum change, dataclass change or `__all__`
change is authorized. `EvidenceRole` is already exported.

### Frozen fail-closed meaning

`RAW_ATTACHMENT` means an original attachment persisted through the generic attachment
POST whose formal business-evidence semantics have not yet been proven by a dedicated
adapter.

- It satisfies no filing, OA, grant, external-submission, submission or receipt gate.
- It is not equal to any formal role: `FILING_FULL_WORD`, `TRACKED_REVISED_WORD`,
  `FILING_COMPONENT`, `EXTERNAL_XML_PACKAGE`, `OFFICIAL_SUBMISSION_LIST`,
  `OFFICIAL_FINAL_PDF`, `SUBMITTED_XML`, `OFFICIAL_RECEIPT` or `CLIENT_LETTER_WORD`.
- Formal promotion requires a new evidence version with the proved formal role plus a
  registered derivation from the raw version. The `RAW_ATTACHMENT` version's role must
  never be rewritten in place.
- An identical content hash carries no role authority and does not make raw evidence
  equivalent to, or sufficient for, any formal evidence role or gate.

These are fail-closed contract boundaries for downstream owners. This task adds no
policy table, readiness predicate, gate evaluator, promotion service or automatic role
inference.

### Exact contract-test delta

In the existing `ENUM_MEMBERS[EvidenceRole]` ordered expectation, append only:

```python
("RAW_ATTACHMENT", "RAW_ATTACHMENT"),
```

The existing exact enum comparison must prove all ten ordered `(name, value)` pairs.
Keep the existing stdlib-only/no-service-functions test green; do not add a service,
policy, API, persistence or gate test to this `TC-INTERFACE` closure.

### Frozen RED / GREEN sequence

1. Confirm the accepted `FPMS-V8-DE-CONTRACTS-20260712-01` dependency and its historical
   PASS evidence without editing either.
2. Append the tenth expected pair to the exact contract test and run the targeted pytest
   to RED. The expected failure is the ordered-role mismatch caused only by the missing
   `EvidenceRole.RAW_ATTACHMENT` member.
3. Append the exact enum member after `CLIENT_LETTER_WORD` and run the same targeted
   pytest to GREEN.
4. Run only task-scoped Ruff, diff, independent review, task and atomic-evidence gates.

RED must not be manufactured by changing another member or downstream product behavior.
GREEN is only the additive enum contract and its exact ordered test.

## Explicit Non-Closure

No upload API, attachment service, evidence service, persistence, policy, readiness or
gate behavior; no schema, migration, seed, endpoint, UI or adapter implementation; no
formal-role promotion or role inference; no unrelated cleanup; and no second closure
slice. Do not edit the accepted `FPMS-V8-DE-CONTRACTS-20260712-01` task, its old PASS
evidence, or any other historical PASS evidence.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-CONTRACTS-20260712-01` — accepted `PASS` before this additive extension.
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` — direct dependency;
  required `PASS` before H3-3 so RAW can only be registered as `DRAFT`.
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` — direct dependency;
  required `PASS` before H3-3 so RAW cannot fresh or replay external submission.

### External, gate and inherited prerequisites

- This task is an external Foundation prerequisite introduced by the accepted delta-2.
- Delta-3 re-freezes it as the row-03 H3-3 successor behind both direct guards; the prior
  blocked finding is resolved only by those dependencies.
- Customer gate: `None`.

### Shared ownership serialization

- Never run concurrently with another owner editing
  `backend/app/modules/documents/evidence_contracts.py` or
  `backend/tests/test_v8_document_evidence_contracts.py`.
- Preserve the predecessor task and evidence as read-only historical PASS inputs.
- Run both post-GREEN guard suites read-only and serially through
  `GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writers `1`; do not overlap either suite with
  another SQLite-writing verification job.
- Complete this additive role prerequisite before either follow-up consumes
  `RAW_ATTACHMENT`.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
- `FPMS-V8-OVERLAY-CONTRACTS-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md`
- `backend/app/modules/documents/evidence_contracts.py`
- `backend/tests/test_v8_document_evidence_contracts.py`
- `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01/**`

No other source, test, task, manifest, old evidence family or shared ownership file is
authorized. Preserve the captured dirty baseline.

## Runtime Contracts

- `RAW_ATTACHMENT` is a distinct intake classification only; its presence never proves
  formal evidence semantics or gate readiness.
- Preserve the original nine `EvidenceRole` names, values and order, every other enum,
  all frozen dataclass shapes and the exact `__all__` order.
- The contract module remains stdlib-only and performs no database, filesystem, network,
  policy or gate operation.
- This task adds no endpoint and has no HTTP response or status-code behavior.

## Verification Commands

- Dependency gate: `./scripts/task_validate.sh FPMS-V8-DE-CONTRACTS-20260712-01`
- Registration-guard dependency gate: `./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- External-submission-guard dependency gate: `./scripts/task_validate.sh FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`
- RED: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py`
- GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py`
- Post-GREEN registration-guard regression, read-only and SQLite-serialized, using real `EvidenceRole.RAW_ATTACHMENT`: `cd backend && .venv/bin/pytest -q tests/test_v8_raw_attachment_registration_guard.py`
- Post-GREEN external-submission-guard regression, read-only and SQLite-serialized, using real `EvidenceRole.RAW_ATTACHMENT`: `cd backend && .venv/bin/pytest -q tests/test_v8_external_submission_role_allowlist.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py && .venv/bin/ruff format app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py && .venv/bin/ruff check app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py`
- Scoped diff: `git diff --check -- backend/app/modules/documents/evidence_contracts.py backend/tests/test_v8_document_evidence_contracts.py tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- Evidence gate (H3-3 single lane; no manifest or peer arguments): `python3 scripts/atomic_evidence_validate.py FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (pure enum interface extension; no endpoint).

## Evidence Path

- `artifacts/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` because execution starts
  from a dirty worktree.

## Done Definition

The accepted contracts dependency and its evidence remain unchanged; both direct guard
dependencies and their task/evidence gates are `PASS`; the exact tenth-member RED is
preserved; only the two allowlisted product/test lines needed for the additive role are
changed; the same targeted pytest is GREEN; both guard suites pass read-only and
SQLite-serialized with the real `EvidenceRole.RAW_ATTACHMENT`; task-scoped Ruff and diff
checks pass; dirty baseline and baseline-subtracted scope evidence prove no upload,
policy, gate or second closure changed; independent review, task gate and H3-3 single-lane
atomic evidence validation pass. Only then may this implementation task be reported PASS.
