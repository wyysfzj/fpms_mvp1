# FPMS Post-demo V8 Ultra Contract Delta-2 Materialization Batch

Status: PASS
Controller task: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01`
Story Shape Classification: `shared_file_density=high`,
`prereq_dependency_density=high`, `be_fe_coupling=high`, `evidence_cost=high`
Chosen runbook: `P0-prereq-heavy-story`

This is a contract-materialization manifest only; it is not product implementation
authorization. Every row has one exact task-file owner. It never permits one worker to
implement more than one product task, and rows 01–24 remain NOT STARTED after this batch.

## Exact rows

| # | Wave | Exact task-file path | Owner role | Runbook | Exact materialization closure | Non-closure |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | M2-1 | `tasks/postdemo/v8/FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01.md` | Architect worker | `P0-single-lane-story` | Create the one-test semantic migration prerequisite. | no product implementation or second closure |
| 02 | M2-1 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Add the exact second registry-rule contract. | no product implementation or second closure |
| 03 | M2-1 | `tasks/postdemo/v8/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Add the reviewed-Word lineage paths and fail-closed errors. | no product implementation or second closure |
| 04 | M2-2 | `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md` | Architect worker | `P0-single-lane-story` | Create the additive fail-closed raw-evidence-role prerequisite. | no product implementation or second closure |
| 05 | M2-2 | `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze wire, raw-role, actor, transaction and compensation contracts. | no product implementation or task-75 absorption |
| 06 | M2-2 | `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze the sole confirm/revoke POST adapter. | no product implementation or second endpoint |
| 07 | M2-3 | `tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze the sole obligation-instruction POST adapter. | no product implementation or payment side effect |
| 08 | M2-3 | `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze the exact four-query no-write detail service. | no product implementation or state mutation |
| 09 | M2-3 | `tasks/postdemo/v8/FPMS-V8-ANNUITY-FIRST-TEN-YEAR-REDUCTION-SCOPE-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze the independent annuity-reduction wrapper. | no product implementation or unrelated fee rule |
| 10 | M2-4 | `tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Freeze exact DTOs and repeated-code composite gate collection. | no product implementation or code-only identity |
| 11 | M2-4 | `tasks/postdemo/v8/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Resolve 7 case plus 22 form entries independently. | no ALL-22 public request |
| 12 | M2-4 | `tasks/postdemo/v8/FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Preserve the 29-entry snapshot across keyset pages. | no gate-code dedup or first-page loss |
| 13 | M2-5 | `tasks/postdemo/v8/FPMS-V8-OVERLAY-HTTP-20260712-01.md` | Architect worker | `P0-prereq-heavy-story` | Serialize all 29 scoped entries unchanged. | no product implementation or response collapse |
| 14 | M2-5 | `tasks/postdemo/v8/FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01.md` | Architect worker | `P0-frontend-heavy-story` | Preserve composite gate identity in the typed adapter. | no Record keyed only by gate code |
| 15 | M2-5 | `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-GATES-WARNINGS-UI-20260712-01.md` | Frontend architect worker | `P0-frontend-heavy-story` | Render distinct scopes and reasons in Simplified Chinese. | no product implementation or classification activation |
| 16 | M2-6 | `tasks/postdemo/v8/FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01.md` | Frontend architect worker | `P0-frontend-heavy-story` | Restrict load-more dedup to milestones. | no gate snapshot replacement |
| 17 | M2-6 | `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-FE-ADAPTER-20260712-01.md` | Frontend architect worker | `P0-frontend-heavy-story` | Freeze strict preview types and isolated compile. | no full typecheck or legacy overload |
| 18 | M2-6 | `tasks/postdemo/v8/FPMS-V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-ADAPTER-20260712-01.md` | Frontend architect worker | `P0-frontend-heavy-story` | Keep the existing sole UI owner and explicit estimate context/date. | no duplicate callsite task |
| 19 | M2-7 | `tasks/postdemo/v8/FPMS-V8-LIVE-FIXTURE-20260712-01.md` | Tester architect worker | `P0-prereq-heavy-story` | Prove 29 scoped entries and fallback provenance in the live fixture. | no product implementation or parallel SQLite write |
| 20 | M2-7 | `tasks/postdemo/v8/FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01.md` | Tester architect worker | `P0-prereq-heavy-story` | Assert 29 composite identities through the real stack. | no route fulfillment or full Playwright scope |
| 21 | M2-7 | `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` | Reviewer architect worker | `P0-prereq-heavy-story` | Add delta-2 controller and two external gates to Foundation audit. | no manifest rewrite or release close |
| 22 | M2-8 | `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md` | Reviewer architect worker | `P0-prereq-heavy-story` | Require seven GLOBAL plus 22 form-scoped requests. | ALL-22 remains fallback-only |
| 23 | M2-8 | `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md` | Reviewer architect worker | `P0-prereq-heavy-story` | Include both overlays and all five external tasks. | no non-catalog omission |
| 24 | M2-8 | `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md` | Reviewer architect worker | `P0-prereq-heavy-story` | Validate both controllers/overlays and all five external gates. | no release-gate move, duplication or weakening |
| 25 | M2-9 | `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01.md` | Ultra controller | `P0-prereq-heavy-story` | Build and audit this deterministic manifest and additive overlay. | no row 01–24, product, parent or AGENTS.md edit; no self-approval |

## Shared ownership and verification order

1. Rows 01–24 were materialized by distinct owners; M2-9 alone owns this manifest and
   delta-2 artifact family.
2. `backend/app/modules/cases/lifecycle_rules.py` remains serialized; the legacy test
   migration gates the second registry rule without editing source itself.
3. `backend/app/modules/documents/evidence_contracts.py` orders accepted contracts before
   `RAW_ATTACHMENT`; `backend/app/modules/documents/service.py` preserves all nine existing
   owners in relative order, including task 75 after the grant adapter.
4. Backend API/service and frontend API/component shared owners remain serialized.
   Composite identity is `(gate_code, requested_scope_key)` and all 29 entries survive
   every overlay page.
5. `GLOBAL_ALEMBIC_HEAD` and `GLOBAL_SQLITE_SERIAL_QUEUE` remain single-owner queues;
   SQLite-writing verification has maximum concurrency one.
6. Foundation closes only after both controllers and all five external tasks. Full
   activation requires 7 GLOBAL plus 22 form scopes. Final close keeps the existing
   release gate last.

## Batch done definition

- All 25 paths are unique and rows 01–24 remain High-ready, Ultra-frozen and NOT STARTED.
- Deterministic overlay validates immutable parent hashes/counts, 22 overrides, two new
  prerequisites, effective graph 288 and effective Foundation 202.
- Two independent read-only controller reviews approve before row 25 becomes PASS.
