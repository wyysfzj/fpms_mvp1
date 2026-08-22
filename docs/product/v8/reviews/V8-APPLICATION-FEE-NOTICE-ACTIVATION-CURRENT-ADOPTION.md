# Independent Review — Application-Fee Notice Activation

- Review class: `PROTECTED`
- Product commits: `36ab390`, `f14d269`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The initial independent review found and runtime-confirmed one P1: the public document
wizard exposed row 34 as a generic fee candidate and could create a zero-value open draft.
The correction added public-path RED coverage, removed the generic preview candidate and
rejects any caller-supplied row-34 fee row before document or draft writes. The existing
deep-module application-fee draft suppression remains unchanged.

The corrected story activates only
`OFFICIAL_NOTICE_034 / 缴纳申请费通知书 / 200103` as executable
`APPLICATION_FEE_NOTICE` with explicit-official-due policy. The prior seven executable
rows remain, every other IN row remains reference-only, seed convergence is idempotent,
and the reviewed real path creates or reuses exactly one obligation. It creates no status,
task, reply or draft side effect and does not activate or infer the pending page/priority
preview-source decision.

Fresh public-wizard correction tests passed `2/2`; original activation and row-126
obligation tests passed `29/29`. Successor tranches for rate-book, fee-category, activity,
document evidence/review and OA reply projection all passed. Scoped Ruff and combined and
correction diff checks passed. All five shared-path stories remain compatible and advance
to the appropriate activation or correction commit.

The exact four-path story fingerprint is
`0be1deb316c639384ba438edc882c96a4e42aa3fb870525ed9b1fe31184a440f`.
The combined product range patch SHA-256 is
`3ce1bde7fdfbcbac21db7ade8726092d9d120bc4c6ca8b47ac022566ffab5650`;
the correction patch SHA-256 is
`638d8b540a4dcbe641ea4cb2bfd1a8c5ebd0cd435b614d81c30a306f576d0a8d`.
