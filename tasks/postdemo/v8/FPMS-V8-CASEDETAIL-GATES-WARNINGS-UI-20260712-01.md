# FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `273`
Executor role: Frontend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- Source catalog line: `811`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-UI`

- RED expectation: Targeted Playwright fails because the UI loses ordered composite gate identity, provenance or the required Simplified-Chinese warning/reason presentation.
- GREEN expectation: Targeted Playwright and exact-file ESLint pass while all 29 gate entries remain visible and rendering performs no state mutation.

## Exact Closure Slice

Render the lifecycle-overlay gate and warning presentation on the case-detail page in Simplified Chinese, preserving all 29 ordered composite gate entries, per-form reason/source provenance and distinct top-level versus milestone warnings without mutating business state.

## Ultra Contract Freeze — 2026-07-14 (delta-2)

This section is authoritative for High implementation. It freezes one visible
gates/warnings capability in `CaseLifecycleOverlay.vue`; it does not create another
page capability, resolver, activation path or frontend business-state calculation.

### Ordered composite gate rendering

- Consume `decision_gates` from the accepted overlay frontend adapter as the complete
  ordered server snapshot. Render exactly 29 rows in received order: the seven
  non-legacy entries requested at `case:<case_id>`, followed by the 22
  `DG-LEGACY-FORM-CLASS` entries requested at `form-001` through `form-022`.
- Row identity is exactly `(gate_code, requested_scope_key)`. Use that composite
  identity for rendering. Do not convert the collection to a gate-code-keyed record,
  deduplicate it with a code-only set, sort it again, or replace one repeated legacy
  row with another. The 22 duplicate legacy gate codes remain 22 distinct visible
  rows.
- Every legacy row visibly renders its requested form scope. A resolved row also
  renders its `resolved_scope_key`, `source_reference` and `source_version` without
  rewriting them. A fallback therefore shows requested `form-NNN` and resolved
  `ALL-22` together; `ALL-22` is source provenance and is never presented as the
  requested form scope.
- An unresolved row keeps its requested scope visible, renders the exact source error
  code alongside the following Simplified-Chinese reason, and does not invent resolved
  scope or source fields:

| Source code | Exact Simplified-Chinese reason |
| --- | --- |
| `DECISION_GATE_NOT_FOUND` | `未找到适用的客户决策` |
| `DECISION_GATE_REVOKED` | `客户决策已撤销` |
| `DECISION_GATE_NOT_EFFECTIVE` | `客户决策尚未生效` |
| `DECISION_GATE_CANDIDATE_MULTIPLICITY` | `存在多个候选客户决策` |
| `DECISION_GATE_CURRENT_IDENTITY_CONFLICT` | `当前客户决策标识冲突` |
| `DECISION_GATE_CURRENT_ROW_CORRUPT` | `当前客户决策记录损坏` |
| `DECISION_GATE_LEGACY_MAP_CORRUPT` | `历史表单分类映射损坏` |

The rendered reason format is `<中文原因>（<source code>）`; the source code MUST remain
visible for support and audit use.

### Resolved legacy classifications and activation boundary

- `HISTORICAL` and `INTERNAL_ONLY` remain source-backed `RESOLVED` values. Render their
  original value and both Simplified-Chinese markers `仅供参考` and `非激活`; do not
  relabel either value as unresolved or activation-ready.
- Only `CURRENT_OFFICIAL` may render the marker `可供后续激活`. That marker describes
  server-provided readiness only. This UI provides no activation control and issues no
  mutation request, even for `CURRENT_OFFICIAL`.
- Do not infer a classification, activation state, fallback, resolved scope or warning
  from gate code, form number, missing data or another row.

### Warning presentation boundary

- Render top-level `warnings` as the current page/snapshot warning group and each
  milestone's `warnings` inside that milestone's activity-local group. Do not merge,
  move, code-deduplicate or count one group as the other.
- Render warning kinds with these Simplified-Chinese labels:
  `UNVERIFIED` as `未核验`, `CUSTOMER_DECISION_GATE` as `客户待确认`, `CONFLICT` as
  `来源冲突`, and `REFERENCE_ONLY` as `仅供参考`. Preserve each warning's server
  message and source/activity provenance; do not hide a warning as an empty state.

## Explicit Non-Closure

No backend/adapter change, gate confirmation or revocation, lane activation, warning aggregation rule, second page capability or frontend business-state calculation. No POST, PUT, PATCH or DELETE request is authorized. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-CASEDETAIL-THREE-LANE-LAYOUT-20260712-01`
- `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): layout; overlay FE adapter; serialized

### Shared ownership serialization

- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01.md`
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
- `artifacts/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Exact Playwright Acceptance

`FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts`
MUST prove through the case-detail UI:

1. The component renders exactly 29 gate rows in server order: seven distinct
   non-legacy entries followed by 22 `DG-LEGACY-FORM-CLASS` rows for ascending
   `form-001..form-022`.
2. At least two legacy rows retain the same visible gate code while showing distinct
   requested form scopes, proving there is no gate-code-only deduplication.
3. An unresolved legacy row shows its requested `form-NNN`, the exact Simplified-Chinese
   reason and the unchanged source error code.
4. A resolved direct legacy row shows its requested scope plus unchanged source
   reference/version. A fallback row simultaneously shows requested `form-NNN` and
   resolved `ALL-22`, with the source provenance retained and no requested `ALL-22` row.
5. `HISTORICAL` and `INTERNAL_ONLY` each show `仅供参考` and `非激活`;
   `CURRENT_OFFICIAL` may show `可供后续激活`, but none exposes or performs activation.
6. Top-level and milestone warning fixtures remain in distinct visible groups, retain
   their own provenance/messages and use the exact Simplified-Chinese kind labels.
7. A request spy observes only the read needed to load the page/overlay and zero POST,
   PUT, PATCH or DELETE requests during rendering and gate/warning interaction.

The RED is a missing named visible behavior, composite-identity loss or prohibited
mutation. GREEN does not require the later cursor/load-more task and does not activate or
record any decision.

## Verification Commands

- RED command: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-gates-warnings.spec.ts --workers=1`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-case-detail-gates-warnings.spec.ts --workers=1`
- `cd frontend && npx eslint src/modules/cases/components/CaseLifecycleOverlay.vue --max-warnings 0`
- `git diff --check -- frontend/src/modules/cases/components/CaseLifecycleOverlay.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts tasks/postdemo/v8/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01` pass. Only then may this task be reported PASS.
