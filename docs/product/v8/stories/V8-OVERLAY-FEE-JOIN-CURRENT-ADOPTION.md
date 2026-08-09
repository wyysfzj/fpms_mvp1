# Story V8-OVERLAY-FEE-JOIN-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commit: `1d34956`.
- Product/test commits: `677a887`, `2977616`, `faf3b91`.
- Catalog ID: `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01` (ordinal `262`).
- Outcome: project only exact activity-rooted obligation and related fee facts into the
  lifecycle overlay.

Seven accepted fee activity families are strictly decoded. Payload obligation, line, item,
draft, PayList, payment and export-artifact identities must match the persisted relation graph;
missing, cross-case, ambiguous or disagreeing data fails 409. Unknown fee activities remain valid
with no attached fee facts, and no amount/name/date fallback is used.

The accepted deep obligation read is cached once per distinct obligation per overlay invocation.
All seven statuses and nullable source fields remain independent, official/source/payable amounts
use exact two-decimal strings, and the reduction ratio uses four decimals. Related draft, PayList,
payment and official-evidence facts preserve their exact stored IDs and statuses. The caller
session is read-only.

The saved RED observed the empty predecessor tuple. Review-driven corrections added exact
payload/persistence checks and the full success/failure matrix. Final fee plus center/document
verification passed 38 tests; scoped Ruff, format and diff checks passed; independent High review
approved P0/P1/P2 all zero.

No fee calculation/mutation, decision gate, pagination, endpoint/UI, schema or fuzzy association
is included. Rollback reverts the three product/test commits and this adoption while preserving
the accepted center/document predecessors.
