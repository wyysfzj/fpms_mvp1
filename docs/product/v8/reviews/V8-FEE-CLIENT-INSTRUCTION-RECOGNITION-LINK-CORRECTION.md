# Independent Review — Fee Client Instruction Recognition Link Correction

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/fo_recognition_link_review`
- Product commits:
  - `91bb15619ce111d8d78f6f4b4d04ee1d3f39511d`
  - `f7bf2fc702a748eac9951dc42fe41f989c070b8e`
- Product baseline: `cb9eb7c735f8986a7ad871c732382d946ba1b48e`
- Story: `docs/product/v8/stories/V8-FEE-CLIENT-INSTRUCTION-RECOGNITION-LINK-CORRECTION.md`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified that the two exact product commits remove only the
unsupported requirement that the unique recognition activity ID equal the obligation
header's durable source activity ID. Both first-write and exact-replay paths now resolve
the same unique same-case `FEE` `FEE_OBLIGATION_RECOGNIZED` activity whose
`FPMS_FEE_OBLIGATION_RECOGNIZED_V1` payload names the obligation. A newly recorded client
instruction continues to name that recognition activity, while the Task-133 obligation
header, line and recognition child retain the grant source.

## Prior P1 closure

The first review rejected `91bb156` because its Task-133-shaped first write succeeded but
the exact same-key replay still treated `header.source_activity_id` as the recognition
activity and compared the instruction source to that header source. Successor
`f7bf2fc702a748eac9951dc42fe41f989c070b8e` closes both failure points:

- replay resolves the recognition through the same cardinality, case, lane, activity-type,
  schema and obligation-payload selector used by the first write;
- selector failure on the existing-key path retains the frozen idempotency-conflict
  partition;
- the resolved recognition ID is passed through current and recursive prior-fact replay
  validation, so every stored instruction activity must still name the exact recognition;
  and
- the focused Task-133 regression now commits the first write, replays the same actor/key
  and payload, requires `reused=True` with the original activity ID, and proves no activity
  row or lifecycle revision is added.

The prior P1 is closed.

## Fail-closed and shared-path compatibility

The full focused suite confirms that malformed, cross-linked and duplicate recognitions;
changed actors, keys, commands or canonical instruction payloads; corrupted timestamps,
sources, evidence, supersession chains or stored state; race conflicts; downstream locks;
caller rollback; and forced post-append failure retain their exact fail-closed/no-side-effect
behavior. The source check changed only from the obligation header source to the uniquely
resolved recognition ID; it was not removed from current or recursive replay-chain
validation.

The current ledger lists four `CURRENT_VERIFIED` stories sharing
`backend/app/modules/fees/obligation_service.py`, and the exact product commits remain
compatible with each:

- `V8-FEE-FACT-WRITERS-CURRENT-ADOPTION`: row 107 now supports Task-133 lineage on first
  write and exact replay while preserving its actor, key, payload, evidence, chain,
  transaction and no-side-effect rules; the fee-reduction writer is untouched.
- `V8-FEE-OBLIGATION-READ-DRAFT-CURRENT-ADOPTION`: new and replayed draft preparation use
  the same unique recognition selector and retain exact instruction-chain source,
  actionable-state, line, relation and replay validation.
- `V8-FEE-OBLIGATION-CORE-CURRENT-VERIFICATION`: the owned recognition, estimate and
  payment-evidence seams do not call the changed replay helpers and are unchanged.
- `V8-ANNUITY-PAYABLE-AMOUNT-RULE-CURRENT-ADOPTION`: the pure payable-amount calculation
  slice is untouched.

## Fresh independent verification

- `cd backend && pytest -q tests/test_v8_fee_obligation_instruction.py` — `35 passed`,
  exit `0`, with one inherited passlib `crypt` deprecation warning.
- `cd backend && ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py`
  — all checks passed, exit `0`; Ruff also reported the existing top-level configuration
  deprecation notice.
- `git show --check 91bb156` and `git show --check f7bf2fc` — clean, exit `0`.
- Exact two-path diff check from `91bb156^` through `f7bf2fc` — clean, exit `0`.
- Worktree comparison against `f7bf2fc` for the service and focused test — no drift,
  exit `0`.
- Each exact product commit names only
  `backend/app/modules/fees/obligation_service.py` and
  `backend/tests/test_v8_fee_obligation_instruction.py`. The unrelated intervening
  documentation commit `eb74f41` is excluded from this product review.

The story-card SHA-256 is
`13e492e3d511903897ce32fbe442fc95ca3af0856ad84fa2ffb011aacf9b4362`.
The exact two-path combined product patch SHA-256 is
`e7499397cc40788f73b17d7b8edc2e129c8c107f3b23f39dc1d7b3f38839e7c4`.
