# PD-ENH-ANSWER-REVIEW-20260611-01 — 客户问题解答复核与文档增强

## Exact Closure Slice

Analyze every answer in `/Users/cfcc/Documents/相关问题解答.docx`, cross-check against the existing FPMS implementation and prior post-demo evidence, then surgically enhance:

- `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`

Every customer answer must be recorded in an answer ledger with evidence, impact, and outcome: updated, already covered, or still pending confirmation.

## Explicit Non-Closure

No backend product code, frontend product code, database migration, CPC/OA direct submission, RPA, signature automation, payment automation, receipt OCR/download automation, or email-sending implementation. Do not rewrite either target document wholesale.

## Remaining Follow-Up Task IDs

None unless the customer answers expose a product implementation gap that needs a later focused development task.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. Edits are limited to two post-demo markdown documents, this task file, and task evidence. |
| prereq_dependency_density | Medium. Requires extracting the customer answer DOCX and checking selected FPMS implementation areas before changing docs. |
| be_fe_coupling | Low. Code is read-only evidence for GAP statements; no implementation files may be edited. |
| evidence_cost | Medium. Requires answer ledger, scoped diff, content checks, and task gate. |

chosen_runbook: `P0-single-lane-story`

## Story Shape

- shared_file_density: Low.
- prereq_dependency_density: Medium.
- be_fe_coupling: Low.
- evidence_cost: Medium.

## Chosen Runbook

`P0-single-lane-story`

## Preflight Dependency Audit

- Source DOCX must be readable from `/Users/cfcc/Documents/相关问题解答.docx`.
- Existing analysis and FS documents must be present.
- Codebase evidence is read-only; any product implementation gap must remain non-closure.
- Dirty worktree baseline must be captured before claiming PASS.

## Baseline Promotion Protocol

- Do not promote unrelated dirty files into this task.
- Only scoped edits to the allowed post-demo documents, task file, and task artifacts may be included in `git/diff.patch`.
- If current implementation evidence contradicts prior analysis, update the documents surgically and record the contradiction in the answer ledger.

## Replan Triggers

- The DOCX cannot be extracted or its embedded image cannot be inspected.
- The customer answer requires product code, schema, CPC/OA automation, RPA, payment automation, or email sending implementation.
- A second independent closure slice appears, such as creating a new implementation task or changing product code.

## Allowed Files

- `tasks/postdemo/PD-ENH-ANSWER-REVIEW-20260611-01.md`
- `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `artifacts/PD-ENH-ANSWER-REVIEW-20260611-01/**`

## Required Source Inputs

- `/Users/cfcc/Documents/相关问题解答.docx`
- `docs/postdemo/相关流程操作-20260526.docx`
- `docs/postdemo/OA答复流程.docx`
- `docs/postdemo/信函生成操作.docx`
- `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `artifacts/PD-ENH-*/summary.md`
- Current FPMS cases/documents/tasks/fees/templates/frontend/product-doc implementation evidence.

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-ENH-ANSWER-REVIEW-20260611-01.md`
- Content extraction / ledger completeness check recorded as `test`
- Markdown/document consistency check recorded as `lint`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize PD-ENH-ANSWER-REVIEW-20260611-01 --status PASS`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-ENH-ANSWER-REVIEW-20260611-01`
- `./scripts/task_validate.sh PD-ENH-ANSWER-REVIEW-20260611-01`

## Evidence Path

- `artifacts/PD-ENH-ANSWER-REVIEW-20260611-01/`

## Done Definition

- The DOCX answer content is extracted and checked for tables/embedded objects.
- An answer ledger exists under task artifacts and covers every identified answer item.
- Target documents are surgically updated only where the answer changes scope, closes a pending question, clarifies P1/P2/P3 boundaries, or corrects a GAP statement.
- Unresolved items remain marked `待确认` with a concrete missing-evidence reason.
- Required evidence files exist, dirty baseline is captured if needed, and task gate passes.
