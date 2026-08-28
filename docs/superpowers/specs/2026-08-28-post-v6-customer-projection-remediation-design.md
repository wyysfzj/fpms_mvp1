# Post-V6 Customer Projection Remediation Design

## 1. Outcome

The case-detail page must remain fact-complete while becoming understandable to a customer. The
current authorization-registration case must no longer appear blocked by an initial-filing gate,
and neither the fee tab nor expanded lifecycle history may use raw UUIDs, hashes, or English domain
codes as primary content.

This design changes presentation and applicability language only. It does not change any lifecycle,
document, lineage, fee, payment, or gate fact.

## 2. Authority and evidence

The design responds to three observed customer-facing defects on case
`CYIP-CN-INV-7906842426`:

1. the case is in business stage `GRANT_REGISTRATION_IN_PROGRESS` and official stage
   `GRANT_REGISTRATION`, but `CaseDocumentsTab.vue` labels the stage-blind initial-filing gate as
   “当前节点文件材料” and renders its `BLOCKED` result as a current blocker;
2. `CaseFeesTab.vue` renders obligation, activity, and document UUIDs plus raw English enums as the
   main “真实费用义务” card;
3. `DocumentEvidenceLane.vue` and `FeeObligationLane.vue` render raw audit identifiers, hashes,
   lineage keys, fee codes, ISO timestamps, and duplicated missing-gate codes in “完整历史”.

The persisted business facts observed during diagnosis remain one authorization-registration GOV
obligation with two lines: 授权登记费 CNY 900.00 and 授权公告印刷费 CNY 50.00. The UI defect is
not evidence of duplicated or corrupted fee facts.

## 3. Vocabulary and fact boundary

- **首次申请递交门禁**: the existing `document-gate` result derived from application request,
  specification, claims, abstract, power-of-attorney, priority, and examination-request rules.
- **当前节点状态**: the case's persisted `business_stage` and `official_procedure_stage`.
- **客户信息**: Chinese business labels, current/historical applicability, statuses, dates, amounts,
  and actions needed to understand the case.
- **审计信息**: UUIDs, hashes, lineage keys, source object identifiers, internal codes, and raw
  snapshots required for traceability but not for first-read comprehension.

Hiding audit information behind an explicit disclosure is not deleting, replacing, or collapsing a
fact. Every evidence version and every fee obligation remains independently visible and traceable.

## 4. Considered approaches

### Approach A — Frontend customer projection layer (selected)

Reuse the current case and lifecycle-overlay payloads. Determine whether the existing initial-filing
gate applies to the current stage, translate known codes centrally, format dates, deduplicate repeated
projection entries, and move raw identifiers into collapsed audit disclosures.

This closes the demonstrated defects without changing API or business truth. It also matches the
current-first lifecycle summary architecture already on this branch.

### Approach B — Stage-aware backend gate framework

Add gate kind, stage applicability, and authorization-specific gate rules to the backend response.
This could support future nodes, but it requires new domain contracts and authoritative definitions
for each node. Those definitions are not needed to correct the current misleading presentation, so
this approach is deferred.

### Approach C — Replace only the visible strings

Rename headings and add a few English-to-Chinese substitutions locally. This is smaller initially,
but it leaves UUIDs, duplicate codes, inconsistent fallbacks, and the same defect in other cards.
It is rejected because it would require repeated patching during the next demo.

## 5. Architecture

The existing components keep their current data ownership:

- `CaseDocumentsTab.vue` continues to fetch the case, documents, and the unchanged document gate;
- `CaseFeesTab.vue` continues to consume the lifecycle overlay and own fee-instruction actions;
- `CaseLifecycleOverlay.vue` continues to own overlay fetching, pagination, and history disclosure;
- the three lane components continue to render their own facts.

`lifecycleOverlayDisplay.ts` becomes the single small presentation module for:

- Chinese labels for known evidence, work-package, receipt, task, fee, and related-fact codes;
- a fallback that returns `待确认` in customer content rather than the unknown raw code;
- stable display-only date/time formatting;
- stable first-occurrence list deduplication;
- latest fee-obligation projection by `obligationId`, preserving the current related-fact merge.

No store, composable, generic rules engine, new endpoint, new request, or persisted view model is
introduced.

## 6. Initial-filing gate applicability

### 6.1 Presentation modes

`CaseDocumentsTab.vue` stores the existing case metadata returned by `getCase` instead of retaining
only the case number. It classifies the two stage axes using these closed sets:

- initial business stages: `NEW_CASE`, `FILING_PREPARATION`;
- post-submission business stages: `WAITING_EXTERNAL_RECEIPT`, `PROSECUTION_MANAGEMENT`,
  `OA_REPLY_IN_PROGRESS`, `GRANT_REGISTRATION_IN_PROGRESS`, `POST_GRANT_MAINTENANCE`, `CLOSED`;
- initial official stage: `NOT_SUBMITTED`;
- post-submission official stages: `SUBMITTED_WAITING_RECEIPT`,
  `SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE`, `ACCEPTED`, `PRELIMINARY_EXAMINATION`,
  `RECTIFICATION_RESPONSE`, `PUBLISHED`, `SUBSTANTIVE_EXAMINATION`, `OFFICE_ACTION_RESPONSE`,
  `REEXAMINATION`, `GRANT_REGISTRATION`, `GRANT_ANNOUNCED`, `PROCEDURE_CLOSED`.

It then derives exactly one display mode:

| Mode | Condition | Customer presentation |
| --- | --- | --- |
| `CURRENT_INITIAL_FILING` | both axes are present; business stage belongs to the initial set and official stage is `NOT_SUBMITTED` | “当前首次申请递交门禁”; preserve the existing PASS/WARNING/BLOCKED severity and actions |
| `HISTORICAL_INITIAL_FILING` | both axes are present; business and official stages both belong to their post-submission sets | “历史首次申请递交材料核验”; show the returned result as a historical rule result and explicitly state that it is not the current-node conclusion |
| `APPLICABILITY_UNKNOWN` | either axis is absent, unrecognized, or the two classifications disagree | “首次申请递交材料核验（适用阶段待确认）”; use neutral warning styling, do not call it the current node, and preserve the returned result as attributed source data |

No enum ordering, legacy `status`, or `workflow_status` fallback participates in this classification.
Partial, conflicting, and future unrecognized values fail to `APPLICABILITY_UNKNOWN` rather than
being inferred.

### 6.2 Historical mode behavior

For the demonstrated authorization-registration case:

- the page first states `当前阶段：授权登记` using existing Chinese lifecycle mappings;
- the status strip labels become `历史已匹配材料`, `历史未匹配材料`, `首次申请规则硬性缺失`, and
  `历史后补审计`;
- a `BLOCKED` source result becomes customer text
  `首次申请递交规则未满足（历史核验）`, not `门禁结论：阻止`;
- the stage-derived statement
  `该结果用于追溯首次申请递交材料，不作为当前“授权登记”的阻断结论。` is visible; other
  post-submission cases substitute their existing Chinese official-stage label rather than reusing
  authorization-specific copy;
- “当前建议动作” becomes “历史核验说明”; the gate-card filing action is not presented as a
  current authorization action, while the page toolbar's generic “登记往来文件” remains available;
- the document event table remains unchanged and continues to show the actual recorded files.

The underlying `documentGate.conclusion`, checks, missing items, and suggested actions are not
mutated. The UI does not fabricate PASS and does not claim that missing filing material exists when
the API reports otherwise.

### 6.3 Load failure

If case metadata fails while the gate succeeds, the page uses `APPLICABILITY_UNKNOWN`. If the gate
fails, the existing load error remains. Neither failure silently converts the gate to PASS or hides
the document-event list.

## 7. Customer-readable fee obligations

### 7.1 One business card per obligation

Both `CaseFeesTab.vue` and `FeeObligationLane.vue` use the same latest-by-`obligationId` projection.
Later milestone values win; related facts are merged by `kind + objectId` as today. This removes
duplicate cards caused by milestone snapshots without collapsing distinct obligations.

### 7.2 Default fee card

The default card contains only customer information:

- title: translated obligation type, for example `授权登记官费义务`;
- badges: `官费` or `服务费`, source verification state, obligation state, and payment state;
- labelled facts: 到期日、币种、估算状态、客户指示、草单状态、缴费清单状态、付款状态、
  官方证据状态;
- a labelled fee-line table: 费项、官费全额、减缴比例、应缴金额、来源金额、来源日期、差额复核;
- fee name from `feeName`; the fee code is not used as the visible title;
- `CNY` is displayed as `人民币（CNY）`; unknown currency remains `币种待确认`.

Amounts, ratios, and source dates are displayed without recalculation. The design does not infer a
balance, paid amount, legal deadline, reduction eligibility, or official evidence.

### 7.3 Audit disclosure

Each obligation card has one collapsed `审计信息` disclosure containing:

- obligation, source activity, and source document identifiers;
- fee and obligation codes;
- related-fact object identifiers and raw statuses;
- superseded-obligation identifier and reason;
- fee-line identifiers and codes.

Fee-instruction success remains actionable. Customer content says, for example,
`支付指示已记录`; returned obligation/activity/idempotency identifiers move into the same audit
disclosure. The existing mutation payload, idempotency behavior, retry behavior, and draft link are
unchanged.

The fee-card field hierarchy is fixed as follows:

| Field class | Default customer card | Collapsed audit information |
| --- | --- | --- |
| fee name, amounts, ratio, source date, due date | labelled business value | not duplicated |
| seven obligation statuses | translated Chinese value, including `估算状态：暂无` when null | raw known or unknown status code |
| currency | `人民币（CNY）` or `币种待确认` | raw currency value when unknown |
| `feeYearKey` | omitted when `0`; otherwise `费种年度：<value>` | always retained |
| obligation, activity, document, related-fact, line IDs | hidden | exact value retained |
| obligation type, fee code, related-fact kind/status | translated value where customer-relevant | exact raw value retained |
| unparseable source value | `待确认` | exact raw value retained |

## 8. Customer-readable expanded history

### 8.1 Shared history boundary

Immediately below “查看完整历史”, the expanded region displays:

`以下为历史事实与审计追溯，不代表当前节点阻断；当前状态以上方摘要为准。`

This statement applies to all three lanes. It prevents a historical `FILING_PREP` work package with
`NEEDS_MAINTENANCE` from being mistaken for the current authorization-registration state.

### 8.2 Document and evidence lane

The default content keeps the existing activity, evidence, derivation, work package, receipt, and
task ordering, but uses customer labels:

| Raw value | Customer label |
| --- | --- |
| `FILING_PREP` | 新申请递交 |
| `OA_REPLY` | 审查意见答复 |
| `NEEDS_MAINTENANCE` | 需维护 |
| `OFFICIAL_FINAL_PDF` | 最终递交 PDF |
| `FINAL` | 已定稿 |
| `APPROVED` | 已复核 |
| `FORMAT_CONVERSION` | 格式转换 |
| `ELECTRONIC_APPLICATION_RECEIPT` | 电子申请回执 |
| `ARCHIVED` | 已归档 |
| `CHECKLIST_INCOMPLETE` | 递交检查清单未完成 |
| `MANIFEST_MISSING` | 递交文件清单缺失 |

Known task states use Chinese labels. Unknown values render `待确认` in default content. Duplicate
missing-gate codes are removed in first-occurrence order before display.

UUIDs, creator/reviewer identifiers, lineage keys, hashes, attachment/document IDs, derivation IDs,
parent/child IDs, raw gate codes, and source snapshots move into one collapsed `审计信息` disclosure
inside the relevant fact card. Every version and derivation remains present; only information
hierarchy changes.

### 8.3 Center lane

Center state mappings remain unchanged. ISO values matching `YYYY-MM-DDTHH:mm:ss...` display as
`YYYY-MM-DD HH:mm` without timezone conversion; date-only values remain date-only. Unparseable
source text displays `待确认` and remains available in audit information only if an audit section
already owns that source value.

### 8.4 Fee lane

The full-history fee lane uses the same customer card and audit hierarchy defined in section 7.
It preserves both GOV and SERVICE tracks and all seven independent statuses: estimate, obligation,
client instruction, draft, pay list, payment, and official evidence. It does not calculate or
display account balance.

## 9. Unknown-code and error policy

- A known code must have exactly one Simplified Chinese label in `lifecycleOverlayDisplay.ts`.
- An unknown code must not leak into default customer text; default text is `待确认` or a
  field-specific variant such as `活动类型待确认`.
- The raw unknown value remains in the card's audit disclosure.
- Empty values display `暂无`, not an empty string and not `undefined`.
- Existing API errors and transport behavior remain unchanged; this task adds no retry.

## 10. Focused verification contract

Implementation must begin with failing focused tests and finish with these observable results:

| Scenario | Required result |
| --- | --- |
| authorization-registration case with initial-filing gate `BLOCKED` | historical heading and non-current explanation visible; no current red “门禁结论：阻止” or filing action |
| initial-filing case with the same gate result | current gate severity and actions remain visible |
| contradictory or missing stage metadata | neutral “适用阶段待确认”; no fabricated PASS/current applicability |
| future unrecognized business or official stage value | neutral “适用阶段待确认”; raw future code is not presented as a known stage |
| repeated obligation across milestones | exactly one card for that obligation ID with latest statuses |
| real fee card | Chinese title/statuses and labelled lines visible; UUID and raw enums absent before audit disclosure |
| audit disclosure opened | exact raw identifiers and codes remain available |
| document history default | known codes translated, duplicate gate codes shown once, UUID/hash absent before audit disclosure |
| unknown evidence/work-package/fee code | `待确认` visible; raw value only inside audit disclosure |
| history expanded | historical-boundary statement visible; center and document/evidence timestamps use customer format |
| fee instruction PAY/HOLD/ABANDON and transport retry | existing request bodies, idempotency-key reuse, errors, and draft-link behavior unchanged |

Focused Playwright coverage extends the existing document-lane, fee-lane, fee-instruction, and case
document-gate specifications:

- create `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-document-gate-applicability.spec.ts`;
- modify `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-document-lane.spec.ts`;
- modify `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-center-lane.spec.ts`;
- modify `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-overlay-fee-lane.spec.ts`;
- modify `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-fees-instruction.spec.ts`;
- update `frontend/tests/demo-v6-fee-ui-parity-contract.mjs` only where its static customer
  projection assertions conflict with this design;
- run the focused case-detail regression in
  `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity.live-backend.spec.ts`
  without changing its V6 business inputs or mutations.

`casedock-real-api.spec.ts` remains unchanged unless the new focused applicability test proves an
existing assertion directly contradicts the approved labels. Typecheck, scoped lint, focused
Playwright, and the named V6 live case-detail regression form the implementation gate; broad
repository tests and release gates remain out of scope.

## 11. Anticipated file boundary

Product implementation is expected to modify only:

- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `frontend/src/modules/cases/components/CaseFeesTab.vue`
- `frontend/src/modules/cases/components/CaseLifecycleOverlay.vue`
- `frontend/src/modules/cases/components/DocumentEvidenceLane.vue`
- `frontend/src/modules/cases/components/LifecycleCenterLane.vue`
- `frontend/src/modules/cases/components/FeeObligationLane.vue`
- `frontend/src/modules/cases/components/lifecycleOverlayDisplay.ts`
- directly affected focused frontend/Playwright tests frozen by the implementation plan.

The implementation plan must not add backend, API-type, schema, database, seed, runbook, or demo
data paths unless a focused RED proves the approved behavior cannot be produced from the existing
case and overlay payloads. That condition is a stop-and-replan event, not permission to absorb the
new path.

## 12. Non-goals

- Define an authorization-specific document gate or change filing-gate requirements.
- Correct or synthesize historical application documents.
- Change lifecycle transitions, legal conclusions, fee sources, amounts, deadlines, reduction
  semantics, payment state, or document lineage.
- Redesign the whole case page, fee estimator, persisted-draft table, warnings, or unrelated legacy
  pages.
- Remove audit identifiers from APIs, logs, or persistence.
- Introduce a reusable rules engine, generalized internationalization framework, or backend
  presentation DTO.

## 13. Stop conditions

Implementation planning stops and returns for a new decision if any of the following is discovered:

1. the case response does not reliably expose the current business and official stages used by the
   demonstrated page;
2. an authorization-specific gate conclusion is required rather than the approved historical
   applicability statement;
3. a requested Chinese term would assert an unverified legal, fee, deadline, payment, or lineage
   fact;
4. preserving audit traceability requires changing API or persistence contracts;
5. the focused change requires modifying the V6 seed, runtime bundle, or runbook business values.
