# Case List Lifecycle Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make case-list and dashboard status wording consistent with the authoritative lifecycle projection while preserving the legacy workflow-status contract and the existing case-detail display.

**Architecture:** Extend the existing `CaseListItem` projection at its current service seam; do not add a query, table, endpoint, or state adapter. Map the additive fields through the existing frontend case mapper, then apply list-only stage wording while keeping `getCaseWorkflow()` and `CaseStepper.vue` unchanged.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy 2, pytest, Vue 3, TypeScript, Node source-contract tests, vue-tsc.

---

## Frozen inputs and file map

- Approved design: `docs/superpowers/specs/2026-08-28-case-list-lifecycle-projection-design.md`;
  the user approved baseline commit `814523a`, and the later metadata-only status update records that approval.
- Atomic task: `tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01.md`.
- Existing unrelated dirty file: `docs/postdemo/demo-v6-colleague-clone-start-guide.md`; never stage, edit, or absorb it.

| Responsibility | File |
| --- | --- |
| List response schema | `backend/app/modules/cases/schemas.py` |
| Actual list-item assembly | `backend/app/modules/cases/service.py` |
| Backend regression contract | `backend/tests/test_v3_workflow.py` |
| Backend-to-frontend mapping | `frontend/src/api/cases.ts` |
| Public frontend case type | `frontend/src/api/cases.types.ts` |
| Existing five-step status rules | `frontend/src/constants/workflow.ts` |
| Customer-visible workflow labels | `frontend/src/constants/labels.zh.ts` |
| Complete case list | `frontend/src/modules/cases/pages/CaseList.vue` |
| Dashboard grouping and card labels | `frontend/src/modules/dashboard/dashboard.api.ts` |
| Dashboard stage table | `frontend/src/modules/dashboard/components/WorkflowCaseTable.vue` |
| Focused frontend regression contract | `frontend/tests/case-list-lifecycle-projection-contract.mjs` |

Do not modify `backend/app/modules/cases/api.py`, `CaseStepper.vue`, lifecycle writers, models,
migrations, seeds, runbooks, or Playwright suites.

### Task 0: Establish the atomic execution baseline

**Files:**
- Read: `tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01.md`
- Evidence: `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/**`

- [ ] **Step 1: Confirm branch and preserved dirty baseline**

Run:

```bash
git branch --show-current
git status --short
```

Expected: branch is `codex/post-v6-mainpath-20260828`; the colleague guide may be untracked
and no unapproved product file is dirty.

- [ ] **Step 2: Start the task through the repository controller**

Run:

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 start \
  --task-file tasks/postdemo/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01.md
```

Expected: task enters `IMPLEMENTING`; the controller validates the contract and records the
pre-existing colleague guide as outside dirt without absorbing it.

### Task 1: Project the existing backend facts through the list API

**Files:**
- Modify: `backend/tests/test_v3_workflow.py`
- Modify: `backend/app/modules/cases/schemas.py`
- Modify: `backend/app/modules/cases/service.py`

- [ ] **Step 1: Write the failing list projection test**

Add this test to `TestCaseListFields`:

```python
def test_list_projects_workflow_status_lifecycle_axes_and_updated_at(
    self, client, auth_headers, session_factory
) -> None:
    from app.modules.cases.models import Case

    case_no = f"V3-LIFECYCLE-{uuid4().hex[:8]}"
    case_id = _create_case_via_orm(
        session_factory,
        case_no=case_no,
        status="GRANT_PENDING",
    )
    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        case.business_stage = "GRANT_REGISTRATION_IN_PROGRESS"
        case.official_procedure_stage = "GRANT_REGISTRATION"
        case.legal_status = "APPLICATION_PENDING"
        db.commit()

    response = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)

    assert response.status_code == 200, response.text
    item = response.json()["items"][0]
    assert item["status"] == "GRANT_PENDING"
    assert item["workflow_status"] == item["status"]
    assert item["business_stage"] == "GRANT_REGISTRATION_IN_PROGRESS"
    assert item["official_procedure_stage"] == "GRANT_REGISTRATION"
    assert item["legal_status"] == "APPLICATION_PENDING"
    assert item["updated_at"]
    assert item["filing_date"] is None
```

- [ ] **Step 2: Run the test to verify RED**

Run:

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  backend-test red -- -q \
  tests/test_v3_workflow.py::TestCaseListFields::test_list_projects_workflow_status_lifecycle_axes_and_updated_at
```

Expected: FAIL because `CaseListItem` and list assembly do not yet expose the five fields.

- [ ] **Step 3: Extend only the list response schema**

Add to `CaseListItem` immediately after `status`:

```python
workflow_status: str
business_stage: str | None = None
official_procedure_stage: str | None = None
legal_status: str | None = None
updated_at: str | None = None
```

Do not change the detail schema, model, endpoint wrapper, query parameters, or response
envelope.

- [ ] **Step 4: Project the existing columns at the service assembly seam**

In the existing `CaseListItem(...)` construction in `list_cases`, add:

```python
workflow_status=case.status,
business_stage=case.business_stage,
official_procedure_stage=case.official_procedure_stage,
legal_status=case.legal_status,
updated_at=case.updated_at.isoformat() if case.updated_at else None,
```

No join or lifecycle event scan is needed because all values already exist on `t_case`.

- [ ] **Step 5: Run the single canonical backend GREEN**

Run:

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  backend-test test -- -q \
  tests/test_v3_workflow.py \
  tests/test_pd_p1_case_official_fields_api.py
```

Expected: both focused backend files pass under the serialized SQLite lease. Do not run a
second canonical `test` later unless backend-owned files change after this result.

- [ ] **Step 6: Inspect the backend slice without committing**

Run `git diff -- backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_v3_workflow.py` and confirm every changed line belongs to the frozen projection. Keep the implementation uncommitted so canonical scope can capture it later.

### Task 2: Map the additive frontend case contract with old-server fallback

**Files:**
- Create: `frontend/tests/case-list-lifecycle-projection-contract.mjs`
- Modify: `frontend/src/api/cases.ts`
- Modify: `frontend/src/api/cases.types.ts`

- [ ] **Step 1: Create the executable mapper contract test**

Create `frontend/tests/case-list-lifecycle-projection-contract.mjs` with the mapper portion:

```javascript
import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const casesApi = read('src/api/cases.ts')
const casesTypes = read('src/api/cases.types.ts')

function importFunction(source, name) {
  const sourceFile = ts.createSourceFile('contract.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const declaration = sourceFile.statements.find(
    (statement) => ts.isFunctionDeclaration(statement) && statement.name?.text === name,
  )
  assert.ok(declaration, `missing executable function: ${name}`)
  const compiled = ts.transpileModule(
    `${declaration.getText(sourceFile)}\nexport { ${name} }`,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

const { mapCase } = await importFunction(casesApi, 'mapCase')
const projected = mapCase({
  id: 'case-1', case_no: 'CYIP-CN-INV-1', client_id: null,
  status: 'GRANT_PENDING', workflow_status: 'GRANT_PENDING',
  business_stage: 'GRANT_REGISTRATION_IN_PROGRESS',
  official_procedure_stage: 'GRANT_REGISTRATION',
  legal_status: 'APPLICATION_PENDING', updated_at: '2026-08-28T10:00:00',
})
assert.equal(projected.workflow_status, 'GRANT_PENDING')
assert.equal(projected.business_stage, 'GRANT_REGISTRATION_IN_PROGRESS')
assert.equal(projected.official_procedure_stage, 'GRANT_REGISTRATION')
assert.equal(projected.legal_status, 'APPLICATION_PENDING')
assert.equal(projected.updated_at, '2026-08-28T10:00:00')

const legacy = mapCase({ id: 'case-2', case_no: 'LEGACY-2', client_id: null, status: 'PUBLISHED', updated_at: null })
assert.equal(legacy.workflow_status, 'PUBLISHED')
assert.equal(legacy.updated_at, '')
for (const field of ['workflow_status', 'business_stage', 'official_procedure_stage', 'legal_status']) {
  assert.match(casesTypes, new RegExp(`${field}\\?: string`))
}
```

- [ ] **Step 2: Run the mapper contract to verify RED**

Run:

```bash
node frontend/tests/case-list-lifecycle-projection-contract.mjs
```

Expected: FAIL because mapped cases lack `workflow_status` and lifecycle-axis fields.

- [ ] **Step 3: Add the backend response fields and public case fields**

In `BackendCase`, add nullable optional response fields:

```typescript
workflow_status?: string | null
business_stage?: string | null
official_procedure_stage?: string | null
legal_status?: string | null
```

Change `updated_at?: string` to `updated_at?: string | null`. In public `Case`, add:

```typescript
workflow_status?: string
business_stage?: string
official_procedure_stage?: string
legal_status?: string
```

Keep public `created_at` and `updated_at` as required strings for compatibility.

- [ ] **Step 4: Extend `mapCase` without changing existing consumers**

Add these properties beside the existing `status` mapping:

```typescript
workflow_status: input.workflow_status || input.status || undefined,
business_stage: input.business_stage || undefined,
official_procedure_stage: input.official_procedure_stage || undefined,
legal_status: input.legal_status || undefined,
```

Retain the existing `updated_at: input.updated_at || ''` normalization and existing
`status` mapping.

- [ ] **Step 5: Run mapper GREEN and typecheck**

Run:

```bash
node frontend/tests/case-list-lifecycle-projection-contract.mjs
PATH="frontend/node_modules/.bin:$PATH" \
  ./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  record frontend_typecheck_pre_ui -- vue-tsc --noEmit -p frontend/tsconfig.json
```

Expected: mapper contract prints no assertion error and vue-tsc exits 0.

- [ ] **Step 6: Inspect the frontend data slice without committing**

Run `git diff -- frontend/src/api/cases.ts frontend/src/api/cases.types.ts frontend/tests/case-list-lifecycle-projection-contract.mjs` and confirm it only adds the approved mapping and fallback. Keep the implementation uncommitted for canonical scope.

### Task 3: Correct list and dashboard semantics without touching case detail

**Files:**
- Modify: `frontend/tests/case-list-lifecycle-projection-contract.mjs`
- Modify: `frontend/src/constants/workflow.ts`
- Modify: `frontend/src/constants/labels.zh.ts`
- Modify: `frontend/src/modules/cases/pages/CaseList.vue`
- Modify: `frontend/src/modules/dashboard/dashboard.api.ts`
- Modify: `frontend/src/modules/dashboard/components/WorkflowCaseTable.vue`

- [ ] **Step 1: Extend the frontend contract with UI and non-regression assertions**

Append source reads and focused assertions:

```javascript
const workflow = read('src/constants/workflow.ts')
const labels = read('src/constants/labels.zh.ts')
const caseList = read('src/modules/cases/pages/CaseList.vue')
const dashboardApi = read('src/modules/dashboard/dashboard.api.ts')
const workflowTable = read('src/modules/dashboard/components/WorkflowCaseTable.vue')
const caseStepper = read('src/modules/cases/components/CaseStepper.vue')

assert.match(workflow, /GRANT_PENDING:.*stepText: '授权登记'/)
assert.match(workflow, /stepLabel: WORKFLOW_STEPS\[stepIndex\]\.label/)
assert.match(workflow, /stepNoText: `第\$\{stepIndex \+ 1\}步\/5`/)
assert.match(labels, /filterStatus: '流程状态'/)
assert.match(labels, /colStep: '当前阶段'/)
assert.match(labels, /colStatus: '流程状态'/)
assert.match(labels, /grantStage: '授权阶段'/)
for (const source of [caseList, workflowTable]) {
  assert.match(source, /c\.workflow_status \|\| c\.status/)
  assert.match(source, /flow\.rule\.stepText/)
  assert.match(source, /第\$\{flow\.stepIndex \+ 1\}阶段\/5/)
}
assert.match(caseList, /row\.filing_date \|\| '待录入'/)
assert.equal(dashboardApi.match(/getStatusRule\(c\.workflow_status \|\| c\.status\)/g)?.length, 2)
assert.match(dashboardApi, /step\.key === 'GRANTED' \? ZH\.workflow\.grantStage : step\.label/)
assert.match(caseStepper, /getCaseWorkflow\(props\.status\)/)
assert.doesNotMatch(caseStepper, /workflow_status|授权阶段|阶段\/5/)
console.log('case list lifecycle projection contract: PASS')
```

- [ ] **Step 2: Run the expanded contract to verify RED**

Run:

```bash
node frontend/tests/case-list-lifecycle-projection-contract.mjs
```

Expected: FAIL on old labels and status consumers.

- [ ] **Step 3: Change only the approved shared labels and status rule**

In `ZH.workflow`, add `filterStatus: '流程状态'` and `grantStage: '授权阶段'`; change
`colStep` to `当前阶段` and `colStatus` to `流程状态`. Change only
`STATUS_STEP_MAP.GRANT_PENDING.stepText` from `授权` to `授权登记`.

Do not change `WORKFLOW_STEPS`, `getCaseWorkflow()`, `ZH.stepper`, or `CaseStepper.vue`.

- [ ] **Step 4: Apply list-local workflow presentation**

In both list components, add a local workflow-status selector and keep it unabstracted:

```typescript
function getWorkflowStatus(c: Case) {
  return c.workflow_status || c.status
}

function getFlow(c: Case) {
  const flow = getCaseWorkflow(getWorkflowStatus(c))
  return {
    ...flow,
    stepLabel: flow.rule.stepText,
    stepNoText: `第${flow.stepIndex + 1}阶段/5`,
  }
}
```

Use `getWorkflowStatus(c)` for local filtering and tag classes. In `CaseList.vue` also:

- bind the filter label to `ZH.workflow.filterStatus`;
- use “阶段” in the step-filter subtitle;
- display `row.filing_date || '待录入'`;
- keep `formatDate(row.updated_at)` unchanged.

- [ ] **Step 5: Update dashboard grouping and card label projection**

Import `ZH` into `dashboard.api.ts`. In both `fetchWorkflowStats` and
`filterCasesByStep`, replace `getStatusRule(c.status)` with:

```typescript
getStatusRule(c.workflow_status || c.status)
```

When mapping step stats, set only the fifth card label locally:

```typescript
label: step.key === 'GRANTED' ? ZH.workflow.grantStage : step.label,
```

This must not mutate `WORKFLOW_STEPS`.

- [ ] **Step 6: Run UI GREEN checks**

Run:

```bash
node frontend/tests/case-list-lifecycle-projection-contract.mjs
PATH="frontend/node_modules/.bin:$PATH" \
  ./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  record frontend_typecheck -- vue-tsc --noEmit -p frontend/tsconfig.json
```

Expected: contract prints `case list lifecycle projection contract: PASS`; vue-tsc exits 0.

- [ ] **Step 7: Inspect the complete frontend slice without committing**

Review the frontend diff and confirm `CaseStepper.vue`, `WORKFLOW_STEPS`, routes, requests,
and lifecycle writers are unchanged. Keep all implementation changes uncommitted until
canonical scope, review, and terminal close finish.

### Task 4: Bind canonical evidence, independent review, and terminal close

**Files:**
- Review: all allowed product and test files
- Evidence: `artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/**`

- [ ] **Step 1: Record the single canonical scoped lint**

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  record lint -- ruff check \
  backend/app/modules/cases/schemas.py \
  backend/app/modules/cases/service.py \
  backend/tests/test_v3_workflow.py
```

Expected: Ruff exits 0. The canonical backend `test` result already exists from Task 1;
frontend contract and typecheck results already exist from Task 3. Do not overwrite them
without a corresponding file change.

- [ ] **Step 2: Record the non-canonical whitespace diagnostic**

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  record whitespace -- git diff --check
```

Expected: exits 0.

- [ ] **Step 3: Record the single canonical scope result**

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  record scope -- python3 scripts/evidence_scope.py finalize \
  FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01
```

Expected: only allowed files appear in the baseline-subtracted patch; the colleague guide
remains recorded as outside dirt and is absent from the candidate patch.

- [ ] **Step 4: Materialize the factual candidate summary**

Create this file with `apply_patch` after reading the actual result logs:

`artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/summary.md`

Use this structure, replacing every bracketed value with observed facts and never claiming
a result that did not run:

```markdown
# FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 Summary

## Status

- Candidate status: AWAITING INDEPENDENT REVIEW
- Runbook: P0-single-lane-story
- Risk: contract-frozen HIGH API/lifecycle/legal/UI projection

## Exact closure slice

- [actual additive backend projection]
- [actual frontend compatibility mapping]
- [actual list/dashboard wording result]

## Modified files

- [exact baseline-subtracted paths]

## Verification

- Backend canonical test: rc=[actual], log=[actual]
- Frontend contract: rc=[actual direct diagnostic]
- Frontend typecheck: rc=[actual], log=[actual]
- Canonical lint: rc=[actual], log=[actual]
- Canonical scope: rc=[actual], log=[actual]

## Scope and non-closure

- No migration, lifecycle write, application-date inference, case-detail change, seed,
  runbook, fee-chain, deployment, or unrelated cleanup.
- The pre-existing colleague guide remains outside the candidate.
```

Expected: `summary.md` exists and accurately matches the latest command results and scoped
patch. Do not edit it after candidate preparation.

- [ ] **Step 5: Freeze the candidate for review**

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 prepare-review
```

Expected: task enters `READY_FOR_REVIEW` with candidate patch and hashes frozen.

- [ ] **Step 6: Obtain independent zero-finding review**

Grant the named reviewer lease:

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  review lease independent --reviewer case-status-projection-independent-r1
```

Give that reviewer only the approved design, atomic task, frozen candidate diff, and latest
results. The reviewer writes:

`artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/review/independent_review.md`

The report must bind the frozen hashes and contain exactly one final `Verdict: APPROVED`,
`P0: 0`, `P1: 0`, and `P2: 0`. Submit it through the controller:

```bash
TASKCTL_ACTOR=case-status-projection-independent-r1 \
  ./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 \
  review submit independent \
  --report artifacts/FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01/review/independent_review.md
```

Any finding returns the task to the bounded fix-and-reverify loop; do not edit a frozen
candidate behind the review lease.

- [ ] **Step 7: Run repository close and terminal doctor**

```bash
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 close
./scripts/taskctl FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01 doctor
```

Expected: close runs task gate and atomic-evidence checks, then doctor reports terminal PASS.
Do not run broad Playwright, full product tests, deployment, seed reset, or release gates in
this task.

- [ ] **Step 8: Commit the already accepted implementation**

Only after terminal PASS, stage the exact allowed product and test files and commit once:

```bash
git add backend/app/modules/cases/schemas.py \
  backend/app/modules/cases/service.py \
  backend/tests/test_v3_workflow.py \
  frontend/src/api/cases.ts \
  frontend/src/api/cases.types.ts \
  frontend/src/constants/workflow.ts \
  frontend/src/constants/labels.zh.ts \
  frontend/src/modules/cases/pages/CaseList.vue \
  frontend/src/modules/dashboard/dashboard.api.ts \
  frontend/src/modules/dashboard/components/WorkflowCaseTable.vue \
  frontend/tests/case-list-lifecycle-projection-contract.mjs
git commit -m "fix(cases): clarify lifecycle list status"
```

Expected: the commit contains the same bytes accepted by terminal PASS; the colleague guide
remains untracked.

## Expected final state

- One post-PASS implementation commit, so the pre-commit candidate diff remains available
  to canonical scope and independent review.
- No migration or lifecycle write.
- No case-detail presentation change.
- The pre-existing colleague guide remains untouched and uncommitted.
- Task closes only with focused PASS results, exact scope evidence, and independent review.
