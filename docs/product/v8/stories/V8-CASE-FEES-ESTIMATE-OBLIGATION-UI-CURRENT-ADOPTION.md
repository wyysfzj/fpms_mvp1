# Story V8 Case Fees Estimate and Obligation UI Current Adoption

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
  (ordinal `267`).
- Product commits: `62d4354`, `e102a9e`, `be2795c`.
- Outcome: keep explicit official-fee estimation, persisted obligations and persisted drafts as
  three independent facts on the case fee tab.

The page performs no preview on mount. A user explicitly chooses the trigger, optional reviewed
source document and rate-effective date before sending the frozen preview request. Reviewed-source
choices retain the accepted overlay's approved-only, first-occurrence ordering. Estimate candidates
preserve raw decimal strings and complete server provenance.

Persisted obligations render all seven status dimensions without deriving them from estimates or
drafts. Overlay failures remain visible and never become an inferred empty obligation set. On the
case-detail page the tab consumes the parent-managed overlay snapshot, including loading and error
state, and performs no second overlay request; standalone callers retain the same fail-closed read.

The final focused suite passed five tests. Scoped ESLint and exact-path diff checks passed. The
frontend typecheck retained only five captured diagnostics in unrelated API modules. Independent
High review approved the corrected exact closure with P0/P1/P2 all zero.

No obligation, draft, PayList, payment, lifecycle or document fact is created or mutated by this
story.
