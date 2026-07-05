# FPMS-AUDIT-REMEDIATION-BATCH-20260705-01

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Coordinate the audit remediation batch for directly executable, evidence-backed findings from `docs/reviews/fpms_functional_correctness_audit_20260705.md` and `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md`. Land the remediation design, update `AGENTS.md` source-document index, execute the listed atomic tasks, and produce a batch close ledger.

## Explicit Non-Closure

Do not handle customer-confirmation items, CPC/OA direct submit, RPA, signing, automatic payment, automatic receipt download, OCR, official payment Excel template compatibility, full legal status transition matrix, Longxia transport, or product audit export.

## Batch Tasks

| Wave | Task file | Task ID | Owner | Dependency |
|---:|---|---|---|---|
| 1 | `tasks/reviews/FPMS-GRANT-STATUS-READINESS-GATE-20260705-01.md` | `FPMS-GRANT-STATUS-READINESS-GATE-20260705-01` | main thread, serialized | Design/index update complete |
| 2 | `tasks/reviews/FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01.md` | `FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01` | main thread, serialized | Wave 1 complete |
| 3 | `tasks/reviews/FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01.md` | `FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01` | main thread, serialized | Wave 2 complete |
| 4 | `tasks/reviews/FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01.md` | `FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01` | main thread, serialized | Wave 3 complete |

## Allowlist

- `AGENTS.md`
- `docs/reviews/fpms_audit_remediation_design_20260705.md`
- `tasks/reviews/FPMS-AUDIT-REMEDIATION-BATCH-20260705-01.md`
- `tasks/reviews/FPMS-GRANT-STATUS-READINESS-GATE-20260705-01.md`
- `tasks/reviews/FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01.md`
- `tasks/reviews/FPMS-FEE-RATE-EFFECTIVE-DATE-SELECTION-20260705-01.md`
- `tasks/reviews/FPMS-OFFICIAL-MANIFEST-MULTI-FILE-ROLE-20260705-01.md`
- `artifacts/FPMS-AUDIT-REMEDIATION-BATCH-20260705-01/**`

Each implementation task has its own narrower allowlist.

## Verification Commands

- `rg -n "fpms_functional_correctness_audit_20260705|fpms_audit_remediation_design_20260705" AGENTS.md`
- `rg -n "Audit Issue Triage|In-Scope Atomic Tasks|Batch Execution Order" docs/reviews/fpms_audit_remediation_design_20260705.md`
- `./scripts/task_validate.sh FPMS-AUDIT-REMEDIATION-BATCH-20260705-01`

## Done Definition

- Remediation design exists and explains in-scope vs skipped findings.
- `AGENTS.md` 0.3 index includes the two audit reports and remediation design.
- Atomic task files exist with closure, non-closure, allowlist, verification, and done definition.
- Batch close ledger maps audit IDs to task evidence and residual gaps.
- Batch evidence exists under `artifacts/FPMS-AUDIT-REMEDIATION-BATCH-20260705-01/**`.

## Evidence Path

- `artifacts/FPMS-AUDIT-REMEDIATION-BATCH-20260705-01/**`

## Remaining Follow-Up Task IDs

- `FPMS-RECEIPT-STRUCTURED-ARCHIVE-GATE-20260705-01` after customer confirms receipt list handling.
- `FPMS-OFFICIAL-WORKFLOW-OVERRIDE-PERMISSION-20260705-01` after customer confirms override role policy.
- `FPMS-PAY-LIST-OFFICIAL-TEMPLATE-COMPAT-20260705-01` after official Excel template/sample is confirmed.
