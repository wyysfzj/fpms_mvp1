# PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01 — P1 Flow / Fee / File Review

- Source: user request to re-check `相关流程操作-20260526.docx`, especially screenshots, later official-document flow, fees, final fee-rate list, and file list.
- Type: `doc-review`
- Execution mode: Atomic (single-task, single-owner)

## Story Shape

- Story Shape Classification:
  - shared_file_density: low
  - prereq_dependency_density: low
  - be_fe_coupling: none
  - evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Chosen Runbook

- chosen_runbook: P0-single-lane-story

## Runbook Rationale

- This task reviews one source customer doc and surgically enhances two target post-demo documents.
- It reads extracted text, docx embedded screenshots, prior review ledgers, and current FPMS code/product evidence where needed.
- It does not implement backend, frontend, database, CPC/OA automation, RPA, or email changes.

## Preflight Dependency Audit

- Permission / RBAC prerequisites: none; doc-only.
- State machine reachability: not applicable; spec/report only.
- Shared ownership file conflicts: no product files touched.
- External-system dependency: no live CPC/OA/cponline interaction; screenshot evidence only.
- Screenshot limitation: final fee-rate list is stored as EMF/WMF and may need customer-provided readable source.
- Dirty baseline: worktree is dirty from prior post-demo artifacts and one Word temp lock file; baseline artifacts required.

## Replan Triggers

- The requested correction requires product code or database changes.
- A second closure slice appears, such as creating implementation task files.
- Screenshot evidence is not readable and materially changes P1 scope; mark `待确认` instead of guessing when possible.
- A shared ownership file outside this task allowlist must be edited.

## Task Definition

- Goal: verify whether screenshots and extracted content from `docs/postdemo/相关流程操作-20260526.docx` reveal omitted details about workflow transitions, later official files, fee/payment handling, fee-rate lists, and file lists; update the analysis document and P1 FS if gaps are found.
- Inputs:
  - `docs/postdemo/相关流程操作-20260526.docx`
  - `docs/postdemo/OA答复流程.docx`
  - `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
  - `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
  - `artifacts/PD-ENH-ANALYSIS-20260530-01/extracted/*.txt`
  - `artifacts/PD-ENH-REVIEW-20260530-01/analysis/review_findings.md`
  - `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/analysis/final_review_ledger.md`
  - current cases/documents/tasks/fees/templates/frontend/product evidence
- Allowlist:
  - `tasks/postdemo/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01.md`
  - `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
  - `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
  - `artifacts/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01/**`
- Out of scope:
  - product code changes
  - backend/frontend/database/migration implementation
  - CPC/OA direct submission implementation
  - RPA implementation
  - email sending implementation
  - editing original customer `.docx` files
  - rewriting the whole report or FS
- Shared ownership: No

## Review Focus

- Screenshot evidence from `相关流程操作-20260526.docx`: menus, buttons, page titles, fields, lists, file lists, fee-rate lists.
- Workflow coverage: new case, application-file upload/management, official-system import, OA reply, later official-file handling, receipt/merged-PDF archive, fee drafts/payment/rates, file roles.
- Boundary review: ensure current FS frames customer-confirmed behavior as existing FPMS enhancement, not long-term supplementation.

## Baseline Promotion Protocol

- Preserve pre-task dirty state in:
  - `artifacts/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01/baseline_allowlist.diff`
  - `artifacts/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01/baseline_external_files.txt`
- Scope diff evidence to this task's allowlist.
- Do not revert or modify unrelated dirty files.

## Verification

- `./scripts/evidence_run.sh PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01 lint /bin/zsh -lc 'python3 scripts/validate_plan_runbook.py tasks/postdemo/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01.md && test -s artifacts/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01/analysis/screenshot_review.md'`
- `./scripts/evidence_run.sh PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01 test /bin/zsh -lc 'rg -n "截图复核|后续官方文件|费率清单|文件清单|费用草单|批量号单|技术交底书|委托指示" docs/postdemo/postdemo_enhancement_analysis_20260530.md docs/postdemo/postdemo_p1_functional_spec_20260531.md'`
- `./scripts/evidence_run.sh PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01 task_gate /bin/bash ./scripts/task_validate.sh PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01`

## Exact Closure Slice

- This task closes exactly one review/update pass for `相关流程操作-20260526.docx` screenshot/flow/fee/file coverage into the existing analysis document and P1 FS.

## Explicit Non-Closure Statement

- This task does NOT close product implementation, schema changes, API changes, UI changes, CPC/OA automation, RPA, email integration, or implementation task creation.

## Remaining Follow-up Task IDs

- None in this task; implementation tasks should be created only after the corrected analysis/FS is accepted.

## Done Definition

- [x] exact closure slice completed
- [x] no out-of-scope product implementation
- [x] dirty baseline artifacts exist
- [x] docx screenshots/embedded images inspected or limitations marked
- [x] flow coverage checked
- [x] later official-file coverage checked
- [x] fee/rate coverage checked
- [x] file-list coverage checked
- [x] analysis document surgically enhanced if needed
- [x] P1 FS surgically enhanced if needed
- [x] verification passed
- [x] artifacts generated
- [x] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01/baseline_allowlist.diff`
- `artifacts/PD-ENH-P1-FLOW-FEE-FILE-REVIEW-20260531-01/baseline_external_files.txt`

## Execution Checklist

- [x] Record baseline artifacts before editing
- [x] Create atomic task file
- [x] Extract and inspect docx screenshot/image evidence
- [x] Read extracted text and prior ledgers
- [x] Compare against current analysis and P1 FS
- [x] Patch target docs surgically
- [x] Record evidence summary
- [x] Run required verification
- [x] Generate scoped diff evidence
- [x] Run task gate
- [x] Stop after one closure slice
