# PD-ENH-FINAL-REVIEW-20260530-01 — Final per-file post-demo review

- Source: user request to use `grill-with-docs` for a final per-file review of three post-demo customer feedback files.
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

- This task is a documentation review and enhancement pass only.
- The task edits one existing post-demo analysis report plus this task file and evidence artifacts.
- No backend, frontend, database, router, schema, permission, email, CPC, or OA automation implementation files are changed.

## Preflight Dependency Audit

- Permission / RBAC prerequisites: none; no product code changes.
- State machine reachability: not applicable; doc-review only.
- Shared ownership file conflicts: none expected.
- External-system dependency: official CPC/OA details are source-limited; uncertain claims must remain `待确认`.
- Dirty baseline: capture current worktree state before report edits.

## Execution Mode

- Mode: single-thread
- Skill: `grill-with-docs`, with repository atomic/evidence constraints.
- Why this mode is safe: each customer feedback file can be reviewed independently against extracted text, current report content, and current code/product documentation, then surgically reflected in the existing report.

## Baseline Promotion Protocol

- Preserve pre-task dirty state in:
  - `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/baseline_allowlist.diff`
  - `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/baseline_external_files.txt`
- Scope diff evidence to only the task allowlist.

## Replan Triggers

- The review discovers a required product implementation change.
- The review requires changing backend/frontend/database files.
- The review discovers that an external CPC/OA claim cannot be sourced and would materially change the recommendation.
- A second closure slice appears, such as implementing CPC/OA submission or email sending.

## Task Definition

- Goal: final-check and surgically enhance `docs/postdemo/postdemo_enhancement_analysis_20260530.md` by reviewing each customer feedback file in its own loop.
- Per-file loops:
  - `相关流程操作-20260526.docx`: new case, filing package, official import, follow-up official documents, internal archive, fees, rates, codes, and current-system GAP.
  - `OA答复流程.docx`: OA reply preparation, cloud download, statement fields, attachment upload, save/preview/sign/submit/confirm/receipt, format fidelity, and current-system status linkage.
  - `信函生成操作.docx`: case query, intermediate files, format-letter mapping, generated Word naming, salutation rules, customer contact handling, and email-system boundary.
- Allowlist:
  - `tasks/postdemo/PD-ENH-FINAL-REVIEW-20260530-01.md`
  - `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
  - `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/**`
- Out of scope:
  - product code changes
  - database/schema/API/frontend implementation
  - CPC/OA automatic submission implementation
  - email sending implementation
  - editing original customer `.docx` files
- Shared ownership: No
- Verification:
  - `./scripts/evidence_run.sh PD-ENH-FINAL-REVIEW-20260530-01 lint /bin/zsh -lc 'python3 scripts/validate_plan_runbook.py tasks/postdemo/PD-ENH-FINAL-REVIEW-20260530-01.md && rg -n "^## 17\\. 最终逐文件复核补充|^### 17\\.1 相关流程操作-20260526\\.docx|^### 17\\.2 OA答复流程\\.docx|^### 17\\.3 信函生成操作\\.docx" docs/postdemo/postdemo_enhancement_analysis_20260530.md'`
  - `./scripts/evidence_run.sh PD-ENH-FINAL-REVIEW-20260530-01 test /bin/zsh -lc 'test -s artifacts/PD-ENH-FINAL-REVIEW-20260530-01/analysis/final_review_ledger.md && rg -n "相关流程操作-20260526\\.docx.*YES|OA答复流程\\.docx.*YES|信函生成操作\\.docx.*YES" artifacts/PD-ENH-FINAL-REVIEW-20260530-01/analysis/final_review_ledger.md && rg -n "FINAL-FLOW-|FINAL-FIELD-|FINAL-FEE-|FINAL-OA-FLOW-|FINAL-OA-STATUS-|FINAL-OA-TEMPLATE-|FINAL-LETTER-FLOW-|FINAL-LETTER-TEMPLATE-|FINAL-LETTER-CONTACT-" artifacts/PD-ENH-FINAL-REVIEW-20260530-01/analysis/final_review_ledger.md && rg -n "Enhancement 设计分析报告|OA / CPC 对接方案|格式保真方案|待客户确认问题|最终逐文件复核补充" docs/postdemo/postdemo_enhancement_analysis_20260530.md'`
  - `./scripts/evidence_run.sh PD-ENH-FINAL-REVIEW-20260530-01 task_gate /bin/bash ./scripts/task_validate.sh PD-ENH-FINAL-REVIEW-20260530-01`

## Exact Closure Slice

- This task closes exactly:
  - one final per-file review over the three post-demo customer feedback files, with evidenced omissions added to the existing enhancement analysis report or explicitly recorded as no omission.

## Explicit Non-Closure Statement

- This task does NOT close:
  - any backend API behavior
  - any frontend page behavior
  - any database model or migration change
  - any real CPC/OA submission automation
  - any email sending implementation
  - any implementation task creation beyond report recommendations

## Remaining Follow-up Task IDs

- None in this task; follow-up implementation tasks remain subject to customer/product confirmation.

## Done Definition

- [x] exact closure slice completed
- [x] no out-of-scope product implementation
- [x] `相关流程操作-20260526.docx` loop completed and ledger status is `YES`
- [x] `OA答复流程.docx` loop completed and ledger status is `YES`
- [x] `信函生成操作.docx` loop completed and ledger status is `YES`
- [x] evidenced omissions added to report or explicitly marked as no omission
- [x] verification passed
- [x] artifacts generated
- [x] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/baseline_allowlist.diff`
- `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/baseline_external_files.txt`

## Execution Checklist

- [x] Confirm allowlist only
- [x] Record baseline artifacts before report editing
- [x] Loop A: cross-check `相关流程操作-20260526.docx`
- [x] Loop B: cross-check `OA答复流程.docx`
- [x] Loop C: cross-check `信函生成操作.docx`
- [x] Implement surgical report enhancement only if evidenced
- [x] Record final review ledger
- [x] Run required verification
- [x] Generate scoped diff evidence
- [x] Run task gate
- [x] Stop after one closure slice
