# BATCH-FE-DEMO-DISPLAY-RESIDUAL-01 — after-demo frontend display residual cleanup manifest

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: high
- chosen_runbook: P0-frontend-heavy-story

## Batch Goal

Close demo-visible frontend display residuals by removing user-facing English/technical labels, normalizing high-impact terminology, and preventing UUID/raw internal IDs from being shown as fallback text.

## Explicit Non-Closure

This batch does not modify backend contracts, schema, migrations, route params, permissions, response envelopes, or business state transitions. Any page that needs a new backend contract or cross-module shared ownership must be split into a follow-up task.

## Prompt-To-Artifact Checklist

| Requirement | Evidence source | Current coverage | Residual |
| --- | --- | --- | --- |
| All user-facing UI text is Simplified Chinese | static scans for English UI strings and task summaries | Partially covered by demo UI history plus `AD-FE-*` tasks below | Some technical-value labels remain intentionally; some visible ID labels still require follow-up. |
| Dropdown options are Chinese | `AD-FE-DEMO-DISPLAY-01` summary and page checks | Billing direction/finance lifecycle touched options covered | Remaining module-specific selectors need per-page tasks if they expose internal IDs. |
| Term consistency | terminology constants and targeted task summaries | `案卷号` fixed in `CaseReceiptList`; prior `AD-FE-TERM-*` plan exists | Remaining `案卷`/`案卷号` instances in task create, annuity generate, fee unified query, etc. |
| UUID not visible to end users | targeted `rg` scans and task `ux_check` steps | Relation chain, fee draft, billing/payment/offset, document list, task list/dashboard covered | Remaining commission, annuity/grant fee, expense, consulting, special search, case filters, system template pages. |
| AGENTS atomic evidence | per-task artifacts under `artifacts/<TASK-ID>/` | Completed tasks below have task gates | Remaining tasks must produce their own artifacts before PASS. |

## Executed Serial Wave Ledger

| Wave | Task file path | Owner role | Allowed product files | Verification | Exact closure slice | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `tasks/afterdemon/AD-FE-DEMO-DISPLAY-01.md` | main-thread frontend worker | `displayText.ts`, `RelationChainCard.vue`, fee draft list/detail, billing create/detail/list/payment/offset pages | lint, typecheck/build, ux grep, task gate, browser sanity | Finance lifecycle and relation-chain display fallbacks no longer show UUID/raw IDs; key status/type/direction labels are Chinese | PASS |
| 2 | `tasks/afterdemon/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01.md` | main-thread frontend worker | `DocumentList.vue` | lint, typecheck/build, ux grep, task gate | Document list case column no longer falls back to `#<case_id>` | PASS |
| 3 | `tasks/afterdemon/AD-FE-TASK-LIST-ID-DISPLAY-01.md` | main-thread frontend worker | `TaskList.vue`, `TodoTable.vue` | lint, typecheck/build, ux grep, task gate | Primary task list and dashboard todo table no longer show internal task/case IDs as fallback text | PASS |
| 4 | `tasks/afterdemon/AD-FE-CASE-RECEIPT-LIST-LABELS-01.md` | main-thread frontend worker | `CaseReceiptList.vue` | lint, typecheck/build, ux grep, task gate | Case receipt list client filter uses readable client selector and `案卷号` is normalized to `案号` | PASS |

## Remaining Task Manifest

| Proposed task file path | Owner role | Allowed product files | Required verification | Dependency notes | Exact closure slice | Explicit non-closure | Follow-up IDs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tasks/afterdemon/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01.md` | frontend worker | `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue` | scoped eslint; typecheck/build; ux grep; task gate | none | Remove visible task/case raw ID fallbacks from special task search rows | No task API/type/export/print behavior changes | `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01` |
| `tasks/afterdemon/AD-FE-ANNUITY-GRANT-ID-DISPLAY-01.md` | frontend worker | selected annuity/grant fee pages/components only, to be frozen in task file | scoped eslint; typecheck/build; ux grep; task gate | may require split if more than one ownership surface | Replace visible client/case/task/draft ID fallbacks in annuity/grant fee list surfaces with Chinese business placeholders | No gov payment contract change, no pay-list mutation change | `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01` |
| `tasks/afterdemon/AD-FE-COMMISSION-ID-DISPLAY-01.md` | frontend worker | selected commission pages only, to be frozen in task file | scoped eslint; typecheck/build; ux grep; task gate | may need separate agent/user selector contract if names are not available | Hide visible raw agent/case IDs in commission list/settlement fallback displays | No commission generation/settlement behavior change | `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01` |
| `tasks/afterdemon/AD-FE-CASE-FILTER-ID-LABELS-01.md` | frontend worker | selected case/report filter pages only, to be frozen in task file | scoped eslint; typecheck/build; ux grep; task gate | broad scan required before execution | Normalize visible `代理人ID`/`申请人ID` labels where no ID entry is intended for demo users | No backend filter contract change | `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01` |
| `tasks/afterdemon/AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01.md` | frontend worker | selected consulting/expense pages only, to be frozen in task file | scoped eslint; typecheck/build; ux grep; task gate | may require split if consulting and expense are not one closure | Hide visible project/case/worker/department raw ID fallbacks in consulting and expense read surfaces | No accounting/report behavior change | `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01` |
| `tasks/afterdemon/AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01.md` | frontend worker | `TaskTemplateList.vue` only unless split | scoped eslint; typecheck/build; ux grep; task gate | system settings may expose technical IDs intentionally; task must freeze exception or replace label | Normalize default supervisor ID visible label or record explicit technical exception | No task template API change | `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01` |
| `tasks/afterdemon/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01.md` | monitor/reviewer | `artifacts/AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01/**` | static full frontend scans; task gates for all in-scope tasks; typecheck/build; browser spot checks | runs last | Produce item-to-slice ledger proving prompt requirements are covered or listing residual gaps | No product code changes | None |

## Serialized Shared-File Decisions

- `frontend/src/constants/displayText.ts` is currently owned by `AD-FE-DEMO-DISPLAY-01`; future tasks should avoid touching it unless they create a dedicated shared-display-text task.
- `frontend/src/api/*.ts` and `frontend/src/api/*.types.ts` remain out of scope unless a future task explicitly freezes a contract-change slice.
- Router/menu files remain out of scope unless a task explicitly targets routing or navigation labels.

## Current Close Decision

Not complete. The executed tasks materially reduce demo-visible leakage, but static scans still show residual visible ID labels/raw fallback displays and term inconsistencies outside the completed task allowlists.
