# Story V8-GENERIC-FEE-DRAFT-OBLIGATION-API-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `0a857f4`
- Outcome: let the existing fee-draft POST accept and pass one optional obligation
  identity while preserving exact linkage, permission, status and atomicity semantics.
- Catalog ID: `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`
  (ordinal `116`, profile `TC-API`).
- Authority: frozen catalog row `116`, its exact task contract, the current-verified
  generic-draft activity adapter, and the fee/API rules in
  `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/fees/schemas.py`
- `backend/app/modules/fees/api.py`
- `backend/tests/test_v8_generic_fee_draft_obligation_api.py`

The dependency is current-verified. This lane shares no product/test path with the active
legacy fee-truth importer; SQLite verification remains serialized.

## Observable contract

The existing FeeDraft POST accepts one optional `obligation_id` and passes it unchanged to
the accepted service adapter. A missing, non-actionable or mismatched linkage returns the
frozen `409` outcome with no partial draft. Existing 200/201/400/401/403/404/409/422,
response-envelope, permission, transaction and activity identity semantics remain intact.

## TDD and verification

The focused RED produced `7` exact behavior failures and retained `2` passing permission
checks. The minimum three-path implementation produced focused GREEN `9/9`; scoped
Ruff/diff checks passed. Independent High review approved the exact candidate with
P0/P1/P2 all zero and successor-attested the three current stories sharing the fee API or
schema paths.

## Non-goals and rollback

No second endpoint, router rewiring, business-rule duplication, service-rule change,
frontend work, old task/evidence mutation or adjacent cleanup. Rollback reverts only
product commit `d494e95` and this story mapping.
