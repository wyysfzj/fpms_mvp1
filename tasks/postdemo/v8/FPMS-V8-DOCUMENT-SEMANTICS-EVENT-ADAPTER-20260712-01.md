# FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `61`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `447`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Resolver emits `lifecycle_event_type`; document create stops direct `Case.status` writes and dispatches supported non-grant semantics exactly once. For `GRANT_NOTICE`, it passes the frozen resolved semantics/source to the grant adapter and appends no lifecycle event itself.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

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

### External, gate and inherited prerequisites

- `inherited` — `Task02:FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_create_atomicity.py.
- `inherited` — `Task03:FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_semantics.py.
- `inherited` — `Task04:FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_semantic_state_effect.py.
- `inherited` — `Task33:FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_oa_acceptance_activation.py.
- `inherited` — `Task34:FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_alias_reply_validation.py.
- `inherited` — `Task38:FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_grant_activation.py.

- Approved source dependency cell (verbatim): event rules; Tasks02–04/33–34/38 regressions

### Shared ownership serialization

- `backend/app/modules/documents/semantics.py` order key `1`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/service.py` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01.md`
- `backend/app/modules/documents/semantics.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_v8_document_semantics_event_adapter.py`
- `artifacts/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_semantics_event_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_semantics_event_adapter.py tests/test_addgap_document_create_atomicity.py tests/test_addgap_document_semantics.py tests/test_addgap_document_semantic_state_effect.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_oa_alias_reply_validation.py tests/test_addgap_notice_grant_activation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py app/modules/documents/service.py tests/test_v8_document_semantics_event_adapter.py && .venv/bin/ruff format app/modules/documents/semantics.py app/modules/documents/service.py tests/test_v8_document_semantics_event_adapter.py && .venv/bin/ruff check app/modules/documents/semantics.py app/modules/documents/service.py tests/test_v8_document_semantics_event_adapter.py`
- `git diff --check -- backend/app/modules/documents/semantics.py backend/app/modules/documents/service.py backend/tests/test_v8_document_semantics_event_adapter.py tasks/postdemo/v8/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
