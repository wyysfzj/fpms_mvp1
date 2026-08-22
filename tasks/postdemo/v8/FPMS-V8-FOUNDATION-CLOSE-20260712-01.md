# FPMS-V8-FOUNDATION-CLOSE-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `17. Wave 8 — real paths and release close`
Catalog ordinal: `280`
Executor role: Independent Reviewer / explorer

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md`
- Source catalog line: `825`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: Contract/gate test fails on missing evidence or coverage.
- GREEN expectation: Exact audit/E2E/gate commands pass and any failure becomes a new task.

## Exact Closure Slice

Foundation-only QA close: verify every other foundation task/evidence and inherited regression mapping, classify every omitted customer lane as unresolved/confirmed-pending/activated/prior-PASS, and publish residuals without product fixes or any repo-wide/release check. It must not claim full V8 completion.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Delta Close Contract — 2026-07-13

- The materialization controller
  `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` must be PASS with its
  required atomic evidence and independent reviews before this close runs. Its deterministic
  `delta_overlay.json` validator is a mandatory pre-close gate.
- The original `tasks/batches/FPMS-POSTDEMO-V8-FOUNDATION-20260712-01.md`, its
  `foundation_manifest_index.json`, and the baseline catalog/dependency/serialization
  materialization remain immutable. Their recorded SHA-256 values and exact counts remain
  `283 = 197 foundation + 86 deferred`; this task must not regenerate or rewrite them.
- The delta validator must verify the baseline hashes and counts and the exact task-file
  hashes, dependency overrides and serialization overrides for these twelve existing tasks:
  `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`,
  `FPMS-V8-LC-CASE-OPENED-20260712-01`,
  `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`,
  `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`,
  `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`,
  `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`,
  `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`,
  `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`,
  `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`,
  `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`,
  `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`, and
  `FPMS-V8-FOUNDATION-CLOSE-20260712-01`.
- Effective Foundation close is the immutable original 197-task set, with this close task
  handled only by the existing self-pending/skip-self mechanism, plus the task gates and
  required evidence for all three external prerequisites listed below. The external tasks
  do not become rows in the immutable Foundation manifest, and no artifact may claim that
  manifest has 200 rows.
- The official-fee preview legacy-test migration is a mandatory regression, not an optional
  alignment: its task gate/evidence and `backend/tests/test_official_fee_preview_api.py`
  must pass before the existing Foundation checks continue.

## Ultra Delta-2 Close Contract — 2026-07-14

- This contract is additive after the accepted 2026-07-13 delta. Both materialization
  controllers, their required atomic evidence and independent reviews must be PASS before
  this close runs: parent controller
  `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` and delta-2 controller
  `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`.
- Both deterministic overlay validators are mandatory. The delta-2 validator must fail
  closed on drift in any immutable baseline parent hash or accepted delta-1 manifest/overlay
  hash, as well as wrong counts, task-hash drift, missing/duplicate rows, unresolved
  dependencies, cycles, shared-owner inversion or a Foundation/Full/Release bypass.
- Effective Foundation close requirements are exactly the immutable 197 Foundation task
  IDs plus the three delta-1 external prerequisites plus the two delta-2 external
  prerequisites: `197 + 3 + 2 = 202`. The immutable Foundation manifest remains exactly
  197 rows; no manifest, overlay, audit or evidence may claim that it has 202 rows.
- All five external prerequisites below require their own task gates, evidence gates and
  independent reviews. They remain additive effective-graph nodes outside the immutable
  Foundation manifest and do not rewrite accepted PASS history.
- Task 75, `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`, and
  `FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01` remain mandatory and unchanged.
  Foundation close cannot pass until both task/evidence gates pass; delta-2 does not absorb,
  move, duplicate or weaken either closure.
- Original Foundation real-path proof remains mandatory: the live fixture retains more
  than 100 activities, all three lanes, gates, conflicts and unverified facts; lifecycle
  overlay E2E uses real login/API/Vite without route fulfillment and proves the three lanes,
  stable three-page cursor and the delta-2 29 composite gate identities; PayList boundary
  E2E still proves internal export is not official upload and payment remains distinct.
  SQLite fixture writes stay globally serialized and both real UI E2E tasks use
  `--workers=1`.

## Ultra Delta-3 Close Contract — 2026-07-14

- This contract is additive after the accepted delta-1 and delta-2 overlays. The delta-3
  supplemental manifest and controller task are authoritative for this override. The
  delta-3 controller
  `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01` must be PASS with its
  task gate, required atomic evidence and two independent reviews before this close runs.
- The cumulative delta-3 validator at
  `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
  is the mandatory current pre-close overlay validator. It must hash-lock the immutable
  baseline and accepted delta-1/delta-2 parents, prove each latest-parent exact
  `task_sha256` before Status-sentinel normalization, preserve the RAW rejected-successor
  exception as the only exception, and fail closed on any other non-Status drift. The old
  delta validators and their evidence remain historical read-only inputs and are neither
  rerun nor sufficient for this close.
- Effective Foundation is exactly 204 unique product task IDs: the immutable 197
  Foundation IDs plus three delta-1, two delta-2 and two delta-3 external prerequisites,
  `197 + 3 + 2 + 2 = 204`. The immutable Foundation manifest remains exactly 197 rows;
  no manifest, overlay, audit or evidence may claim that it has 204 rows.
- All seven external product prerequisites below require their own task gates, atomic
  evidence gates and independent reviews. G1, G2 and all three materialization controllers
  are audit-only governance gates outside both the 204-task Foundation product set and the
  290-node effective product graph.
- Foundation close directly requires the delta-3 controller, G1 structural JSONL gate,
  G2 concurrent validator, RAW registration guard and external-submission role allowlist
  task/evidence gates. Task 75, the direct-status static gate, every delta-1/delta-2
  prerequisite and all original Foundation regressions remain mandatory and unchanged.
- This close runs single-lane with no peers. Atomic evidence validation uses the repository
  wrapper without `--manifest` or `--concurrent-task`; SQLite-writing checks and shared-file
  verification remain serialized. Foundation close does not run the release gate.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
- `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
- `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
- `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
- `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
- `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
- `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
- `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
- `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`
- `FPMS-V8-LC-CONTRACTS-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
- `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`
- `FPMS-V8-LC-CASE-OPENED-20260712-01`
- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`
- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-RECORDED-20260712-01`
- `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
- `FPMS-V8-LC-ACCEPTANCE-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-PRELIMINARY-EXAMINATION-STARTED-20260712-01`
- `FPMS-V8-LC-PRELIMINARY-EXAMINATION-PASSED-20260712-01`
- `FPMS-V8-LC-RECTIFICATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-PUBLICATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-SUBSTANTIVE-EXAMINATION-STARTED-20260712-01`
- `FPMS-V8-LC-OA-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`
- `FPMS-V8-LC-REEXAMINATION-STARTED-20260712-01`
- `FPMS-V8-LC-GRANT-REGISTRATION-NOTICE-RECORDED-20260712-01`
- `FPMS-V8-LC-GRANT-ANNOUNCEMENT-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-REGISTER-STATUS-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-REJECTION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-WITHDRAWAL-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-ABANDONMENT-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-TERMINATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-EXPIRY-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-INVALIDATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-APPLICATION-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- `FPMS-V8-LC-PATENT-RIGHT-RESTORATION-CONFIRMED-20260712-01`
- `FPMS-V8-DE-CONTRACTS-20260712-01`
- `FPMS-V8-DE-REGISTER-VERSION-20260712-01`
- `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`
- `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`
- `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`
- `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01`
- `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01`
- `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
- `FPMS-V8-DE-REVIEW-API-20260712-01`
- `FPMS-V8-DE-ATTACHMENT-EVIDENCE-READ-PROJECTION-20260712-01`
- `FPMS-V8-DE-REVIEW-FE-ADAPTER-20260712-01`
- `FPMS-V8-DE-REVIEW-UI-20260712-01`
- `FPMS-V8-CASE-CREATE-STATUS-INPUT-GATE-20260712-01`
- `FPMS-V8-CASE-UPDATE-STATUS-INPUT-GATE-20260712-01`
- `FPMS-V8-CASE-CREATE-STATUS-UI-GATE-20260712-01`
- `FPMS-V8-CASE-EDIT-STATUS-UI-GATE-20260712-01`
- `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
- `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
- `FPMS-V8-DOCUMENT-SEMANTICS-EVENT-ADAPTER-20260712-01`
- `FPMS-V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-20260712-01`
- `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
- `FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`
- `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
- `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
- `FPMS-V8-OA-PREPARED-DOCUMENT-ACTIVITY-20260712-01`
- `FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01`
- `FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-OA-REPLY-DATE-RECEIPT-PROJECTION-20260712-01`
- `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
- `FPMS-V8-OA-NONCOPYABLE-APPENDIX-POLICY-20260712-01`
- `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01`
- `FPMS-V8-GRANT-FEE-DONE-NO-GRANTED-20260712-01`
- `FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01`
- `FPMS-V8-PRELIMINARY-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-PRELIMINARY-PASSED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-RECTIFICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-PUBLICATION-NOTICE-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-SUBSTANTIVE-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-REEXAMINATION-STARTED-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-REJECTION-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-WITHDRAWAL-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-ABANDONMENT-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-RESTORATION-EVIDENCE-API-ADAPTER-20260712-01`
- `FPMS-V8-FORMAT-LETTER-REAL-TEMPLATE-SET-20260712-01`
- `FPMS-V8-FORMAT-LETTER-CONTEXT-20260712-01`
- `FPMS-V8-FORMAT-LETTER-RENDER-20260712-01`
- `FPMS-V8-FORMAT-LETTER-ARCHIVE-20260712-01`
- `FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01`
- `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-LIST-API-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-CASEEDIT-UI-20260712-01`
- `FPMS-V8-CASE-CREATE-FEE-REDUCTION-API-20260712-01`
- `FPMS-V8-CASE-UPDATE-FEE-REDUCTION-API-20260712-01`
- `FPMS-V8-CASE-CREATE-FEE-REDUCTION-UI-20260712-01`
- `FPMS-V8-CASE-EDIT-FEE-REDUCTION-UI-20260712-01`
- `FPMS-V8-FO-CONTRACTS-20260712-01`
- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- `FPMS-V8-FO-PREVIEW-ESTIMATE-20260712-01`
- `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
- `FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01`
- `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- `FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
- `FPMS-V8-FO-INSTRUCTION-FE-ADAPTER-20260712-01`
- `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
- `FPMS-V8-FO-OBLIGATION-DETAIL-HTTP-20260712-01`
- `FPMS-V8-FO-OBLIGATION-DETAIL-FE-ADAPTER-20260712-01`
- `FPMS-V8-FO-PREPARE-DRAFT-20260712-01`
- `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`
- `FPMS-V8-GENERIC-FEE-DRAFT-ACTIVITY-ADAPTER-20260712-01`
- `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-API-ADAPTER-20260712-01`
- `FPMS-V8-GENERIC-FEE-DRAFT-OBLIGATION-FE-ADAPTER-20260712-01`
- `FPMS-V8-FEE-DRAFT-OBLIGATION-UI-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`
- `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- `FPMS-V8-ANNUITY-DRAFT-OBLIGATION-ADAPTER-20260712-01`
- `FPMS-V8-PAYLIST-CREATE-FEE-ACTIVITY-ADAPTER-20260712-01`
- `FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
- `FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01`
- `FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-20260712-01`
- `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
- `FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01`
- `FPMS-V8-ANNUITY-PAYABLE-AMOUNT-RULE-20260712-01`
- `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
- `FPMS-V8-ANNUITY-LATE-FEE-RULE-20260712-01`
- `FPMS-V8-PCT-FEE-POLICY-20260712-01`
- `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
- `FPMS-V8-LAYOUT-REEXAMINATION-FEE-RULE-20260712-01`
- `FPMS-V8-LAYOUT-RESTORATION-FEE-RULE-20260712-01`
- `FPMS-V8-LAYOUT-BIBLIOGRAPHIC-CHANGE-FEE-RULE-20260712-01`
- `FPMS-V8-LAYOUT-EXTENSION-FEE-RULE-20260712-01`
- `FPMS-V8-LAYOUT-NONVOLUNTARY-LICENSE-FEE-RULE-20260712-01`
- `FPMS-V8-LAYOUT-REMUNERATION-ADJUDICATION-FEE-RULE-20260712-01`
- `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-FEE-RULE-20260712-01`
- `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-FEE-RULE-20260712-01`
- `FPMS-V8-OPEN-LICENSE-ANNUITY-REDUCTION-RULE-20260712-01`
- `FPMS-V8-IC-LAYOUT-REGISTRATION-FILED-OBLIGATION-20260712-01`
- `FPMS-V8-IC-LAYOUT-REEXAM-REQUEST-OBLIGATION-20260712-01`
- `FPMS-V8-IC-LAYOUT-RIGHT-RESTORATION-REQUEST-OBLIGATION-20260712-01`
- `FPMS-V8-IC-LAYOUT-BIBLIOGRAPHIC-CHANGE-SUBMISSION-OBLIGATION-20260712-01`
- `FPMS-V8-IC-LAYOUT-EXTENSION-REQUEST-OBLIGATION-20260712-01`
- `FPMS-V8-IC-LAYOUT-NONVOLUNTARY-LICENSE-REQUEST-OBLIGATION-20260712-01`
- `FPMS-V8-IC-LAYOUT-REMUNERATION-ADJUDICATION-REQUEST-OBLIGATION-20260712-01`
- `FPMS-V8-PATENT-TERM-COMPENSATION-REQUEST-OBLIGATION-20260712-01`
- `FPMS-V8-COMPENSATION-PERIOD-ANNUITY-OBLIGATION-20260712-01`
- `FPMS-V8-OPEN-LICENSE-ANNUITY-OBLIGATION-ADAPTER-20260712-01`
- `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`
- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- `FPMS-V8-OFFICIAL-FEE-CATEGORY-CORRECTION-20260712-01`
- `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- `FPMS-V8-PAYLIST-INTERNAL-EXPORT-SERVICE-20260712-01`
- `FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01`
- `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`
- `FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`
- `FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
- `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`
- `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`
- `FPMS-V8-DECISION-GATE-LIST-API-20260712-01`
- `FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
- `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
- `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
- `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
- `FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
- `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
- `FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01`
- `FPMS-V8-OVERLAY-CONTRACTS-20260712-01`
- `FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01`
- `FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01`
- `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`
- `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`
- `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`
- `FPMS-V8-OVERLAY-HTTP-20260712-01`
- `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`
- `FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01`
- `FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01`
- `FPMS-V8-OVERLAY-CENTER-LANE-UI-20260712-01`
- `FPMS-V8-OVERLAY-DOCUMENT-LANE-UI-20260712-01`
- `FPMS-V8-OVERLAY-FEE-LANE-UI-20260712-01`
- `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
- `FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
- `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01`
- `FPMS-V8-LIVE-FIXTURE-20260712-01`
- `FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01`
- `FPMS-V8-PAYLIST-BOUNDARY-REAL-UI-E2E-20260712-01`
- `FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01`

### External, gate and inherited prerequisites

Audit-only controller gates:

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`

These three controller IDs are audit gates only. They are not rows in the immutable
197-task Foundation manifest, are not included in the effective 204-task Foundation
requirement, and are not product nodes in the effective 290-node dependency graph.

Audit-only repository governance gates:

- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` (`G1`)
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` (`G2`)

G1 and G2 require their own task gates, atomic evidence and independent acceptance in
that order. They are governance prerequisites and must never be counted as product tasks.

External product prerequisites:

- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`
- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`

- Approved source dependency cell (verbatim): all other foundation task gates, catalog coverage gate

### Shared ownership serialization

- `FOUNDATION_MANIFEST_OWNERSHIP` order key `1`; project this order only across owners present in the active manifest.
- `FOUNDATION_SHARED_VERIFICATION` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md`
- `docs/reviews/fpms_postdemo_v8_foundation_close_audit_20260712.md`
- `backend/tests/test_v8_foundation_close_contract.py`
- `artifacts/FPMS-V8-FOUNDATION-CLOSE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Foundation close is a single lane. Every `scripts/atomic_evidence_validate.py` command
  omits `--manifest` and `--concurrent-task`.
- Follow the frozen foundation/full close order; QA tasks report failures and never repair product code.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_foundation_close_contract.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `for task in FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01 FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01 FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01; do ./scripts/task_validate.sh "$task"; done`
- `for task in FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01 FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01 FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01; do python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
- `for task in REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01 REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01; do ./scripts/task_validate.sh "$task"; python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `for task in FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01 FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01 FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01 FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01 FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01 FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01; do ./scripts/task_validate.sh "$task"; done`
- `for task in FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01 FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01 FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01 FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01 FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01 FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01; do python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `for task in FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01 FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01; do ./scripts/task_validate.sh "$task"; done`
- `for task in FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01 FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01; do python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `cd backend && .venv/bin/pytest -q tests/test_official_fee_preview_api.py`
- `for task in $(python3 -c "import json; print(*json.load(open('artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/materialization/foundation_manifest_index.json'))['task_ids'])"); do [ "$task" = "FPMS-V8-FOUNDATION-CLOSE-20260712-01" ] || ./scripts/task_validate.sh "$task"; done`
- `./scripts/task_validate.sh FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01`
- `python3 scripts/v8_catalog_manifest_gate.py --phase foundation --manifest tasks/batches/FPMS-POSTDEMO-V8-FOUNDATION-20260712-01.md --self-pending FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- `cd backend && .venv/bin/pytest -q tests/test_v8_foundation_close_contract.py`
- `git diff --check -- docs/reviews/fpms_postdemo_v8_foundation_close_audit_20260712.md backend/tests/test_v8_foundation_close_contract.py tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- Evidence validation (single lane; no manifest or peer arguments): `python3 scripts/atomic_evidence_validate.py FPMS-V8-FOUNDATION-CLOSE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FOUNDATION-CLOSE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FOUNDATION-CLOSE-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority and start gate

- Authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`,
  its 34-row supplemental manifest, and row `30 / M4-H / FOUNDATION-CLOSE`.
- Risk is `HIGH`; `chosen_runbook: P0-prereq-heavy-story` is latest-wins. Delta-1/2/3
  close overlays remain immutable history, and the existing Allowed Files list is unchanged.
- The Delta-4 controller
  `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01` must first reach
  independent accepted PASS with its task gate, Evidence 1.1 and both required review axes.
- Before this close starts, every Delta-1/2/3 controller and governance gate inherited
  above must still be accepted PASS; no older overlay or controller is superseded away.

### Exact effective Foundation acceptance set

- Effective Foundation is exactly 216 unique product nodes:
  `197 immutable Foundation + 7 Delta-1/2/3 external prerequisites + 12 Delta-4 products`.
- The immutable Foundation manifest remains exactly 197 rows. The seven earlier external
  prerequisites and twelve Delta-4 additions are effective-graph nodes outside that file;
  controllers, overlays, reviews and governance gates are audit-only and never product-counted.
- All 216 product nodes must independently PASS their exact task contract, targeted
  verification, repository task gate, Evidence 1.1 scope/evidence gate and independent
  zero-finding review. Historical PASS remains accepted only where AGENTS.md permits it.
- All Delta-1–4 product additions, existing-task overlays/re-freezes, controller rows,
  structural/concurrent evidence gates and inherited Foundation audit/regression gates
  must have their separate required verdicts and evidence; no aggregate verdict substitutes
  for any row or task.
- Delta-4 rows 01–33 retain separate `APPROVED/P0=P1=P2=0` materialization verdicts, and
  row 34 retains independent task-shape/scope plus graph/domain/fail-closed approvals.

### Mandatory cumulative graph and ordering gate

- Run the accepted cumulative validator only after the Delta-4 controller PASS:
  `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/analysis/
  validate_delta4_overlay.py`.
- It must PASS immutable parent hashes and normalized anchors and prove exactly 302 unique
  product nodes, 216 Foundation, 86 deferred, zero unresolved dependency and zero cycle.
- It must also prove all twelve Delta-4 closures, seventeen re-freezes, allowlists and
  dependencies; exact migration heads; shared-owner order; SQLite queue; and immutable
  `Foundation → Full → item-to-slice ledger → final close → release` order.
- Any count, hash, row, dependency, verdict, evidence, allowlist, shared-owner, migration,
  serialization or close-order drift fails this close closed. Never infer, repair, waive,
  recategorize or silently omit a missing prerequisite.

### Serialized close execution

- Product/shared-file execution and verification must respect every accepted dependency
  order with no concurrent shared owner. SQLite/Alembic writers use
  `GLOBAL_SQLITE_SERIAL_QUEUE`, maximum writer one; real UI close checks retain their
  accepted single-worker constraints.
- This independent close remains one lane and cannot approve its own task. It reports
  failures only; it must not repair product code, weaken tests or absorb another closure.
- The inherited real-path, regression, catalog coverage and self-pending/skip-self checks
  remain mandatory after every prerequisite above passes.

### Materialization and close non-execution

- This materialization changes only Status and this EOF appendix. It does not execute
  Foundation close, initialize this close's evidence, run product tests, edit audit/test/
  product files, change the allowlist, or rewrite any inherited overlay.
- Do not run repo-wide Ruff/pytest, frontend build, broad Playwright, Full activation,
  item-to-slice/final close or the release gate early. The release gate remains last.
- Only atomic `check-task` runs now; all Foundation acceptance commands remain deferred
  until the controller and every prerequisite above are durably accepted PASS.
