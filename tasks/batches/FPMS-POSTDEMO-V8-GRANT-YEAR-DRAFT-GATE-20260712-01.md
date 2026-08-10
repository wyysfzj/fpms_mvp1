# FPMS Post-Demo V8 Grant-Year Draft Gate

Status: IMPLEMENTED / INDEPENDENT REVIEW REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Phase: `deferred customer-decision lane activation`
Runbook: `P0-prereq-heavy-story`

## Frozen Decision Authority

- Gate: `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`
- Decision status: `APPROVED_POLICY`
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`
- Exact customer source:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- Current decision registry: `docs/product/v8/source-decision-registry.md`
- Source publication commit: `e5a41c8d07f11d1b0dec68891ef7bef53312f883`
- Current-owner acceptance commit: `72877386974cd57c720b7c622e6b00ca49c03d7d`

## Prerequisite Proof

- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`: historical task card is
  `PASS`; the active Git-native coverage ledger records its current successor story.
- `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`: active coverage disposition is
  `CURRENT_VERIFIED`.
- `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`: active coverage disposition is
  `CURRENT_VERIFIED`.

## Exact Lane Membership and Order

Task count: 2

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-DRAFT-MANIFEST-ACTIVATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-AUTO-DRAFT-POLICY-20260712-01.md`

The activation task is the only current implementation item. The child task remains
unstarted until the activation has current independent acceptance; it then executes as the
only grant-year auto-draft child in this lane.

## Frozen Runtime Boundary

- Real grant-year notice review required: yes
- Internal pending-review draft count after notice review: exactly one
- Actual payment requires client instruction: yes
- Child execution requires independently accepted activation: yes
- Product, schema, catalog and coverage-ledger changes: forbidden

This activation does not create a draft, perform payment, change legal status, select an
official-fee amount, or authorize any additional customer-decision lane. The child task must
preserve the reviewed notice as the source of year, amount and deadline truth and must retain
the separate client-instruction gate for actual payment.

## Acceptance Boundary

Independent High review must approve this exact two-member manifest, the accepted decision
binding, prerequisite proof, baseline-subtracted patch, and zero product/schema/catalog/ledger
scope before the child task may start. This manifest does not self-approve the activation or
the child implementation.
