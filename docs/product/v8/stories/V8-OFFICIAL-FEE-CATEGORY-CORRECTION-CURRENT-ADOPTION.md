# Story V8-OFFICIAL-FEE-CATEGORY-CORRECTION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the already-integrated official-fee
  category correction satisfies frozen catalog row `158`.
- Change mode: current adoption only; no seed, test or product byte changes.
- Catalog ID: `FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01` (ordinal `158`,
  profile `TC-SERVICE`).
- Authority: the official-fee, source, seed and SQLite rules in
  `docs/product/v8/domain-contract.md`; the reviewed-source and activation boundaries in
  `docs/product/v8/source-decision-registry.md`; frozen catalog row `158`; and its exact
  task contract.
- Archive comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.
- Base: `bd1b60344dc2cc65da593f2fddb7f2ffcf18fcf7`.

## Dependency and exact correction

The canonical prerequisite
`FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` is current-verified by
`V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-CURRENT-VERIFICATION`. Its latest story
clarification commit
`409918c74405213e0ca294baa45e214d0a0f1ed9` is an ancestor of this story base.

The exact `CN_PUBLICATION_PRINT_FEE` row retains its fee code and established row history
while synchronizing only the frozen classification:

- `fee_category="公布印刷费"`;
- `fee_subtype="仅发明专利"`;
- `reduction_scope="不可费减"`; and
- `allow_reduction=False`.

The idempotent seed updates the existing row in place. It preserves the row ID,
`created_at`, fee code and all history represented by that identity. It does not create a
replacement code, activate a new source, infer another fee amount or widen reduction
eligibility.

## Exact paths and byte identity

- Seed: `backend/scripts/seed_dev.py`
  - Git blob: `82a58ec0035cb97116a4303f9d14e956972ac841`
  - SHA-256:
    `b9867318c9e24742a56bd3607ef7048f07153672446876e8d85b6c4de48ae928`
- Focused test: `backend/tests/test_v8_official_fee_category_correction.py`
  - Git blob: `a217312c52de64d5105372fd998b2119bd57ca4c`
  - SHA-256:
    `fa10d9f37cca9f6a4113b27f09624a1706b6c2f81f6d148628b572051b1c0c16`
- Story:
  `docs/product/v8/stories/V8-OFFICIAL-FEE-CATEGORY-CORRECTION-CURRENT-ADOPTION.md`

Both complete seed/test files are byte-identical between the archive checkpoint and this
story base. Historical PASS and archive identity are comparison evidence; current
acceptance still depends on the controller's focused current-tree verification and
independent High review.

## Verification and review

The controller ran the focused test serially on this exact base before story work:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_official_fee_category_correction.py
```

Observed result: `1 passed, 1 warning`; the warning is the existing third-party passlib
`crypt` deprecation. The implementer did not repeat that serialized test.

Scoped Ruff check-only on the exact seed/test paths passed. Exact diff checks prove both
paths remain unchanged from the story base. An independent High reviewer must review the
exact story commit and independently rerun the decisive check under the serialized lane.
The implementer does not approve this `PROTECTED` story; it remains pending independent
review.

## Parked work, non-goals and rollback

Catalog row `88`, `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`, remains parked
behind its external LibreOffice loader blocker. This story does not adopt any row-88
template, loader, mapping, seed or test byte.

No second dataset, fee-code replacement, source activation, official-rate or amount
change, reduction-policy change, backfill, service, endpoint/API, schema/migration, UI,
adjacent seed cleanup, customer-decision activation, ledger/disposition/review edit, old
task/evidence mutation or Foundation claim.

Rollback reverts only this story-card commit; the already-integrated seed and focused
test bytes remain unchanged.
