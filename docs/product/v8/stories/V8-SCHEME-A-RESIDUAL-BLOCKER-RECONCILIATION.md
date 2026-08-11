# Story V8-SCHEME-A-RESIDUAL-BLOCKER-RECONCILIATION

- Risk: `PROTECTED`.
- Outcome: replace the obsolete pre-decision blocker reason on the 20 remaining Full/Final rows
  with the exact external prerequisites retained by approved Scheme A.
- Authority: `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`, SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.

## Exact reconciliation

The customer decision now exists, so `CUSTOMER_DECISION_REQUIRED` is no longer an accurate
blocker code for these rows. Their disposition remains `CUSTOMER_BLOCKED`, but the blocker becomes
`EXTERNAL_PREREQUISITE_REQUIRED`:

- `DG-PAYMENT-WORKBOOK:GLOBAL`: rows 175, 214–222 and 278 require both a clean current workbook
  and controlled-upload proof before activation.
- `DG-SERVICE-RATE-VERSION:GLOBAL`: rows 176 and 223–229 require an approved complete price
  version before activation.
- Full-manifest row 199 remains blocked by both exact identities because its frozen contract
  requires all seven GLOBAL resolutions. It does not bypass, synthesize or weaken either gate.

Rows 281–283 remain `PENDING` under their already accepted exact dependency contract. Their root
dependency continues to be Full activation, with row 278 and row 281 ordering retained where
applicable.

## Exact paths and verification

- `docs/product/v8/coverage-ledger.json`;
- `docs/product/v8/stories/V8-SCHEME-A-RESIDUAL-BLOCKER-RECONCILIATION.md`.

Verification must prove exactly 11 payment-workbook rows, eight service-rate rows and one combined
Full-manifest row receive the new precise blocker; no disposition, story binding or other row
changes; JSON/schema/inventory/Foundation checks remain PASS; and independent High review approves
the exact two-path commit.

## Non-goals and rollback

No gate confirmation or activation, no workbook/rate invention, no product task execution, no
Full/Final/Release claim, no frozen catalog/source-registry/product/schema/test change. Rollback
restores only the superseded blocker metadata and this story card.
