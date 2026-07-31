# Story V8-FEE-REDUCTION-APPROVAL-NOTICE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `bfcd7fa`
- Outcome: a reviewed confirmed fee-reduction approval notice records or reuses scoped
  approval evidence while reference-only or unknown notices remain inert.
- Catalog ID: `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
  (ordinal `127`, profile `TC-ADAPTER`).
- Authority: frozen catalog row `127`, its exact task contract, the current-verified
  approval-record service and application-fee notice story, and
  `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/app/modules/documents/semantics.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_v8_fee_reduction_approval_notice_adapter.py`

Shared document fee-linking ownership follows accepted row126. This lane shares no path
with the batch-filing story; SQLite and any Playwright verification remain serialized.

## Observable contract

The resolver freezes `FEE_REDUCTION_APPROVAL_NOTICE`. Only exact reviewed, confirmed notice
and evidence authority records or reuses the scoped approval. Reference-only or unknown
notices do nothing. The adapter does not activate the catalog row, create an obligation or
draft, or change lifecycle state.

## TDD and verification

The focused RED failed `4/4` on missing executable semantic and adapter. The minimum
current-tree-compatible resolver/adapter produced focused GREEN `4/4`; scoped
Ruff/compile/diff checks passed. Independent High review approved P0/P1/P2 all zero and
successor-attested the row126 application-fee and special-fee handlers.

## Non-goals and rollback

No activation, obligation/draft, second entrypoint, deep approval-rule change, endpoint,
UI, schema, migration, old task/evidence mutation or adjacent cleanup. Rollback reverts
only product commit `b61069d` and this story mapping.
