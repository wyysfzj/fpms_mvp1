# FPMS V8 Inherited Filing Preparation Test Alignment

Status: `READY`
Risk: `PROTECTED`
Runbook: `P0-single-lane-story`

## Observable outcome

Align the two inherited filing-preparation tests with the current reviewed lifecycle adapter:
every resolve supplies an explicit actor, starts from the exact confirmed NEW_CASE lifecycle
projection, records immutable package evidence once, and fails closed on write collision.

## Authority

- `docs/product/v8/domain-contract.md`
- `docs/product/v8/stories/V8-FILING-PREPARATION-STARTED-ADAPTER-CURRENT-ADOPTION.md`
- `backend/tests/test_v8_filing_preparation_started_adapter.py`

## Exact closure

- Update the inherited direct-service helper to supply one stable explicit test actor.
- Seed its cases with the exact pre-event lifecycle projection required by the reviewed
  `FILING_PREPARATION_STARTED` rule.
- Bind API fixtures to the same exact lifecycle projection.
- Preserve package identity, checklist, manifest, archived reuse, missing case and invalid-state
  assertions.
- Align the obsolete unique-collision reread expectation to the reviewed fail-closed `409`
  identity-conflict contract; no service rollback or implicit winner adoption.

## Non-closure

- No product, schema, migration, seed, API, lifecycle rule or transaction change.
- No anonymous/default actor and no fixture bypass of lifecycle validation.
- No test skip/xfail or removal of identity/collision coverage.
- No changes to OA reply, notice seed, case-create input or Row281 files.
- No Row281 adoption, Row282, Row283 or release close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-FILING-PREPARATION-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_addgap_filing_ensure_service.py`
- `backend/tests/test_addgap_filing_resolve_api.py`

## Verification and acceptance

The recorded Row281 RED is eight direct-service `actor_id` errors plus one API `409`
`LIFECYCLE_RULE_DECISION_INVALID`. Final verification runs both inherited files together with
`test_v8_filing_preparation_started_adapter.py`, scoped Ruff, exact diff and independent High
review with P0/P1/P2 `0/0/0`.

Rollback reverts only this task card and the inherited test-contract inputs/expectations; it never
changes product behavior or business data.
