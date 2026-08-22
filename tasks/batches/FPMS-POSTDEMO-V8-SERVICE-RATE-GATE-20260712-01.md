# FPMS Post-Demo V8 Service-Rate Capability Lane

Status: IMPLEMENTED / INDEPENDENT REVIEW REQUIRED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Phase: `service-rate capability lane`
Runbook: `P0-prereq-heavy-story`

## Exact Lane Membership and Order

Task count: 8

- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md`
- Task file: `tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01.md`

These are exactly the original activation row 176 and product rows 223–229.
No external successor is a lane member.

## Development Prerequisites

The original dependencies remain prerequisites: the catalog-manifest coverage gate, accepted
PayList export-artifact carrier, decision-gate read service, and serialized global Alembic
predecessor.

External successors remain prerequisite authority only and are never manifest members. Accepted
development with isolated `TEST_ONLY` input may establish `CAPABILITY_READY`; it does not
establish `PRODUCTION_INPUT_ACTIVE` or production activation.

## Production Gate and Fail-Closed Boundary

The original production gate remains `DG-SERVICE-RATE-VERSION:GLOBAL`. Production use requires a
complete, current, reviewed, source-backed real service-rate version. When that production input
is absent, invalid, unreviewed, expired, revoked, or scope-mismatched, the lane remains
`CONFIG_REQUIRED` and returns `409 / NO WRITE`. This does not block development or
`CAPABILITY_READY` acceptance.

Service receivables remain separate from official-fee obligations. Manifest acceptance does not
activate a price book, create a receivable, change legal state, or imply production activation.

## Execution and Acceptance Boundary

After independent activation acceptance, execute the carrier, import service, import API,
activation service, activation API, receivable service, and receivable API in the listed
dependency order. Shared fee model, service, schema, and API files and all SQLite-writing checks
remain serialized.

Independent High review must approve the exact eight-member manifest, external-prerequisite
classification, preserved production gate, focused contract test, dependencies, and zero
product/schema/catalog/ledger scope before product-row execution. This manifest does not
self-approve its activation or any member task.
