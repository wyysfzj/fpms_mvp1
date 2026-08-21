# FPMS V8 Source and Decision Registry

## Source precedence

For requirements, post-demo feedback, workflow, fees, demo behavior, and implementation
coverage, prefer original customer or primary authority first, extracted text second,
approved analysis/design third, and code evidence last. Ignore Word lock files such as
`docs/postdemo/~$*.docx`. When screenshots, layout, buttons, menus, lists, fee tables, or
attachments matter, inspect rendered pages and embedded images rather than extracted text
alone. If an external local original is unavailable, use its indexed extraction and mark
the source `待确认`. Verify the effective version before activating law, fee, rate, form, or
workflow truth. The task that first relies on a new customer or authoritative design source
updates this index.

## Customer and external sources

- `docs/TXX.pdf`; mirror: `reference/TXX.pdf`.
- `docs/postdemo/相关流程操作-20260526.docx`.
- `docs/postdemo/OA答复流程.docx`.
- `docs/postdemo/信函生成操作.docx`.
- `docs/postdemo/专利收费场景-20260626.docx`.
- `docs/postdemo/相关问题解答.docx`; prefer it over the historical external copy.
- `docs/postdemo/标准费率.XLS`; customer pricing/configuration, not current legal authority.
- `docs/postdemo/补充缴费信息模板.xlsm`; preserve provenance, macros, hidden sheets, order,
  and validation; do not assume current acceptance without upload verification.
- `docs/postdemo/文件样例及模版/**`; distinguish legacy/current forms and render when needed.
- `/Users/cfcc/Documents/相关问题解答.docx`; external local customer answer copy.
- `http://www.tianyueip.com/product/612`; secondary customer/business reference; cached at
  `artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/tianyueip_product_612.txt`.
- `https://www.cnipa.gov.cn/art/2024/8/6/art_1518_155983.html`; CNIPA primary fee page.
- **Current reviewed CNIPA annuity source (D4-10 authority)**:
  - Metadata article:
    `https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html`.
  - Exact PDF:
    `https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518`.
  - Title: `专利和集成电路布图设计缴费服务指南`.
  - Published/reviewed snapshot date: `2026-03-30`.
  - Size: `32 pages`; `2478214 bytes`.
  - PDF SHA-256:
    `3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce`.
  - Retrieved at UTC: `2026-07-19T03:55:57Z`.
  - PDF creation/modification: `2026-03-30 16:00:48 CST`.
  - Exact canonical `CNIPA_RATE_SOURCE_V1` snapshot:
    `{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":[{"content_sha256":"3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce","document_no":null,"published_on":"2026-03-30","retrieved_at":"2026-07-19T03:55:57Z","title":"专利和集成电路布图设计缴费服务指南","url":"https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"}]}`.
  - Canonical snapshot SHA-256:
    `e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544`.
  - Annex 2 reviewed full annual fee tiers:
    - INV: years 1–3 `900.00`; 4–6 `1200.00`; 7–9 `2000.00`;
      10–12 `4000.00`; 13–15 `6000.00`; 16–20 `8000.00`.
    - UM: years 1–3 `600.00`; 4–5 `900.00`; 6–8 `1200.00`;
      9–10 `2000.00`.
    - DES: years 1–3 `600.00`; 4–5 `900.00`; 6–8 `1200.00`;
      9–10 `2000.00`; 11–15 `3000.00`.
  - This reviewed snapshot records source authority only. It does not infer fee amount
    activation, legal effect before `2026-03-30`, or runtime rate-book activation.
- **Superseded history (31 pages; not current D4-10 authority)**:
  `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`;
  retained only as historical index context.

## Extracted customer text and review ledgers

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

## Authoritative FPMS baselines and designs

- `docs/FPMS SPEC 2.0.md`; mirrors: `reference/FPMS SPEC 2.0.md` and
  `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md`.
- `docs/FPMS 架构技术设计.md` and `reference/FPMS 架构技术设计.md`.
- `docs/00_mvp1_scope.md` through `docs/07_db_ddl_and_sqlite.md`.
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
- `docs/gap.md`, `docs/mvp1_gap.md`, and `docs/mvp_story_gap.md`.

## Post-demo, audit, and remediation authority

- `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_p1_e2e_demo_20260612.md` and `.docx`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/p1_demo_engineering_checklist.md`
- `docs/postdemo/p1_demo_execution_runbook.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `docs/postdemo/postdemo_fee_scenario_gap_review_20260705.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `docs/superpowers/plans/2026-05-31-postdemo-p1-full-scope-development.md`
- `docs/superpowers/plans/2026-06-11-postdemo-p1-answer-delta-full-scope.md`
- `docs/superpowers/plans/2026-07-05-official-fee-scenario-enhancement.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/reviews/fpms_functional_correctness_audit_20260705.md`
- `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md`
- `docs/reviews/fpms_audit_remediation_design_20260705.md`

## Evidence families for audits

- `artifacts/PD-ENH-*/summary.md`
- `artifacts/PD-P1-*/summary.md`
- `artifacts/PD-FEE-SCENARIO-*/summary.md`
- `artifacts/PD-DOC-*/summary.md`
- `artifacts/PD-P1-E2E-UI-FULLSCOPE-20260602-01/full_scope_coverage_ledger.md`
- `artifacts/PD-P1-FULLSCOPE-ANSWER-DELTA-PLAN-20260611-01/analysis/full_scope_delta_ledger.md`
- `artifacts/PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01/analysis/close_ledger.md`
- `artifacts/PD-P1-QA-FULLSCOPE-E2E-01/close_ledger.md`

## Active source records

| Record | Status | Exact effect |
| --- | --- | --- |
| `SRC-CNIPA-LAYOUT-246-20170630` | `source-metadata-reviewed/not activated` | The locked Announcement 246 normalized source and provenance below are accepted only as the D4-09 source prerequisite. They do not activate a rate book, rate, legal conclusion or customer decision. |
| `SRC-CNIPA-ANNUITY-20260330` | Source metadata reviewed | The 32-page CNIPA payment guide and hashes above are the current reviewed D4-10 annuity source. This does not by itself activate runtime rates or infer earlier legal effect. |
| Historical 31-page CNIPA guide | Superseded source history | Read-only comparison input; never current D4-10 authority. |
| Customer `标准费率.XLS` | Customer pricing/configuration | Never automatic legal or official-fee authority. |
| Customer `补充缴费信息模板.xlsm` | Unverified operational template | Preserve provenance/macros/hidden sheets; controlled upload remains gated. |

### `SRC-CNIPA-LAYOUT-246-20170630`

- Source URL:
  `https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html`.
- Title: `关于执行新的集成电路布图设计保护费收费标准的公告（第246号）`.
- Document number: `第二四六号`.
- Published on: `2017-06-30`.
- Effective from: `2017-07-01`.
- Retrieval method: `normalized-primary-page-excerpt`.
- Retrieved at UTC: `2026-07-18T08:39:40Z`.
- Locked normalized-content SHA-256:
  `13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8`.
- Locked provenance-record SHA-256:
  `2ff9eb7e84253359b2075e972bdd955313b95955f0ebad5e3d1b9fe9ec642377`.
- Decision value: `source-metadata-reviewed/not activated`.
- Actor and acceptance authority: the repository controller-authorized
  `V8-CNIPA-246-LAYOUT-SOURCE-SNAPSHOT-CURRENT-ADOPTION` lane records this metadata;
  one independent HIGH reviewer of its exact commit is the acceptance authority. Neither
  role acts as a customer, legal or runtime source activator.
- Effective scope and time: the source's recorded effective date is `2017-07-01`, while
  this registry decision becomes active only when the exact source-adoption story is
  independently approved and integrated. Its scope is only the locked-source prerequisite
  for D4-09; it creates no retroactive runtime, fee-book or legal activation.
- Rollback impact: reverting that source-adoption story removes this record and its two
  locked source files, returns D4-09 to `PARKED_DEPENDENCY`, and performs no runtime
  deactivation because no source, candidate or rate was activated.

## Customer and authority decision gates

### `DEC-LOCAL-DEMO-ABC-20260815`

- Status: `SCOPE_SELECTED / WRITTEN_ADOPTION_PENDING`.
- Exact source/version: customer approval in Codex task
  `019ffc07-14a5-7dc2-9536-f2047327e14a`, preserved without normalization at
  `docs/product/v8/customer-decisions/2026-08-15-local-demo-abc.txt`, decision version
  `customer-decision:2026-08-15:local-demo-abc:v1`, received on `2026-08-15` in timezone
  `Asia/Shanghai`.
- Exact source size: `87` bytes.
- Source SHA-256:
  `c0a1021f46f18ecd13e81417b387cd4dba4326e523a4b5d9d19d361fd5b0cc45`.
- Decision value: the customer selected the previously discussed high-level combination: a local
  demonstration, a runtime bundle, and customer AR billing/payment/offset. The exact checkpoint,
  lifecycle, input-authority, transaction and acceptance semantics are only the proposal in
  `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`; they are not inferred as
  customer-approved bytes. Product implementation remains unauthorized until the customer
  confirms an independently reviewed exact commit of that written specification.
- Preserved boundaries: this decision does not activate `DG-SERVICE-RATE-VERSION`,
  `DG-PAYMENT-WORKBOOK`, an official rate, a production template or a legal conclusion. Missing or
  invalid demo input remains fail-closed. The demonstration is limited to loopback or controlled
  screen sharing, a disposable SQLite database and storage directory, and fictional data. It is
  not authority for public hosting, production deployment, security acceptance or release.
- Actor and acceptance authority: the repository customer/user selected the high-level scope.
  The exact written design still requires customer adoption; every later `PROTECTED`
  implementation slice and the exact integrated demo candidate require independent High review
  before `DEMO_READY`.
- Effective scope/time: active from `2026-08-15` only as authority to produce and review the W0
  written design. It does not yet authorize product implementation. A future production input,
  remote demo, official payment, bad debt, dunning, commission or release requires separate
  authority and acceptance.
- Rollback impact: reverting the local demo branch or selecting no valid external bundle disables
  the demo-only providers. Rollback must not delete or rewrite any already created demo history;
  production input and decision-gate state remain unchanged because this decision never activates
  them.

### `DEC-V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-20260809`

- Status: `APPROVED`.
- Source/version: user authority decision in Codex Goal thread
  `019f4a1a-6f55-77a2-b558-b6555201415c`, exact UTF-8 decision text
  `批准方案 A，Resume Goal`, received on `2026-08-09` in timezone `Asia/Shanghai`.
- Source SHA-256:
  `91a336042550c2ee616f43654f4216955f6fff774528b696c676faebb4f1ac64`.
- Decision value: ordinary document create, batch create and ordinary document edit are
  lifecycle-neutral. They may persist document, deadline, reply, task and fee-routing
  facts, but must not directly write `Case.status` or the three central lifecycle
  projections and must not append a lifecycle event. A legal/lifecycle transition is
  accepted only through its dedicated actor-aware, reviewed-evidence, confirmed and
  idempotent lifecycle adapter.
- Actor and acceptance authority: the repository user approved option A. One independent
  High reviewer of the exact frozen successor contract and one independent High reviewer
  of its exact implementation candidate remain required before ledger activation.
- Effective scope/time: the decision becomes active only for V8 current-tree acceptance
  after the exact successor implementation is independently approved and integrated. It
  supersedes the conflicting ordinary-create dispatch requirement of catalog row 61; it
  does not retroactively rewrite historical evidence or authorize a new lifecycle event.
- Rollback impact: reverting the successor adoption restores the pre-adoption runtime and
  returns row 61 and its dependent lanes to `AUTHORITY_BLOCKED`; no lifecycle event,
  status or historical record may be synthesized during rollback.

### `DEC-V8-FULL-BATCH-SCHEME-A-20260810`

- Status: `APPROVED_POLICY`; current-owner adoption remains subject to independent High review.
- Exact source/version: customer approval in Codex Goal thread
  `019f4a1a-6f55-77a2-b558-b6555201415c`, preserved without normalization at
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`, decision version
  `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`, received on `2026-08-10` in timezone
  `Asia/Shanghai`.
- Exact source size: `2167` bytes.
- Source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Actor and acceptance authority: the repository customer/user explicitly approved Scheme A.
  Publication records its authenticated actor, publication/effective time, unique version and
  content hash. Independent High review of these exact source and registry bytes remains required
  before current-owner adoption.
- Approved exact decisions:
  - `DG-FEE-APPLICATION-DRAFT:GLOBAL`: after the real application-fee notice is reviewed, create
    one internal draft pending review; actual payment still requires client instruction.
  - `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`: after the real grant-year notice is reviewed, create one
    internal draft pending review; actual payment still requires client instruction.
  - `DG-FEE-FUTURE-ANNUITY:GLOBAL`: client instruction is required before draft creation; the
    initial exception set is empty. Later exceptions require an authorized, audited customer/case
    scope with explicit start and end.
  - `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`: an institution administrator may select only a currently
    reviewed and activated CNIPA source record. A new source records its exact channel/data/file,
    version, acquisition method, scope and effective time and requires independent review. Missing,
    stale or unreviewed source configuration is `409`, no write and no legal-state change.
  - `DG-GRANT-MANUAL-REVIEW:GLOBAL`: institution-configured roles control official-copy
    acquisition, first and second verification, proposal and second review. First and second
    verifiers must be different actual users; proposer and second reviewer must be different
    actual users. Missing, stale or incomplete role bindings are `409`, no write and no
    legal-state change. Original official evidence, acquisition facts, reason, actors and complete
    audit history remain mandatory.
  - `DG-LEGACY-FORM-CLASS:form-001` through `form-022`: every exact identity is
    `INTERNAL_ONLY`; `form-009` and `form-017` remain distinct. The initial current-official-form
    exception set is empty. A later exception requires its own reviewed official source, version
    and effective interval and cannot silently reclassify an old file.
- Canonical all-22 decision value:
  `{"form-001":"INTERNAL_ONLY","form-002":"INTERNAL_ONLY","form-003":"INTERNAL_ONLY","form-004":"INTERNAL_ONLY","form-005":"INTERNAL_ONLY","form-006":"INTERNAL_ONLY","form-007":"INTERNAL_ONLY","form-008":"INTERNAL_ONLY","form-009":"INTERNAL_ONLY","form-010":"INTERNAL_ONLY","form-011":"INTERNAL_ONLY","form-012":"INTERNAL_ONLY","form-013":"INTERNAL_ONLY","form-014":"INTERNAL_ONLY","form-015":"INTERNAL_ONLY","form-016":"INTERNAL_ONLY","form-017":"INTERNAL_ONLY","form-018":"INTERNAL_ONLY","form-019":"INTERNAL_ONLY","form-020":"INTERNAL_ONLY","form-021":"INTERNAL_ONLY","form-022":"INTERNAL_ONLY"}`.
- Non-activation decisions: `DG-PAYMENT-WORKBOOK:GLOBAL` remains `PENDING` until a clean current
  workbook and controlled-upload proof are approved. `DG-SERVICE-RATE-VERSION:GLOBAL` remains
  `PENDING` until a complete customer service-rate version is approved. Neither negative decision
  may be persisted as a confirmed activation value.
- Development/runtime boundary: the five approved global policy contracts and 22 classifications
  may enter their exact independently accepted development lanes. Grant-source and manual-review
  runtime remains disabled until complete source/role configuration is published. Test fixtures
  may use explicit test-only source and role examples; they must never become production defaults
  or production seed data.
- Rollback impact: revocation stops later automated or manual actions and later draft generation,
  but does not delete, synthesize or rewrite historical obligations, drafts, evidence, activities,
  decisions or legal status. A form reclassification affects only later use of that exact form.

The following statuses are the decision snapshot after the customer approval above. `PENDING`
means no sufficient reviewed positive activation decision is present. Missing or conflicting input
blocks only the named lane; it never activates a default.

| Gate | Status | Fail-closed behavior |
| --- | --- | --- |
| `DG-FEE-APPLICATION-DRAFT` | `APPROVED_POLICY` | Runtime waits for the independently accepted notice-driven draft implementation; payment still requires client instruction. |
| `DG-FEE-GRANT-YEAR-DRAFT` | `APPROVED_POLICY` | Runtime waits for the independently accepted notice-driven draft implementation; payment still requires client instruction. |
| `DG-FEE-FUTURE-ANNUITY` | `APPROVED_POLICY` | Each future annuity waits for instruction; the initial exception set is empty. |
| `DG-GRANT-EVIDENCE-SOURCE` | `APPROVED_POLICY / CONFIG_REQUIRED` | Archive candidate evidence as unverified; without published source configuration do not enter patent in force. |
| `DG-GRANT-MANUAL-REVIEW` | `APPROVED_POLICY / CONFIG_REQUIRED` | Manual review remains disabled without complete published role bindings and actual-user separation. |
| `DG-PAYMENT-WORKBOOK` | `PENDING` | Only internal workbook output is allowed; official adapter remains fail-closed. |
| `DG-SERVICE-RATE-VERSION` | `PENDING` | No service quote/receivable activation; official obligations remain separate. |
| `DG-LEGACY-FORM-CLASS` | `APPROVED: INTERNAL_ONLY` for each `form-001`–`form-022` | Every form remains internal/reference-only; no official submission activation. |
| `DG-APPLICATION-FEE-NOTICE-PREVIEW-SOURCE` | `PENDING` | Do not dispatch the application-fee notice or accept its official-fee obligation from guessed page/priority counts. |

## 2026-08-10 grant-year official-fee manual review authority

Status: `APPROVED`.

- Exact source/version: customer decision in Codex thread
  `019f4a1a-6f55-77a2-b558-b6555201415c`, decision version
  `customer-decision:2026-08-10:grant-fee-manual-review:v1`, exact UTF-8 approval text
  `批准方案A`, received on `2026-08-10` in timezone `Asia/Shanghai`.
- Source SHA-256:
  `4d21111b0b915b1c506083636d36782a59c9238028c8503f56a98ddcfffc0f09`.
- Decision value: only an authenticated operator with `GrantFeeTask.Write`, using the exact
  archived and approved grant-notice evidence version, may manually enter and confirm every
  official full amount. The system must durably record operator, confirmation time, source
  document/activity, evidence version/hash, complete before/after line amounts and idempotency
  identity before all exact lines move atomically from `REVIEW_REQUIRED` to `MATCHED`. No rate
  book, reduction ratio, payable amount or other stored/calculated value may infer an official
  full amount.
- Actor and acceptance authority: the repository customer/user approved option A. One independent
  High reviewer of the exact frozen successor contract and one independent High reviewer of its
  exact implementation candidate remain required before ledger activation.
- Effective scope/time: active from `2026-08-10` only for the manual review prerequisite frozen in
  `V8-GRANT-OFFICIAL-FEE-MANUAL-REVIEW-SUCCESSOR-CONTRACT`, after its independently approved
  implementation is integrated. It does not itself activate `DG-FEE-GRANT-YEAR-DRAFT`, infer an
  amount, bypass explicit client `PAY`, or alter historical records.
- Rollback impact: reverting the successor adoption removes the controlled manual review action
  and returns catalog Row120 and its dependent Foundation lanes to `AUTHORITY_BLOCKED`. Existing
  review activities and matched amounts must not be deleted, synthesized or silently reclassified;
  rollback requires fail-closed read handling for any already persisted review fact.

### Application-fee notice preview source questions

The pending record
`docs/postdemo/postdemo_application_fee_notice_preview_source_decision_20260721.md`
requires customer confirmation of:

1. the exact reviewed source/version for specification page count;
2. whether and how drawing pages enter the 31/300/301 thresholds;
3. the exact current priority-record source and deduplication rule.

The system must not infer these quantities from fee amounts, case type, filenames or
mutable current data. Missing, conflicting, ambiguous or stale inputs block only this
dispatch lane.

## Registry update rule

### `DEC-INTEGRATED-DEMO-A-20260821`

- Status: `APPROVED_DESIGN_SCOPE_PENDING_INDEPENDENT_REVIEW`; implementation and customer-input
  activation remain blocked until their own exact acceptance gates.
- Exact source/version: the customer requirement, the complete Scheme A proposal it references,
  and the customer's exact approval in Codex task
  `019ffc07-14a5-7dc2-9536-f2047327e14a`, preserved as a labelled UTF-8/LF transcript with one
  terminal LF at
  `docs/product/v8/customer-decisions/2026-08-21-integrated-demo-a.txt`, decision version
  `customer-decision:2026-08-21:integrated-demo-a:v1`, received on `2026-08-21` in timezone
  `Asia/Shanghai`.
- Exact source size: `2112` bytes.
- Source SHA-256:
  `f0fa544eb6291382d8ab8cc4c630a3747e04afe7d3b0a8d25a066275bed9d438`.
- Actor and acceptance authority: the repository customer/user requires the upcoming demo to
  retain the prior demo and show the new changes, then explicitly confirmed Scheme A.
- Approved exact decision: use one fictional client and one fictional case for one continuous
  presentation. Preserve the V7 client/contact, case, wizard/catalog, filing, two-OA/receipt,
  grant-source replacement and superseded-task safety story, then continue on the same case into
  the accepted runtime service-price, locked draft, unique AR bill, customer bank receipt and full
  offset story. Do not replace the prior story with the finance slice or split the two chapters
  across unrelated cases.
- Safety boundary: historical hard-coded amounts, seeds, lifecycle enrichment and fixtures do not
  become authority. Missing official-fee or customer service-price authority remains fail-closed.
  A visibly labelled `SYNTHETIC_TEST_ONLY` bundle may support a fictional local technical
  rehearsal but cannot become customer pricing, legal or production truth.
- Acceptance boundary: the integrated current-candidate journey must pass twice on distinct fresh
  local runs and receive independent High `P0/P1/P2 = 0/0/0`. This decision does not approve
  production, release, security, PostgreSQL, remote hosting, official submission/payment or a real
  customer runtime bundle.
- Effective scope/time: active only as authority to review the exact successor design. Atomic
  implementation planning and implementation remain blocked until that design has an independent
  zero-finding review and written customer acceptance. Customer-facing activation of actual
  templates/prices starts only after a separate exact bundle authority record and digest
  validation.
- Rollback impact: reverting the successor design or implementation returns the accepted demo to
  the prior local ABC technical boundary. It must not delete or rewrite any historical evidence,
  lifecycle, obligation, draft, bill, payment or offset fact.

The first story that relies on a new or changed source/decision must update this registry
with source/version/hash, decision value, actor, effective scope/time and rollback impact.
Official/legal/fee/customer truth remains `PROTECTED` and requires independent review.
