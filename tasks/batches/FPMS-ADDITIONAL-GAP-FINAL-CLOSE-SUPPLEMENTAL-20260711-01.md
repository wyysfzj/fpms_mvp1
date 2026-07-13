# FPMS Additional GAP Final-Close Supplemental Batch Manifest

Status: FROZEN / READY FOR EXECUTION
Program ID: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Parent final-close task: `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`
Task count: 8

## Story Shape Classification and runbook

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-multi-lane-parallel-story`

## Execution rules

These seven tasks are supplemental prerequisites discovered by Task47's final gates and remain
outside the frozen 47-entry manifest. Each row owns exactly one task file and one closure slice.
Product code is not authorized. SQLite-writing tests are serialized through
`/tmp/fpms_addgap_sqlite_test.lock`. Task63 must finish before Task47 resumes its secret scan;
Tasks64–69 must all finish before Task47 reruns full backend pytest. No implementer may approve its
own task. No commit, push, reset, clean, stash, checkout, or discard is authorized.

| Order | Task file | Exact closure | Allowlist ownership | Dependency |
|---|---|---|---|---|
| 63 | `tasks/additional_gaps/FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01.md` | Redact only raw secret substrings in the frozen hit list | frozen artifact hit paths plus Task63 evidence/task | Task47 secret-scan RED |
| 64 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02.md` | Align one atomicity fixture to confirmed grant deadline lineage | `backend/tests/test_addgap_document_create_atomicity.py` | Task24/35/37 |
| 65 | `tasks/additional_gaps/FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02.md` | Align one OA helper fixture in need-reply edit tests | `backend/tests/test_b_need_reply_deadline_edit_rule.py` | Task27 |
| 66 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02.md` | Align one document-search test file's OA fixtures | `backend/tests/test_document_specific_search_api.py` | Task27 |
| 67 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02.md` | Align one UI-path OA fixture | `backend/tests/test_document_ui_deadline_generation.py` | Task27 |
| 68 | `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02.md` | Align one wizard preview expectation to explicit deadline input | `backend/tests/test_document_wizard_task_preview.py` | Task27 |
| 69 | `tasks/additional_gaps/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02.md` | Align one frozen schema test to Task35 lineage carriers | `backend/tests/test_grant_fee_prereq_schema.py` | Task35 |
| 70 | `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01.md` | Align one obsolete OA_OUT auto-writeoff assertion to Task43's keep-open contract | `backend/tests/test_document_ui_deadline_generation.py` | Task43; Task67 fixture edit serialized first |

## Wave order

- Wave S1: Tasks63, 64, 65, and 69 may implement concurrently because their owned files do not overlap.
- Wave S2: Tasks66, 67, and 68 reuse released lanes.
- Wave S2b: Task70 serially owns the same test file after Task67 stops; Task67 is reverified only
  after Task70 PASS.
- Verification: all pytest invocations are serialized even when edits are concurrent.
- Final: Task47 appends Tasks63–69 to its supplemental ledger, reruns full gates, and closes itself.
