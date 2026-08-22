# Story V8-FUTURE-ANNUITY-REDUCTION-LINEAGE-CARRIER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Product/test commit: `03585cb723dece246d987eba92efcf3f0c24e7a5`
- Outcome: adopt the frozen Delta-27 Future Annuity reduction-lineage schema carrier on
  the current lean integrated tree.
- External prerequisite ID:
  `FPMS-V8-FUTURE-ANNUITY-REDUCTION-LINEAGE-CARRIER-20260724-01`.
- Authority: the exact archived task and approved Delta-27 contract freeze at archive
  commit `6b2ef89`.

## Exact paths and behavior

- `backend/app/modules/annuity/models.py`
- `backend/alembic/versions/v8_delta27_future_annuity_reduction_lineage.py`
- `backend/tests/test_v8_future_annuity_reduction_lineage_carrier.py`

The additive one-to-one carrier has exactly four columns linking one annuity task and one
fee-obligation line to the accepted reduction provenance and nullable exact approval row.
It uses the frozen named primary, unique, foreign-key and check constraints, `RESTRICT`
foreign keys, and create-only ORM update/delete guards. Revision
`v8_d27_annuity_reduction_01` consumes exact parent
`v8_d4_evidence_kind_capacity_01`; the migration creates only this table, performs no
backfill and is forward-only.

## Verification and review

The current-tree RED failed all five focused assertions because the model and migration
were absent and the repository head was still the frozen parent. After exact archive-hunk
recovery, the focused SQLite-writing schema, constraint and immutability test passed
`5/5`, including a clean temporary upgrade to the single Delta-27 head. Scoped Ruff,
single-head and exact-path diff checks passed.

An independent High reviewer approved the exact product commit with P0/P1/P2 `0/0/0`
after independently rerunning the focused test (`5 passed`), confirming the single
`v8_d27_annuity_reduction_01` head, scoped Ruff and diff checks, and verifying that no
Task 133 service or product-test behavior was absorbed.

## Non-goals and rollback

No annuity service or product-test edit, generic fee model or service change, backfill,
approval/rate behavior, API/UI, seventh annuity-task field, current product replay, old
task/evidence mutation or milestone claim. Rollback reverts only these three recovered
product/test paths and this story card.
