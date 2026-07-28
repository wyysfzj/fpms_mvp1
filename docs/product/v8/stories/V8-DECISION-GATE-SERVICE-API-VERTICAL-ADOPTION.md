# Story V8-DECISION-GATE-SERVICE-API-VERTICAL-ADOPTION

- Risk: `PROTECTED`
- Outcome: current-verify the frozen decision-gate record service, read service and
  confirmation API, then adopt one bodyless read-only audit GET that returns persisted
  gate facts without interpretation or writes.
- Change mode: rows 166–168 remain current product behavior; row 169 adopts the exact
  archived API/schema/list-test bytes plus one row-168 successor-test compatibility hunk.
- Authority: the customer-decision, permission, API and SQLite rules in
  `docs/product/v8/domain-contract.md`; the pending-gate snapshot and no-default activation
  rule in `docs/product/v8/source-decision-registry.md`; frozen catalog rows 166–169; and
  the latest-wins audit-list contract in
  `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md`.
- Archive comparison anchor: `6b2ef89da447353380b99853168d4d38aaf9210a`.

## Catalog IDs and dependencies

1. `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01` (ordinal `166`)
2. `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01` (ordinal `167`)
3. `FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01` (ordinal `168`)
4. `FPMS-V8-DECISION-GATE-LIST-API-20260712-01` (ordinal `169`)

The canonical chain is carrier → record service → read service and confirm API → list
API. The carrier prerequisite is current-verified by
`V8-DECISION-GATE-CARRIER-CURRENT-VERIFICATION` at
`f0da54ef4e31f2f50330d5b11846479138677fb5`.

## Exact product and test paths

- Current-verified service:
  `backend/app/modules/system/decision_gate_service.py`
- Adopted API:
  `backend/app/modules/system/api.py`
- Adopted schemas:
  `backend/app/modules/system/decision_gate_schemas.py`
- Current record-service test:
  `backend/tests/test_v8_decision_gate_record_service.py`
- Current read-service test:
  `backend/tests/test_v8_decision_gate_read_service.py`
- Row-168 confirmation test with the sole compatibility change that selects the POST
  route by `route.methods == {"POST"}`:
  `backend/tests/test_v8_decision_gate_confirm_api.py`
- Adopted list test:
  `backend/tests/test_v8_decision_gate_list_api.py`

The adopted API, schema and list-test blobs must be byte-identical to the archive anchor.
The confirmation-test diff must contain only the POST-method route selection above.

## Frozen audit GET

`GET /api/v1/system/decision-gates` has no body, path, query, filter, pagination or as-of
input. It uses parameter-injected `SystemParam.Read`, returns a bare list in stable
`recorded_at ASC, gate_id ASC` order, and projects all persisted current, superseded,
revoked and future-effective facts through one selected-column query under
`transaction.no_autoflush`. It does not call the decision resolver or perform any write,
clock read, transaction boundary or authority inference.

## Verification

- RED: run only `tests/test_v8_decision_gate_list_api.py` before product edits and confirm
  failure because the DTO/GET is absent.
- Successor compatibility RED: run the four-file tranche after exact archive adoption and
  confirm row 168 fails only because its POST lookup also sees the legitimate same-path GET.
- GREEN from this worktree's `backend` directory:
  `/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_decision_gate_record_service.py tests/test_v8_decision_gate_read_service.py tests/test_v8_decision_gate_confirm_api.py tests/test_v8_decision_gate_list_api.py`
- Run scoped Ruff check-only on the service, API, schemas and four tests; run exact
  diff-check, archive-blob comparison and successor-test diff inspection.
- An independent High reviewer must review the exact commit and rerun the decisive checks;
  the implementer does not approve this `PROTECTED` story.

## Non-goals and rollback

No source activation, customer default, business-policy interpretation, additional route,
router rewiring, model/schema/migration change, frontend, ledger/disposition/review edit,
old evidence mutation, Foundation claim, or adoption of
`backend/tests/test_addgap_notice_catalog_reference_gate.py` or
`backend/tests/test_v8_application_fee_notice_source_carrier.py`. Rollback reverts only
this story commit, restoring the pre-vertical lean tree.
