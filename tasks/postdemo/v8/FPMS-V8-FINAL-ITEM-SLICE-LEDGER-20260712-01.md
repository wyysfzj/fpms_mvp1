# FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `17. Wave 8 — real paths and release close`
Catalog ordinal: `282`
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
- Delta-3 supplemental materialization row: `11`
- Source catalog line: `827`
- Expected manifest phase: `deferred`
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

Full-manifest-only independent map of every P0/P1 row to slices/evidence/gates/migration/regression/residual; no product fix and no gated residual.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Delta-3 Cumulative Full-Ledger Contract — 2026-07-14

- This additive contract narrows the existing independent full-ledger QA closure only. It
  does not authorize a product fix, change the explicit non-closure or expand the existing
  product/test/review/artifact allowlist.
- The full item-to-slice ledger must preserve the immutable `283`-row catalog and immutable
  `197`-row Foundation manifest as distinct baseline counts. Delta-1 adds three product
  external nodes, delta-2 adds two and delta-3 adds two, so the required claims are exactly
  `290` effective product-graph nodes, `204` effective Foundation product requirements and
  `86` deferred product tasks. It is prohibited to claim that the catalog has 290 rows, that
  the Foundation manifest has 204 rows or that any governance gate changes the deferred 86.
- All three controller/overlay families, all seven product external prerequisites and G1/G2
  must have their own ledger evidence entries. Every entry must map its exact closure,
  evidence, task/evidence gate result and residual gap; no representative catalog row,
  aggregate program PASS or adjacent implementation slice may stand in for any entry.

| Required ledger entry and classification | Exact closure mapping | Required evidence | Required gate mapping | Required residual |
| --- | --- | --- | --- | --- |
| Delta-1 controller/overlay — audit-only: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` and `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/materialization/delta_overlay.json` | Accepted delta-1 overrides and three product externals validate against immutable 283/197/86 parents | Controller evidence, independent reviews, overlay SHA-256 and historical validator command/output/return code | Controller task gate and atomic evidence gate PASS; historical validator evidence accepted as a cumulative-validator input | `None`; never a product slice or count |
| Delta-1 product external: `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01` | Canonical reviewed grant-notice fee-line snapshot/parser prerequisite | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS | `None` |
| Delta-1 product external: `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` | Production read-only official-fee estimate rate provider prerequisite | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS | `None` |
| Delta-1 product external: `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01` | Obsolete official-fee preview test semantic migration prerequisite | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS | `None` |
| Delta-2 controller/overlay — audit-only: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01` and `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01/materialization/delta_overlay.json` | Accepted delta-2 overrides and two product externals validate against immutable parents and accepted delta-1 hashes | Controller evidence, independent reviews, overlay SHA-256 and historical validator command/output/return code | Controller task gate and atomic evidence gate PASS; historical validator evidence accepted as a cumulative-validator input | `None`; never a product slice or count |
| Delta-2 product external: `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01` | One-test lifecycle registry semantic migration prerequisite | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS | `None` |
| Delta-2 product external: `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01` | Fail-closed raw-attachment evidence-role prerequisite behind both delta-3 guards | Its own required atomic evidence, both real-member guard regressions and independent review | Its own task gate and atomic evidence gate PASS after both guards PASS | `None` |
| Delta-3 controller/cumulative overlay — audit-only: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01` and `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/materialization/delta3_overlay.json` | Hash-lock immutable parents, prove latest-parent task hashes before Status normalization and validate the closed, acyclic 290/204/86 cumulative graph | Controller evidence, two independent reviews, cumulative overlay SHA-256 and `analysis/validate_delta3_overlay.py` command/output/return code | Controller task gate, atomic evidence gate and current cumulative validator PASS | `None`; never a product slice or count |
| Delta-3 product external: `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` | Explicit registration role/state matrix keeps RAW at DRAFT-only and future roles fail closed before transaction access | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS | `None` |
| Delta-3 product external: `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` | Explicit nine-role external-submission positive set rejects RAW/future roles and CAS-locks exact role | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS | `None` |
| G1 — audit-only: `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` | Structural JSONL lint/test success validation for the repository task gate | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS before G2 | `None`; never a product slice or count |
| G2 — audit-only: `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` | Common-manifest peer-ownership proof and isolated-clone atomic evidence wrapper | Its own required atomic evidence and independent review | Its own task gate and atomic evidence gate PASS after G1 | `None`; never a product slice or count |

- The three overlay/controller rows must cite their exact artifact families and overlay paths.
  Delta-1/delta-2 historical validator outputs, return codes and SHA-256 values remain
  read-only evidence inputs; they are not rerun or sufficient for the current close. The
  cumulative delta-3 validator at
  `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
  must record its output, return code and validated overlay SHA-256. Missing output, a hash
  mismatch, unresolved reference, cycle, wrong count or skipped external/audit gate is a
  blocking residual and forbids ledger PASS.
- Decision-gate coverage must trace the approved 29-entry composite identity through
  overlay contracts, decision-gate join, keyset revision, HTTP, FE adapter, gates/warnings
  UI, cursor UI, live fixture, real UI E2E and Full activation. Overlay evidence must prove
  seven `case:{case_id}` requests plus `form-001..form-022`; Full activation evidence must
  independently prove seven `GLOBAL` non-legacy requests plus `form-001..form-022`.
  `ALL-22` may appear only as resolved fallback provenance, and no consumer may deduplicate
  by gate code instead of `(gate_code, requested_scope_key)`.
- The close-audit shared file retains order key `1` and independent Reviewer ownership.
  This ledger reports any missing mapping, evidence, gate or residual as a new task; it
  never repairs product code or absorbs the final-close slice.

## Dependencies

### Canonical V8 task dependencies

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
- `FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01`
- `FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01`
- `FPMS-V8-PATENT-REGISTER-EVIDENCE-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-ACCEPTED-DISPATCH-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-REVIEW-FE-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-EVIDENCE-REVIEW-UI-20260712-01`
- `FPMS-V8-APPLICATION-AUTO-DRAFT-POLICY-20260712-01`
- `FPMS-V8-GRANT-YEAR-AUTO-DRAFT-POLICY-20260712-01`
- `FPMS-V8-FUTURE-ANNUITY-AUTO-DRAFT-POLICY-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01`
- `FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01`
- `FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01`
- `FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01`
- `FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01`
- `FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01`
- `FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01`
- `FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01`
- `FPMS-V8-OUT-001-RECTIFICATION-REPLY-20260712-01`
- `FPMS-V8-OUT-002-FIRST-OA-STATEMENT-20260712-01`
- `FPMS-V8-OUT-003-EARLY-PUBLICATION-20260712-01`
- `FPMS-V8-OUT-004-EXAM-REQUEST-20260712-01`
- `FPMS-V8-OUT-005-WITHDRAWAL-20260712-01`
- `FPMS-V8-OUT-006-ABANDONMENT-20260712-01`
- `FPMS-V8-OUT-007-BIBLIOGRAPHIC-CHANGE-20260712-01`
- `FPMS-V8-OUT-008-REEXAMINATION-REQUEST-20260712-01`
- `FPMS-V8-OUT-009-VOLUNTARY-RECTIFICATION-20260712-01`
- `FPMS-V8-OUT-010-RIGHT-RESTORATION-20260712-01`
- `FPMS-V8-OUT-011-REEXAM-INVALIDATION-STATEMENT-20260712-01`
- `FPMS-V8-OUT-012-REEXAMINATION-RECTIFICATION-20260712-01`
- `FPMS-V8-OUT-013-PAPER-TO-ELECTRONIC-20260712-01`
- `FPMS-V8-OUT-014-FEE-REDUCTION-REQUEST-20260712-01`
- `FPMS-V8-OUT-015-TRANSLATION-CORRECTION-20260712-01`
- `FPMS-V8-OUT-016-PPH-REQUEST-20260712-01`
- `FPMS-V8-OUT-017-INVENTION-VOLUNTARY-AMENDMENT-20260712-01`
- `FPMS-V8-OUT-018-TIME-EXTENSION-20260712-01`
- `FPMS-V8-OUT-019-SECOND-OA-STATEMENT-20260712-01`
- `FPMS-V8-OUT-020-THIRD-OA-STATEMENT-20260712-01`
- `FPMS-V8-OUT-021-FOURTH-OA-STATEMENT-20260712-01`
- `FPMS-V8-OUT-022-FILE-COPY-REQUEST-20260712-01`
- `FPMS-V8-LEGACY-STATE-PREFLIGHT-20260712-01`
- `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`
- `FPMS-V8-LEGACY-DOCUMENT-EVIDENCE-IMPORT-20260712-01`
- `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`
- `FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
- `FPMS-V8-DUAL-READ-RECONCILIATION-20260712-01`
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

### External, gate and inherited prerequisites

Audit-only materialization and repository-governance gates:

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` (`G1`)
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` (`G2`)

These five tasks require their own task/evidence gates and independent acceptance. They
are audit-only evidence and are excluded from the immutable 283-row catalog, the effective
290-node product graph and the effective 204-product-task Foundation requirement.

External product prerequisites:

- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`
- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`

- Approved source dependency cell (verbatim): full manifest activation, all catalog product-task gates

### Shared ownership serialization

- `docs/reviews/fpms_postdemo_v8_mitigation_close_audit_20260712.md` order key `1`; project this order only across owners present in the active manifest.
- `FULL_SHARED_VERIFICATION` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md`
- `docs/reviews/fpms_postdemo_v8_mitigation_close_audit_20260712.md`
- `backend/tests/test_v8_final_item_slice_ledger.py`
- `artifacts/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- This ledger is a single declared lane. Every atomic evidence validation uses the G2
  repository wrapper `scripts/atomic_evidence_validate.py` without `--manifest` or
  `--concurrent-task`; single-lane execution does not authorize direct external-helper use.
- Follow the frozen Foundation to Full to ledger to final-close order; QA tasks report
  failures and never repair product code. The existing release gate remains last and is
  not run, moved, duplicated or weakened by this task.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_final_item_slice_ledger.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `for task in FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01 FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01 FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01 REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01 REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01; do ./scripts/task_validate.sh "$task"; python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `for task in FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01 FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01 FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01 FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01 FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01 FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01; do ./scripts/task_validate.sh "$task"; python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
- `./scripts/task_validate.sh FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `cd backend && .venv/bin/pytest -q tests/test_v8_final_item_slice_ledger.py`
- `cd backend && .venv/bin/ruff check --fix tests/test_v8_final_item_slice_ledger.py && .venv/bin/ruff format tests/test_v8_final_item_slice_ledger.py && .venv/bin/ruff check tests/test_v8_final_item_slice_ledger.py`
- `git diff --check -- docs/reviews/fpms_postdemo_v8_mitigation_close_audit_20260712.md backend/tests/test_v8_final_item_slice_ledger.py tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01`
- Evidence validation (single declared lane; no manifest or peer arguments): `python3 scripts/atomic_evidence_validate.py FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01` pass. Only then may this task be reported PASS.

The final ledger must also contain all three overlay/controller audit entries, all seven
product external entries and both G1/G2 audit entries above; record all three overlay hashes
and validator evidence while treating only the cumulative delta-3 validator as the current
sufficient overlay gate; prove effective product graph `290`, effective Foundation `204`
and deferred `86` without rewriting the immutable `283`/`197` baselines or counting any
controller/G1/G2 as product; and preserve the full 29-entry decision-gate
propagation/activation evidence. Any omitted prerequisite, count conflation, direct-helper
validation, representative-row substitution or premature release execution blocks PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins count and authority boundary

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, especially lines 797–842 and 919–941; supplemental authority is row `32 / M4-H / FINAL-LEDGER` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work, Full activation and ledger evidence remain `NOT STARTED`. `chosen_runbook: P0-prereq-heavy-story` remains authoritative.
- Preserve the immutable source catalog at exactly `283` rows and the immutable Foundation manifest at exactly `197` rows. Never relabel either immutable baseline with an effective count.
- Delta-4 adds exactly 12 Foundation product nodes to the prior `290/204/86` graph, producing exactly `302` effective product nodes, `216` effective Foundation requirements and `86` deferred product tasks.
- The 17 existing-task re-freezes, all controller/review/overlay work, this ledger and every governance gate are audit-only lineage and add zero product or Foundation nodes.

### Twelve additive Delta-4 product nodes

1. `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01`
2. `FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01`
3. `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01`
4. `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01`
5. `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01`
6. `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01`
7. `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01`
8. `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01`
9. `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01`
10. `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`
11. `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01`
12. `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01`

### Seventeen existing-task re-freezes

1. `FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01`
2. `FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01`
3. `FPMS-V8-DE-REVIEW-API-20260712-01`
4. `FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
5. `FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01`
6. `FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01`
7. `FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
8. `FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01`
9. `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`
10. `FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01`
11. `FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01` — changed-mechanism recovery only
12. `FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
13. `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01`
14. `FPMS-V8-PCT-FEE-POLICY-20260712-01`
15. `FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
16. `FPMS-V8-DECISION-GATE-LIST-API-20260712-01`
17. `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01`

### Four cumulative controller and overlay families

- Delta-1: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01` with `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/materialization/delta_overlay.json`.
- Delta-2: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01` with `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01/materialization/delta_overlay.json`.
- Delta-3: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01` with `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/materialization/delta3_overlay.json`.
- Delta-4: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01` with `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/analysis/cumulative_delta4_overlay.json`.
- Each family is an audit-only gate and must carry its own accepted controller evidence, independent review, deterministic overlay/hash/validator evidence, task gate, atomic evidence gate and explicit residual; no family is counted as product.

### Exact ledger acceptance and non-closure

- Every one of the 302 effective product nodes, including each D4 addition and each re-frozen catalog task, receives its own exact closure/slice mapping, evidence path and latest required results/logs, independent verdict, repository task-gate result, atomic evidence-gate result and explicit residual. Aggregate PASS or representative substitution is forbidden.
- The cumulative ledger must prove unique `302/216/86`, zero unresolved references/cycles, exact migration/shared-file/SQLite order, all four overlay hashes and the complete inherited decision-gate propagation evidence while preserving dirty-baseline subtraction.
- `FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01` must independently PASS after effective Foundation close and existing customer decision gates before this ledger may execute or close.
- This task reports every missing mapping, artifact, gate, verdict or residual as blocking; it never repairs product, alters an assertion, activates a customer gate, closes the ledger early, runs final close or moves/duplicates/weakens the release gate.
- Existing scoped RED/GREEN, ledger test, Ruff/diff, Evidence 1.1, independent review, task gate, atomic validation and Done Definition remain binding for later High execution.
- This Ultra materialization edits no ledger output/test/evidence and runs only the atomic task-file check.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

CONFIG_REQUIRED is acceptable only with verified negative-path evidence. This task never claims production activation.

## Current C3 Latest-Wins Close Contract — 2026-08-13

The approved current design is
`docs/superpowers/specs/2026-08-13-v8-final-item-slice-ledger-current-design.md`.
It replaces only the historical taskctl/artifact mechanics above. The business closure,
non-closure, immutable catalog and Foundation counts, exact external identities and
release-last boundary remain authoritative.

The current derived ledger contains exactly `302` effective product nodes: the immutable
`283` catalog rows plus the following `19` external Foundation nodes. The effective
Foundation count is `216` (`197 + 19`) and the immutable deferred count remains `86`.
Each external identity maps to these exact already-current path-owning stories:

| External identity | Exact supporting current story IDs |
| --- | --- |
| `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01` | `V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-CURRENT-ADOPTION` |
| `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` | `V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION` |
| `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01` | `V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION` |
| `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01` | `V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01` | `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` | `V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` | `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION`, `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION` |
| `FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01` | `V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01` | `V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION`, `V8-FULL-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION` |
| `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01` | `V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01` | `V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION` |
| `FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01` | `V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION` |
| `FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01` | `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01` | `V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION` |
| `FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01` | `V8-D4-08-OA-STRUCTURED-ATTACHMENT-PROMOTION` |
| `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01` | `V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-CURRENT-ADOPTION` |
| `FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01` | `V8-CNIPA-ANNUITY-RATE-CANDIDATE-CURRENT-ADOPTION` |
| `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01` | `V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-CURRENT-ADOPTION` |
| `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01` | `V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-CURRENT-VERIFICATION` |

The four Delta controller/overlay families and G1/G2 are audit-only lineage and add no
product node. Current Git-native catalog hash, terminal overlay, coverage ledger, Row281
matrix, focused contract, candidate fingerprint, independent High review and lean inventory
replace their obsolete execution commands; historical artifacts are not rerun.

Exact current candidate files are:

- `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md`
- `backend/tests/test_v8_final_item_slice_ledger.py`
- `docs/product/v8/final-item-slice-ledger.json`
- `docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md`

Reviewer-only receipt and the separately reviewed ledger-only adoption are:

- `docs/product/v8/reviews/V8-FINAL-ITEM-SLICE-LEDGER-CURRENT-ADOPTION.md`
- `docs/product/v8/coverage-ledger.json`

The exact RED is `FileNotFoundError` for the required output/story. GREEN requires:

```text
cd backend && .venv/bin/pytest -q tests/test_v8_final_item_slice_ledger.py
cd backend && .venv/bin/ruff check tests/test_v8_final_item_slice_ledger.py
python3 -m json.tool docs/product/v8/final-item-slice-ledger.json >/dev/null
python3 -m json.tool docs/product/v8/coverage-ledger.json >/dev/null
python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha <exact-candidate-sha>
git diff --check <exact-base-sha>..<exact-candidate-sha> -- tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md backend/tests/test_v8_final_item_slice_ledger.py docs/product/v8/final-item-slice-ledger.json docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md
git diff --check -- docs/product/v8/coverage-ledger.json
```

Rows 1–281 must resolve before this close. Row282 alone becomes `CURRENT_VERIFIED` only
after independent P0/P1/P2 `0/0/0` review. Row283 remains `FINAL_CLOSE_PENDING`; no Row283
byte or release command is in scope. Production inputs remain
`CONFIG_REQUIRED / PENDING / 409 NO WRITE`, TEST_ONLY remains isolated, and
`production_activation_claimed` remains false.
