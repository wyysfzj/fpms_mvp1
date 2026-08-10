# FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01

Status: CONTRACT FROZEN / PRODUCT NOT STARTED / ACTIVATION REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Backend Developer / worker
Repository risk: HIGH

## Authority and dependencies

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/domain-safety.md`
- `docs/agents/source-authority.md`
- `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md`
- `FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01` terminal HIGH PASS

Customer authority remains exactly `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`, Scheme A version
`customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`, source SHA-256
`e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
This API configures reviewed CNIPA source records; it never supplies a default or proves grant.

## Task Contract Profile

Task Contract Profile: `TC-API`

- RED: exact route tests fail because the six source/configuration mutation endpoints and schemas
  are absent.
- GREEN: the six endpoints delegate once to the accepted service, inject the authenticated actor
  and one server time, preserve status/envelope/permission semantics, and commit or roll back once.

## Exact Closure Slice

Add exactly six authenticated JSON `POST` endpoints under the existing system router:

1. `/system/grant-evidence-sources` — register; `201` for `CREATED`, `200` for `REUSED`.
2. `/system/grant-evidence-sources/{source_record_id}/review` — approve/reject; `200`.
3. `/system/grant-evidence-sources/{source_record_id}/activate` — activate with expected-current
   CAS; `200`.
4. `/system/grant-evidence-sources/{source_record_id}/retire` — one-shot explicit retire; `200`.
5. `/system/grant-evidence-source-configurations` — publish active `GLOBAL` selection; `201` for
   `CREATED`, `200` for `REUSED`.
6. `/system/grant-evidence-source-configurations/{config_id}/revoke` — append the exact revoked
   successor using expected-current CAS; `201` for `CREATED`, `200` for `REUSED`.

All require `SystemParam.Edit`; no new permission or role is invented. Every actor field comes
only from `current_user.id`. The route captures one UTC-naive `now` after authentication and input
validation and supplies it as `reviewed_at`, `activated_at`, `retired_at` or `published_at`.
Clients cannot submit actor IDs or audit timestamps.

## Frozen request and response boundary

Create `backend/app/modules/system/grant_evidence_source_schemas.py` with strict Pydantic request
and response models. Unknown fields are forbidden. Enum values use the accepted service enums;
raw lookalikes are rejected by validation rather than coerced in the service.

- `RegisterGrantEvidenceSourceIn`: `source_code`, `source_version`, `evidence_scope`,
  `source_reference_kind`, `source_reference_value`, `acquisition_method`, `effective_from`,
  `effective_to`, `supersedes_source_id`, `idempotency_key`.
- `ReviewGrantEvidenceSourceIn`: `decision`, `reason`.
- `ActivateGrantEvidenceSourceIn`: `expected_current_source_id` only. This is the predecessor/CAS
  input; it is not compared with the target path ID.
- `RetireGrantEvidenceSourceIn`: `expected_current_source_id` only. The route requires it to equal
  the `source_record_id` path target before service invocation.
- `PublishGrantEvidenceSourceConfigIn`: `evidence_scope`, `source_record_id`, `config_version`,
  `effective_from`, `effective_to`, `selection_reason`, `expected_current_config_id`,
  `idempotency_key`.
- `RevokeGrantEvidenceSourceConfigIn`: `evidence_scope`, `config_version`, `effective_from`,
  `selection_reason`, `expected_current_config_id`, `idempotency_key`. The route requires
  `expected_current_config_id == config_id` from the path because the accepted service command has
  no separate target-config field.
- `GrantEvidenceSourceRecordOut` exposes exactly the accepted result fields:
  `source_record_id`, `review_status`, `activation_status`, `source_snapshot_hash`,
  `current_identity_key`, `disposition`.
- `GrantEvidenceSourceConfigOut` exposes exactly the accepted result fields: `config_id`,
  `config_status`, `config_snapshot_hash`, `current_identity_key`, `disposition`.

Review and activate path IDs map directly to `command.source_record_id`. Register/publish bodies
map field-for-field while actor and audit time are injected. Retire and revoke apply the exact
path/body equality guards above. No response adds version, interval or audit fields absent from the
accepted service result DTOs.

The API does not recompute canonical snapshots/hashes, inspect ORM state, resolve source authority,
or duplicate service rules. It constructs the exact accepted command and invokes exactly one
service callable.

## HTTP, transaction and error contract

- Missing/invalid bearer authentication: existing `401` envelope.
- Authenticated user without `SystemParam.Edit`: existing `403` envelope.
- The two exact retire/revoke path/body identity mismatches, malformed UUID/string/enum/interval
  shape: `422`, with no service call.
- Missing source/config/user, unusable/illegal targets, stale expected-current, replay mismatch,
  duplicate/current/scope/hash/status/reviewer conflicts preserve the accepted service
  `409 GRANT_EVIDENCE_SOURCE_CONFLICT` code/detail and perform zero durable write.
- Successful request calls `db.commit()` exactly once after the service returns, then returns the
  service result. A raised error calls `db.rollback()` exactly once and preserves the error.
- No endpoint calls `flush()` before the service, reads a clock twice, retries a conflict,
  substitutes a user, or converts a failure to success.

## Non-weakenable invariants

- No concrete CNIPA URL, dataset, file, version, channel or actor is seeded or defaulted.
- Proposer/reviewer separation and source review/activation/config effectiveness remain enforced
  by the accepted service and schema; the API never bypasses them.
- Missing/unreviewed/inactive/future/expired/revoked/ambiguous authority stays fail-closed.
- No document/candidate ingestion, legal-state confirmation, lifecycle event, fee/payment fact,
  role binding, or source resolution endpoint is added.
- Existing FastAPI envelope, dependency injection, permission and SQLite behavior are preserved.

## Explicit Non-Closure

No GET/list/search endpoint; no UI; no seed/backfill; no new permission or default Admin binding;
no `DG-GRANT-MANUAL-REVIEW` role configuration; no ingestion/read/review candidate endpoint; no
generic decision-gate change; no migration/model/service change; no production source selection;
no coverage-ledger, customer-source or release edit.

## Remaining Follow-Up Task IDs

- `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01` consumes the accepted resolver and
  candidate carrier after its dependency/allowlist is explicitly re-frozen.
- `FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01` remains the separate role-binding
  closure required before manual review or legal-state confirmation.

## Shared ownership and serialization

- `backend/app/modules/system/api.py`: exclusive API owner for this task.
- `backend/app/modules/system/grant_evidence_source_schemas.py`: exclusive schema owner.
- Focused API tests that write SQLite run through the global serialized queue.
- The source service must already be independently accepted; implementer cannot approve this task.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md`
- `backend/app/modules/system/grant_evidence_source_schemas.py`
- `backend/app/modules/system/api.py`
- `backend/tests/test_v8_grant_evidence_source_api.py`
- `artifacts/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01/**`

All other source, schema, task, manifest, model, service, router and test paths are read-only.
Preserve and subtract the complete dirty baseline.

## RED / GREEN acceptance matrix

1. Each route has one success test proving exact command mapping, authenticated actor injection,
   one captured timestamp, response status/body and one commit.
2. Registration and config publication/revocation distinguish `CREATED` (`201`) from exact
   `REUSED` (`200`) without a second write.
3. `401`, `403` and `422` tests prove zero service call/commit/rollback before a transaction exists.
4. Every accepted service `409 GRANT_EVIDENCE_SOURCE_CONFLICT` family preserves code/detail,
   calls rollback once and commits zero times; the API invents no `404` conversion.
5. Body actor/timestamp/unknown fields, exact retire/revoke path/body identity mismatch, blank
   reason/key/version, invalid enum and invalid interval fail validation. Activate proves a
   predecessor ID different from the target path is passed through rather than rejected.
6. Changed idempotency payload, changed expected-current and cross-scope IDs cannot be normalized
   into replay.
7. The API neither queries carrier ORM tables nor calls the resolver, ingestion or legal-state
   services; monkeypatch sentinels prove single delegation.
8. Existing system parameter and decision-gate route regressions remain green and unchanged.

## Verification Commands

- RED: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_api.py`
- GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_api.py`
- Scoped regression: `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_record_api.py tests/test_system_config_readiness_api.py`
- Lint: `cd backend && .venv/bin/ruff check --fix app/modules/system/grant_evidence_source_schemas.py app/modules/system/api.py tests/test_v8_grant_evidence_source_api.py && .venv/bin/ruff format app/modules/system/grant_evidence_source_schemas.py app/modules/system/api.py tests/test_v8_grant_evidence_source_api.py && .venv/bin/ruff check app/modules/system/grant_evidence_source_schemas.py app/modules/system/api.py tests/test_v8_grant_evidence_source_api.py`
- Scope: `git diff --check -- backend/app/modules/system/grant_evidence_source_schemas.py backend/app/modules/system/api.py backend/tests/test_v8_grant_evidence_source_api.py tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01`
- Atomic evidence: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01/**`
- Required: `results.jsonl`, `summary.md`, `git/diff.patch`, dirty-baseline artifacts, current
  dependency hashes, independent review and zero-RC task/atomic gates.

## Done Definition

The exact RED is preserved; only the six endpoints/schemas/tests are added; focused and inherited
regressions, scoped Ruff/diff and dirty-baseline checks pass; service/permission/envelope/transaction
semantics remain exact; one independent High reviewer approves zero findings; task and atomic
evidence gates pass. Only then may this task be reported PASS.
