# Story V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY

- Risk: `PROTECTED`
- Outcome: when an obligation-linked official payment carries a verified official receipt,
  voucher, or invoice, mark only its official-evidence state verified and append one
  traceable fee-lane activity without duplicating the payment activity.
- Catalog ID:
  `FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01` (ordinal `125`).
- Base: `3c0ee20730c9ce6727639e8bdd9a1611f759853c`.
- Authority: `docs/product/v8/domain-contract.md`, frozen catalog row `125`, its exact task
  contract, and the already-current GovPayment activity adapter.

## Dependencies and observable contract

The sole catalog dependency,
`FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`, is current-verified by
`V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION` at commit
`4d85a56e9990107245c0f448e9d7ecb11c3fb5a3`.

For an obligation-linked payment:

- the existing payment activity and payment status update run exactly once;
- presence of any normalized `official_receipt_no`, `voucher_no`, or `invoice_no` changes
  `official_evidence_status` from `PENDING` to `VERIFIED`;
- the adapter appends one `OFFICIAL_PAYMENT_EVIDENCE_VERIFIED` activity with a stable
  idempotency key, the original obligation source activity, and exact receipt lineage;
- the case lifecycle projection and legal status are unchanged; and
- the existing entrypoint transaction behavior is preserved.

## Exact paths and tests

- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_official_payment_evidence_activity_adapter.py`
- `docs/product/v8/stories/V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY.md`

The focused test is byte-identical to archive ref
`6b2ef89da447353380b99853168d4d38aaf9210a` (Git blob
`fb44f59e80ee7d067e3920b14580b8ca274c7dc3`). On the clean story base it produced the
observable RED: `official_evidence_status` remained `PENDING`. After the minimum adapter
change, the focused test plus the inherited GovPayment activity regression produced
`2 passed`; scoped Ruff and exact diff-check passed.

## Non-goals and rollback

This story does not change the underlying payment-evidence rule, another entrypoint,
official-fee amount or reduction logic, PayList export, schema/migration, API/UI,
permissions, customer decisions, source activation, transaction ownership, or adjacent
annuity behavior. In particular it does not absorb catalog row `160` or any later export
story.

Rollback reverts the single story commit, restoring the prior adapter while leaving its
current dependency and all unrelated annuity behavior intact.
