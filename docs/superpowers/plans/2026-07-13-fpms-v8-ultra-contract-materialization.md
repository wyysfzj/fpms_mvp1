# FPMS V8 Ultra Contract Materialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to materialize this plan task-by-task. Each worker owns exactly one task-file path; no product implementation occurs in this plan.

**Goal:** Convert the approved Ultra delta design into High-ready atomic task contracts, three explicit external prerequisite tasks, and an audited delta execution overlay without rewriting the immutable V8 baseline catalog.

**Architecture:** Preserve the approved 283/197/86 catalog and its PASS evidence as historical baseline. Add a separately validated delta overlay containing three external prerequisites and dependency/contract overrides; update the affected existing task contracts and Foundation close so the external tasks cannot be skipped. Materialization runs in non-conflicting documentation waves, followed by one serialized main-thread manifest/index audit.

**Tech Stack:** Markdown task contracts, JSON materialization indexes, Python validation scripts, Git scoped diffs, repository atomic evidence/task gates.

---

No worktree or commit is created: the user requires preservation of the current dirty
worktree and explicitly forbids commit/push/reset/clean/stash/discard during this cycle.

## Story Shape Classification

- `shared_file_density`: high — one final controller owns the delta batch manifest and
  overlay; all other workers own distinct task files.
- `prereq_dependency_density`: high — snapshot → grant lifecycle adapter → annuity and
  activation → provider → HTTP are explicit chains.
- `be_fe_coupling`: medium — current work is task-contract documentation, while later
  High implementation crosses backend/API and final-close verification.
- `evidence_cost`: high — baseline-subtracted scope, dependency closure, serialization,
  independent plan/spec review and atomic gates remain mandatory.
- `chosen_runbook`: `P0-prereq-heavy-story`.

## File responsibility map

### Existing task contracts to modify

1. `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md` — generic lifecycle/rule seam.
2. `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md` — first rule-registry implementation contract.
3. `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md` — protected status input/CAS.
4. `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md` — client instruction state/activity service.
5. `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md` — source approval/activation.
6. `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md` — approval identity/evidence service.
7. `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md` — exact export carrier schema.
8. `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md` — current scoped read precedence.
9. `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md` — immutable fee-line snapshot in activity.
10. `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md` — consume reviewed snapshot only.
11. `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md` — strict V8 HTTP/provider adapter.
12. `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` — require delta external prerequisites and migration regression.

### New task contracts to create

13. `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01.md` — canonical reviewed fee-line snapshot parser.
14. `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01.md` — production read-only provider.
15. `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01.md` — obsolete-test semantic migration only.

### Serialized materialization controller to create last

16. `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01.md` — owns only:

- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-20260713-01.md`;
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/materialization/delta_overlay.json`;
- its validator, review and evidence under the same artifact family.

The controller must not modify the seven baseline materialization JSON files, the
historical materializer/validator, or the 197-row Foundation manifest.

## Explicit batch manifest

Each row below is one agent-owned task-file path. “Allowed edit” means the task contract
file itself plus that materialization task's artifacts; product allowlists are written
inside the resulting contract but are not edited now.

| # | Exact task-file path | Materialization closure | Runbook | Direct dependency correction |
| --- | --- | --- | --- | --- |
| 01 | `tasks/postdemo/v8/FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01.md` | Add exact lazy registry/rule-decision/replay/projector/error/TDD contract | `P0-prereq-heavy-story` | append + projection |
| 02 | `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md` | Freeze first `lifecycle_rules` registry implementation and CASE_OPENED only | `P0-prereq-heavy-story` | apply seam |
| 03 | `tasks/postdemo/v8/FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01.md` | Add five-carrier predicate, no-op semantics, exact 409 and CAS | `P0-prereq-heavy-story` | legacy projection |
| 04 | `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md` | Add exact service/transition/activity/idempotency/transaction contract | `P0-prereq-heavy-story` | recognize obligation + activity append |
| 05 | `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md` | Add CNIPA snapshot, interval, activation/replay/CAS/seed contract | `P0-prereq-heavy-story` | rate-book carrier |
| 06 | `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01.md` | Add DTO/canonical identity/evidence/hash/race contract | `P0-prereq-heavy-story` | F5 + DE register + DE review |
| 07 | `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01.md` | Freeze exact table/ORM/constraints/revision/SQLite tests | `P0-prereq-heavy-story` | rate-book carrier/global Alembic order |
| 08 | `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md` | Add scope precedence/as-of/current/error/query contract | `P0-prereq-heavy-story` | record service |
| 09 | `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01.md` | Create one pure canonical snapshot/parser task | `P0-single-lane-story` | DE review service |
| 10 | `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01.md` | Require snapshot/hash in immutable lifecycle activity payload | `P0-prereq-heavy-story` | fee-line snapshot + grant lifecycle rule |
| 11 | `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md` | Consume activity-bound reviewed lines; no guesses/draft | `P0-prereq-heavy-story` | snapshot + grant adapter + recognize |
| 12 | `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01.md` | Create one read-only production provider task | `P0-prereq-heavy-story` | activation + supported rate-rule tasks |
| 13 | `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md` | Add strict request/response/provider/error/no-write contract | `P0-prereq-heavy-story` | preview service + production provider |
| 14 | `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01.md` | Create one test-only post-HTTP semantic migration task | `P0-single-lane-story` | preview HTTP |
| 15 | `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` | Require all three external tasks and delta overlay/manifest validation | `P0-prereq-heavy-story` | migration + affected catalog tasks |
| 16 | `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01.md` | Create delta manifest/index, validate closure/graph/serialization and obtain independent review | `P0-prereq-heavy-story` | rows 01–15 materialized |

## Exact new-task contracts

### New task 09 — grant-notice fee-line snapshot

The task file must declare exactly one closure: add
`backend/app/modules/documents/grant_fee_lines.py` and
`backend/tests/test_v8_grant_notice_fee_line_snapshot.py`.

Its public immutable DTO/parser contract must cover:

- schema `FPMS_GRANT_NOTICE_FEE_LINES_V1`;
- exact source document ID, reviewed evidence-version ID and expected `sha256:<64>`;
- non-empty ordered lines containing fee name, positive unique year, finite positive amount
  with at most two decimal places, and exact ratio `0/0.7/0.85`;
- canonical JSON using UTF-8, sorted keys, compact separators and `allow_nan=False`;
- bare lowercase snapshot hash;
- extraction from the exact `GrantFeeLines` member of existing Document `extra_data`;
- strict duplicate-key/non-finite/extra-field/type rejection;
- no DB write, OCR, PDF parsing, rate lookup, eligibility decision or obligation.

Dependencies: `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`. The later grant lifecycle adapter
validates the referenced version is current FINAL/APPROVED and copies canonical snapshot
and hash into its activity payload.

### New task 12 — production estimate rate provider

The task file must own only:

- `backend/app/modules/fees/official_rate_book.py`;
- `backend/tests/test_v8_official_fee_estimate_rate_provider.py`;
- its task/evidence paths.

It freezes `SqlAlchemyOfficialFeeEstimateRateProvider(Session)` as a read-only
implementation of the existing provider protocol. It selects exactly one ACTIVE,
APPROVED, trusted OfficialRateBook effective on the caller date; resolves only explicitly
supported trigger/rate-rule rows; maps source provenance without lossy flattening; and
fails closed on absence, overlap, broken linkage, invalid source or unsupported trigger.
No API, calculation duplication, obligation, draft, activity, legacy fallback, flush or
commit is permitted.

Dependencies must enumerate rate-book activation and every rate-rule task actually
supported by the first provider implementation; “all rules” or an inferred wildcard is
invalid.

### New task 14 — legacy preview test migration

The task file must own only:

- `backend/tests/test_official_fee_preview_api.py`;
- its task/evidence paths.

After the strict V8 HTTP adapter passes, update only the obsolete test expectations from
legacy `trigger_event`/unlinked FeeRate fallback to explicit V8 context/date and verified
provider linkage. RED proves the old expectation conflicts with V8; GREEN proves the
strict route and no-fallback behavior. No product file or backward-compatibility path is
allowed.

## Existing-task materialization checklist

For every row 01–08, 10–11, 13 and 15, its owner performs these actions only:

- [ ] Read the approved delta spec and the exact current task file.
- [ ] Update Story Shape Classification and `chosen_runbook` where listed.
- [ ] Add an `Ultra Contract Freeze — 2026-07-13` section with exact callable/data/error/
      transaction/RED-GREEN behavior; do not copy broad rationale.
- [ ] Correct canonical dependencies, shared-file order, remaining follow-ups and
      allowlist/verification commands only when required by the approved contract.
- [ ] Preserve original exact closure and non-closure; if the delta reveals a second
      closure, link the new task rather than absorbing it.
- [ ] Keep implementation status `READY ... / NOT STARTED`; never mark product PASS.
- [ ] Run task structure and scoped diff checks; do not run product pytest, migrations,
      frontend builds, Playwright, release gate or repo-wide Ruff.
- [ ] Return the exact task path and a concise contract-delta summary to the lead.

## New-task materialization checklist

For rows 09, 12 and 14, each owner creates exactly its named task file containing:

- [ ] Status `READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-13 / NOT STARTED`.
- [ ] Program/wave/catalog classification: external Foundation prerequisite delta; it is
      not silently inserted into the immutable 283-row baseline catalog.
- [ ] Story classification, chosen runbook and one matching Task Contract Profile.
- [ ] Exact closure, explicit non-closure and remaining follow-up IDs.
- [ ] Canonical dependencies and shared ownership order.
- [ ] Exact product/test/task/artifact allowlist.
- [ ] RED, GREEN, scoped lint/format/diff, task gate and evidence validation commands.
- [ ] Caller-owned transaction and SQLite requirements where applicable.
- [ ] Done definition requiring independent review and atomic evidence.

## Wave order

Materialization is documentation-only, but ownership remains atomic. At most three child
workers run concurrently; the main thread performs serialized review/administration.

### Wave M1

- Row 01 — LC apply seam.
- Row 02 — CASE_OPENED registry contract.
- Row 03 — case update status gate.

Main thread verifies the three distinct task-file diffs and their mutual dependency order.

### Wave M2

- Row 04 — client instruction.
- Row 05 — rate-book activation.
- Row 06 — fee-reduction approval.

Main thread confirms no product/shared file was edited and DE review dependency is PASS.

### Wave M3

- Row 07 — PayList carrier.
- Row 08 — decision-gate read.
- Row 09 — new grant fee-line snapshot task.

Main thread freezes the new external-prerequisite identity and GLOBAL_ALEMBIC_HEAD order.

### Wave M4

- Row 10 — grant-notice lifecycle adapter.
- Row 11 — grant-year annuity obligation.
- Row 12 — new rate provider task.

Main thread validates `snapshot → grant adapter → annuity` and
`activation → provider` closure without cycles.

### Wave M5

- Row 13 — preview HTTP.
- Row 14 — new legacy-test migration task.
- Row 15 — Foundation close.

Main thread validates `provider → HTTP → test migration → Foundation close`.

### Wave M6 — serialized controller

Main thread materializes row 16 only after rows 01–15 are reviewed. It creates the delta
batch manifest and `delta_overlay.json`, then dispatches two read-only reviewers:

1. task-shape/contract/scope reviewer;
2. dependency/serialization/final-close reviewer.

The controller fixes findings and re-dispatches, maximum three review iterations.

## Delta overlay contract

`delta_overlay.json` must contain exactly:

- `baseline`: paths and SHA-256 of the original catalog, dependency index, serialization
  index and Foundation index; counts remain 283/197/86.
- `approved_delta_spec`: path and SHA-256.
- `external_prerequisites`: exactly the three new task IDs/paths, phase
  `foundation_external_prerequisite`, closure, dependencies and allowlists.
- `contract_overrides`: exactly the twelve affected existing product/close task IDs
  (rows 01–08, 10–11, 13, 15), with old/new dependency lists and task-file SHA-256.
- `serialization_overrides`: official-rate-book shared source chain, grant workflow chain,
  global Alembic chain and SQLite-global serialization decisions.
- `effective_close_requirements`: original 197 Foundation tasks plus the three external
  tasks; no claim that the immutable Foundation manifest itself contains 200 rows.
- `generated_at` omitted; content is deterministic and hashable.

The delta batch manifest lists rows 01–16 and explicitly states that it is a planning/
contract materialization manifest, not authorization to implement more than one task per
worker. Original materialization artifacts remain untouched.

## Shared ownership and verification

- Task-file edits are conflict-free because every worker owns a distinct path.
- `backend/app/modules/fees/official_rate_book.py` later serializes activation before
  provider; no two High workers may edit it concurrently.
- `backend/app/modules/cases/lifecycle_rules.py` later serializes CASE_OPENED and every
  subsequent event rule in original order.
- Grant snapshot, grant lifecycle adapter and annuity service are dependency-ordered even
  though their product files differ.
- PayList migration remains under GLOBAL_ALEMBIC_HEAD; all Alembic and SQLite writes are
  main-thread serialized.
- Preview API/shared schemas remain serialized with the existing fees API chain.
- Materialization verification is structure/hash/diff only; product RED/GREEN begins only
  after switching back to High.

## Done definition

- [ ] All 16 exact task-file paths exist and pass atomic task-structure checks.
- [ ] The twelve existing affected contracts preserve one closure and carry the approved
      Ultra delta without product status claims.
- [ ] The three new external prerequisite tasks have exact allowlists, dependencies,
      TDD commands and non-closures.
- [ ] Foundation close explicitly requires all three external prerequisite task gates.
- [ ] Delta manifest and deterministic overlay validate against unchanged baseline hashes.
- [ ] Dependency graph is acyclic and all shared-file chains are serialized.
- [ ] Two independent materialization reviews approve with no blocking finding.
- [ ] Controller evidence contains results, summary, scoped diff and dirty-baseline files;
      its task gate and atomic evidence validation pass.
- [ ] No product source/test/schema/UI was modified and no product test/release gate ran.
- [ ] Lead reports `READY FOR HIGH DEVELOPMENT` and requests the user switch to High and
      Resume Goal; it does not silently switch models or begin implementation.
