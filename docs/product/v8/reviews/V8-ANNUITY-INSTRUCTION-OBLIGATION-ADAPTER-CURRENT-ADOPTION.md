# Independent Review — Annuity Instruction Obligation Adapter Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row121_independent_review`
- Product/test commit: `05a2c9346ca36b9c19b3bb0b59a67f258a74cc14`
- Product baseline: `ae42096d7a82c91dfcc552a8238c37dde6445f79`
- Story: `docs/product/v8/stories/V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-CURRENT-ADOPTION.md`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified the exact Task-121 closure at the named commit. The
adapter accepts only the exact frozen command and `PAY | HOLD | ABANDON` values, resolves
only the named persisted task and its unique obligation, requires the complete six-field
carrier, and fails closed under the accepted 404/409 partition for absent, partial,
malformed, cross-case, wrong-type/year, source, document, evidence, recognition and
cardinality facts. It delegates exactly once to `record_client_instruction()` with the
resolved obligation and unchanged actor/idempotency key.

## Replay, transaction and non-mutation

The current row-107 successor semantics are preserved: the obligation header and line keep
the grant source activity, the unique same-case recognition is its child, and the new
instruction activity names that recognition activity. Exact replay reaches the same deep
selector, reuses the original result/activity without writes, and changed command, task,
obligation, lineage or stored instruction facts retain conflict behavior. A new key for the
current instruction remains the deep same-state conflict.

The adapter performs no commit or rollback. The focused rollback assertion proves that the
caller can remove the instruction header change, activity and lifecycle revision together.
The adapter never assigns any annuity-task field, so legacy `client_instruction`,
`pay_next_year`, source/rate/lineage carrier fields and other named non-goals remain
unchanged. The delegated instruction activity retains the accepted empty evidence tuple.

## Current successor compatibility

`V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION` remains intact at the exact current
`05a2c9346ca36b9c19b3bb0b59a67f258a74cc14` state:

- the certificate-archive adapter and focused test are byte-unchanged from the product
  baseline (blob IDs `1bc4ff97490697eaa233764a85826c46c6d3d917` and
  `3e60ae225851f2a8e53c798dd2b683e8efc15da5`); and
- the existing government-payment adapter functions are outside every changed service
  hunk, while its focused test is byte-unchanged (blob ID
  `15de344eb6883fd96f8352a91460f637657020a0`).

The Task-121 commit adds only its three imports, its disjoint adapter block after
`add_manual_gov_payment`, and its focused test. It does not alter either existing activity
adapter or absorb their closures.

## Fresh independent verification

- `cd backend && pytest -q tests/test_v8_annuity_instruction_obligation_adapter.py` —
  `45 passed`, exit `0`, with one inherited passlib `crypt` deprecation warning. The
  worktree has no `backend/.venv`, so the available project pytest executable was used.
- `cd backend && ruff check app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py`
  — all checks passed, exit `0`, with only the existing Ruff configuration deprecation
  notice.
- `git show --check 05a2c93` and the exact two-path `git diff --check` — clean, exit `0`.
- Commit inspection names only `backend/app/modules/annuity/service.py` and
  `backend/tests/test_v8_annuity_instruction_obligation_adapter.py`; both tracked paths
  have no drift from the exact reviewed commit.

The story-card SHA-256 is
`75d397f869f8d7660d94e80f0c71aab9bc012fcdcd6c1768b35ece68c1b0c2c2`.
The exact two-path product patch SHA-256 is
`72af710a6cee9ba2d356ba008493420ccb9f417b3f4a7192583fed76507a9830`.
