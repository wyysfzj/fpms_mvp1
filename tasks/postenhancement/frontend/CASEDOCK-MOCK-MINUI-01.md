# CASEDOCK-MOCK-MINUI-01 — Minimal UI mock pages for case-document gate option A

- Source: user request based on `fpms_case_document_gate_phase1` enhancement option A.

## Exact Closure Slice

Create static mock pages that show the minimal UI changes on top of existing case/document filing entry points: case create intake gate, case detail file-event tab, document create impact preview, and batch filing final-material gate.

## Explicit Non-Closure

No production Vue implementation, no backend/API/schema changes, no replacement of the existing 10-page Phase 1 mock package, no new independent file-center workflow.

## Remaining Follow-Up Task IDs

  - `CASEDOCK-FE-DOCIMPACT-01`
  - `CASEDOCK-FE-CASEDETAIL-01`
  - `CASEDOCK-FE-CASECREATE-01`
  - `CASEDOCK-FE-BATCHFILING-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. Static mock files only; no shared production frontend files. |
| prereq_dependency_density | Medium. Mock reflects future FileAsset/GateEvaluation/ImpactPlan/EffectLedger contracts without implementing them. |
| be_fe_coupling | Medium. Pages are contract visualizations and do not call APIs. |
| evidence_cost | Low. HTML structure checks and scoped diff evidence are sufficient. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-MOCK-MINUI-01.md`
- `fpms_case_document_gate_phase1/fpms_case_document_gate_minimal_ui_mock_index.html`
- `fpms_case_document_gate_phase1/mock-ui/pages/11_00_minimal_ui_change_index.html`
- `fpms_case_document_gate_phase1/mock-ui/pages/11_01_min_case_create_intake_gate.html`
- `fpms_case_document_gate_phase1/mock-ui/pages/11_02_min_case_detail_file_event_tab.html`
- `fpms_case_document_gate_phase1/mock-ui/pages/11_03_min_document_create_impact_preview.html`
- `fpms_case_document_gate_phase1/mock-ui/pages/11_04_min_batch_filing_final_gate.html`

## Verification Commands

- `test -f <each allowed mock html file>`
- `rg -n "未实现|TODO|lorem" <allowed mock html files>` must return no matches.
- `git diff -- <allowed files>` reviewed for static mock-only scope.

## Evidence Path

- `artifacts/CASEDOCK-MOCK-MINUI-01/`
