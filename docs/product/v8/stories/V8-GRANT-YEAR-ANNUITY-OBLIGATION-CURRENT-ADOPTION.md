# Story V8-GRANT-YEAR-ANNUITY-OBLIGATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: recognize or correct only the grant-year annuity lines frozen on one confirmed
  grant-registration-notice lifecycle activity.
- Catalog ID: `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01` (ordinal `130`).
- Product commits: `ff0b5d5c2ce6c32c76f04be4915c1297279085f1`,
  `8cb0f37e0ecb8fb785d9e781e818fde49744135a`, and
  `69032f394fa6da0fad12efee22671a5c71022176`.

## Observable contract

The typed adapter accepts only a grant-fee task and its exact confirmed
`GRANT_REGISTRATION_NOTICE_RECORDED` activity. It revalidates the activity payload,
canonical Row74 snapshot/hash, source document, reviewed evidence version and evidence
links, then maps every and only every frozen annual-fee line to the category-specific INV,
UM or DES fee code.

The adapter never rereads mutable document metadata, OCR/PDF bytes, task amount or a rate
book, and never infers another fee, year, reduction or full amount. It delegates exactly
once to generic fee-obligation recognition, which owns the sole FEE activity and all
writes. Caller transaction, error and replay semantics remain unchanged.

For a correction, the current activity/task pair must name one unique direct predecessor.
The predecessor task, activity, source document, evidence, obligation header and complete
line projection are all rebound to the immutable prior snapshot. Exact historical replay
and recovery remain supported; partial, ambiguous, indirect, divergent or drifted lineage
fails closed without a write.

## Verification and review

The real RED produced `3 failed, 1 passed` on the missing adapter. The initial product
implementation reached `30 passed` focused and `172 passed` in the nearest dependency
tranche. Independent review exposed predecessor evidence validation, historical replay,
canonical amount and overlapping-invalidity gaps. The first correction raised focused
coverage to `44 passed` and the dependency tranche to `186 passed`.

A second independent review found two remaining exact gaps: leading-zero amount bytes that
Row74 can never produce and predecessor obligation header/line drift. Commit `69032f3`
closed both. Final focused verification passed `49` tests; the four-file fee-line snapshot,
grant lifecycle, obligation recognition and adapter tranche passed `191` tests. Scoped
Ruff, format and diff checks passed, and final independent High review approved
`P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

No rate-book calculation, fee-reduction decision, draft, PayList, payment, instruction,
schema/migration, API/UI, second entrypoint or deep fee-obligation rule change is included.
Rollback reverts only the three product commits and this adoption record; the accepted
Row74 snapshot, grant lifecycle and generic recognition prerequisites remain intact.
