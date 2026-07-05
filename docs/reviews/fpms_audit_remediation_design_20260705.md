# FPMS Audit Remediation Design

Date: 2026-07-05

Source audits:

- `docs/reviews/fpms_functional_correctness_audit_20260705.md`
- `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md`

## Story Shape Classification

- `shared_file_density`: medium; several backend service/test files are touched, but each task has an explicit allowlist.
- `prereq_dependency_density`: medium; remediation depends on the audit report, P1 FS, fee designs, and current implementation.
- `be_fe_coupling`: low; selected items are backend behavior and API contract tests only.
- `evidence_cost`: high; each remediation task needs red/green tests, scoped lint, diff evidence, and task gate.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Product Assumptions

- This round fixes only issues that are already evidenced by source documents and code, and do not require additional customer decisions.
- The source of truth for `GRANTED` readiness is the existing case status required-field rule, not an ad hoc document-upload shortcut.
- Attachment role validation is role-level file quality control. It does not change storage paths, official notice catalogs, or CPC/OA submission behavior.
- Fee-rate effective dates are already present in `FeeRate`; selectors must respect them before choosing an enabled rate.
- OA manifest roles can be single-file or multi-file. `OA_OTHER_PROOF` and similar proof/extra file roles must preserve multiple attachment lines.

## Audit Issue Triage

| Audit ID | Executable now? | Decision | Reason |
|---|---:|---|---|
| `IC-01` | Yes | In scope | GRANTED readiness predicates demonstrably drift across case, document, and grant-fee services. No customer decision is needed. |
| `FG-03` / `IC-09` | Yes | In scope | Upload service already has role metadata and disabled type guards; role-level extension/MIME checks are directly testable. |
| `IC-05` | Yes | In scope | `FeeRate.effective_from/effective_to` exist and selectors ignore them. No fee amount or customer sample change is needed. |
| `IC-04` | Yes | In scope | Current manifest upsert is role-unique and can overwrite repeated proof attachments. Multi-file proof role behavior is directly testable. |
| `IC-02` / `FG-04` | No | Skipped | Receipt metadata completeness and received-file validation overlap with the unresolved question of whether receipt lists are manually entered or system-parsed. OCR/automatic parsing is explicitly skipped. |
| `IC-03` | No | Skipped | Dedicated override permission depends on customer-approved role/approval policy. |
| `FG-01` | No | Skipped | Agent qualification certificate ownership remains a customer confirmation item. |
| `FG-05` | No | Skipped | Official payment Excel requires official/customer sample template and field confirmation. |
| `FG-09` / `IC-10` | No | Skipped | Latest official notice tie-break rule remains unresolved. |
| `FG-10` | No | Skipped | Longxia handoff transport contract remains unresolved. |
| `FG-12` | No | Skipped | PCT/Hague/IC automatic triggers are intentionally frozen until P2/P3 samples and fields are confirmed. |
| `FG-02`, `FG-06`, `FG-07`, `IC-06`, `IC-07`, `IC-08` | No | Deferred | High-value follow-ups, but not selected for this remediation batch because they require broader workflow/state design. |

## In-Scope Atomic Tasks

| Task ID | Closure | Main files | Verification focus |
|---|---|---|---|
| `FPMS-GRANT-STATUS-READINESS-GATE-20260705-01` | Make grant-notice upload and grant-fee status advancement use the same `GRANTED` readiness rule as case status validation. | `cases/service.py`, `documents/service.py`, `grant_fees/service.py`, grant notice tests | Missing `pub_no`/`pub_date` must prevent auto-advance to `GRANTED`. |
| `FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01` | Add role-level extension/MIME validation for receipt PDF, XML zip, Word/PDF OA files, claims/comparison pages, and proof files. | `documents/service.py`, attachment upload tests | Wrong type for XML zip or receipt/OA PDF must fail before storage. |
| `FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01` | Select official fee, annuity, and grant rates by `effective_from/effective_to` windows. | `fees/service.py`, `annuity/service.py`, `grant_fees/service.py`, fee tests | Old/future enabled rates must not be selected when a current rate exists. |
| `FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01` | Preserve multiple manifest rows for multi-file OA roles such as `OA_OTHER_PROOF`. | `official_workflows/service.py`, official work package tests | Two proof attachments must produce two present manifest rows, not one overwritten row. |

## Out of Scope

- No CPC/OA direct submit, RPA, automatic signing, automatic payment, automatic receipt download, or OCR.
- No database migration.
- No fee amount/catalog changes.
- No official payment Excel generation.
- No full legal status transition matrix.
- No Longxia integration contract implementation.
- No product audit export.

## Data Model / API / UI Impact

- Data model: no schema changes.
- API: existing response shapes are preserved. Validation may now return existing business error envelope with `400` for invalid upload file role/type combinations.
- UI: no direct UI change in this batch. Existing upload UI will surface backend validation errors through current error handling.
- Tests: backend targeted tests are required for every behavior change.

## Verification Strategy

- Each atomic task uses TDD: write a failing test, run the targeted test to capture red, implement the smallest fix, then rerun targeted tests.
- Run scoped Ruff on each task allowlist.
- Generate `artifacts/<TASK-ID>/results.jsonl`, `summary.md`, `git/diff.patch`, and dirty baseline files when needed.
- Run `./scripts/task_validate.sh <TASK-ID>` for every task.
- Final batch close ledger maps audit IDs to tasks, evidence, close decision, residual gap, and skipped reason.

## Batch Execution Order

1. `FPMS-GRANT-STATUS-READINESS-GATE-20260705-01`
2. `FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01`
3. `FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01`
4. `FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01`

The batch is intentionally serialized because all tasks are backend service/test changes and must keep task evidence isolated.
