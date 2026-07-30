# Story V8-PREPARE-OA-REPLY-SEAM-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
  (frozen catalog ordinal `48`, profile `TC-SERVICE`).
- Base: `434378756fe02a937b32127dbbe5605b8fad7c3d`.
- Outcome: validate one same-case incoming OA notice, its current evidence and the exact
  selected typed copyable/noncopyable attachment policy, then create or exactly replay one
  unreviewed `DRAFT` `OA_OUT` evidence version, its unique reply-package link and one
  canonical preparation derivation in the caller transaction.
- Authority: the exact frozen row-48 task and its Delta-4 appendix,
  `docs/product/v8/domain-contract.md`, `docs/product/v8/source-decision-registry.md`, and
  the current independently accepted document-evidence and OA policy stories.
- Change mode: exact archive adoption from
  `6b2ef89da447353380b99853168d4d38aaf9210a`, with current successor-owned policy bytes
  winning.

## Dependency and hidden-prerequisite chain

The current dependency chain is:

1. row 47 external-submission finalization and its successor role allowlist, current
   verified by `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION` and the current contracts
   story;
2. D4-08 typed OA structured-attachment promotion at
   `87a7205452c813d7be02b4d2b4c70bab37db3c16`;
3. row 72 typed copyable OA attachment policy at
   `8341a7a4146494af6038f72bc26d6e2efd028038`;
4. row 73 noncopyable appendix policy, including its independently reviewed carrier
   correction; and
5. this row-48 preparation seam.

Row 48 directly persists an `OA_REPLY_PREPARATION` derivation. The current contracts story
deliberately reserved that exact public vocabulary member for a future row-48 story. The
controller therefore authorized one hidden prerequisite inside this same PROTECTED story:
the exact one-line enum member and matching expected-contract test line from the archive.
No other role, derivation value or public contract shape changes.

## Exact closure

`PrepareOaReplyCommand` and `OaReplyPackageResult` retain their frozen, slotted,
keyword-only shapes. `prepare_oa_reply(command, transaction)`:

- validates the named case, executable incoming OA notice, its exact current source
  evidence, the exact `OA_REPLY` package and exact outgoing `OA_OUT` document/attachment;
- consumes only typed `CopyableOaAttachmentEvidence` DTOs and exact persisted
  version/manifest/attachment identities;
- applies the current row-72 copyable policy and, only for a two-sided
  `OA_STATEMENT_APPENDIX` alias, the current row-73 noncopyable derivation policy;
- rejects duplicate, stale, cross-case/package, RAW, unapproved, hash/link/state/review,
  role and cardinality conflicts before durable reply writes;
- creates exactly one current `GENERATED_ATTACHMENT` version in `DRAFT/PENDING`, with no
  reviewer, review time or external-submission time;
- links the unique source package to the exact reply and records one canonical
  `OA_REPLY_PREPARATION` source-to-reply derivation receipt; and
- reuses only an exact complete replay with the same source, typed attachment set,
  identities, hashes, roles, links, cardinality, actor and canonical receipt.

The caller owns commit and rollback. The seam performs no internal commit or rollback and
does not repair or select among contradictory carriers.

## Exact paths

### Product

- `backend/app/modules/documents/evidence_workflow_service.py`
- `backend/app/modules/documents/evidence_contracts.py`

### Tests

- `backend/tests/test_v8_prepare_oa_reply_seam.py`
- `backend/tests/test_v8_document_evidence_contracts.py`

### Story

- `docs/product/v8/stories/V8-PREPARE-OA-REPLY-SEAM-CURRENT-ADOPTION.md`

The workflow service is byte-identical to archive ref
`6b2ef89da447353380b99853168d4d38aaf9210a`. The focused row-48 test differs from its
archive blob by one successor-only fixture line: its full-reply parent is explicitly
`DRAFT`, as required by the current independently accepted row-73 carrier policy. The two
public-contract files differ from their current base by only the archive's matching
`OA_REPLY_PREPARATION` lines.

## Historical RED and fresh verification

Historical row-48 RED/GREEN is preserved by reference and is not rerun or manufactured.
Fresh verification runs only:

- the focused row-48 GREEN;
- the row-42 public-contract regression;
- row 47 finalization and the current external-submission role allowlist;
- D4-08 structured-attachment promotion;
- row 72 copyable policy; and
- row 73 noncopyable appendix policy.

Scoped Ruff covers the four code/test paths, followed by exact diff and allowlist checks.
SQLite-writing tests remain serialized under the controller-granted lane. The exact
commit/range still requires an independent High review; the implementer does not approve
this story.

The first controller-granted focused command produced `35 passed, 1 failed`. The sole
failure reached the current row-73 policy and proved the archived positive appendix
fixture still supplied a `FINAL` generated full-reply parent, while the accepted successor
requires the parent to be current `DRAFT` with no final-submission time. The service
correctly failed closed with `OA_REPLY_IDENTITY_CONFLICT`. The lane was released before
the declared regression tranche, and no ungranted rerun occurred. The minimum test-only
alignment above preserves independent approval while making the fixture satisfy the
current parent-state authority.

After the one-line test-only alignment, the fresh controller-granted verification
produced:

- focused row-48 GREEN: `36 passed, 1 warning` in `9.93s`; and
- the exact six-file public-contract, row-47, allowlist, D4-08, row-72 and row-73
  regression tranche: `269 passed, 1 warning` in `66.44s`.

Both warnings are the inherited passlib `crypt` deprecation. No other pytest command or
rerun occurred, and the controller's SQLite lane was released immediately after the
declared tranche.

## Non-goals and rollback

No HTTP, router, schema/model/migration/seed, UI, task close, external submission,
independent review, approval/finalization, lifecycle or legal-status transition, fee,
deadline, customer decision, filename/ORM-role inference, row 49+, adjacent enum, ledger,
disposition, review receipt, old evidence or taskctl mutation is included.

Rollback reverts the single story commit: the preparation seam/test, the exact
`OA_REPLY_PREPARATION` public vocabulary/test lines and this story card. All current row
47, D4-08, row-72 and row-73 successor bytes remain intact.
