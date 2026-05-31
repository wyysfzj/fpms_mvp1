# PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01 — P1 Functional Spec Alignment Review

- Source: user review of `docs/postdemo/postdemo_p1_functional_spec_20260531.md`.
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

- This task surgically reviews and updates one Functional Spec document.
- The task reads customer extracts, prior post-demo analysis, review ledgers, and current FPMS code/product docs.
- No backend, frontend, database, migration, CPC/OA automation, RPA, or email implementation is changed.

## Lightweight Brainstorming

### Product Assumptions

- P1 is an enhancement to existing FPMS workflows, not a separate temporary submission-package workaround.
- Customer-confirmed official fields should be modeled as FPMS UI/API/data-model enhancement requirements.
- `待补录` is reserved for official-page temporary values, customer-unclear ownership, or future integration-only data.
- New case material gate should align to customer feedback: required technical disclosure and optional instruction/engagement documents, rather than a broad generic official-filing gate.

### Alternatives Considered

1. Keep the current work-package-first FS and only add implementation notes.
   - Rejected: still frames missing official fields as补录 and under-specifies current FPMS enhancement.
2. Rewrite the whole FS as an implementation PRD.
   - Rejected: too broad for this atomic doc-review task.
3. Recommended: surgical alignment review that changes the FS language from补录 workaround to current-system enhancement, while preserving P1/P2/P3 boundaries.
   - Selected.

## Preflight Dependency Audit

- Permission / RBAC prerequisites: none; doc-only.
- State machine reachability: not applicable; spec only.
- Shared ownership file conflicts: no product files touched.
- External-system dependency: CPC/OA direct submit remains out of scope; unknown claims must be marked `待确认`.
- Dirty baseline: worktree is dirty from prior post-demo artifacts and one Word temp lock file; baseline artifacts required.

## Execution Mode

- Mode: single-thread
- Skills: `superpowers:brainstorming`, `fpms-postdemo-enhancement`, `grill-with-docs`, `atomic-evidence-gates`
- Why this mode is safe: the product boundary can be clarified from user feedback and existing evidence, then applied surgically to the existing FS.

## Baseline Promotion Protocol

- Preserve pre-task dirty state in:
  - `artifacts/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01/baseline_allowlist.diff`
  - `artifacts/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01/baseline_external_files.txt`
- Scope diff evidence to this task's allowlist.
- Do not revert or modify unrelated dirty files.

## Replan Triggers

- The requested FS edit requires implementation code changes.
- A second closure slice appears, such as creating implementation task files.
- Current-system claims cannot be grounded and would materially change P1 scope.

## Task Definition

- Goal: review and update `docs/postdemo/postdemo_p1_functional_spec_20260531.md` so P1 explicitly means enhancing existing FPMS workflows and data maintenance, aligned with `相关流程操作-20260526.docx` and integrated with `OA答复流程.docx`.
- Inputs:
  - `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
  - `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
  - `artifacts/PD-ENH-ANALYSIS-20260530-01/extracted/*.txt`
  - `artifacts/PD-ENH-REVIEW-20260530-01/analysis/review_findings.md`
  - `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/analysis/final_review_ledger.md`
  - current cases/documents/tasks/fees/templates/frontend/product evidence
- Allowlist:
  - `tasks/postdemo/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01.md`
  - `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
  - `artifacts/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01/**`
- Out of scope:
  - product code changes
  - database/schema/API/frontend implementation
  - CPC/OA automatic submission implementation
  - RPA implementation
  - email sending implementation
  - editing original customer `.docx` files
  - creating implementation tasks
- Shared ownership: No

## Verification

- `./scripts/evidence_run.sh PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01 lint /bin/zsh -lc 'python3 scripts/validate_plan_runbook.py tasks/postdemo/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01.md && rg -n "P1 是对现有 FPMS|系统字段增强|主数据维护|UI / API|数据模型|上传技术交底书|上传委托指示" docs/postdemo/postdemo_p1_functional_spec_20260531.md'`
- `./scripts/evidence_run.sh PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01 test /bin/zsh -lc 'rg -n "申请人国籍|申请人证件类型|申请人证件号|申请人官方邮编|发明人国籍|中国籍发明人身份证号|代理人资格证号|客户总委号|OA 答复工作包|现有系统 enhancement|待确认|待补录" docs/postdemo/postdemo_p1_functional_spec_20260531.md'`
- `./scripts/evidence_run.sh PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01 task_gate /bin/bash ./scripts/task_validate.sh PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01`

## Exact Closure Slice

- This task closes exactly one review/update of the P1 Functional Spec to align it with the user's clarified product boundary.

## Explicit Non-Closure Statement

- This task does NOT close product implementation, schema changes, API changes, UI changes, CPC/OA automation, RPA, email integration, or implementation task creation.

## Remaining Follow-up Task IDs

- None in this task; implementation tasks should be created only after the corrected FS is accepted.

## Done Definition

- [x] exact closure slice completed
- [x] no out-of-scope product implementation
- [x] dirty baseline artifacts exist
- [x] FS states P1 as existing FPMS enhancement, not补录 workaround
- [x] customer file gate feedback is reflected
- [x] official fields are categorized as UI/API/model enhancement where evidenced
- [x] OA reply is integrated into existing document/task/attachment workflow
- [x] P1 vs P2/P3 integration boundaries remain explicit
- [x] verification passed
- [x] artifacts generated
- [x] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01/baseline_allowlist.diff`
- `artifacts/PD-ENH-P1-FSPEC-ALIGN-REVIEW-20260531-01/baseline_external_files.txt`

## Execution Checklist

- [x] Record baseline artifacts before editing
- [x] Create atomic task file
- [x] Read current FS, customer extracts, prior analysis, and code evidence
- [x] Patch Functional Spec surgically
- [x] Record evidence summary
- [x] Run required verification
- [x] Generate scoped diff evidence
- [x] Run task gate
- [x] Stop after one closure slice
