# Story V8 Grant Official Fee Manual Review Current Adoption

- Risk: `PROTECTED`.
- Contract commits: `9749fd1`, `1b70b57`, `922b6ff`.
- Product commits: `2af34af`, `5ac5568`, `92087a9`.
- Prerequisite owner: `REPO-V8-GRANT-OFFICIAL-FEE-MANUAL-REVIEW-20260810-01`.
- Downstream catalog owner: Row120
  `FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`.

An authenticated `GrantFeeTask.Write` operator can now confirm every exact grant-year official
full amount against the current approved grant-notice evidence. The service never derives that
amount from the payable amount, reduction ratio or rate data. It appends one canonical FEE review
fact with the original two evidence references, actor/time, before/after lines and case-scoped
idempotency, then atomically compare-and-sets the complete line set from `REVIEW_REQUIRED` to
`MATCHED` in the caller transaction.

Exact replay, current evidence, immutable recognition, unique review lineage, unchanged center
projection, full CAS predicates and the Row120 read seam fail closed. Generic obligation detail and
overlay readers retain the immutable recognition payload while accepting matched live lines only
through this exact review fact; partial review, evidence drift and later lifecycle transitions are
covered.

The original RED failed five tests on the absent interface. Final focused verification passed 11
tests; the exact grant, obligation detail/overlay and generic draft tranche passed 197 tests.
Scoped Ruff and diff checks passed. Two independent High reviewers approved the final correction
with P0/P1/P2 all zero.

The accepted path set includes the exact successor contract and its authoritative
`source-decision-registry.md` entry. This records the reviewed source/decision bytes as the latest
accepted owner instead of leaving their post-C3 amendment outside the coverage ledger.
