# Story V8-APPLICATION-FEE-NOTICE-ACTIVATION-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `e111497`
- Activation commit: `36ab390` (preserved; review correction is a separate successor diff)
- Outcome: only `OFFICIAL_NOTICE_034 / 缴纳申请费通知书 / 200103` becomes an
  executable `APPLICATION_FEE_NOTICE` with an explicit-official-due policy; the reviewed
  real create path creates or reuses exactly one application-fee obligation.
- Catalog ID: `FPMS-V8-APPLICATION-FEE-NOTICE-ACTIVATION-20260712-01`
  (ordinal `128`, profile `TC-SERVICE`).
- Authority: frozen catalog row `128`, its exact task contract, the current-verified row
  `126` application-fee obligation story/code, `docs/product/v8/domain-contract.md`, and
  `docs/product/v8/source-decision-registry.md`.

## Dependency and exact paths

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/app/modules/documents/service.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_v8_application_fee_notice_activation.py`

The row-126 obligation dependency is current-verified. The shared catalog, seed and SQLite
verification lanes remain serialized. The C3 integration contract supersedes the old task,
canonical-scope and evidence-artifact machinery; this story does not mutate those historical
paths.

## Observable contract

The application-fee target extends the seven existing executable official-notice rows and
no others. Its direct fee trigger is `APPLICATION_FEE`, while the existing semantics and
fee-linking path suppress generic draft creation and require exact reviewed notice evidence,
an exact confirmed due date and one permitted official due-date source. The seed converges
existing rows and is idempotent.

The focused real-path test uses only an explicit `CN_INV_APPLICATION_FEE` notice line and
`MANUAL_OFFICIAL_NOTICE`; it neither infers page or priority counts nor activates
`DG-APPLICATION-FEE-NOTICE-PREVIEW-SOURCE`. Recognition creates once and reuses on replay,
without changing case status or creating a task, reply or draft.

The public document wizard is also obligation-only for this semantic. Fee preview returns
no generic candidate, and batch creation rejects any caller-supplied row-34 fee row with
`DOCUMENT_WIZARD_BATCH_INVALID / APPLICATION_FEE_NOTICE_DRAFT_FORBIDDEN` before creating a
document or draft. The existing single-document `maybe_create_fee_draft` suppression remains
unchanged.

## TDD and verification

The targeted RED produced three expected failures: the activation seeder was absent and
the development seed retained only the prior seven executable rows. The minimum catalog and
seed changes then passed the focused `3/3` test. Current affected regressions, scoped Ruff
and diff checks are required before independent High review of the exact candidate patch.

Independent review then reproduced a P1 public-path gap: wizard fee preview returned one
unskipped `APPLICATION_FEE` candidate, and batch creation accepted it and persisted one
zero-value `OPEN` draft plus its document. The correction RED captured both outcomes as
`(1 candidate)` and `(201, 1 draft, 1 document)`. The minimum service correction makes
preview return no candidate and rejects explicit application-fee wizard rows before writes;
the correction-focused GREEN passed `2/2` and requires successor-diff re-review.

## Non-goals and rollback

No endpoint, UI, schema, customer decision, preview-source activation, page/priority-count
inference, adjacent service rule, second catalog row, status transition, task, reply or draft
behavior is added. Rollback removes the row-34 activation/seeder selection, its focused test
and this story mapping, restoring the prior seven executable rows. The review correction can
be rolled back independently by removing only the wizard preview exclusion, batch rejection
and their public-path regressions.
