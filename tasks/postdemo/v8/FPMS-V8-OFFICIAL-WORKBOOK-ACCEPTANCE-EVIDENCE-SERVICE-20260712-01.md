# FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `219`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `727`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-PAYMENT-WORKBOOK[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Record one same-PayList official-site acceptance proof against the persisted generated official artifact; acceptance changes neither payment nor ticket state and appends its own FEE activity.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-PAYMENT-WORKBOOK:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): generation service, payment-workbook gate

### Shared ownership serialization

- `backend/app/modules/annuity/service.py` order key `12`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_official_workbook_acceptance_service.py`
- `artifacts/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_official_workbook_acceptance_service.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_official_workbook_acceptance_service.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_official_workbook_acceptance_service.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_official_workbook_acceptance_service.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_official_workbook_acceptance_service.py`
- `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_official_workbook_acceptance_service.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01` pass. Only then may this task be reported PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

## Executable Contract Freeze — 2026-08-13

- Command DTO: `RecordOfficialWorkbookAcceptanceCommand`, keyword-only, with exact fields
  `pay_list_id:int`, `artifact_id:str`, `evidence_ref:str`, `evidence_sha256:str`,
  `accepted_at:datetime`, `actor_id:str`, `idempotency_key:str`, and
  `runtime_profile:"test"|"production"`.
- Result DTO: `OfficialWorkbookAcceptanceResult` with the same carrier identity and accepted
  tuple, one `activity_id`, `status="OFFICIAL_SITE_ACCEPTED"`, `accepted=True`,
  `paid=False`, `ticket_verified=False`, and `disposition="CREATED"|"REUSED"`.
- The target must be the command's same-PayList persisted `OFFICIAL_XLSM` artifact. New
  acceptance requires `GENERATED` plus a wholly empty acceptance tuple; replay requires the
  exact persisted ref/hash/time tuple. Any other kind, status, tuple or payload is 409.
- Exactly one GovPayment case must belong to that PayList. Acceptance updates only the artifact
  status/ref/hash/time/`updated_at`; it does not change PayList or GovPayment state and never
  commits or rolls back the caller-owned transaction.
- Append/replay exactly one FEE activity `OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED` with idempotency
  `official-workbook-acceptance:{artifact_id}:{idempotency_key}:{case_id}`. Its evidence is
  `OFFICIAL_SITE_ACCEPTANCE_PROOF` / `PayListExportArtifact` / the same artifact ID / submitted
  hash / acceptance time; its payload binds artifact, PayList, proof ref/hash, accepted time and
  the four distinct facts `generated_status=GENERATED`, `accepted=true`, `paid=false`,
  `ticket_verified=false`.
- `production` resolves the current exact `DG-PAYMENT-WORKBOOK:GLOBAL` gate as of
  `accepted_at` and requires resolved scope `GLOBAL` plus source version equal to the artifact
  template version; missing/revoked/future/mismatched input is 409/no write. `test` is the
  isolated `TEST_ONLY` development path and does not resolve a production gate.
- Validation is fail-fast 400; missing PayList/artifact is 404; same-key/payload, artifact,
  activity, lineage, case multiplicity or concurrent-write conflicts are 409.

## Independent Review Amendment — 2026-08-13

- Before any read, establish the SQLite outer transaction. Lock the exact artifact row with
  `SELECT ... FOR UPDATE` on non-SQLite databases; SQLite uses an exact conditional update.
- Resolve the exact effective `OfficialPaymentWorkbookInputVersion` for `accepted_at` and the
  requested runtime profile. The persisted generation activity/evidence is the artifact's
  durable input-lineage carrier and must bind the same artifact/PayList/content/path,
  `workbook_input_version_id`, template version and template content hash.
- Production additionally requires the exact current `DG-PAYMENT-WORKBOOK:GLOBAL` result:
  requested and resolved scope `GLOBAL`, source reference equal to the resolved controlled-upload
  proof path, source version equal to its template version, and decision value equal to the
  canonical input gate snapshot. Any mismatch is 409/no write.
- Test execution resolves one effective approved `TEST_ONLY` input and requires the generated
  artifact lineage to bind that exact test-only version and hashes. Switching a production or
  unclassified artifact to `runtime_profile="test"` is 409/no write.
- A new acceptance performs one exact `GENERATED` plus empty-tuple to
  `OFFICIAL_SITE_ACCEPTED` conditional update and appends the activity in one nested unit. Zero or
  multiple affected rows, database lock/race, activity collision or integrity failure is the
  contracted 409. Caller-owned commit/rollback semantics remain unchanged.
