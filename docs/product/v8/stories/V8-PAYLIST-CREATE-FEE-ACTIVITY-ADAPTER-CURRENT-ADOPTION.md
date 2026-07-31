# Story V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `ddc0a53`
- Catalog row: `123`,
  `FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01`.
- Outcome: current-adopt PayList creation so every included fee item is bound to its exact
  obligation lines and each affected case receives one linked `PAY_LIST_CREATED` fee
  activity without a second financial activity.
- Authority: the frozen row-123 task contract and current-verified obligation-draft-link
  carrier and `prepare_draft` dependencies.

## Exact behavior and paths

Before writing the PayList, every selected item must resolve to exactly one same-scope
obligation and its exact draft-item links. Obligations for one case must share one
non-null recognition activity. The adapter groups rows per case, appends one confirmed
fee-lane activity with exact sorted item/obligation/line IDs and the stable PayList key,
and preserves the existing lifecycle projection. Missing links, conflicting source
activities, missing case or actor fail closed before durable completion. The caller owns
the transaction; this entrypoint flushes but does not commit.

Story-owned paths:

- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_pay_list_create_activity_adapter.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- this story card.

The focused public test is adopted byte-for-byte from the independently accepted archive
checkpoint with SHA-256
`9ff792e45db6294e225770b511e7d626866d76d36ac54c1343b4c59f24d4b2d8`.
The product change is limited to pre-resolving obligation link/activity context, appending
the exact per-case activity, and replacing the internal commit with a flush.

## Verification, non-goals and rollback

Run the focused test as RED and GREEN under the serialized SQLite lane, then the affected
PayList/obligation regressions and scoped Ruff/diff checks. An independent High reviewer
reviews the exact commit and reruns the decisive focused test.

The adopted public test produced the contract-complete RED with `4 failed`: missing list
activity, missing-link and source-conflict acceptance, and an internal commit that survived
caller rollback. After the minimum adapter port, the focused GREEN passed `4` tests and
the combined PayList activity, government-payment activity and prepare-draft regression
passed `28` tests. Scoped Ruff and diff checks passed. The disposition transfer leaves
`474` unique paths with exact story counts and SHA-256
`dd26fa48ec2d74f8c95df7db3de2fb6594df0c12673c4e3629ae709ad65bc04c`.

No PayList export, official workbook, payment acceptance, payment evidence, obligation
creation, fee amount/rate/reduction, service receivable, API, UI, schema, migration, seed,
unrelated annuity flow or adjacent refactor is included. Rollback removes only this adapter
slice, focused test, exact disposition transfer and story card.
