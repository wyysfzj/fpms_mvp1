# FPMS Post-Demo V8 Future-Annuity Gate

Status: ACTIVATION CANDIDATE / INDEPENDENT REVIEW REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Phase: `deferred customer-decision lane activation`
Runbook: `P0-prereq-heavy-story`

## Frozen Decision Authority

- Gate: `DG-FEE-FUTURE-ANNUITY:GLOBAL`
- Decision status: `APPROVED_POLICY`
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`
- Exact customer source:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- Decision source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`
- Current decision registry: `docs/product/v8/source-decision-registry.md`
- Source publication commit: `e5a41c8d07f11d1b0dec68891ef7bef53312f883`
- Current-owner acceptance commit: `72877386974cd57c720b7c622e6b00ca49c03d7d`

## Prerequisite Proof

- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`: historical task card is
  `PASS`; the active Git-native coverage ledger records its current successor story.
- `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`: active coverage disposition is
  `CURRENT_VERIFIED`.
- `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`: active coverage disposition is
  `CURRENT_VERIFIED`.

## Exact Lane Membership and Order

Task count: 2

- Task file: `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-MANIFEST-ACTIVATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-20260712-01.md`

The activation task is the only current implementation item. The child task remains
unstarted until the activation has current independent acceptance; it then executes as the
only future-annuity auto-draft child in this lane.

## Frozen Runtime Boundary

- Client instruction required before draft: yes
- Initial exception set: empty
- Later exception scope: authorized, audited customer or case
- Later exception interval: explicit start and end
- Child execution requires independently accepted activation: yes
- Product, schema, catalog and coverage-ledger changes: forbidden

This activation creates no draft, payment, legal-status change, fee selection or exception.
The child task must preserve client instruction as the default prerequisite to draft creation.
A later exception remains unavailable unless an institution administrator separately publishes
an authorized customer- or case-scoped configuration with explicit start and end, and the
publication and later use retain an audit record.

## Acceptance Boundary

Independent High review must approve this exact two-member manifest, the accepted decision
binding, prerequisite proof, baseline-subtracted patch, and zero product/schema/catalog/ledger
scope before the child task may start. This manifest does not self-approve the activation or
the child implementation.
