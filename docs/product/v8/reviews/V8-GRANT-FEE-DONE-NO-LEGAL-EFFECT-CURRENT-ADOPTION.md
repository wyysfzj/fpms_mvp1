# Independent Review — Grant Fee Completion Without Legal Effect

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row67_independent_review`
- Product/test commit: `bd73ceb851e7b4b4b8ba87a9914eeac283079d53`
- Product/test parent: `541d25397bd285985b14b4b5c6a09feca15e5cbd`
- Adoption-story/current commit: `3474dc3e8ce987f11f3cb1cf9281214984e07957`
- Story:
  `docs/product/v8/stories/V8-GRANT-FEE-DONE-NO-LEGAL-EFFECT-CURRENT-ADOPTION.md`
- Integration binding: `UNBOUND` (the controller owns the later coverage-ledger binding)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

## Independent contract review

The exact `mark_done` path no longer writes `Case.status = GRANTED` or any other legal,
business-stage, official-procedure, verification or legacy projection. It mutates the
grant-fee task to `DONE` and appends exactly one confirmed `GRANT_FEE_TASK_DONE` activity
in the `FEE` lane with canonical payload `{"center_changes":{}}`, no evidence references
and deterministic idempotency key `grant-fee-task:{task_id}:done`.

The activity receives the same typed lifecycle projection on both sides and the unchanged
legacy case status. The shared append seam therefore advances only activity sequence and
`lifecycle_revision` by one. A second `mark_done` action is rejected by the existing state
machine and cannot append a duplicate activity; the deterministic key also retains the
deep append seam's exact-key idempotency boundary.

Audit identity is resolved only as `task.updated_by or task.created_by`. A missing,
non-string, blank, whitespace-padded or over-36 identity fails closed with 409 code
`GRANT_FEE_TASK_DONE_ACTOR_REQUIRED` and Simplified Chinese text
`授权费任务完成活动缺少可追溯操作者`; no client, system or evidence fallback is introduced.
Invalid stored lifecycle projection also fails closed with Simplified Chinese conflict
text.

Task mutation, case revision, activity append and commit share the existing service
transaction. Both append and commit exceptions invoke rollback before re-raising. No
Row74 dispatcher/API behavior, grant-announcement transition, obligation/draft, fee
amount, schema/migration, endpoint, UI or adjacent state-machine behavior entered the
reviewed range.

## Exact scope and identities

Range `541d253..bd73ceb` changes exactly the service and focused test. Range
`bd73ceb..3474dc3` leaves both blobs unchanged and adds only the adoption story.

- service Git blob at product and current commits:
  `62ea637707725c1b5e99cd6c89f239e194edb5d3`;
- focused-test Git blob at product and current commits:
  `58b4e1e825059adf3afbab87e9415240ef51a212`;
- story Git blob: `509dd6d52753609aa300caa53bd9fbd7b3e39f62`;
- service SHA-256:
  `67b4d062266255d5893fc52d35df761a6b314731d26e3839869184535a8b1b38`;
- focused-test SHA-256:
  `b32ce0a8d6f2e47c9ee9fb95f7696d9bf8779d4d3f2af043853baad889eb7c40`;
- story SHA-256:
  `a23de7cb13c0041e2fecb18f50c9a4615a1fff744e4c1682d150d857d4e08000`;
- exact product/test binary-patch SHA-256:
  `7f5b89f99d7184799d443c3d2a2dd2d3e4b9e1cffba90ff1b66deb3182aac9f4`;
- exact story binary-patch SHA-256:
  `4c9b8626b0bd1c03eda98baab864272ff890ae1d2fbd89c643fcd316c88b5b7e`;
- exact current two-path Git-tree fingerprint:
  `1b08626ba493ad5d6cbc4ead7b0fd503ba44ae04e9022a5b8399701cba72bd51`;
- exact current product/test/story Git-tree fingerprint:
  `cabe8dac8e3e42bdaa2655b2bcb1b68b01a8eb58d8b2069625da5f62fe7ca212`.

## Fresh independent verification

- From `backend`, the exact serialized command
  `pytest -q tests/test_v8_grant_fee_done_no_legal_effect.py
  tests/test_v8_grant_notice_lifecycle_adapter.py` returned
  `54 passed, 1 warning in 14.02s`, exit `0`. The warning is the inherited passlib
  `crypt` deprecation. The SQLite lane was released immediately afterward.
- Fresh scoped `ruff check` returned `All checks passed!`, exit `0`; fresh
  `ruff format --check` returned `2 files already formatted`, exit `0`. Their only
  message was the repository's existing top-level-settings deprecation.
- Exact product/test and story `git diff --check` commands returned exit `0`.
- The reviewed product, test and story paths have no worktree drift from `3474dc3`.

The unrelated parallel-work path
`backend/tests/test_v8_grant_attachment_no_legal_effect.py` was already modified outside
this review scope before receipt creation. It was not read, changed, staged, reviewed or
absorbed here.
