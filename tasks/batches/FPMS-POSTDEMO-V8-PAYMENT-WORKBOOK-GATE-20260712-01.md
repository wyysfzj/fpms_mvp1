# FPMS Post-Demo V8 Payment-Workbook Capability Lane

Status: IMPLEMENTED / INDEPENDENT REVIEW REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Phase: `payment-workbook capability lane`
Runbook: `P0-prereq-heavy-story`

## Exact Lane Membership and Order

Task count: 11

- Task file: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01.md`

These are exactly the original activation row 175, product rows 214–222, and real UI E2E
row 278. No successor input-governance task is a lane member.

## Development Prerequisites

The original dependencies remain prerequisites: the catalog-manifest coverage gate and the
accepted PayList export-artifact carrier, artifact read, boundary FE adapter, and
internal/official boundary UI.

The following WB tasks are external successor prerequisites only and are never manifest
members:

- WB-I1: `FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01`
- WB-I2: `FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01`
- WB-I3: `FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01`

The frozen execution order is row 175 → WB-I1 → row 214 → WB-I2 → WB-I3 → rows 215–222
→ row 278. Accepted development with isolated `TEST_ONLY` input may establish
`CAPABILITY_READY`; it does not establish `PRODUCTION_INPUT_ACTIVE` or production
activation.

## Production Gate and Fail-Closed Boundary

The original production gate remains `DG-PAYMENT-WORKBOOK:GLOBAL`. Production use requires
a real, current, reviewed `.xlsm` workbook and its source-backed activation record. When
that production input is absent, invalid, unreviewed, expired, revoked, or scope-mismatched,
the lane remains `CONFIG_REQUIRED` and returns `409 / NO WRITE`. This does not block
development or `CAPABILITY_READY` acceptance.

Generation, official-site acceptance evidence, payment, and ticket verification remain
four distinct facts. No manifest acceptance implies any of them, changes legal state, or
fulfills a route.

## Acceptance Boundary

Independent High review must approve the exact 11-member manifest, external-prerequisite
classification, preserved production gate, focused contract test, and zero
product/schema/catalog/ledger scope before product-row execution. This manifest does not
self-approve its activation or any member task.
