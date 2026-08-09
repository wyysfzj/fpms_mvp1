# Independent Review — Annuity Draft Obligation Adapter Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row122_independent_review`
- Product/test commit: `2bac83751696741822ff8c269fb7784e3c4291a6`
- Product baseline: `545079d279b5296ec9cc101d1dc05b31ac2e7d3f`
- Story: `docs/product/v8/stories/V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-CURRENT-ADOPTION.md`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified the exact frozen row-122 closure. For every selected
current or next-year target, the adapter resolves that target's complete Task121 six-field
carrier and exact same-case Future Annuity obligation, recognition, document, evidence,
due-date, fee-year and fee-line lineage before delegation. Missing, partial, malformed,
absent or contradictory carrier facts fail closed before `prepare_draft` or any draft
write.

The adapter delegates once with the selected obligation, unchanged actor and stable
`annuity-draft:{task_id}:{obligation_id}` key. It projects the exact deep obligation,
draft, persisted link, activity, idempotency and reuse identities. Exact replay therefore
returns the original one draft, one item, one link and one `FEE_DRAFT_CREATED` activity;
the adapter does not append a second activity or synthesize another item.

## Transaction, savepoint and non-mutation

The adapter performs no commit or rollback. Each deep delegation and returned-lineage
validation is enclosed by a caller-owned nested transaction, so a post-delegation
lineage conflict rolls back that target's deep writes before the per-target failure is
reported. The SQLite outer-transaction bootstrap preserves the enclosing SQLAlchemy
transaction, and the focused caller-rollback assertion removes the draft, item, link,
activity and obligation draft-status change together.

The former direct draft/item write, internal commit and `task.draft_generated = True`
assignment are removed. The legacy marker check remains only as a fail-closed guard for
historical annuity drafts; the adapter neither changes nor relies on the legacy
`draft_generated` flag. `backend/app/modules/fees/obligation_service.py` and its accepted
deep `prepare_draft` rule are unchanged.

## Current shared-service successor attestation

The exact `2bac837^..2bac837` service diff changes only two non-colliding imports and
`generate_fee_drafts_from_annuity_tasks`. Every named current consumer below is outside
the changed service hunk, and each focused test or dependency blob remains unchanged at
the exact reviewed commit:

- `V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION`: `register_gov_payment` and its payment
  activity path remain disjoint; the certificate and government-payment tests remain
  blobs `3e60ae225851f2a8e53c798dd2b683e8efc15da5` and
  `15de344eb6883fd96f8352a91460f637657020a0`.
- `V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY`:
  `_record_gov_payment_official_evidence_activity` and `register_gov_payment` remain
  disjoint; the focused test remains blob
  `fb44f59e80ee7d067e3920b14580b8ca274c7dc3`.
- `V8-PAYLIST-INTERNAL-EXPORT-SERVICE`: its command/result, export, replay, storage and
  compensation seams remain disjoint; `export_excel.py` and the focused test remain blobs
  `beafa9b6ad228a26947e3bbd321fe9c2a7b63a0f` and
  `7322dd5f7081ae8102a6831bfd506a0de3d4c90a`.
- `V8-PAYLIST-EXPORT-BOUNDARY-CURRENT-ADOPTION`: `mark_pay_list_paid` and
  `get_pay_list_detail` remain disjoint; the payment/export-decoupling and artifact-read
  tests remain blobs `150572fa1024b821f9765167ac45e392d6459e20` and
  `8a81afde52206090c0d236d843fb2afd043f401c`.
- `V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-CURRENT-ADOPTION`:
  `create_pay_list_from_fee_items` remains disjoint; its focused test remains blob
  `59d6c94f743fc2ee84440d78346ac5baf5c1fe93`.
- `V8-FUTURE-ANNUITY-OBLIGATION-CURRENT-ADOPTION`: its command/result, writer, replay,
  six-field carrier and reduction-lineage helpers remain disjoint; its focused test
  remains blob `d54e9e1e5132a874b0d9a3150934e4e55549ed83`.
- Task121 `V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-CURRENT-ADOPTION`:
  `record_annuity_task_instruction` and its validation/result seams remain disjoint; the
  focused test remains blob `70b4aafe64683af30ceca8d7dbd5fa5d0b7c8e75`.

The implementer's durable affected tranche (`68 passed`) was accepted as prior evidence
and was not repeated. This review independently reran only the decisive row-122 test and
used exact current-commit static attestation for the named successors.

## Fresh independent verification

- `cd backend && pytest -q tests/test_v8_annuity_draft_obligation_adapter.py` —
  `5 passed`, exit `0`, with one inherited passlib `crypt` deprecation warning; the
  serialized SQLite lane was released immediately afterward.
- `cd backend && ruff check app/modules/annuity/service.py tests/test_v8_annuity_draft_obligation_adapter.py`
  — all checks passed, exit `0`, with only the existing Ruff configuration deprecation
  notice.
- `git show --check 2bac837` and the exact two-path `git diff --check` — clean, exit `0`.
- The two reviewed product/test paths have no worktree drift from `2bac837`; only
  `backend/app/modules/annuity/service.py` and
  `backend/tests/test_v8_annuity_draft_obligation_adapter.py` occur in the exact commit.

The exact two-path product patch SHA-256 is
`dc46b3a444517261b0b61732b33439c3af8d61b409223a22aa060c62a2bd1dae`.
The exact two-path Git tree fingerprint is
`2cdee5a4298e84495f88f814b0d59d32e45b9d9fd149d5829fba6aa181488f2c`.
The story-card SHA-256 is
`5f5a36f38cf220e15ef309a4a83b253bc275c5eef5309fb4893d13637d6a4187`.

No deep fee rule, second entrypoint, API/UI, schema/migration/seed, source/rate/reduction
policy, PayList, payment, service receivable, ledger, story, task, evidence or unrelated
annuity closure was absorbed.
