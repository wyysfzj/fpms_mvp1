# Story V8-FORMAT-LETTER-ARCHIVE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: archive one rendered format-letter Word as current draft evidence derived from
  the reviewed latest incoming source and bind it to the existing handoff.
- Catalog ID: `FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01` (ordinal `91`).
- Product commit: `7607a03e422b5e38d87767cc53b303e0e0013518`.

## Observable contract

The caller supplies the accepted Row89 context, Row90 rendered bytes, exact handoff and
actor under a caller-owned transaction. The service validates the case, source evidence,
mapping/template/handoff identities, filename, media type, content hash and managed path,
then creates the linked outgoing document and archive attachment. It registers one current
`CLIENT_LETTER_WORD` evidence version in `DRAFT`/`PENDING` state, records its derivation
from the approved latest incoming official source, and binds the generated document and
attachment to the handoff.

The service does not commit. It returns pending archive state so a caller rollback can
remove only the newly created managed file. Exclusive file creation, database identity and
content checks make an exact retry deterministic; mismatched, stale, ambiguous, conflicting
or partially existing state fails closed without overwriting another file or evidence
lineage.

## Verification and review

The exact archived focused test produced `20 failed` when the archive API/helpers were
absent. The minimal task-owned hunk was transplanted into the current shared service; no
whole-file archive replacement occurred. Focused GREEN passed `20` tests. The implementer
passed an affected `107`-test tranche after formatting; independent review passed the
focused `20` and an expanded current Row89/90, evidence, handoff and workflow tranche of
`123` tests.

Scoped Ruff, format and exact two-path diff checks passed. Independent High review approved
the exact commit with `P0/P1/P2 = 0/0/0`. The focused test remains byte-identical to the
preserved archive reference.

## Non-goals and rollback

No endpoint/UI/schema/migration, email delivery, final evidence approval, unrelated shared
workflow behavior or second catalog row is included. Rollback reverts the exact Row91 hunk,
focused test and this adoption record while retaining the accepted Row89 context and Row90
renderer.
