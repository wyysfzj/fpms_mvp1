# Independent Review — V8 Fee-Obligation Read/Draft Current Adoption

- Review class: `PROTECTED`
- Reviewed range:
  `ea06bcd71a5017ba543f78f272605db56d19ee0b..1975bb1027f201a9bc35201dcc0cafbdfc278729`
- Reviewer: independent GPT-5.6 High review lane
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The exact four-path story adopts catalog rows 110 and 113 from their preserved terminal
legacy evidence into the current Lean tree. Historical RED was not rerun. The detail-read
test remains the exact accepted archive blob; current Ruff normalization of the service
and prepare-draft test is AST-equivalent to their accepted archive blobs.

`get_fee_obligation` preserves zero/one/exactly-four SELECT budgets, explicit mapping rows,
`no_autoflush`, the caller identity map and zero writes. It returns persisted independent
statuses without inference and fails closed on corrupt, partial, cross-linked, ambiguous
or broken supersession lineage.

`prepare_draft` requires an actionable persisted obligation, explicit `PAY` instruction
and valid current lines. It creates or reuses exact draft/item/link facts and exactly one
canonical `FEE_DRAFT_CREATED` activity with `center_changes={}` in the caller transaction.
Replay, conflict, rollback and partial-failure behavior remain atomic.

Fresh independent verification:

- serialized eleven-file SQLite tranche: 290 passed;
- scoped Ruff, Ruff format-check and exact-range diff-check: passed;
- product/test tree SHA-256:
  `3725084b2996d6257fb8f5e3767c3293ed9ba7c5295b6c4d7cb264391fcf3aa3`;
- patch SHA-256:
  `7b74fc9b507cce0b7f4c957bf9d688393520acd5581de51592b722d16cf423ed`;
- story SHA-256:
  `c8fa32be54126026d86cdfa8cc449581d5b97dcdd1937828822be2f79eabea35`.

The existing fee-obligation core was independently re-attested compositionally. All 92
pre-existing service functions/classes, including row 114 `record_payment_evidence`, are
unchanged. Its current tree SHA-256 is
`56728d5e3aff63642cd5e4b7f1b98846f0b6771510b15cea3d93796db56648be`.
