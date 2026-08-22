# Story V8-OA-OUT-PACKAGE-ATOMIC-LINK-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `f7bf2fc702a7`
- Outcome: the existing OA_OUT wizard entrypoint prepares the exact unique OA reply
  package through `prepare_oa_reply()` in the caller-owned transaction, so document,
  generated attachment, evidence version, package link and preparation derivation persist
  together or roll back together while the reply task remains open.
- Catalog ID: `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01` (ordinal `67`, profile
  `TC-ADAPTER`).
- Authority: frozen catalog row `67`, its Delta-8 latest-wins recovery appendix,
  `docs/product/v8/domain-contract.md`, and the independently accepted
  `V8-PREPARE-OA-REPLY-SEAM-CURRENT-ADOPTION` story.

## Dependency and exact paths

The current row-48 `prepare_oa_reply()` seam and its accepted typed copyable/noncopyable
attachment policy are the prerequisite. The Delta-8 inherited case-create fixture
alignment is historical prerequisite evidence; its accepted strict `fee_reduction`
contract remains unchanged.

- `backend/app/modules/documents/service.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_out_package_atomic_link.py`
- `docs/product/v8/stories/V8-OA-OUT-PACKAGE-ATOMIC-LINK-CURRENT-ADOPTION.md`

The two shared services and all SQLite-writing verification remain serialized.

## Observable contract

Only an OA_OUT wizard row with one exact source OA notice, one exact current source
evidence version, one exact OA_REPLY package, one generated reply attachment and the exact
typed package manifests reaches the preparation seam. The adapter builds the frozen
`PrepareOaReplyCommand` from persisted identities and calls `prepare_oa_reply()` without
duplicating its deep validation or committing internally.

Missing or ambiguous package, source evidence, reply attachment or selected typed
manifest identity fails closed with `OA_REPLY_IDENTITY_CONFLICT`. The existing outer
wizard transaction rolls back all database writes and removes generated managed files on
any adapter, seam or commit failure. A successful preparation links the package to the
reply, creates one DRAFT/PENDING reply evidence version and one preparation derivation,
and leaves the existing reply task OPEN.

## TDD and verification

The archived row-67 focused test is restored byte-for-byte. Its SHA-256 is
`afbcfd1750d4f1ca394be5509a5b124d3d9627d5e58f2e1c13f1ab7954f71818`.
The controller-granted focused RED produced `9 failed, 1 passed`: the positive path left
the package reply link unset and every invalid-identity case failed to raise. The minimum
archived row-67 adapter hunk then produced focused GREEN `10 passed, 2 warnings` in `3.54s`.
Both warnings are inherited deprecations. The inherited regression tranche and targeted
Playwright remain deferred to their controller-granted serialized close point. Independent
High review of the eventual exact commit/range remains required.

## Non-goals and rollback

No change to `prepare_oa_reply()`, evidence policy, OA prepared activity, task completion,
external submission, lifecycle projection, HTTP/API, schema/model/migration/seed, UI,
legacy task/evidence, ledger, review receipt or adjacent service behavior. In particular,
the row-68 `OA_REPLY_PREPARED` activity hunk present in the quarantined mixed diff is not
part of this story. Rollback reverts only the four paths listed above.
