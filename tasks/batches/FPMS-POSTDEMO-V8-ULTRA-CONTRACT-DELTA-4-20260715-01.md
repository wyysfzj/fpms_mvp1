# FPMS Post-demo V8 Ultra Contract Delta-4 Supplemental Batch

Status: IN PROGRESS / ULTRA MATERIALIZATION ONLY / PRODUCT HIGH NOT STARTED
Controller task: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01`
Story Shape Classification: `shared_file_density=high`,
`prereq_dependency_density=high`, `be_fe_coupling=medium`, `evidence_cost=high`
Chosen runbook: `P0-prereq-heavy-story`

## Authority and phase boundary

This manifest is the exact 34-row materialization and later High execution authority for
Delta-4. During Ultra, rows 01–33 authorize only their named task-file edit by one owner;
row 34 alone owns this manifest and controller artifacts. No row authorizes product/test/
migration/script implementation, customer approval, source activation or release work.

Every row 01–33 receives an independent per-task verdict before row 34 closes. After the
cumulative overlay and controller reviews PASS, product execution still waits for the
user's manual switch to High. All SQLite-writing verification and all shared-file product
execution remain serialized.

## Exact rows

| # | Materialization wave | High execution wave | Exact task-file path | Owner role | Runbook | Exact materialization closure | Explicit materialization non-closure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | M4-A | H4-0 | `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01.md` | Backend architect | `P0-prereq-heavy-story` | Create the exact CASE_OPENED evidence-rule task contract. | no lifecycle implementation/test execution |
| 02 | M4-A | H4-0 | `tasks/postdemo/v8/FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01.md` | Backend architect | `P0-prereq-heavy-story` | Create the exact case-create evidence adapter task contract. | no case service/API implementation |
| 03 | M4-A | H4-0 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01.md` | Backend architect | `P0-prereq-heavy-story` | Create the exact filing-preparation evidence-rule task contract. | no lifecycle implementation/test execution |
| 04 | M4-A | H4-0 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01.md` | Backend architect | `P0-prereq-heavy-story` | Create the exact external-submission evidence-rule task contract. | no lifecycle implementation/test execution |
| 05 | M4-B | H4-2 | `tasks/postdemo/v8/FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01.md` | Backend architect | `P0-prereq-heavy-story` | Create the exact read-only filing evidence resolver task contract. | no resolver implementation or DB write |
| 06 | M4-B | H4-1 | `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01.md` | Document architect | `P0-prereq-heavy-story` | Create the exact two-role enum-extension task contract. | no enum implementation or adjacent role change |
| 07 | M4-B | H4-1 | `tasks/postdemo/v8/FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01.md` | Document architect | `P0-prereq-heavy-story` | Create the exact two-row registration-matrix task contract. | no service implementation or other matrix change |
| 08 | M4-B | H4-1 | `tasks/postdemo/v8/FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01.md` | Document architect | `P0-prereq-heavy-story` | Create the exact OA promotion/derivation/activity task contract. | no OA preparation/submission/lifecycle implementation |
| 09 | M4-C | H4-3 | `tasks/postdemo/v8/FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01.md` | Fee-domain architect | `P0-prereq-heavy-story` | Create the exact inactive layout-rate candidate task contract. | no activation or customer-rate promotion |
| 10 | M4-C | H4-3 | `tasks/postdemo/v8/FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01.md` | Fee-domain architect | `P0-prereq-heavy-story` | Create the exact inactive annuity-tier candidate task contract. | no activation or permissive tier parser |
| 11 | M4-C | H4-3 | `tasks/postdemo/v8/FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01.md` | Migration architect | `P0-prereq-heavy-story` | Create the six-column lineage/migration task contract. | no migration/model implementation or backfill |
| 12 | M4-C | H4-3 | `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01.md` | Migration architect | `P0-prereq-heavy-story` | Create the append-only legacy provenance carrier task contract. | no importer/migration execution or customer confirmation |
| 13 | M4-D | H4-0 | `tasks/postdemo/v8/FPMS-V8-LC-FILING-RECEIPT-ARCHIVED-20260712-01.md` | Backend architect | `P0-prereq-heavy-story` | Re-freeze the exact filing-receipt evidence rule contract. | no rule implementation or second event |
| 14 | M4-D | H4-1 | `tasks/postdemo/v8/FPMS-V8-DE-GENERATED-ATTACHMENT-EVIDENCE-ADAPTER-20260712-01.md` | Document architect | `P0-prereq-heavy-story` | Re-freeze generated attachment actor/role/hash/lineage behavior. | no adapter implementation or fake derivation |
| 15 | M4-D | H4-4 | `tasks/postdemo/v8/FPMS-V8-DE-REVIEW-API-20260712-01.md` | API architect | `P0-prereq-heavy-story` | Re-freeze the exact evidence-review HTTP contract. | no API/service implementation or router edit |
| 16 | M4-D | H4-2 | `tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md` | Backend architect | `P0-prereq-heavy-story` | Re-freeze actor, snapshot, replay and API allowlist behavior. | no adapter/API implementation |
| 17 | M4-E | H4-2 | `tasks/postdemo/v8/FPMS-V8-CASE-BATCH-FILING-EVENT-ADAPTER-20260712-01.md` | Backend architect | `P0-prereq-heavy-story` | Re-freeze atomic batch document/lifecycle evidence behavior. | no batch implementation or partial commit |
| 18 | M4-E | H4-2 | `tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md` | Backend architect | `P0-prereq-heavy-story` | Re-freeze exact operation, actor, idempotency and shared API path. | no adapter/API implementation |
| 19 | M4-E | H4-2 | `tasks/postdemo/v8/FPMS-V8-FILING-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md` | Backend architect | `P0-prereq-heavy-story` | Re-freeze archived receipt evidence/transaction behavior. | no receipt implementation or OA behavior change |
| 20 | M4-E | H4-1 | `tasks/postdemo/v8/FPMS-V8-OA-COPYABLE-ATTACHMENT-POLICY-20260712-01.md` | Document architect | `P0-prereq-heavy-story` | Re-freeze typed OA manifest/version cardinality policy. | no policy implementation or filename inference |
| 21 | M4-F | H4-1 | `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md` | Document architect | `P0-prereq-heavy-story` | Re-freeze promotion/policy prerequisites and exact DRAFT closure. | no OA seam implementation or external submission |
| 22 | M4-F | H4-4 | `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-CREATE-API-20260712-01.md` | API architect | `P0-prereq-heavy-story` | Re-freeze exact fee-reduction approval HTTP contract. | no API/service implementation or invented idempotency field |
| 23 | M4-F | H4-R | `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md` | Recovery architect | `P0-prereq-heavy-story` | Mark changed-mechanism recovery with valid RED preserved. | no contract redesign, RED rerun or product edit |
| 24 | M4-F | H4-5 | `tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md` | Fee-domain architect | `P0-prereq-heavy-story` | Re-freeze PAY/HOLD/ABANDON obligation-instruction adapter. | no adapter implementation or DEFER mapping |
| 25 | M4-G | H4-5 | `tasks/postdemo/v8/FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01.md` | Fee-domain architect | `P0-prereq-heavy-story` | Re-freeze six-field evidence/rate/obligation lineage behavior. | no service implementation or source inference |
| 26 | M4-G | H4-4 | `tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md` | Patent-fee architect | `P0-prereq-heavy-story` | Re-freeze the pure CNIPA 594 evidence/cardinality/amount policy. | no DB/HTTP/rate activation or whole-PCT flag |
| 27 | M4-G | H4-5 | `tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md` | Patent-fee architect | `P0-prereq-heavy-story` | Re-freeze the exact active CNIPA 246 read rule. | no rate write/activation or customer fallback |
| 28 | M4-G | H4-4 | `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md` | API architect | `P0-prereq-heavy-story` | Re-freeze exact bodyless decision-gate list API contract. | no API implementation or authority inference |
| 29 | M4-H | H4-5 | `tasks/postdemo/v8/FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01.md` | Migration architect | `P0-prereq-heavy-story` | Re-freeze grammar, approved manifest, plan hash and provenance import. | no importer implementation or production migration |
| 30 | M4-H | FOUNDATION-CLOSE | `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` | Independent close architect | `P0-prereq-heavy-story` | Propagate 216 Foundation nodes and all Delta-4 gates. | no Foundation/release execution |
| 31 | M4-H | FULL-ACTIVATION | `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md` | Independent close architect | `P0-prereq-heavy-story` | Require effective Foundation close before existing customer gates. | no customer-gate activation or product work |
| 32 | M4-H | FINAL-LEDGER | `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md` | Independent close architect | `P0-prereq-heavy-story` | Propagate all 302 product nodes and four Delta overlays. | no ledger close or governance miscount |
| 33 | M4-I | FINAL-CLOSE | `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md` | Independent close architect | `P0-prereq-heavy-story` | Require cumulative Delta-4 validation before unchanged final release gate. | no release execution/movement/weakening |
| 34 | M4-J | AUDIT-ONLY | `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01.md` | Ultra controller | `P0-prereq-heavy-story` | Build/review this manifest and deterministic cumulative overlay. | no row 01–33, product, parent, AGENTS or release edit; no self-approval |

## Shared ownership and High order

1. Lifecycle rule product execution: D4-01 → D4-03 → D4-04 → row 13.
2. Case service product execution: accepted Task 55 → D4-02 → row 17.
3. Official workflow shared service/API: D4-05 PASS, then row 16 → row 18 → row 19;
   row 16 and row 18 alone add exact `backend/app/modules/official_workflows/api.py`.
4. Document chain: D4-06 → D4-07 → D4-08 → row 20 → row 21; row 14 waits for D4-06/07
   and precedes row 15 on exact `backend/app/modules/documents/api.py` ownership.
5. Migration chain: D4-11 → D4-12 only; no other migration or SQLite writer overlaps.
6. Rate candidates D4-09/D4-10 may implement concurrently, but SQLite verification is
   serial; production activation is explicit and outside materialization.
7. Close order is controller → all required product/audit gates → Foundation → Full →
   item-to-slice ledger → final close → existing release gate last.

## Batch done definition

- All 34 paths are unique; rows 01–33 contain exact closure, non-closure, allowlist,
  dependencies, runbook, TDD/verification, evidence and Done Definition and remain product
  NOT STARTED.
- Deterministic overlay proves parent hashes, normalized task anchors, 302/216/86, zero
  unresolved/cycle, exact shared/migration/SQLite/close order and Task 110 recovery.
- Independent review ledger carries a separate APPROVED/P0=P1=P2=0 verdict for every row;
  controller receives independent task-shape/scope and graph/domain/fail-closed approvals.
- Row 34 gates and evidence pass before manual High routing.
