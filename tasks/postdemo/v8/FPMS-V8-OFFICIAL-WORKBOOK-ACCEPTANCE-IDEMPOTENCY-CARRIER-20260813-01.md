# FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-IDEMPOTENCY-CARRIER-20260813-01

Status: CURRENT_VERIFIED_NOT_ADOPTED
Risk: PROTECTED — lifecycle/evidence idempotency
Catalog rows: successor support for 219, 220, 221, 222 and 278; no new catalog row

## Observable outcome

A canonical 36-character request UUID accepted by the HTTP/TypeScript contracts can record and
replay an official-workbook acceptance. Its internal lifecycle key fits the 128-character carrier
without truncating or weakening the exact artifact/request/case identity.

## Exact closure

- Derive the internal activity idempotency key as a domain prefix plus lowercase SHA-256 over the
  NUL-delimited exact `(artifact_id, request idempotency_key, case_id)` tuple.
- Preserve the original request key in the public result and all existing replay/conflict, lineage,
  transaction, payment and ticket behavior.
- Prove the production integration path with a canonical UUID and exact stable internal key.

## Non-goals

No external API/body/type, uniqueness scope, event type, payload, evidence, permission, gate,
acceptance meaning, payment, ticket, schema, migration or UI change.

## Allowed paths

- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_official_workbook_acceptance_service.py`
- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-IDEMPOTENCY-CARRIER-20260813-01.md`

## Verification

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_official_workbook_acceptance_service.py`
- Scoped lint: `cd backend && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_official_workbook_acceptance_service.py`
- Scope: `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_official_workbook_acceptance_service.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-IDEMPOTENCY-CARRIER-20260813-01.md`

## Rollback boundary

Revert the exact successor commit; short test keys remain usable, while canonical browser UUIDs
again fail before acceptance writes.
