# FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `50`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `436`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Existing generated-attachment service registers its evidence version in the same transaction, without changing template rendering behavior.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `backend/tests/test_document_generated_attachment_persist.py`: Exact read-only pre-V8 regression required by the approved dependency alias.
- `inherited` — `backend/tests/test_document_wizard_batch_create.py`: Exact read-only pre-V8 regression required by the approved dependency alias.
- `inherited` — `backend/tests/test_document_wizard_template_source_resolution.py`: Exact read-only pre-V8 regression required by the approved dependency alias.

- Approved source dependency cell (verbatim): attachment adapter; wizard/template regressions; serialized

### Shared ownership serialization

- `backend/app/modules/documents/service.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md`
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_v8_generated_attachment_evidence_adapter.py`
- `artifacts/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_generated_attachment_evidence_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_generated_attachment_evidence_adapter.py tests/test_document_generated_attachment_persist.py tests/test_document_wizard_batch_create.py tests/test_document_wizard_template_source_resolution.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_v8_generated_attachment_evidence_adapter.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_v8_generated_attachment_evidence_adapter.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_v8_generated_attachment_evidence_adapter.py`
- `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_v8_generated_attachment_evidence_adapter.py tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

- Latest-wins authority is
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
  at SHA-256
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`,
  especially lines 345–359 and the ownership rules at lines 844–848 and 888–903. Delta-4
  selects `chosen_runbook: P0-prereq-heavy-story`; the historical runbook line above is
  intentionally preserved byte-for-byte and is superseded only for this Delta-4 execution.
- Product TDD and implementation must not start until both
  `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` (`D4-06`) and
  `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` (`D4-07`) have
  independently accepted `PASS` evidence at the frozen authority hash. D4-06 owns the exact
  `GENERATED_ATTACHMENT` role and D4-07 owns its exact `DRAFT` registration row; this task
  must not recreate or broaden either contract.
- The documents API/wizard obtains the authenticated `current_user.id` server-side and
  propagates it to the generated-attachment service as the evidence creator. No body,
  attachment row, render context, default, constant or client-supplied value may choose or
  replace that actor.
- Each newly persisted generated output registers exactly one evidence version for the same
  case, document and attachment: role `GENERATED_ATTACHMENT`, state `DRAFT`, review state
  `PENDING`, creator equal to that server-owned actor, not `FINAL`, and with no external-
  submission marker or readiness inference. The evidence `content_hash` is exactly the
  `sha256:<64-lower-hex>` hash of the persisted generated attachment bytes and must equal the
  attachment's stored content hash; equal hashes do not make different evidence roles,
  attachments or template identities interchangeable.
- The lineage key is exactly
  `generated:<template-id>:<first-16-lower-hex-of-sha256(template-code)>:<attachment-id>`.
  Together with `Document.doc_template_id`, it must persist the resolved template ID and
  exact template-code identity. Missing, ambiguous, changed or mismatched template identity,
  hash, case/document/attachment relation, role or registration state fails closed; the
  adapter must never fall back to a different or latest template.
- Preserve the existing replay boundary: this task adds no client idempotency field and does
  not treat equal content bytes as authority to reuse another attachment or template.
  Within one generated output/attachment identity, registration occurs once; a duplicate or
  conflicting identity must not create another evidence version/activity or silently select
  alternate provenance and instead fails closed without partial durable state.
- The generated attachment, its evidence version and the version-registration activity are
  one atomic unit. Preserve the existing `commit` contract: a direct `commit=True` call may
  commit only after the whole unit succeeds, while the wizard's `commit=False` path only
  flushes and leaves the single outer batch commit/rollback to its caller. Any render,
  persistence, registration, flush or commit failure leaves no committed attachment,
  version, activity or orphan managed generated file.
- Task 50 retains separate ownership of `backend/app/modules/documents/service.py` at order
  key `2`. Its newly allowlisted `backend/app/modules/documents/api.py` edit is solely for
  server-owned actor propagation and is serialized in the exact shared-API order Task 50 →
  Task 51 (`FPMS-V8-DE-REVIEW-API-20260712-01`); the two tasks must never execute
  concurrently. No router, schema, permission, response, second entrypoint or
  `evidence_workflow_service.py` edit is authorized.
- No fake derivation may be created when no parent evidence version exists, and this task
  must not invent or resolve a parent merely to create one. Derivation, OA structured
  promotion (`D4-08`), review, current-version switching, external submission, template
  rendering output/order changes, and every second closure slice remain explicit
  non-closure.
- The existing task-owned RED, GREEN, inherited wizard/template regressions, scoped lint and
  scope checks, serialized SQLite verification, evidence path/artifact requirements,
  independent review, task gate and Done Definition remain unchanged. This Ultra
  materialization performs no product/test implementation, does not rerun RED/GREEN, and
  does not initialize or rewrite execution evidence.
