# FPMS V8 Input Activation Decoupling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the payment-workbook and service-price capabilities without real customer inputs while keeping every production activation, formal workbook, and service-receivable action fail-closed until an exact reviewed input is active.

**Architecture:** One successor-authority task changes only dependency interpretation, then two independent lanes implement payment-workbook and service-price capabilities. Production resolution accepts only reviewed, effective `PRODUCTION` inputs; isolated tests use explicitly classified `TEST_ONLY` inputs under server-controlled `fpms_env=test`. Full/Final close after both capabilities are verified and records `CONFIG_REQUIRED` when real inputs are still absent.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, SQLite, pytest, Ruff, Vue 3, TypeScript, Vite, Playwright, repository task/evidence gates.

---

## 1. Authority, execution mode, and immutable boundaries

Authoritative inputs:

- `docs/superpowers/specs/2026-08-12-fpms-v8-input-activation-decoupling-design.md`
- design review commit `bd88cb3e38d88ef83359f4b2c70e2454bb27aeb4`
- design patch SHA-256 `8f471d53690b91a222591c991c6b602cae65f827c37a8c01d3ab77578cea3b0c`
- customer written adoption in the current Codex thread on 2026-08-13
- existing exact task cards for catalog rows 175, 176, 214–229, 278 and 281–283

Hard boundaries:

- Do not modify `docs/product/v8/catalog.frozen.json`.
- Do not record either customer decision gate as positively resolved without a real reviewed input.
- `TEST_ONLY` is never a production seed, default, fallback, or production-active source.
- `fpms_env` is server configuration; request payloads cannot set or override it.
- Production workbook resolution accepts only one exact
  `PRODUCTION + workflow_status=APPROVED + activation_status=ACTIVE` version whose retained
  validation tuple, interval, hashes and current identity match.
- `PRODUCTION_INPUT_ACTIVE` additionally requires the exact persisted
  `DG-PAYMENT-WORKBOOK:GLOBAL` or `DG-SERVICE-RATE-VERSION:GLOBAL` authority applicable to the
  lane; an active carrier alone is insufficient.
- Test workbook resolution is available only when `fpms_env == "test"`; it accepts exactly one
  explicitly selected `TEST_ONLY + workflow_status=APPROVED + activation_status=INACTIVE` record
  with a retained validation tuple from isolated test data.
  It never publishes `current_identity_key`, and production code paths reject it in every other
  environment.
- Official fee, generated workbook, official-site acceptance, payment, ticket verification and
  service receivable remain separate facts.
- Implementers do not approve their own tasks. SQLite-writing verification, migrations, shared
  routers, shared models, frontend typecheck and final broad checks are serialized.
- Preserve `backend/uv.lock` and all unrelated dirt. Do not push, reset, clean, stash or discard.

## 2. File ownership map

| File or ownership group | Responsibility | Serialized owner order |
| --- | --- | --- |
| successor adoption, appendices and four successor task cards | capability-vs-production dependency authority | Task 1 only |
| `tasks/batches/FPMS-POSTDEMO-V8-PAYMENT-WORKBOOK-GATE-20260712-01.md` | frozen 11-member payment lane manifest | row 175 only |
| `tasks/batches/FPMS-POSTDEMO-V8-SERVICE-RATE-GATE-20260712-01.md` | frozen 8-member service-rate lane manifest | row 176 only |
| `backend/alembic/versions/v8_payment_workbook_input_version.py` | workbook input carrier migration | WB-I1 before row 223 |
| `backend/app/modules/annuity/models.py` | workbook input ORM | WB-I1 only, serialized |
| `backend/app/modules/annuity/verified_official_payment_workbook.py` | safe `.xlsm` validation/fill; never execute macros | row 214 only |
| `backend/app/modules/annuity/official_payment_workbook_input_service.py` | workbook input state machine and resolver | WB-I2 only |
| `backend/app/modules/annuity/api.py` | workbook admin/generation/acceptance HTTP | WB-I3, then rows 216 and 220 |
| `backend/app/modules/annuity/service.py` | generation and acceptance services | row 215, then row 219 |
| frontend annuity API/types/page files | workbook generation and acceptance UI | rows 217, 218, 221, 222 in their task-card order |
| `backend/alembic/versions/v8_w6_service_price_book.py` | service-price migration | row 223 after WB-I1 migration |
| `backend/app/modules/fees/models.py` | service-price ORM | row 223 only, serialized |
| `backend/app/modules/fees/service_price_book.py` | import then activation state machine | rows 224 then 226 |
| `backend/app/modules/fees/api.py` and schemas | import, activation, receivable HTTP | rows 225, 227, 229 |
| `backend/app/modules/fees/obligation_service.py` | service receivable creation | row 228 only |
| Full/Final ledgers and broad verification | final acceptance only | rows 281 → 282 → 283 |

No two active agents may own the same row or shared file. The main controller may run read-only
preflight while workers edit disjoint files.

## 3. Wave map

| Wave | Lane A — payment workbook | Lane B — service price | Serialized lane |
| --- | --- | --- | --- |
| 0 | — | — | Task 1 successor adoption and four task-card materializations |
| 1 | row 175 manifest | row 176 manifest | manifest tests may run in parallel; close separately |
| 2 | WB-I1 carrier | — | migration/model/SQLite |
| 3 | row 214 adapter | row 223 carrier after WB-I1 | migrations remain sequential |
| 4 | WB-I2 governance service | row 224 import service | SQLite tests one at a time |
| 5 | WB-I3 admin API | row 225 import API | `annuity/api.py` and `fees/api.py` are disjoint |
| 6 | rows 215/216 generation service/API | rows 226/227 activation service/API | shared-file order within each module |
| 7 | rows 217/218 FE/UI | rows 228/229 receivable service/API | frontend typecheck serialized |
| 8 | rows 219/220 acceptance service/API | — | `annuity/service.py` then `annuity/api.py` |
| 9 | rows 221/222 acceptance FE/UI | — | frontend typecheck serialized |
| 10 | row 278 isolated full-stack E2E | — | Playwright single worker |
| 11 | — | — | capability close, then rows 281 → 282 → 283; release last |

The mandatory payment dependency spine is exactly
`row 175 → WB-I1 → row 214 → WB-I2 → WB-I3 → rows 215–222 → row 278`.
The service-price spine starts `row 176 → row 223 → rows 224–229`.

## 4. Canonical per-task close loop

Every product task below uses the same close loop after its task-specific RED/GREEN:

- [ ] Stabilize all task-owned bytes and metadata.
- [ ] Run scoped Ruff/ESLint/typecheck/diff checks from the exact task card.
- [ ] Generate one baseline-subtracted candidate/scope; do not regenerate without a byte change.
- [ ] Obtain one independent HIGH review bound to the exact candidate; require zero P0/P1/P2.
- [ ] Submit review, run repository task gate, atomic evidence validation and `fast-close-1` accept.
- [ ] Confirm terminal PASS before releasing ownership or starting a dependent task.
- [ ] Commit only the exact task allowlist; never include `backend/uv.lock`.

## 5. Task 1 — Adopt the successor authority and materialize execution contracts

**Files:**

- Create: `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-DECOUPLING-ADOPTION-20260813-01.md`
- Create: `docs/product/v8/reviews/V8-INPUT-ACTIVATION-DECOUPLING-CURRENT-ADOPTION.md`
- Create: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01.md`
- Create: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01.md`
- Create: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01.md`
- Create: `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md`
- Create: `backend/tests/test_v8_input_activation_decoupling_contract.py`

The exact existing task-card allowlist for latest-wins appendices is:

```text
tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md
tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01.md
tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01.md
tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01.md
tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md
tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md
```

Task 1 also owns only its own task/evidence paths. It does not create or modify either lane batch
manifest; those files do not exist at the parent and remain owned by rows 175 and 176.

- [ ] **Step 1: Materialize the task and initialize evidence before other edits.**

  The closure is only successor adoption and dependency correction. Non-closure prohibits product
  code, frozen catalog changes and positive production decisions.

- [ ] **Step 2: Write the failing contract test.**

  Assert the exact design commit/hash, customer-adopted authority, all affected IDs, three WB task
  IDs, dependency order, `CAPABILITY_READY`, `CONFIG_REQUIRED`, production gate retention,
  `TEST_ONLY` isolation and unchanged frozen-catalog SHA-256.

- [ ] **Step 3: Run RED.**

  Run: `cd backend && .venv/bin/pytest -q tests/test_v8_input_activation_decoupling_contract.py`

  Expected: FAIL because the adoption record, four exact successor task cards and latest-wins
  appendices are absent. It must not expect either lane batch manifest.

- [ ] **Step 4: Add one latest-wins appendix to each affected existing task.**

  The appendix changes only the external prerequisite interpretation:

  ```text
  Development prerequisite: adopted successor + exact code dependencies.
  Production prerequisite: original DG-* gate plus reviewed active real input.
  Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
  ```

  Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.
  The row-175 and row-176 task appendices permit their existing manifest-creation closures without
  a positive real-input decision, but their frozen membership counts remain exactly 11 and 8;
  WB-I1/I2/I3 are external successor prerequisites, never new manifest members. Full/Final appendices accept
  `CONFIG_REQUIRED` only with verified negative-path evidence and prohibit any activation claim.

- [ ] **Step 5: Materialize all four successor task cards before product edits.**

  Each card must contain exact closure, non-closure, allowlist, dependencies, targeted RED/GREEN,
  serialized ownership, evidence path and independent close. The capability-close card is QA-only.
  Run repository atomic task-shape checks on all four cards.

- [ ] **Step 6: Run GREEN and scoped checks.**

  Run:

  ```bash
  cd backend && .venv/bin/pytest -q tests/test_v8_input_activation_decoupling_contract.py
  cd backend && .venv/bin/ruff check tests/test_v8_input_activation_decoupling_contract.py
  git diff --check -- \
    docs/product/v8/reviews/V8-INPUT-ACTIVATION-DECOUPLING-CURRENT-ADOPTION.md \
    backend/tests/test_v8_input_activation_decoupling_contract.py \
    tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-DECOUPLING-ADOPTION-20260813-01.md \
    tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01.md \
    tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01.md \
    tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01.md \
    tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md \
    tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md \
    tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md
  ```

  Expected: PASS; the frozen catalog hash is unchanged.

- [ ] **Step 7: Independently review, close and commit.**

  Commit message: `docs(v8): activate input decoupling successor`

## 6. Tasks 2–3 — Create and close the two original lane manifests

### Task 2 / row 175 — Payment-workbook manifest

**Files:** use the existing row-175 task card allowlist only.

- [ ] **Step 1: Initialize row-175 evidence after Task 1 terminal PASS.**
- [ ] **Step 2: Run its exact RED; expect failure because the batch manifest is absent.**
- [ ] **Step 3: Create
  `tasks/batches/FPMS-POSTDEMO-V8-PAYMENT-WORKBOOK-GATE-20260712-01.md` with exactly the original
  activation row, nine product rows 214–222 and row 278. Do not add WB-I1/I2/I3 as members.**
- [ ] **Step 4: Record the three WB successors as external prerequisite authority only, distinguish
  `CAPABILITY_READY` from production activation, and retain the exact 11-member count.**
- [ ] **Step 5: Run the exact focused GREEN/Ruff/diff checks from row 175.**
- [ ] **Step 6: Independently close and commit `docs(v8): activate payment workbook capability lane`.**

### Task 3 / row 176 — Service-rate manifest

**Files:** use the existing row-176 task card allowlist only.

- [ ] **Step 1: Initialize row-176 evidence after Task 1 terminal PASS.**
- [ ] **Step 2: Run its exact RED; expect failure because the batch manifest is absent.**
- [ ] **Step 3: Create
  `tasks/batches/FPMS-POSTDEMO-V8-SERVICE-RATE-GATE-20260712-01.md` with exactly the original
  activation row and seven product rows 223–229.**
- [ ] **Step 4: Distinguish capability acceptance from production activation, retain the exact
  `8-member count`, and do not add external successors as members.**
- [ ] **Step 5: Run exact focused GREEN/Ruff/diff checks from row 176.**
- [ ] **Step 6: Independently close and commit `docs(v8): activate service rate capability lane`.**

Rows 175 and 176 touch disjoint files and may implement/review in parallel, but each reaches its own
terminal PASS before its lane's first product task.

## 7. Task 4 / WB-I1 — Payment workbook input version carrier

**Files:**

- Modify: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01.md`
- Create: `backend/alembic/versions/v8_payment_workbook_input_version.py`
- Modify: `backend/app/modules/annuity/models.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_v8_payment_workbook_input_version.py`

Preflight: `cd backend && PYTHONPATH=. .venv/bin/alembic heads` must return exactly one head. At
planning time it is `v8_grant_official_copy_01`; if Task 1 or accepted concurrent work changed the
head, freeze the observed single head as `down_revision` before RED. Never create a branch or merge.

- [ ] **Step 1: Verify the already materialized exact card and initialize its evidence before source
  edits. Do not alter its frozen schema semantics.**

  Create `OfficialPaymentWorkbookInputVersion` / `t_official_payment_workbook_input_version` with
  application UUID ID and these exact fields:

  ```text
  id, scope_key, source_classification, template_version,
  template_storage_path, template_content_hash,
  upload_proof_storage_path, upload_proof_content_hash,
  structure_snapshot, structure_snapshot_hash,
  workflow_status, validated_by, validated_at, validation_reason,
  reviewed_by, reviewed_at, review_reason,
  activation_status, activated_by, activated_at,
  retired_by, retired_at, retirement_reason,
  effective_from, effective_to, supersedes_version_id,
  idempotency_key, current_identity_key,
  created_by, created_at, updated_by, updated_at
  ```

  Use `String(36)` IDs, `String(64)` hashes, `String(128)` versions/identity, `Text` paths/snapshots/
  reasons, `DateTime(timezone=False)` times and `CURRENT_TIMESTAMP`. Status vocabularies are:

  ```text
  source_classification: PRODUCTION | TEST_ONLY
  workflow_status: DRAFT | VALIDATED | APPROVED | REJECTED
  activation_status: INACTIVE | ACTIVE | RETIRED
  ```

  Named constraints must enforce `scope_key='GLOBAL'`, hash length 64, interval ordering and the
  approved exact workflow tuple: DRAFT has no validation/review tuple; VALIDATED has a complete
  validation tuple and no review tuple; APPROVED/REJECTED retain the complete validation tuple and
  add a complete review tuple with `reviewed_by <> created_by`. ACTIVE is allowed only for
  `PRODUCTION + workflow_status=APPROVED` with
  `current_identity_key='GLOBAL'`. RETIRED retains original activation actor/time plus retirement
  actor/time/reason and clears current identity. Add unique `(scope_key, template_version)`,
  idempotency key and nullable current identity, user FKs with RESTRICT, self-supersede FK with
  RESTRICT, and one scope/status/effective interval index. Migration is forward-only.

- [ ] **Step 2: Write RED schema tests.**

  Prove exact ORM/reflected columns and constraints; cross-user review; invalid TEST_ONLY ACTIVE;
  one active GLOBAL row; interval/hash/status failures; clean upgrade head; no seed rows.

- [ ] **Step 3: Run RED.**

  Run: `cd backend && .venv/bin/pytest -q tests/test_v8_payment_workbook_input_version.py`

  Expected: FAIL because the table/model/migration is absent.

- [ ] **Step 4: Implement the minimum model and migration.**

  Do not add services, relationships, seed data or a second carrier.

- [ ] **Step 5: Run serialized GREEN.**

  ```bash
  cd backend && .venv/bin/pytest -q tests/test_v8_payment_workbook_input_version.py
  cd backend && .venv/bin/ruff check alembic/versions/v8_payment_workbook_input_version.py app/modules/annuity/models.py app/models/__init__.py tests/test_v8_payment_workbook_input_version.py
  cd backend && PYTHONPATH=. .venv/bin/alembic heads
  cd backend && tmp_db="$(mktemp -t fpms_wbi1).db" && DATABASE_URL="sqlite:///$tmp_db" PYTHONPATH=. .venv/bin/alembic upgrade head
  ```

  Expected: all PASS; one Alembic head; no inserted workbook input.

- [ ] **Step 6: Close and commit.**

  Commit message: `feat(v8): add payment workbook input version carrier`

## 8. Task 5 / row 214 — Safe workbook adapter using a TEST_ONLY fixture

**Files:** use the existing exact row-214 task card allowlist only.

- [ ] **Step 1: Add the latest successor reference to the task-owned card if Task 1 did not already
  freeze it; do not recapture the original dirty baseline.**
- [ ] **Step 2: Write/retain RED proving the adapter is absent and the fixture is explicitly
  TEST_ONLY.**
- [ ] **Step 3: Run the corrected RED command.**

  Run: `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_workbook_adapter.py`

  Expected: FAIL on missing adapter behavior. Do not pass the binary `.xlsm` to pytest as a test
  module; that obsolete command is superseded by Task 1.

- [ ] **Step 4: Implement a pure adapter interface.**

  Required public operations:

  ```python
  validate_template(path: Path) -> WorkbookStructureSnapshot
  fill_template(path: Path, rows: Sequence[OfficialPaymentRow]) -> bytes
  ```

  Open packages without executing VBA; preserve `vbaProject.bin`, worksheet order, hidden sheets,
  columns and validations. Reject structure mismatch before producing output. Do not query gates or
  persist artifacts.

- [ ] **Step 5: Run focused GREEN and exact row-214 checks.**
- [ ] **Step 6: Close and commit.**

  Commit message: `feat(v8): add safe official payment workbook adapter`

## 9. Task 6 / WB-I2 — Workbook input governance service

**Files:**

- Modify: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01.md`
- Create: `backend/app/modules/annuity/official_payment_workbook_input_service.py`
- Create: `backend/tests/test_v8_payment_workbook_input_service.py`

- [ ] **Step 1: Freeze command/result DTOs in the task card.**

  ```python
  RegisterWorkbookInputCommand(
      template_version, template_storage_path, expected_template_hash,
      upload_proof_storage_path, expected_upload_proof_hash,
      effective_from, effective_to, source_classification,
      actor_id, idempotency_key, runtime_profile,
  )
  ReviewWorkbookInputCommand(version_id, decision, reason, actor_id)
  ActivateWorkbookInputCommand(version_id, actor_id, at, idempotency_key, runtime_profile)
  RetireWorkbookInputCommand(version_id, reason, actor_id, at, idempotency_key)
  ResolveWorkbookInputCommand(at, runtime_profile)
  ```

  `runtime_profile` is supplied by trusted server configuration, never request JSON. Results expose
  server state only. Services call `flush()` but never commit.

- [ ] **Step 2: Write RED tests.**

  Cover path existence, streamed SHA-256 recomputation, structure validation through row 214,
  canonical snapshot/hash, idempotent replay, conflicting replay, second-person approval, interval,
  predecessor, active replacement, retire, missing/ambiguous production source, and no-write on
  every failure. `fpms_env=test` may resolve exactly one approved/validated INACTIVE TEST_ONLY row;
  any other environment or ambiguity rejects it. TEST_ONLY never receives ACTIVE/current identity.

- [ ] **Step 3: Run RED.**

  Run: `cd backend && .venv/bin/pytest -q tests/test_v8_payment_workbook_input_service.py`

- [ ] **Step 4: Implement the minimum deep service.**

  Use delimiter-safe canonical JSON (`ensure_ascii=False`, `sort_keys=True`, compact separators,
  `allow_nan=False`). Recompute hashes from managed files, never trust payload hashes alone. Call
  row-214 validation; never import/execute macros. Resolver accepts exactly one eligible row.

- [ ] **Step 5: Run focused serialized GREEN and Ruff.**
- [ ] **Step 6: Close and commit.**

  Commit message: `feat(v8): govern payment workbook inputs`

## 10. Task 7 / WB-I3 — Protected workbook input admin API

**Files:**

- Modify: `tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01.md`
- Modify: `backend/app/modules/annuity/api.py`
- Create: `backend/app/modules/annuity/official_payment_workbook_input_schemas.py`
- Create: `backend/tests/test_v8_payment_workbook_input_api.py`

- [ ] **Step 1: Write API RED tests for multipart register, review, activate and retire.**

  Prove 401/403, `Fee.Edit`, 201/200 replay, 409 conflict, 422 validation, server actor/time,
  two-person review, cleanup of request-created files after failure, and no product state writes.

- [ ] **Step 2: Run RED.**

  Run: `cd backend && .venv/bin/pytest -q tests/test_v8_payment_workbook_input_api.py`

- [ ] **Step 3: Implement the four actions.**

  Use `app.core.storage` without modifying it. Store template and proof under separate managed paths;
  sanitize names; never accept a client file path or runtime profile. Call WB-I2 and let the API own
  commit/rollback. Keep the module response envelope.

- [ ] **Step 4: Run GREEN, scoped Ruff and route conflict checks.**
- [ ] **Step 5: Close and commit.**

  Commit message: `feat(v8): expose payment workbook input governance API`

## 11. Tasks 8–15 — Existing payment-workbook product rows

Execute each existing task independently and in this order. Reuse its exact closure, allowlist,
tests and close loop; Task 1 is latest-wins only for dependency/gate interpretation.

| Task | RED/GREEN focus | Commit message |
| --- | --- | --- |
| row 215 generation service | active production resolver; atomic artifact/hash/template version + FEE activity; missing config 409/no write | `feat(v8): generate official payment workbooks` |
| row 216 HTTP | generation/download action, permission/envelope/status | `feat(v8): expose official workbook generation API` |
| row 217 FE adapter | typed generation/download; no client-derived official/payment facts | `feat(v8): add official workbook frontend adapter` |
| row 218 UI | Simplified Chinese generation/download UI; generated is not accepted/paid/ticket verified | `feat(v8): add official workbook UI` |
| row 219 acceptance service | same-PayList acceptance proof bound to generated artifact; separate FEE activity | `feat(v8): record official workbook acceptance evidence` |
| row 220 acceptance API | `Fee.Edit`, exact 200/4xx behavior, caller transaction | `feat(v8): expose workbook acceptance evidence API` |
| row 221 acceptance FE | typed acceptance result separate from generation/payment/ticket | `feat(v8): add workbook acceptance frontend adapter` |
| row 222 acceptance UI | Chinese display/action; four independent facts | `feat(v8): add workbook acceptance UI` |

For each row:

- [ ] **Step 1: Confirm predecessor terminal PASS and no shared-file owner.**
- [ ] **Step 2: Run its exact RED before source changes.**
- [ ] **Step 3: Implement only the exact closure.**
- [ ] **Step 4: Run its focused GREEN and listed inherited regressions.**
- [ ] **Step 5: Run the canonical close loop and exact commit.**

Additional row-215 requirement: production resolution calls WB-I2 and rejects TEST_ONLY outside
`fpms_env=test`. In test profile, the isolated resolver can supply the one TEST_ONLY input without
publishing ACTIVE/current identity. The generated artifact must retain the resolved template version
and source hash; no success path may infer official acceptance, payment or ticket status.

## 12. Tasks 16–22 — Existing service-price product rows

### Task 16 / row 223 — Service price-book carrier

**Files:** use the existing row-223 allowlist.

- [ ] **Step 1: Freeze the physical schema in the task card before RED.**

  The header must include explicit `source_classification (PRODUCTION|TEST_ONLY)`, immutable source
  reference/hash and item snapshot/hash, version, scope, currency, tax/discount policy, effective
  interval, DRAFT/ACTIVE/RETIRED status, approval actor/time/reason, idempotency/current identity and
  audit fields. ACTIVE requires approval and a nonempty validated snapshot. A production resolver
  accepts only PRODUCTION; test-profile resolution may accept TEST_ONLY only in isolated storage.

- [ ] **Step 2: Recheck the single Alembic head after WB-I1 and freeze it as down revision.**
- [ ] **Step 3: Write/run exact schema RED.**
- [ ] **Step 4: Implement model/migration only; no seed/import/activation.**
- [ ] **Step 5: Run focused GREEN, Ruff, unique-head and clean SQLite upgrade.**
- [ ] **Step 6: Independently close and commit `feat(v8): add service price book carrier`.**

### Tasks 17–22 / rows 224–229

| Row | Exact behavior to prove | Focused test |
| --- | --- | --- |
| 224 import service | create/reuse DRAFT; canonical source/item hashes; unique codes and Decimal validation; no activation | `backend/tests/test_v8_service_price_book_import.py` |
| 225 import API | `Fee.Edit`; 201 new/200 replay; invalid/duplicate/source conflict statuses | exact task-card test |
| 226 activation service | populated, approved, non-overlapping version only; production gate required only for PRODUCTION activation; isolated TEST_ONLY activation usable only in `fpms_env=test` | `backend/tests/test_v8_service_price_book_activation.py` |
| 227 activation API | server runtime profile and actor; persisted gate/source approval; exact 200/409 | exact task-card test |
| 228 receivable service | exact active version/item/case; SERVICE domain; never derived from official fee; caller transaction | exact task-card test |
| 229 receivable API | `Fee.Edit`; 201/200 replay; inactive/absent/mismatch 409; no client price | exact task-card test |

For each row:

- [ ] **Step 1: Confirm predecessor PASS and acquire its shared-file/SQLite lane.**
- [ ] **Step 2: Run exact RED.**
- [ ] **Step 3: Implement the minimum closure without UI or adjacent refactor.**
- [ ] **Step 4: Run exact focused GREEN, scoped Ruff and diff check.**
- [ ] **Step 5: Independently close and commit.**

Commit messages, in order:

```text
feat(v8): import service price book drafts
feat(v8): expose service price book import API
feat(v8): activate reviewed service price books
feat(v8): expose service price book activation API
feat(v8): create service receivable obligations
feat(v8): expose service receivable API
```

## 13. Task 23 / row 278 — Isolated full-stack workbook E2E

**Files:** use the existing row-278 task card allowlist only.

- [ ] **Step 1: Start the E2E backend with `FPMS_ENV=test`, an isolated SQLite DB and isolated
  storage. Never reuse development or production storage.**
- [ ] **Step 2: Seed through the protected API one TEST_ONLY validated/approved INACTIVE workbook
  input and the minimum PayList state. Do not write ACTIVE/current identity.**
- [ ] **Step 3: Run RED proving the visible four-fact path is absent or conflated.**

  Run the exact row-278 Playwright spec with `--workers=1`.

- [ ] **Step 4: If RED identifies a product/UI defect, stop row 278 and materialize one separate
  exact product task with its own closure, allowlist, RED/GREEN and independent close. Resume row
  278 only after that task is terminal PASS.**

  Row 278 is QA-only and may edit only its Playwright spec, task card and evidence. It never fixes
  product/UI code. Do not weaken assertions, intercept the product API, mock a successful official
  submission, or claim CNIPA acceptance. The test-profile resolver may supply the isolated
  TEST_ONLY input; the browser must still traverse the real UI and HTTP/service/persistence path.

- [ ] **Step 5: Run GREEN with one worker.**

  Prove generated, official-site acceptance evidence, paid and ticket-verified are four persisted,
  separately visible facts and that no route or legal status is fulfilled by generation.

- [ ] **Step 6: Close and commit `test(v8): verify official workbook real UI path`.**

## 14. Task 24 — Capability close and residual production configuration receipt

Before Full, execute the QA-only successor close task already materialized by Task 1. It is owned by
an independent reviewer.

**Files:**

- Modify: `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md`
- Create: `docs/product/v8/reviews/V8-INPUT-ACTIVATION-CAPABILITY-CURRENT-ADOPTION.md`
- Create: `backend/tests/test_v8_input_activation_capability_close.py`

- [ ] **Step 1: Write RED requiring terminal PASS for Task 1, WB-I1/I2/I3, rows 175/176,
  rows 214–229 and row 278.**
- [ ] **Step 2: Require negative production proofs:** no active real workbook/price version means
  production generation/activation/receivable returns 409 and produces zero writes.
- [ ] **Step 3: Require TEST_ONLY isolation proofs and official-fee/service-fee separation.**
- [ ] **Step 4: Write a receipt with actual states, for example:**

  ```json
  {
    "capability": "CAPABILITY_READY",
    "payment_workbook": "CONFIG_REQUIRED",
    "service_rate": "CONFIG_REQUIRED",
    "production_activation_claimed": false
  }
  ```

  If a real input has actually been independently activated by then, record its exact version/hash
  instead; never infer it from tests.

- [ ] **Step 5: Run GREEN, independent review, close and commit.**

  Commit message: `test(v8): close input activation capabilities`

## 15. Tasks 25–27 — Full, item ledger and release close

### Task 25 / row 281 — Inherited regression matrix

- [ ] Run only after Task 24 PASS.
- [ ] Use the exact row-281 contract and Full manifest; include the successor capability receipt as
  authority for the two CONFIG_REQUIRED lanes.
- [ ] Any product failure becomes a new exact task; row 281 does not fix product code.
- [ ] Independently close and commit.

### Task 26 / row 282 — Final item-to-slice ledger

- [ ] Map every immutable catalog row plus the new successor tasks to exact evidence and terminal
  gate outcome.
- [ ] Record payment workbook and service rate as `CONFIG_REQUIRED` if still inactive; this is no
  longer a “gated residual” because capability and fail-closed behavior are terminally verified.
- [ ] Do not change immutable catalog/Foundation counts; successor nodes are external overlays.
- [ ] Independently close and commit.

### Task 27 / row 283 — Final close and release last

- [ ] Confirm every required product and successor task except self is terminal PASS.
- [ ] Run clean SQLite upgrade+seed and the exact row-283 fresh-login check.
- [ ] Run repo-wide backend Ruff/pytest, frontend lint/typecheck/build and named Playwright specs
  only now, serialized.
- [ ] Run the pre-self manifest gate and release gate excluding self.
- [ ] Independently review the final close patch and capability receipt.
- [ ] Run row-283 task/evidence gates.
- [ ] Run the final release gate last.
- [ ] Commit the exact final-close allowlist; do not push.
- [ ] Mark the existing Goal complete only after the final release gate returns zero and no required
  work remains.

## 16. Failure and recovery rules

- A transport failure first reconciles HEAD, task status, diff, evidence ordinal, running process and
  locks; resume from the first incomplete durable step.
- A missing real workbook or price version is expected `CONFIG_REQUIRED`, not a development blocker.
- A missing frozen field/constraint or contradictory source is a HIGH contract blocker for that lane
  only. Continue the other lane.
- Test, JSON, evidence-format, taskctl, owner compatibility or ordinary code failures remain High
  implementation work; do not escalate to Ultra.
- Do not create another governance task for ordinary scope/evidence friction.
- Broad verification never runs before Task 27 / row 283.

## 17. Completion evidence

The overall cycle is complete only when:

1. all successor and rows 175/176, 214–229, 278 tasks are terminal PASS;
2. production paths fail closed without real active inputs;
3. TEST_ONLY cannot activate or resolve outside isolated test profile;
4. workbook macros were never executed;
5. official fee and service receivable remain separate;
6. rows 281, 282 and 283 are terminal PASS;
7. the final release gate is last and PASS;
8. the release receipt states the actual production configuration status without inventing inputs.
