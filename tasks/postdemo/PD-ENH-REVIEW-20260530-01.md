# PD-ENH-REVIEW-20260530-01 — Post-demo enhancement analysis double-check

- Source: user request to use `grill-with-docs` for a second-pass review of `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
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
- No backend, frontend, database, router, schema, permission, or shared API ownership files are changed.

## Preflight Dependency Audit

- Permission / RBAC prerequisites: none; no product code changes.
- State machine reachability: not applicable; doc-review only.
- Shared ownership file conflicts: none expected.
- External-system dependency: official CPC/OA details are source-limited; uncertain claims must remain `待确认`.
- Dirty baseline: current worktree is dirty; baseline artifacts are required.

## Execution Mode

- Mode: single-thread
- Skill: `grill-with-docs`, with `karpathy-guidelines` and `atomic-evidence-gates` constraints.
- Why this mode is safe: the review can be completed by reading source docs, product docs, and code, then surgically enhancing the report.

## Baseline Promotion Protocol

- Preserve pre-task dirty state in:
  - `artifacts/PD-ENH-REVIEW-20260530-01/baseline_allowlist.diff`
  - `artifacts/PD-ENH-REVIEW-20260530-01/baseline_external_files.txt`
- Scope diff evidence to only the task allowlist.

## Replan Triggers

- The review discovers a required product implementation change.
- The review requires changing backend/frontend/database files.
- The review discovers that an external CPC/OA claim cannot be sourced and would materially change the recommendation.
- A second closure slice appears, such as creating implementation task files beyond review recommendations.

## Task Definition

- Goal: double-check and surgically enhance the existing post-demo enhancement analysis report for missed details in process flow, page jumps, fields, templates, fee/rate handling, files, statuses, external systems, risks, and current-system GAP.
- Covered items:
  - source doc cross-check against extracted Word text
  - current report cross-check
  - code/product-doc scan of cases, documents, tasks, fees, templates, frontend pages, and product specs
  - surgical update to `docs/postdemo/postdemo_enhancement_analysis_20260530.md` if omissions are found
- Allowlist:
  - `tasks/postdemo/PD-ENH-REVIEW-20260530-01.md`
  - `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
  - `artifacts/PD-ENH-REVIEW-20260530-01/**`
- Out of scope:
  - product code changes
  - database/schema/API/frontend implementation
  - CPC/OA automatic submission implementation
  - email sending implementation
  - editing original customer `.docx` files
- Shared ownership: No
- Verification:
  - `./scripts/evidence_run.sh PD-ENH-REVIEW-20260530-01 lint /bin/zsh -lc 'python3 scripts/validate_plan_runbook.py tasks/postdemo/PD-ENH-REVIEW-20260530-01.md && rg -n "^## 4\\.1 二次复核补充|^### 9\\.4 字段与模板细节复核补充|^### 10\\.6 外部系统口径复核补充|^### 14\\.1 二次复核新增待确认问题" docs/postdemo/postdemo_enhancement_analysis_20260530.md'`
  - `./scripts/evidence_run.sh PD-ENH-REVIEW-20260530-01 test /bin/zsh -lc 'test -s artifacts/PD-ENH-REVIEW-20260530-01/analysis/review_findings.md && rg -n "REV-FLOW|REV-FIELD|REV-TEMPLATE|REV-FEE|REV-STATUS|REV-CPC" artifacts/PD-ENH-REVIEW-20260530-01/analysis/review_findings.md && rg -n "总委号|代理人资格证号|费减比例|批量号单上传|电子申请回执|格式函|reply_to_id|need_reply|PDF 保真" docs/postdemo/postdemo_enhancement_analysis_20260530.md'`
  - `./scripts/evidence_run.sh PD-ENH-REVIEW-20260530-01 task_gate /bin/bash ./scripts/task_validate.sh PD-ENH-REVIEW-20260530-01`

## Exact Closure Slice

- This task closes exactly:
  - one double-check pass over the existing post-demo enhancement analysis, with any evidenced omissions added to the same report.

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
- [x] source docs and report cross-checked
- [x] code/product-doc scan summarized
- [x] evidenced omissions added or explicitly marked as no omission
- [x] verification passed
- [x] artifacts generated
- [x] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PD-ENH-REVIEW-20260530-01/baseline_allowlist.diff`
- `artifacts/PD-ENH-REVIEW-20260530-01/baseline_external_files.txt`

## Execution Checklist

- [x] Confirm allowlist only
- [x] Record baseline artifacts before editing
- [x] Cross-check extracted Word text
- [x] Cross-check code/product docs
- [x] Implement surgical report enhancement only if evidenced
- [x] Run required verification
- [x] Generate scoped diff evidence
- [x] Run task gate
- [x] Stop after one closure slice
