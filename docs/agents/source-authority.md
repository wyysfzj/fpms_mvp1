# FPMS Source Authority

### Rule GOV-SOURCE-001 — Original, effective, and reviewable sources

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
- `https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`;
  CNIPA payment service guide updated 2026-03-30.

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

Rule-Ref: GOV-CUSTOMER-001
Rule-Ref: GOV-LIFECYCLE-001
Rule-Ref: GOV-FEE-001
Rule-Ref: GOV-LINEAGE-001
