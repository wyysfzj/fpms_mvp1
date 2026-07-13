# AGENTS — FPMS MVP1 (Authoritative)

This file defines the authoritative execution rules for Codex/Agent working on this repository.
Agent MUST follow these rules without exception.

---

## 0) Karpathy Behavioral Iron Rules (MANDATORY)

These rules are derived from the installed `karpathy-guidelines` skill and are mandatory for all repository work.

1. Think before coding.
   - Do NOT assume silently.
   - Surface assumptions, ambiguity, tradeoffs, and simpler alternatives before implementation.
   - If the requested behavior is unclear or has multiple credible interpretations, stop and ask or state the chosen assumption explicitly.

2. Simplicity first.
   - Implement the minimum code or documentation change that satisfies the requested closure slice.
   - Do NOT add speculative abstractions, configurability, features, or defensive paths that were not requested or required by the task.
   - If the implementation becomes larger than the problem warrants, simplify before claiming completion.

3. Surgical changes only.
   - Touch only files and lines that directly serve the explicit task.
   - Match existing local style and patterns.
   - Do NOT refactor, reformat, rename, or clean up adjacent code unless the task explicitly requires it.
   - Remove only unused code introduced by the current change; mention unrelated dead code instead of deleting it.

4. Goal-driven execution with verification.
   - Convert every task into concrete success criteria before or during execution.
   - For code changes, prefer a verifiable loop: reproduce or specify the expected behavior, implement the smallest fix, then run targeted verification.
   - Do NOT claim PASS, fixed, complete, or ready unless the relevant verification has run and the evidence requirements in this file are satisfied.

## 0.1 Development Skill Stack & Precedence (MANDATORY)

For future development, agents MUST use this skill stack in order. The order is a behavior precedence chain, not permission to ignore repository rules.

1. Karpathy's `karpathy-guidelines` first.
   - Start with assumptions, ambiguity, simplicity, surgical scope, and verifiable success criteria.
   - If any later skill suggests broadening scope, adding speculative structure, or touching unrelated files, Karpathy's simplicity and surgical-change rules win.

2. Superpowers second.
   - Use the relevant Superpowers process skill when it matches the task: brainstorming for behavior/design changes, systematic-debugging for bugs, test-driven-development for feature/bugfix implementation, writing-plans for approved multi-step work, verification-before-completion before success claims, requesting-code-review for meaningful completed work.
   - Apply Superpowers as workflow discipline, but do not let it override this repository's atomic task, evidence, SQLite, permission, status-code, or Simplified Chinese UI rules.
   - For tiny single-file documentation or configuration updates, use a compact design statement in-thread instead of producing heavy planning artifacts unless the user explicitly asks for a full spec.

3. `mattpocock/skills` third.
   - Use `grill-with-docs` when requirements or domain terms are fuzzy; resolve vocabulary against `CONTEXT.md`/ADRs when those files exist.
   - Use `diagnose` for bugs and regressions: create a fast feedback loop, reproduce, rank hypotheses, instrument one variable at a time, fix, then regression-test.
   - Use `tdd` for code changes where tests are appropriate: one behavior test at a time through public interfaces, then minimal implementation, then refactor only while green.
   - Use `to-prd`, `to-issues`, `triage`, `zoom-out`, `prototype`, or `improve-codebase-architecture` only when the task explicitly calls for that shape of work or when the lead has made it part of the approved plan.

4. `atomic-evidence-gates` fourth and always before claiming completion.
   - For implementation tasks, freeze exactly one task file path or one explicit batch manifest before editing.
   - Initialize or create evidence under `artifacts/<TASK-ID>/**`, run targeted verification, record results, and validate scope before reporting PASS.
   - If no task file exists and the user asks for a broad change, stop at planning or create/confirm the atomic task file before implementation.

Conflict rule:

- User instructions and this `AGENTS.md` remain authoritative. When two skills conflict, choose the stricter rule that preserves atomicity, scope control, evidence, and verifiable behavior.
- Do not invoke every skill mechanically. Invoke the smallest relevant subset, in the precedence order above, and state the chosen subset briefly when it affects execution.

## 0.2 Instruction Hygiene & Best-Practice Operating Loop

- Keep durable rules in `AGENTS.md`; keep transient task details in task files, plans, issues, or `artifacts/<TASK-ID>/**`.
- Prefer concrete commands, allowed files, expected behavior, and observable checks over broad prose.
- Do not paste large skill bodies, external articles, or long rationale into task plans; reference the skill name and load the current local skill file when needed.
- Before editing, identify: task id/path, closure slice, non-closure boundary, allowlist, relevant skills, and verification commands.
- During execution, keep changes small and reviewable; stop and replan if a hidden prerequisite, shared-file conflict, or second closure slice appears.
- After execution, report only evidence-backed claims: modified files, commands run, observed status, evidence path, closure completed, non-closure respected, and PASS/FAIL/BLOCKED.

## 0.3 Source Document Index for Reviews and Audits

When reviewing FPMS requirements, post-demo feedback, workflow gaps, fee logic, demo behavior, or implementation coverage, agents MUST check the relevant source documents below before relying on memory or code inference.

Rules:

- Prefer original customer/source documents first, extracted text second, generated analysis/design third, and code evidence last.
- Ignore Word temporary lock files such as `docs/postdemo/~$*.docx`.
- For `.docx` files with screenshots or embedded images, do not rely only on extracted text when UI paths, buttons, menus, lists, or fee tables matter.
- If an external local file is unavailable, use the extracted artifact listed below and mark the missing original as `待确认`.
- When a new customer source file or authoritative design file is added, update this index in the same task that first relies on it.

Customer and external source documents:

- `docs/TXX.pdf` - original customer/source PDF; `reference/TXX.pdf` is the reference mirror.
- `docs/postdemo/相关流程操作-20260526.docx` - customer workflow clarification, screenshots, internal official-file list, filing/OA/official document/fee/file-list details.
- `docs/postdemo/OA答复流程.docx` - OA reply workflow and official-system interaction expectations.
- `docs/postdemo/信函生成操作.docx` - letter generation and customer handoff workflow.
- `docs/postdemo/专利收费场景-20260626.docx` - post-demo patent fee scenario source, trigger scenes, fee categories/subtypes, fee reduction semantics, fee-node expectations.
- `docs/postdemo/相关问题解答.docx` - repo-local customer answer file confirming master power-of-attorney numbering, OA replies containing non-copyable content, and fee-reduction ratio semantics; prefer this original over the historical external copy below.
- `docs/postdemo/标准费率.XLS` - customer internal fee-code/rate workbook containing official-fee and service-fee columns; treat it as a customer pricing/configuration source, not as the current legal authority for official fee rates.
- `docs/postdemo/补充缴费信息模板.xlsm` - customer-provided macro-enabled supplementary payment workbook with a visible upload sheet and hidden fee/business-type dictionaries; preserve its provenance, macros, hidden sheets, field order, and validation behavior when assessing compatibility, and do not assume it is a clean or currently accepted official template without upload verification.
- `docs/postdemo/文件样例及模版/**` - customer-provided filing draft, official-document, OA-response, email-template, XML-handling, and archive examples; classify legacy forms separately from current official forms and inspect rendered pages when layout or attachments matter.
- `/Users/cfcc/Documents/相关问题解答.docx` - external local customer answer file used for post-demo clarification follow-up.
- `http://www.tianyueip.com/product/612` - customer-provided law-firm fee-standard webpage; use as a secondary customer/business reference, not as the primary legal fee authority; cached extraction lives at `artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/tianyueip_product_612.txt`.
- `https://www.cnipa.gov.cn/art/2024/8/6/art_1518_155983.html` - CNIPA primary webpage for current patent and integrated-circuit layout-design fee standards; verify the effective policy/version when activating rates.
- `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf` - CNIPA patent and integrated-circuit layout-design payment service guide, updated 2026-03-30; primary operational source for payment channels, fee types, reduction, late fees, and ticket rules.

Extracted customer-source text and review ledgers:

- `artifacts/PD-ENH-ANALYSIS-20260530-01/extracted/相关流程操作-20260526.txt`
- `artifacts/PD-ENH-ANALYSIS-20260530-01/extracted/OA答复流程.txt`
- `artifacts/PD-ENH-ANALYSIS-20260530-01/extracted/信函生成操作.txt`
- `artifacts/PD-ENH-ANSWER-REVIEW-20260611-01/extracted/related_answers_extracted.txt`
- `artifacts/PD-ENH-ANSWER-REVIEW-20260611-01/analysis/answer_ledger.md`
- `artifacts/PD-ENH-REVIEW-20260530-01/analysis/review_findings.md`
- `artifacts/PD-ENH-FINAL-REVIEW-20260530-01/analysis/final_review_ledger.md`
- `artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/专利收费场景-20260626.txt`
- `artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/docx_inventory.txt`
- `artifacts/PD-FEE-SCENARIO-GAP-REVIEW-20260705-01/extracted/专利收费场景-20260626.txt`
- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/analysis/source_ledger.md`

Authoritative FPMS baseline and design documents:

- `docs/FPMS SPEC 2.0.md` - primary FPMS lifecycle, state, workflow, fee, document, and case-management baseline; `reference/FPMS SPEC 2.0.md` and `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md` are mirrors.
- `docs/FPMS 架构技术设计.md` - architecture design baseline; `reference/FPMS 架构技术设计.md` is the reference mirror.
- `docs/00_mvp1_scope.md` through `docs/07_db_ddl_and_sqlite.md` - MVP1 scope, IA, RBAC, database, backend, frontend, deployment, and SQLite baseline.
- `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md`
- `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- `docs/FPMS_Code_Review_Report_SPEC_2.0_20260227.md`
- `docs/FPMS_Full_Test_Scenarios_and_Cases_SPEC_2.0_20260228.md`
- `docs/FPMS_SPEC2_0_Test_Cases_E2E.md`
- `docs/FPMS_SPEC2_2nd_Review.md`
- `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
- `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
- `docs/FRMS_SPEC2_2nd_POST.md`
- `docs/2026-04-09-spec20-process-follow-test-cases.md`
- `docs/spec20_end_to_end_ui_testing.md`
- `docs/spec20_tech_mitigate.md`
- `docs/gap.md`, `docs/mvp1_gap.md`, and `docs/mvp_story_gap.md`

Post-demo analysis, Functional Spec, demo, and fee-design documents:

- `docs/postdemo/postdemo_enhancement_analysis_20260530.md` - main post-demo enhancement analysis.
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md` - P1 Functional Spec used for P1 application and test work.
- `docs/postdemo/postdemo_p1_e2e_demo_20260612.md` and `docs/postdemo/postdemo_p1_e2e_demo_20260612.docx` - P1 end-to-end demo script with mock data.
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md` - lifecycle/status/file-driven demo design.
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md` - lifecycle demo execution script.
- `docs/postdemo/p1_demo_engineering_checklist.md`
- `docs/postdemo/p1_demo_execution_runbook.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md` - patent fee scenario integration design.
- `docs/postdemo/postdemo_fee_scenario_gap_review_20260705.md` - fee scenario gap review.
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md` - follow-up fee trigger design for reexamination and grant/annuity deadline preview.
- `docs/superpowers/plans/2026-05-31-postdemo-p1-full-scope-development.md`
- `docs/superpowers/plans/2026-06-11-postdemo-p1-answer-delta-full-scope.md`
- `docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md` - canonical V8 mitigation design for subsequent planning and implementation; inherits accepted Additional-GAP Tasks 01–70, supersedes conflicting V7 business semantics without rewriting V7 history, and keeps unresolved customer choices behind explicit decision gates.
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md` - comprehensive V8 implementation plan and 283-path atomic task catalog; preserves Tasks 01–70, serializes migrations/shared files/SQLite verification, starts with a 197-path foundation manifest, and defers 86 customer-dependent/full-only paths into independent gate lanes plus the eventual full manifest.

Audit and remediation review documents:

- `docs/reviews/fpms_functional_correctness_audit_20260705.md` - English functional completeness and implementation correctness audit.
- `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md` - Chinese version of the functional completeness and implementation correctness audit.
- `docs/reviews/fpms_audit_remediation_design_20260705.md` - remediation design for directly executable audit findings; records skipped customer-confirmation items.

Evidence families to search during audits:

- `artifacts/PD-ENH-*/summary.md` - post-demo enhancement analysis and review evidence.
- `artifacts/PD-P1-*/summary.md` - P1 implementation, QA, demo, lifecycle, and UI E2E evidence.
- `artifacts/PD-FEE-SCENARIO-*/summary.md` - patent fee scenario design and implementation evidence.
- `artifacts/PD-DOC-*/summary.md` - document, official notice catalog, attachment role, and upload UX evidence.
- `artifacts/PD-P1-E2E-UI-FULLSCOPE-20260602-01/full_scope_coverage_ledger.md`
- `artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/analysis/full_scope_delta_ledger.md`
- `artifacts/PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01/analysis/close_ledger.md`
- `artifacts/PD-P1-QA-FULLSCOPE-E2E-01/close_ledger.md`

Useful source-discovery commands:

```bash
find docs/postdemo \( -name '*.md' -o -name '*.doc' -o -name '*.docx' -o -name '*.pdf' -o -name '*.PDF' -o -name '*.txt' -o -name '*.xls' -o -name '*.XLS' -o -name '*.xlsm' \) ! -name '~$*' -print | sort
rg --files docs reference artifacts | rg '(TXX|FPMS SPEC|postdemo|专利收费|标准费率|补充缴费|文件样例|相关流程|OA答复|信函生成|相关问题|PD-ENH|PD-P1|PD-FEE|PD-DOC)'
find artifacts -maxdepth 2 -name summary.md | rg '/(PD-ENH|PD-P1|PD-FEE|PD-DOC)-'
```

---

## 1) Atomic Task Discipline

- The atomic unit remains EXACTLY ONE task file path.
- One atomic task = one endpoint OR one service OR one doc change.
- Atomicity is enforced at the AGENT level, not at the whole-session level.
- In a multi-agent run, the lead/main thread MAY coordinate multiple atomic task files in one session, but each spawned agent MUST own exactly one explicit task file path.
- No single agent may implement more than one task file in the same execution.
- Do NOT implement multiple endpoints inside one atomic task unless the task file explicitly defines them as a single unit.
- Do NOT proactively refactor unrelated code.
- When asked “which task to implement”, request/confirm either:
  - one exact task file path, OR
  - an explicit batch manifest listing one exact task file path per agent.
- If no explicit batch manifest exists, default to ONE task file only.
- Two agents MUST NOT concurrently edit the same task file or the same shared ownership file.
- Shared ownership files (for example: router wiring, shared schemas, permission registries, common exports) require serialized ownership.
- An atomic task file MUST define EXACTLY ONE closure slice, not one module cluster.
- Every atomic task file MUST explicitly state:
  - exact closure slice
  - explicit non-closure statement
  - remaining follow-up task ids, or `None`
- If a task file cannot clearly answer “what exact behavior does this task close?”, it is NOT ready for implementation.
- A task file MUST NOT use broad acceptance wording such as:
  - “close the remaining module”
  - “finish the whole chain”
  - “complete backend/frontend parity”
  - “close the remaining feasible scope”
- Preferred atomic examples:
  - one endpoint behavior
  - one service rule
  - one page capability
  - one query / visibility slice
  - one final QA close audit
- Disallowed atomic examples:
  - one whole module cluster
  - one mixed backend+frontend mega task
  - one task that combines defaults + linkage + queries + dashboard

## 1.1 Story Shape Classification & Runbook Selection (MANDATORY)

- This rule applies whenever there is a written spec, implementation plan, or batch manifest prepared to drive multi-step execution, or whenever the task requires more than one atomic task file or more than one execution wave; the single-file fix and doc-only exclusions only apply when no such written spec, implementation plan, or batch manifest exists.
- Before entering `writing-plans`, the task spec MUST record `Story Shape Classification` with at least:
  - `shared_file_density`
  - `prereq_dependency_density`
  - `be_fe_coupling`
  - `evidence_cost`
- The resulting task plan MUST also record the same `Story Shape Classification`.
- The task spec and the task plan MUST both record the selected `chosen_runbook`.
- Valid `chosen_runbook` IDs are:
  - `P0-single-lane-story`
  - `P0-prereq-heavy-story`
  - `P0-multi-lane-parallel-story`
  - `P0-frontend-heavy-story`
- The selected `chosen_runbook` MUST be explicit; reviewers and leads MUST reject plans that omit it.
- Execution MUST NOT start until both classification and runbook selection are complete and recorded in the spec and plan.
- If execution discovers a new shared prerequisite, shared ownership conflict, or state-machine reachability issue, the task MUST stop and return to planning with an updated classification and runbook choice before continuing.
- If the new prerequisite changes the closure slice, the original task MUST NOT be stretched to absorb it; the work MUST be split into a follow-up task.

---

## 2) Phase Constraints

### Phase 3 (Domain APIs)
- No database schema changes.
- No Alembic migration edits (except Phase 0-EXT compatibility fixes explicitly requested).
- Use existing ORM models only.
- Implement endpoints only in module-level `api.py`.
- Preserve existing response envelope conventions.

### Phase 3.1 (API Extensions — `tasks/backend/apis_ext/`)
- Same constraints as Phase 3.
- Only implement tasks under `tasks/backend/apis_ext/`.

### Phase 3.5 (Business Logic — `tasks/backend/business_logic/`)
- Service-layer logic only.
- No schema changes.
- Allowed:
  - docxtpl rendering
  - context builders
  - Document → Task auto-generation
- API wiring may be updated ONLY where explicitly required by the task.

---

## 3) Router Wiring (Module-level, One-time)

- Router wiring is module-level and one-time.
- Do NOT rewire routers when adding endpoints within an already-wired module.
- Only add `include_router(...)` when entering a module for the FIRST time.
- Router wiring changes are limited to `backend/app/api/router.py` unless a task explicitly requires otherwise.

---

## 4) Authorization & Permission Enforcement

- Permission enforcement is mandatory for all protected endpoints.
- NEVER use `Depends(require_perm(...))` inside decorator `dependencies=[...]`.
- ALWAYS inject permission as a function parameter:

```python
_perm: None = Depends(require_perm("Title.Action"))

- Permission codes MUST follow Title.Action naming.

———

## 5) FastAPI Status Code Semantics (MANDATORY)

### 204 No Content

- MUST NOT return a response body.
- MUST NOT define response_model for 204 routes.
- Handler must end with:
    - return None OR
    - return Response(status_code=204)

### 201 Created

- MUST return created resource or its identifier (unless task says otherwise).

### GET

- MUST NOT require a request body.

### Error semantics (use consistently)

- 400: business validation failure (explicit message)
- 401: unauthenticated
- 403: permission denied
- 404: resource not found
- 409: conflict / missing configuration
- 422: validation error (FastAPI)

Before finishing any task, self-check:

- Is the response body compatible with declared status_code?

———

## 6) Ruff / Lint Discipline

Code MUST pass task-scoped lint/format checks by default.

### Default task-level verification

- ruff check --fix <task-allowlist-files>
- ruff format <task-allowlist-files>
- ruff check <task-allowlist-files>

### Full-repo verification

- ruff check --fix .
- ruff format .
- ruff check .

Full-repo verification is allowed ONLY when one of the following is true:

- final batch close
- explicit user request
- explicit task/runbook requirement

Imports must remain minimal and ordered; remove unused imports.

Rules:

- Do NOT run repo-wide Ruff write operations by default for a single atomic task.
- Do NOT modify files outside the task allowlist only because repo-wide Ruff touched them.
- In multi-agent execution, repo-wide Ruff write operations require serialized main-thread ownership.
- If a task is atomic and file-scoped, lint/format should be file-scoped by default.

———

## 7) Response Envelope Discipline

- Do NOT invent new response envelopes.
- Follow existing module conventions.

———

## 8) SQLite PoC Compatibility (MVP1 REQUIRED)

MVP1 PoC uses SQLite. Code and migrations MUST remain SQLite-compatible.

### 8.1 Timestamp defaults (REQUIRED)

- Do NOT use now() in migrations or server_default.
- Use server_default=sa.text("CURRENT_TIMESTAMP") for created_at/updated_at.

### 8.2 Autoincrement primary keys (REQUIRED)

- SQLite autoincrement works only with INTEGER PRIMARY KEY.
- For PoC, prefer Integer PK everywhere.
- Do NOT use BigInteger PK expecting autoincrement.
- Keep PK/FK types aligned (e.g., do NOT point String PKs from BigInteger FKs).
- If UUID PK is used, UUID MUST be generated in application code (uuid4) and stored as TEXT.

### 8.3 Foreign keys must be enabled (REQUIRED)

- SQLite foreign keys are not guaranteed unless enabled.
- Engine creation MUST set PRAGMA foreign_keys=ON on every connection (SQLAlchemy connect event).

### 8.4 Dialect-specific SQL is prohibited in PoC

Do NOT introduce PG-only functions/types:

- uuid_generate_v4(), gen_random_uuid()
- ILIKE
- date_trunc(...), timezone(...), interval '...'
- JSONB, ARRAY, CITEXT
  If needed, implement SQLite-safe alternatives (lower()+LIKE; app-side date math; store JSON as TEXT).

### 8.5 Do not rely on RETURNING for correctness

- Do not assume RETURNING support; use session.flush() to obtain PK values after insert.

### 8.6 Concurrency note (PoC)

- SQLite uses file locks. Keep write transactions short.
- If “database is locked” occurs, prefer reducing concurrency; WAL/retry may be considered later.

———

## 9) Forward-only Migrations Policy

Some migrations intentionally do NOT support downgrade.

- Do NOT attempt to rely on alembic downgrade base in dev workflows.
- For clean rebuild on SQLite dev:
    1. Delete the SQLite db file (and -wal/-shm if present)
    2. Run alembic upgrade head

———

## 10) Seeding (MVP1 Required)

- Seeding MUST be idempotent and bootstrap-safe.
- Avoid deadlocks: seed must be runnable when no users OR no Admin role exists.
- After any SQLite DB rebuild, seed MUST be re-run and token must be refreshed (log in again).

———

## 11) Required Agent Output (End of each execution)

Every agent MUST explicitly state:

- Which task/runbook was executed
- Which role executed it
- Which file(s) were modified
- Verification commands + expected status codes
- Evidence path under artifacts/<TASK-ID>/**
- Final per-task status: PASS / FAIL / BLOCKED
- Exact closure slice completed
- Explicit non-closure boundary respected

If the main thread coordinates multiple agents in one session, it MUST additionally state:

- Agent-to-task mapping
- Execution wave / batch order
- Any serialized shared-file decisions
- Per-task completion summary

Status policy:

- PASS means the task is claimed complete and has required evidence
- FAIL means the task was attempted but did not meet completion criteria
- BLOCKED means execution could not proceed or complete because of a dependency, scope issue, missing contract, or policy constraint

An agent MUST NOT mark a task PASS unless:

- required verification has run
- required evidence exists
- scope compliance has been checked
- the exact closure slice has been completed
- no second closure slice was silently absorbed into the same task

———

## 12) Evidence & Gates (EOS Bootstrap — MVP1 Enhancement)

To make AI-first execution auditable and deterministic, every task MAY create/update evidence under:

- artifacts/<TASK-ID>/**

This is non-product output and is explicitly allowed for all tasks, even when a task’s code scope is restricted to a single source file.

Rules:

- Do NOT store secrets/PII in artifacts logs.
- Artifacts should be generated by wrapper scripts (see scripts/evidence_run.sh).
- Evidence is OPTIONAL for exploratory, in-progress, or blocked work.
- Evidence is REQUIRED for tasks that claim completion or PASS:
    - artifacts/<TASK-ID>/results.jsonl (commands + rc)
    - artifacts/<TASK-ID>/summary.md (human-readable evidence summary)
    - artifacts/<TASK-ID>/git/diff.patch (scoped diff)
    - artifacts/<TASK-ID>/baseline_allowlist.diff when the task started from a dirty worktree
    - artifacts/<TASK-ID>/baseline_external_files.txt when the task started from a dirty worktree

Completion policy:

- An agent MUST NOT mark a task PASS without the required evidence artifacts.
- FAIL and BLOCKED may be reported without complete evidence, but any available evidence should still be attached.
- Reviewer and main thread MUST treat missing required evidence as non-completion.
- If dirty baseline artifacts are required but missing, the task MUST NOT be treated as cleanly accepted.

Gates:

- Task Gate: ./scripts/task_validate.sh <TASK-ID>
- Release Gate: ./scripts/release_gate.sh

———

## 13) Codex Multi-Agent Atomic Execution (MVP1 Execution)

This repository supports multi-agent execution with strict atomic-task discipline.

Team behavior is enforced by this file + task files + evidence gates.

### 13.1 Role Mapping (Supported)

| Business Role | Codex Executor | Responsibility |
|---|---|---|
| Team Lead / Project Manager | Main thread / default | Plan, assign task IDs, group tasks into safe waves, coordinate dependencies, final acceptance |
| Architect / Designer | explorer agent | Spec/contract analysis, module boundary checks, design decisions, impact analysis |
| Backend Developer | worker agent | Implement exactly one backend atomic task file per agent |
| Frontend Developer | worker agent | Implement exactly one frontend atomic task file per agent |
| Tester / Progress Monitor | monitor agent | Wait/poll long-running work, run task gates, collect evidence, report pass/fail/blockers |
| Reviewer | explorer agent or main thread | Independent scope review, acceptance validation, risk notes |

Notes:

- Built-in roles may be used directly (default, explorer, worker, monitor).
- One session MAY contain multiple atomic tasks only when each task has an explicit task file path and is assigned to a distinct agent or serialized wave.
- Acceptance remains per-task, not per-session.

### 13.2 Hard Constraints (Iron Rules + Quality Gate)

- Preserve all rules in Sections 1-12; this section is additive, not a replacement.
- Each spawned agent MUST target exactly one atomic task file path.
- Lead MAY coordinate multiple task file paths in one run only through an explicit batch manifest.
- No single agent may own more than one task file concurrently.
- No two agents may concurrently edit the same ownership file or shared support file.
- Each execution task file MUST define one exact closure slice only.
- Each execution task file MUST include an explicit non-closure statement.
- If a task file still reads like a cluster plan, it must be rewritten before execution.
- Shared ownership files that require serialization include:
    - backend/app/api/router.py
    - shared schema files
    - permission registry / permission constants
    - common exports / index files
    - any file explicitly listed in more than one task allowlist
- Frontend shared ownership files that require serialization include:
    - frontend/src/api/*.ts
    - frontend/src/api/*.types.ts
    - frontend router wiring / route registry files
    - shared stores
    - shared constants / display-text registries
    - common module exports / index files
- If two tasks require the same shared file, split out a dedicated follow-up task OR serialize them into different waves.
- Backend/Frontend dev agents MUST NOT modify each other's ownership files unless task explicitly allows.
- Reviewer cannot mark a task complete unless required gates pass and evidence exists.
- Reviewer cannot mark an item or batch `covered` merely because one representative slice passed; close decisions must be based on item-to-slice evidence.

### 13.3 Coordination Protocol (Wave-based, Multi-Agent Safe)

1. Lead defines an explicit batch manifest:

- one row = one task file path
- owner role
- allowed files
- required verification
- dependency notes
- exact closure slice
- explicit non-closure statement
- remaining follow-up task ids
- done definition

Plan-driven execution rule:

- If the user initiates work from a plan/batch document instead of explicit task file paths, the lead MUST first convert that plan into an explicit batch manifest.
- No real multi-agent implementation may begin until each execution agent has:
    - one exact task file path
    - one allowlist
    - one verification set
    - one exact closure slice
- Without such a manifest, execution MUST fall back to single-agent or planning-only mode.

2. Architect (explorer) freezes API contract / acceptance checklist for each task or for the batch if the contract is shared and identical.
3. Lead groups only NON-CONFLICTING tasks into the same execution wave.
4. Spawn one execution agent per task in the current wave:

- backend task → worker
- frontend task → worker
- validation / long-wait / evidence tracking → monitor

5. Monitor tracks completion and records evidence per task under:

- artifacts/<TASK-ID>/results.jsonl
- artifacts/<TASK-ID>/summary.md
- artifacts/<TASK-ID>/git/diff.patch
- artifacts/<TASK-ID>/baseline_allowlist.diff when required
- artifacts/<TASK-ID>/baseline_external_files.txt when required

6. Reviewer validates each completed task independently:

- scope compliance
- gate pass
- no regression
- no cross-task contamination
- exact closure slice completed
- explicit non-closure boundary respected

7. Lead closes tasks individually.

- A session may complete multiple tasks.
- Each task must independently pass before being marked done.

Mandatory handoff artifacts per task when claiming PASS:

- artifacts/<TASK-ID>/results.jsonl
- artifacts/<TASK-ID>/summary.md
- artifacts/<TASK-ID>/git/diff.patch
- dirty baseline artifacts when required

8. Final QA close audit for any batch MUST include an item-to-slice ledger.

The ledger MUST map each in-scope `Partially Implemented` item to:

- required slices
- implemented task ids
- evidence
- residual gap
- close decision

A batch MUST NOT be declared `complete` unless:

- all implementation tasks are `PASS`
- all required artifacts exist
- all task gates pass
- every in-scope item is `covered` in the ledger
- no residual gap remains inside the approved batch interpretation

9. Worker takeover and stall handling MUST preserve slice boundaries.

Before labeling a worker `idle` or `stalled`, lead/monitor MUST check:

- recent allowlist diff growth
- artifact timestamp changes
- running verification activity
- whether only evidence or gate closure is missing

Allowed takeover types:

- evidence-only takeover
- verification-only takeover
- limited slice-completion takeover, but only when the remaining work is still inside the SAME exact closure slice

Forbidden takeover types:

- silently completing a second slice inside the same task
- stretching a broad acceptance statement to fit a partial result
- using takeover to cross into another batch
- using takeover to avoid splitting a needed follow-up task

If the remaining work belongs to another slice, the correct action is to create a new follow-up task, not to finish it in place.

### 13.4 Required Verification by Role

- Backend task:
    - task-level Ruff on allowlist files
    - task-defined targeted tests
    - pytest -q only for:
        - final batch close
        - explicit user request
        - explicit task/runbook requirement
- Frontend task:
    - targeted lint/type/build checks when supported by the repo tooling
    - repo-wide npm run lint / npm run typecheck / npm run build only for:
        - final batch close
        - explicit user request
        - explicit task/runbook requirement
- Tester / Monitor:
    - ./scripts/task_validate.sh <TASK-ID>
    - targeted regression checks
    - release gate only when explicitly requested for batch close
- Reviewer:
    - Verify status-code semantics, permission enforcement, envelope consistency,
      SQLite compatibility, task allowlist compliance, and no cross-task/shared-file regression.

SQLite test concurrency rule:

- Agents MUST NOT run concurrent test jobs that write to the same SQLite database.
- If a test suite is known or likely to perform writes, it must run in serialized ownership.
- When “database is locked” risk exists, prefer targeted tests and serialized execution over parallel full-suite execution.

### 13.5 `READY FOR HIGH DEVELOPMENT` Handoff Gate (MANDATORY)

A task or wave may enter High implementation only when the lead completes this mechanical checklist:

- [ ] Freeze the exact materialized task file path(s), exact closure slice, explicit non-closure boundary, and remaining follow-up task IDs.
- [ ] Freeze each task allowlist, dependencies, Story Shape Classification, chosen runbook, targeted verification commands, and evidence path.
- [ ] Build conflict-free waves and record every serialized shared-file owner; unresolved legal, business, customer, or product choices remain behind named decision gates and outside implementation scope.
- [ ] Complete the materialization/dependency preflight: every task file exists and passes the atomic task check, every prerequisite is closed or explicitly ordered, and no hidden shared prerequisite or unreachable state transition remains.

Reasoning and execution lanes:

- Ultra/highest-capability work MUST be limited to design freeze, unresolved legal/business or cross-module architecture decisions, high-risk escalation, and Foundation/Full/Release close audits.
- High implementation (balanced/high reasoning) is the default lane for frozen atomic tasks and MUST proceed through tracer TDD (one behavior at a time through public interfaces where tests are appropriate) and scoped evidence.
- An implementation worker MUST NOT perform broad source-document reanalysis unless it demonstrates a genuine contract ambiguity; it must stop the affected lane and escalate that ambiguity instead.
- Load only the minimal relevant skill stack in repository precedence order. Overlapping workflow skills MUST NOT be loaded mechanically.
- Give an independent reviewer only the task contract, baseline-subtracted diff, targeted results, and task evidence. Expand review context only when the reviewer identifies a concrete ambiguity that those inputs cannot resolve.
- Shared files, migrations, SQLite-writing verification, repo-wide checks, and release gates remain serialized under the existing ownership and gate rules.

No-progress takeover:

- A lead or monitor may declare a worker stalled only after two consecutive observations show no allowlist-diff growth, no artifact timestamp advancement, and no running verification.
- Any takeover MUST be bounded to evidence completion, verification, or the unfinished work inside the same exact closure slice. It MUST preserve the original allowlist and non-closure boundary and MUST NOT absorb a second slice.

Automatic escalation and fallback:

- Escalate the affected lane for a demonstrated contract ambiguity, unresolved legal/business/customer decision, cross-module architecture decision, hidden shared prerequisite, ownership conflict, closure-slice change, or high-risk/contradictory gate result.
- When the runtime exposes no programmatic model switching or reasoning-tier control, record an explicit escalation handoff with the task path, blocker, evidence, decision needed, and recommended capability tier; ask the lead or user to re-route it and never claim that a switch occurred.
- Unaffected conflict-free lanes MAY continue safely when their frozen contracts and dependencies do not cross the escalation boundary.

———

## 14) Frontend UI Language Iron Rule (MANDATORY)

- All user-facing UI text MUST be Simplified Chinese.
- This rule applies to:
    - page titles
    - menu labels
    - buttons
    - form labels/placeholders
    - validation/error/toast messages
    - empty states and helper texts
    - dialog titles/content/actions
- English is allowed only for non-UI technical values:
    - IDs, enum/code values, API field names, protocol terms, file paths, logs.
- If an existing page has mixed language, FE tasks touching that page MUST normalize visible text to Simplified Chinese within task scope.
- Reviewer MUST reject FE tasks that introduce or retain user-visible non-Chinese text without explicit task-level exception.
