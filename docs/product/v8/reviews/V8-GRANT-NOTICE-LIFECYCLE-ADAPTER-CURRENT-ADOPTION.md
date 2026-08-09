# Independent Review — Grant Notice Lifecycle Adapter Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row155_independent_review`
- Integration parent: `37beb56c66a2dc450a7cb9e0ba6acffee4b0ef51`
- Dispatcher product/test commit: `997a6896b90deae18ecda7bde9db35e48513b242`
- Production-entry contract correction: `c6eaada1242e5093621ed173bdd6c8da8a8ab08d`
- API product/test commit: `06cd5882ac92a7ac3d6c7f102ccdecb67bb2c43b`
- Review correction product/test commit: `0ddab25caf2aee017bc3662a3b1068e13be631be`
- Adoption-story commit: `0c1d5e3e91852c5e7a0886f7e16b5db55adb9f7f`
- Story:
  `docs/product/v8/stories/V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-CURRENT-ADOPTION.md`
- Integration binding: `UNBOUND` (the controller alone owns coverage-ledger binding and
  ordinal-74 activation)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

## Independent contract and implementation review

The exact five-path implementation exposes one dedicated
`POST /grant-fee-tasks/{grant_fee_task_id}/lifecycle/grant-notice` route. It requires
`Doc.Edit`, derives the actor from the authenticated user, accepts only the four strict
contracted body fields, derives the source document only from the named grant-fee task,
and delegates to `dispatch_grant_registration_notice()` in one caller-owned transaction.
Missing task remains 404; invalid stored source-document lineage remains a write-free 409;
service or commit failure rolls back; success commits once and returns HTTP 200.

The dispatcher validates the exact task, document, executable semantics, current
`FINAL / APPROVED` evidence, immutable evidence hash, confirmed deadline, canonical
fee-line snapshot and replacement lineage before writing one confirmed
`GRANT_REGISTRATION_NOTICE_RECORDED` fact. Exact replay returns the stored activity without
a new write; drift and malformed stored history fail closed. The current production call
sites are only the dedicated API and the dispatcher definition. Ordinary document create,
attachment upload and generic evidence review remain lifecycle-neutral and were unchanged
by the reviewed product range.

The first independent review found one P2: the newly API-visible Row74 business and custom
validation messages were English. Correction `0ddab25` changes only those human-readable
messages to Simplified Chinese and adds exact assertions. Technical error codes, HTTP
statuses, request fields, permission, delegation, transaction and replay behavior are
unchanged. The correction re-review found no remaining P0, P1 or P2 issue.

## Fresh independent verification

From `backend/`, the exact serialized command after the review correction was:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q \
  tests/test_v8_grant_notice_lifecycle_api.py \
  tests/test_v8_grant_notice_lifecycle_adapter.py
```

Result: `73 passed, 3 warnings in 22.48s`, exit `0`. The warnings are inherited passlib
`crypt` and Pydantic `strip_whitespace` deprecations. The SQLite lane was released
immediately afterward. Before the correction, the same exact tranche returned
`66 passed, 3 warnings in 21.02s`, exit `0`; that result did not override the P2 finding.

From the repository root, scoped static verification ran on exactly the five authorized
Python paths:

```text
ruff check backend/app/modules/grant_fees/service.py \
  backend/app/modules/grant_fees/api.py \
  backend/app/modules/grant_fees/schemas.py \
  backend/tests/test_v8_grant_notice_lifecycle_adapter.py \
  backend/tests/test_v8_grant_notice_lifecycle_api.py

ruff format --check backend/app/modules/grant_fees/service.py \
  backend/app/modules/grant_fees/api.py \
  backend/app/modules/grant_fees/schemas.py \
  backend/tests/test_v8_grant_notice_lifecycle_adapter.py \
  backend/tests/test_v8_grant_notice_lifecycle_api.py
```

Results: Ruff returned `All checks passed!`; format check reported all five files already
formatted. Exact correction and cumulative five-path `git diff --check` commands returned
exit `0`. The worktree was clean before receipt creation.

## Exact identities

- cumulative five-path binary patch SHA-256 for `37beb56..0ddab25`:
  `eb0b6b2df7ca89f2ce7b7ae44cf97129c9d4f3b6b9d36310cf99ab26ba432aff`;
- review-correction five-path binary patch SHA-256 for `06cd588..0ddab25`:
  `3bb5bca506b010a1271e7b4bf83af8db932e5c44a47e866f93e3b80546bfec3e`;
- exact five-path Git-tree fingerprint at `0ddab25`:
  `30897eb30f288f9e25b7c4f83339227779a1d8f66a2161983234d6f3a28080da`;
- adoption-story SHA-256 at `0c1d5e3`:
  `6ec58befb8701851f559e3b8802df5cd299800c014b269433ddf4ccf5c3365a2`;
- adoption-story Git blob:
  `1501505e7f83ae6ed5e3f8a8a5fb7a380754e75b`.

This receipt approves only the exact reviewed dispatcher, dedicated API, strict schema,
two focused tests, correction and adoption story. It does not bind the coverage ledger,
activate ordinal 74, authorize ordinary upload/review lifecycle dispatch, create or
promote evidence, absorb Row75/76/130, repair inherited baselines, or claim a Foundation,
release or production milestone.
