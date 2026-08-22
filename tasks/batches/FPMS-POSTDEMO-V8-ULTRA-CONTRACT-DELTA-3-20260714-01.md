# FPMS Post-demo V8 Ultra Contract Delta-3 Supplemental Batch

Status: PASS / ROW 15 CLOSED 2026-07-14 / MANUAL HIGH SWITCH REQUIRED
Controller task: `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
Story Shape Classification: `shared_file_density=high`,
`prereq_dependency_density=high`, `be_fe_coupling=low`, `evidence_cost=high`
Chosen runbook: `P0-prereq-heavy-story`

## Authority and phase boundary

This one supplemental manifest has exactly one row per exact task-file path. During Ultra
materialization, it authorizes only row-contract edits by one architect owner per row; it
does not authorize product, test or repository-tool implementation. After all rows,
cumulative overlay and independent reviews PASS, and only after the user manually switches
to High, the `High execution wave` column becomes the authoritative supplemental execution
order for these exact task files.

Rows 01–14 never permit one agent to implement more than one task file. Row 15 is the sole
owner of this manifest and its controller artifacts. The immutable 197-row Foundation
manifest and 283/197/86 baseline remain read-only.

`FPMS-V8-ULTRA-RAW-EVIDENCE-LINEAGE-CORRECTION-20260714-01` is the independently
approved, audit-only pre-controller authority prerequisite that resolves rejected/current
RAW evidence lineage. It is not a sixteenth materialization row, product-graph node or
Foundation task. Row 15 cannot PASS unless its task/evidence gates and frozen 29-file
inventory authority validate.

## Exact rows

| # | Materialization wave | High execution wave | Exact task-file path | Owner role | Runbook | Exact materialization closure | Explicit materialization non-closure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | M3-1 | H3-2 | `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Create the one-service RAW registration role/state guard contract. | no product/test implementation, enum edit or second service rule |
| 02 | M3-1 | H3-2 | `tasks/postdemo/v8/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Create the one-service external-submission positive-role allowlist contract. | no product/test implementation, enum edit or adapter work |
| 03 | M3-2 | H3-3 | `tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Re-freeze the rejected RAW enum task behind both guards and real-member regressions. | no enum implementation or rejected-history deletion |
| 04 | M3-2 | DEPENDENCY-SCHEDULER | `tasks/postdemo/v8/FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Insert the external-submission allowlist into the workflow-service predecessor chain. | no OA service implementation or closure change |
| 05 | M3-3 | DEPENDENCY-SCHEDULER | `tasks/postdemo/v8/FPMS-V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-20260712-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Add the external-submission role guard as a direct adapter prerequisite. | no filing adapter implementation or role-policy duplication |
| 06 | M3-3 | DEPENDENCY-SCHEDULER | `tasks/postdemo/v8/FPMS-V8-OA-EXTERNAL-SUBMISSION-EVIDENCE-20260712-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Add the external-submission role guard as a direct OA adapter prerequisite. | no OA adapter implementation, task close or role-policy duplication |
| 07 | M3-1 | H3-0 | `tasks/repo/REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01.md` | Repository governance worker | `P0-single-lane-story` | Create the structural JSONL repository task-gate contract. | no script/test implementation, new evidence requirement or release gate |
| 08 | M3-2 | H3-1 | `tasks/repo/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01.md` | Repository governance worker | `P0-prereq-heavy-story` | Create the common-manifest ownership and isolated atomic-validator contract. | no wrapper/test implementation, external skill edit or scope ignore |
| 09 | M3-4 | FOUNDATION-CLOSE | `tasks/postdemo/v8/FPMS-V8-FOUNDATION-CLOSE-20260712-01.md` | Independent close reviewer | `P0-prereq-heavy-story` | Require controller, seven product externals, G1/G2 and cumulative 204-task validation. | no Foundation implementation, immutable manifest rewrite or release gate |
| 10 | M3-4 | FULL-ACTIVATION | `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md` | Independent close reviewer | `P0-prereq-heavy-story` | Require cumulative delta-3 validation through effective Foundation before Full. | no customer-gate activation or 7 GLOBAL + 22 form semantic change |
| 11 | M3-5 | FINAL-LEDGER | `tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md` | Independent close reviewer | `P0-prereq-heavy-story` | Add delta-3, seven product externals and audit-only G1/G2 to the final ledger. | no product/audit count conflation or ledger close |
| 12 | M3-5 | FINAL-CLOSE | `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md` | Independent close reviewer | `P0-prereq-heavy-story` | Require cumulative validator and every delta-3 gate before the unchanged release gate. | no release execution, movement, duplication or weakening |
| 13 | M3-3 | DEPENDENCY-SCHEDULER | `tasks/postdemo/v8/FPMS-V8-DE-ATTACHMENT-EVIDENCE-ATOMIC-ADAPTER-20260712-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Record that the RAW dependency now transitively includes both fail-closed guards. | no attachment adapter implementation or direct guard duplication |
| 14 | M3-4 | DEPENDENCY-SCHEDULER | `tasks/postdemo/v8/FPMS-V8-OVERLAY-CONTRACTS-20260712-01.md` | Backend architect worker | `P0-prereq-heavy-story` | Record that RAW overlay typing inherits both guards without granting gate authority. | no overlay implementation, DTO change or direct guard duplication |
| 15 | M3-6 | AUDIT-ONLY | `tasks/postdemo/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01.md` | Ultra materialization controller | `P0-prereq-heavy-story` | Build and independently audit this manifest and deterministic cumulative overlay. | no row 01–14, product, parent, AGENTS or release edit; no self-approval |

## Common execution-manifest rule

- Row 07 (G1) executes alone in H3-0. Row 08 (G2) depends on G1 and executes alone in
  H3-1. Neither is a product-graph node.
- Rows 01 and 02 are the only H3-2 peers. This exact file is their one common authoritative
  execution manifest. Each task's atomic validation must name this manifest and the other
  row's task ID through the G2 wrapper.
- Both H3-2 implementations may proceed concurrently, but their SQLite-writing RED/GREEN
  commands are serialized with `GLOBAL_SQLITE_SERIAL_QUEUE` maximum writers `1`.
- Row 03 starts only after rows 01 and 02 PASS and reruns both guard suites with the real
  `EvidenceRole.RAW_ATTACHMENT` member.
- `DEPENDENCY-SCHEDULER` rows rejoin the cumulative Foundation graph only when their own
  canonical prerequisites and shared-file predecessors are PASS. The label is not a
  waiver of file-conflict checks.
- After G2 PASS, every declared-peer validation in any V8 wave uses its one common
  authoritative execution manifest. Unknown, cross-manifest or shared-owner peers fail
  closed; single-lane validation may use the wrapper's no-peer direct-helper path.

## Shared ownership and close order

1. `evidence_service.py`: accepted register → derivation → current → review → row 01 →
   remaining accepted owners.
2. `evidence_workflow_service.py`: accepted finalize seam → row 02 → row 04 → remaining
   accepted owners.
3. G1 solely owns `scripts/task_validate.sh`; G2 solely owns
   `scripts/atomic_evidence_validate.py`; order is G1 → G2.
4. Filing and OA adapter shared owners remain serialized in their existing relative order.
5. All SQLite-writing tests and all shared-file verification remain serialized.
6. Effective product graph is 290, Foundation is 204, deferred is 86. G1/G2/controllers
   stay audit-only outside product counts.
7. Close order is cumulative controller → all required product/audit gates → Foundation
   → Full → item-to-slice ledger → final close → existing release gate last.

## Batch done definition

- All 15 paths are unique; rows 01–14 have one closure, non-closure, allowlist,
  dependency/runbook and evidence command and remain NOT STARTED after materialization.
- Parent bytes and latest overlay task hashes validate before Status normalization; the
  RAW blocked successor is the only explicit exception.
- The audit-only RAW evidence-lineage correction is PASS and the cumulative overlay
  validates its task, review, evidence gates and immutable 29-file rejection snapshot.
- Deterministic overlay proves 290 nodes, zero unresolved, zero cycles and 204 unique
  Foundation product IDs without counting G1/G2.
- Two independent controller reviews approve task shape/scope and graph/tool/close safety.
- Row 15 becomes PASS before any High row; then execution pauses for the user's manual
  switch to High.
