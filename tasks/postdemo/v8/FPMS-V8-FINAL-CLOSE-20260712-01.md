# FPMS-V8-FINAL-CLOSE-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `17. Wave 8 — real paths and release close`
Catalog ordinal: `283`
Executor role: Independent Reviewer / explorer

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`
- `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md`
- `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
- Source catalog line: `828`
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

Full-program QA-only close: zero catalog omissions, every other catalog task PASS, clean SQLite upgrade+seed, full backend Ruff/pytest, frontend lint/typecheck/build, real UI specs, pre-self manifest gate and evidence audit.

## Explicit Non-Closure

No product fix, schema change or test-assertion weakening. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

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
- `FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-GRANT-YEAR-DRAFT-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-FUTURE-ANNUITY-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-001-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-002-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-003-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-004-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-005-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-006-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-007-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-008-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-009-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-010-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-011-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-012-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-013-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-014-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-015-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-016-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-017-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-018-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-019-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-020-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-021-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-LEGACY-FORM-022-MANIFEST-ACTIVATION-20260712-01`
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
- `FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01`
- `FPMS-V8-FOUNDATION-INHERITED-REGRESSION-MATRIX-20260712-01`
- `FPMS-V8-FOUNDATION-CLOSE-20260712-01`
- `FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01`
- `FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01`

### External, gate and inherited prerequisites

Audit-only materialization controllers (outside product counts):

- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`

Product external prerequisites (seven additive product-graph nodes):

- `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01`
- `FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`
- `FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`
- `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`

Audit-only governance gates (outside product counts):

- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`
- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`

- Approved source dependency cell (verbatim): full ledger, every other catalog task

### Shared ownership serialization

- `docs/reviews/fpms_postdemo_v8_mitigation_close_audit_20260712.md` order key `2`; project this order only across owners present in the active manifest.
- `FULL_SHARED_VERIFICATION` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md`
- `docs/reviews/fpms_postdemo_v8_mitigation_close_audit_20260712.md`
- `backend/tests/test_v8_final_close_contract.py`
- `artifacts/FPMS-V8-FINAL-CLOSE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Follow the frozen foundation/full close order; QA tasks report failures and never repair product code.
- Before the existing full-manifest coverage gate or either release gate runs, do not
  rerun the delta-1 or delta-2 overlay validators. Their accepted outputs, return codes,
  evidence and overlay hashes are pinned read-only historical inputs. The cumulative
  delta-3 validator must validate those pinned parent overlay hashes plus the corresponding
  historical controller task/evidence gate results, fail closed on parent or task hash
  drift, and prove an acyclic effective product graph of `290` unique nodes plus `204`
  effective Foundation product requirements while the immutable catalog remains exactly
  `283` rows, the immutable Foundation manifest remains exactly `197` rows and deferred
  remains exactly `86`. G1/G2 and all three controllers are audit-only governance gates
  and must never be counted as product nodes or Foundation product requirements. Only the
  cumulative delta-3 validator is run as the current overlay gate; the pinned delta-1 and
  delta-2 historical validator inputs are neither rerun nor required to report a current
  PASS for Foundation, Full or Release closure. Then validate the task and atomic-evidence
  gates for all seven product external prerequisites and audit-only G1/G2.
- After G2 passes, every atomic-evidence validation in this final-close run, including a
  single-lane validation with no peers, must use the repository G2 wrapper
  `python3 scripts/atomic_evidence_validate.py`; direct external-helper validation is not
  permitted. All SQLite-writing tests and shared-file verification remain serialized.
- The final item-to-slice ledger must map all three additive controller/overlay families,
  all seven product external prerequisite tasks and audit-only G1/G2 evidence without
  representing controllers or governance gates as product slices. It must also prove all
  `29` scoped decision-gate composite identities propagate through contracts, join,
  keyset, HTTP, frontend, UI, fixture, real UI E2E and Full activation. A
  representative-slice pass is never sufficient for Full or Release closure.
- This final-close task alone owns repository-wide backend Ruff/pytest, frontend
  lint/typecheck/build and full real-path Playwright verification. Keep the final close
  audit shared-file order key `2`, require independent reviewer approval, and do not move,
  duplicate, edit or weaken either existing release-gate command.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_final_close_contract.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `python3 artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/analysis/validate_delta3_overlay.py`
- `./scripts/task_validate.sh REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`
- `python3 scripts/atomic_evidence_validate.py REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `./scripts/task_validate.sh REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`
- `python3 scripts/atomic_evidence_validate.py REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `for task in FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01 FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01 FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01; do ./scripts/task_validate.sh "$task"; done`
- `for task in FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01 FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01 FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01; do python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `./scripts/task_validate.sh FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `for task in FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01; do ./scripts/task_validate.sh "$task"; done`
- `for task in FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01 FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01; do python3 scripts/atomic_evidence_validate.py "$task" --required-step lint --required-step test --required-step independent_review --required-step scope; done`
- `./scripts/task_validate.sh FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`
- `python3 scripts/atomic_evidence_validate.py FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `python3 scripts/v8_catalog_manifest_gate.py --phase full --manifest tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md --self-pending FPMS-V8-FINAL-CLOSE-20260712-01`
- `for task in $(python3 -c "import json; print(*(row['task_id'] for row in json.load(open('artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/materialization/catalog.json'))['tasks']))"); do [ "$task" = "FPMS-V8-FINAL-CLOSE-20260712-01" ] || ./scripts/task_validate.sh "$task"; done`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads`
- `cd backend && tmp_db="$(mktemp -t fpms_v8_final_close).db" && DATABASE_URL="sqlite:///$tmp_db" PYTHONPATH=. .venv/bin/alembic upgrade head && DATABASE_URL="sqlite:///$tmp_db" PYTHONPATH=. .venv/bin/python scripts/seed_dev.py && DATABASE_URL="sqlite:///$tmp_db" PYTHONPATH=. .venv/bin/pytest -q tests/test_v8_final_close_contract.py -k fresh_login`
- `cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q`
- `cd frontend && npm run lint && npm run typecheck && npm run build`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-lifecycle-overlay-live.spec.ts src/tests/v8-pay-list-boundary-live.spec.ts src/tests/v8-official-workbook-live.spec.ts --workers=1`
- `./scripts/release_gate.sh --manifest tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md --exclude-task FPMS-V8-FINAL-CLOSE-20260712-01`
- `cd backend && .venv/bin/pytest -q tests/test_v8_final_close_contract.py`
- `git diff --check -- docs/reviews/fpms_postdemo_v8_mitigation_close_audit_20260712.md backend/tests/test_v8_final_close_contract.py tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FINAL-CLOSE-20260712-01`
- Evidence validation: `python3 scripts/atomic_evidence_validate.py FPMS-V8-FINAL-CLOSE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- `./scripts/release_gate.sh --manifest tasks/batches/FPMS-POSTDEMO-V8-MITIGATION-20260712-01.md  # lead-only after the final-close task gate passes`

## Evidence Path

- `artifacts/FPMS-V8-FINAL-CLOSE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

All three controller task/evidence gates, all seven product external task/evidence gates
and audit-only G1/G2 gates must pass before the existing manifest and release sequence
begins. The current cumulative delta-3 validator must validate the pinned delta-1/delta-2
historical validator outputs/evidence, parent overlay hashes and corresponding controller
task/evidence gate results. The historical validators are not rerun and are not required
to report a current PASS.
Immutable-parent `283/197/86` counts, effective product/Foundation `290/204` counts and the
complete three-family plus 29-composite-gate item-to-slice ledger must validate without
counting controllers or G1/G2 as product slices. The exact RED is preserved; the minimum
allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped
lint/format/scope checks pass; shared files and SQLite verification were serialized; every
atomic-evidence validation used the G2 wrapper, including single-lane validation;
dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer
approves the exact closure and non-closure; atomic evidence validation and
`./scripts/task_validate.sh FPMS-V8-FINAL-CLOSE-20260712-01` pass. Only then may this task
be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority and controller gate

- Authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`,
  its 34-row supplemental manifest, and row `33 / M4-I / FINAL-CLOSE`.
- Risk is `HIGH`; `chosen_runbook: P0-prereq-heavy-story` is latest-wins. Every inherited
  Delta overlay, Allowed Files entry and verification/release command remains unchanged.
- The Delta-4 controller
  `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01` must first reach
  independent accepted PASS with task gate, Evidence 1.1 and both required review axes.
- Delta-1/2/3 controllers, their pinned overlays/hashes and all inherited audit/governance
  gates remain mandatory accepted parents; Delta-4 does not rerun or rewrite their history.

### Cumulative Delta-4 graph and hash gate

- Run the accepted current validator
  `artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/analysis/
  validate_delta4_overlay.py` only after the controller PASS.
- It must hash-lock every immutable parent, pinned prior overlay and normalized task anchor
  and validate the deterministic cumulative Delta-4 manifest/overlay hashes.
- It must prove exactly 302 unique product nodes, 216 effective Foundation nodes,
  86 deferred nodes, zero unresolved dependency and zero cycle; governance controllers,
  reviews and audit gates remain excluded from all product/Foundation counts.
- It must also prove all twelve Delta-4 additions, seventeen re-freezes, four close
  propagations, exact allowlists/dependencies, migration heads, shared-owner ordering,
  SQLite serialization and unchanged final release-gate position.
- Any missing, duplicate, stale, drifted, unresolved, cyclic, miscounted or self-approved
  fact fails final close closed. No inference, waiver, repair or representative slice is
  accepted.

### Thirty-three row gates and immutable close order

- Each Delta-4 row 01–33 requires its separate independent materialization verdict
  `APPROVED/P0=P1=P2=0`; the controller's aggregate reviews never substitute for a row.
- Every applicable row/product task must independently pass its exact targeted checks,
  repository task gate, Evidence 1.1 scope/evidence gate and zero-finding review. The final
  close consumes recorded results; it does not repair product code or approve itself.
- Close order is exact and serialized:
  `Foundation close → Full activation → item-to-slice ledger → final close → release`.
- Row 30 must first prove all 216 Foundation product nodes and required audit gates. Row 31
  may then pass only after the accepted customer-decision gates. Row 32 must then map all
  302 product nodes, twelve Delta-4 additions, seventeen re-freezes and all four overlays
  without counting governance as product. Only then may this Row 33 execute.
- Full/catalog/ledger/final audit assertions, inherited real-path regressions and all
  required task/evidence gates remain complete; no early or partial close is authoritative.

### Shared verification and release boundary

- Respect every shared-file ownership order. Alembic/SQLite-writing verification uses
  `GLOBAL_SQLITE_SERIAL_QUEUE`, maximum writer one; real Playwright verification keeps its
  inherited single-worker boundary. Final-close shared verification remains exclusive.
- The existing repository-wide backend Ruff/pytest, frontend lint/typecheck/build and
  full real-path Playwright commands remain owned only by this final-close task and run
  only at their inherited manifest-defined close point.
- Preserve both inherited release-gate command lines byte-for-byte and in place. The
  lead-only final release gate runs only after this final-close task gate and independent
  evidence/review acceptance; never move, duplicate, omit, weaken or run it early.

### Materialization non-execution

- This materialization changes only Status and this EOF appendix. It initializes no final
  evidence, runs no controller/validator/product/repo-wide/close/release command, edits no
  audit/test/product file and changes no inherited allowlist or release command.
- Only atomic `check-task` runs now. Foundation, Full, ledger, final-close and release
  execution remain deferred until every prerequisite above is durably accepted PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

CONFIG_REQUIRED is acceptable only with verified negative-path evidence. This task never claims production activation.

## Current C3 Latest-Wins Final Contract — 2026-08-13

The approved current design and plan are:

- `docs/superpowers/specs/2026-08-13-v8-final-close-current-design.md`
- `docs/superpowers/plans/2026-08-13-v8-final-close-current.md`

They replace only obsolete taskctl/artifact/release mechanics. Row283 remains an audit-only
PROTECTED Final close: no product, schema, migration, seed, registry or test behavior may be
changed. Exact candidate paths are:

- `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md`
- `backend/tests/test_v8_final_close_contract.py`
- `scripts/run_v8_paylist_boundary_live_isolated.py`
- `docs/product/v8/final-close-report.json`
- `docs/product/v8/stories/V8-FINAL-CLOSE.md`

Reviewer receipt and separately reviewed adoption are limited to:

- `docs/product/v8/reviews/V8-FINAL-CLOSE-CURRENT-ADOPTION.md`
- `docs/product/v8/coverage-ledger.json`

The exact RED is missing report/story. The broad Final matrix then runs once: isolated clean
SQLite upgrade+seed; full backend Ruff+pytest; frontend lint+typecheck+build; isolated
lifecycle, PayList boundary and official workbook real E2E. A mode-0700 external directory
holds command logs. The report stores only exact commands, return codes, counts/summaries,
warnings and log SHA-256 values. The focused contract verifies/scans logs and tracked
report/story/receipt without echoing sensitive matches; it also validates the exact current
Foundation/Full story and review inputs.

After that named RED is captured, the focused contract recognizes exactly one pre-report execution
state so the full backend lane can itself become report evidence: report, story and receipt are all
absent; both HEAD and worktree keep Row283 PENDING; and no Final adoption story exists. Any partial
Final artifact, ledger transition or receipt leaves that state and requires the complete report
consumer. This staging rule does not skip or weaken any adopted/release assertion.

Customer production inputs remain `CONFIG_REQUIRED / PENDING / 409 NO WRITE`; TEST_ONLY is
isolated and production activation is not claimed. The three candidate/pre-review/adopted
states, exact fingerprint, sole-ledger patch hash, receipt-only commit and ledger-only
adoption follow the approved plan. After adoption, the final two checks are focused/lean
Final; the last program command is exactly:

```text
python3 scripts/v8_lean_coverage_check.py --milestone release --integration-sha HEAD
```

Nothing is executed or changed after that release command.
