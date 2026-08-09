# Story V8-PAYLIST-REAL-ROUTE-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: expose the accepted PayList creation and internal-export services through the
  existing authenticated HTTP routes, then prove on the real UI path that internal export,
  official workbook evidence and payment remain separate facts.
- Superseded catalog ID: `FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01`
  (ordinal `277`).
- Successor contract:
  `docs/product/v8/stories/V8-PAYLIST-REAL-ROUTE-ADAPTER-CONTRACT.md`.
- Product commit: `3c2abea7ae2780e54f3af82611cf70ec90b63fc8`.

## Observable contract

The existing PayList creation route supplies the authenticated actor, invokes the accepted
service once and owns the commit/rollback boundary, so its returned PayList identity is
immediately durable. The existing bodyless export route preserves permission, binary
response, media type, filename, missing `404` and non-draft `409` semantics while calling
only the accepted internal-export service with the deterministic PayList-scoped retry key.

A successful internal export creates or reuses the exact `INTERNAL_XLSX` artifact and
activity, commits before returning bytes and leaves the PayList header `DRAFT`. Service
failure rolls back; commit failure additionally compensates only a fresh managed file and
never removes a replayed durable file. The route never creates or infers an official
workbook, official acceptance evidence, payment, receipt, fee instruction or legal status.

The live Chromium path creates a real obligation-linked government-fee draft and PayList,
uses the real PayList detail page and export action, then proves the persisted internal
artifact/hash while official workbook/evidence remain absent and the payment rows remain
unchanged.

## Verification and review

The first missing-file RED reported no matching live E2E. The real path then exposed two
adapter failures: creation returned an uncommitted identity and export still called the
legacy status-changing service. The focused route RED produced `10 failed`; the minimum
three-file implementation made all `10` pass.

Fresh verification passed the focused adapter plus accepted PayList rows 157 and 159–164
tranche (`38` tests), scoped Ruff and format checks, the existing static boundary UI tests
(`2` tests) and the exact live Chromium E2E (`1` test). An additional inherited annuity E2E
probe stopped before the PayList behavior because its shared case fixture omits the now
mandatory `fee_reduction` field; it was recorded as an unrelated old-baseline mismatch and
was not absorbed into this story.

Independent High review of the exact three-file product commit reran the decisive backend
and live browser checks, inspected permission, transaction, compensation, replay and the
internal/official/payment separation, and approved it with `P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

No service-rule or schema/migration change, official workbook generation/upload, payment
registration, receipt fabrication, PayList header redesign, request/header addition, UI
redesign, legacy fixture cleanup or adjacent refactor is included. Rollback reverts only
the exact product commit and this adoption record while retaining all accepted deep
services.
