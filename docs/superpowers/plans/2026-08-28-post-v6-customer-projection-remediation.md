# Post-V6 Customer Projection Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the case-detail gate, real fee obligations, and expanded lifecycle history customer-readable without changing any lifecycle, gate, fee, payment, document, or lineage fact.

**Architecture:** Keep all existing API calls and payload ownership. Add deterministic display-only stage applicability, Chinese mappings, date formatting, list/obligation deduplication, and collapsed audit disclosures in the existing Vue presentation layer. Execute one serialized frontend-heavy task because `lifecycleOverlayDisplay.ts` is shared by the fee tab and detailed history lanes.

**Tech Stack:** Vue 3 `<script setup>` + TypeScript, Element Plus, existing lifecycle-overlay types, Playwright mock/live harnesses, Node static UI contracts, FPMS atomic evidence controller.

---

## Approved Inputs and Fixed Boundaries

- Approved design commit: `ed61376`.
- Approved design:
  `docs/superpowers/specs/2026-08-28-post-v6-customer-projection-remediation-design.md`.
- Implementation task ID: `FE-POST-V6-CUSTOMER-PROJECTION-20260828-01`.
- Use `@karpathy-guidelines`, `@superpowers:test-driven-development`,
  `@superpowers:verification-before-completion`, and `@atomic-evidence-gates` during execution.
- Preserve the current endpoint responses, mutation payloads, idempotency behavior, case stages,
  document gate result, evidence versions, fee obligation amounts, statuses, and ordering.
- Do not add a backend gate kind, authorization-specific gate, presentation DTO, store, composable,
  generic i18n framework, database field, seed value, request, retry, or business calculation.
- The existing untracked `docs/postdemo/demo-v6-colleague-clone-start-guide.md` is user-owned
  external dirt. Record it at task start and never stage, modify, delete, or absorb it.

## File Responsibility Map

### Create

- `tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md`
  - Freezes the exact implementation closure, allowlist, evidence commands, and stop conditions.
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts`
  - Covers current, historical, missing, conflicting, and future-unknown stage applicability.

### Modify: product presentation

- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
  - Retains case metadata, derives the three gate presentation modes, and separates generic document
    registration from stage-specific gate actions.
- `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
  - Owns exact Chinese mappings, safe fallbacks, date formatting, stable code dedupe, currency text,
    and latest fee-obligation projection.
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
  - Adds the shared historical-fact boundary message inside the existing disclosure.
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
  - Shows business labels by default and raw identifiers/codes only in collapsed audit disclosures.
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
  - Applies display-only timestamp formatting.
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
  - Shows the full seven-status customer card, labelled fee lines, and collapsed audit details.
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
  - Reuses the latest-obligation projection and customer/audit hierarchy while preserving all
    instruction actions and retry semantics.

### Modify: focused contracts

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts`
  - Its initial-filing case assertion changes from the removed generic “当前节点文件材料” label to
    the approved current-initial-filing label; no setup, mutation, or other assertion changes.
- `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`
  - Imports the relocated shared obligation projection and binds customer/audit display requirements.

### Verification only; do not modify

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- `scripts/run_demo_integrated_a_rehearsal.py`

No other path is authorized. If an existing focused test directly contradicts the approved copy and
is not listed above, stop and amend the task contract before editing it.

## Task 1: Materialize and Start the Atomic Product Task

**Files:**

- Create: `tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md`

- [ ] **Step 1: Write the exact task contract**

Use:

```markdown
Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
Chosen runbook: `P0-frontend-heavy-story`
```

Exact closure is the three presentation slices in this plan. Explicit non-closure repeats the
approved backend/API/schema/database/seed/runbook/business-fact exclusions. Allowed files are the
task file, the seven product files, six focused test files, the static contract, and
`artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/**`.

- [ ] **Step 2: Commit the task contract before evidence initialization**

```bash
git diff --check -- tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md
git add tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md
git commit -m "docs(cases): freeze customer projection task"
```

Expected: one task-contract commit. This ordering ensures the task file is not mistakenly captured
as an untracked dirty baseline.

- [ ] **Step 3: Initialize evidence**

```bash
./scripts/taskctl FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 start \
  --task-file tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md
```

Expected: state `IMPLEMENTING`; allowlist baseline is clean; external baseline contains only
`docs/postdemo/demo-v6-colleague-clone-start-guide.md`.

- [ ] **Step 4: Freeze the canonical evidence commands in the task file**

Record these exact final commands:

```bash
./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 lint git diff --check -- frontend/src/modules/cases/components/CaseDocumentsTab.vue frontend/src/modules/cases/components/CaseFeesTab.vue frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md
./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 test shasum -a 256 frontend/src/modules/cases/components/CaseDocumentsTab.vue frontend/src/modules/cases/components/CaseFeesTab.vue frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs tasks/frontend/cases/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01.md artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/typecheck.log artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/eslint.log artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/build.log artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/static-contract.log artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/gate-green/index.html artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/history-green/index.html artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/fee-green/index.html artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/focused-final/index.html artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/strict-pass-receipt.json artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/network-errors.json artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/console-errors.json artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass/run1/playwright.log
./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 scope python3 scripts/evidence_scope.py finalize FE-POST-V6-CUSTOMER-PROJECTION-20260828-01
```

The Playwright/typecheck/eslint/build commands run normally and retain logs. The `test` shasum binds
their final artifacts because the evidence controller permits only check-only generic commands.

## Task 2: RED and GREEN the Gate Applicability Projection

**Files:**

- Create: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts`
- Modify: `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts`

- [ ] **Step 1: Write the five-mode RED fixture matrix**

Mock the existing case, document-gate, and documents GETs. Reuse one `BLOCKED` gate payload and vary
only `business_stage` and `official_procedure_stage`:

```ts
const cases = [
  ['current', 'FILING_PREPARATION', 'NOT_SUBMITTED'],
  ['historical', 'GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION'],
  ['missing', undefined, 'GRANT_REGISTRATION'],
  ['conflicting', 'FILING_PREPARATION', 'GRANT_REGISTRATION'],
  ['future', 'FUTURE_BUSINESS_STAGE', 'FUTURE_OFFICIAL_STAGE'],
] as const
```

Assert:

- current: “当前首次申请递交门禁”, error severity, gate action, and generic toolbar registration;
- historical: “当前阶段：授权登记”, “历史首次申请递交材料核验”, historical rule conclusion,
  stage-derived non-current explanation, no gate-card filing action, and generic toolbar registration;
- missing/conflicting/future: neutral “适用阶段待确认”, no fabricated PASS, no current/historical
  applicability, and no raw future code as a known stage;
- case GET failure with a successful gate GET: neutral “适用阶段待确认”, the gate fetch result is
  not relabelled as current or historical, and the existing metadata error remains visible;
- every mode makes exactly one case GET, one gate GET, and one documents GET; no mutation.

- [ ] **Step 2: Run RED**

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/gate-red" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-document-gate-applicability.spec.ts
```

Expected: FAIL because `CaseDocumentsTab.vue` still labels every result as current.

- [ ] **Step 3: Retain case metadata and derive a closed-set mode**

In `CaseDocumentsTab.vue`:

```ts
type GatePresentationMode =
  | 'CURRENT_INITIAL_FILING'
  | 'HISTORICAL_INITIAL_FILING'
  | 'APPLICABILITY_UNKNOWN'

const caseData = ref<Case | null>(null)

const INITIAL_BUSINESS_STAGES = new Set(['NEW_CASE', 'FILING_PREPARATION'])
const POST_BUSINESS_STAGES = new Set([
  'WAITING_EXTERNAL_RECEIPT',
  'PROSECUTION_MANAGEMENT',
  'OA_REPLY_IN_PROGRESS',
  'GRANT_REGISTRATION_IN_PROGRESS',
  'POST_GRANT_MAINTENANCE',
  'CLOSED',
])
const POST_OFFICIAL_STAGES = new Set([
  'SUBMITTED_WAITING_RECEIPT',
  'SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE',
  'ACCEPTED',
  'PRELIMINARY_EXAMINATION',
  'RECTIFICATION_RESPONSE',
  'PUBLISHED',
  'SUBSTANTIVE_EXAMINATION',
  'OFFICE_ACTION_RESPONSE',
  'REEXAMINATION',
  'GRANT_REGISTRATION',
  'GRANT_ANNOUNCED',
  'PROCEDURE_CLOSED',
])
```

Return current only for recognized initial business + `NOT_SUBMITTED`, historical only for
recognized post business + post official, otherwise unknown. Do not inspect enum ordering,
`status`, or `workflow_status`.

- [ ] **Step 4: Project headings, severity, and actions without mutating the gate**

- Store the returned case object and continue using its `case_no` for navigation.
- Keep the page-toolbar `登记往来文件` button in every mode.
- In historical mode, render returned checks with historical labels, use an info alert, attribute
  `BLOCKED` to the initial-filing rule, and replace the gate action area with the approved explanation.
- In unknown mode, use neutral warning language and no stage-specific action.
- In current mode, keep the current severity and suggested actions unchanged.
- A case metadata failure selects unknown; a gate failure keeps the existing error.

- [ ] **Step 5: Run GREEN and the real-API compatibility assertion**

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/gate-green" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-document-gate-applicability.spec.ts
```

Expected: PASS. Update only the two obsolete gate-heading assertions in `casedock-real-api.spec.ts`
to the approved current-initial-filing copy; retain every setup, response, impact-preview, and
batch-filing assertion.

- [ ] **Step 6: Commit the gate slice**

```bash
git diff --check -- frontend/src/modules/cases/components/CaseDocumentsTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts
git add frontend/src/modules/cases/components/CaseDocumentsTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/casedock-real-api.spec.ts
git commit -m "fix(cases): contextualize filing material gate"
```

## Task 3: RED and GREEN the Expanded-History Customer Projection

**Files:**

- Modify: `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
- Modify: `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- Modify: `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- Modify: `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- Modify: `frontend/src/modules/cases/components/FeeObligationLane.vue`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`

- [ ] **Step 1: Turn current raw-value assertions into RED customer/audit assertions**

In the existing fixtures, include:

- duplicated `CHECKLIST_INCOMPLETE` and `MANIFEST_MISSING` codes;
- known and unknown evidence/work-package/receipt/task codes;
- UUID-shaped document, attachment, package, receipt, and obligation identifiers;
- hashes and source snapshots;
- ISO timestamps with fractional seconds;
- GOV and SERVICE obligations, one repeated in a later milestone with updated statuses.

Before opening any `审计信息`, assert known Chinese labels, one occurrence per missing-gate meaning,
customer-formatted timestamps, exactly one card per obligation, and no raw ID/hash/code visible.
After opening the relevant disclosure, assert the exact raw values are visible. Unknown values show
`待确认` by default and their raw code only after disclosure.

- [ ] **Step 2: Run the three-lane RED suite**

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/history-red" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-overlay-document-lane.spec.ts \
  src/tests/v8-overlay-center-lane.spec.ts \
  src/tests/v8-overlay-fee-lane.spec.ts
```

Expected: FAIL on raw default content, duplicate gate codes, ISO timestamps, and missing audit
disclosures.

- [ ] **Step 3: Add only the approved shared display functions**

Extend `lifecycleOverlayDisplay.ts` with exact closed maps and these small functions:

```ts
export function overlayDateText(value: string | null): string
export function currencyText(value: string | null): string
export function evidenceRoleText(value: string | null): string
export function evidenceStateText(value: string | null): string
export function evidenceReviewText(value: string | null): string
export function derivationTypeText(value: string | null): string
export function workPackageKindText(value: string | null): string
export function workPackageStatusText(value: string | null): string
export function receiptKindText(value: string | null): string
export function taskStatusText(value: string | null): string
export function missingGateText(value: string | null): string
export function uniqueCodes(values: readonly string[]): readonly string[]
export function latestObligationsById(
  milestones: readonly OverlayMilestone[],
): readonly OverlayFeeObligation[]
```

Use the exact mappings approved in the design. `overlayDateText` performs lexical formatting only:
`YYYY-MM-DDTHH:mm:ss...` becomes `YYYY-MM-DD HH:mm`; it does not construct `Date` or shift timezone.
`uniqueCodes` preserves first occurrence. Unknown customer values return `待确认`; raw input is
passed separately to audit markup. `latestObligationsById` moves the existing related-fact merge
unchanged and lets later milestone occurrences win.

Freeze the display vocabulary below. These labels are a presentation projection of existing typed
values and existing V6 UI vocabulary; the implementation must not add synonyms or infer meanings.
Any value not listed uses the approved unknown fallback and remains raw only inside `审计信息`.

| Value family | Exact customer mapping |
| --- | --- |
| evidence role | `FILING_FULL_WORD` → `申请文件完整 Word`；`TRACKED_REVISED_WORD` → `修订留痕 Word`；`FILING_COMPONENT` → `申请文件组成部分`；`EXTERNAL_XML_PACKAGE` → `外部递交 XML 包`；`OFFICIAL_SUBMISSION_LIST` → `官方递交清单`；`OFFICIAL_FINAL_PDF` → `最终递交 PDF`；`SUBMITTED_XML` → `已递交 XML`；`OFFICIAL_RECEIPT` → `官方回执`；`CLIENT_LETTER_WORD` → `客户函 Word`；`RAW_ATTACHMENT` → `原始附件`；`GENERATED_ATTACHMENT` → `生成附件`；`OA_STRUCTURED_ATTACHMENT` → `审查意见结构化附件` |
| evidence version state | `DRAFT` → `草稿`；`FINAL` → `已定稿` |
| evidence review state | `PENDING` → `待复核`；`APPROVED` → `已复核`；`REJECTED` → `复核未通过` |
| derivation type | `REVISION` → `版本修订`；`COMPONENT_EXTRACTION` → `组成部分提取`；`FORMAT_CONVERSION` → `格式转换`；`OFFICIAL_RECOGNITION` → `官方文件识别`；`EXTERNAL_SUBMISSION` → `外部递交`；`RECEIPT_LINK` → `回执关联`；`CUSTOMER_LETTER_RENDER` → `客户函生成`；`OA_REPLY_PREPARATION` → `审查意见答复准备` |
| work-package kind | `FILING_PREP` → `新申请递交`；`OA_REPLY` → `审查意见答复` |
| work-package state | `PREPARING` → `准备中`；`NEEDS_MAINTENANCE` → `需维护`；`NEEDS_CONFIRMATION` → `待确认`；`READY_FOR_EXTERNAL_SUBMIT` → `可人工提交`；`SUBMITTED` → `已提交`；`WAITING_RECEIPT` → `待回执`；`ARCHIVED` → `已归档`；`EXCEPTION` → `异常`；`OVERRIDE` → `已例外处理` |
| receipt kind / archive | `RECEIPT_PDF` → `回执 PDF`；`MERGED_PDF` → `合并 PDF`；`ELECTRONIC_APPLICATION_RECEIPT` → `电子申请回执`；`ARCHIVED` → `已归档`；`PENDING` → `待归档` |
| task state | `OPEN` → `待处理`；`DONE` → `已完成`；`CANCELLED` → `已取消` |
| missing gate | `CHECKLIST_INCOMPLETE` → `递交检查清单未完成`；`MANIFEST_MISSING` → `递交文件清单缺失`；`RECEIPT_MISSING` → `回执缺失` |
| fee domain / type | `GOV` → `官费`；`SERVICE` → `服务费`；`OFFICIAL_FEE` → `官费缴费义务`；`GRANT_REGISTRATION_OFFICIAL_FEES` → `授权登记官费义务`；`SERVICE_FEE` → `服务费应收义务` |
| fee source / difference | `VERIFIED` → `已核验`；`REVIEW_REQUIRED` → `需复核`；`LEGACY_UNVERIFIED` → `历史数据待核验`；`MATCHED` → `一致`；`SOURCE_PENDING` → `来源待确认` |
| seven fee statuses | null estimate → `暂无`；`ESTIMATE` → `估算`；`RECOGNIZED` → `已确认`；`SUPERSEDED` → `已被替代`；`PENDING` → `待处理`；`PAY` → `缴费`；`HOLD` → `暂缓`；`ABANDON` → `放弃`；`NOT_CREATED` → `未创建`；`CREATED` → `已创建`；`UNPAID` → `未缴费`；`PAID` → `已缴费`；`VERIFIED` → `已核验`；`NOT_APPLICABLE` → `不适用` |
| related-fact kind | `DRAFT` → `草单`；`PAY_LIST` → `缴费清单`；`PAYMENT` → `付款记录`；`OFFICIAL_EVIDENCE` → `官方证据` |

Fee line names come from the persisted `feeName` and remain unchanged. Fee codes are not translated
or shown in default content. Related-fact status uses the same closed fee-status map; an unlisted
status is `待确认` by default and raw in audit. `AGENCY_SERVICE`, `GRANT_REGISTRATION`, or any other
unlisted obligation type is likewise unknown; do not silently promote a test-only value to a known
business label.

- [ ] **Step 4: Add the shared historical boundary**

Inside the existing expanded region in `CaseLifecycleOverlay.vue`, render:

```text
以下为历史事实与审计追溯，不代表当前节点阻断；当前状态以上方摘要为准。
```

Do not change fetch, pagination, revision, disclosure, warning, or summary behavior.

- [ ] **Step 5: Rebuild the document/evidence default-versus-audit hierarchy**

In `DocumentEvidenceLane.vue`:

- keep milestone, evidence, derivation, work-package, receipt, and task ordering;
- use Chinese customer labels and formatted dates in default content;
- dedupe missing-gate codes before translating them;
- move activity ID/raw type, document/attachment IDs, lineage/hash, creator/reviewer IDs,
  derivation IDs/parent/child/source snapshot, package/document IDs, receipt IDs/attachment IDs, and
  task IDs/template IDs into a collapsed native `<details>` section labelled `审计信息`;
- keep each evidence version and derivation as a separate card; never collapse version facts.

- [ ] **Step 6: Format center timestamps only**

In `LifecycleCenterLane.vue`, call `overlayDateText` for snapshot and confirmed-change timestamps.
Do not alter filtering or three-axis values.

- [ ] **Step 7: Rebuild the detailed fee customer card**

In `FeeObligationLane.vue`:

- use shared latest-obligation projection;
- keep GOV/SERVICE counts and all seven statuses, including `估算状态：暂无` when null;
- show translated title, status labels, currency, due date, and labelled fee-line fields;
- omit `feeYearKey` from default content only when zero; retain it in audit information;
- move all IDs, raw codes/statuses, related-fact IDs, and supersession IDs into collapsed audit;
- do not sum money, infer balance, or format reduction ratio beyond displaying the source string.

- [ ] **Step 8: Run GREEN**

Repeat Step 2 with output directory `history-green`.

Expected: PASS; raw values are hidden only visually until audit expansion and remain exact afterward.

- [ ] **Step 9: Commit the history slice**

```bash
git diff --check -- frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts
git add frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts frontend/src/modules/cases/components/CaseLifecycleOverlay.vue frontend/src/modules/cases/components/DocumentEvidenceLane.vue frontend/src/modules/cases/components/LifecycleCenterLane.vue frontend/src/modules/cases/components/FeeObligationLane.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts
git commit -m "fix(cases): present lifecycle history for customers"
```

## Task 4: RED and GREEN the Case Fee-Tab Projection

**Files:**

- Modify: `frontend/src/modules/cases/components/CaseFeesTab.vue`
- Modify: `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts`
- Modify: `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`

- [ ] **Step 1: Write RED for customer content and unchanged mutations**

Extend `v8-case-fees-instruction.spec.ts` with the same obligation in multiple milestones and two
Chinese fee lines. Assert one card, all seven translated statuses, labelled line fields, no visible
UUID/raw enum, and exact raw audit fields after opening `审计信息`.

Retain the existing PAY/HOLD/ABANDON request count, request body, idempotency-key reuse, 409 error,
transport retry, and draft-link assertions. Change result-copy assertions from raw server fields to
the approved Chinese success summary, then open audit information before asserting server IDs and
raw returned instruction.

- [ ] **Step 2: Run RED**

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/fee-red" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-fees-instruction.spec.ts
```

Expected: FAIL because `CaseFeesTab.vue` flat-maps milestones and exposes raw fields.

- [ ] **Step 3: Reuse the shared projection and mapping functions**

Replace `realObligations` flat-map with `latestObligationsById(activeOverlay.milestones)`. Do not add
a second dedupe implementation. Render the same default business hierarchy as the detailed fee lane,
but retain the three instruction buttons and result link owned by this tab.

The instruction result default text is `支付指示已记录`, `暂缓指示已记录`, or `放弃指示已记录`.
Returned obligation/activity/idempotency identifiers and the raw returned instruction live in the
card audit disclosure. Existing errors retain server code/message behavior.

- [ ] **Step 4: Update the static V6 contract at the moved helper boundary**

In `frontend/tests/demo-v6-fee-ui-parity-contract.mjs`:

- read `lifecycleOverlayDisplay.ts` and import `latestObligationsById` from it instead of extracting
  that helper from `FeeObligationLane.vue`;
- keep the existing latest-wins and related-fact merge assertions;
- assert customer mappings live in the shared module;
- assert `CaseFeesTab.vue` consumes the shared projection and contains `审计信息`;
- do not change demo service item, bill, payment, or adjustment facts.

- [ ] **Step 5: Run GREEN and the static contract**

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/fee-green" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-fees-instruction.spec.ts
node frontend/tests/demo-v6-fee-ui-parity-contract.mjs
```

Expected: both PASS.

- [ ] **Step 6: Commit the fee-tab slice**

```bash
git diff --check -- frontend/src/modules/cases/components/CaseFeesTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs
git add frontend/src/modules/cases/components/CaseFeesTab.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts frontend/tests/demo-v6-fee-ui-parity-contract.mjs
git commit -m "fix(cases): present fee obligations for customers"
```

## Task 5: Run Focused Static and Compatibility Verification

**Files:**

- Evidence only: `artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/**`

- [ ] **Step 1: Run typecheck, scoped ESLint, and build**

```bash
mkdir -p artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs
script -q artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/typecheck.log \
  npm --prefix frontend run typecheck
script -q artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/eslint.log \
  /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/components/CaseDocumentsTab.vue src/modules/cases/components/CaseFeesTab.vue src/modules/cases/components/CaseLifecycleOverlay.vue src/modules/cases/components/DocumentEvidenceLane.vue src/modules/cases/components/LifecycleCenterLane.vue src/modules/cases/components/FeeObligationLane.vue src/modules/cases/components/lifecycleOverlayDisplay.ts --max-warnings 0'
script -q artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/build.log \
  npm --prefix frontend run build
script -q artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/logs/static-contract.log \
  node frontend/tests/demo-v6-fee-ui-parity-contract.mjs
```

Expected: all rc 0.

- [ ] **Step 2: Run the complete focused mock suite once**

```bash
PLAYWRIGHT_HTML_OUTPUT_DIR="$(pwd)/artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/playwright/focused-final" \
python3 scripts/run_v8_playwright_mock_isolated.py \
  src/tests/v8-case-document-gate-applicability.spec.ts \
  src/tests/v8-overlay-document-lane.spec.ts \
  src/tests/v8-overlay-center-lane.spec.ts \
  src/tests/v8-overlay-fee-lane.spec.ts \
  src/tests/v8-case-fees-instruction.spec.ts
```

Expected: PASS. Do not add broad Playwright or backend pytest here.

- [ ] **Step 3: Run the real-API gate compatibility test only if its environment is already active**

Run `casedock-real-api.spec.ts` against the task-owned local services when available. If the
environment is unavailable, record it as not run; the new mocked applicability matrix and final
strict V6 rehearsal remain the required gates. Do not claim this optional compatibility test PASS
without a captured result, and do not start a second bespoke stack solely for it.

- [ ] **Step 4: Record the final canonical lint evidence**

Run the exact `lint` evidence command frozen in Task 1 after the last source/test edit. Expected:
rc 0.

## Task 6: Run One Strict V6 Regression and Close Evidence

**Files:**

- Verification only:
  `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
- Evidence only: `artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/**`

- [ ] **Step 1: Confirm only the known colleague guide is dirty**

```bash
git status --porcelain=v1 -uall
shasum -a 256 docs/postdemo/demo-v6-colleague-clone-start-guide.md
```

Expected: the guide is the only status entry. If another path is dirty, stop instead of hiding it.

- [ ] **Step 2: Park and restore that exact untracked guide around one strict rehearsal**

Use this exact shell wrapper so every exit restores the guide and verifies its hash. The failed
attempt remains at `strict-v6-attempt-1`; only a successful run is renamed to `strict-v6-pass`:

```bash
set -euo pipefail
guide_path='docs/postdemo/demo-v6-colleague-clone-start-guide.md'
guide_hash="$(shasum -a 256 "$guide_path" | awk '{print $1}')"
parking_dir="$(mktemp -d /tmp/fpms-customer-projection.XXXXXX)"
parked_guide="$parking_dir/demo-v6-colleague-clone-start-guide.md"
restore_guide() {
  if [ -f "$parked_guide" ]; then
    mv "$parked_guide" "$guide_path"
  fi
  rmdir "$parking_dir" 2>/dev/null || true
}
trap restore_guide EXIT INT TERM
test ! -e artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-attempt-1
test ! -e artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass
mv "$guide_path" "$parked_guide"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL \
  --strict-ui \
  --headless \
  --runs 1 \
  --artifact artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-attempt-1
mv artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-attempt-1 \
  artifacts/FE-POST-V6-CUSTOMER-PROJECTION-20260828-01/strict-v6-pass
restore_guide
trap - EXIT INT TERM
restored_hash="$(shasum -a 256 "$guide_path" | awk '{print $1}')"
test "$restored_hash" = "$guide_hash"
test "$(git status --porcelain=v1 -uall)" = '?? docs/postdemo/demo-v6-colleague-clone-start-guide.md'
```

Expected: rc 0, zero network/console errors, and
`strict-v6-pass/run1/strict-pass-receipt.json`. Run once. On failure, the trap restores the guide;
retain the attempt, diagnose the exact failure, and do not retry until a new committed fix exists.

- [ ] **Step 3: Bind final files and verification artifacts**

Run the exact `test` shasum evidence command from Task 1. Expected: rc 0.

- [ ] **Step 4: Finalize scope**

```bash
./scripts/evidence_run.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01 scope \
  python3 scripts/evidence_scope.py finalize FE-POST-V6-CUSTOMER-PROJECTION-20260828-01
```

Expected: rc 0; `git/diff.patch` contains only the allowed implementation/test changes and the
external guide path/hash remains unchanged.

- [ ] **Step 5: Obtain independent HIGH review**

The independent reviewer must inspect the final baseline-subtracted patch, approved design,
implementation task, focused logs, strict V6 receipt, and non-closure. Approval must report one
final verdict with `P0: 0`, `P1: 0`, and `P2: 0`, bound to the final patch hash.

- [ ] **Step 6: Run task and atomic evidence gates**

After the independent review is submitted through `taskctl`, run:

```bash
./scripts/task_validate.sh FE-POST-V6-CUSTOMER-PROJECTION-20260828-01
python3 scripts/atomic_evidence_validate.py FE-POST-V6-CUSTOMER-PROJECTION-20260828-01
```

Expected: both PASS. Only then close the task and report terminal PASS.

## Execution Stop Conditions

Stop and replan instead of absorbing work if:

1. existing case and overlay payloads cannot produce the approved applicability or customer labels;
2. a legal, deadline, fee, payment, or lineage term lacks an approved mapping;
3. preserving exact audit facts requires an API, type, backend, database, or seed change;
4. a focused test proves the current V6 business inputs must change;
5. any source/test path outside the frozen allowlist requires modification;
6. the strict V6 run reveals a business failure unrelated to the presentation changes.

## Implementation Commit Sequence

1. `docs(cases): freeze customer projection task`
2. `fix(cases): contextualize filing material gate`
3. `fix(cases): present lifecycle history for customers`
4. `fix(cases): present fee obligations for customers`

No cleanup, rename, reformat, or adjacent English-text commit is permitted.
